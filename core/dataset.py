"""
DMS-Eval Dataset & Ontology Definitions
=======================================
Maintains the frozen 4-cue single-frame driver monitoring ontology,
subject splits, and path resolution helpers.
"""

from pathlib import Path
import json

# Frozen 4-Cue Ontology
COCO_CATEGORIES = {
    1: {"id": 1, "name": "yawning", "supercategory": "driver_cue"},
    2: {"id": 2, "name": "hand_over_mouth", "supercategory": "driver_cue"},
    3: {"id": 3, "name": "drinking", "supercategory": "driver_cue"},
    4: {"id": 4, "name": "phone_use", "supercategory": "driver_cue"}
}

YOLO_NAMES = {
    0: "yawning",
    1: "hand_over_mouth",
    2: "drinking",
    3: "phone_use"
}

COCO_TO_YOLO = {1: 0, 2: 1, 3: 2, 4: 3}
YOLO_TO_COCO = {0: 1, 1: 2, 2: 3, 3: 4}

# Benchmark Image Specifications
INPUT_WIDTH = 640
INPUT_HEIGHT = 640
RANDOM_SEED = 13

def get_repo_root() -> Path:
    return Path(__file__).resolve().parent.parent

def load_splits(splits_path: Path = None) -> dict:
    if splits_path is None:
        splits_path = get_repo_root() / "dataset" / "splits.json"
    with open(splits_path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_master_coco(annotations_path: Path = None) -> dict:
    if annotations_path is None:
        annotations_path = get_repo_root() / "dataset" / "annotations.json"
    with open(annotations_path, "r", encoding="utf-8") as f:
        return json.load(f)
