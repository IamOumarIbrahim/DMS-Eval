"""Frozen Windows/RTX 4060 environment validation used by every protected test."""

from __future__ import annotations

import platform
import shutil
import subprocess
import sys
from importlib.metadata import PackageNotFoundError, version
from typing import Any

import torch

from .protocol import ProtocolError, REPO_ROOT


EXPECTED_PACKAGES = {
    "torch": "2.4.1+cu121",
    "torchvision": "0.19.1+cu121",
    "ultralytics": "8.4.123",
    "ultralytics-thop": "2.1.6",
    "numpy": "2.5.2",
    "opencv-python": "5.0.0.93",
    "Pillow": "12.3.0",
    "PyYAML": "6.0.3",
    "pycocotools": "2.0.11",
    "faster-coco-eval": "1.7.2",
}


def environment_report() -> dict[str, Any]:
    packages: dict[str, str | None] = {}
    failures: list[str] = []
    for package, expected in EXPECTED_PACKAGES.items():
        try:
            actual = version(package)
        except PackageNotFoundError:
            actual = None
        packages[package] = actual
        if actual != expected:
            failures.append(f"{package}: expected {expected}, got {actual}")
    cuda_available = torch.cuda.is_available()
    gpu = torch.cuda.get_device_name(0) if cuda_available else None
    total_vram = torch.cuda.get_device_properties(0).total_memory if cuda_available else 0
    if not cuda_available:
        failures.append("PyTorch CUDA is unavailable")
    elif "RTX 4060" not in gpu:
        failures.append(f"Expected RTX 4060, got {gpu}")
    if total_vram < 7_500_000_000:
        failures.append(f"Expected approximately 8GB VRAM, got {total_vram} bytes")
    fp16_ok = False
    if cuda_available:
        try:
            fp16_ok = (torch.ones(1, device="cuda", dtype=torch.float16) * 2).item() == 2.0
        except Exception:
            fp16_ok = False
    if not fp16_ok:
        failures.append("CUDA FP16 smoke operation failed")
    driver = None
    if platform.system() == "Windows":
        try:
            driver = subprocess.check_output(
                [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    "(Get-CimInstance Win32_VideoController | Where-Object Name -Like '*NVIDIA*' | Select-Object -First 1).DriverVersion",
                ],
                text=True,
                timeout=15,
            ).strip()
        except Exception:
            driver = None
    report: dict[str, Any] = {
        "ok": not failures,
        "failures": failures,
        "os": platform.platform(),
        "python": platform.python_version(),
        "executable": sys.executable,
        "packages": packages,
        "torch_cuda_runtime": torch.version.cuda,
        "cudnn": torch.backends.cudnn.version(),
        "gpu": gpu,
        "gpu_driver": driver,
        "gpu_total_bytes": total_vram,
        "cuda_fp16": fp16_ok,
        "disk_free_bytes": shutil.disk_usage(REPO_ROOT).free,
    }
    if platform.python_version() != "3.12.10":
        report["ok"] = False
        report["failures"].append(f"Expected Python 3.12.10, got {platform.python_version()}")
    return report


def require_benchmark_environment(report: dict[str, Any] | None = None) -> dict[str, Any]:
    report = environment_report() if report is None else report
    if not report.get("ok"):
        failures = report.get("failures") or ["unspecified environment validation failure"]
        raise ProtocolError("Protected test environment rejected: " + "; ".join(map(str, failures)))
    return report
