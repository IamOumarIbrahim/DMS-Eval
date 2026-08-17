"""
Import All 15,723 DMS-Eval Tasks into Label Studio
===================================================
Creates/configures the single 'DMS-Eval' project and imports all 15,723 frames
from `dataset/images/` with complete task metadata.
"""

import os
import sys
import json
import pathlib
import time

repo_root = pathlib.Path(__file__).resolve().parents[2]
data_dir = repo_root / 'tools' / 'label-studio' / 'data'
config_file = repo_root / 'tools' / 'label-studio' / 'config' / 'dms_labeling_config.xml'
manifest_file = repo_root / 'dataset' / 'manifest.json'
images_dir = repo_root / 'dataset' / 'images'
ledger_file = repo_root / 'tools' / 'label-studio' / 'annotation_progress_ledger.json'

os.environ['LABEL_STUDIO_BASE_DATA_DIR'] = str(data_dir)
os.environ['LABEL_STUDIO_LOCAL_FILES_SERVING_ENABLED'] = 'true'
os.environ['LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT'] = str(repo_root)

import label_studio.server
label_studio.server._setup_env()

from organizations.models import Organization
from users.models import User
from projects.models import Project
from tasks.models import Task
from io_storages.localfiles.models import LocalFilesImportStorage

def get_or_create_user_and_org():
    user = User.objects.filter(is_active=True).first()
    if not user:
        user = User.objects.create_user(email='annotator@dms-eval.local', password='password123')
        org = Organization.create_organization(created_by=user, title='DMS-Eval')
        user.active_organization = org
        user.save()
    else:
        org = user.active_organization or Organization.objects.first()
    return user, org

def main():
    t0 = time.time()
    user, org = get_or_create_user_and_org()

    with open(config_file, 'r', encoding='utf-8') as f:
        label_config = f.read()

    # 1. Project Setup
    project = Project.objects.filter(title='DMS-Eval').first()
    if not project:
        project = Project.objects.create(
            title='DMS-Eval',
            organization=org,
            created_by=user,
            description='DMS-Eval Benchmark Dataset (15,723 frames) across 14 subjects targeting 6 frozen warning cues.',
            label_config=label_config
        )
    else:
        project.label_config = label_config
        project.save()

    # 2. Local Storage Setup
    storage, _ = LocalFilesImportStorage.objects.get_or_create(
        project=project,
        path=str((images_dir).resolve()),
        defaults={'title': 'DMS-Eval Local Images', 'use_blob_urls': True}
    )

    print(f"Project 'DMS-Eval' (ID: {project.id}) ready. Storage ID: {storage.id}")

    # 3. Load manifest and build task objects
    with open(manifest_file, 'r', encoding='utf-8') as mf:
        manifest = json.load(mf)

    # Check existing tasks
    existing_tasks = Task.objects.filter(project=project).values_list('data', flat=True)
    existing_filenames = set()
    for d in existing_tasks:
        if isinstance(d, dict) and 'filename' in d:
            existing_filenames.add(d['filename'])

    print(f"Existing tasks in project: {len(existing_filenames)}")

    task_objects = []
    ledger_entries = {}

    # Load existing ledger if present
    if ledger_file.exists():
        try:
            with open(ledger_file, 'r', encoding='utf-8') as lf:
                ledger_entries = json.load(lf)
        except Exception:
            ledger_entries = {}

    for entry in manifest:
        sub = entry['subject_folder']
        vid = entry['video_folder']
        vid_dir = images_dir / sub / vid
        if not vid_dir.exists():
            continue

        jpg_files = sorted([f for f in os.listdir(vid_dir) if f.endswith('.jpg')])
        for idx, fname in enumerate(jpg_files, start=1):
            if fname not in existing_filenames:
                rel_url = f"/data/local-files/?d=dataset/images/{sub}/{vid}/{fname}"
                task_data = {
                    "image": rel_url,
                    "filename": fname,
                    "subject": sub,
                    "video": vid,
                    "sampled_frame_index": idx
                }
                task_objects.append(Task(project=project, data=task_data))

            if fname not in ledger_entries:
                ledger_entries[fname] = {
                    "filename": fname,
                    "subject": sub,
                    "video": vid,
                    "sampled_frame_index": idx,
                    "processing_status": "not_processed",
                    "proposal_count": 0,
                    "proposed_classes": [],
                    "secondary_review_required": False,
                    "human_review_status": "unreviewed",
                    "last_processed_timestamp": None,
                    "error": None
                }

    if task_objects:
        print(f"Bulk creating {len(task_objects)} new tasks...")
        batch_size = 1000
        for i in range(0, len(task_objects), batch_size):
            chunk = task_objects[i:i + batch_size]
            Task.objects.bulk_create(chunk)
            print(f"  Imported {min(i + batch_size, len(task_objects))}/{len(task_objects)} tasks...")

    # Save ledger
    with open(ledger_file, 'w', encoding='utf-8') as lf:
        json.dump(ledger_entries, lf, indent=2)

    total_tasks = Task.objects.filter(project=project).count()
    print(f"\nTask import complete in {round(time.time() - t0, 1)}s.")
    print(f"Total project tasks: {total_tasks} / 15723")
    print(f"Ledger entries: {len(ledger_entries)}")

if __name__ == '__main__':
    main()
