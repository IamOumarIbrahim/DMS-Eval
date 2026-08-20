"""Generate benchmark accuracy/latency figures from a complete aggregate artifact."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from core.protocol import resolve_repo_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--aggregate", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    with resolve_repo_path(args.aggregate).open("r", encoding="utf-8") as handle:
        rows = json.load(handle)["rows"]
    figure, axis = plt.subplots(figsize=(7, 5), constrained_layout=True)
    for row in rows:
        latency = row["tensor_to_final_detections_p50_ms"]
        axis.scatter(latency, row["map_50_95"], s=75)
        axis.annotate(row["model_id"], (latency, row["map_50_95"]), xytext=(5, 5), textcoords="offset points")
    axis.set_xlabel("Tensor-to-final-detections p50 latency (ms), batch 1 CUDA AMP FP16")
    axis.set_ylabel("COCO mAP@0.5:0.95")
    axis.grid(True, alpha=0.25)
    destination = resolve_repo_path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(destination, dpi=300)
    plt.close(figure)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
