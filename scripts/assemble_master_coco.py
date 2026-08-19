"""
Assemble and Validate Master COCO JSON (dataset/annotations.json)
================================================================
Converts the authoritative Label Studio 14-subject export into the canonical
master COCO ground truth for the DMS-Eval benchmark.

Requirements enforced:
1. Relative image paths (e.g. 'images/subject_01/video_01/subject_01_video_01_frame_0001.jpg').
2. Category IDs mapped strictly to 1-4:
   - 1: 'yawning'
   - 2: 'hand_over_mouth'
   - 3: 'drinking'
   - 4: 'phone_use'
3. Validated, clamped bounding boxes within [0, 0, 640, 640].
4. Exact count validation: 15,723 images, 3,001 bounding boxes (12,722 negative frames).
"""

import os
import json
import zipfile
from datetime import datetime

# Category Mapping (1-indexed COCO convention)
CATEGORY_MAP = {
    'yawning': 1,
    'hand_over_mouth': 2,
    'drinking': 3,
    'phone_use': 4
}

CATEGORIES = [
    {"id": 1, "name": "yawning", "supercategory": "driver_cue"},
    {"id": 2, "name": "hand_over_mouth", "supercategory": "driver_cue"},
    {"id": 3, "name": "drinking", "supercategory": "driver_cue"},
    {"id": 4, "name": "phone_use", "supercategory": "driver_cue"}
]

def make_relative_path(abs_or_raw_path: str) -> str:
    """Normalize path to relative 'images/subject_XX/video_YY/filename.jpg'."""
    normalized = abs_or_raw_path.replace('\\', '/')
    idx = normalized.find('images/')
    if idx != -1:
        return normalized[idx:]
    # Fallback if only filename
    parts = normalized.split('/')
    fname = parts[-1]
    # Extract subject and video from fname: subject_01_video_01_frame_0001.jpg
    tokens = fname.split('_')
    if len(tokens) >= 4 and tokens[0] == 'subject' and tokens[2] == 'video':
        subj = f"subject_{tokens[1]}"
        vid = f"video_{tokens[3]}"
        return f"images/{subj}/{vid}/{fname}"
    return f"images/{fname}"

def assemble_master_coco():
    zip_path = r"dataset/All_Subjects_annotated/project-1-at-2026-08-19-17-29-a3bbb88e.zip"
    json_export_path = r"dataset/All_Subjects_annotated/project-1-at-2026-08-19-17-28-a3bbb88e.json"
    out_coco_path = r"dataset/annotations.json"

    print(f"Reading export from: {zip_path}")
    with zipfile.ZipFile(zip_path, 'r') as z:
        raw_coco = json.loads(z.read('result.json').decode('utf-8'))

    raw_images = raw_coco.get('images', [])
    raw_annotations = raw_coco.get('annotations', [])
    raw_categories = raw_coco.get('categories', [])

    # Map raw category ID to category name
    raw_cat_id_to_name = {c['id']: c['name'] for c in raw_categories}
    print(f"Raw categories in export: {raw_cat_id_to_name}")

    # Build standard images array
    # We will map raw image_id to 1-indexed sequential image_id (1..15723)
    # Sort images by filename for deterministic order
    sorted_raw_images = sorted(raw_images, key=lambda x: make_relative_path(x['file_name']))

    raw_id_to_new_id = {}
    master_images = []

    for new_id, img in enumerate(sorted_raw_images, start=1):
        raw_id_to_new_id[img['id']] = new_id
        rel_path = make_relative_path(img['file_name'])
        
        master_images.append({
            "id": new_id,
            "file_name": rel_path,
            "width": 640,
            "height": 640
        })

    print(f"Processed {len(master_images)} image records.")

    # Build standard annotations array
    master_annotations = []
    category_counts = {1: 0, 2: 0, 3: 0, 4: 0}
    images_with_boxes = set()

    for ann_id, ann in enumerate(raw_annotations, start=1):
        raw_img_id = ann['image_id']
        new_img_id = raw_id_to_new_id[raw_img_id]
        images_with_boxes.add(new_img_id)

        raw_cat_id = ann['category_id']
        cat_name = raw_cat_id_to_name[raw_cat_id]
        new_cat_id = CATEGORY_MAP[cat_name]
        category_counts[new_cat_id] += 1

        # Validate and clamp bbox [x, y, w, h] within 640x640
        x, y, w, h = ann['bbox']
        
        # Clamp to [0, 640]
        x_clamped = max(0.0, min(640.0, float(x)))
        y_clamped = max(0.0, min(640.0, float(y)))
        
        # Ensure w and h don't exceed image bounds
        w_clamped = max(1.0, min(640.0 - x_clamped, float(w)))
        h_clamped = max(1.0, min(640.0 - y_clamped, float(h)))

        # Round to 2 decimal places for clean formatting
        x_final = round(x_clamped, 2)
        y_final = round(y_clamped, 2)
        w_final = round(w_clamped, 2)
        h_final = round(h_clamped, 2)
        area_final = round(w_final * h_final, 2)

        master_annotations.append({
            "id": ann_id,
            "image_id": new_img_id,
            "category_id": new_cat_id,
            "bbox": [x_final, y_final, w_final, h_final],
            "area": area_final,
            "segmentation": [],
            "iscrowd": 0,
            "ignore": 0
        })

    print(f"Processed {len(master_annotations)} annotation records.")
    print(f"Category counts (1:yawn, 2:hand, 3:drink, 4:phone): {category_counts}")
    print(f"Positive images count: {len(images_with_boxes)}")
    print(f"Negative images count: {len(master_images) - len(images_with_boxes)}")

    # Verify benchmark invariants
    assert len(master_images) == 15723, f"Expected 15,723 images, got {len(master_images)}"
    assert len(master_annotations) == 3001, f"Expected 3,001 annotations, got {len(master_annotations)}"
    assert category_counts[1] == 159, f"Expected 159 yawning, got {category_counts[1]}"
    assert category_counts[2] == 141, f"Expected 141 hand_over_mouth, got {category_counts[2]}"
    assert category_counts[3] == 264, f"Expected 264 drinking, got {category_counts[3]}"
    assert category_counts[4] == 2437, f"Expected 2,437 phone_use, got {category_counts[4]}"
    assert len(images_with_boxes) == 3001, "Single annotation policy check failed (duplicate boxes found)"

    master_coco = {
        "info": {
            "description": "DMS-Eval Master Benchmark Annotations (Authoritative Human Ground Truth)",
            "url": "https://github.com/IamOumarIbrahim/DMS-Eval",
            "version": "1.0",
            "year": 2026,
            "contributor": "DMS-Eval Research Team",
            "date_created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        },
        "licenses": [
            {
                "id": 1,
                "name": "Apache License 2.0",
                "url": "https://www.apache.org/licenses/LICENSE-2.0"
            }
        ],
        "images": master_images,
        "annotations": master_annotations,
        "categories": CATEGORIES
    }

    print(f"Writing master COCO JSON to {out_coco_path}...")
    with open(out_coco_path, 'w', encoding='utf-8') as f:
        json.dump(master_coco, f, indent=2)

    file_size_mb = os.path.getsize(out_coco_path) / (1024 * 1024)
    print(f"Successfully generated {out_coco_path} ({file_size_mb:.2f} MB)")

if __name__ == "__main__":
    assemble_master_coco()
