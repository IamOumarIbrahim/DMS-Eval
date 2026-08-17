"""
DMS-Eval Agent-Assisted Pre-Annotation Engine
=============================================
Implements deterministic, rule-based vision pre-annotation strictly conforming
to the frozen DMS-Eval ontology (6 target cues):
1. `eyes_closed` (separate bounding box per eye)
2. `yawning` (mouth region only)
3. `head_down` (full head/face)
4. `hand_over_mouth` (full head/face)
5. `phone_use` (hand + phone together)
6. `head_turned_away` (full head/face)

Proposals are stored in Label Studio as `Prediction` objects (model_version: 'dms-eval-agent-v1.0').
Progress is tracked in `tools/label-studio/annotation_progress_ledger.json`.
Ambiguities and edge cases are logged in `tools/label-studio/annotation_decision_log.json`.
"""

import os
import sys
import json
import time
import pathlib
import datetime
import cv2
import numpy as np

repo_root = pathlib.Path(__file__).resolve().parents[2]
data_dir = repo_root / 'tools' / 'label-studio' / 'data'
manifest_file = repo_root / 'dataset' / 'manifest.json'
images_dir = repo_root / 'dataset' / 'images'
ledger_file = repo_root / 'tools' / 'label-studio' / 'annotation_progress_ledger.json'
decision_log_file = repo_root / 'tools' / 'label-studio' / 'annotation_decision_log.json'

os.environ['LABEL_STUDIO_BASE_DATA_DIR'] = str(data_dir)
os.environ['LABEL_STUDIO_LOCAL_FILES_SERVING_ENABLED'] = 'true'
os.environ['LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT'] = str(repo_root)

import label_studio.server
label_studio.server._setup_env()

from projects.models import Project
from tasks.models import Task, Prediction

# Load OpenCV Cascades
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
profile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_profileface.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')

MODEL_VERSION = "dms-eval-agent-v1.0"

def analyze_frame_cues(img_bgr):
    """
    Analyzes static 640x640 frame for the 6 frozen target cues.
    Returns: (proposals_list, secondary_review_flags, decision_notes)
    """
    h_img, w_img = img_bgr.shape[:2]
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    proposals = []
    secondary_review = False
    notes = []

    # 1. Face detection (Frontal + Profile)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))
    profiles = profile_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(100, 100))

    primary_face = None
    if len(faces) > 0:
        # Choose largest face box
        primary_face = max(faces, key=lambda b: b[2] * b[3])
    elif len(profiles) > 0:
        primary_face = max(profiles, key=lambda b: b[2] * b[3])
        # Detect head_turned_away from profile view
        fx, fy, fw, fh = primary_face
        proposals.append({
            "cue": "head_turned_away",
            "x": fx, "y": fy, "w": fw, "h": fh
        })
        notes.append("Detected profile face view -> head_turned_away")

    if primary_face is not None:
        fx, fy, fw, fh = primary_face

        # Check head_down (face detected significantly low in frame)
        if fy + fh > 520 and fy > 180:
            proposals.append({
                "cue": "head_down",
                "x": fx, "y": fy, "w": fw, "h": fh
            })
            notes.append(f"Head lowered substantially (y={fy}) -> head_down")

        # Head turned away check if face is strongly shifted laterally
        face_center_x = fx + fw / 2.0
        if face_center_x < 180 or face_center_x > 460:
            proposals.append({
                "cue": "head_turned_away",
                "x": fx, "y": fy, "w": fw, "h": fh
            })
            notes.append(f"Face center shifted laterally (cx={face_center_x:.1f}) -> head_turned_away")

        # Upper face region for eyes
        eye_region_y1 = fy + int(fh * 0.18)
        eye_region_y2 = fy + int(fh * 0.55)
        eye_roi_gray = gray[eye_region_y1:eye_region_y2, fx:fx + fw]

        # Lower face region for mouth
        mouth_region_y1 = fy + int(fh * 0.60)
        mouth_region_y2 = fy + fh
        mouth_roi_gray = gray[mouth_region_y1:mouth_region_y2, fx:fx + fw]

        # Eye state analysis
        if eye_roi_gray.size > 0:
            eyes = eye_cascade.detectMultiScale(eye_roi_gray, scaleFactor=1.1, minNeighbors=3, minSize=(25, 20))
            # If no open eyes detected or very low vertical eye contrast -> investigate closed eyes
            if len(eyes) == 0:
                # Estimate eye positions for closed eye boxes
                left_eye_x = fx + int(fw * 0.15)
                left_eye_y = eye_region_y1 + int((eye_region_y2 - eye_region_y1) * 0.2)
                left_eye_w = int(fw * 0.32)
                left_eye_h = int((eye_region_y2 - eye_region_y1) * 0.6)

                right_eye_x = fx + int(fw * 0.53)
                right_eye_y = left_eye_y
                right_eye_w = int(fw * 0.32)
                right_eye_h = left_eye_h

                # Check edge variance in eye patch
                patch_l = gray[left_eye_y:left_eye_y + left_eye_h, left_eye_x:left_eye_x + left_eye_w]
                patch_r = gray[right_eye_y:right_eye_y + right_eye_h, right_eye_x:right_eye_x + right_eye_w]

                if patch_l.size > 0 and patch_r.size > 0:
                    grad_l = cv2.Sobel(patch_l, cv2.CV_64F, 0, 1, ksize=3).var()
                    grad_r = cv2.Sobel(patch_r, cv2.CV_64F, 0, 1, ksize=3).var()

                    # High horizontal gradient line with low circular pupil intensity indicates closed lid
                    if grad_l > 120 and grad_r > 120:
                        proposals.append({
                            "cue": "eyes_closed",
                            "x": left_eye_x, "y": left_eye_y, "w": left_eye_w, "h": left_eye_h
                        })
                        proposals.append({
                            "cue": "eyes_closed",
                            "x": right_eye_x, "y": right_eye_y, "w": right_eye_w, "h": right_eye_h
                        })
                        notes.append("Low open-eye response + horizontal eyelid texture -> eyes_closed (2 separate boxes)")

        # Mouth / Yawn analysis
        if mouth_roi_gray.size > 0:
            # Check for large dark opening in mouth region
            _, mouth_thresh = cv2.threshold(mouth_roi_gray, 45, 255, cv2.THRESH_BINARY_INV)
            dark_ratio = np.count_nonzero(mouth_thresh) / mouth_thresh.size
            if dark_ratio > 0.38:
                mx = fx + int(fw * 0.25)
                my = mouth_region_y1 + int((mouth_region_y2 - mouth_region_y1) * 0.2)
                mw = int(fw * 0.50)
                mh = int((mouth_region_y2 - mouth_region_y1) * 0.75)
                proposals.append({
                    "cue": "yawning",
                    "x": mx, "y": my, "w": mw, "h": mh
                })
                notes.append("Large vertical mouth opening detected -> yawning")

        # Hand over mouth analysis (skin / hand occlusion in lower face)
        hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
        lower_face_hsv = hsv[mouth_region_y1:mouth_region_y2, fx:fx + fw]
        if lower_face_hsv.size > 0:
            # Skin mask in lower face
            skin_mask = cv2.inRange(lower_face_hsv, np.array([0, 20, 70]), np.array([25, 255, 255]))
            edges = cv2.Canny(skin_mask, 50, 150)
            edge_density = np.count_nonzero(edges) / edges.size
            if edge_density > 0.12 and not any(p["cue"] == "yawning" for p in proposals):
                proposals.append({
                    "cue": "hand_over_mouth",
                    "x": fx, "y": fy, "w": fw, "h": fh
                })
                notes.append("High edge/contour density over mouth area -> hand_over_mouth")

    # 2. Hand / Phone use analysis (lower quadrant of cabin)
    lower_quadrant_gray = gray[360:640, 0:420]
    if lower_quadrant_gray.size > 0:
        # Detect sharp rectangular edges / phone objects in hand region
        edges_q = cv2.Canny(lower_quadrant_gray, 80, 200)
        contours, _ = cv2.findContours(edges_q, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if 3000 < area < 45000:
                bx, by, bw, bh = cv2.boundingRect(cnt)
                aspect = bh / max(bw, 1)
                if 1.2 < aspect < 3.2 and bw > 40 and bh > 70:
                    px = max(0, bx - 20)
                    py = 360 + max(0, by - 20)
                    pw = min(640 - px, bw + 60)
                    ph = min(640 - py, bh + 60)
                    proposals.append({
                        "cue": "phone_use",
                        "x": px, "y": py, "w": pw, "h": ph
                    })
                    notes.append("Detected vertical handheld rectangular object -> phone_use")
                    break

    # Ambiguity check: if multiple conflicting weak signals exist
    if len(proposals) > 3:
        secondary_review = True
        notes.append("High cue density; marked for secondary human review")

    return proposals, secondary_review, notes

def format_ls_prediction(proposals, task_id):
    """Formats proposals into Label Studio prediction result structure."""
    results = []
    for idx, p in enumerate(proposals, start=1):
        x_pct = (p["x"] / 640.0) * 100.0
        y_pct = (p["y"] / 640.0) * 100.0
        w_pct = (p["w"] / 640.0) * 100.0
        h_pct = (p["h"] / 640.0) * 100.0

        results.append({
            "id": f"pred_{task_id}_{p['cue']}_{idx}",
            "type": "rectanglelabels",
            "value": {
                "x": round(x_pct, 2),
                "y": round(y_pct, 2),
                "width": round(w_pct, 2),
                "height": round(h_pct, 2),
                "rotation": 0,
                "rectanglelabels": [p["cue"]]
            },
            "to_name": "image",
            "from_name": "cues",
            "original_width": 640,
            "original_height": 640
        })
    return results

def process_batch(subject_filter=None, limit=None):
    """
    Processes tasks matching subject_filter in deterministic order.
    """
    project = Project.objects.filter(title='DMS-Eval').first()
    if not project:
        print("Project DMS-Eval not found!")
        return 0, 0, 0, 0

    # Load ledger
    with open(ledger_file, 'r', encoding='utf-8') as lf:
        ledger = json.load(lf)

    decision_log = {}
    if decision_log_file.exists():
        try:
            with open(decision_log_file, 'r', encoding='utf-8') as df:
                decision_log = json.load(df)
        except Exception:
            decision_log = {}

    tasks_qs = Task.objects.filter(project=project).order_by('id')
    
    processed_count = 0
    proposals_count = 0
    secondary_review_count = 0
    zero_proposals_count = 0

    for task in tasks_qs:
        data = task.data
        fname = data.get('filename')
        sub = data.get('subject')
        vid = data.get('video')

        if subject_filter and sub != subject_filter:
            continue

        if limit and processed_count >= limit:
            break

        # Check existing human annotations - NEVER touch human annotations
        if task.annotations.exists():
            continue

        # Check if already processed in ledger
        status = ledger.get(fname, {}).get('processing_status')
        if status in ['agent_processed', 'zero_proposals']:
            continue

        img_path = images_dir / sub / vid / fname
        if not img_path.exists():
            continue

        img = cv2.imread(str(img_path))
        if img is None:
            ledger[fname]['processing_status'] = 'failed'
            ledger[fname]['error'] = 'Could not read image'
            continue

        proposals, sec_rev, notes = analyze_frame_cues(img)
        pred_results = format_ls_prediction(proposals, task.id)

        # Update or create Prediction object
        existing_pred = Prediction.objects.filter(task=task, model_version=MODEL_VERSION).first()
        if existing_pred:
            existing_pred.result = pred_results
            existing_pred.save()
        else:
            Prediction.objects.create(
                task=task,
                project=project,
                result=pred_results,
                model_version=MODEL_VERSION
            )

        # Update ledger entry
        proc_status = 'zero_proposals' if len(proposals) == 0 else ('secondary_review_required' if sec_rev else 'agent_processed')
        ledger[fname] = {
            "filename": fname,
            "subject": sub,
            "video": vid,
            "sampled_frame_index": data.get('sampled_frame_index'),
            "processing_status": proc_status,
            "proposal_count": len(proposals),
            "proposed_classes": [p["cue"] for p in proposals],
            "secondary_review_required": sec_rev,
            "human_review_status": "unreviewed",
            "last_processed_timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "error": None
        }

        if notes:
            decision_log[fname] = {
                "subject": sub,
                "video": vid,
                "cues_detected": [p["cue"] for p in proposals],
                "secondary_review": sec_rev,
                "rationale": "; ".join(notes),
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
            }

        processed_count += 1
        proposals_count += len(proposals)
        if len(proposals) == 0:
            zero_proposals_count += 1
        if sec_rev:
            secondary_review_count += 1

    # Save ledger and decision log
    with open(ledger_file, 'w', encoding='utf-8') as lf:
        json.dump(ledger, lf, indent=2)

    with open(decision_log_file, 'w', encoding='utf-8') as df:
        json.dump(decision_log, df, indent=2)

    return processed_count, proposals_count, zero_proposals_count, secondary_review_count

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="DMS-Eval Pre-Annotation Runner")
    parser.add_argument("--subject", type=str, default=None, help="Filter by subject (e.g. subject_01)")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of processed images")
    args = parser.parse_args()

    n_proc, n_prop, n_zero, n_rev = process_batch(subject_filter=args.subject, limit=args.limit)
    print(f"Processed: {n_proc} frames | Proposals: {n_prop} boxes | Zero proposals: {n_zero} | Secondary review: {n_rev}")
