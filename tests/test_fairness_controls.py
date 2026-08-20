"""Regression tests for the fairness controls introduced before training."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import pytest
import torch

from core.adapters.base import DetectorAdapter
from core.environment import require_benchmark_environment
from core.profiling import latency_summary
from core.protocol import ProtocolError, REPO_ROOT
from core.training import accumulation_loss_scale
from scripts.benchmark.setup_backends import _patch_ultralytics_trainer_source, _run_git_patch
from scripts.benchmark.train_dfine import subprocess_environment
from scripts.benchmark import train_yolo


@pytest.mark.parametrize(
    ("batch_index", "total_batches", "current_batch_size", "total_samples", "reduction", "expected"),
    [
        (0, 8, 8, 64, "mean", 1 / 4),
        (3, 8, 8, 64, "sum", 1.0),
        (4, 7, 8, 55, "mean", 8 / 23),
        (6, 7, 7, 55, "mean", 7 / 23),
        (4, 7, 8, 55, "sum", 32 / 23),
        (6, 7, 7, 55, "sum", 32 / 23),
        (0, 1, 7, 7, "sum", 32 / 7),
    ],
)
def test_partial_accumulation_window_scale(batch_index, total_batches, current_batch_size, total_samples, reduction, expected):
    actual = accumulation_loss_scale(
        batch_index=batch_index,
        total_batches=total_batches,
        accumulation_steps=4,
        current_batch_size=current_batch_size,
        total_samples=total_samples,
        physical_batch_size=8,
        batch_loss_reduction=reduction,
    )
    assert actual == pytest.approx(expected)


def test_invalid_accumulation_dimensions_are_rejected():
    with pytest.raises(ValueError):
        accumulation_loss_scale(
            batch_index=1,
            total_batches=1,
            accumulation_steps=4,
            current_batch_size=8,
            total_samples=8,
            physical_batch_size=8,
            batch_loss_reduction="mean",
        )


def test_environment_gate_rejects_failures_and_accepts_verified_report():
    verified = {"ok": True, "failures": [], "gpu": "NVIDIA GeForce RTX 4060"}
    assert require_benchmark_environment(verified) is verified
    with pytest.raises(ProtocolError, match="Protected test environment rejected"):
        require_benchmark_environment({"ok": False, "failures": ["wrong GPU"]})


def test_latency_summary_has_frozen_statistics_and_boundary():
    summary = latency_summary([1.0, 2.0, 3.0], timing="clock", boundary="tensor_to_final_detections")
    assert summary["p50_ms"] == 2.0
    assert summary["timed_frames"] == 3
    assert summary["boundary"] == "tensor_to_final_detections"
    assert summary["sustained_fps"] == pytest.approx(500.0)


class _DummyAdapter(DetectorAdapter):
    def load(self):
        self.model = torch.nn.Sequential(torch.nn.Linear(2, 2), torch.nn.BatchNorm1d(2))
        return self

    def preprocess(self, image):
        raise NotImplementedError

    def raw_forward(self, batch):
        return self.model(batch)

    def normalize(self, raw_outputs: Any, image_ids: list[int]):
        return []

    def parameter_count(self):
        return sum(parameter.numel() for parameter in self.model.parameters())


def test_standardized_artifact_is_inference_only_fp16(tmp_path: Path):
    checkpoint = tmp_path / "source.pt"
    torch.save({"optimizer": {"state": "training-only"}}, checkpoint)
    adapter = _DummyAdapter("dummy", checkpoint, device="cpu").load()
    destination = adapter.export_inference_artifact(tmp_path / "inference.pt")
    artifact = torch.load(destination, map_location="cpu", weights_only=False)
    assert artifact["artifact"] == "standardized_inference_state_dict"
    assert "optimizer" not in artifact
    assert all(not tensor.is_floating_point() or tensor.dtype == torch.float16 for tensor in artifact["state_dict"].values())


def test_ultralytics_patch_is_fixed_and_idempotent():
    source = "\n".join(
        [
            "                    self.accumulate = max(1, int(np.interp(ni, xi, [1, self.args.nbs / self.batch_size]).round()))",
            "                    # Backward",
            "                    self.scaler.scale(self.loss).backward()",
            "                if ni - last_opt_step >= self.accumulate:",
        ]
    )
    patched = _patch_ultralytics_trainer_source(source)
    assert "keep the shared four-step update cadence" in patched
    assert "accumulation_loss_scale" in patched
    assert "(i + 1) % self.accumulate == 0 or (i + 1) == nb" in patched
    assert _patch_ultralytics_trainer_source(patched) == patched


def test_dfine_patch_removes_validation_guided_reload_and_normalizes_loss():
    patch = (REPO_ROOT / "patches" / "dfine-gradient-accumulation.patch").read_text(encoding="utf-8")
    assert '+                self.load_resume_state(str(self.output_dir / "best_stg1.pth"))' not in patch
    assert 'batch_loss_reduction="mean"' in patch
    assert "drop_last: true" not in (REPO_ROOT / "configs" / "dfine" / "dfine_n_dms.yml").read_text(encoding="utf-8")


def test_git_patch_verification_is_independent_of_patch_line_endings(tmp_path: Path):
    source = tmp_path / "sample.txt"
    source.write_text("alpha\n", encoding="utf-8", newline="\n")
    patch = tmp_path / "sample.patch"
    patch.write_bytes(
        b"diff --git a/sample.txt b/sample.txt\r\n"
        b"--- a/sample.txt\r\n"
        b"+++ b/sample.txt\r\n"
        b"@@ -1 +1 @@\r\n"
        b"-alpha\r\n"
        b"+beta\r\n"
    )
    assert _run_git_patch(tmp_path, patch, check_only=True).returncode == 0
    assert _run_git_patch(tmp_path, patch).returncode == 0
    assert source.read_text(encoding="utf-8") == "beta\n"
    assert _run_git_patch(tmp_path, patch, reverse=True, check_only=True).returncode == 0


def test_dfine_subprocess_can_import_shared_training_helper():
    python_path = subprocess_environment()["PYTHONPATH"].split(os.pathsep)
    assert python_path[0] == str(REPO_ROOT)


def test_ultralytics_launcher_disables_environment_mutation():
    assert os.environ["YOLO_AUTOINSTALL"] == "false"
    assert 'os.environ["YOLO_AUTOINSTALL"] = "false"' in Path(train_yolo.__file__).read_text(encoding="utf-8")
