"""
DMS-Eval Label Studio Project Setup & Dataset Importer
======================================================
Prepares the Label Studio project with the 4 frozen DMS-Eval target warning cues,
connects local storage to `dataset/images/`, and prepares the 15,723 frame dataset.
"""

import os
import sys
import json
import pathlib
import argparse

repo_root = pathlib.Path(__file__).resolve().parents[2]
data_dir = repo_root / 'tools' / 'label-studio' / 'data'
config_file = repo_root / 'tools' / 'label-studio' / 'config' / 'dms_labeling_config.xml'
manifest_file = repo_root / 'dataset' / 'manifest.json'

os.environ['LABEL_STUDIO_BASE_DATA_DIR'] = str(data_dir)
os.environ['LABEL_STUDIO_LOCAL_FILES_SERVING_ENABLED'] = 'true'
os.environ['LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT'] = str(repo_root)

import label_studio.server
label_studio.server._setup_env()

from organizations.models import Organization
from users.models import User
from projects.models import Project
from tasks.models import Task, Annotation
from io_storages.localfiles.models import LocalFilesImportStorage

def get_or_create_user_and_org():
    env_file = repo_root / 'tools' / 'label-studio' / '.env'
    initial_pass = os.environ.get('LABEL_STUDIO_USER_PASSWORD')
    if not initial_pass and env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('LABEL_STUDIO_USER_PASSWORD='):
                    initial_pass = line.strip().split('=', 1)[1]
    if not initial_pass:
        import secrets
        initial_pass = secrets.token_urlsafe(24)

    user = User.objects.filter(is_active=True).first()
    if not user:
        user = User.objects.create_user(email='annotator@dms-eval.local', password=initial_pass)
        org = Organization.create_organization(created_by=user, title='DMS-Eval')
        user.active_organization = org
        user.save()
    else:
        org = user.active_organization or Organization.objects.first()
    return user, org

def setup_project(title="DMS-Eval Benchmark Annotation (15k Frames)"):
    user, org = get_or_create_user_and_org()

    with open(config_file, 'r', encoding='utf-8') as f:
        label_config = f.read()

    project, created = Project.objects.get_or_create(
        title=title,
        organization=org,
        defaults={
            'created_by': user,
            'description': '15,723 frame benchmark annotation across 14 subjects targeting the 4 frozen warning cues.',
            'label_config': label_config
        }
    )
    if not created:
        project.label_config = label_config
        project.save()

    # Configure LocalFilesImportStorage pointing to dataset directory
    dataset_path = str((repo_root / 'dataset').resolve())
    storage, _ = LocalFilesImportStorage.objects.get_or_create(
        project=project,
        path=dataset_path,
        defaults={
            'title': 'DMS-Eval Dataset Directory',
            'use_blob_urls': True
        }
    )

    print(f"Project '{project.title}' (ID: {project.id}) ready.")
    print(f"Storage connected to: {dataset_path}")
    return project

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Setup DMS-Eval Label Studio Project")
    parser.add_argument("--clean", action="store_true", help="Clean existing tasks before setup")
    args = parser.parse_args()

    project = setup_project()
    print("\nReady for 15,000 image dataset labeling!")
