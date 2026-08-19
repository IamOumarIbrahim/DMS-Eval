"""
DMS-Eval Label Studio Checkpoint & Backup Exporter (REST API)
============================================================
Exports recoverable Label Studio project state, task metadata, annotations,
predictions, decision log, and progress ledger into `archive/label-studio-backups/`
using official REST API endpoints with Token authentication.
"""

import os
import sys
import json
import pathlib
import datetime
import argparse
import requests

repo_root = pathlib.Path(__file__).resolve().parents[2]
env_file = repo_root / 'tools' / 'label-studio' / '.env'
backup_dir = repo_root / 'archive' / 'label-studio-backups'
ledger_file = repo_root / 'tools' / 'label-studio' / 'annotation_progress_ledger.json'
decision_log_file = repo_root / 'tools' / 'label-studio' / 'annotation_decision_log.json'

api_key = ''
url = 'http://127.0.0.1:8080'
if env_file.exists():
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

def export_checkpoint(project_id: int = 1):
    """
    Exports a checkpoint for the specified Label Studio project.
    By default, project_id=1 corresponding to the canonical DMS-Eval project.
    """
    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"label_studio_checkpoint_proj{project_id}_{timestamp}.json"

    # Fetch project metadata via REST API
    r_proj = requests.get(f'{url}/api/projects/{project_id}', headers=headers)
    if r_proj.status_code != 200:
        print(f"Failed to fetch Project {project_id}: {r_proj.status_code} {r_proj.text}")
        return None
    proj_meta = r_proj.json()

    # Fetch project tasks via REST API (exported snapshot)
    r_tasks = requests.get(f'{url}/api/tasks?project={project_id}&page_size=100000', headers=headers)
    tasks_data = r_tasks.json().get('tasks', []) if r_tasks.status_code == 200 else []

    # Read ledger and decision log if present
    ledger = {}
    if ledger_file.exists():
        with open(ledger_file, 'r', encoding='utf-8') as lf:
            ledger = json.load(lf)

    decision_log = {}
    if decision_log_file.exists():
        with open(decision_log_file, 'r', encoding='utf-8') as df:
            decision_log = json.load(df)

    checkpoint_payload = {
        "timestamp": timestamp,
        "project": proj_meta,
        "task_count": len(tasks_data),
        "tasks": tasks_data,
        "ledger": ledger,
        "decision_log": decision_log
    }

    with open(backup_path, 'w', encoding='utf-8') as bf:
        json.dump(checkpoint_payload, bf, indent=2)

    print(f"Checkpoint for Project {project_id} successfully exported via REST API to {backup_path}")
    return backup_path

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Export Label Studio Checkpoint & Backup")
    parser.add_argument(
        "--project-id",
        type=int,
        default=int(os.environ.get("LABEL_STUDIO_PROJECT_ID", "1")),
        help="Label Studio project ID to back up (default: 1)"
    )
    args = parser.parse_args()
    export_checkpoint(project_id=args.project_id)
