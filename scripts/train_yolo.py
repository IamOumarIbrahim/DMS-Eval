"""
DMS-Eval YOLO Training Script with Gradient Accumulation
========================================================
Addresses the Batch Normalization instability and gradient noise under physical batch size = 1
by configuring gradient accumulation over 16 to 64 steps (effective batch size 16-64).

Features:
- Configurable gradient accumulation (nbs/accumulate)
- Single-frame 640x640 resolution
- Fixed benchmark seed (13)
- Automatic Mixed Precision (AMP FP16)
- Real-time GPU telemetry (RTX 4060 VRAM, peak memory, loss logging)
- Checkpoint persistence (best.pt and last.pt)
"""

import os
import sys
import argparse
from pathlib import Path
import torch

def parse_args():
    parser = argparse.ArgumentParser(description="DMS-Eval YOLO Training Script")
    parser.add_argument("--model", type=str, default="weights/pretrained/yolo11n.pt", help="Pretrained model weights path or name")
    parser.add_argument("--data", type=str, default=None, help="Path to dataset YAML configuration")
    parser.add_argument("--epochs", type=int, default=220, help="Number of training epochs (use 2 or 3 for mini-epoch sanity check)")
    parser.add_argument("--batch", type=int, default=1, help="Physical mini-batch size (frozen at 1 for benchmark hardware constraints)")
    parser.add_argument("--accumulate", type=int, default=32, help="Gradient accumulation steps (nominal batch size nbs, e.g. 16-64)")
    parser.add_argument("--imgsz", type=int, default=640, help="Input image dimension (frozen at 640x640)")
    parser.add_argument("--workers", type=int, default=4, help="DataLoader workers count")
    parser.add_argument("--seed", type=int, default=13, help="Deterministic benchmark random seed")
    parser.add_argument("--device", type=str, default="0", help="CUDA device index or 'cpu'")
    parser.add_argument("--project", type=str, default=None, help="Destination directory for training runs (defaults to runs/train)")
    parser.add_argument("--name", type=str, default="yolo11n_run", help="Experiment name identifier")
    parser.add_argument("--exist-ok", action="store_true", default=True, help="Allow overwriting existing run directory")
    parser.add_argument("--amp", action="store_true", default=True, help="Enable Automatic Mixed Precision (FP16)")
    return parser.parse_args()

def main():
    args = parse_args()
    repo_root = Path(__file__).resolve().parent.parent

    # Resolve model weights path
    model_path = Path(args.model)
    if not model_path.exists():
        fallback_path = repo_root / "weights" / "pretrained" / model_path.name
        if fallback_path.exists():
            args.model = str(fallback_path)
        else:
            args.model = model_path.name

    # Default data configuration path
    if args.data is None:
        configs = [
            repo_root / "configs" / "yolo" / "dms_eval.yaml",
            repo_root / "dataset" / "yolo" / "dms_eval.yaml",
            repo_root / "dataset" / "dms_eval_yolo.yaml"
        ]
        for cfg in configs:
            if cfg.exists():
                args.data = str(cfg)
                break

    # Destination directory for runs
    if args.project is None:
        args.project = str(repo_root / "runs" / "train")

    print("=" * 70)
    print("DMS-Eval Benchmark YOLO Training Engine")
    print("=" * 70)
    print(f"  Model Architecture     : {args.model}")
    print(f"  Dataset Config         : {args.data}")
    print(f"  Epochs                 : {args.epochs}")
    print(f"  Physical Batch Size    : {args.batch}")
    print(f"  Gradient Accumulation  : {args.accumulate} steps (Effective Batch Size: {args.batch * args.accumulate})")
    print(f"  Input Resolution       : {args.imgsz}x{args.imgsz}")
    print(f"  DataLoader Workers     : {args.workers}")
    print(f"  Random Seed            : {args.seed}")
    print(f"  Automatic Mixed Prec.  : {args.amp}")
    print(f"  Device Request         : {args.device}")

    # CUDA Hardware Telemetry
    if torch.cuda.is_available():
        cuda_device = torch.cuda.current_device() if args.device == "0" else args.device
        gpu_name = torch.cuda.get_device_name(cuda_device)
        total_vram_gb = torch.cuda.get_device_properties(cuda_device).total_memory / (1024 ** 3)
        print(f"  Active GPU Hardware    : {gpu_name} ({total_vram_gb:.2f} GB VRAM)")
        torch.cuda.reset_peak_memory_stats()
    else:
        print("  Active Hardware        : CPU (WARNING: CUDA not detected)")

    print("-" * 70)
    print("Initializing Ultralytics YOLO model...")

    from ultralytics import YOLO

    model = YOLO(args.model)

    # Train model
    print("\nStarting training execution...")
    results = model.train(
        data=args.data,
        epochs=args.epochs,
        batch=args.batch,
        nbs=args.accumulate,       # Nominal batch size configures gradient accumulation: accumulate = round(nbs / batch)
        imgsz=args.imgsz,
        workers=args.workers,
        seed=args.seed,
        device=args.device,
        project=args.project,
        name=args.name,
        exist_ok=args.exist_ok,
        amp=args.amp,
        val=True,
        save=True,
        plots=True,
        verbose=True
    )

    # Post-Training Verification & Telemetry Summary
    print("\n" + "=" * 70)
    print("DMS-Eval Training Execution Summary")
    print("=" * 70)

    if torch.cuda.is_available():
        peak_vram_mb = torch.cuda.max_memory_allocated() / (1024 ** 2)
        reserved_vram_mb = torch.cuda.max_memory_reserved() / (1024 ** 2)
        print(f"  Peak VRAM Allocated    : {peak_vram_mb:.1f} MB ({peak_vram_mb / 1024:.2f} GB)")
        print(f"  Peak VRAM Reserved     : {reserved_vram_mb:.1f} MB ({reserved_vram_mb / 1024:.2f} GB)")

    save_dir = Path(args.project) / args.name
    weights_dir = save_dir / "weights"
    best_pt = weights_dir / "best.pt"
    last_pt = weights_dir / "last.pt"

    print(f"  Run Directory          : {save_dir}")
    print(f"  Weights Directory      : {weights_dir}")
    print(f"  best.pt Exists         : {best_pt.exists()} ({best_pt.stat().st_size / (1024**2):.2f} MB)" if best_pt.exists() else "  best.pt Exists         : False")
    print(f"  last.pt Exists         : {last_pt.exists()} ({last_pt.stat().st_size / (1024**2):.2f} MB)" if last_pt.exists() else "  last.pt Exists         : False")

    if best_pt.exists() or last_pt.exists():
        print("\nCheckpoint verification PASSED: Model weights successfully persisted.")
    else:
        print("\nCheckpoint verification WARNING: Checkpoint file was not located at expected path.")

    return results

if __name__ == "__main__":
    main()
