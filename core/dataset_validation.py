"""Read-only, deterministic validation of authoritative and derived dataset artifacts."""

from __future__ import annotations

import hashlib
import json
import math
import random
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from PIL import Image

from .protocol import REPO_ROOT, load_protocol, resolve_repo_path, verify_authoritative_fingerprints


@dataclass
class DatasetValidationReport:
    checks: list[str] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)

    def check(self, condition: bool, message: str) -> None:
        (self.checks if condition else self.failures).append(message)

    @property
    def ok(self) -> bool:
        return not self.failures

    def as_dict(self) -> dict[str, Any]:
        return {"ok": self.ok, "passed_checks": len(self.checks), "failures": self.failures, "summary": self.summary}


def subject_from_filename(filename: str) -> str:
    parts = Path(filename).parts
    if len(parts) < 3 or parts[0] != "images" or not parts[1].startswith("subject_"):
        raise ValueError(f"Invalid canonical image path: {filename}")
    return parts[1]


def _inspect_image(item: tuple[int, Path, int, int]) -> tuple[int, str | None, str | None]:
    image_id, path, expected_width, expected_height = item
    try:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            while chunk := handle.read(1024 * 1024):
                digest.update(chunk)
        with Image.open(path) as image:
            image.load()
            if image.format != "JPEG" or image.size != (expected_width, expected_height):
                return image_id, None, f"{path}: expected JPEG {expected_width}x{expected_height}, got {image.format} {image.size}"
        return image_id, digest.hexdigest(), None
    except Exception as exc:
        return image_id, None, f"{path}: {exc}"


def _canonical_split_images(master: dict[str, Any], subjects: list[str], shuffle: bool) -> list[dict[str, Any]]:
    subject_set = set(subjects)
    images = [image for image in master["images"] if subject_from_filename(image["file_name"]) in subject_set]
    if shuffle:
        random.Random(13).shuffle(images)
    return images


def _validate_yolo(report: DatasetValidationReport, master: dict[str, Any], split_subjects: dict[str, list[str]]) -> None:
    annotations_by_image: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for annotation in master["annotations"]:
        annotations_by_image[int(annotation["image_id"])].append(annotation)
    for split in ("train", "val", "test"):
        expected_images = _canonical_split_images(master, split_subjects[split], shuffle=split == "train")
        list_path = REPO_ROOT / "dataset" / "yolo" / f"{split}.txt"
        if not list_path.is_file():
            report.check(False, f"YOLO {split} list exists")
            continue
        actual_lines = list_path.read_text(encoding="utf-8").splitlines()
        expected_lines = ["./" + (Path("..") / Path(*Path(image["file_name"]).parts[1:])).as_posix() for image in expected_images]
        report.check(actual_lines == expected_lines, f"YOLO {split} order and membership match frozen policy")

    for image in master["images"]:
        relative = Path(*Path(image["file_name"]).parts[1:]).with_suffix(".txt")
        label_path = REPO_ROOT / "dataset" / "labels" / relative
        if not label_path.is_file():
            report.check(False, f"YOLO label exists for image {image['id']}")
            continue
        lines = [line for line in label_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        expected = annotations_by_image[int(image["id"])]
        if len(lines) != len(expected):
            report.check(False, f"YOLO label count matches image {image['id']}")
            continue
        for line, annotation in zip(lines, expected):
            try:
                values = [float(value) for value in line.split()]
                x, y, width, height = map(float, annotation["bbox"])
                target = [float(int(annotation["category_id"]) - 1), (x + width / 2) / 640, (y + height / 2) / 640, width / 640, height / 640]
                if len(values) != 5 or any(abs(a - b) > 5.1e-7 for a, b in zip(values, target)):
                    raise ValueError("coordinate mismatch")
            except Exception as exc:
                report.check(False, f"YOLO label parity for image {image['id']}: {exc}")
    report.check(True, "YOLO labels parsed and compared with master COCO")


def _validate_dfine(report: DatasetValidationReport, master: dict[str, Any], split_subjects: dict[str, list[str]]) -> None:
    for split in ("train", "val", "test"):
        path = REPO_ROOT / "dataset" / "coco" / f"instances_{split}.json"
        if not path.is_file():
            report.check(False, f"D-FINE {split} COCO exists")
            continue
        with path.open("r", encoding="utf-8") as handle:
            derived = json.load(handle)
        expected_images = _canonical_split_images(master, split_subjects[split], shuffle=split == "train")
        image_rank = {int(image["id"]): rank for rank, image in enumerate(expected_images)}
        expected_annotations = [annotation for annotation in master["annotations"] if int(annotation["image_id"]) in image_rank]
        if split == "train":
            expected_annotations.sort(key=lambda annotation: (image_rank[int(annotation["image_id"])], int(annotation["id"])))
        report.check(derived.get("images") == expected_images, f"D-FINE {split} image order and content match")
        report.check(derived.get("annotations") == expected_annotations, f"D-FINE {split} annotations match")
        report.check(derived.get("categories") == master["categories"], f"D-FINE {split} ontology matches")


def validate_dataset(full_image_scan: bool = True, workers: int = 8) -> DatasetValidationReport:
    protocol = load_protocol()
    dataset_spec = protocol["dataset"]
    report = DatasetValidationReport()
    try:
        verify_authoritative_fingerprints(protocol)
        report.check(True, "Authoritative annotation and split fingerprints match")
    except Exception as exc:
        report.check(False, str(exc))

    with resolve_repo_path(dataset_spec["annotations"]).open("r", encoding="utf-8") as handle:
        master = json.load(handle)
    with resolve_repo_path(dataset_spec["splits"]).open("r", encoding="utf-8") as handle:
        raw_splits = json.load(handle)
    split_subjects = {"train": raw_splits["train"], "val": raw_splits["validation"], "test": raw_splits["test"]}
    expected_categories = [{"id": int(key), "name": value, "supercategory": "driver_cue"} for key, value in dataset_spec["classes"].items()]
    report.check(master.get("categories") == expected_categories, "Master COCO ontology is exact")
    report.check(isinstance(master.get("images"), list) and isinstance(master.get("annotations"), list), "Master COCO arrays exist")

    image_ids = [int(image["id"]) for image in master["images"]]
    annotation_ids = [int(annotation["id"]) for annotation in master["annotations"]]
    filenames = [image["file_name"] for image in master["images"]]
    report.check(len(image_ids) == len(set(image_ids)), "Image IDs are unique")
    report.check(len(annotation_ids) == len(set(annotation_ids)), "Annotation IDs are unique")
    report.check(len(filenames) == len(set(filenames)), "Image filenames are unique")
    report.check(len(master["images"]) == dataset_spec["expected"]["global"]["images"], "Global image count is frozen")
    report.check(len(master["annotations"]) == dataset_spec["expected"]["global"]["annotations"], "Global annotation count is frozen")

    image_by_id = {int(image["id"]): image for image in master["images"]}
    annotations_per_image = Counter()
    class_counts = Counter()
    for annotation in master["annotations"]:
        image_id = int(annotation.get("image_id", -1))
        category_id = int(annotation.get("category_id", -1))
        annotations_per_image[image_id] += 1
        class_counts[category_id] += 1
        report.check(image_id in image_by_id, f"Annotation {annotation.get('id')} references an existing image")
        report.check(category_id in {1, 2, 3, 4}, f"Annotation {annotation.get('id')} category is valid")
        bbox = annotation.get("bbox", [])
        valid_bbox = len(bbox) == 4 and all(isinstance(value, (int, float)) and math.isfinite(value) for value in bbox)
        if valid_bbox:
            x, y, width, height = map(float, bbox)
            valid_bbox = width > 0 and height > 0 and x >= 0 and y >= 0 and x + width <= 640 and y + height <= 640
            # The protected master stores COCO area rounded to two decimals.
            valid_area = math.isclose(float(annotation.get("area", -1)), round(width * height, 2), rel_tol=0, abs_tol=1e-9)
        else:
            valid_area = False
        report.check(valid_bbox, f"Annotation {annotation.get('id')} bbox is finite, positive, and in bounds")
        report.check(valid_area, f"Annotation {annotation.get('id')} area equals bbox area")
    report.check(max(annotations_per_image.values(), default=0) <= dataset_spec["max_annotations_per_image"], "Frozen at-most-one-annotation policy holds")
    report.check(dict(class_counts) == {int(key): value for key, value in dataset_spec["expected"]["global"]["per_class"].items()}, "Global per-class counts are frozen")

    all_subjects = [subject for subjects in split_subjects.values() for subject in subjects]
    report.check(len(all_subjects) == dataset_spec["subjects"] and len(set(all_subjects)) == dataset_spec["subjects"], "Exactly 14 split subjects are disjoint")
    image_split: dict[int, str] = {}
    split_summary: dict[str, Any] = {}
    for split, subjects in split_subjects.items():
        expected = dataset_spec["expected"][split]
        subject_set = set(subjects)
        ids = {int(image["id"]) for image in master["images"] if subject_from_filename(image["file_name"]) in subject_set}
        image_split.update({image_id: split for image_id in ids})
        annotations = [annotation for annotation in master["annotations"] if int(annotation["image_id"]) in ids]
        counts = Counter(int(annotation["category_id"]) for annotation in annotations)
        negatives = len(ids) - len({int(annotation["image_id"]) for annotation in annotations})
        report.check(subjects == expected["subjects"], f"{split} subject assignment is exact")
        report.check(len(ids) == expected["images"], f"{split} image count is exact")
        report.check(len(annotations) == expected["annotations"], f"{split} annotation count is exact")
        report.check(negatives == expected["negatives"], f"{split} negative count is exact")
        report.check(dict(counts) == {int(key): value for key, value in expected["per_class"].items()}, f"{split} per-class counts are exact")
        report.check(set(counts) == {1, 2, 3, 4}, f"Every cue is present in {split}")
        split_summary[split] = {"images": len(ids), "annotations": len(annotations), "negatives": negatives, "per_class": dict(counts)}
    report.check(len(image_split) == len(master["images"]), "Every image belongs to exactly one frozen split")

    if full_image_scan:
        tasks = []
        for image in master["images"]:
            path = REPO_ROOT / "dataset" / image["file_name"]
            report.check(path.is_file(), f"Image file exists for ID {image['id']}")
            if path.is_file():
                report.check(int(image.get("width", -1)) == 640 and int(image.get("height", -1)) == 640, f"COCO dimensions are 640x640 for image {image['id']}")
                tasks.append((int(image["id"]), path, 640, 640))
        hashes: dict[str, list[int]] = defaultdict(list)
        with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
            for image_id, digest, error in pool.map(_inspect_image, tasks):
                report.check(error is None, error or f"Image {image_id} is readable JPEG 640x640")
                if digest:
                    hashes[digest].append(image_id)
        duplicates = {digest: ids for digest, ids in hashes.items() if len(ids) > 1}
        report.check(not duplicates, "No duplicate image content or cross-split content leakage")
        report.summary["distinct_image_sha256"] = len(hashes)

    _validate_yolo(report, master, split_subjects)
    _validate_dfine(report, master, split_subjects)
    report.summary.update({"global": {"images": len(master["images"]), "annotations": len(master["annotations"]), "negatives": len(master["images"]) - len(annotations_per_image), "per_class": dict(class_counts)}, "splits": split_summary})
    return report
