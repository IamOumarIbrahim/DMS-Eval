# Benchmark readiness and traceability

`configs/benchmark.yaml` is the machine-readable frozen source of truth. The authoritative artifacts `dataset/annotations.json` and `dataset/splits.json` are protected by SHA-256 fingerprints and are never rewritten by preflight.

## Requirement traceability

| Frozen requirement | Authoritative documentation | Configuration | Implementation | Automated test/check |
|---|---|---|---|---|
| Models: YOLO11n, YOLO26n, D-FINE-N | `README.md`, `docs/training-protocol.md` | `configs/benchmark.yaml`, `configs/backends.yaml` | `core/adapters/` | `scripts/validate_backends.py --synthetic` |
| Official pretrained initialization and provenance | `docs/training-protocol.md` | `configs/backends.yaml` | `scripts/setup_backends.py` | checksum/size checks in setup and backend validation |
| Four-class ontology and COCO↔YOLO mapping | `docs/annotation-protocol.md` | `configs/benchmark.yaml` | `core/dataset.py`, adapters | `tests/test_protocol.py`, dataset preflight |
| Protected master COCO and split fingerprints | this document | `configs/benchmark.yaml` | `core/protocol.py` | `tests/test_protocol.py`, preflight |
| 640×640 input and 14 subjects | `docs/quick-start.md` | `configs/benchmark.yaml` | adapters, dataset validator | full image decode preflight |
| Frozen 8/3/3 subject split and exact counts | `README.md`, `docs/quick-start.md` | `dataset/splits.json`, `configs/benchmark.yaml` | `core/dataset_validation.py` | `tests/test_audit_fixes.py`, full preflight |
| Train-only seed-13 permutation; native val/test order | `docs/training-protocol.md` | `configs/benchmark.yaml` | conversion scripts | derived parity and order checks in dataset preflight |
| Physical batch 8 and nominal effective batch 32 | `docs/training-protocol.md` | `configs/benchmark.yaml`, D-FINE YAML | YOLO `nbs=32` warm-up ramp; fixed D-FINE accumulation patch | launcher dry-runs; patch verification |
| 220 epochs, seed 13, AMP FP16, no early stopping | `docs/training-protocol.md` | `configs/benchmark.yaml` | training launchers | frozen-plan dry-runs |
| Benchmark-pinned optimization and augmentation recipes | `docs/training-protocol.md` | `configs/benchmark.yaml`, D-FINE YAML | explicit YOLO launcher arguments; pinned D-FINE config | `tests/test_protocol.py`, launcher dry-runs, D-FINE config construction |
| Validation-only checkpoint selection | `docs/evaluation-protocol.md` | `configs/benchmark.yaml` | `select-checkpoint` subcommand | CLI and artifact validation tests |
| Primary mAP50:95; ties mAP50 then later epoch | `docs/evaluation-protocol.md` | `configs/benchmark.yaml` | `select-checkpoint` subcommand | evaluator unit tests and selection artifact validation |
| Validation-only threshold grid 0.01…0.99 | `docs/evaluation-protocol.md` | `configs/benchmark.yaml` | `core/evaluation.py` | `tests/test_evaluation.py` |
| Maximize micro-F1; ties precision then threshold | `docs/evaluation-protocol.md` | `configs/benchmark.yaml` | `calibrate_threshold` | threshold known-answer tests |
| Official COCO mAP50:95, mAP50, per-class AP | `docs/evaluation-protocol.md` | `configs/benchmark.yaml` | `pycocotools` evaluator | perfect-prediction known-answer test |
| IoU 0.50, same-class greedy one-to-one matching | `docs/evaluation-protocol.md` | `configs/benchmark.yaml` | `operating_point_metrics` | IoU/matching known-answer tests |
| FAR = negative-frame FP detections / negative frames ×100 | `docs/evaluation-protocol.md` | `configs/benchmark.yaml` | `operating_point_metrics` | FAR known-answer test |
| Frozen-artifact test isolation and single test pass | `docs/evaluation-protocol.md` | `configs/benchmark.yaml` | `core/isolation.py`, protected `test` command | `tests/test_isolation.py` |
| RTX 4060; batch-1 FP16; 10 warm-ups | `docs/evaluation-protocol.md` | `configs/benchmark.yaml` | `core/profiling.py` | environment validation and synthetic CUDA profile |
| CUDA events and model-forward-only boundary | `docs/evaluation-protocol.md` | `configs/benchmark.yaml` | adapters’ `raw_forward`, `CudaForwardProfiler` | synthetic profiler smoke |
| p50/p95/p99 and sustained frames/total GPU time | `docs/evaluation-protocol.md` | `configs/benchmark.yaml` | `CudaForwardProfiler.finish` | profiler smoke and unit assertions |
| Parameters, FLOPs, peak allocated VRAM, checkpoint size | `docs/evaluation-protocol.md` | `configs/benchmark.yaml` | profiler and protected result schema | backend/profile smoke |

## Readiness versus fairness

`READY FOR TRAINING` means that the frozen implementation, environment, data, adapters, evaluator, isolation controls, and future commands pass their technical checks. It does not mean that every cross-framework optimization step or deployment artifact is identical, nor does it make the eventual results publication-ready by itself. The current directional comparability risks are listed in the [fairness audit](./fairness.md) and must be considered before authorizing training or making architectural-superiority claims.

## Safe setup commands

```powershell
uv venv --python 3.12.10 .venv
uv pip sync --python .venv\Scripts\python.exe requirements.lock.txt
.venv\Scripts\python.exe scripts/setup_backends.py --install
.venv\Scripts\python.exe scripts/validate_environment.py
.venv\Scripts\python.exe scripts/validate_dataset.py
.venv\Scripts\python.exe scripts/validate_backends.py --synthetic
.venv\Scripts\python.exe -m pytest -q
```

The training launchers are dry-runs unless `--execute-training` is present. Validation export and calibration also require explicit execution gates. Test is unavailable until selection, validation predictions, calibration, and their checksums are frozen into a manifest; it additionally requires `--execute-protected-test`, and the append-only ledger refuses repeats.

## Future benchmark lifecycle (do not run during setup)

```powershell
# Training (each command prints a dry-run plan without the final gate)
.venv\Scripts\python.exe scripts/train_yolo.py --model-id yolo11n --execute-training
.venv\Scripts\python.exe scripts/train_yolo.py --model-id yolo26n --execute-training
.venv\Scripts\python.exe scripts/train_dfine.py --execute-training

# Export validation predictions once per saved epoch/checkpoint
.venv\Scripts\python.exe scripts/evaluate_benchmark.py export-validation --model-id yolo11n --checkpoint runs/train/yolo11n_seed13/weights/epoch1.pt --epoch 1 --output predictions/yolo11n/epoch1-val.json --execute-validation-export

# Rank validation artifacts, calibrate the selected validation predictions, and freeze
.venv\Scripts\python.exe scripts/evaluate_benchmark.py select-checkpoint --model-id yolo11n --validation-predictions predictions/yolo11n/*-val.json --output results/frozen/yolo11n-selection.json
.venv\Scripts\python.exe scripts/evaluate_benchmark.py calibrate --validation-predictions predictions/yolo11n/SELECTED-val.json --output results/frozen/yolo11n-calibration.json --execute-validation-calibration
.venv\Scripts\python.exe scripts/evaluate_benchmark.py freeze --selection results/frozen/yolo11n-selection.json --calibration results/frozen/yolo11n-calibration.json --output results/frozen/yolo11n-manifest.json

# Protected test and runtime profiling happen together in the sole real test pass
.venv\Scripts\python.exe scripts/evaluate_benchmark.py test --manifest results/frozen/yolo11n-manifest.json --output results/test/yolo11n.json --execute-protected-test

# Synthetic standalone profiling is safe and never reads a dataset split
.venv\Scripts\python.exe scripts/profile_runtime.py --model-id yolo11n --checkpoint weights/pretrained/yolo11n.pt --allow-pretrained-head-mismatch

# Final aggregation and publication artifacts
.venv\Scripts\python.exe scripts/aggregate_results.py results/test/yolo11n.json results/test/yolo26n.json results/test/dfine_n.json --output results/aggregate.json
.venv\Scripts\python.exe scripts/generate_publication_tables.py --aggregate results/aggregate.json --markdown generated/results.md --latex generated/results.tex
.venv\Scripts\python.exe scripts/generate_figures.py --aggregate results/aggregate.json --output generated/accuracy-latency.png
```

PowerShell wildcard expansion is not automatic for native Python programs. Replace `predictions/yolo11n/*-val.json` with the explicit validation artifact paths when selecting a checkpoint.
