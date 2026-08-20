"""Pinned D-FINE-N launcher with accumulation patch and explicit training gate."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from core.protocol import ProtocolError, REPO_ROOT, TRAINING_SEEDS, load_backends, load_protocol, resolve_repo_path
from scripts.benchmark.setup_backends import ensure_dfine, ensure_weight


def subprocess_environment() -> dict[str, str]:
    """Expose the shared benchmark helpers to the pinned D-FINE subprocess."""

    environment = os.environ.copy()
    existing = environment.get("PYTHONPATH")
    environment["PYTHONPATH"] = str(REPO_ROOT) + (os.pathsep + existing if existing else "")
    return environment


def build_plan(seed: int) -> dict:
    protocol = load_protocol()
    backend = load_backends()["dfine"]
    ensure_dfine(False)
    if seed not in TRAINING_SEEDS:
        raise ProtocolError(f"Training seed must be one of {list(TRAINING_SEEDS)}")
    weight = ensure_weight(backend["weight"], False)
    output = REPO_ROOT / "runs" / "train" / f"dfine_n_seed{seed}"
    return {
        "model_id": "dfine_n",
        "upstream_commit": backend["commit"],
        "config": str(resolve_repo_path(backend["config"])),
        "tuning": weight["file"],
        "output_dir": str(output),
        "epochs": protocol["training"]["epochs"],
        "physical_batch_size": protocol["training"]["physical_batch_size"],
        "gradient_accumulation_steps": protocol["training"]["gradient_accumulation_steps"],
        "effective_batch_size": protocol["training"]["effective_batch_size"],
        "seed": seed,
        "amp": True,
        "device": "cuda:0",
        "recipe_policy": protocol["training"]["recipe_policy"]["type"],
        "validation_intervention": protocol["training"]["validation_intervention"],
        "drop_last": protocol["training"]["incomplete_batch"]["drop_last"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", required=True, type=int, choices=TRAINING_SEEDS)
    parser.add_argument("--execute-training", action="store_true", help="Explicitly start the 220-epoch training run")
    args = parser.parse_args()
    plan = build_plan(args.seed)
    print(json.dumps(plan, indent=2))
    if not args.execute_training:
        print("Dry-run only. Training was NOT started; add --execute-training to execute this frozen plan.")
        return 0
    if not torch.cuda.is_available() or "RTX 4060" not in torch.cuda.get_device_name(0):
        raise ProtocolError("Frozen training requires the RTX 4060 CUDA environment")
    output_dir = Path(plan["output_dir"])
    if output_dir.exists():
        raise ProtocolError(f"Refusing to reuse existing run directory: {output_dir}")
    command = [
        sys.executable,
        str(REPO_ROOT / "third_party" / "D-FINE" / "train.py"),
        "--config", plan["config"],
        "--tuning", plan["tuning"],
        "--device", plan["device"],
        "--seed", str(plan["seed"]),
        "--use-amp",
        "--output-dir", plan["output_dir"],
    ]
    subprocess.run(command, cwd=REPO_ROOT, env=subprocess_environment(), check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
