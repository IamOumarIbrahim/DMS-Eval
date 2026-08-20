# Evaluation Protocol and Profiling Harness

[Back to repository](../README.md) · [Documentation hub](./README.md) · [Training protocol](./training-protocol.md) · [Fairness audit](./fairness.md)

This document freezes the shared detection metrics, validation-only selection and calibration, protected test access, and batch-1 RTX 4060 profiling protocol.

## Reported measures

| Dimension | Measure | Frozen interpretation |
|---|---|---|
| Detection | mAP@0.5:0.95, mAP@0.5, per-class AP | Computed by the shared COCO evaluator |
| Operating point | Precision, recall, micro-F1 | IoU 0.50; same-class greedy one-to-one matching |
| False alarms | FAR per 100 negative frames | `100 × false-positive detections on negative frames / negative frames`; may exceed 100 |
| Model runtime | p50/p95/p99 and sustained FPS | Preprocessed tensor to raw model output |
| System runtime | p50/p95/p99 and sustained FPS | Preprocessed tensor to normalized final detections, including required postprocessing/NMS |
| Resources | Parameters and peak allocated VRAM | Loaded four-class model; protected batch-1 pass |
| Workload | Two FLOP estimates | THOP (`2 × MACs`) and `torch.profiler` operator sum, both explicitly tool-dependent |
| Storage | Standardized FP16 inference artifact bytes | Model state dictionary only; excludes optimizer, scheduler, scaler, EMA wrapper, and training history |

Generic classification accuracy is not reported because DMS-Eval is an object-detection benchmark.

## Shared evaluator

Every adapter emits the same COCO-style prediction schema. The master COCO annotations are the only ground truth, and one implementation computes all published quality metrics. This removes framework-evaluator differences without removing native detection/postprocessing differences.

## Validation and protected test isolation

Validation has exactly two roles:

1. Rank retained epoch checkpoints by validation mAP@0.5:0.95, then mAP@0.5, then later epoch.
2. Choose a confidence threshold from 0.01 through 0.99 in steps of 0.01 by maximum validation micro-F1, then higher precision, then higher threshold.

Validation never reloads or otherwise changes a model's training state. The chosen checkpoint, prediction artifact, threshold, and checksums are frozen into an immutable manifest before test access.

Before any protected access, a suite artifact must validate and hash all nine model–seed manifests. The protected test command requires that suite plus an explicit `--execute-protected-test` gate, validates membership, rejects a repeated model–seed run/manifest in the append-only ledger, and calls the complete RTX 4060 environment validator before inference. Test images are traversed once per frozen run: predictions, both timing boundaries, peak VRAM, and the pre-registered qualitative/error candidates are collected in that same pass. Exactly nine passes are permitted—one for each model–seed pair. Test results cannot guide checkpoint, threshold, run selection, recipe, or any other training decision.

## Shared precision and timing

All three adapters retain FP32 model weights and FP32 input tensors and execute model forward under CUDA autocast with FP16 enabled. Batch size is 1 and input shape is `1 × 3 × 640 × 640`.

Ten untimed full-path warm-ups precede measurement. Two boundaries are reported:

- **Model forward:** synchronized CUDA events around `raw_forward`.
- **Tensor to final detections:** synchronized high-resolution wall-clock timing from the preprocessed input tensor through raw forward and architecture-required normalization/postprocessing, including YOLO11n NMS.

Disk I/O, image decoding, preprocessing, metric computation, and result serialization are outside both boundaries. The second measure is therefore comparable tensor-to-detections latency, not camera-to-alert application latency.

## Complexity and storage safeguards

FLOPs are estimates rather than audited ground truth. The result artifact stores both THOP and PyTorch-profiler values plus their methods/status so operator-coverage disagreement is visible across CNN and transformer components.

Raw training checkpoint size is never used as the cross-model storage comparison. Immediately before a protected test, each loaded adapter exports the same schema: an inference-only state dictionary whose floating tensors are stored in FP16. The artifact path, SHA-256, and byte count are recorded.

## Pending results table

No numerical result is inserted before the authorized frozen runs.

| Model | Runs | mAP@0.5:0.95 | mAP@0.5 | F1 | FAR/100 | Forward p50 | Tensor→detections p50 | Forward FPS | Tensor→detections FPS | Params | FLOPs (THOP / profiler) | Peak VRAM | FP16 artifact |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| YOLO11n | 3 | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING |
| YOLO26n | 3 | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING |
| D-FINE-N | 3 | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING |

## Interpretation boundary

The benchmark compares three fully configured deployable detector systems. Equal data exposure and shared evaluation do not isolate architecture, equalize compute, or eliminate native postprocessing differences. Three equal predeclared seeds quantify limited stochastic variation, but do not by themselves establish broad statistical superiority.
