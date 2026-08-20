"""Frozen-artifact validation and protected single-pass test ledger."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .evaluation import read_prediction_envelope
from .protocol import TRAINING_SEEDS, ProtocolError, canonical_json_sha256, resolve_repo_path, sha256_file, verify_authoritative_fingerprints


MANIFEST_SCHEMA_VERSION = 2
SUITE_SCHEMA_VERSION = 1
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
    training_seed: int,
    selection: str | Path | None = None,
) -> dict[str, Any]:
    if model_id not in FROZEN_MODEL_IDS:
        raise ProtocolError(f"Unknown frozen model: {model_id}")
    if training_seed not in TRAINING_SEEDS:
        raise ProtocolError(f"Frozen training seed must be one of {list(TRAINING_SEEDS)}")
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
    if prediction_envelope.get("training_seed") != training_seed or calibration_data.get("training_seed") != training_seed:
        raise ProtocolError("Training seed differs across frozen artifacts")
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
        "training_seed": training_seed,
        "checkpoint": str(checkpoint_path),
        "checkpoint_sha256": checkpoint_sha,
        "checkpoint_bytes": checkpoint_path.stat().st_size,
        "validation_predictions": str(predictions_path),
        "validation_predictions_sha256": sha256_file(predictions_path),
        "calibration": str(calibration_path),
        "calibration_sha256": sha256_file(calibration_path),
        "threshold": threshold,
        "dataset_fingerprints": fingerprints,
        "test_policy": "single_protected_pass_per_frozen_model_seed_run",
    }
    if selection is not None:
        selection_path = resolve_repo_path(selection)
        with selection_path.open("r", encoding="utf-8") as handle:
            selection_data = json.load(handle)
        selected = selection_data.get("selected", {})
        if (
            selection_data.get("model_id") != model_id
            or selection_data.get("training_seed") != training_seed
            or selected.get("checkpoint_sha256") != checkpoint_sha
        ):
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
    if manifest.get("training_seed") not in TRAINING_SEEDS:
        raise ProtocolError("Frozen manifest has an unknown training seed")
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


def create_frozen_suite(manifest_paths: list[str | Path], output: str | Path) -> dict[str, Any]:
    """Freeze the complete nine-run manifest suite before any protected test access."""

    entries = []
    seen: set[tuple[str, int]] = set()
    for value in manifest_paths:
        path = resolve_repo_path(value)
        manifest = validate_frozen_manifest(path)
        key = (manifest["model_id"], manifest["training_seed"])
        if key in seen:
            raise ProtocolError(f"Duplicate frozen manifest for {key[0]}/seed-{key[1]}")
        seen.add(key)
        entries.append(
            {
                "model_id": key[0],
                "training_seed": key[1],
                "manifest_id": manifest["manifest_id"],
                "path": str(path),
                "sha256": sha256_file(path),
            }
        )
    required = {(model_id, seed) for model_id in FROZEN_MODEL_IDS for seed in TRAINING_SEEDS}
    if seen != required:
        raise ProtocolError(f"Frozen suite requires all nine model-seed manifests; missing {sorted(required - seen)}")
    suite = {
        "schema_version": SUITE_SCHEMA_VERSION,
        "artifact": "frozen_nine_run_evaluation_suite",
        "created_at_utc": utc_now(),
        "test_access_policy": "all_nine_manifests_frozen_before_first_protected_test",
        "manifests": sorted(entries, key=lambda item: (item["model_id"], item["training_seed"])),
    }
    suite["suite_id"] = canonical_json_sha256(suite)
    write_json_atomic(output, suite)
    return suite


def validate_frozen_suite(path: str | Path) -> dict[str, Any]:
    suite_path = resolve_repo_path(path)
    with suite_path.open("r", encoding="utf-8") as handle:
        suite = json.load(handle)
    if suite.get("schema_version") != SUITE_SCHEMA_VERSION or suite.get("artifact") != "frozen_nine_run_evaluation_suite":
        raise ProtocolError("Unsupported frozen evaluation suite")
    suite_without_id = {key: value for key, value in suite.items() if key != "suite_id"}
    if canonical_json_sha256(suite_without_id) != suite.get("suite_id"):
        raise ProtocolError("Frozen evaluation-suite content hash mismatch")
    entries = suite.get("manifests", [])
    if len(entries) != len(FROZEN_MODEL_IDS) * len(TRAINING_SEEDS):
        raise ProtocolError("Frozen evaluation suite does not contain nine manifests")
    seen = set()
    for entry in entries:
        manifest_path = resolve_repo_path(entry.get("path", ""))
        if sha256_file(manifest_path) != entry.get("sha256"):
            raise ProtocolError(f"Frozen suite manifest changed: {manifest_path}")
        manifest = validate_frozen_manifest(manifest_path)
        key = (manifest["model_id"], manifest["training_seed"])
        if key in seen or entry.get("manifest_id") != manifest["manifest_id"] or key != (
            entry.get("model_id"), entry.get("training_seed")
        ):
            raise ProtocolError("Frozen evaluation-suite manifest identity mismatch")
        seen.add(key)
    required = {(model_id, seed) for model_id in FROZEN_MODEL_IDS for seed in TRAINING_SEEDS}
    if seen != required:
        raise ProtocolError("Frozen evaluation suite is incomplete")
    return suite


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

    def _run_sentinel(self, model_id: str, training_seed: int) -> Path:
        return self.path.parent / ".test-ledger-locks" / f"model-{model_id}-seed-{training_seed}.started"

    def refuse_if_seen(self, manifest_id: str, model_id: str | None = None, training_seed: int | None = None) -> None:
        records = self.records()
        if self._sentinel(manifest_id).exists() or any(record.get("manifest_id") == manifest_id for record in records):
            raise ProtocolError(f"Protected test manifest {manifest_id} already has a ledger record")
        if model_id is not None and training_seed is not None and (
            self._run_sentinel(model_id, training_seed).exists()
            or any(record.get("model_id") == model_id and record.get("training_seed") == training_seed for record in records)
        ):
            raise ProtocolError(f"Protected test run {model_id}/seed-{training_seed} already has a ledger record")

    def start(self, manifest: dict[str, Any]) -> dict[str, Any]:
        self.refuse_if_seen(manifest["manifest_id"], manifest["model_id"], manifest["training_seed"])
        self.path.parent.mkdir(parents=True, exist_ok=True)
        sentinel = self._sentinel(manifest["manifest_id"])
        sentinel.parent.mkdir(parents=True, exist_ok=True)
        try:
            with self._run_sentinel(manifest["model_id"], manifest["training_seed"]).open("x", encoding="utf-8") as handle:
                handle.write(utc_now() + "\n")
            with sentinel.open("x", encoding="utf-8") as handle:
                handle.write(utc_now() + "\n")
        except FileExistsError as exc:
            raise ProtocolError(
                f"Protected test for {manifest['model_id']}/seed-{manifest['training_seed']} already started"
            ) from exc
        record = {
            "manifest_id": manifest["manifest_id"],
            "model_id": manifest["model_id"],
            "training_seed": manifest["training_seed"],
            "status": "started",
            "at_utc": utc_now(),
        }
        with self.path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(record, sort_keys=True) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        return record

    def complete(self, manifest: dict[str, Any], result_path: str | Path) -> dict[str, Any]:
        record = {
            "manifest_id": manifest["manifest_id"],
            "model_id": manifest["model_id"],
            "training_seed": manifest["training_seed"],
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
