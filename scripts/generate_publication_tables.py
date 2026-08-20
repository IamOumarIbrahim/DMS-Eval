"""Generate Markdown and LaTeX tables from a complete aggregate result artifact."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.protocol import resolve_repo_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--aggregate", required=True)
    parser.add_argument("--markdown", required=True)
    parser.add_argument("--latex", required=True)
    args = parser.parse_args()
    with resolve_repo_path(args.aggregate).open("r", encoding="utf-8") as handle:
        rows = json.load(handle)["rows"]
    header = "| Model | mAP50:95 | mAP50 | Precision | Recall | F1 | FAR | p50 ms | p95 ms | p99 ms | FPS |\n|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|\n"
    markdown = header + "".join(
        f"| {row['model_id']} | {row['map_50_95']:.4f} | {row['map_50']:.4f} | {row['precision']:.4f} | {row['recall']:.4f} | {row['micro_f1']:.4f} | {row['far_per_100_negative_frames']:.4f} | {row['p50_ms']:.3f} | {row['p95_ms']:.3f} | {row['p99_ms']:.3f} | {row['sustained_fps']:.2f} |\n"
        for row in rows
    )
    latex = "\\begin{tabular}{lrrrrrrrrrr}\nModel & mAP & mAP50 & P & R & F1 & FAR & p50 & p95 & p99 & FPS \\\\\n\\hline\n" + "".join(
        f"{row['model_id']} & {row['map_50_95']:.4f} & {row['map_50']:.4f} & {row['precision']:.4f} & {row['recall']:.4f} & {row['micro_f1']:.4f} & {row['far_per_100_negative_frames']:.4f} & {row['p50_ms']:.3f} & {row['p95_ms']:.3f} & {row['p99_ms']:.3f} & {row['sustained_fps']:.2f} \\\\\n"
        for row in rows
    ) + "\\end{tabular}\n"
    for destination, content in ((resolve_repo_path(args.markdown), markdown), (resolve_repo_path(args.latex), latex)):
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
