"""Aggregate all nine protected runs into per-model mean and sample-SD results."""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from core.isolation import write_json_atomic
from core.protocol import TRAINING_SEEDS, ProtocolError, resolve_repo_path, sha256_file


FROZEN_MODELS = ("yolo11n", "yolo26n", "dfine_n")
NUMERIC_FIELDS = (
    "map_50_95", "map_50", "precision", "recall", "micro_f1", "far_per_100_negative_frames",
    "model_forward_p50_ms", "model_forward_p95_ms", "model_forward_p99_ms",
    "model_forward_sustained_fps", "tensor_to_final_detections_p50_ms",
    "tensor_to_final_detections_p95_ms", "tensor_to_final_detections_p99_ms",
    "tensor_to_final_detections_sustained_fps", "peak_allocated_vram_bytes", "parameters",
    "inference_artifact_bytes",
)


def _stats(values: list[float | int]) -> dict[str, float]:
    numbers = [float(value) for value in values]
    if len(numbers) != len(TRAINING_SEEDS) or not all(math.isfinite(value) for value in numbers):
        raise ProtocolError("Every aggregate statistic requires three finite predeclared-seed values")
    return {"mean": statistics.mean(numbers), "sample_std": statistics.stdev(numbers)}


def _run_row(result: dict[str, Any], source: Path) -> dict[str, Any]:
    coco, operating, runtime = result["coco_metrics"], result["operating_point"], result["runtime_profile"]
    forward, end_to_end = runtime["model_forward"], runtime["tensor_to_final_detections"]
    qualitative = result.get("qualitative_analysis", {})
    if qualitative.get("artifact") != "qualitative_error_analysis":
        raise ProtocolError(f"Protected result lacks the pre-registered qualitative/error artifact: {source}")
    qualitative_path = resolve_repo_path(qualitative.get("path", ""))
    if not qualitative_path.is_file() or sha256_file(qualitative_path) != qualitative.get("sha256"):
        raise ProtocolError(f"Qualitative/error artifact integrity failure: {source}")
    return {
        "model_id": result["model_id"], "training_seed": result["training_seed"],
        "manifest_id": result["manifest_id"], "suite_id": result["suite_id"], "source": str(source),
        "map_50_95": coco["map_50_95"], "map_50": coco["map_50"],
        "per_class_ap_50_95": coco["per_class_ap_50_95"],
        "precision": operating["precision"], "recall": operating["recall"],
        "micro_f1": operating["micro_f1"],
        "far_per_100_negative_frames": operating["far_per_100_negative_frames"],
        "model_forward_p50_ms": forward["p50_ms"], "model_forward_p95_ms": forward["p95_ms"],
        "model_forward_p99_ms": forward["p99_ms"], "model_forward_sustained_fps": forward["sustained_fps"],
        "tensor_to_final_detections_p50_ms": end_to_end["p50_ms"],
        "tensor_to_final_detections_p95_ms": end_to_end["p95_ms"],
        "tensor_to_final_detections_p99_ms": end_to_end["p99_ms"],
        "tensor_to_final_detections_sustained_fps": end_to_end["sustained_fps"],
        "peak_allocated_vram_bytes": runtime["peak_allocated_vram_bytes"],
        "parameters": result["parameters"], "flop_estimates": result["flop_estimates"],
        "inference_artifact_bytes": result["inference_artifact"]["bytes"],
        "inference_artifact_sha256": result["inference_artifact"]["sha256"],
        "qualitative_analysis": {"path": str(qualitative_path), "sha256": qualitative["sha256"]},
    }


def build_aggregate(results: list[tuple[dict[str, Any], Path]]) -> dict[str, Any]:
    runs: list[dict[str, Any]] = []
    seen: set[tuple[str, int]] = set()
    for result, source in results:
        model_id, seed = result.get("model_id"), result.get("training_seed")
        if result.get("artifact") != "protected_test_result" or model_id not in FROZEN_MODELS:
            raise ProtocolError(f"Not a protected DMS-Eval result: {source}")
        if seed not in TRAINING_SEEDS:
            raise ProtocolError(f"Unexpected training seed in {source}")
        key = (model_id, seed)
        if key in seen:
            raise ProtocolError(f"Duplicate result for {model_id}/seed-{seed}")
        seen.add(key)
        runs.append(_run_row(result, source))
    required = {(model_id, seed) for model_id in FROZEN_MODELS for seed in TRAINING_SEEDS}
    if seen != required:
        raise ProtocolError(f"Aggregation requires exactly all nine frozen runs; missing {sorted(required - seen)}")
    suite_ids = {run["suite_id"] for run in runs}
    if len(suite_ids) != 1:
        raise ProtocolError("All nine protected results must belong to the same pre-test frozen suite")

    rows = []
    for model_id in FROZEN_MODELS:
        model_runs = sorted((run for run in runs if run["model_id"] == model_id), key=lambda run: run["training_seed"])
        row: dict[str, Any] = {"model_id": model_id, "runs": len(model_runs), "training_seeds": list(TRAINING_SEEDS)}
        for field in NUMERIC_FIELDS:
            row[field] = _stats([run[field] for run in model_runs])
        row["per_class_ap_50_95"] = {
            name: _stats([run["per_class_ap_50_95"][name] for run in model_runs])
            for name in model_runs[0]["per_class_ap_50_95"]
        }
        row["flop_estimates"] = {}
        for estimator in ("thop", "torch_profiler"):
            values = [run["flop_estimates"][estimator]["flops"] for run in model_runs]
            row["flop_estimates"][estimator] = None if any(value is None for value in values) else _stats(values)
        rows.append(row)
    return {
        "schema_version": 3, "artifact": "dms_eval_aggregate",
        "run_policy": "three_predeclared_equal_seeds_no_run_selection",
        "suite_id": next(iter(suite_ids)),
        "training_seeds": list(TRAINING_SEEDS), "dispersion": "sample_standard_deviation",
        "runs": sorted(runs, key=lambda run: (run["model_id"], run["training_seed"])), "rows": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", nargs="+", help="The nine protected test result JSON files")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = resolve_repo_path(args.output)
    if output.exists():
        raise ProtocolError(f"Refusing to overwrite existing aggregate result: {output}")
    loaded = []
    for source in args.results:
        path = resolve_repo_path(source)
        with path.open("r", encoding="utf-8") as handle:
            loaded.append((json.load(handle), path))
    artifact = build_aggregate(loaded)
    write_json_atomic(output, artifact)
    print(json.dumps(artifact, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
