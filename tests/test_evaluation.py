"""Known-answer tests for the shared benchmark evaluator."""

from __future__ import annotations

import math

import pytest

from core.evaluation import (
    calibrate_threshold,
    coco_metrics,
    compute_iou,
    operating_point_metrics,
    select_checkpoint_candidate,
    select_threshold_candidate,
    threshold_grid,
)
from core.protocol import ProtocolError


def fixture_ground_truth():
    return {
        "info": {"description": "synthetic known answer"},
        "licenses": [],
        "images": [{"id": 1, "file_name": "one.jpg", "width": 640, "height": 640}, {"id": 2, "file_name": "two.jpg", "width": 640, "height": 640}],
        "annotations": [{"id": 1, "image_id": 1, "category_id": 1, "bbox": [0, 0, 10, 20], "area": 200, "iscrowd": 0}],
        "categories": [
            {"id": 1, "name": "yawning", "supercategory": "driver_cue"},
            {"id": 2, "name": "hand_over_mouth", "supercategory": "driver_cue"},
            {"id": 3, "name": "drinking", "supercategory": "driver_cue"},
            {"id": 4, "name": "phone_use", "supercategory": "driver_cue"},
        ],
    }


def test_iou_known_answers():
    assert compute_iou([0, 0, 10, 20], [0, 0, 10, 20]) == 1.0
    assert compute_iou([0, 0, 10, 20], [10, 0, 20, 20]) == 0.0
    assert compute_iou([0, 0, 10, 20], [5, 0, 15, 20]) == pytest.approx(1 / 3)
    assert compute_iou([0, 0, 0, 20], [0, 0, 10, 20]) == 0.0


def test_matching_metrics_and_far_known_answer():
    predictions = [
        {"image_id": 1, "category_id": 1, "bbox": [0, 0, 10, 20], "score": 0.9},
        {"image_id": 1, "category_id": 1, "bbox": [0, 0, 10, 20], "score": 0.8},
        {"image_id": 2, "category_id": 2, "bbox": [10, 10, 10, 10], "score": 0.7},
        {"image_id": 2, "category_id": 3, "bbox": [20, 20, 10, 10], "score": 0.6},
    ]
    result = operating_point_metrics(fixture_ground_truth(), predictions, 0.5)
    assert (result["tp"], result["fp"], result["fn"]) == (1, 3, 0)
    assert result["precision"] == 0.25
    assert result["recall"] == 1.0
    assert result["micro_f1"] == 0.4
    assert result["far_per_100_negative_frames"] == 200.0


def test_threshold_grid_and_higher_threshold_tie_break():
    assert len(threshold_grid()) == 99
    assert threshold_grid()[0] == 0.01 and threshold_grid()[-1] == 0.99
    predictions = [{"image_id": 1, "category_id": 1, "bbox": [0, 0, 10, 20], "score": 0.5}]
    selected = calibrate_threshold(fixture_ground_truth(), predictions)
    assert selected["threshold"] == 0.5
    assert selected["micro_f1"] == 1.0


def test_threshold_selection_prefers_precision_before_threshold():
    candidates = [
        {"micro_f1": 0.8, "precision": 0.7, "threshold": 0.9},
        {"micro_f1": 0.8, "precision": 0.8, "threshold": 0.4},
        {"micro_f1": 0.8, "precision": 0.8, "threshold": 0.6},
    ]
    assert select_threshold_candidate(candidates)["threshold"] == 0.6


def test_checkpoint_selection_tie_break_order():
    candidates = [
        {"map_50_95": 0.5, "map_50": 0.7, "epoch": 220},
        {"map_50_95": 0.6, "map_50": 0.7, "epoch": 100},
        {"map_50_95": 0.6, "map_50": 0.8, "epoch": 90},
        {"map_50_95": 0.6, "map_50": 0.8, "epoch": 110},
    ]
    assert select_checkpoint_candidate(candidates)["epoch"] == 110


def test_official_coco_map_perfect_known_answer():
    predictions = [{"image_id": 1, "category_id": 1, "bbox": [0, 0, 10, 20], "score": 0.9}]
    result = coco_metrics(fixture_ground_truth(), predictions)
    assert result["implementation"] == "pycocotools"
    assert result["map_50_95"] == pytest.approx(1.0)
    assert result["map_50"] == pytest.approx(1.0)
    assert result["per_class_ap_50_95"]["yawning"] == pytest.approx(1.0)
    assert math.isnan(result["per_class_ap_50_95"]["drinking"])


def test_predictions_outside_split_are_rejected():
    predictions = [{"image_id": 99, "category_id": 1, "bbox": [0, 0, 10, 20], "score": 0.9}]
    with pytest.raises(ProtocolError, match="outside the selected split"):
        operating_point_metrics(fixture_ground_truth(), predictions, 0.5)
