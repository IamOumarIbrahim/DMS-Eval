"""Install/verify pinned model backends and official pretrained weights."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.protocol import ProtocolError, REPO_ROOT, load_backends, resolve_repo_path, sha256_file


def run(command: list[str], cwd: Path = REPO_ROOT) -> None:
    subprocess.run(command, cwd=cwd, check=True)


def ensure_dfine(install: bool) -> dict[str, str]:
    spec = load_backends()["dfine"]
    checkout = resolve_repo_path(spec["checkout"])
    if not checkout.exists():
        if not install:
            raise ProtocolError("Pinned D-FINE checkout is missing")
        run(["git", "clone", "--filter=blob:none", spec["repository"], str(checkout)])
        run(["git", "checkout", "--detach", spec["commit"]], checkout)
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=checkout, text=True).strip()
    if head != spec["commit"]:
        raise ProtocolError(f"D-FINE checkout is {head}, expected {spec['commit']}")
    patch = REPO_ROOT / "patches" / "dfine-gradient-accumulation.patch"
    reverse = subprocess.run(["git", "apply", "--reverse", "--check", str(patch)], cwd=checkout, capture_output=True)
    if reverse.returncode != 0:
        if not install:
            raise ProtocolError("D-FINE gradient-accumulation patch is not applied")
        run(["git", "apply", str(patch)], checkout)
    return {"commit": head, "patch": "applied"}


def ensure_weight(spec: dict, install: bool) -> dict[str, str | int]:
    path = resolve_repo_path(spec["file"])
    if not path.exists():
        if not install:
            raise ProtocolError(f"Missing official weight: {path}")
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".download")
        urllib.request.urlretrieve(spec["url"], temporary)
        temporary.replace(path)
    actual_hash = sha256_file(path)
    if actual_hash != spec["sha256"] or path.stat().st_size != spec["size_bytes"]:
        raise ProtocolError(f"Weight integrity check failed: {path}")
    return {"file": str(path), "size_bytes": path.stat().st_size, "sha256": actual_hash}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--install", action="store_true", help="Download/clone missing official artifacts and apply the pinned patch")
    args = parser.parse_args()
    backends = load_backends()
    report = {"dfine_checkout": ensure_dfine(args.install), "weights": {}}
    for model_id, spec in backends["ultralytics"]["models"].items():
        report["weights"][model_id] = ensure_weight(spec, args.install)
    report["weights"]["dfine_n"] = ensure_weight(backends["dfine"]["weight"], args.install)
    for key, value in report.items():
        print(f"{key}: {value}")
    print("Backend artifact verification PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
