"""Frozen-artifact validation and protected single-pass test ledger."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .evaluation import read_prediction_envelope
from .protocol import ProtocolError, canonical_json_sha256, resolve_repo_path, sha256_file, verify_authoritative_fingerprints


MANIFEST_SCHEMA_VERSION = 1
FROZEN_MODEL_IDS = {"yolo11n", "yolo26n", "dfine_n"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json_atomic(path: str | Path, value: Any) -> Path:
    destination = resolve_repo_path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + f".{os.getpid()}.tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(temporary, destination)
    return destination


def create_frozen_manifest(
    model_id: str,
    checkpoint: str | Path,
    validation_predictions: str | Path,
    calibration: str | Path,
    output: str | Path,
    selection: str | Path | None = None,
) -> dict[str, Any]:
    if model_id not in FROZEN_MODEL_IDS:
        raise ProtocolError(f"Unknown frozen model: {model_id}")
    checkpoint_path = resolve_repo_path(checkpoint)
    predictions_path = resolve_repo_path(validation_predictions)
    calibration_path = resolve_repo_path(calibration)
    if not checkpoint_path.is_file():
        raise ProtocolError(f"Selected checkpoint does not exist: {checkpoint_path}")
    prediction_envelope = read_prediction_envelope(predictions_path, required_split="val")
    with calibration_path.open("r", encoding="utf-8") as handle:
        calibration_data = json.load(handle)
    checkpoint_sha = sha256_file(checkpoint_path)
    if prediction_envelope.get("model_id") != model_id or calibration_data.get("model_id") != model_id:
        raise ProtocolError("Model identity differs across frozen artifacts")
    for artifact, name in ((prediction_envelope, "validation predictions"), (calibration_data, "calibration")):
        if artifact.get("checkpoint_sha256") != checkpoint_sha:
            raise ProtocolError(f"Checkpoint checksum differs in {name}")
    if calibration_data.get("artifact") != "validation_threshold_calibration":
        raise ProtocolError("Calibration artifact type is invalid")
    if resolve_repo_path(calibration_data.get("validation_predictions", "")) != predictions_path:
        raise ProtocolError("Calibration did not use the selected validation predictions")
    if calibration_data.get("validation_predictions_sha256") != sha256_file(predictions_path):
        raise ProtocolError("Calibration validation-prediction checksum differs")
    threshold = calibration_data.get("selected", {}).get("threshold")
    if threshold not in {index / 100.0 for index in range(1, 100)}:
        raise ProtocolError("Calibrated threshold is outside the frozen grid")
    fingerprints = verify_authoritative_fingerprints()
    if prediction_envelope.get("dataset_fingerprints") != fingerprints:
        raise ProtocolError("Validation predictions use different dataset fingerprints")
    manifest = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "created_at_utc": utc_now(),
        "model_id": model_id,
        "checkpoint": str(checkpoint_path),
        "checkpoint_sha256": checkpoint_sha,
        "checkpoint_bytes": checkpoint_path.stat().st_size,
        "validation_predictions": str(predictions_path),
        "validation_predictions_sha256": sha256_file(predictions_path),
        "calibration": str(calibration_path),
        "calibration_sha256": sha256_file(calibration_path),
        "threshold": threshold,
        "dataset_fingerprints": fingerprints,
        "test_policy": "single_protected_pass",
    }
    if selection is not None:
        selection_path = resolve_repo_path(selection)
        with selection_path.open("r", encoding="utf-8") as handle:
            selection_data = json.load(handle)
        selected = selection_data.get("selected", {})
        if selection_data.get("model_id") != model_id or selected.get("checkpoint_sha256") != checkpoint_sha:
            raise ProtocolError("Checkpoint selection does not identify the frozen checkpoint")
        if resolve_repo_path(selected.get("validation_predictions", "")) != predictions_path:
            raise ProtocolError("Checkpoint selection and calibration use different validation predictions")
        manifest["checkpoint_selection"] = str(selection_path)
        manifest["checkpoint_selection_sha256"] = sha256_file(selection_path)
    manifest["manifest_id"] = canonical_json_sha256(manifest)
    write_json_atomic(output, manifest)
    return manifest


def validate_frozen_manifest(path: str | Path) -> dict[str, Any]:
    manifest_path = resolve_repo_path(path)
    with manifest_path.open("r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    if manifest.get("schema_version") != MANIFEST_SCHEMA_VERSION:
        raise ProtocolError("Unsupported frozen evaluation manifest")
    if manifest.get("model_id") not in FROZEN_MODEL_IDS:
        raise ProtocolError("Frozen manifest has an unknown model")
    if sha256_file(manifest["checkpoint"]) != manifest.get("checkpoint_sha256"):
        raise ProtocolError("Frozen checkpoint checksum changed")
    if sha256_file(manifest["validation_predictions"]) != manifest.get("validation_predictions_sha256"):
        raise ProtocolError("Frozen validation prediction artifact changed")
    if sha256_file(manifest["calibration"]) != manifest.get("calibration_sha256"):
        raise ProtocolError("Frozen calibration artifact changed")
    if manifest.get("checkpoint_selection") and sha256_file(manifest["checkpoint_selection"]) != manifest.get("checkpoint_selection_sha256"):
        raise ProtocolError("Frozen checkpoint-selection artifact changed")
    if verify_authoritative_fingerprints() != manifest.get("dataset_fingerprints"):
        raise ProtocolError("Frozen dataset or split fingerprint changed")
    manifest_without_id = {key: value for key, value in manifest.items() if key != "manifest_id"}
    if canonical_json_sha256(manifest_without_id) != manifest.get("manifest_id"):
        raise ProtocolError("Frozen manifest content hash mismatch")
    return manifest


class TestRunLedger:
    """Append-only JSONL ledger; a started manifest cannot be started again."""

    def __init__(self, path: str | Path = "runs/test-ledger.jsonl") -> None:
        self.path = resolve_repo_path(path)

    def records(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        records = []
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    records.append(json.loads(line))
        return records

    def _sentinel(self, manifest_id: str) -> Path:
        return self.path.parent / ".test-ledger-locks" / f"{manifest_id}.started"

    def _model_sentinel(self, model_id: str) -> Path:
        return self.path.parent / ".test-ledger-locks" / f"model-{model_id}.started"

    def refuse_if_seen(self, manifest_id: str, model_id: str | None = None) -> None:
        records = self.records()
        if self._sentinel(manifest_id).exists() or any(record.get("manifest_id") == manifest_id for record in records):
            raise ProtocolError(f"Protected test manifest {manifest_id} already has a ledger record")
        if model_id is not None and (
            self._model_sentinel(model_id).exists() or any(record.get("model_id") == model_id for record in records)
        ):
            raise ProtocolError(f"Protected test model {model_id} already has a ledger record")

    def start(self, manifest: dict[str, Any]) -> dict[str, Any]:
        self.refuse_if_seen(manifest["manifest_id"], manifest["model_id"])
        self.path.parent.mkdir(parents=True, exist_ok=True)
        sentinel = self._sentinel(manifest["manifest_id"])
        sentinel.parent.mkdir(parents=True, exist_ok=True)
        try:
            with self._model_sentinel(manifest["model_id"]).open("x", encoding="utf-8") as handle:
                handle.write(utc_now() + "\n")
            with sentinel.open("x", encoding="utf-8") as handle:
                handle.write(utc_now() + "\n")
        except FileExistsError as exc:
            raise ProtocolError(f"Protected test for model {manifest['model_id']} already started") from exc
        record = {"manifest_id": manifest["manifest_id"], "model_id": manifest["model_id"], "status": "started", "at_utc": utc_now()}
        with self.path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(record, sort_keys=True) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        return record

    def complete(self, manifest: dict[str, Any], result_path: str | Path) -> dict[str, Any]:
        record = {
            "manifest_id": manifest["manifest_id"],
            "model_id": manifest["model_id"],
            "status": "completed",
            "result": str(resolve_repo_path(result_path)),
            "result_sha256": sha256_file(result_path),
            "at_utc": utc_now(),
        }
        with self.path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(record, sort_keys=True) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        return record
