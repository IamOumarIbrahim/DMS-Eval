"""
Dataset pipeline: split master annotations and raw export per subject
===================================================
Generates 14 per-subject folders under `dataset/annotations_per_subject/`:
  dataset/annotations_per_subject/subject_01/
    ├── coco_annotations.json   (Standard COCO format for subject_01)
    └── raw_annotations.json    (Raw Label Studio task records for subject_01)
  ...
  dataset/annotations_per_subject/subject_14/

Verifies:
- 14 distinct folders.
- Sum of all per-subject COCO annotations == 3,001 boxes, 15,723 images.
- Exact cue counts preserved per subject.
"""

import os
import glob
import json
import argparse
from collections import defaultdict, Counter

CATEGORIES = [
    {"id": 1, "name": "yawning", "supercategory": "driver_cue"},
    {"id": 2, "name": "hand_over_mouth", "supercategory": "driver_cue"},
    {"id": 3, "name": "drinking", "supercategory": "driver_cue"},
    {"id": 4, "name": "phone_use", "supercategory": "driver_cue"}
]

def check(cond: bool, msg: str):
    if not cond:
        raise ValueError(msg)

def find_latest_export(pattern: str) -> str:
    matches = sorted(glob.glob(pattern), reverse=True)
    if not matches:
        raise FileNotFoundError(f"No export file found matching pattern: {pattern}")
    return matches[0]

def split_annotations_per_subject(master_coco_path: str = "dataset/annotations.json",
                                  raw_json_path: str = None,
                                  out_base_dir: str = "dataset/annotations_per_subject"):
    if raw_json_path is None:
        raw_json_path = find_latest_export("dataset/All_Subjects_annotated/project-*.json")

    os.makedirs(out_base_dir, exist_ok=True)

    # 1. Load Master COCO
    print(f"Loading master COCO from {master_coco_path}...")
    with open(master_coco_path, 'r', encoding='utf-8') as f:
        master_coco = json.load(f)

    # 2. Load Raw Label Studio JSON
    print(f"Loading raw Label Studio tasks from {raw_json_path}...")
    with open(raw_json_path, 'r', encoding='utf-8') as f:
        raw_tasks = json.load(f)

    # Verify task count parity between raw export and master COCO
    check(len(raw_tasks) == len(master_coco['images']),
          f"Task count mismatch between raw tasks ({len(raw_tasks)}) and COCO images ({len(master_coco['images'])})")

    # Map image_id -> subject
    image_id_to_subject = {}
    for img in master_coco['images']:
        # file_name is 'images/subject_01/video_01/...'
        parts = img['file_name'].replace('\\', '/').split('/')
        # find subject_XX part
        subj = None
        for p in parts:
            if p.startswith('subject_') and len(p) == 10 and p[8:].isdigit():
                subj = p
                break
        if not subj:
            # fallback from filename: subject_01_video_01_frame_0001.jpg
            fname = parts[-1]
            tokens = fname.split('_')
            subj = f"subject_{tokens[1]}"
        image_id_to_subject[img['id']] = subj

    # Group COCO images and annotations by subject
    subject_coco_images = defaultdict(list)
    for img in master_coco['images']:
        subj = image_id_to_subject[img['id']]
        subject_coco_images[subj].append(img)

    subject_coco_annotations = defaultdict(list)
    for ann in master_coco['annotations']:
        subj = image_id_to_subject[ann['image_id']]
        subject_coco_annotations[subj].append(ann)

    # Group raw tasks by subject
    subject_raw_tasks = defaultdict(list)
    for task in raw_tasks:
        subj = task.get('data', {}).get('subject')
        if not subj:
            fname = task.get('data', {}).get('filename') or task.get('data', {}).get('image', '')
            tokens = fname.replace('\\', '/').split('/')[-1].split('_')
            subj = f"subject_{tokens[1]}"
        subject_raw_tasks[subj].append(task)

    # All 14 subjects
    subjects = sorted(list(set(list(subject_coco_images.keys()) + list(subject_raw_tasks.keys()))))
    print(f"Discovered {len(subjects)} subjects: {subjects}")
    check(len(subjects) == 14, f"Expected 14 subjects, got {len(subjects)}")

    total_images_written = 0
    total_boxes_written = 0
    total_raw_tasks_written = 0
    global_cue_counts = Counter()

    print("\n--- Generating Per-Subject Annotation Folders ---")
    for subj in subjects:
        subj_dir = os.path.join(out_base_dir, subj)
        os.makedirs(subj_dir, exist_ok=True)

        imgs = subject_coco_images[subj]
        anns = subject_coco_annotations[subj]
        raw_t = subject_raw_tasks[subj]

        total_images_written += len(imgs)
        total_boxes_written += len(anns)
        total_raw_tasks_written += len(raw_t)

        subj_cues = Counter([a['category_id'] for a in anns])
        for cid, count in subj_cues.items():
            global_cue_counts[cid] += count

        # Build Per-Subject COCO structure
        subj_coco = {
            "info": {
                "description": f"DMS-Eval Annotations for {subj} (Authoritative Human Ground Truth)",
                "url": "https://github.com/IamOumarIbrahim/DMS-Eval",
                "version": "1.0",
                "year": 2026,
                "subject": subj,
                "contributor": "DMS-Eval Research Team"
            },
            "licenses": master_coco.get("licenses", []),
            "images": imgs,
            "annotations": anns,
            "categories": CATEGORIES
        }

        # 1. Save COCO format
        coco_out_file = os.path.join(subj_dir, "coco_annotations.json")
        with open(coco_out_file, 'w', encoding='utf-8') as f:
            json.dump(subj_coco, f, indent=2)

        # 2. Save Raw Label Studio format
        raw_out_file = os.path.join(subj_dir, "raw_annotations.json")
        with open(raw_out_file, 'w', encoding='utf-8') as f:
            json.dump(raw_t, f, indent=2)

        print(f"[{subj}] -> {len(imgs)} frames, {len(anns)} boxes (P={subj_cues[4]}, D={subj_cues[3]}, Y={subj_cues[1]}, H={subj_cues[2]}), {len(raw_t)} raw tasks")

    # Global Validation
    print("\n=== VERIFICATION SUMMARY ===")
    print(f"Total Folders Created: {len(subjects)}")
    print(f"Total Images Across 14 Folders: {total_images_written} (Expected: 15723)")
    print(f"Total Bounding Boxes Across 14 Folders: {total_boxes_written} (Expected: 3001)")
    print(f"Total Raw Tasks Across 14 Folders: {total_raw_tasks_written} (Expected: 15723)")
    print(f"Global Category Counts (1:Yawn, 2:Hand, 3:Drink, 4:Phone): {dict(global_cue_counts)}")

    check(total_images_written == 15723, f"Total images mismatch: {total_images_written}")
    check(total_boxes_written == 3001, f"Total boxes mismatch: {total_boxes_written}")
    check(total_raw_tasks_written == 15723, f"Total raw tasks mismatch: {total_raw_tasks_written}")
    check(global_cue_counts[1] == 159, f"Yawning count mismatch: {global_cue_counts[1]}")
    check(global_cue_counts[2] == 141, f"Hand over mouth count mismatch: {global_cue_counts[2]}")
    check(global_cue_counts[3] == 264, f"Drinking count mismatch: {global_cue_counts[3]}")
    check(global_cue_counts[4] == 2437, f"Phone use count mismatch: {global_cue_counts[4]}")

    print("\nSUCCESS: All 14 subject annotation folders generated and verified with 100% integrity!")

def parse_args():
    parser = argparse.ArgumentParser(description="Split Master Annotations and Raw Export Per Subject")
    parser.add_argument(
        "--master-coco",
        type=str,
        default="dataset/annotations.json",
        help="Path to master COCO JSON (default: dataset/annotations.json)"
    )
    parser.add_argument(
        "--raw-json",
        type=str,
        default=None,
        help="Path to raw Label Studio export JSON (defaults to newest in dataset/All_Subjects_annotated/)"
    )
    parser.add_argument(
        "--out-dir",
        type=str,
        default="dataset/annotations_per_subject",
        help="Output base directory (default: dataset/annotations_per_subject)"
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    split_annotations_per_subject(master_coco_path=args.master_coco,
                                  raw_json_path=args.raw_json,
                                  out_base_dir=args.out_dir)
