"""Aggregate the three protected test artifacts into a machine-readable benchmark table."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.isolation import write_json_atomic
from core.protocol import ProtocolError, resolve_repo_path


FROZEN_MODELS = {"yolo11n", "yolo26n", "dfine_n"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", nargs="+", help="Protected test result JSON files")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    rows = []
    seen = set()
    for source in args.results:
        path = resolve_repo_path(source)
        with path.open("r", encoding="utf-8") as handle:
            result = json.load(handle)
        if result.get("artifact") != "protected_test_result" or result.get("model_id") not in FROZEN_MODELS:
            raise ProtocolError(f"Not a protected DMS-Eval result: {path}")
        if result["model_id"] in seen:
            raise ProtocolError(f"Duplicate result for {result['model_id']}")
        seen.add(result["model_id"])
        coco = result["coco_metrics"]
        operating = result["operating_point"]
        runtime = result["runtime_profile"]
        rows.append(
            {
                "model_id": result["model_id"],
                "manifest_id": result["manifest_id"],
                "map_50_95": coco["map_50_95"],
                "map_50": coco["map_50"],
                "per_class_ap_50_95": coco["per_class_ap_50_95"],
                "precision": operating["precision"],
                "recall": operating["recall"],
                "micro_f1": operating["micro_f1"],
                "far_per_100_negative_frames": operating["far_per_100_negative_frames"],
                "p50_ms": runtime["p50_ms"],
                "p95_ms": runtime["p95_ms"],
                "p99_ms": runtime["p99_ms"],
                "sustained_fps": runtime["sustained_fps"],
                "peak_allocated_vram_bytes": runtime["peak_allocated_vram_bytes"],
                "parameters": result["parameters"],
                "flops": result["flops"],
                "checkpoint_bytes": result["checkpoint_bytes"],
            }
        )
    if seen != FROZEN_MODELS:
        raise ProtocolError(f"Aggregation requires all three frozen models; missing {sorted(FROZEN_MODELS - seen)}")
    artifact = {"schema_version": 1, "artifact": "dms_eval_aggregate", "rows": sorted(rows, key=lambda row: row["model_id"])}
    write_json_atomic(args.output, artifact)
    print(json.dumps(artifact, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
