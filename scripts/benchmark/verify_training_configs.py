"""Verify the final three-model plans without starting training or reading the test set."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from core.protocol import (
    ALLOWED_RECIPE_ADAPTATIONS,
    ProtocolError,
    REPO_ROOT,
    TRAINING_SEEDS,
    load_protocol,
    load_yaml,
    validate_protocol,
)
from scripts.benchmark.setup_backends import ensure_dfine, ensure_ultralytics
from scripts.benchmark.train_dfine import build_plan as build_dfine_plan
from scripts.benchmark.train_yolo import build_plan as build_yolo_plan


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise ProtocolError(message)


def verify_training_configs() -> dict[str, Any]:
    protocol = validate_protocol()
    training = protocol["training"]
    backend_report = {
        "ultralytics": ensure_ultralytics(False),
        "dfine": ensure_dfine(False),
    }
    plans = {
        f"{model_id}_seed{seed}": (
            build_dfine_plan(seed) if model_id == "dfine_n" else build_yolo_plan(model_id, seed)
        )
        for model_id in ("yolo11n", "yolo26n", "dfine_n")
        for seed in TRAINING_SEEDS
    }
    _expect(len(plans) == 9, "Training plan must contain exactly nine model-seed runs")
    for model_id in ("yolo11n", "yolo26n"):
        for seed in TRAINING_SEEDS:
            plan = plans[f"{model_id}_seed{seed}"]
            _expect(plan["epochs"] == 220 and plan["batch"] == 8 and plan["nbs"] == 32, f"{model_id} budget drift")
            _expect(plan["imgsz"] == 640 and plan["seed"] == seed and plan["patience"] == 0, f"{model_id} shared-control drift")
            _expect(plan["optimizer"] == "auto", f"{model_id} must retain the pinned Ultralytics optimizer recipe")
    for seed in TRAINING_SEEDS:
        dfine_plan = plans[f"dfine_n_seed{seed}"]
        _expect(
            (dfine_plan["epochs"], dfine_plan["physical_batch_size"], dfine_plan["gradient_accumulation_steps"], dfine_plan["seed"])
            == (220, 8, 4, seed),
            "D-FINE shared-control drift",
        )
    _expect(len({plan.get("name", plan.get("output_dir")) for plan in plans.values()}) == 9, "Run outputs must be unique")
    dfine = load_yaml(REPO_ROOT / "configs" / "dfine" / "dfine_n_dms.yml")
    _expect(dfine["num_classes"] == 4 and dfine["eval_spatial_size"] == [640, 640], "D-FINE task adaptation drift")
    _expect(dfine["train_dataloader"]["total_batch_size"] == 8, "D-FINE physical batch drift")
    _expect(dfine["train_dataloader"]["drop_last"] is False, "D-FINE may not drop training images")
    _expect(dfine["gradient_accumulation_steps"] == 4 and dfine["epochs"] == 220 and dfine["seed"] == 13, "D-FINE budget drift")
    _expect(dfine["optimizer"]["type"] == "AdamW", "D-FINE optimizer recipe drift")
    _expect(dfine["optimizer"]["lr"] == 0.0008 and dfine["optimizer"]["weight_decay"] == 0.0001, "D-FINE base recipe drift")
    backbone_rates = [group.get("lr") for group in dfine["optimizer"]["params"] if "backbone" in group.get("params", "")]
    _expect(backbone_rates == [0.0004, 0.0004], "D-FINE backbone recipe drift")

    solver = (REPO_ROOT / "third_party" / "D-FINE" / "src" / "solver" / "det_solver.py").read_text(encoding="utf-8")
    _expect('load_resume_state(str(self.output_dir / "best_stg1.pth"))' not in solver, "D-FINE still has a validation-guided reload")
    engine = (REPO_ROOT / "third_party" / "D-FINE" / "src" / "solver" / "det_engine.py").read_text(encoding="utf-8")
    _expect('batch_loss_reduction="mean"' in engine and "loss * loss_scale" in engine, "D-FINE accumulation normalization patch is missing")
    yolo_patch = (REPO_ROOT / "patches" / "ultralytics-fixed-accumulation.patch").read_text(encoding="utf-8")
    _expect("keep the shared four-step update cadence" in yolo_patch, "Ultralytics fixed-accumulation patch is missing")
    _expect("accumulation_loss_scale" in yolo_patch, "Ultralytics partial-window normalization is missing")
    _expect(training["recipe_policy"]["allowed_adaptations"] == ALLOWED_RECIPE_ADAPTATIONS, "Closed adaptation list drift")

    return {
        "status": "VERIFIED",
        "training_started": False,
        "protected_test_accessed": False,
        "allowed_recipe_adaptations": ALLOWED_RECIPE_ADAPTATIONS,
        "shared_controls": {
            "epochs": 220,
            "physical_batch_size": 8,
            "gradient_accumulation_steps": 4,
            "training_seeds": list(TRAINING_SEEDS),
            "runs_per_model": len(TRAINING_SEEDS),
            "run_selection": "none",
            "result_aggregation": "mean_and_sample_standard_deviation",
            "early_stopping": False,
            "drop_last": False,
            "validation_intervention": "checkpoint_retention_only",
        },
        "architecture_recipes": {
            "yolo11n": "Ultralytics 8.4.123 default; optimizer=auto (expected MuSGD)",
            "yolo26n": "Ultralytics 8.4.123 default; optimizer=auto (expected MuSGD)",
            "dfine_n": "Pinned official D-FINE-N config; AdamW lr=0.0008, backbone lr=0.0004",
        },
        "backends": backend_report,
        "plans": plans,
    }


def main() -> int:
    report = verify_training_configs()
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ProtocolError, FileNotFoundError, KeyError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
