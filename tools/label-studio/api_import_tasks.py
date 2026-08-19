"""
Official REST API Project Setup and Task Importer
=================================================
Uses only supported Label Studio REST APIs with Token authentication.
"""

import os
import sys
import json
import pathlib
import requests
import xml.etree.ElementTree as ET

repo_root = pathlib.Path(__file__).resolve().parents[2]
env_file = repo_root / 'tools' / 'label-studio' / '.env'
config_file = repo_root / 'tools' / 'label-studio' / 'config' / 'dms_labeling_config.xml'
manifest_file = repo_root / 'dataset' / 'manifest.json'
images_dir = repo_root / 'dataset' / 'images'

api_key = ''
url = 'http://127.0.0.1:8080'
with open(env_file, 'r', encoding='utf-8') as f:
    for line in f:
        if line.startswith('LABEL_STUDIO_API_KEY='):
            api_key = line.strip().split('=', 1)[1]
        elif line.startswith('LABEL_STUDIO_URL='):
            url = line.strip().split('=', 1)[1]

headers = {
    'Authorization': f'Token {api_key}',
    'Content-Type': 'application/json'
}

# 1. Read XML config
with open(config_file, 'r', encoding='utf-8') as f:
    label_config = f.read()

# 2. Get or create project via REST API
r = requests.get(f'{url}/api/projects', headers=headers)
projects = r.json().get('results', [])

if projects:
    project = projects[0]
    proj_id = project['id']
    # Update title and label config
    patch_data = {
        'title': 'DMS-Eval',
        'description': 'DMS-Eval Benchmark Dataset (15,723 frames across 14 subjects) targeting 4 frozen warning cues.',
        'label_config': label_config
    }
    r_patch = requests.patch(f'{url}/api/projects/{proj_id}', json=patch_data, headers=headers)
    if r_patch.status_code != 200:
        raise RuntimeError(f"Failed to patch project {proj_id}: {r_patch.status_code} {r_patch.text}")
    print(f"Updated Project {proj_id} to 'DMS-Eval' via REST API")
else:
    post_data = {
        'title': 'DMS-Eval',
        'description': 'DMS-Eval Benchmark Dataset (15,723 frames across 14 subjects) targeting 4 frozen warning cues.',
        'label_config': label_config
    }
    r_post = requests.post(f'{url}/api/projects', json=post_data, headers=headers)
    if r_post.status_code != 201:
        raise RuntimeError(f"Failed to create project: {r_post.status_code} {r_post.text}")
    proj_id = r_post.json()['id']
    print(f"Created Project {proj_id} 'DMS-Eval' via REST API")

# 3. Read manifest and build tasks payload
with open(manifest_file, 'r', encoding='utf-8') as mf:
    manifest = json.load(mf)

all_tasks_payload = []
for entry in manifest:
    sub = entry['subject_folder']
    vid = entry['video_folder']
    vid_dir = images_dir / sub / vid
    if not vid_dir.exists():
        continue

    jpg_files = sorted([f for f in os.listdir(vid_dir) if f.endswith('.jpg')])
    for idx, fname in enumerate(jpg_files, start=1):
        rel_url = f"/data/local-files/?d=dataset/images/{sub}/{vid}/{fname}"
        all_tasks_payload.append({
            "data": {
                "image": rel_url,
                "filename": fname,
                "subject": sub,
                "video": vid,
                "sampled_frame_index": idx
            }
        })

print(f"Prepared {len(all_tasks_payload)} tasks for import via official REST API...")

# 4. Import tasks in chunks of 1000 via POST /api/projects/{id}/import
chunk_size = 1000
for i in range(0, len(all_tasks_payload), chunk_size):
    chunk = all_tasks_payload[i:i + chunk_size]
    r_imp = requests.post(f'{url}/api/projects/{proj_id}/import', json=chunk, headers=headers)
    if r_imp.status_code not in [200, 201]:
        print(f"Import chunk {i} failed: {r_imp.status_code} {r_imp.text[:200]}")
    else:
        print(f"  Imported {min(i + chunk_size, len(all_tasks_payload))}/{len(all_tasks_payload)} tasks...")

# 5. Verify Project Status via REST API
r_final = requests.get(f'{url}/api/projects/{proj_id}', headers=headers)
proj_final = r_final.json()
print("\n=== FINAL REST API VERIFICATION ===")
print("Project ID:", proj_final['id'])
print("Project Title:", proj_final['title'])
print("Total Tasks Number:", proj_final['task_number'])
print("Total Annotations Number:", proj_final['total_annotations_number'])
print("Total Predictions Number:", proj_final['total_predictions_number'])
