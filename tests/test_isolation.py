"""Known-answer tests for protected test isolation."""

from __future__ import annotations

import pytest

from core.isolation import TestRunLedger as RunLedger
from core.protocol import ProtocolError


def test_test_ledger_refuses_repeated_started_manifest(tmp_path):
    ledger = RunLedger(tmp_path / "ledger.jsonl")
    manifest = {"manifest_id": "frozen-123", "model_id": "yolo11n"}
    ledger.start(manifest)
    with pytest.raises(ProtocolError, match="already has a ledger record"):
        ledger.start(manifest)


def test_different_manifest_can_start(tmp_path):
    ledger = RunLedger(tmp_path / "ledger.jsonl")
    ledger.start({"manifest_id": "one", "model_id": "yolo11n"})
    ledger.start({"manifest_id": "two", "model_id": "yolo26n"})
    assert [record["manifest_id"] for record in ledger.records()] == ["one", "two"]


def test_same_model_cannot_start_with_a_second_manifest(tmp_path):
    ledger = RunLedger(tmp_path / "ledger.jsonl")
    ledger.start({"manifest_id": "one", "model_id": "yolo11n"})
    with pytest.raises(ProtocolError, match="model yolo11n"):
        ledger.start({"manifest_id": "two", "model_id": "yolo11n"})
