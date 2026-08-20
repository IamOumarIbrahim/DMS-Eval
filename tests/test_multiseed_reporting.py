"""Regression tests for nine-run aggregation and publication outputs."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.protocol import TRAINING_SEEDS, sha256_file
from core.qualitative import CATEGORIES
from scripts.benchmark.aggregate_results import build_aggregate
from scripts.publication.generate_publication_tables import render_tables
from scripts.publication.generate_qualitative_error_analysis import load_analyses, render_contact_sheet, render_markdown


def _artifacts(tmp_path: Path):
    loaded = []
    result_paths = []
    for model_index, model_id in enumerate(("yolo11n", "yolo26n", "dfine_n")):
        for seed_index, seed in enumerate(TRAINING_SEEDS):
            analysis_path = tmp_path / f"{model_id}-{seed}-analysis.json"
            analysis = {
                "schema_version": 1,
                "artifact": "qualitative_error_analysis",
                "model_id": model_id,
                "training_seed": seed,
                "counts": {"images": 2, "tp": seed_index + 1, "fp": 1, "fn": 2, **{category: 0 for category in CATEGORIES}},
                "examples": {category: [] for category in CATEGORIES},
            }
            analysis_path.write_text(json.dumps(analysis), encoding="utf-8")
            value = 0.1 * (model_index + 1) + 0.01 * seed_index
            result = {
                "artifact": "protected_test_result",
                "model_id": model_id,
                "training_seed": seed,
                "manifest_id": f"{model_id}-{seed}",
                "suite_id": "frozen-suite",
                "coco_metrics": {
                    "map_50_95": value,
                    "map_50": value + 0.1,
                    "per_class_ap_50_95": {name: value for name in ("yawning", "hand_over_mouth", "drinking", "phone_use")},
                },
                "operating_point": {"precision": value, "recall": value, "micro_f1": value, "far_per_100_negative_frames": value},
                "runtime_profile": {
                    "model_forward": {"p50_ms": 1.0, "p95_ms": 2.0, "p99_ms": 3.0, "sustained_fps": 100.0},
                    "tensor_to_final_detections": {"p50_ms": 2.0, "p95_ms": 3.0, "p99_ms": 4.0, "sustained_fps": 50.0},
                    "peak_allocated_vram_bytes": 1_000_000 + seed_index,
                },
                "parameters": 2_000_000,
                "flop_estimates": {"thop": {"flops": 3_000_000_000}, "torch_profiler": {"flops": 2_000_000_000}},
                "inference_artifact": {"bytes": 4_000_000, "sha256": f"artifact-{model_id}-{seed}"},
                "qualitative_analysis": {
                    "artifact": "qualitative_error_analysis",
                    "path": str(analysis_path),
                    "sha256": sha256_file(analysis_path),
                },
            }
            result_path = tmp_path / f"{model_id}-{seed}.json"
            result_path.write_text(json.dumps(result), encoding="utf-8")
            loaded.append((result, result_path))
            result_paths.append(result_path)
    return loaded, result_paths


def test_nine_run_aggregate_and_publication_columns(tmp_path):
    loaded, _ = _artifacts(tmp_path)
    aggregate = build_aggregate(loaded)
    assert aggregate["training_seeds"] == [13, 37, 73]
    assert len(aggregate["runs"]) == 9 and len(aggregate["rows"]) == 3
    assert aggregate["rows"][0]["map_50_95"]["mean"] == pytest.approx(0.11)
    assert aggregate["rows"][0]["map_50_95"]["sample_std"] == pytest.approx(0.01)
    markdown, latex = render_tables(aggregate)
    assert "Params M" in markdown and "Peak VRAM MB" in markdown and "±" in markdown
    assert "\\pm" in latex


def test_qualitative_generator_requires_and_uses_all_nine_runs(tmp_path):
    _, result_paths = _artifacts(tmp_path)
    analyses = load_analyses(result_paths)
    assert len(analyses) == 9
    assert "mean ± sample SD" in render_markdown(analyses)
    output = render_contact_sheet(analyses, tmp_path / "contact.png")
    assert output.is_file()
