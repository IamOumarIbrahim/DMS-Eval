"""
Generate Shuffled Per-Subject Dataset Split Hierarchy
=====================================================
Duplicates per-subject annotations and creates:
  dataset/annotations_per_subject_shuffled/
  ├── Training/                  # 8 subjects (shuffled raw JSON & COCO with seed 13)
  │   ├── subject_01/
  │   │   ├── coco_annotations.json
  │   │   └── raw_annotations.json
  │   └── ... (subject_04, 06, 07, 08, 09, 13, 14)
  ├── Validation/                # 3 subjects (unshuffled, original sequential order)
  │   ├── subject_02/
  │   ├── subject_03/
  │   └── subject_11/
  └── Test/                      # 3 subjects (unshuffled, original sequential order)
      ├── subject_05/
      ├── subject_10/
      └── subject_12/

Randomization:
- Training subjects are shuffled using Python random.Random(13 + subj_num) for raw JSON and random.Random(13 + subj_num + 1000) for COCO JSON
- Validation and Test subjects remain strictly unshuffled
"""

import os
import json
import random
import copy
from collections import Counter

SEED = 13

SPLIT_FOLDER_MAP = {
    "train": "Training",
    "validation": "Validation",
    "test": "Test"
}

def check(cond: bool, msg: str):
    if not cond:
        raise ValueError(msg)

def create_shuffled_annotations():
    splits_file = "dataset/splits.json"
    src_base_dir = "dataset/annotations_per_subject"
    out_base_dir = "dataset/annotations_per_subject_shuffled"

    print(f"Loading split definition from {splits_file}...")
    with open(splits_file, "r", encoding="utf-8") as f:
        splits = json.load(f)

    os.makedirs(out_base_dir, exist_ok=True)

    total_images_written = 0
    total_boxes_written = 0
    total_raw_written = 0
    split_stats = {}

    print(f"\n--- Generating Shuffled Per-Subject Split Hierarchy (Seed: {SEED}) ---")

    for split_key, folder_name in SPLIT_FOLDER_MAP.items():
        subjs = splits[split_key]
        split_dir = os.path.join(out_base_dir, folder_name)
        os.makedirs(split_dir, exist_ok=True)

        is_train = (split_key == "train")
        split_imgs = 0
        split_boxes = 0
        split_raw = 0
        split_cues = Counter()

        print(f"\nProcessing [{folder_name}] split ({len(subjs)} subjects, Shuffled: {is_train})...")

        for subj in subjs:
            src_subj_dir = os.path.join(src_base_dir, subj)
            dst_subj_dir = os.path.join(split_dir, subj)
            os.makedirs(dst_subj_dir, exist_ok=True)

            coco_src = os.path.join(src_subj_dir, "coco_annotations.json")
            raw_src = os.path.join(src_subj_dir, "raw_annotations.json")

            with open(coco_src, "r", encoding="utf-8") as f:
                coco_data = json.load(f)

            with open(raw_src, "r", encoding="utf-8") as f:
                raw_data = json.load(f)

            orig_imgs_count = len(coco_data["images"])
            orig_boxes_count = len(coco_data["annotations"])
            orig_raw_count = len(raw_data)

            check(orig_imgs_count == orig_raw_count, f"Mismatch between images ({orig_imgs_count}) and raw tasks ({orig_raw_count}) in {subj}")

            if is_train:
                # Deterministic pseudo-random shuffling with seed 13
                # Single permutation order shared across companion files (images and raw tasks)
                subj_num = int(subj.split("_")[1])
                rng = random.Random(SEED + subj_num)

                order = list(range(orig_imgs_count))
                rng.shuffle(order)

                shuffled_images = [copy.deepcopy(coco_data["images"][i]) for i in order]
                shuffled_raw = [copy.deepcopy(raw_data[i]) for i in order]

                # Annotations reference image_id (not position); shuffle independently
                shuffled_annotations = copy.deepcopy(coco_data["annotations"])
                random.Random(SEED + subj_num + 1000).shuffle(shuffled_annotations)

                # Verify that order has changed
                if orig_imgs_count > 1:
                    check([img["id"] for img in shuffled_images] != [img["id"] for img in coco_data["images"]], f"Image shuffle check failed for {subj}")
                    check([t["id"] for t in shuffled_raw] != [t["id"] for t in raw_data], f"Raw task shuffle check failed for {subj}")

                # Verify 1-to-1 correspondence between shuffled images and shuffled raw tasks
                for idx_check, (img_item, raw_item) in enumerate(zip(shuffled_images, shuffled_raw)):
                    img_fname = os.path.basename(img_item["file_name"].replace("\\", "/"))
                    raw_fname = raw_item.get("data", {}).get("filename") or os.path.basename(raw_item.get("data", {}).get("image", "").replace("\\", "/"))
                    check(img_fname == raw_fname, f"Shuffle alignment desync at index {idx_check} in {subj}: {img_fname} vs {raw_fname}")

                coco_data["images"] = shuffled_images
                coco_data["annotations"] = shuffled_annotations
                coco_data["info"]["description"] = f"DMS-Eval Annotations for {subj} (Shuffled Frame Order, Seed {SEED})"
                raw_data = shuffled_raw
            else:
                # Validation and Test splits are preserved in exact sequential order
                pass

            # Write out files
            coco_dst = os.path.join(dst_subj_dir, "coco_annotations.json")
            raw_dst = os.path.join(dst_subj_dir, "raw_annotations.json")

            with open(coco_dst, "w", encoding="utf-8") as f:
                json.dump(coco_data, f, indent=2)

            with open(raw_dst, "w", encoding="utf-8") as f:
                json.dump(raw_data, f, indent=2)

            # Accumulate statistics
            cues = Counter([a["category_id"] for a in coco_data["annotations"]])
            split_cues += cues
            split_imgs += orig_imgs_count
            split_boxes += orig_boxes_count
            split_raw += orig_raw_count

            print(f"  [{folder_name}/{subj}] -> {orig_imgs_count} frames, {orig_boxes_count} boxes (P={cues[4]}, D={cues[3]}, Y={cues[1]}, H={cues[2]}), {orig_raw_count} raw tasks")

        split_stats[folder_name] = {
            "images": split_imgs,
            "boxes": split_boxes,
            "raw": split_raw,
            "cues": dict(split_cues)
        }
        total_images_written += split_imgs
        total_boxes_written += split_boxes
        total_raw_written += split_raw

    # Global Assertions & Parity Verification
    print("\n=== GLOBAL VERIFICATION SUMMARY ===")
    for folder, stats in split_stats.items():
        print(f"  {folder:12s}: {stats['images']:5d} frames, {stats['boxes']:4d} boxes, Cues: {stats['cues']}")

    print(f"\nTotal Frames Written : {total_images_written} (Expected: 15723)")
    print(f"Total Bounding Boxes : {total_boxes_written} (Expected: 3001)")
    print(f"Total Raw Tasks      : {total_raw_written} (Expected: 15723)")

    check(total_images_written == 15723, f"Image count mismatch: {total_images_written}")
    check(total_boxes_written == 3001, f"Box count mismatch: {total_boxes_written}")
    check(total_raw_written == 15723, f"Raw task count mismatch: {total_raw_written}")

    check(split_stats["Training"]["images"] == 9087, f"Training images mismatch: {split_stats['Training']['images']}")
    check(split_stats["Training"]["boxes"] == 1748, f"Training boxes mismatch: {split_stats['Training']['boxes']}")
    check(split_stats["Validation"]["images"] == 3423, f"Validation images mismatch: {split_stats['Validation']['images']}")
    check(split_stats["Validation"]["boxes"] == 639, f"Validation boxes mismatch: {split_stats['Validation']['boxes']}")
    check(split_stats["Test"]["images"] == 3213, f"Test images mismatch: {split_stats['Test']['images']}")
    check(split_stats["Test"]["boxes"] == 614, f"Test boxes mismatch: {split_stats['Test']['boxes']}")

    print("\n[OK] Successfully created and verified dataset/annotations_per_subject_shuffled!")

if __name__ == "__main__":
    create_shuffled_annotations()
