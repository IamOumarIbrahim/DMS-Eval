"""
DMS-Eval Label Studio Checkpoint & Backup Exporter
==================================================
Exports recoverable Label Studio project state, task metadata, predictions,
review metadata, decision log, and progress ledger into `archive/label-studio-backups/`.
"""

import os
import sys
import json
import pathlib
import datetime

repo_root = pathlib.Path(__file__).resolve().parents[2]
data_dir = repo_root / 'tools' / 'label-studio' / 'data'
backup_dir = repo_root / 'archive' / 'label-studio-backups'
ledger_file = repo_root / 'tools' / 'label-studio' / 'annotation_progress_ledger.json'
decision_log_file = repo_root / 'tools' / 'label-studio' / 'annotation_decision_log.json'

os.environ['LABEL_STUDIO_BASE_DATA_DIR'] = str(data_dir)
os.environ['LABEL_STUDIO_LOCAL_FILES_SERVING_ENABLED'] = 'true'
os.environ['LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT'] = str(repo_root)

import label_studio.server
label_studio.server._setup_env()

from projects.models import Project
from tasks.models import Task, Prediction, Annotation

def export_checkpoint():
    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"label_studio_checkpoint_{timestamp}.json"

    project = Project.objects.filter(title='DMS-Eval').first()
    if not project:
        print("Project DMS-Eval not found.")
        return None

    tasks_data = []
    for task in Task.objects.filter(project=project):
        preds = []
        for p in task.predictions.all():
            preds.append({
                "id": p.id,
                "model_version": p.model_version,
                "result": p.result,
                "created_at": p.created_at.isoformat() if hasattr(p, 'created_at') else None
            })
        
        annots = []
        for a in task.annotations.all():
            annots.append({
                "id": a.id,
                "completed_by": str(a.completed_by),
                "result": a.result,
                "was_cancelled": a.was_cancelled,
                "ground_truth": a.ground_truth
            })

        tasks_data.append({
            "task_id": task.id,
            "data": task.data,
            "predictions": preds,
            "annotations": annots
        })

    # Read ledger
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
        "project": {
            "id": project.id,
            "title": project.title,
            "label_config": project.label_config
        },
        "task_count": len(tasks_data),
        "tasks": tasks_data,
        "ledger_summary": {
            "total_tracked": len(ledger),
            "processed": sum(1 for v in ledger.values() if v.get('processing_status') in ['agent_processed', 'zero_proposals']),
            "secondary_review": sum(1 for v in ledger.values() if v.get('secondary_review_required'))
        },
        "decision_log": decision_log
    }

    with open(backup_path, 'w', encoding='utf-8') as bf:
        json.dump(checkpoint_payload, bf, indent=2)

    print(f"Checkpoint successfully exported to {backup_path}")
    return backup_path

if __name__ == '__main__':
    export_checkpoint()
