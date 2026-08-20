"""Run one guarded optimizer-update smoke test per frozen training backend.

The smoke test uses only the training split, preserves the exact batch/AMP/
accumulation settings, and never writes a benchmark checkpoint or accesses the
validation or test annotations for model selection.
"""

from __future__ import annotations

import argparse
import gc
import json
import sys
from itertools import islice
from pathlib import Path
from typing import Any, Iterable

import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from core.isolation import write_json_atomic
from core.protocol import ProtocolError, REPO_ROOT, load_backends, load_protocol, resolve_repo_path
from core.training import accumulation_loss_scale
from scripts.benchmark.train_yolo import build_plan as build_yolo_plan


MODELS = ("yolo11n", "yolo26n", "dfine_n")


class _SizedDataset:
    def __init__(self, size: int) -> None:
        self.size = size

    def __len__(self) -> int:
        return self.size


class _LimitedLoader:
    """Materialize one complete accumulation window from a real loader."""

    def __init__(self, loader: Iterable, batches: int, batch_size: int) -> None:
        self._batches = list(islice(iter(loader), batches))
        if len(self._batches) != batches:
            raise ProtocolError(f"Training loader yielded only {len(self._batches)} of {batches} smoke batches")
        self.batch_size = batch_size
        self.dataset = _SizedDataset(batches * batch_size)

    def __iter__(self):
        return iter(self._batches)

    def __len__(self) -> int:
        return len(self._batches)


def _cuda_peak_reset() -> None:
    torch.cuda.synchronize(0)
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats(0)


def _trainable_parameter_snapshot(model: torch.nn.Module) -> list[torch.Tensor]:
    return [parameter.detach().cpu().clone() for parameter in model.parameters() if parameter.requires_grad]


def _parameters_changed(model: torch.nn.Module, before: list[torch.Tensor]) -> bool:
    after = [parameter.detach().cpu() for parameter in model.parameters() if parameter.requires_grad]
    return len(after) == len(before) and any(not torch.equal(old, new) for old, new in zip(before, after))


def smoke_yolo(model_id: str, output_root: Path) -> dict[str, Any]:
    from ultralytics.models.yolo.detect import DetectionTrainer
    from ultralytics.utils.torch_utils import autocast

    plan = build_yolo_plan(model_id, 13)
    overrides = {key: value for key, value in plan.items() if key != "model_id"}
    overrides.update(
        {
            "project": str(output_root),
            "name": model_id,
            "exist_ok": False,
            "save": False,
            "plots": False,
        }
    )
    trainer = DetectionTrainer(overrides=overrides)
    trainer._setup_train()
    if trainer.batch_size != 8 or trainer.accumulate != 4 or trainer.epochs != 220:
        raise ProtocolError(f"{model_id} setup changed the frozen training budget")
    if trainer.train_loader.drop_last:
        raise ProtocolError(f"{model_id} smoke loader drops the final training batch")
    if len(trainer.train_loader.dataset) != 9087:
        raise ProtocolError(f"{model_id} smoke loader has an unexpected training-set size")
    if type(trainer.optimizer).__name__ != "MuSGD":
        raise ProtocolError(f"{model_id} optimizer=auto resolved to {type(trainer.optimizer).__name__}, expected MuSGD")

    trainer._model_train()
    trainer.optimizer.zero_grad()
    parameters_before = _trainable_parameter_snapshot(trainer.model)
    initial_scaler_value = float(trainer.scaler.get_scale())
    _cuda_peak_reset()
    losses: list[float] = []
    batches = list(islice(iter(trainer.train_loader), 64))
    if len(batches) != 64:
        raise ProtocolError(f"{model_id} could not provide sixteen accumulation windows")
    optimizer_attempts = 0
    processed_batches = 0
    parameter_update_observed = False
    for index, batch in enumerate(batches):
        with autocast(trainer.amp, device=trainer.device.type):
            batch = trainer.preprocess_batch(batch)
            if int(batch["img"].shape[0]) != 8 or batch["img"].dtype != torch.float32:
                raise ProtocolError(f"{model_id} smoke batch violates batch-8 FP32 input storage")
            loss, _ = trainer.model(batch)
            loss = loss.sum()
        scale = accumulation_loss_scale(
            batch_index=index % 4,
            total_batches=4,
            accumulation_steps=4,
            current_batch_size=8,
            total_samples=32,
            physical_batch_size=8,
            batch_loss_reduction="sum",
        )
        trainer.scaler.scale(loss * scale).backward()
        losses.append(float(loss.detach().cpu()))
        processed_batches += 1
        if processed_batches % 4 == 0:
            optimizer_attempts += 1
            trainer.optimizer_step()
            torch.cuda.synchronize(0)
            if _parameters_changed(trainer.model, parameters_before):
                parameter_update_observed = True
                break
    torch.cuda.synchronize(0)
    final_scaler_value = float(trainer.scaler.get_scale())
    if not parameter_update_observed:
        raise ProtocolError(
            f"{model_id} smoke observed no parameter update across {optimizer_attempts} attempts; "
            f"scaler {initial_scaler_value} -> {final_scaler_value}"
        )
    report = {
        "model_id": model_id,
        "training_split_images": len(trainer.train_loader.dataset),
        "physical_batch_size": trainer.batch_size,
        "gradient_accumulation_steps": trainer.accumulate,
        "epochs_configured": trainer.epochs,
        "drop_last": bool(trainer.train_loader.drop_last),
        "amp": bool(trainer.amp),
        "optimizer": type(trainer.optimizer).__name__,
        "smoke_batches": processed_batches,
        "smoke_samples": processed_batches * 8,
        "optimizer_update_attempts": optimizer_attempts,
        "successful_optimizer_steps": 1,
        "amp_scaler_initial": initial_scaler_value,
        "amp_scaler_final": final_scaler_value,
        "finite_losses": all(torch.isfinite(torch.tensor(losses)).tolist()),
        "peak_allocated_vram_bytes": int(torch.cuda.max_memory_allocated(0)),
    }
    del batches, trainer
    gc.collect()
    torch.cuda.empty_cache()
    return report


def smoke_dfine(output_root: Path) -> dict[str, Any]:
    checkout = REPO_ROOT / "third_party" / "D-FINE"
    if str(checkout) not in sys.path:
        sys.path.insert(0, str(checkout))
    from src.core import YAMLConfig
    from src.solver import TASKS
    from src.solver.det_engine import train_one_epoch

    protocol = load_protocol()
    backend = load_backends()["dfine"]
    config = resolve_repo_path(backend["config"])
    tuning = resolve_repo_path(backend["weight"]["file"])
    cfg = YAMLConfig(
        str(config),
        device="cuda:0",
        seed=13,
        tuning=str(tuning),
        use_amp=True,
        output_dir=str(output_root / "dfine_n"),
        summary_dir=str(output_root / "dfine_n" / "summary"),
    )
    cfg.yaml_cfg["HGNetv2"]["pretrained"] = False
    solver = TASKS[cfg.yaml_cfg["task"]](cfg)
    solver.train()
    loader = solver.train_dataloader
    optimizer = solver.optimizer
    if loader.batch_size != 8 or len(loader.dataset) != 9087 or loader.drop_last:
        raise ProtocolError("D-FINE smoke loader violates the frozen data-retention or batch policy")
    if type(optimizer).__name__ != "AdamW":
        raise ProtocolError(f"D-FINE optimizer resolved to {type(optimizer).__name__}, expected AdamW")
    # D-FINE's initial GradScaler attempts may be skipped on overflow. Eight
    # complete four-batch windows let the real scaler recover without changing
    # its frozen behavior, and the state/parameter checks below require that at
    # least one update actually occurred.
    limited = _LimitedLoader(loader, batches=32, batch_size=8)
    if optimizer.state:
        raise ProtocolError("D-FINE optimizer state is not empty before the smoke update")
    parameters_before = _trainable_parameter_snapshot(solver.model)
    initial_scaler_value = float(solver.scaler.get_scale())
    _cuda_peak_reset()
    stats = train_one_epoch(
        solver.model,
        solver.criterion,
        limited,
        optimizer,
        solver.device,
        epoch=0,
        use_wandb=False,
        max_norm=cfg.clip_max_norm,
        epochs=protocol["training"]["epochs"],
        print_freq=10,
        ema=solver.ema,
        scaler=solver.scaler,
        lr_warmup_scheduler=solver.lr_warmup_scheduler,
        output_dir=None,
        gradient_accumulation_steps=4,
    )
    optimizer_state_steps = {
        int(state["step"].item() if torch.is_tensor(state["step"]) else state["step"])
        for state in optimizer.state.values()
        if "step" in state
    }
    final_scaler_value = float(solver.scaler.get_scale())
    if not optimizer_state_steps or not 1 <= max(optimizer_state_steps) <= 8:
        raise ProtocolError(
            "D-FINE smoke expected at least one successful AdamW update across eight attempts, "
            f"observed {sorted(optimizer_state_steps)}; scaler {initial_scaler_value} -> {final_scaler_value}"
        )
    if not _parameters_changed(solver.model, parameters_before):
        raise ProtocolError("D-FINE smoke did not change any trainable parameter")
    successful_steps = max(optimizer_state_steps)
    torch.cuda.synchronize(0)
    report = {
        "model_id": "dfine_n",
        "training_split_images": len(loader.dataset),
        "physical_batch_size": loader.batch_size,
        "gradient_accumulation_steps": 4,
        "epochs_configured": cfg.epochs,
        "drop_last": bool(loader.drop_last),
        "amp": solver.scaler is not None,
        "optimizer": type(optimizer).__name__,
        "smoke_batches": 32,
        "smoke_samples": 256,
        "optimizer_update_attempts": 8,
        "successful_optimizer_steps": successful_steps,
        "amp_scaler_initial": initial_scaler_value,
        "amp_scaler_final": final_scaler_value,
        "finite_losses": all(torch.isfinite(torch.as_tensor(value)).all().item() for value in stats.values()),
        "peak_allocated_vram_bytes": int(torch.cuda.max_memory_allocated(0)),
    }
    del limited, loader, solver
    gc.collect()
    torch.cuda.empty_cache()
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--models", nargs="+", choices=MODELS, default=list(MODELS))
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--execute-training-smoke", action="store_true")
    args = parser.parse_args()
    if not args.execute_training_smoke:
        raise ProtocolError("Refusing backward/optimizer smoke test without --execute-training-smoke")
    if not torch.cuda.is_available() or "RTX 4060" not in torch.cuda.get_device_name(0):
        raise ProtocolError("Training smoke requires the frozen RTX 4060 CUDA environment")
    output_root = resolve_repo_path(args.output_root)
    report_path = resolve_repo_path(args.report)
    if output_root.exists() or report_path.exists():
        raise ProtocolError("Training-smoke outputs must not already exist")
    output_root.mkdir(parents=True)
    results = []
    for model_id in args.models:
        results.append(smoke_dfine(output_root) if model_id == "dfine_n" else smoke_yolo(model_id, output_root))
    report = {
        "schema_version": 1,
        "artifact": "dms_eval_training_smoke",
        "benchmark_training_started": False,
        "protected_test_accessed": False,
        "optimizer_data_split": "train",
        "optimizer_batches_from_training_split_only": True,
        "validation_loader_initialized": True,
        "validation_inference_performed": False,
        "test_annotations_or_images_accessed": False,
        "models": results,
    }
    write_json_atomic(report_path, report)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ProtocolError, FileNotFoundError, RuntimeError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
