"""Run the read-only DMS-Eval dataset preflight validator."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.dataset_validation import validate_dataset


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metadata-only", action="store_true", help="Skip file decoding and content hashes")
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    args = parser.parse_args()
    report = validate_dataset(full_image_scan=not args.metadata_only, workers=args.workers)
    if args.json:
        print(json.dumps(report.as_dict(), indent=2, sort_keys=True))
    else:
        print(f"Dataset validation: {'PASSED' if report.ok else 'FAILED'}")
        print(json.dumps(report.summary, indent=2, sort_keys=True))
        for failure in report.failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        print(f"Checks passed: {len(report.checks)}; failures: {len(report.failures)}")
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
