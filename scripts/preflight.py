"""Run the safe repository, environment, backend, and dataset preflight."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.dataset_validation import validate_dataset
from core.protocol import validate_protocol
from core.protocol import load_backends
from scripts.setup_backends import ensure_dfine, ensure_weight
from scripts.validate_environment import environment_report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metadata-only", action="store_true", help="Skip full image decode and hashes")
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    failures = []
    try:
        validate_protocol()
        protocol_ok = True
    except Exception as exc:
        protocol_ok = False
        failures.append(f"protocol: {exc}")
    environment = environment_report()
    failures.extend(f"environment: {failure}" for failure in environment["failures"])
    try:
        backend_specs = load_backends()
        backend = {
            "dfine_checkout": ensure_dfine(False),
            "weights": {
                **{model_id: ensure_weight(spec, False) for model_id, spec in backend_specs["ultralytics"]["models"].items()},
                "dfine_n": ensure_weight(backend_specs["dfine"]["weight"], False),
            },
        }
    except Exception as exc:
        backend = {"error": str(exc)}
        failures.append(f"backend: {exc}")
    dataset = validate_dataset(full_image_scan=not args.metadata_only, workers=args.workers)
    failures.extend(f"dataset: {failure}" for failure in dataset.failures)
    report = {"ok": not failures, "protocol": protocol_ok, "environment": environment, "backend": backend, "dataset": dataset.as_dict(), "failures": failures}
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
