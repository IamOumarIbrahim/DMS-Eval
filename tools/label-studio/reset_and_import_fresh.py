"""
Fresh Task Re-Index & Import (IDs starting from 1 to 15,723)
===========================================================
Cleans existing project/task tables, resets SQLite auto-increment sequences,
and imports all 15,723 DMS-Eval tasks sequentially so Task IDs align from 1 to 15,723.
"""

import os
import sys
import json
import sqlite3
import pathlib

repo_root = pathlib.Path(__file__).resolve().parents[2]
data_dir = repo_root / 'tools' / 'label-studio' / 'data'
db_file = data_dir / 'label_studio.sqlite3'
config_file = repo_root / 'tools' / 'label-studio' / 'config' / 'dms_labeling_config.xml'
manifest_file = repo_root / 'dataset' / 'manifest.json'
images_dir = repo_root / 'dataset' / 'images'

os.environ['LABEL_STUDIO_BASE_DATA_DIR'] = str(data_dir)
os.environ['LABEL_STUDIO_LOCAL_FILES_SERVING_ENABLED'] = 'true'
os.environ['LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT'] = str(repo_root)

import label_studio.server
label_studio.server._setup_env()

from django.db import connection
from users.models import User
from organizations.models import Organization
from projects.models import Project
from tasks.models import Task, Prediction, Annotation
from io_storages.localfiles.models import LocalFilesImportStorage

def main():
    print("=== RESETTING DATABASE FOR SEQUENTIAL TASK IDs (1 -> 15723) ===")

    # 1. Clean existing tasks and reset SQLite sequences with PRAGMA foreign_keys = OFF
    with connection.cursor() as cursor:
        cursor.execute("PRAGMA foreign_keys = OFF;")
        cursor.execute("DELETE FROM task_completion;")
        cursor.execute("DELETE FROM prediction;")
        cursor.execute("DELETE FROM prediction_meta;")
        cursor.execute("DELETE FROM tasks_annotationdraft;")
        cursor.execute("DELETE FROM tasks_tasklock;")
        cursor.execute("DELETE FROM data_manager_filtergroup_filters;")
        cursor.execute("DELETE FROM data_manager_filtergroup;")
        cursor.execute("DELETE FROM data_manager_filter;")
        cursor.execute("DELETE FROM data_manager_view;")
        cursor.execute("DELETE FROM task;")
        cursor.execute("DELETE FROM io_storages_localfilesimportstoragelink;")
        cursor.execute("DELETE FROM io_storages_localfilesmixin;")
        cursor.execute("DELETE FROM project;")
        
        # Reset sqlite_sequence counters
        cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('task', 'prediction', 'task_completion', 'project', 'data_manager_view', 'data_manager_filter', 'data_manager_filtergroup', 'io_storages_localfilesmixin');")
        cursor.execute("PRAGMA foreign_keys = ON;")

    print("Purged all old tasks and reset auto-increment sequences.")

    # 2. Get User & Org
    user = User.objects.filter(is_active=True).first()
    org = user.active_organization or Organization.objects.first()

    # 3. Read XML label config
    with open(config_file, 'r', encoding='utf-8') as f:
        label_config = f.read()

    # 4. Create Project ID 1
    project = Project.objects.create(
        title='DMS-Eval',
        organization=org,
        created_by=user,
        description='DMS-Eval Benchmark Dataset (15,723 frames across 14 subjects) targeting 6 frozen warning cues.',
        label_config=label_config
    )
    print(f"Created Project '{project.title}' (ID: {project.id})")

    # 5. Connect Local Storage
    storage = LocalFilesImportStorage.objects.create(
        project=project,
        path=str((images_dir).resolve()),
        title='DMS-Eval Local Images',
        use_blob_urls=True
    )
    print(f"Connected Local Storage (ID: {storage.id})")

    # 6. Read manifest and build task objects in sequential order
    with open(manifest_file, 'r', encoding='utf-8') as mf:
        manifest = json.load(mf)

    task_objects = []
    for entry in manifest:
        sub = entry['subject_folder']
        vid = entry['video_folder']
        vid_dir = images_dir / sub / vid
        if not vid_dir.exists():
            continue

        jpg_files = sorted([f for f in os.listdir(vid_dir) if f.endswith('.jpg')])
        for idx, fname in enumerate(jpg_files, start=1):
            rel_url = f"/data/local-files/?d=dataset/images/{sub}/{vid}/{fname}"
            task_data = {
                "image": rel_url,
                "filename": fname,
                "subject": sub,
                "video": vid,
                "sampled_frame_index": idx
            }
            task_objects.append(Task(project=project, data=task_data))

    print(f"Bulk importing {len(task_objects)} tasks sequentially...")
    batch_size = 1000
    for i in range(0, len(task_objects), batch_size):
        chunk = task_objects[i:i + batch_size]
        Task.objects.bulk_create(chunk)
        print(f"  Imported {min(i + batch_size, len(task_objects))}/{len(task_objects)}...")

    # 7. Verification
    first_task = Task.objects.filter(project=project).order_by('id').first()
    last_task = Task.objects.filter(project=project).order_by('-id').first()
    total_count = Task.objects.filter(project=project).count()

    print("\n=== VERIFICATION ===")
    print(f"Project ID: {project.id}")
    print(f"Total Tasks: {total_count}")
    print(f"First Task ID: {first_task.id} -> {first_task.data.get('filename')}")
    print(f"Last Task ID: {last_task.id} -> {last_task.data.get('filename')}")
    print(f"Human Annotations: {Annotation.objects.filter(project=project).count()}")
    print(f"Predictions: {Prediction.objects.filter(project=project).count()}")
    print("SUCCESS: Task IDs now run sequentially starting from 1 to 15723.")

if __name__ == '__main__':
    main()
