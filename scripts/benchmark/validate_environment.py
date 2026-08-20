"""Validate the frozen Windows/RTX 4060 project environment."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from core.environment import environment_report


def main() -> int:
    argparse.ArgumentParser(description=__doc__).parse_args()
    report = environment_report()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
