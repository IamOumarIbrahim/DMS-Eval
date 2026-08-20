"""Frozen detector adapter registry."""

from .base import DetectorAdapter
from .dfine import DFineAdapter
from .ultralytics import UltralyticsAdapter


def create_adapter(model_id: str, checkpoint, device: str = "cuda:0", allow_pretrained_head_mismatch: bool = False) -> DetectorAdapter:
    if model_id in {"yolo11n", "yolo26n"}:
        return UltralyticsAdapter(model_id, checkpoint, device=device, allow_pretrained_head_mismatch=allow_pretrained_head_mismatch)
    if model_id == "dfine_n":
        return DFineAdapter(model_id, checkpoint, device=device, allow_pretrained_head_mismatch=allow_pretrained_head_mismatch)
    raise ValueError(f"Unknown frozen model: {model_id}")


__all__ = ["DetectorAdapter", "DFineAdapter", "UltralyticsAdapter", "create_adapter"]
