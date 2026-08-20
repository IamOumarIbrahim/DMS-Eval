"""CUDA-event model-only profiling shared by every detector adapter."""

from __future__ import annotations

import platform
import sys
from pathlib import Path
from typing import Any

import numpy as np
import torch

from .adapters.base import DetectorAdapter
from .protocol import ProtocolError


def environment_metadata() -> dict[str, Any]:
    metadata: dict[str, Any] = {
        "platform": platform.platform(),
        "python": sys.version.split()[0],
        "torch": torch.__version__,
        "cuda_runtime": torch.version.cuda,
        "cudnn": torch.backends.cudnn.version(),
        "cuda_available": torch.cuda.is_available(),
    }
    if torch.cuda.is_available():
        properties = torch.cuda.get_device_properties(0)
        metadata["gpu"] = properties.name
        metadata["gpu_total_bytes"] = properties.total_memory
        metadata["compute_capability"] = f"{properties.major}.{properties.minor}"
    return metadata


class CudaForwardProfiler:
    """Collect per-frame CUDA events around only ``adapter.raw_forward``."""

    def __init__(self, adapter: DetectorAdapter, warmups: int = 10) -> None:
        if adapter.device.type != "cuda" or not torch.cuda.is_available():
            raise ProtocolError("The frozen profiler requires a CUDA device")
        self.adapter = adapter
        self.warmups = warmups
        self.events: list[tuple[torch.cuda.Event, torch.cuda.Event]] = []

    @torch.inference_mode()
    def prepare(self, sample: torch.Tensor) -> None:
        if sample.shape != (1, 3, 640, 640) or sample.dtype != torch.float16 or sample.device.type != "cuda":
            raise ProtocolError("Profiler input must be CUDA FP16 with shape 1x3x640x640")
        for _ in range(self.warmups):
            self.adapter.raw_forward(sample)
        torch.cuda.synchronize(self.adapter.device)
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats(self.adapter.device)

    @torch.inference_mode()
    def forward(self, sample: torch.Tensor) -> Any:
        start = torch.cuda.Event(enable_timing=True)
        end = torch.cuda.Event(enable_timing=True)
        start.record()
        outputs = self.adapter.raw_forward(sample)
        end.record()
        self.events.append((start, end))
        return outputs

    def finish(self) -> dict[str, Any]:
        if not self.events:
            raise ProtocolError("No timed forward passes were recorded")
        torch.cuda.synchronize(self.adapter.device)
        latencies = np.asarray([start.elapsed_time(end) for start, end in self.events], dtype=np.float64)
        total_ms = float(latencies.sum())
        return {
            "batch_size": 1,
            "precision": "fp16",
            "precision_mode": getattr(self.adapter, "precision_mode", "fp16"),
            "input_shape": [1, 3, 640, 640],
            "warmup_passes": self.warmups,
            "timed_frames": int(latencies.size),
            "p50_ms": float(np.percentile(latencies, 50)),
            "p95_ms": float(np.percentile(latencies, 95)),
            "p99_ms": float(np.percentile(latencies, 99)),
            "total_gpu_forward_ms": total_ms,
            "sustained_fps": float(latencies.size / (total_ms / 1000.0)),
            "peak_allocated_vram_bytes": int(torch.cuda.max_memory_allocated(self.adapter.device)),
            "timing": "synchronized_cuda_events",
            "boundary": "model_forward_only",
            "environment": environment_metadata(),
        }


@torch.inference_mode()
def model_flops(adapter: DetectorAdapter, sample: torch.Tensor | None = None) -> int:
    from thop import profile

    class _ProfileBoundary(torch.nn.Module):
        def __init__(self, detector: DetectorAdapter) -> None:
            super().__init__()
            self.model = detector.model
            object.__setattr__(self, "_detector", detector)

        def forward(self, value):
            return self._detector.raw_forward(value)

    sample = sample if sample is not None else adapter.synthetic_input()
    macs, _ = profile(_ProfileBoundary(adapter), inputs=(sample,), verbose=False)
    return int(2 * macs)


@torch.inference_mode()
def synthetic_profile(adapter: DetectorAdapter, repeats: int = 100, warmups: int = 10) -> dict[str, Any]:
    sample = adapter.synthetic_input()
    profiler = CudaForwardProfiler(adapter, warmups=warmups)
    profiler.prepare(sample)
    for _ in range(repeats):
        profiler.forward(sample)
    report = profiler.finish()
    report.update({"model_id": adapter.model_id, "input_source": "synthetic", "parameters": adapter.parameter_count(), "checkpoint_bytes": adapter.checkpoint.stat().st_size})
    report["flops"] = model_flops(adapter, sample)
    report["flop_method"] = "THOP MACs * 2"
    return report
