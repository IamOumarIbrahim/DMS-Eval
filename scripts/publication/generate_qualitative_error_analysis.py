"""Generate the pre-registered qualitative/error report without re-reading the test set."""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from core.protocol import TRAINING_SEEDS, ProtocolError, resolve_repo_path, sha256_file
from core.qualitative import CATEGORIES


MODELS = ("yolo11n", "yolo26n", "dfine_n")
REFERENCE_SEED = 13


def _mean_sd(values: list[int]) -> str:
    return f"{statistics.mean(values):.2f} ± {statistics.stdev(values):.2f}"


def load_analyses(result_paths: list[str | Path]) -> dict[tuple[str, int], dict[str, Any]]:
    analyses: dict[tuple[str, int], dict[str, Any]] = {}
    suite_ids: set[str] = set()
    for source in result_paths:
        result_path = resolve_repo_path(source)
        with result_path.open("r", encoding="utf-8") as handle:
            result = json.load(handle)
        if result.get("artifact") != "protected_test_result":
            raise ProtocolError(f"Not a protected result: {result_path}")
        if not result.get("suite_id"):
            raise ProtocolError(f"Protected result lacks a frozen-suite identity: {result_path}")
        suite_ids.add(result["suite_id"])
        key = (result.get("model_id"), result.get("training_seed"))
        if key in analyses:
            raise ProtocolError(f"Duplicate qualitative run: {key}")
        reference = result.get("qualitative_analysis", {})
        analysis_path = resolve_repo_path(reference.get("path", ""))
        if not analysis_path.is_file() or sha256_file(analysis_path) != reference.get("sha256"):
            raise ProtocolError(f"Qualitative artifact integrity failure: {result_path}")
        with analysis_path.open("r", encoding="utf-8") as handle:
            analysis = json.load(handle)
        if analysis.get("artifact") != "qualitative_error_analysis" or (
            analysis.get("model_id"), analysis.get("training_seed")
        ) != key:
            raise ProtocolError(f"Qualitative artifact identity mismatch: {analysis_path}")
        analyses[key] = analysis
    required = {(model, seed) for model in MODELS for seed in TRAINING_SEEDS}
    if set(analyses) != required:
        raise ProtocolError(f"Qualitative generation requires all nine runs; missing {sorted(required - set(analyses))}")
    if len(suite_ids) != 1:
        raise ProtocolError("Qualitative results must belong to one pre-test frozen suite")
    return analyses


def render_markdown(analyses: dict[tuple[str, int], dict[str, Any]]) -> str:
    labels = {
        "correct_detection": "Correct detections",
        "false_positive_negative_frame": "FP negative frames",
        "false_negative": "False-negative images",
        "class_confusion": "Class-confusion images",
        "localization_error": "Localization-error images",
    }
    output = (
        "# Pre-registered qualitative and error analysis\n\n"
        "Counts are mean ± sample SD across the fixed seeds 13, 37, and 73. Examples are selected "
        "deterministically during each protected pass; the publication contact sheet uses only seed 13, "
        "which was fixed before training.\n\n"
        "| Model | TP | FP | FN | " + " | ".join(labels[category] for category in CATEGORIES) + " |\n"
        "|---|---:|---:|---:|" + "---:|" * len(CATEGORIES) + "\n"
    )
    for model in MODELS:
        runs = [analyses[(model, seed)] for seed in TRAINING_SEEDS]
        fields = ("tp", "fp", "fn", *CATEGORIES)
        output += f"| {model} | " + " | ".join(_mean_sd([run["counts"][field] for run in runs]) for field in fields) + " |\n"
    output += "\nClass-confusion pairs use `ground-truth→prediction` class IDs and are reported without selecting a favorable seed.\n"
    return output


def render_contact_sheet(analyses: dict[tuple[str, int], dict[str, Any]], destination: str | Path) -> Path:
    cell_width, cell_height, label_height = 320, 240, 32
    sheet = Image.new("RGB", (cell_width * len(MODELS), (cell_height + label_height) * len(CATEGORIES)), "white")
    draw = ImageDraw.Draw(sheet)
    for row, category in enumerate(CATEGORIES):
        for column, model in enumerate(MODELS):
            x, y = column * cell_width, row * (cell_height + label_height)
            examples = analyses[(model, REFERENCE_SEED)]["examples"][category]
            if examples:
                rendered = resolve_repo_path(examples[0]["rendered_path"])
                if sha256_file(rendered) != examples[0]["rendered_sha256"]:
                    raise ProtocolError(f"Rendered qualitative example changed: {rendered}")
                with Image.open(rendered) as image:
                    thumbnail = ImageOps.contain(image.convert("RGB"), (cell_width, cell_height))
                sheet.paste(thumbnail, (x + (cell_width - thumbnail.width) // 2, y + (cell_height - thumbnail.height) // 2))
            else:
                draw.text((x + 10, y + cell_height // 2), "No qualifying example", fill="black")
            draw.rectangle((x, y, x + cell_width - 1, y + cell_height + label_height - 1), outline="black")
            draw.text((x + 5, y + cell_height + 8), f"{model} · {category}", fill="black")
    output = resolve_repo_path(destination)
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output, format="PNG")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", nargs="+", help="The nine protected result JSON files")
    parser.add_argument("--markdown", required=True)
    parser.add_argument("--contact-sheet", required=True)
    args = parser.parse_args()
    analyses = load_analyses(args.results)
    markdown = resolve_repo_path(args.markdown)
    markdown.parent.mkdir(parents=True, exist_ok=True)
    markdown.write_text(render_markdown(analyses), encoding="utf-8", newline="\n")
    render_contact_sheet(analyses, args.contact_sheet)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
