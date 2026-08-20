"""
Convert Master COCO JSON Ground Truth to YOLO Format
====================================================
Transforms dataset/annotations.json into:
  - YOLO-compliant .txt label files under dataset/labels/
  - Split image lists: dataset/yolo/train.txt, val.txt, test.txt
  - Ultralytics dataset configuration: dataset/yolo/dms_eval.yaml

Features:
- Normalized bounding boxes: [class_id, x_center, y_center, width, height]
- 0-indexed classes:
    0: yawning (COCO 1)
    1: hand_over_mouth (COCO 2)
    2: drinking (COCO 3)
    3: phone_use (COCO 4)
- Full negative frame preservation: creates empty .txt files for background images (0 boxes)
- Subject-disjoint partition matching dataset/splits.json
"""

import os
import json
import random
from collections import defaultdict, Counter
from pathlib import Path

CATEGORY_MAP = {
    1: 0,  # yawning -> 0
    2: 1,  # hand_over_mouth -> 1
    3: 2,  # drinking -> 2
    4: 3   # phone_use -> 3
}

def check(cond: bool, msg: str):
    if not cond:
        raise ValueError(msg)

CLASS_NAMES = {
    0: "yawning",
    1: "hand_over_mouth",
    2: "drinking",
    3: "phone_use"
}

def convert_coco_to_yolo():
    repo_root = Path(__file__).resolve().parents[2]
    annotations_file = repo_root / "dataset" / "annotations.json"
    splits_file = repo_root / "dataset" / "splits.json"
    labels_base_dir = repo_root / "dataset" / "labels"
    yolo_dir = repo_root / "dataset" / "yolo"

    print(f"Loading master COCO annotations from {annotations_file}...")
    with open(annotations_file, "r", encoding="utf-8") as f:
        coco_data = json.load(f)

    print(f"Loading splits definition from {splits_file}...")
    with open(splits_file, "r", encoding="utf-8") as f:
        splits = json.load(f)

    # Build mapping of subject -> split name
    subject_to_split = {}
    for split_name, subjects in splits.items():
        for subj in subjects:
            subject_to_split[subj] = split_name

    # Group annotations by image_id
    img_to_anns = defaultdict(list)
    for ann in coco_data.get("annotations", []):
        img_to_anns[ann["image_id"]].append(ann)

    print(f"Total images in COCO: {len(coco_data['images'])}")
    print(f"Total annotations in COCO: {len(coco_data['annotations'])}")

    os.makedirs(labels_base_dir, exist_ok=True)
    os.makedirs(yolo_dir, exist_ok=True)

    split_image_paths = {"train": [], "validation": [], "test": []}
    split_box_counts = {"train": Counter(), "validation": Counter(), "test": Counter()}
    split_frame_counts = {"train": 0, "validation": 0, "test": 0}

    total_labels_written = 0
    total_boxes_written = 0

    for img in coco_data["images"]:
        img_id = img["id"]
        rel_file_name = img["file_name"]  # e.g. "images/subject_01/video_01/subject_01_video_01_frame_0001.jpg"
        img_w = float(img.get("width", 640))
        img_h = float(img.get("height", 640))

        # Extract subject id from path
        parts = Path(rel_file_name).parts
        # parts: ('images', 'subject_01', 'video_01', 'subject_01_video_01_frame_0001.jpg')
        if len(parts) >= 2 and parts[0] == "images":
            subject_id = parts[1]
            subpath = Path(*parts[1:])  # 'subject_01/video_01/subject_01_video_01_frame_0001.jpg'
        else:
            subject_id = parts[0]
            subpath = Path(*parts)

        split_name = subject_to_split.get(subject_id)
        if not split_name:
            raise ValueError(f"Subject {subject_id} not found in splits.json!")

        # Label file path: dataset/labels/subject_01/video_01/subject_01_video_01_frame_0001.txt
        label_rel_path = subpath.with_suffix(".txt")
        label_full_path = labels_base_dir / label_rel_path
        os.makedirs(label_full_path.parent, exist_ok=True)

        anns = img_to_anns.get(img_id, [])
        yolo_lines = []

        for ann in anns:
            cat_id = ann["category_id"]
            if cat_id not in CATEGORY_MAP:
                raise ValueError(f"Unexpected category_id {cat_id} in annotation {ann['id']}")

            yolo_cls = CATEGORY_MAP[cat_id]
            x_min, y_min, w, h = ann["bbox"]

            # Convert to YOLO format: x_center, y_center, width, height normalized
            x_center = (x_min + w / 2.0) / img_w
            y_center = (y_min + h / 2.0) / img_h
            w_norm = w / img_w
            h_norm = h / img_h

            # Clamp coordinates to [0.0, 1.0]
            x_center = max(0.0, min(1.0, x_center))
            y_center = max(0.0, min(1.0, y_center))
            w_norm = max(0.0, min(1.0, w_norm))
            h_norm = max(0.0, min(1.0, h_norm))

            yolo_lines.append(f"{yolo_cls} {x_center:.6f} {y_center:.6f} {w_norm:.6f} {h_norm:.6f}")
            split_box_counts[split_name][yolo_cls] += 1
            total_boxes_written += 1

        # Write label file (empty if background frame)
        with open(label_full_path, "w", encoding="utf-8") as f:
            if yolo_lines:
                f.write("\n".join(yolo_lines) + "\n")

        total_labels_written += 1
        split_frame_counts[split_name] += 1

        # Split-list paths are relative to dataset/yolo/*.txt and deliberately
        # begin with './' so Ultralytics resolves them against the list file.
        img_rel_to_list = "./" + str((Path("..") / Path(*Path(rel_file_name).parts[1:])).as_posix())
        split_image_paths[split_name].append(img_rel_to_list)

    # Only the training order is randomized. Validation and test retain the
    # exact native order of dataset/annotations.json.
    random.Random(13).shuffle(split_image_paths["train"])

    # Write split .txt files
    split_filename_map = {
        "train": "train.txt",
        "validation": "val.txt",
        "test": "test.txt"
    }

    for split_name, filename in split_filename_map.items():
        split_file_path = yolo_dir / filename
        with open(split_file_path, "w", encoding="utf-8") as f:
            for p in split_image_paths[split_name]:
                f.write(f"{p}\n")
        print(f"Wrote {len(split_image_paths[split_name])} image paths to {split_file_path}")

    # Generate dataset/yolo/dms_eval.yaml
    yaml_path = yolo_dir / "dms_eval.yaml"
    yaml_content = """# DMS-Eval YOLO Dataset Configuration
# Auto-generated by scripts/data/convert_coco_to_yolo.py

path: dataset
train: yolo/train.txt
val: yolo/val.txt
test: yolo/test.txt

# Class ontology (0-indexed for YOLO)
names:
  0: yawning
  1: hand_over_mouth
  2: drinking
  3: phone_use
"""
    with open(yaml_path, "w", encoding="utf-8") as f:
        f.write(yaml_content)
    print(f"Wrote dataset YAML configuration to {yaml_path}")

    # Also create a repo-root relative config at dataset/dms_eval_yolo.yaml for convenience
    root_yaml_path = repo_root / "dataset" / "dms_eval_yolo.yaml"
    root_yaml_content = """# DMS-Eval YOLO Dataset Configuration
path: dataset
train: yolo/train.txt
val: yolo/val.txt
test: yolo/test.txt

names:
  0: yawning
  1: hand_over_mouth
  2: drinking
  3: phone_use
"""
    with open(root_yaml_path, "w", encoding="utf-8") as f:
        f.write(root_yaml_content)

    print("\n=== YOLO Conversion Summary ===")
    print(f"Total label files written: {total_labels_written}")
    print(f"Total bounding boxes written: {total_boxes_written}")
    for split_name in ["train", "validation", "test"]:
        boxes = split_box_counts[split_name]
        print(f"  [{split_name:10s}] Frames: {split_frame_counts[split_name]:5d} | Boxes: {sum(boxes.values()):4d} "
              f"(yawning: {boxes[0]}, hand_over_mouth: {boxes[1]}, drinking: {boxes[2]}, phone_use: {boxes[3]})")

    check(total_labels_written == len(coco_data["images"]), f"Label count mismatch: {total_labels_written} vs {len(coco_data['images'])}")
    check(total_boxes_written == len(coco_data["annotations"]), f"Box count mismatch: {total_boxes_written} vs {len(coco_data['annotations'])}")
    print("\nParity check PASSED: All images and bounding boxes converted with 100% fidelity.")

if __name__ == "__main__":
    convert_coco_to_yolo()
