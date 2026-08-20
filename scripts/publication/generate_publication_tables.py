"""Generate Markdown and LaTeX tables from a complete aggregate result artifact."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from core.protocol import resolve_repo_path


def _flop_pair_g(row: dict) -> str:
    estimates = row["flop_estimates"]
    thop = estimates["thop"]["flops"]
    profiler = estimates["torch_profiler"]["flops"]
    profiler_text = "NA" if profiler is None else f"{profiler / 1e9:.3f}"
    return f"{thop / 1e9:.3f}/{profiler_text}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--aggregate", required=True)
    parser.add_argument("--markdown", required=True)
    parser.add_argument("--latex", required=True)
    args = parser.parse_args()
    with resolve_repo_path(args.aggregate).open("r", encoding="utf-8") as handle:
        rows = json.load(handle)["rows"]

    header = (
        "| Model | mAP50:95 | mAP50 | P | R | F1 | FAR | Fwd p50 ms | "
        "Tensor→det p50 ms | p95 ms | p99 ms | FPS | FLOPs G (T/P) | FP16 MB |\n"
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|\n"
    )
    markdown = header + "".join(
        f"| {row['model_id']} | {row['map_50_95']:.4f} | {row['map_50']:.4f} | "
        f"{row['precision']:.4f} | {row['recall']:.4f} | {row['micro_f1']:.4f} | "
        f"{row['far_per_100_negative_frames']:.4f} | {row['model_forward_p50_ms']:.3f} | "
        f"{row['tensor_to_final_detections_p50_ms']:.3f} | "
        f"{row['tensor_to_final_detections_p95_ms']:.3f} | "
        f"{row['tensor_to_final_detections_p99_ms']:.3f} | "
        f"{row['tensor_to_final_detections_sustained_fps']:.2f} | {_flop_pair_g(row)} | "
        f"{row['inference_artifact_bytes'] / 1e6:.3f} |\n"
        for row in rows
    )
    latex = (
        "\\begin{tabular}{lrrrrrrrrrrrrr}\n"
        "Model & mAP & mAP50 & P & R & F1 & FAR & Fwd50 & T2D50 & T2D95 & T2D99 & FPS & FLOPs & MB \\\\\n"
        "\\hline\n"
        + "".join(
            f"{row['model_id']} & {row['map_50_95']:.4f} & {row['map_50']:.4f} & "
            f"{row['precision']:.4f} & {row['recall']:.4f} & {row['micro_f1']:.4f} & "
            f"{row['far_per_100_negative_frames']:.4f} & {row['model_forward_p50_ms']:.3f} & "
            f"{row['tensor_to_final_detections_p50_ms']:.3f} & "
            f"{row['tensor_to_final_detections_p95_ms']:.3f} & "
            f"{row['tensor_to_final_detections_p99_ms']:.3f} & "
            f"{row['tensor_to_final_detections_sustained_fps']:.2f} & {_flop_pair_g(row)} & "
            f"{row['inference_artifact_bytes'] / 1e6:.3f} \\\\\n"
            for row in rows
        )
        + "\\end{tabular}\n"
    )
    for destination, output in (
        (resolve_repo_path(args.markdown), markdown),
        (resolve_repo_path(args.latex), latex),
    ):
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(output, encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
