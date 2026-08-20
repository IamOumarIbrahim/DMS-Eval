"""Common detector adapter contract."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import torch
from PIL import Image


class DetectorAdapter(ABC):
    class_count = 4
    input_size = (640, 640)

    def __init__(self, model_id: str, checkpoint: str | Path, device: str = "cuda:0", allow_pretrained_head_mismatch: bool = False) -> None:
        self.model_id = model_id
        self.checkpoint = Path(checkpoint).resolve()
        self.device = torch.device(device)
        self.allow_pretrained_head_mismatch = allow_pretrained_head_mismatch
        if not self.checkpoint.is_file():
            raise FileNotFoundError(self.checkpoint)

    @abstractmethod
    def load(self) -> "DetectorAdapter":
        raise NotImplementedError

    @abstractmethod
    def preprocess(self, image: Image.Image) -> torch.Tensor:
        """Decode-independent preprocessing, returning BCHW float data on the adapter device."""
        raise NotImplementedError

    @abstractmethod
    def raw_forward(self, batch: torch.Tensor) -> Any:
        """Model-only forward boundary used by every runtime profile."""
        raise NotImplementedError

    @abstractmethod
    def normalize(self, raw_outputs: Any, image_ids: list[int]) -> list[dict[str, Any]]:
        """Normalize raw outputs to COCO xywh predictions with category IDs 1..4."""
        raise NotImplementedError

    def infer(self, batch: torch.Tensor, image_ids: list[int]) -> list[dict[str, Any]]:
        return self.normalize(self.raw_forward(batch), image_ids)

    @abstractmethod
    def parameter_count(self) -> int:
        raise NotImplementedError

    def synthetic_input(self) -> torch.Tensor:
        dtype = torch.float16 if self.device.type == "cuda" else torch.float32
        return torch.zeros((1, 3, 640, 640), dtype=dtype, device=self.device)
