"""Known-answer tests for the pre-registered qualitative/error analysis."""

from __future__ import annotations

from PIL import Image

from core.qualitative import QualitativeErrorCollector, analyze_image


def _prediction(category: int, box: list[float], score: float = 0.9) -> dict:
    return {"image_id": 1, "category_id": category, "bbox": box, "score": score}


def _truth(category: int, box: list[float]) -> dict:
    return {"image_id": 1, "category_id": category, "bbox": box}


def test_predeclared_error_categories_have_known_answers():
    truth = [_truth(1, [0, 0, 20, 20])]
    assert analyze_image(truth, [_prediction(1, [0, 0, 20, 20])], 0.5)["categories"] == ["correct_detection"]
    assert analyze_image([], [_prediction(1, [0, 0, 20, 20])], 0.5)["categories"] == [
        "false_positive_negative_frame"
    ]
    assert "false_negative" in analyze_image(truth, [], 0.5)["categories"]
    confused = analyze_image(truth, [_prediction(2, [0, 0, 20, 20])], 0.5)
    assert "class_confusion" in confused["categories"]
    localized = analyze_image(truth, [_prediction(1, [10, 0, 20, 20])], 0.5)
    assert "localization_error" in localized["categories"]


def test_collector_renders_ranked_artifact(tmp_path):
    collector = QualitativeErrorCollector("yolo11n", 13, 0.5, {1: "yawning", 2: "hand"}, limit=1)
    image = Image.new("RGB", (64, 64), "black")
    info = {"id": 1, "file_name": "images/subject_01/frame.jpg"}
    truth = [_truth(1, [4, 4, 20, 20])]
    collector.observe(info, image, truth, [_prediction(1, [4, 4, 20, 20])])
    artifact = collector.finalize(tmp_path / "qualitative")
    assert artifact["counts"]["correct_detection"] == 1
    example = artifact["examples"]["correct_detection"][0]
    assert example["rank"] == 1
    assert (tmp_path / "qualitative" / "analysis.json").is_file()
    assert __import__("pathlib").Path(example["rendered_path"]).is_file()
