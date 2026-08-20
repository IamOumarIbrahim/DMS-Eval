"""Run the frozen profiler on synthetic input only (safe setup smoke test)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.adapters import create_adapter
from core.profiling import synthetic_profile
from core.protocol import resolve_repo_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-id", required=True, choices=["yolo11n", "yolo26n", "dfine_n"])
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--repeats", type=int, default=100)
    parser.add_argument("--allow-pretrained-head-mismatch", action="store_true", help="Only for official initialization smoke tests")
    parser.add_argument("--output")
    args = parser.parse_args()
    adapter = create_adapter(args.model_id, resolve_repo_path(args.checkpoint), args.device, args.allow_pretrained_head_mismatch).load()
    result = synthetic_profile(adapter, repeats=args.repeats, warmups=10)
    if args.output:
        from core.isolation import write_json_atomic
        write_json_atomic(args.output, result)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
