"""Load and validate the machine-readable frozen DMS-Eval protocol."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
BENCHMARK_CONFIG = REPO_ROOT / "configs" / "benchmark.yaml"
BACKEND_CONFIG = REPO_ROOT / "configs" / "backends.yaml"


class ProtocolError(RuntimeError):
    """Raised when a frozen protocol invariant is violated."""


def resolve_repo_path(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else REPO_ROOT / path


def load_yaml(path: str | Path) -> dict[str, Any]:
    with resolve_repo_path(path).open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ProtocolError(f"Expected a YAML mapping in {path}")
    return data


def load_protocol() -> dict[str, Any]:
    return load_yaml(BENCHMARK_CONFIG)


def load_backends() -> dict[str, Any]:
    return load_yaml(BACKEND_CONFIG)


def sha256_file(path: str | Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with resolve_repo_path(path).open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json_sha256(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def verify_authoritative_fingerprints(protocol: dict[str, Any] | None = None) -> dict[str, str]:
    protocol = protocol or load_protocol()
    dataset = protocol["dataset"]
    actual = {
        "annotations_sha256": sha256_file(dataset["annotations"]),
        "splits_sha256": sha256_file(dataset["splits"]),
    }
    expected = {key: str(dataset[key]).lower() for key in actual}
    mismatches = [key for key in actual if actual[key] != expected[key]]
    if mismatches:
        details = ", ".join(f"{key}: expected {expected[key]}, got {actual[key]}" for key in mismatches)
        raise ProtocolError(f"Authoritative dataset fingerprint mismatch: {details}")
    return actual


def model_spec(model_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    protocol = load_protocol()
    model = next((item for item in protocol["models"] if item["id"] == model_id), None)
    if model is None:
        raise ProtocolError(f"Unknown frozen model: {model_id}")
    backends = load_backends()
    backend = backends["ultralytics"]["models"][model_id] if model["adapter"] == "ultralytics" else backends["dfine"]
    return model, backend


def validate_protocol() -> dict[str, Any]:
    protocol = load_protocol()
    if protocol["seed"] != 13:
        raise ProtocolError("Frozen seed must be 13")
    classes = {int(k): v for k, v in protocol["dataset"]["classes"].items()}
    if classes != {1: "yawning", 2: "hand_over_mouth", 3: "drinking", 4: "phone_use"}:
        raise ProtocolError("Frozen ontology mismatch")
    training = protocol["training"]
    if training["physical_batch_size"] * training["gradient_accumulation_steps"] != training["effective_batch_size"]:
        raise ProtocolError("Physical batch and accumulation do not equal effective batch")
    threshold = protocol["evaluation"]["threshold"]
    if (threshold["start"], threshold["stop"], threshold["step"]) != (0.01, 0.99, 0.01):
        raise ProtocolError("Frozen threshold grid mismatch")
    verify_authoritative_fingerprints(protocol)
    return protocol
