"""Known-answer tests for protected test isolation."""

from __future__ import annotations

import pytest

import core.isolation as isolation
from core.isolation import TestRunLedger as RunLedger
from core.protocol import ProtocolError


def test_test_ledger_refuses_repeated_started_manifest(tmp_path):
    ledger = RunLedger(tmp_path / "ledger.jsonl")
    manifest = {"manifest_id": "frozen-123", "model_id": "yolo11n", "training_seed": 13}
    ledger.start(manifest)
    with pytest.raises(ProtocolError, match="already has a ledger record"):
        ledger.start(manifest)


def test_different_manifest_can_start(tmp_path):
    ledger = RunLedger(tmp_path / "ledger.jsonl")
    ledger.start({"manifest_id": "one", "model_id": "yolo11n", "training_seed": 13})
    ledger.start({"manifest_id": "two", "model_id": "yolo26n", "training_seed": 13})
    assert [record["manifest_id"] for record in ledger.records()] == ["one", "two"]


def test_same_model_seed_cannot_start_with_a_second_manifest(tmp_path):
    ledger = RunLedger(tmp_path / "ledger.jsonl")
    ledger.start({"manifest_id": "one", "model_id": "yolo11n", "training_seed": 13})
    with pytest.raises(ProtocolError, match="yolo11n/seed-13"):
        ledger.start({"manifest_id": "two", "model_id": "yolo11n", "training_seed": 13})


def test_same_model_can_start_each_predeclared_seed_once(tmp_path):
    ledger = RunLedger(tmp_path / "ledger.jsonl")
    for seed in (13, 37, 73):
        ledger.start({"manifest_id": f"run-{seed}", "model_id": "yolo11n", "training_seed": seed})
    assert [record["training_seed"] for record in ledger.records()] == [13, 37, 73]


def test_complete_suite_is_required_before_test_access(tmp_path, monkeypatch):
    manifests = []
    identities = {}
    for model_id in ("yolo11n", "yolo26n", "dfine_n"):
        for seed in (13, 37, 73):
            path = tmp_path / f"{model_id}-{seed}.json"
            path.write_text("{}", encoding="utf-8")
            manifests.append(path)
            identities[str(path.resolve())] = {
                "model_id": model_id,
                "training_seed": seed,
                "manifest_id": f"{model_id}-{seed}",
            }

    monkeypatch.setattr(isolation, "validate_frozen_manifest", lambda path: identities[str(path.resolve())])
    monkeypatch.setattr(isolation, "sha256_file", lambda path: "frozen-sha")
    suite_path = tmp_path / "suite.json"
    suite = isolation.create_frozen_suite(manifests, suite_path)
    assert len(suite["manifests"]) == 9
    assert isolation.validate_frozen_suite(suite_path)["suite_id"] == suite["suite_id"]
    with pytest.raises(ProtocolError, match="all nine"):
        isolation.create_frozen_suite(manifests[:-1], tmp_path / "incomplete.json")
