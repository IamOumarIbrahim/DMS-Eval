"""Pre-registered qualitative and image-level error analysis."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw

from .evaluation import compute_iou, xywh_to_xyxy
from .isolation import write_json_atomic
from .protocol import sha256_file


CATEGORIES = (
    "correct_detection",
    "false_positive_negative_frame",
    "false_negative",
    "class_confusion",
    "localization_error",
)


def analyze_image(
    ground_truths: list[dict[str, Any]],
    predictions: list[dict[str, Any]],
    threshold: float,
    iou_threshold: float = 0.5,
) -> dict[str, Any]:
    """Classify one image using the frozen operating point and deterministic matching."""

    detections = sorted(
        (item for item in predictions if float(item["score"]) >= threshold),
        key=lambda item: (-float(item["score"]), int(item["category_id"]), *item["bbox"]),
    )
    matched: set[int] = set()
    tp = 0
    unmatched: list[dict[str, Any]] = []
    matched_ious: list[float] = []
    for detection in detections:
        best_iou, best_index = -1.0, None
        for index, truth in enumerate(ground_truths):
            if index in matched or int(truth["category_id"]) != int(detection["category_id"]):
                continue
            iou = compute_iou(xywh_to_xyxy(detection["bbox"]), xywh_to_xyxy(truth["bbox"]))
            if iou > best_iou:
                best_iou, best_index = iou, index
        if best_index is not None and best_iou >= iou_threshold:
            matched.add(best_index)
            matched_ious.append(best_iou)
            tp += 1
        else:
            unmatched.append(detection)

    confusions: list[dict[str, Any]] = []
    localization_ious: list[float] = []
    for detection in unmatched:
        for truth in ground_truths:
            iou = compute_iou(xywh_to_xyxy(detection["bbox"]), xywh_to_xyxy(truth["bbox"]))
            if int(detection["category_id"]) != int(truth["category_id"]) and iou >= iou_threshold:
                confusions.append(
                    {
                        "ground_truth_category_id": int(truth["category_id"]),
                        "predicted_category_id": int(detection["category_id"]),
                        "iou": iou,
                    }
                )
            elif int(detection["category_id"]) == int(truth["category_id"]) and 0.0 < iou < iou_threshold:
                localization_ious.append(iou)

    fp, fn = len(unmatched), len(ground_truths) - len(matched)
    categories: list[str] = []
    scores: dict[str, list[float]] = {}
    if ground_truths and tp == len(ground_truths) and fp == 0:
        categories.append("correct_detection")
        scores["correct_detection"] = [float(tp), max(matched_ious, default=0.0)]
    if not ground_truths and fp:
        categories.append("false_positive_negative_frame")
        scores["false_positive_negative_frame"] = [float(fp), max(float(item["score"]) for item in unmatched)]
    if fn:
        categories.append("false_negative")
        scores["false_negative"] = [float(fn), 1.0 - max(matched_ious, default=0.0)]
    if confusions:
        categories.append("class_confusion")
        scores["class_confusion"] = [float(len(confusions)), max(item["iou"] for item in confusions)]
    if localization_ious:
        categories.append("localization_error")
        scores["localization_error"] = [float(len(localization_ious)), max(localization_ious)]
    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "categories": categories,
        "category_scores": scores,
        "class_confusions": confusions,
        "detections": detections,
    }


class QualitativeErrorCollector:
    """Keep only deterministically ranked examples during the protected pass."""

    def __init__(self, model_id: str, training_seed: int, threshold: float, class_names: dict[int, str], limit: int = 3):
        self.model_id = model_id
        self.training_seed = training_seed
        self.threshold = threshold
        self.class_names = class_names
        self.limit = limit
        self.counts = {"images": 0, "tp": 0, "fp": 0, "fn": 0, **{category: 0 for category in CATEGORIES}}
        self.confusion_pairs: dict[str, int] = defaultdict(int)
        self.examples: dict[str, list[dict[str, Any]]] = {category: [] for category in CATEGORIES}

    def observe(
        self,
        image_info: dict[str, Any],
        image: Image.Image,
        ground_truths: list[dict[str, Any]],
        predictions: list[dict[str, Any]],
    ) -> None:
        analysis = analyze_image(ground_truths, predictions, self.threshold)
        self.counts["images"] += 1
        for key in ("tp", "fp", "fn"):
            self.counts[key] += int(analysis[key])
        for confusion in analysis["class_confusions"]:
            pair = f"{confusion['ground_truth_category_id']}->{confusion['predicted_category_id']}"
            self.confusion_pairs[pair] += 1
        image_id = int(image_info["id"])
        for category in analysis["categories"]:
            self.counts[category] += 1
            candidate = {
                "image_id": image_id,
                "file_name": image_info["file_name"],
                "rank_score": analysis["category_scores"][category],
                "ground_truths": ground_truths,
                "predictions": analysis["detections"],
                "_image": image.copy(),
            }
            ranked = self.examples[category] + [candidate]
            ranked.sort(key=lambda item: (tuple(-value for value in item["rank_score"]), item["image_id"]))
            self.examples[category] = ranked[: self.limit]

    def _render(self, candidate: dict[str, Any], destination: Path) -> None:
        image = candidate["_image"].copy().convert("RGB")
        draw = ImageDraw.Draw(image)
        for truth in candidate["ground_truths"]:
            x, y, width, height = map(float, truth["bbox"])
            label = f"GT {self.class_names[int(truth['category_id'])]}"
            draw.rectangle((x, y, x + width, y + height), outline=(0, 220, 0), width=3)
            draw.text((x + 2, max(0, y - 12)), label, fill=(0, 220, 0), stroke_width=2, stroke_fill=(0, 0, 0))
        for prediction in candidate["predictions"]:
            x, y, width, height = map(float, prediction["bbox"])
            label = f"P {self.class_names[int(prediction['category_id'])]} {prediction['score']:.2f}"
            draw.rectangle((x, y, x + width, y + height), outline=(255, 80, 40), width=3)
            draw.text((x + 2, y + 2), label, fill=(255, 180, 80), stroke_width=2, stroke_fill=(0, 0, 0))
        destination.parent.mkdir(parents=True, exist_ok=True)
        image.save(destination, format="PNG")

    def finalize(self, output_dir: str | Path) -> dict[str, Any]:
        output = Path(output_dir).resolve()
        serialized_examples: dict[str, list[dict[str, Any]]] = {}
        for category in CATEGORIES:
            serialized_examples[category] = []
            for rank, candidate in enumerate(self.examples[category], start=1):
                rendered = output / "images" / f"{category}-{rank:02d}-image-{candidate['image_id']}.png"
                self._render(candidate, rendered)
                serialized = {key: value for key, value in candidate.items() if key != "_image"}
                serialized.update({"rank": rank, "rendered_path": str(rendered), "rendered_sha256": sha256_file(rendered)})
                serialized_examples[category].append(serialized)
        artifact = {
            "schema_version": 1,
            "artifact": "qualitative_error_analysis",
            "model_id": self.model_id,
            "training_seed": self.training_seed,
            "threshold": self.threshold,
            "selection": "deterministic_predeclared_category_ranking",
            "examples_per_category": self.limit,
            "counts": self.counts,
            "class_confusion_pairs": dict(sorted(self.confusion_pairs.items())),
            "examples": serialized_examples,
        }
        artifact_path = write_json_atomic(output / "analysis.json", artifact)
        return {"path": str(artifact_path), "sha256": sha256_file(artifact_path), **artifact}
