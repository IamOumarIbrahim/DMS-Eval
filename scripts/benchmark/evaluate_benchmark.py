"""Guarded DMS-Eval prediction, calibration, freeze, and test workflow.

Running this script without a subcommand performs only a protocol dry-run.
No subcommand defaults to the test split.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import torch
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from core.adapters import create_adapter
from core.environment import require_benchmark_environment
from core.evaluation import (
    calibrate_threshold,
    coco_metrics,
    load_ground_truth,
    operating_point_metrics,
    read_prediction_envelope,
    select_checkpoint_candidate,
)
from core.isolation import (
    TestRunLedger,
    create_frozen_manifest,
    create_frozen_suite,
    validate_frozen_manifest,
    validate_frozen_suite,
    write_json_atomic,
)
from core.profiling import CudaForwardProfiler, model_flop_estimates
from core.qualitative import QualitativeErrorCollector
from core.protocol import TRAINING_SEEDS, ProtocolError, REPO_ROOT, resolve_repo_path, sha256_file, validate_protocol, verify_authoritative_fingerprints


@torch.inference_mode()
def _predict_split(adapter, ground_truth: dict, profile: bool = False) -> tuple[list[dict], dict | None]:
    predictions: list[dict] = []
    profiler = CudaForwardProfiler(adapter, warmups=10) if profile else None
    if profiler:
        profiler.prepare(adapter.synthetic_input())
    for image in ground_truth["images"]:
        image_path = REPO_ROOT / "dataset" / image["file_name"]
        with Image.open(image_path) as source:
            batch = adapter.preprocess(source)
        raw_outputs = profiler.forward(batch) if profiler else adapter.raw_forward(batch)
        if profiler:
            predictions.extend(profiler.finalize(raw_outputs, [int(image["id"])]))
        else:
            predictions.extend(adapter.normalize(raw_outputs, [int(image["id"])]))
    return predictions, profiler.finish() if profiler else None


def export_validation(args: argparse.Namespace) -> int:
    if not args.execute_validation_export:
        raise ProtocolError("Refusing real validation inference without --execute-validation-export")
    checkpoint = resolve_repo_path(args.checkpoint)
    adapter = create_adapter(args.model_id, checkpoint, args.device).load()
    protocol = validate_protocol()
    ground_truth = load_ground_truth(protocol["dataset"]["annotations"], "val", protocol["dataset"]["splits"])
    predictions, _ = _predict_split(adapter, ground_truth)
    metrics = coco_metrics(ground_truth, predictions)
    envelope = {
        "schema_version": 1,
        "artifact": "validation_predictions",
        "model_id": args.model_id,
        "training_seed": args.seed,
        "checkpoint": str(checkpoint),
        "checkpoint_sha256": sha256_file(checkpoint),
        "checkpoint_epoch": args.epoch,
        "split": "val",
        "dataset_fingerprints": verify_authoritative_fingerprints(),
        "coco_metrics": metrics,
        "predictions": predictions,
    }
    write_json_atomic(args.output, envelope)
    print(json.dumps({key: value for key, value in envelope.items() if key != "predictions"}, indent=2))
    return 0


def select_checkpoint(args: argparse.Namespace) -> int:
    candidates = []
    for path in args.validation_predictions:
        resolved = resolve_repo_path(path)
        envelope = read_prediction_envelope(resolved, required_split="val")
        if envelope.get("model_id") != args.model_id:
            raise ProtocolError(f"Model mismatch in {resolved}")
        if envelope.get("training_seed") != args.seed:
            raise ProtocolError(f"Training-seed mismatch in {resolved}")
        checkpoint = resolve_repo_path(envelope["checkpoint"])
        if sha256_file(checkpoint) != envelope.get("checkpoint_sha256"):
            raise ProtocolError(f"Checkpoint changed for {resolved}")
        metrics = envelope.get("coco_metrics", {})
        if not all(key in metrics for key in ("map_50_95", "map_50")) or not isinstance(envelope.get("checkpoint_epoch"), int):
            raise ProtocolError(f"Incomplete validation metrics in {resolved}")
        candidates.append(
            {
                "checkpoint": str(checkpoint),
                "checkpoint_sha256": envelope["checkpoint_sha256"],
                "epoch": envelope["checkpoint_epoch"],
                "map_50_95": float(metrics["map_50_95"]),
                "map_50": float(metrics["map_50"]),
                "validation_predictions": str(resolved),
                "validation_predictions_sha256": sha256_file(resolved),
            }
        )
    selected = select_checkpoint_candidate(candidates)
    artifact = {
        "schema_version": 1,
        "artifact": "validation_only_checkpoint_selection",
        "model_id": args.model_id,
        "training_seed": args.seed,
        "primary": "map_50_95",
        "tie_breakers": ["map_50", "later_epoch"],
        "candidates": candidates,
        "selected": selected,
    }
    write_json_atomic(args.output, artifact)
    print(json.dumps(selected, indent=2))
    return 0


def calibrate(args: argparse.Namespace) -> int:
    if not args.execute_validation_calibration:
        raise ProtocolError("Refusing real validation calibration without --execute-validation-calibration")
    envelope_path = resolve_repo_path(args.validation_predictions)
    envelope = read_prediction_envelope(envelope_path, required_split="val")
    protocol = validate_protocol()
    ground_truth = load_ground_truth(protocol["dataset"]["annotations"], "val", protocol["dataset"]["splits"])
    selected = calibrate_threshold(ground_truth, envelope["predictions"])
    artifact = {
        "schema_version": 1,
        "artifact": "validation_threshold_calibration",
        "model_id": envelope["model_id"],
        "training_seed": envelope["training_seed"],
        "checkpoint_sha256": envelope["checkpoint_sha256"],
        "validation_predictions": str(envelope_path),
        "validation_predictions_sha256": sha256_file(envelope_path),
        "grid": {"start": 0.01, "stop": 0.99, "step": 0.01},
        "objective": "micro_f1",
        "tie_breakers": ["higher_precision", "higher_threshold"],
        "selected": selected,
    }
    write_json_atomic(args.output, artifact)
    print(json.dumps(selected, indent=2))
    return 0


def freeze(args: argparse.Namespace) -> int:
    selection_path = resolve_repo_path(args.selection)
    with selection_path.open("r", encoding="utf-8") as handle:
        selection = json.load(handle)
    selected = selection.get("selected", {})
    manifest = create_frozen_manifest(
        model_id=selection.get("model_id"),
        checkpoint=selected.get("checkpoint", ""),
        validation_predictions=selected.get("validation_predictions", ""),
        calibration=args.calibration,
        output=args.output,
        training_seed=selection.get("training_seed"),
        selection=selection_path,
    )
    print(json.dumps(manifest, indent=2))
    return 0


def freeze_suite(args: argparse.Namespace) -> int:
    suite = create_frozen_suite(args.manifests, args.output)
    print(json.dumps(suite, indent=2))
    return 0


def protected_test(args: argparse.Namespace) -> int:
    if not args.execute_protected_test:
        raise ProtocolError("Refusing test inference without --execute-protected-test")
    benchmark_environment = require_benchmark_environment()
    manifest = validate_frozen_manifest(args.manifest)
    suite = validate_frozen_suite(args.suite)
    manifest_path = resolve_repo_path(args.manifest)
    matching_entry = next(
        (entry for entry in suite["manifests"] if entry["manifest_id"] == manifest["manifest_id"]),
        None,
    )
    if matching_entry is None or resolve_repo_path(matching_entry["path"]) != manifest_path:
        raise ProtocolError("Protected manifest is not a member of the frozen nine-run suite")
    ledger = TestRunLedger()
    ledger.refuse_if_seen(manifest["manifest_id"], manifest["model_id"], manifest["training_seed"])
    adapter = create_adapter(manifest["model_id"], manifest["checkpoint"], args.device).load()
    flop_estimates = model_flop_estimates(adapter)
    artifact_path = (
        resolve_repo_path(args.artifact_output)
        if args.artifact_output
        else REPO_ROOT
        / "results"
        / "inference-artifacts"
        / f"{manifest['model_id']}-seed{manifest['training_seed']}-{manifest['checkpoint_sha256'][:12]}-fp16.pt"
    )
    adapter.export_inference_artifact(artifact_path)
    inference_artifact = {
        "path": str(artifact_path),
        "sha256": sha256_file(artifact_path),
        "bytes": artifact_path.stat().st_size,
        "format": "standardized_inference_state_dict_fp16",
    }
    profiler = CudaForwardProfiler(adapter, warmups=10)
    profiler.prepare(adapter.synthetic_input())
    protocol = validate_protocol()
    ground_truth = load_ground_truth(protocol["dataset"]["annotations"], "test", protocol["dataset"]["splits"])
    truths_by_image: dict[int, list[dict]] = defaultdict(list)
    for annotation in ground_truth["annotations"]:
        truths_by_image[int(annotation["image_id"])].append(annotation)
    qualitative_config = protocol["evaluation"]["qualitative_error_analysis"]
    class_names = {int(key): value for key, value in protocol["dataset"]["classes"].items()}
    qualitative = QualitativeErrorCollector(
        manifest["model_id"],
        manifest["training_seed"],
        manifest["threshold"],
        class_names,
        qualitative_config["examples_per_category"],
    )

    # The irreversible boundary is immediately before the first real test frame.
    ledger.start(manifest)
    predictions: list[dict] = []
    for image in ground_truth["images"]:
        with Image.open(REPO_ROOT / "dataset" / image["file_name"]) as source:
            batch = adapter.preprocess(source)
            retained_image = source.convert("RGB").copy()
        raw_outputs = profiler.forward(batch)
        image_predictions = profiler.finalize(raw_outputs, [int(image["id"])])
        predictions.extend(image_predictions)
        qualitative.observe(image, retained_image, truths_by_image[int(image["id"])], image_predictions)
    qualitative_output = (
        resolve_repo_path(args.qualitative_output)
        if args.qualitative_output
        else REPO_ROOT / "results" / "qualitative" / f"{manifest['model_id']}_seed{manifest['training_seed']}"
    )
    qualitative_artifact = qualitative.finalize(qualitative_output)
    result = {
        "schema_version": 1,
        "artifact": "protected_test_result",
        "manifest_id": manifest["manifest_id"],
        "suite_id": suite["suite_id"],
        "model_id": manifest["model_id"],
        "training_seed": manifest["training_seed"],
        "checkpoint_sha256": manifest["checkpoint_sha256"],
        "threshold": manifest["threshold"],
        "coco_metrics": coco_metrics(ground_truth, predictions),
        "operating_point": operating_point_metrics(ground_truth, predictions, manifest["threshold"]),
        "runtime_profile": profiler.finish(),
        "parameters": adapter.parameter_count(),
        "flop_estimates": flop_estimates,
        "inference_artifact": inference_artifact,
        "benchmark_environment": benchmark_environment,
        "qualitative_analysis": qualitative_artifact,
        "predictions": predictions,
    }
    write_json_atomic(args.output, result)
    ledger.complete(manifest, args.output)
    print(json.dumps({key: value for key, value in result.items() if key != "predictions"}, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command")

    export = subparsers.add_parser("export-validation", help="Export predictions from the real validation split")
    export.add_argument("--model-id", required=True, choices=["yolo11n", "yolo26n", "dfine_n"])
    export.add_argument("--seed", required=True, type=int, choices=TRAINING_SEEDS)
    export.add_argument("--checkpoint", required=True)
    export.add_argument("--epoch", required=True, type=int)
    export.add_argument("--output", required=True)
    export.add_argument("--device", default="cuda:0")
    export.add_argument("--execute-validation-export", action="store_true", required=True)
    export.set_defaults(func=export_validation)

    select = subparsers.add_parser("select-checkpoint", help="Apply frozen validation-only checkpoint ranking")
    select.add_argument("--model-id", required=True, choices=["yolo11n", "yolo26n", "dfine_n"])
    select.add_argument("--seed", required=True, type=int, choices=TRAINING_SEEDS)
    select.add_argument("--validation-predictions", nargs="+", required=True)
    select.add_argument("--output", required=True)
    select.set_defaults(func=select_checkpoint)

    calibration = subparsers.add_parser("calibrate", help="Search the frozen threshold grid on validation only")
    calibration.add_argument("--validation-predictions", required=True)
    calibration.add_argument("--output", required=True)
    calibration.add_argument("--execute-validation-calibration", action="store_true", required=True)
    calibration.set_defaults(func=calibrate)

    freeze_parser = subparsers.add_parser("freeze", help="Freeze selected checkpoint, validation predictions, and threshold")
    freeze_parser.add_argument("--selection", required=True)
    freeze_parser.add_argument("--calibration", required=True)
    freeze_parser.add_argument("--output", required=True)
    freeze_parser.set_defaults(func=freeze)

    suite_parser = subparsers.add_parser("freeze-suite", help="Freeze all nine manifests before protected test access")
    suite_parser.add_argument("--manifests", nargs="+", required=True)
    suite_parser.add_argument("--output", required=True)
    suite_parser.set_defaults(func=freeze_suite)

    test = subparsers.add_parser("test", help="Run the protected single test pass")
    test.add_argument("--manifest", required=True)
    test.add_argument("--suite", required=True, help="Complete nine-manifest suite frozen before any test access")
    test.add_argument("--output", required=True)
    test.add_argument("--artifact-output", help="Optional path for the standardized FP16 inference state dictionary")
    test.add_argument("--qualitative-output", help="Optional directory for the pre-registered qualitative/error artifact")
    test.add_argument("--device", default="cuda:0")
    test.add_argument("--execute-protected-test", action="store_true", required=True)
    test.set_defaults(func=protected_test)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if not args.command:
        protocol = validate_protocol()
        print(f"Protocol dry-run PASSED for {protocol['benchmark']}; no images were loaded and no inference ran.")
        parser.print_help()
        return 0
    try:
        return args.func(args)
    except (ProtocolError, FileNotFoundError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
