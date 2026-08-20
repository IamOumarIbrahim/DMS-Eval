"""Ultralytics adapter for YOLO11n and YOLO26n."""

from __future__ import annotations

from typing import Any

import numpy as np
import torch
from PIL import Image

from ..protocol import ProtocolError
from .base import DetectorAdapter


class UltralyticsAdapter(DetectorAdapter):
    precision_mode = "fp16_weights"

    def load(self) -> "UltralyticsAdapter":
        try:
            from ultralytics import YOLO
        except ImportError as exc:
            raise ProtocolError("ultralytics is not installed") from exc
        self.wrapper = YOLO(str(self.checkpoint))
        self.model = self.wrapper.model.to(self.device).eval()
        if self.device.type == "cuda":
            self.model.half()
        names = self.wrapper.names
        if len(names) != self.class_count and not self.allow_pretrained_head_mismatch:
            raise ProtocolError(f"{self.model_id} checkpoint has {len(names)} classes, expected 4")
        return self

    def preprocess(self, image: Image.Image) -> torch.Tensor:
        image = image.convert("RGB").resize(self.input_size, Image.Resampling.BILINEAR)
        array = np.asarray(image, dtype=np.float32).transpose(2, 0, 1) / 255.0
        batch = torch.from_numpy(array).unsqueeze(0).to(self.device)
        return batch.half() if self.device.type == "cuda" else batch

    def raw_forward(self, batch: torch.Tensor) -> Any:
        return self.model(batch)

    @torch.inference_mode()
    def normalize(self, raw_outputs: Any, image_ids: list[int]) -> list[dict[str, Any]]:
        from ultralytics.utils.nms import non_max_suppression

        detections = non_max_suppression(raw_outputs, conf_thres=0.001, iou_thres=0.7, nc=len(self.wrapper.names), max_det=300)
        if len(detections) != len(image_ids):
            raise ProtocolError("Batch size and image ID count differ")
        predictions: list[dict[str, Any]] = []
        for image_id, image_detections in zip(image_ids, detections):
            for detection in image_detections.cpu():
                x1, y1, x2, y2, score, class_id = map(float, detection[:6].tolist())
                category_id = int(class_id) + 1
                if category_id not in {1, 2, 3, 4}:
                    if self.allow_pretrained_head_mismatch:
                        continue
                    raise ProtocolError(f"Adapter emitted class {category_id} outside frozen ontology")
                predictions.append({"image_id": int(image_id), "category_id": category_id, "bbox": [x1, y1, x2 - x1, y2 - y1], "score": score})
        return predictions

    def parameter_count(self) -> int:
        return sum(parameter.numel() for parameter in self.model.parameters())
