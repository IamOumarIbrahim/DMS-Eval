"""Verify pinned backends, official weights, and synthetic adapter inference."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.adapters import create_adapter
from core.protocol import load_backends, resolve_repo_path
from scripts.setup_backends import ensure_dfine, ensure_weight


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--synthetic", action="store_true", help="Run one FP16 1x3x640x640 forward per adapter")
    parser.add_argument("--device", default="cuda:0")
    args = parser.parse_args()
    specs = load_backends()
    report = {"dfine_checkout": ensure_dfine(False), "models": {}}
    models = {
        **specs["ultralytics"]["models"],
        "dfine_n": specs["dfine"]["weight"],
    }
    for model_id, spec in models.items():
        weight = ensure_weight(spec, False)
        entry = {"weight": weight, "synthetic": "not requested"}
        if args.synthetic:
            adapter = create_adapter(model_id, resolve_repo_path(spec["file"]), args.device, allow_pretrained_head_mismatch=True).load()
            sample = adapter.synthetic_input()
            with torch.inference_mode():
                raw = adapter.raw_forward(sample)
                predictions = adapter.normalize(raw, [1])
            entry.update({"synthetic": "passed", "parameters": adapter.parameter_count(), "normalized_predictions": len(predictions), "dtype": str(sample.dtype), "shape": list(sample.shape)})
            del adapter, sample, raw
            torch.cuda.empty_cache()
        report["models"][model_id] = entry
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
