"""Pinned D-FINE-N adapter."""

from __future__ import annotations

import sys
from typing import Any

import numpy as np
import torch
from PIL import Image

from ..protocol import ProtocolError, REPO_ROOT
from .base import DetectorAdapter


class DFineAdapter(DetectorAdapter):
    config_path = REPO_ROOT / "configs" / "dfine" / "dfine_n_dms.yml"
    precision_mode = "cuda_amp_fp16"

    def load(self) -> "DFineAdapter":
        checkout = REPO_ROOT / "third_party" / "D-FINE"
        if not checkout.is_dir():
            raise ProtocolError("Pinned D-FINE checkout is missing; run scripts/benchmark/setup_backends.py")
        if str(checkout) not in sys.path:
            sys.path.insert(0, str(checkout))
        try:
            from src.core import YAMLConfig
        except ImportError as exc:
            raise ProtocolError("D-FINE dependencies are incomplete") from exc

        cfg = YAMLConfig(str(self.config_path))
        cfg.yaml_cfg["HGNetv2"]["pretrained"] = False
        self.model = cfg.model
        checkpoint = torch.load(self.checkpoint, map_location="cpu", weights_only=False)
        state = checkpoint.get("ema", {}).get("module") if isinstance(checkpoint.get("ema"), dict) else checkpoint.get("model")
        if not isinstance(state, dict):
            raise ProtocolError("Unsupported D-FINE checkpoint structure")
        current = self.model.state_dict()
        matched = {key: value for key, value in state.items() if key in current and current[key].shape == value.shape}
        mismatched = sorted(key for key, value in state.items() if key in current and current[key].shape != value.shape)
        missing = sorted(set(current) - set(matched))
        if (mismatched or missing) and not self.allow_pretrained_head_mismatch:
            raise ProtocolError(f"D-FINE checkpoint is not a strict four-class checkpoint: {len(mismatched)} mismatched, {len(missing)} missing")
        self.model.load_state_dict(matched, strict=not self.allow_pretrained_head_mismatch)
        self.postprocessor = cfg.postprocessor.deploy()
        self.model = self.model.deploy().to(self.device).eval()
        self.postprocessor = self.postprocessor.to(self.device).eval()
        self.load_report = {"matched": len(matched), "mismatched": mismatched, "missing": missing}
        return self

    def preprocess(self, image: Image.Image) -> torch.Tensor:
        image = image.convert("RGB").resize(self.input_size, Image.Resampling.BILINEAR)
        array = np.asarray(image, dtype=np.float32).transpose(2, 0, 1) / 255.0
        return torch.from_numpy(array).unsqueeze(0).to(self.device)

    def raw_forward(self, batch: torch.Tensor) -> Any:
        if self.device.type == "cuda":
            with torch.autocast(device_type="cuda", dtype=torch.float16):
                return self.model(batch)
        return self.model(batch.float())

    @torch.inference_mode()
    def normalize(self, raw_outputs: Any, image_ids: list[int]) -> list[dict[str, Any]]:
        sizes = torch.tensor([[640, 640]] * len(image_ids), device=self.device)
        labels, boxes, scores = self.postprocessor(raw_outputs, sizes)
        if len(labels) != len(image_ids):
            raise ProtocolError("Batch size and image ID count differ")
        predictions: list[dict[str, Any]] = []
        for image_id, image_labels, image_boxes, image_scores in zip(image_ids, labels, boxes, scores):
            for label, box, score in zip(image_labels.cpu(), image_boxes.cpu(), image_scores.cpu()):
                category_id = int(label.item()) + 1
                if category_id not in {1, 2, 3, 4}:
                    if self.allow_pretrained_head_mismatch:
                        continue
                    raise ProtocolError(f"Adapter emitted class {category_id} outside frozen ontology")
                x1, y1, x2, y2 = map(float, box.tolist())
                predictions.append({"image_id": int(image_id), "category_id": category_id, "bbox": [x1, y1, x2 - x1, y2 - y1], "score": float(score.item())})
        return predictions

    def parameter_count(self) -> int:
        return sum(parameter.numel() for parameter in self.model.parameters())
