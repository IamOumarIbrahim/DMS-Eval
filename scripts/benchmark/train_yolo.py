"""Frozen YOLO11n/YOLO26n launcher with an explicit training gate."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from core.protocol import ProtocolError, REPO_ROOT, load_backends, load_protocol, resolve_repo_path, sha256_file
from scripts.benchmark.setup_backends import ensure_ultralytics


def build_plan(model_id: str) -> dict:
    protocol = load_protocol()
    training = protocol["training"]
    optimization = training["optimization"]["ultralytics"]
    ensure_ultralytics(False)
    weight = load_backends()["ultralytics"]["models"][model_id]
    checkpoint = resolve_repo_path(weight["file"])
    if not checkpoint.is_file() or sha256_file(checkpoint) != weight["sha256"]:
        raise ProtocolError(f"Official {model_id} initialization is missing or invalid")
    return {
        "model_id": model_id,
        "model": str(checkpoint),
        "data": str(REPO_ROOT / "configs" / "yolo" / "dms_eval.yaml"),
        "epochs": training["epochs"],
        "batch": training["physical_batch_size"],
        "nbs": training["effective_batch_size"],
        "imgsz": protocol["dataset"]["width"],
        "seed": protocol["seed"],
        "device": 0,
        "project": str(REPO_ROOT / "runs" / "train"),
        "name": f"{model_id}_seed13",
        "exist_ok": False,
        "amp": True,
        "optimizer": optimization["optimizer"],
        "val": True,
        "patience": 0,
        "save": True,
        "save_period": 1,
        "plots": True,
        "deterministic": True,
        "cache": False,
        "verbose": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-id", required=True, choices=["yolo11n", "yolo26n"])
    parser.add_argument("--execute-training", action="store_true", help="Explicitly start the 220-epoch training run")
    args = parser.parse_args()
    plan = build_plan(args.model_id)
    print(json.dumps(plan, indent=2))
    if not args.execute_training:
        print("Dry-run only. Training was NOT started; add --execute-training to execute this frozen plan.")
        return 0
    if not torch.cuda.is_available() or "RTX 4060" not in torch.cuda.get_device_name(0):
        raise ProtocolError("Frozen training requires the RTX 4060 CUDA environment")
    run_dir = Path(plan["project"]) / plan["name"]
    if run_dir.exists():
        raise ProtocolError(f"Refusing to reuse existing run directory: {run_dir}")
    from ultralytics import YOLO

    model = YOLO(plan.pop("model"))
    frozen_batch = plan["batch"]

    def enforce_frozen_batch(trainer) -> None:
        if trainer.batch_size != frozen_batch:
            raise ProtocolError(
                f"Ultralytics changed the frozen physical batch from {frozen_batch} to {trainer.batch_size}"
            )

    model.add_callback("on_train_batch_start", enforce_frozen_batch)
    model.train(**{key: value for key, value in plan.items() if key != "model_id"})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
