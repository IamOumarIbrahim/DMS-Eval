"""Generate publication assets from the complete canonical benchmark aggregate.

This module never performs inference and never opens dataset images.  It consumes
only the saved aggregate and its nine protected-result source files.  A dry-run
mode accepts the clearly marked fixture produced by ``--create-mock-fixture`` and
writes only below ``manuscript/generated/dry_run``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import shutil
import statistics
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parents[2]
MANUSCRIPT_DIR = REPO_ROOT / "manuscript"
MANUAL_RESULTS_PATH = MANUSCRIPT_DIR / "manual_results.json"
SENTINEL = "TO_BE_UPDATED"
MODELS = ("yolo11n", "yolo26n", "dfine_n")
SEEDS = (13, 37, 73)
CLASSES = ("phone_use", "drinking", "yawning", "hand_over_mouth")
MODEL_LABELS = {
    "yolo11n": "YOLO11n",
    "yolo26n": "YOLO26n",
    "dfine_n": "D-FINE-N",
}
MODEL_MACROS = {
    "yolo11n": "YOLOElevenN",
    "yolo26n": "YOLOTwentySixN",
    "dfine_n": "DFINEN",
}
SEED_MACROS = {13: "Thirteen", 37: "ThirtySeven", 73: "SeventyThree"}
CLASS_MACROS = {
    "phone_use": "PhoneUse",
    "drinking": "Drinking",
    "yawning": "Yawning",
    "hand_over_mouth": "HandOverMouth",
}
PALETTE = {
    "yolo11n": "#0072B2",
    "yolo26n": "#E69F00",
    "dfine_n": "#009E73",
}

NUMERIC_FIELDS = (
    "map_50_95",
    "map_50",
    "precision",
    "recall",
    "micro_f1",
    "far_per_100_negative_frames",
    "model_forward_p50_ms",
    "model_forward_p95_ms",
    "model_forward_p99_ms",
    "model_forward_sustained_fps",
    "tensor_to_final_detections_p50_ms",
    "tensor_to_final_detections_p95_ms",
    "tensor_to_final_detections_p99_ms",
    "tensor_to_final_detections_sustained_fps",
    "peak_allocated_vram_bytes",
    "parameters",
    "inference_artifact_bytes",
)

PROBABILITY_FIELDS = {"map_50_95", "map_50", "precision", "recall", "micro_f1"}
POSITIVE_FIELDS = {
    "model_forward_p50_ms",
    "model_forward_p95_ms",
    "model_forward_p99_ms",
    "model_forward_sustained_fps",
    "tensor_to_final_detections_p50_ms",
    "tensor_to_final_detections_p95_ms",
    "tensor_to_final_detections_p99_ms",
    "tensor_to_final_detections_sustained_fps",
    "peak_allocated_vram_bytes",
    "parameters",
    "inference_artifact_bytes",
}

METRIC_MACROS = {
    "map_50_95": "MapFiftyNinetyFive",
    "map_50": "MapFifty",
    "precision": "Precision",
    "recall": "Recall",
    "micro_f1": "MicroFOne",
    "far_per_100_negative_frames": "FARPerHundred",
    "model_forward_p50_ms": "ForwardPFifty",
    "model_forward_p95_ms": "ForwardPNinetyFive",
    "model_forward_p99_ms": "ForwardPNinetyNine",
    "model_forward_sustained_fps": "ForwardFPS",
    "tensor_to_final_detections_p50_ms": "TensorDetectionPFifty",
    "tensor_to_final_detections_p95_ms": "TensorDetectionPNinetyFive",
    "tensor_to_final_detections_p99_ms": "TensorDetectionPNinetyNine",
    "tensor_to_final_detections_sustained_fps": "TensorDetectionFPS",
    "peak_allocated_vram_bytes": "PeakVRAM",
    "parameters": "Parameters",
    "inference_artifact_bytes": "ModelSize",
}


class AssetError(RuntimeError):
    """Fail-closed manuscript asset error."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", newline="\n", delete=False, dir=path.parent, suffix=".tmp"
    ) as handle:
        handle.write(text)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def atomic_write_json(path: Path, payload: Any) -> None:
    atomic_write_text(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


def finite_number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise AssetError(f"{label} must be numeric")
    number = float(value)
    if not math.isfinite(number):
        raise AssetError(f"{label} must be finite")
    return number


def validate_value(field: str, value: Any, label: str) -> float:
    number = finite_number(value, label)
    if field in PROBABILITY_FIELDS and not 0.0 <= number <= 1.0:
        raise AssetError(f"{label} must be in [0, 1]")
    if field == "far_per_100_negative_frames" and number < 0.0:
        raise AssetError(f"{label} cannot be negative")
    if field in POSITIVE_FIELDS and number <= 0.0:
        raise AssetError(f"{label} must be positive")
    if field.endswith("_ms") and number > 1_000_000:
        raise AssetError(f"{label} is not a plausible millisecond value")
    if field.endswith("_bytes") and number > 2**50:
        raise AssetError(f"{label} is not a plausible byte count")
    return number


def sample_stats(values: Iterable[float]) -> dict[str, float]:
    numbers = list(values)
    if len(numbers) != 3:
        raise AssetError("Every model statistic requires exactly three seeds")
    return {"mean": statistics.mean(numbers), "sample_std": statistics.stdev(numbers)}


def close_enough(left: float, right: float) -> bool:
    return math.isclose(left, right, rel_tol=1e-9, abs_tol=1e-12)


def resolve_source(source: str) -> Path:
    path = Path(source)
    if not path.is_absolute():
        path = REPO_ROOT / path
    return path.resolve()


def portable_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def validate_aggregate(aggregate: dict[str, Any], aggregate_path: Path, *, dry_run: bool) -> dict[str, Any]:
    if aggregate.get("artifact") != "dms_eval_aggregate" or aggregate.get("schema_version") != 3:
        raise AssetError("Input is not the canonical schema-version-3 DMS-Eval aggregate")
    if aggregate.get("run_policy") != "three_predeclared_equal_seeds_no_run_selection":
        raise AssetError("Aggregate run policy does not prohibit run selection")
    if aggregate.get("dispersion") != "sample_standard_deviation":
        raise AssetError("Aggregate dispersion is not sample standard deviation")
    if aggregate.get("training_seeds") != list(SEEDS):
        raise AssetError(f"Aggregate seeds must be exactly {list(SEEDS)}")
    is_fixture = aggregate.get("fixture") is True
    if dry_run != is_fixture:
        mode = "dry-run fixture" if dry_run else "canonical non-fixture aggregate"
        raise AssetError(f"Expected a {mode}")

    runs = aggregate.get("runs")
    rows = aggregate.get("rows")
    if not isinstance(runs, list) or len(runs) != 9:
        raise AssetError("Exactly nine individual run rows are required")
    if not isinstance(rows, list) or len(rows) != 3:
        raise AssetError("Exactly three model aggregate rows are required")

    expected_matrix = {(model, seed) for model in MODELS for seed in SEEDS}
    seen_matrix: set[tuple[str, int]] = set()
    seen_sources: set[Path] = set()
    source_hashes: list[dict[str, str]] = []
    suite_ids: set[str] = set()

    for run in runs:
        model = run.get("model_id")
        seed = run.get("training_seed")
        key = (model, seed)
        if key not in expected_matrix:
            raise AssetError(f"Unexpected model-seed row: {key}")
        if key in seen_matrix:
            raise AssetError(f"Duplicate model-seed row: {key}")
        seen_matrix.add(key)
        source_text = str(run.get("source", ""))
        if "backup_epoch120" in source_text.lower() or "_backup_" in source_text.lower():
            raise AssetError(f"Historical backup artifact is forbidden: {source_text}")
        source_path = resolve_source(source_text)
        if source_path in seen_sources:
            raise AssetError(f"Duplicated protected-result source: {source_path}")
        if not source_path.is_file():
            raise AssetError(f"Protected-result source is missing: {source_path}")
        seen_sources.add(source_path)
        source_hashes.append({"path": portable_path(source_path), "sha256": sha256_file(source_path)})
        suite_id = run.get("suite_id")
        if not isinstance(suite_id, str) or not suite_id:
            raise AssetError(f"Missing suite_id for {key}")
        suite_ids.add(suite_id)
        for field in NUMERIC_FIELDS:
            validate_value(field, run.get(field), f"{model}/seed-{seed}/{field}")
        class_values = run.get("per_class_ap_50_95")
        if not isinstance(class_values, dict) or set(class_values) != set(CLASSES):
            raise AssetError(f"Per-class AP keys are incomplete for {key}")
        for class_name, value in class_values.items():
            validate_value("map_50_95", value, f"{model}/seed-{seed}/{class_name}")
        estimates = run.get("flop_estimates")
        if not isinstance(estimates, dict):
            raise AssetError(f"FLOP estimates are missing for {key}")
        for estimator in ("thop", "torch_profiler"):
            estimate = estimates.get(estimator)
            if not isinstance(estimate, dict):
                raise AssetError(f"{estimator} FLOP estimate is missing for {key}")
            value = finite_number(estimate.get("flops"), f"{model}/seed-{seed}/{estimator}/flops")
            if value <= 0:
                raise AssetError(f"{model}/seed-{seed}/{estimator}/flops must be positive")

    if seen_matrix != expected_matrix:
        raise AssetError(f"Incomplete model-seed matrix: missing {sorted(expected_matrix - seen_matrix)}")
    if len(suite_ids) != 1:
        raise AssetError("All nine runs must belong to one frozen suite")

    row_by_model: dict[str, dict[str, Any]] = {}
    for row in rows:
        model = row.get("model_id")
        if model not in MODELS or model in row_by_model:
            raise AssetError(f"Missing or duplicated model aggregate row: {model}")
        if row.get("runs") != 3 or row.get("training_seeds") != list(SEEDS):
            raise AssetError(f"Aggregate row for {model} does not preserve all three seeds")
        row_by_model[model] = row
    if set(row_by_model) != set(MODELS):
        raise AssetError("Aggregate model rows are incomplete")

    run_by_key = {(run["model_id"], run["training_seed"]): run for run in runs}
    for model in MODELS:
        row = row_by_model[model]
        model_runs = [run_by_key[(model, seed)] for seed in SEEDS]
        for field in NUMERIC_FIELDS:
            stored = row.get(field)
            if not isinstance(stored, dict) or set(stored) != {"mean", "sample_std"}:
                raise AssetError(f"Malformed aggregate statistic {model}/{field}")
            expected = sample_stats(validate_value(field, run[field], f"{model}/{field}") for run in model_runs)
            for statistic in ("mean", "sample_std"):
                actual = validate_value(
                    field if statistic == "mean" else "far_per_100_negative_frames",
                    stored.get(statistic),
                    f"{model}/{field}/{statistic}",
                )
                if statistic == "sample_std" and actual < 0:
                    raise AssetError(f"Negative sample SD for {model}/{field}")
                if not close_enough(actual, expected[statistic]):
                    raise AssetError(f"Aggregate statistic mismatch for {model}/{field}/{statistic}")

        aggregate_classes = row.get("per_class_ap_50_95")
        if not isinstance(aggregate_classes, dict) or set(aggregate_classes) != set(CLASSES):
            raise AssetError(f"Aggregate per-class AP is incomplete for {model}")
        for class_name in CLASSES:
            expected = sample_stats(float(run["per_class_ap_50_95"][class_name]) for run in model_runs)
            stored = aggregate_classes[class_name]
            if not isinstance(stored, dict) or set(stored) != {"mean", "sample_std"}:
                raise AssetError(f"Malformed aggregate per-class AP for {model}/{class_name}")
            for statistic in ("mean", "sample_std"):
                actual = finite_number(stored[statistic], f"{model}/{class_name}/{statistic}")
                if actual < 0 or (statistic == "mean" and actual > 1):
                    raise AssetError(f"Out-of-range per-class AP for {model}/{class_name}/{statistic}")
                if not close_enough(actual, expected[statistic]):
                    raise AssetError(f"Aggregate per-class mismatch for {model}/{class_name}/{statistic}")

        row_flops = row.get("flop_estimates")
        if not isinstance(row_flops, dict):
            raise AssetError(f"Aggregate FLOP estimates are missing for {model}")
        for estimator in ("thop", "torch_profiler"):
            stored = row_flops.get(estimator)
            if not isinstance(stored, dict) or set(stored) != {"mean", "sample_std"}:
                raise AssetError(f"Aggregate {estimator} FLOPs are incomplete for {model}")
            expected = sample_stats(float(run["flop_estimates"][estimator]["flops"]) for run in model_runs)
            for statistic in ("mean", "sample_std"):
                actual = finite_number(stored[statistic], f"{model}/{estimator}/{statistic}")
                if actual < 0 or (statistic == "mean" and actual == 0):
                    raise AssetError(f"Invalid aggregate FLOP value for {model}/{estimator}/{statistic}")
                if not close_enough(actual, expected[statistic]):
                    raise AssetError(f"Aggregate FLOP mismatch for {model}/{estimator}/{statistic}")

    return {
        "aggregate": aggregate,
        "aggregate_path": aggregate_path.resolve(),
        "row_by_model": row_by_model,
        "run_by_key": run_by_key,
        "source_hashes": sorted(source_hashes, key=lambda item: item["path"]),
        "suite_id": next(iter(suite_ids)),
    }


def format_metric(field: str, value: float) -> str:
    if field in PROBABILITY_FIELDS:
        return f"{value:.3f}"
    if field == "far_per_100_negative_frames":
        return f"{value:.2f}"
    if field.endswith("_ms"):
        return f"{value:.2f}"
    if field.endswith("_fps"):
        return f"{value:.1f}"
    if field == "parameters":
        return f"{value / 1_000_000:.2f}"
    if field in {"peak_allocated_vram_bytes", "inference_artifact_bytes"}:
        return f"{value / (1024**2):.2f}"
    return f"{value:.3f}"


def format_flops(value: float) -> str:
    return f"{value / 1_000_000_000:.2f}"


def latex_escape(text: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(character, character) for character in text)


def all_value_macro_names() -> list[str]:
    names: list[str] = []
    for model in MODELS:
        prefix = MODEL_MACROS[model]
        for field in NUMERIC_FIELDS:
            metric = METRIC_MACROS[field]
            names.extend((f"{prefix}{metric}Mean", f"{prefix}{metric}SD"))
            for seed in SEEDS:
                names.append(f"{prefix}Seed{SEED_MACROS[seed]}{metric}")
        for estimator in ("THOP", "Profiler"):
            names.extend((f"{prefix}FLOPs{estimator}Mean", f"{prefix}FLOPs{estimator}SD"))
            for seed in SEEDS:
                names.append(f"{prefix}Seed{SEED_MACROS[seed]}FLOPs{estimator}")
        for class_name in CLASSES:
            class_macro = CLASS_MACROS[class_name]
            names.extend((f"{prefix}{class_macro}APMean", f"{prefix}{class_macro}APSD"))
            for seed in SEEDS:
                names.append(f"{prefix}Seed{SEED_MACROS[seed]}{class_macro}AP")
        names.append(f"{prefix}TrainingDuration")
    names.extend(
        (
            "FastestModel",
            "HighestAccuracyModel",
            "BestTradeoffModel",
            "AbstractResultSentence",
            "ResultsComparisonSentence",
            "DiscussionTradeoffSentence",
            "ConclusionResultSentence",
        )
    )
    return names


def placeholder_macros() -> str:
    lines = [
        "% AUTO-GENERATED PLACEHOLDERS. DO NOT EDIT BY HAND.",
        r"\providecommand{\DMSPending}{\texttt{TO\_BE\_UPDATED}}",
    ]
    for name in all_value_macro_names():
        lines.append(rf"\providecommand{{\{name}}}{{\DMSPending}}")
    return "\n".join(lines) + "\n"


def load_manual_results() -> dict[str, Any]:
    if not MANUAL_RESULTS_PATH.is_file():
        raise AssetError(f"Manual result registry is missing: {MANUAL_RESULTS_PATH}")
    payload = json.loads(MANUAL_RESULTS_PATH.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or set(payload) != {
        "schema_version",
        "training_duration_hours",
        "best_tradeoff_model",
        "discussion_tradeoff_sentence",
    }:
        raise AssetError("Manual result registry has unexpected keys")
    if payload.get("schema_version") != 1:
        raise AssetError("Manual result registry schema version must be 1")
    durations = payload.get("training_duration_hours")
    if not isinstance(durations, dict) or set(durations) != set(MODELS):
        raise AssetError("Manual training-duration registry must contain exactly the three model IDs")
    clean_durations: dict[str, float | None] = {}
    for model in MODELS:
        value = durations[model]
        if value == SENTINEL:
            clean_durations[model] = None
        else:
            number = finite_number(value, f"manual training duration/{model}")
            if number <= 0 or number > 10_000:
                raise AssetError(f"Manual training duration for {model} is not plausible")
            clean_durations[model] = number
    tradeoff = payload.get("best_tradeoff_model")
    if tradeoff != SENTINEL and tradeoff not in MODELS:
        raise AssetError(f"Manual best_tradeoff_model must be one of {list(MODELS)}")
    discussion = payload.get("discussion_tradeoff_sentence")
    if discussion != SENTINEL and (not isinstance(discussion, str) or len(discussion.strip()) < 20):
        raise AssetError("Manual discussion trade-off sentence is too short")
    return {
        "training_duration_hours": clean_durations,
        "best_tradeoff_model": None if tradeoff == SENTINEL else tradeoff,
        "discussion_tradeoff_sentence": None if discussion == SENTINEL else discussion.strip(),
    }


def result_macros(context: dict[str, Any], manual: dict[str, Any]) -> str:
    rows = context["row_by_model"]
    runs = context["run_by_key"]
    lines = [
        "% AUTO-GENERATED FROM THE COMPLETE CANONICAL AGGREGATE. DO NOT EDIT.",
        r"\providecommand{\DMSPending}{\texttt{TO\_BE\_UPDATED}}",
    ]
    values: dict[str, str] = {}
    for model in MODELS:
        prefix = MODEL_MACROS[model]
        row = rows[model]
        for field in NUMERIC_FIELDS:
            metric = METRIC_MACROS[field]
            values[f"{prefix}{metric}Mean"] = format_metric(field, float(row[field]["mean"]))
            values[f"{prefix}{metric}SD"] = format_metric(field, float(row[field]["sample_std"]))
            for seed in SEEDS:
                values[f"{prefix}Seed{SEED_MACROS[seed]}{metric}"] = format_metric(
                    field, float(runs[(model, seed)][field])
                )
        for estimator, macro in (("thop", "THOP"), ("torch_profiler", "Profiler")):
            values[f"{prefix}FLOPs{macro}Mean"] = format_flops(float(row["flop_estimates"][estimator]["mean"]))
            values[f"{prefix}FLOPs{macro}SD"] = format_flops(float(row["flop_estimates"][estimator]["sample_std"]))
            for seed in SEEDS:
                values[f"{prefix}Seed{SEED_MACROS[seed]}FLOPs{macro}"] = format_flops(
                    float(runs[(model, seed)]["flop_estimates"][estimator]["flops"])
                )
        for class_name in CLASSES:
            class_macro = CLASS_MACROS[class_name]
            values[f"{prefix}{class_macro}APMean"] = f"{float(row['per_class_ap_50_95'][class_name]['mean']):.3f}"
            values[f"{prefix}{class_macro}APSD"] = f"{float(row['per_class_ap_50_95'][class_name]['sample_std']):.3f}"
            for seed in SEEDS:
                values[f"{prefix}Seed{SEED_MACROS[seed]}{class_macro}AP"] = (
                    f"{float(runs[(model, seed)]['per_class_ap_50_95'][class_name]):.3f}"
                )
        duration = manual["training_duration_hours"][model]
        values[f"{prefix}TrainingDuration"] = r"\DMSPending" if duration is None else f"{duration:.2f}~h"

    accuracy_model = max(MODELS, key=lambda model: (rows[model]["map_50_95"]["mean"], -MODELS.index(model)))
    fastest_model = min(
        MODELS,
        key=lambda model: (rows[model]["tensor_to_final_detections_p50_ms"]["mean"], MODELS.index(model)),
    )
    values["HighestAccuracyModel"] = MODEL_LABELS[accuracy_model]
    values["FastestModel"] = MODEL_LABELS[fastest_model]
    tradeoff_model = manual["best_tradeoff_model"]
    values["BestTradeoffModel"] = r"\DMSPending" if tradeoff_model is None else MODEL_LABELS[tradeoff_model]

    accuracy_value = format_metric("map_50_95", rows[accuracy_model]["map_50_95"]["mean"])
    accuracy_sd = format_metric("map_50_95", rows[accuracy_model]["map_50_95"]["sample_std"])
    latency_value = format_metric(
        "tensor_to_final_detections_p50_ms",
        rows[fastest_model]["tensor_to_final_detections_p50_ms"]["mean"],
    )
    latency_sd = format_metric(
        "tensor_to_final_detections_p50_ms",
        rows[fastest_model]["tensor_to_final_detections_p50_ms"]["sample_std"],
    )
    values["AbstractResultSentence"] = latex_escape(
        f"{MODEL_LABELS[accuracy_model]} attained the highest mean mAP@0.5:0.95 "
        f"({accuracy_value} ± {accuracy_sd}), while {MODEL_LABELS[fastest_model]} had the lowest "
        f"tensor-to-final-detections median latency ({latency_value} ± {latency_sd} ms)."
    ).replace("±", r"$\pm$")
    values["ResultsComparisonSentence"] = latex_escape(
        f"The highest mean protected-test mAP@0.5:0.95 was obtained by {MODEL_LABELS[accuracy_model]} "
        f"({accuracy_value}), and the lowest mean tensor-to-final-detections p50 latency was obtained "
        f"by {MODEL_LABELS[fastest_model]} ({latency_value} ms); all values summarize n=3 seeds."
    )
    discussion = manual["discussion_tradeoff_sentence"]
    values["DiscussionTradeoffSentence"] = r"\DMSPending" if discussion is None else latex_escape(discussion)
    values["ConclusionResultSentence"] = latex_escape(
        f"Under the frozen configured-system protocol, {MODEL_LABELS[accuracy_model]} yielded the "
        f"highest mean mAP@0.5:0.95 and {MODEL_LABELS[fastest_model]} yielded the lowest mean "
        f"tensor-to-final-detections p50 latency across the three retained seeds."
    )

    for name in all_value_macro_names():
        value = values.get(name, r"\DMSPending")
        lines.append(rf"\providecommand{{\{name}}}{{{value}}}")
    return "\n".join(lines) + "\n"


def placeholder_primary_table() -> str:
    return r"""% AUTO-GENERATED PLACEHOLDER TABLE. DO NOT EDIT.
\begin{table*}[t]
\caption{Protected-test quality, latency, and resources (mean $\pm$ sample SD, $n=3$ seeds).}
\label{tab:primary-results}
\centering
\textit{(a) Detection quality and operating point}\par\smallskip
\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}lcccccc}
\toprule
Model & mAP@.5:.95 & mAP@.5 & Precision & Recall & F1 & FAR$_{100}$ \\
\midrule
YOLO11n & \DMSPending & \DMSPending & \DMSPending & \DMSPending & \DMSPending & \DMSPending \\
YOLO26n & \DMSPending & \DMSPending & \DMSPending & \DMSPending & \DMSPending & \DMSPending \\
D-FINE-N & \DMSPending & \DMSPending & \DMSPending & \DMSPending & \DMSPending & \DMSPending \\
\bottomrule
\end{tabular*}
\par\medskip
\textit{(b) Batch-1 latency}\par\smallskip
\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}lcccc}
\toprule
Model & Forward p50 (ms) & T$\rightarrow$D p50 (ms) & T$\rightarrow$D p95 (ms) & T$\rightarrow$D FPS \\
\midrule
YOLO11n & \DMSPending & \DMSPending & \DMSPending & \DMSPending \\
YOLO26n & \DMSPending & \DMSPending & \DMSPending & \DMSPending \\
D-FINE-N & \DMSPending & \DMSPending & \DMSPending & \DMSPending \\
\bottomrule
\end{tabular*}
\par\medskip
\textit{(c) Resources}\par\smallskip
\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}lccccc}
\toprule
Model & Params (M) & THOP FLOPs (G) & Profiler FLOPs (G) & Peak VRAM (MiB) & FP16 (MiB) \\
\midrule
YOLO11n & \DMSPending & \DMSPending & \DMSPending & \DMSPending & \DMSPending \\
YOLO26n & \DMSPending & \DMSPending & \DMSPending & \DMSPending & \DMSPending \\
D-FINE-N & \DMSPending & \DMSPending & \DMSPending & \DMSPending & \DMSPending \\
\bottomrule
\end{tabular*}
\end{table*}
"""


def aggregate_primary_table(context: dict[str, Any]) -> str:
    rows = context["row_by_model"]
    quality_body = []
    latency_body = []
    resource_body = []
    for model in MODELS:
        row = rows[model]
        pair = lambda field: (
            f"{format_metric(field, row[field]['mean'])} $\\pm$ "
            f"{format_metric(field, row[field]['sample_std'])}"
        )
        quality_body.append(
            " & ".join(
                (
                    MODEL_LABELS[model],
                    pair("map_50_95"),
                    pair("map_50"),
                    pair("precision"),
                    pair("recall"),
                    pair("micro_f1"),
                    pair("far_per_100_negative_frames"),
                )
            )
            + r" \\"
        )
        latency_body.append(
            " & ".join(
                (
                    MODEL_LABELS[model],
                    pair("model_forward_p50_ms"),
                    pair("tensor_to_final_detections_p50_ms"),
                    pair("tensor_to_final_detections_p95_ms"),
                    pair("tensor_to_final_detections_sustained_fps"),
                )
            )
            + r" \\"
        )
        resource_body.append(
            " & ".join(
                (
                    MODEL_LABELS[model],
                    pair("parameters"),
                    f"{format_flops(row['flop_estimates']['thop']['mean'])} $\\pm$ "
                    f"{format_flops(row['flop_estimates']['thop']['sample_std'])}",
                    f"{format_flops(row['flop_estimates']['torch_profiler']['mean'])} $\\pm$ "
                    f"{format_flops(row['flop_estimates']['torch_profiler']['sample_std'])}",
                    pair("peak_allocated_vram_bytes"),
                    pair("inference_artifact_bytes"),
                )
            )
            + r" \\"
        )
    template = placeholder_primary_table().replace("PLACEHOLDER TABLE", "FINAL TABLE")
    first_start = template.index("\\midrule\n") + len("\\midrule\n")
    first_end = template.index("\\bottomrule", first_start)
    template = template[:first_start] + "\n".join(quality_body) + "\n" + template[first_end:]
    second_start = template.index("\\midrule\n", first_start) + len("\\midrule\n")
    second_end = template.index("\\bottomrule", second_start)
    template = template[:second_start] + "\n".join(latency_body) + "\n" + template[second_end:]
    third_start = template.index("\\midrule\n", second_start) + len("\\midrule\n")
    third_end = template.index("\\bottomrule", third_start)
    return template[:third_start] + "\n".join(resource_body) + "\n" + template[third_end:]


def placeholder_per_class_table() -> str:
    return r"""% AUTO-GENERATED PLACEHOLDER TABLE. DO NOT EDIT.
\begin{table}[t]
\caption{Per-class AP@0.5:0.95 (mean $\pm$ sample SD, $n=3$).}
\label{tab:per-class}
\centering
\resizebox{\columnwidth}{!}{%
\begin{tabular}{lcccc}
\toprule
Model & Phone use & Drinking & Yawning & Hand over mouth \\
\midrule
YOLO11n & \DMSPending & \DMSPending & \DMSPending & \DMSPending \\
YOLO26n & \DMSPending & \DMSPending & \DMSPending & \DMSPending \\
D-FINE-N & \DMSPending & \DMSPending & \DMSPending & \DMSPending \\
\bottomrule
\end{tabular}}
\end{table}
"""


def aggregate_per_class_table(context: dict[str, Any]) -> str:
    rows = context["row_by_model"]
    body = []
    for model in MODELS:
        cells = [MODEL_LABELS[model]]
        for class_name in CLASSES:
            stat = rows[model]["per_class_ap_50_95"][class_name]
            cells.append(f"{stat['mean']:.3f} $\\pm$ {stat['sample_std']:.3f}")
        body.append(" & ".join(cells) + r" \\")
    template = placeholder_per_class_table().replace("PLACEHOLDER TABLE", "FINAL TABLE")
    start = template.index("\\midrule\n") + len("\\midrule\n")
    end = template.index("\\bottomrule")
    return template[:start] + "\n".join(body) + "\n" + template[end:]


def placeholder_per_seed_table() -> str:
    rows = []
    for model in MODELS:
        for seed in SEEDS:
            rows.append(
                f"{MODEL_LABELS[model]} & {seed} & \\DMSPending & \\DMSPending & \\DMSPending & "
                r"\DMSPending & \DMSPending & \DMSPending & \DMSPending \\"
            )
    return """% AUTO-GENERATED PLACEHOLDER TABLE. DO NOT EDIT.
\\begin{table*}[t]
\\caption{Individual protected-test seed results retained without run selection.}
\\label{tab:per-seed-results}
\\centering
\\resizebox{\\textwidth}{!}{%
\\begin{tabular}{lcccccccc}
\\toprule
Model & Seed & mAP@.5:.95 & mAP@.5 & P & R & F1 & T$\\rightarrow$D p50 (ms) & FPS \\\\
\\midrule
""" + "\n".join(rows) + """
\\bottomrule
\\end{tabular}}
\\end{table*}
"""


def aggregate_per_seed_table(context: dict[str, Any]) -> str:
    runs = context["run_by_key"]
    rows = []
    for model in MODELS:
        for seed in SEEDS:
            run = runs[(model, seed)]
            fields = (
                "map_50_95",
                "map_50",
                "precision",
                "recall",
                "micro_f1",
                "tensor_to_final_detections_p50_ms",
                "tensor_to_final_detections_sustained_fps",
            )
            cells = [MODEL_LABELS[model], str(seed)] + [format_metric(field, run[field]) for field in fields]
            rows.append(" & ".join(cells) + r" \\")
    template = placeholder_per_seed_table()
    start = template.index("\\midrule\n") + len("\\midrule\n")
    end = template.index("\\bottomrule")
    return template[:start] + "\n".join(rows) + "\n" + template[end:].replace("PLACEHOLDER TABLE", "FINAL TABLE")


def import_plotting() -> Any:
    try:
        import matplotlib

        matplotlib.use("Agg")
        matplotlib.rcParams.update(
            {
                "font.family": "DejaVu Sans",
                "font.size": 7.5,
                "axes.labelsize": 8,
                "axes.titlesize": 8.5,
                "legend.fontsize": 7,
                "xtick.labelsize": 7,
                "ytick.labelsize": 7,
                "pdf.fonttype": 42,
                "ps.fonttype": 42,
                "svg.hashsalt": "dms-eval-manuscript-assets-v1",
                "svg.fonttype": "none",
            }
        )
        import matplotlib.pyplot as plt

        return plt
    except ImportError as exc:
        raise AssetError("matplotlib is required to generate manuscript figures") from exc


def save_figure(fig: Any, base: Path, *, dry_run: bool) -> None:
    base.parent.mkdir(parents=True, exist_ok=True)
    if dry_run:
        fig.text(
            0.5,
            0.5,
            "MOCK DATA - NOT BENCHMARK RESULTS",
            ha="center",
            va="center",
            fontsize=13,
            color="#D55E00",
            alpha=0.34,
            rotation=24,
            weight="bold",
        )
    for suffix in (".pdf", ".svg", ".png"):
        target = base.with_suffix(suffix)
        target.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(delete=False, dir=target.parent, suffix=suffix) as handle:
            temporary = Path(handle.name)
        metadata: dict[str, Any]
        if suffix == ".pdf":
            metadata = {"Creator": "DMS-Eval deterministic postprocessor", "CreationDate": None, "ModDate": None}
        elif suffix == ".svg":
            metadata = {"Creator": "DMS-Eval deterministic postprocessor", "Date": None}
        else:
            metadata = {"Software": "DMS-Eval deterministic postprocessor"}
        fig.savefig(temporary, dpi=300, bbox_inches="tight", metadata=metadata)
        if suffix == ".svg":
            normalized = "\n".join(line.rstrip() for line in temporary.read_text(encoding="utf-8").splitlines()) + "\n"
            temporary.write_text(normalized, encoding="utf-8", newline="\n")
        os.replace(temporary, target)


def generate_figures(context: dict[str, Any], output_dir: Path, *, dry_run: bool) -> None:
    plt = import_plotting()
    rows = context["row_by_model"]
    colors = [PALETTE[model] for model in MODELS]
    labels = [MODEL_LABELS[model] for model in MODELS]

    fig, ax = plt.subplots(figsize=(3.5, 2.35))
    for model in MODELS:
        row = rows[model]
        ax.errorbar(
            row["tensor_to_final_detections_p50_ms"]["mean"],
            row["map_50_95"]["mean"],
            xerr=row["tensor_to_final_detections_p50_ms"]["sample_std"],
            yerr=row["map_50_95"]["sample_std"],
            fmt="o",
            markersize=6,
            capsize=3,
            color=PALETTE[model],
            label=MODEL_LABELS[model],
        )
    ax.set_xlabel("Tensor-to-final-detections p50 latency (ms)")
    ax.set_ylabel("mAP@0.5:0.95")
    ax.grid(True, alpha=0.25, linewidth=0.5)
    ax.legend(frameon=False)
    ax.set_title("Mean with sample-SD error bars ($n=3$)")
    save_figure(fig, output_dir / "accuracy_efficiency", dry_run=dry_run)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(3.5, 2.35))
    positions = list(range(len(CLASSES)))
    width = 0.24
    for index, model in enumerate(MODELS):
        means = [rows[model]["per_class_ap_50_95"][name]["mean"] for name in CLASSES]
        errors = [rows[model]["per_class_ap_50_95"][name]["sample_std"] for name in CLASSES]
        offsets = [position + (index - 1) * width for position in positions]
        ax.bar(offsets, means, width, yerr=errors, capsize=2, color=colors[index], label=labels[index])
    ax.set_xticks(positions, ("Phone use", "Drinking", "Yawning", "Hand over\nmouth"))
    ax.set_ylabel("AP@0.5:0.95")
    ax.set_ylim(0, 1.05)
    ax.grid(True, axis="y", alpha=0.25, linewidth=0.5)
    ax.legend(frameon=False, ncols=3, loc="upper center")
    ax.set_title("Per-class mean with sample SD ($n=3$)")
    save_figure(fig, output_dir / "per_class_ap", dry_run=dry_run)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(3.5, 2.35))
    positions = list(range(len(MODELS)))
    width = 0.34
    forward_means = [rows[model]["model_forward_p50_ms"]["mean"] for model in MODELS]
    forward_errors = [rows[model]["model_forward_p50_ms"]["sample_std"] for model in MODELS]
    final_means = [rows[model]["tensor_to_final_detections_p50_ms"]["mean"] for model in MODELS]
    final_errors = [rows[model]["tensor_to_final_detections_p50_ms"]["sample_std"] for model in MODELS]
    ax.bar([p - width / 2 for p in positions], forward_means, width, yerr=forward_errors, capsize=2, color="#56B4E9", label="Model only")
    ax.bar([p + width / 2 for p in positions], final_means, width, yerr=final_errors, capsize=2, color="#D55E00", label="Tensor to detections")
    ax.set_xticks(positions, labels)
    ax.set_ylabel("p50 latency (ms)")
    ax.grid(True, axis="y", alpha=0.25, linewidth=0.5)
    ax.legend(frameon=False)
    ax.set_title("Mean with sample-SD error bars ($n=3$)")
    save_figure(fig, output_dir / "latency_comparison", dry_run=dry_run)
    plt.close(fig)

    fig, axes = plt.subplots(2, 2, figsize=(3.5, 3.15))
    panels = (
        ("parameters", "Parameters (M)", lambda value: value / 1_000_000),
        ("thop", "THOP FLOPs (G)", lambda value: value / 1_000_000_000),
        ("inference_artifact_bytes", "FP16 artifact (MiB)", lambda value: value / (1024**2)),
        ("tensor_to_final_detections_sustained_fps", "Throughput (FPS)", lambda value: value),
    )
    for axis, (field, title, transform) in zip(axes.flat, panels):
        if field == "thop":
            means = [transform(rows[model]["flop_estimates"]["thop"]["mean"]) for model in MODELS]
            errors = [transform(rows[model]["flop_estimates"]["thop"]["sample_std"]) for model in MODELS]
        else:
            means = [transform(rows[model][field]["mean"]) for model in MODELS]
            errors = [transform(rows[model][field]["sample_std"]) for model in MODELS]
        axis.bar(range(len(MODELS)), means, yerr=errors, capsize=2, color=colors)
        axis.set_xticks(range(len(MODELS)), ("Y11n", "Y26n", "D-FINE"))
        axis.set_title(title)
        axis.grid(True, axis="y", alpha=0.25, linewidth=0.5)
    fig.suptitle("Resource and throughput means with sample SD ($n=3$)", fontsize=8.5)
    fig.tight_layout()
    save_figure(fig, output_dir / "resource_comparison", dry_run=dry_run)
    plt.close(fig)


def result_summary(context: dict[str, Any], manual: dict[str, Any], *, dry_run: bool) -> dict[str, Any]:
    aggregate = context["aggregate"]
    rows = context["row_by_model"]
    runs = context["run_by_key"]
    return {
        "schema_version": 1,
        "artifact": "dms_eval_manuscript_result_summary",
        "dry_run": dry_run,
        "watermark": "MOCK DATA - NOT BENCHMARK RESULTS" if dry_run else None,
        "suite_id": context["suite_id"],
        "models": list(MODELS),
        "seeds": list(SEEDS),
        "dispersion": "sample_standard_deviation_n_minus_1",
        "aggregate_source": {
            "path": portable_path(context["aggregate_path"]),
            "sha256": sha256_file(context["aggregate_path"]),
        },
        "manual_registry": {
            "path": portable_path(MANUAL_RESULTS_PATH),
            "sha256": sha256_file(MANUAL_RESULTS_PATH),
            "pending": [
                *[f"training_duration_hours/{model}" for model in MODELS if manual["training_duration_hours"][model] is None],
                *(["best_tradeoff_model"] if manual["best_tradeoff_model"] is None else []),
                *(["discussion_tradeoff_sentence"] if manual["discussion_tradeoff_sentence"] is None else []),
            ],
        },
        "protected_result_sources": context["source_hashes"],
        "individual_runs": [runs[(model, seed)] for model in MODELS for seed in SEEDS],
        "aggregate_rows": [rows[model] for model in MODELS],
        "run_policy": aggregate["run_policy"],
    }


def human_report(context: dict[str, Any], *, dry_run: bool) -> str:
    rows = context["row_by_model"]
    marker = "\n> **MOCK DATA - NOT BENCHMARK RESULTS.**\n" if dry_run else ""
    lines = [
        "# DMS-Eval Final Result Report" if not dry_run else "# DMS-Eval Dry-Run Result Report",
        marker,
        "All nine model-seed rows were validated. Values are mean +/- sample standard deviation over the three predeclared seeds (13, 37, 73); the standard deviation uses the n-1 denominator. No run was selected or discarded.",
        "",
        "| Model | mAP@0.5:0.95 | mAP@0.5 | Precision | Recall | F1 | Tensor-to-detections p50 (ms) | FPS |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for model in MODELS:
        row = rows[model]
        pair = lambda field: f"{format_metric(field, row[field]['mean'])} +/- {format_metric(field, row[field]['sample_std'])}"
        lines.append(
            f"| {MODEL_LABELS[model]} | {pair('map_50_95')} | {pair('map_50')} | {pair('precision')} | "
            f"{pair('recall')} | {pair('micro_f1')} | {pair('tensor_to_final_detections_p50_ms')} | "
            f"{pair('tensor_to_final_detections_sustained_fps')} |"
        )
    lines.extend(
        (
            "",
            "## Interpretation boundary",
            "",
            "These are configured-system comparisons on one RTX 4060 protocol. Equal epochs and data exposure do not equalize compute, architecture capacity, or native postprocessing. Three seeds provide limited run-to-run variation, not a general proof of statistical superiority.",
            "",
            "## Provenance",
            "",
            f"- Aggregate: `{portable_path(context['aggregate_path'])}` (`{sha256_file(context['aggregate_path'])}`)",
            f"- Frozen suite: `{context['suite_id']}`",
            "- Exact protected-result hashes: `source_hashes.json`",
            "",
        )
    )
    return "\n".join(lines)


def factual_results_tex(context: dict[str, Any]) -> str:
    rows = context["row_by_model"]
    accuracy_model = max(MODELS, key=lambda model: rows[model]["map_50_95"]["mean"])
    fastest_model = min(MODELS, key=lambda model: rows[model]["tensor_to_final_detections_p50_ms"]["mean"])
    return (
        "% AUTO-GENERATED FACTUAL PROSE ONLY. NUANCED INTERPRETATION REMAINS MANUAL.\n"
        f"The highest mean protected-test mAP@0.5:0.95 was obtained by {MODEL_LABELS[accuracy_model]}, "
        f"and the lowest mean tensor-to-final-detections p50 latency was obtained by {MODEL_LABELS[fastest_model]}. "
        "All comparisons summarize the three predeclared retained seeds.\n"
    )


def locate_aggregate() -> Path:
    results_dir = REPO_ROOT / "results"
    candidates: list[Path] = []
    for pattern in ("**/*aggregate*.json", "**/*summary*.json"):
        for path in sorted(results_dir.glob(pattern)) if results_dir.exists() else []:
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if payload.get("artifact") == "dms_eval_aggregate":
                candidates.append(path.resolve())
    candidates = sorted(set(candidates))
    if len(candidates) != 1:
        raise AssetError(f"Auto-discovery requires exactly one canonical aggregate; found {len(candidates)}")
    return candidates[0]


def build_manuscript() -> None:
    environment = os.environ.copy()
    environment["SOURCE_DATE_EPOCH"] = "1"
    miktex_bin = Path.home() / "AppData/Local/Programs/MiKTeX/miktex/bin/x64"

    latexmk_candidates = [shutil.which("latexmk"), str(miktex_bin / "latexmk.exe")]
    latexmk = next((candidate for candidate in latexmk_candidates if candidate and Path(candidate).is_file()), None)
    if latexmk and shutil.which("perl"):
        subprocess.run(
            [latexmk, "-pdf", "-interaction=nonstopmode", "-halt-on-error", "main.tex"],
            cwd=MANUSCRIPT_DIR,
            env=environment,
            check=True,
        )
        return

    def executable(name: str) -> str:
        candidates = [shutil.which(name), str(miktex_bin / f"{name}.exe")]
        match = next((candidate for candidate in candidates if candidate and Path(candidate).is_file()), None)
        if match is None:
            raise AssetError(f"{name} is unavailable; assets were generated but the PDF was not rebuilt")
        return match

    pdflatex = executable("pdflatex")
    bibtex = executable("bibtex")
    commands = (
        [pdflatex, "-interaction=nonstopmode", "-halt-on-error", "main.tex"],
        [bibtex, "main"],
        [pdflatex, "-interaction=nonstopmode", "-halt-on-error", "main.tex"],
        [pdflatex, "-interaction=nonstopmode", "-halt-on-error", "main.tex"],
    )
    for command in commands:
        subprocess.run(command, cwd=MANUSCRIPT_DIR, env=environment, check=True)


def initialize_placeholders() -> None:
    root = MANUSCRIPT_DIR / "generated"
    atomic_write_text(root / "results_macros.tex", placeholder_macros())
    atomic_write_text(root / "tables" / "primary_results.tex", placeholder_primary_table())
    atomic_write_text(root / "tables" / "per_class_results.tex", placeholder_per_class_table())
    atomic_write_text(root / "tables" / "per_seed_results.tex", placeholder_per_seed_table())


def generate_protocol_figure() -> None:
    """Create the static benchmark lifecycle as a code-native publication figure."""
    plt = import_plotting()
    fig, ax = plt.subplots(figsize=(7.16, 3.15))
    ax.set_xlim(0, 3)
    ax.set_ylim(0, 2.12)
    ax.set_axis_off()
    nodes = (
        (0.05, 1.17, "1  Data adaptation", ("68 public sessions / 14 subjects", "1 FPS; direct 640 x 640 crop", "15,723 frames; 12,722 no-cue"), "#0072B2"),
        (1.05, 1.17, "2  Frozen split", ("8/3/3 disjoint subjects", "60,060 assignments scored", "Zero identity overlap"), "#009E73"),
        (2.05, 1.17, "3  Controlled training", ("3 systems x 3 seeds", "220 epochs; batch 8 x 4", "All trajectories retained"), "#E69F00"),
        (2.05, 0.25, "4  Validation only", ("Checkpoint + threshold selection", "No protected-test feedback", "Immutable run manifests"), "#D55E00"),
        (1.05, 0.25, "5  Protected evaluation", ("One ledger-gated pass per run", "Shared COCO metrics", "Latency, resources, fixed examples"), "#CC79A7"),
        (0.05, 0.25, "6  Verified reporting", ("Complete 3 x 3 matrix required", "Mean + sample SD; no best seed", "Deterministic tables, plots, prose"), "#56B4E9"),
    )
    width, height = 0.90, 0.64
    for x, y, title, body, color in nodes:
        ax.add_patch(plt.Rectangle((x, y), width, height, facecolor="#F7F7F7", edgecolor=color, linewidth=1.3))
        ax.add_patch(plt.Rectangle((x, y + height - 0.18), width, 0.18, facecolor=color, edgecolor=color, linewidth=0))
        ax.text(x + width / 2, y + height - 0.09, title, color="white", ha="center", va="center", fontsize=8.2, weight="bold")
        for index, line in enumerate(body):
            ax.text(x + 0.05, y + 0.34 - index * 0.13, line, ha="left", va="center", fontsize=7.1, color="#202020")

    arrow = {"arrowstyle": "-|>", "color": "#333333", "linewidth": 1.2, "shrinkA": 2, "shrinkB": 2}
    ax.annotate("", xy=(1.05, 1.49), xytext=(0.95, 1.49), arrowprops=arrow)
    ax.annotate("", xy=(2.05, 1.49), xytext=(1.95, 1.49), arrowprops=arrow)
    ax.annotate("", xy=(2.50, 0.89), xytext=(2.50, 1.17), arrowprops=arrow)
    ax.annotate("", xy=(1.95, 0.57), xytext=(2.05, 0.57), arrowprops=arrow)
    ax.annotate("", xy=(0.95, 0.57), xytext=(1.05, 0.57), arrowprops=arrow)
    ax.text(1.5, 2.03, "Frozen DMS-Eval lifecycle", ha="center", va="center", fontsize=11, weight="bold", color="#1D2A3A")
    ax.text(1.5, 1.91, "Data and decisions flow left-to-right, then right-to-left; protected-test access begins only at stage 5.", ha="center", va="center", fontsize=7.4, color="#444444")
    save_figure(fig, MANUSCRIPT_DIR / "figures" / "dms_eval_pipeline", dry_run=False)
    plt.close(fig)


def generate_placeholder_image() -> None:
    plt = import_plotting()
    fig, ax = plt.subplots(figsize=(7.16, 2.15), dpi=300)
    ax.set_axis_off()
    ax.add_patch(plt.Rectangle((0.01, 0.02), 0.98, 0.96, transform=ax.transAxes, fill=False, linewidth=1.2, color="#666666"))
    ax.text(0.5, 0.62, "Placeholder_image_1", ha="center", va="center", fontsize=16, weight="bold")
    ax.text(0.5, 0.40, "Qualitative detections and failure cases", ha="center", va="center", fontsize=11)
    ax.text(0.5, 0.20, "TO_BE_UPDATED", ha="center", va="center", fontsize=10, family="monospace", color="#D55E00")
    target = MANUSCRIPT_DIR / "figures" / "Placeholder_image_1.png"
    with tempfile.NamedTemporaryFile(delete=False, dir=target.parent, suffix=".png") as handle:
        temporary = Path(handle.name)
    fig.savefig(temporary, dpi=300, bbox_inches="tight", pad_inches=0.02, metadata={"Software": "DMS-Eval placeholder generator"})
    plt.close(fig)
    os.replace(temporary, target)


def create_mock_fixture(path: Path) -> None:
    fixture_dir = path.parent / "mock_protected_results"
    fixture_dir.mkdir(parents=True, exist_ok=True)
    runs: list[dict[str, Any]] = []
    for model_index, model in enumerate(MODELS):
        for seed_index, seed in enumerate(SEEDS):
            source = fixture_dir / f"{model}_seed{seed}.json"
            atomic_write_json(
                source,
                {
                    "schema_version": 1,
                    "artifact": "mock_protected_test_result",
                    "watermark": "MOCK DATA - NOT BENCHMARK RESULTS",
                    "model_id": model,
                    "training_seed": seed,
                },
            )
            accuracy = 0.40 + 0.025 * model_index + 0.005 * seed_index
            latency = 3.0 + 0.8 * model_index + 0.1 * seed_index
            parameters = 2_600_000 + 350_000 * model_index
            run: dict[str, Any] = {
                "model_id": model,
                "training_seed": seed,
                "manifest_id": f"mock-{model}-{seed}",
                "suite_id": "mock-suite-not-results",
                "source": portable_path(source),
                "map_50_95": accuracy,
                "map_50": accuracy + 0.20,
                "precision": 0.70 + 0.015 * model_index + 0.003 * seed_index,
                "recall": 0.65 + 0.015 * model_index + 0.004 * seed_index,
                "micro_f1": 0.674 + 0.015 * model_index + 0.003 * seed_index,
                "far_per_100_negative_frames": 8.0 - 0.5 * model_index + 0.1 * seed_index,
                "model_forward_p50_ms": latency - 0.7,
                "model_forward_p95_ms": latency - 0.2,
                "model_forward_p99_ms": latency,
                "model_forward_sustained_fps": 1000.0 / (latency - 0.55),
                "tensor_to_final_detections_p50_ms": latency,
                "tensor_to_final_detections_p95_ms": latency + 0.7,
                "tensor_to_final_detections_p99_ms": latency + 1.1,
                "tensor_to_final_detections_sustained_fps": 1000.0 / (latency + 0.15),
                "peak_allocated_vram_bytes": 900_000_000 + model_index * 100_000_000 + seed_index * 2_000_000,
                "parameters": parameters,
                "inference_artifact_bytes": parameters * 2,
                "inference_artifact_sha256": "0" * 64,
                "per_class_ap_50_95": {
                    class_name: accuracy - 0.03 + class_index * 0.015
                    for class_index, class_name in enumerate(CLASSES)
                },
                "flop_estimates": {
                    "thop": {"flops": 6_000_000_000 + model_index * 700_000_000 + seed_index * 10_000_000},
                    "torch_profiler": {"flops": 5_700_000_000 + model_index * 650_000_000 + seed_index * 9_000_000},
                },
                "qualitative_analysis": {"path": "mock", "sha256": "0" * 64},
            }
            runs.append(run)

    rows = []
    for model in MODELS:
        model_runs = [run for run in runs if run["model_id"] == model]
        row: dict[str, Any] = {"model_id": model, "runs": 3, "training_seeds": list(SEEDS)}
        for field in NUMERIC_FIELDS:
            row[field] = sample_stats(float(run[field]) for run in model_runs)
        row["per_class_ap_50_95"] = {
            class_name: sample_stats(float(run["per_class_ap_50_95"][class_name]) for run in model_runs)
            for class_name in CLASSES
        }
        row["flop_estimates"] = {
            estimator: sample_stats(float(run["flop_estimates"][estimator]["flops"]) for run in model_runs)
            for estimator in ("thop", "torch_profiler")
        }
        rows.append(row)
    aggregate = {
        "schema_version": 3,
        "artifact": "dms_eval_aggregate",
        "fixture": True,
        "watermark": "MOCK DATA - NOT BENCHMARK RESULTS",
        "run_policy": "three_predeclared_equal_seeds_no_run_selection",
        "suite_id": "mock-suite-not-results",
        "training_seeds": list(SEEDS),
        "dispersion": "sample_standard_deviation",
        "runs": sorted(runs, key=lambda run: (run["model_id"], run["training_seed"])),
        "rows": rows,
    }
    atomic_write_json(path, aggregate)


def generate_assets(context: dict[str, Any], output_root: Path, *, dry_run: bool) -> None:
    output_root.mkdir(parents=True, exist_ok=True)
    manual = load_manual_results()
    macros = result_macros(context, manual)
    tex_marker = "% MOCK DATA - NOT BENCHMARK RESULTS. DRY-RUN OUTPUT ONLY.\n" if dry_run else ""
    macros = tex_marker + macros
    atomic_write_text(output_root / "results_macros.tex", macros)
    atomic_write_text(output_root / "tables" / "primary_results.tex", tex_marker + aggregate_primary_table(context))
    atomic_write_text(output_root / "tables" / "per_class_results.tex", tex_marker + aggregate_per_class_table(context))
    atomic_write_text(output_root / "tables" / "per_seed_results.tex", tex_marker + aggregate_per_seed_table(context))
    atomic_write_text(output_root / "factual_results.tex", tex_marker + factual_results_tex(context))
    summary = result_summary(context, manual, dry_run=dry_run)
    atomic_write_json(output_root / "result_summary.json", summary)
    atomic_write_json(
        output_root / "source_hashes.json",
        {
            "schema_version": 1,
            "dry_run": dry_run,
            "watermark": "MOCK DATA - NOT BENCHMARK RESULTS" if dry_run else None,
            "aggregate": summary["aggregate_source"],
            "manual_registry": summary["manual_registry"],
            "protected_results": context["source_hashes"],
        },
    )
    atomic_write_text(output_root / "FINAL_RESULT_REPORT.md", human_report(context, dry_run=dry_run))
    generate_figures(context, output_root / "figures", dry_run=dry_run)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--aggregate", help="Canonical aggregate JSON path, or 'auto' to find exactly one under results/")
    parser.add_argument("--dry-run", action="store_true", help="Require a marked fixture and write watermarked outputs")
    parser.add_argument("--build", action="store_true", help="Rebuild manuscript/main.pdf after final asset generation")
    parser.add_argument("--initialize-placeholders", action="store_true", help="Create visible centralized placeholder macros/tables")
    parser.add_argument("--create-mock-fixture", metavar="PATH", help="Write a deterministic, clearly marked schema-compatible fixture")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.initialize_placeholders:
        if any((args.aggregate, args.dry_run, args.build, args.create_mock_fixture)):
            raise AssetError("--initialize-placeholders cannot be combined with other modes")
        initialize_placeholders()
        generate_protocol_figure()
        generate_placeholder_image()
        print("Initialized centralized manuscript placeholders.")
        return 0
    if args.create_mock_fixture:
        if any((args.aggregate, args.dry_run, args.build)):
            raise AssetError("--create-mock-fixture cannot be combined with aggregate generation")
        create_mock_fixture((REPO_ROOT / args.create_mock_fixture).resolve())
        print(f"Created marked mock fixture: {args.create_mock_fixture}")
        return 0
    if not args.aggregate:
        raise AssetError("--aggregate is required for asset generation")
    aggregate_path = locate_aggregate() if args.aggregate == "auto" else resolve_source(args.aggregate)
    if not aggregate_path.is_file():
        raise AssetError(f"Aggregate not found: {aggregate_path}")
    aggregate = json.loads(aggregate_path.read_text(encoding="utf-8"))
    context = validate_aggregate(aggregate, aggregate_path, dry_run=args.dry_run)
    output_root = MANUSCRIPT_DIR / "generated" / "dry_run" if args.dry_run else MANUSCRIPT_DIR / "generated"
    generate_assets(context, output_root, dry_run=args.dry_run)
    if args.build:
        if args.dry_run:
            raise AssetError("The manuscript cannot be rebuilt from mock dry-run outputs")
        build_manuscript()
    print(f"Generated deterministic manuscript assets in {portable_path(output_root)}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssetError, json.JSONDecodeError, OSError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
