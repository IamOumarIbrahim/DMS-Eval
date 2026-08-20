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
TRAINING_SEEDS = (13, 37, 73)
ALLOWED_RECIPE_ADAPTATIONS = [
    "dataset_and_classes",
    "input_size_640x640",
    "physical_batch_size_8",
    "gradient_accumulation_steps_4",
    "epochs_220",
    "training_seeds_13_37_73",
    "early_stopping_disabled",
]


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
    if protocol["dataset"]["ordering"].get("train_seed") != 13:
        raise ProtocolError("Frozen dataset-ordering seed must be 13")
    classes = {int(k): v for k, v in protocol["dataset"]["classes"].items()}
    if classes != {1: "yawning", 2: "hand_over_mouth", 3: "drinking", 4: "phone_use"}:
        raise ProtocolError("Frozen ontology mismatch")
    training = protocol["training"]
    if (training["epochs"], training["physical_batch_size"], training["gradient_accumulation_steps"]) != (220, 8, 4):
        raise ProtocolError("Frozen shared training budget must be 220 epochs, physical batch 8, accumulation 4")
    if training["physical_batch_size"] * training["gradient_accumulation_steps"] != training["effective_batch_size"]:
        raise ProtocolError("Physical batch and accumulation do not equal effective batch")
    if training["early_stopping"] is not False:
        raise ProtocolError("Frozen early-stopping policy must be disabled")
    if training.get("runs_per_model") != len(TRAINING_SEEDS) or tuple(training.get("run_seeds", ())) != TRAINING_SEEDS:
        raise ProtocolError("Every model must use the three frozen training seeds 13, 37, and 73")
    if training.get("run_selection") != "none":
        raise ProtocolError("Run selection is prohibited; all frozen seeds must be reported")
    if training.get("result_aggregation") != "mean_and_sample_standard_deviation":
        raise ProtocolError("Multi-run results must use mean and sample standard deviation")
    if training["recipe_policy"]["allowed_adaptations"] != ALLOWED_RECIPE_ADAPTATIONS:
        raise ProtocolError("Recipe adaptations must equal the frozen seven-item closed list")
    if training["recipe_policy"]["model_specific_tuning_trials"] != 0:
        raise ProtocolError("Model-specific tuning is not permitted")
    if training["incomplete_batch"] != {"drop_last": False, "normalize_partial_accumulation_window": True}:
        raise ProtocolError("Every training image must be retained with normalized partial accumulation")
    if training["validation_intervention"] != "checkpoint_retention_only":
        raise ProtocolError("Validation may select retained checkpoints but may not alter training state")
    profiling = protocol["profiling"]
    if (profiling["precision"], profiling["model_weights"], profiling["input_dtype"]) != ("cuda_amp_fp16", "fp32", "fp32"):
        raise ProtocolError("Inference must use FP32 model/input storage under shared CUDA AMP FP16")
    if profiling["boundaries"] != ["model_forward", "tensor_to_final_detections"]:
        raise ProtocolError("Both frozen timing boundaries must be reported")
    threshold = protocol["evaluation"]["threshold"]
    if (threshold["start"], threshold["stop"], threshold["step"]) != (0.01, 0.99, 0.01):
        raise ProtocolError("Frozen threshold grid mismatch")
    if protocol["evaluation"].get("test_policy") != "single_protected_pass_per_frozen_model_seed_run":
        raise ProtocolError("Protected test policy drift")
    if protocol["evaluation"].get("suite_freeze_policy") != "all_nine_manifests_frozen_before_first_protected_test":
        raise ProtocolError("All nine manifests must be frozen before first protected test access")
    qualitative = protocol["evaluation"].get("qualitative_error_analysis", {})
    if qualitative != {
        "enabled": True,
        "generated_during_protected_pass": True,
        "examples_per_category": 3,
        "publication_reference_seed": 13,
        "categories": [
            "correct_detection",
            "false_positive_negative_frame",
            "false_negative",
            "class_confusion",
            "localization_error",
        ],
        "selection": "deterministic_predeclared_category_ranking",
    }:
        raise ProtocolError("Qualitative/error-analysis pre-registration drift")
    verify_authoritative_fingerprints(protocol)
    return protocol
