"""Generate mean-plus-sample-SD Markdown and LaTeX tables from the nine-run aggregate."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from core.protocol import ProtocolError, resolve_repo_path


def _value(statistic: dict, scale: float = 1.0, digits: int = 4, latex: bool = False) -> str:
    separator = r" $\pm$ " if latex else " ± "
    return f"{statistic['mean'] / scale:.{digits}f}{separator}{statistic['sample_std'] / scale:.{digits}f}"


def _flops(row: dict, latex: bool = False) -> str:
    values = []
    for estimator in ("thop", "torch_profiler"):
        statistic = row["flop_estimates"].get(estimator)
        values.append("NA" if statistic is None else _value(statistic, 1e9, 3, latex))
    return "/".join(values)


def render_tables(artifact: dict) -> tuple[str, str]:
    if artifact.get("schema_version") != 3 or artifact.get("run_policy") != "three_predeclared_equal_seeds_no_run_selection":
        raise ProtocolError("Publication tables require the complete frozen nine-run aggregate")
    rows = artifact["rows"]
    header = (
        "| Model | Runs | Params M | Peak VRAM MB | mAP50:95 | mAP50 | P | R | F1 | FAR | "
        "Fwd p50 ms | Tensor→det p50 ms | p95 ms | p99 ms | FPS | FLOPs G (T/P) | FP16 MB |\n"
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|\n"
    )
    markdown = header + "".join(
        f"| {row['model_id']} | {row['runs']} | {_value(row['parameters'], 1e6, 3)} | "
        f"{_value(row['peak_allocated_vram_bytes'], 1e6, 2)} | {_value(row['map_50_95'])} | "
        f"{_value(row['map_50'])} | {_value(row['precision'])} | {_value(row['recall'])} | "
        f"{_value(row['micro_f1'])} | {_value(row['far_per_100_negative_frames'])} | "
        f"{_value(row['model_forward_p50_ms'], digits=3)} | "
        f"{_value(row['tensor_to_final_detections_p50_ms'], digits=3)} | "
        f"{_value(row['tensor_to_final_detections_p95_ms'], digits=3)} | "
        f"{_value(row['tensor_to_final_detections_p99_ms'], digits=3)} | "
        f"{_value(row['tensor_to_final_detections_sustained_fps'], digits=2)} | {_flops(row)} | "
        f"{_value(row['inference_artifact_bytes'], 1e6, 3)} |\n"
        for row in rows
    )
    markdown += "\nPer-class AP50:95 (mean ± sample SD across seeds 13, 37, and 73):\n\n"
    markdown += "| Model | Yawning | Hand over mouth | Drinking | Phone use |\n|---|---:|---:|---:|---:|\n"
    markdown += "".join(
        f"| {row['model_id']} | {_value(row['per_class_ap_50_95']['yawning'])} | "
        f"{_value(row['per_class_ap_50_95']['hand_over_mouth'])} | "
        f"{_value(row['per_class_ap_50_95']['drinking'])} | "
        f"{_value(row['per_class_ap_50_95']['phone_use'])} |\n"
        for row in rows
    )

    latex = (
        "\\begin{tabular}{lrrrrrrrrrrrrrrrr}\n"
        "Model & Runs & Params & VRAM & mAP & mAP50 & P & R & F1 & FAR & Fwd50 & T2D50 & T2D95 & T2D99 & FPS & FLOPs & MB \\\\\n"
        "\\hline\n"
        + "".join(
            f"{row['model_id']} & {row['runs']} & {_value(row['parameters'], 1e6, 3, True)} & "
            f"{_value(row['peak_allocated_vram_bytes'], 1e6, 2, True)} & {_value(row['map_50_95'], latex=True)} & "
            f"{_value(row['map_50'], latex=True)} & {_value(row['precision'], latex=True)} & "
            f"{_value(row['recall'], latex=True)} & {_value(row['micro_f1'], latex=True)} & "
            f"{_value(row['far_per_100_negative_frames'], latex=True)} & "
            f"{_value(row['model_forward_p50_ms'], digits=3, latex=True)} & "
            f"{_value(row['tensor_to_final_detections_p50_ms'], digits=3, latex=True)} & "
            f"{_value(row['tensor_to_final_detections_p95_ms'], digits=3, latex=True)} & "
            f"{_value(row['tensor_to_final_detections_p99_ms'], digits=3, latex=True)} & "
            f"{_value(row['tensor_to_final_detections_sustained_fps'], digits=2, latex=True)} & "
            f"{_flops(row, True)} & {_value(row['inference_artifact_bytes'], 1e6, 3, True)} \\\\\n"
            for row in rows
        )
        + "\\end{tabular}\n"
    )
    return markdown, latex


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--aggregate", required=True)
    parser.add_argument("--markdown", required=True)
    parser.add_argument("--latex", required=True)
    args = parser.parse_args()
    with resolve_repo_path(args.aggregate).open("r", encoding="utf-8") as handle:
        artifact = json.load(handle)
    markdown, latex = render_tables(artifact)
    for destination, output in ((resolve_repo_path(args.markdown), markdown), (resolve_repo_path(args.latex), latex)):
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(output, encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
