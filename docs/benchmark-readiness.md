# Benchmark Readiness and Traceability

**Status:** READY FOR TRAINING AT THE IMPLEMENTATION LEVEL; TRAINING NOT AUTHORIZED

**Verified:** 2026-08-20 17:32 GST (+04:00)

**Publication target:** `main`

`configs/benchmark.yaml` is the machine-readable source of truth. Dataset master artifacts remain protected by pinned SHA-256 fingerprints. No training, validation export/calibration, protected test inference, or test metric computation was run while producing this report.

## Frozen claim boundary

All models use the same underlying data/classes, subject-disjoint split, 640×640 input, physical batch 8, fixed accumulation 4, 220 epochs, seed 13, disabled early stopping, one run, sample-correct retention of every training image, validation-only checkpoint selection without training-state intervention, RTX 4060 environment, FP32 model/input storage under CUDA AMP FP16, shared evaluator, batch-1 dual-boundary profiling, and protected test policy.

Architecture-specific optimizer, learning-rate, scheduler, weight-decay, and augmentation settings follow pinned official recipes. The only recipe adaptations are dataset/classes, 640×640 input, batch 8, accumulation 4, 220 epochs, seed 13, and disabled early stopping.

## Verification evidence

| Check | Result |
|---|---|
| Full preflight | PASS; protocol, environment, backends, weights, and 59,217 dataset checks |
| Dataset validation | PASS; 15,723 distinct decoded images; exact global/train/val/test counts; 0 failures |
| Environment | PASS; Python 3.12.10, Torch 2.4.1+cu121, RTX 4060 8 GB, CUDA FP16 smoke |
| Backend provenance | PASS; Ultralytics 8.4.123 recipe hash and patch; D-FINE commit `956d170...`, official N recipe hash, and patch |
| Final plan verifier | VERIFIED; exact seven-item adaptation list and all three dry-run configurations |
| Adapter smoke | PASS for YOLO11n, YOLO26n, and D-FINE-N with FP32 input under CUDA AMP |
| Dual-boundary synthetic profiler | PASS for all three adapters; three timed synthetic frames after 10 warm-ups, dual FLOP estimators exercised |
| Test suite | PASS; 31 tests |
| Link integrity | PASS; 108 local targets and 13 unique HTTP(S) targets; 0 broken |
| Training launchers | PASS as dry-runs; each explicitly reported that training was not started |
| Manuscript production | PASS; stable multi-pass compile, 6 letter-size pages, 0 errors, 0 undefined references, 0 overfull boxes, and 11 harmless underfull spacing notices; all pages visually inspected with no clipping/overlap |
| Protected test | NOT RUN by design |

Synthetic profiler values are setup diagnostics only and must not be used as benchmark results.

## Requirement traceability

| Requirement | Configuration / source | Enforcement |
|---|---|---|
| Three pinned models and official initialization | `configs/backends.yaml` | Setup hashes, versions, commit, and adapter smoke |
| Four classes, 640×640, subject-disjoint 8/3/3 split | `configs/benchmark.yaml`, protected dataset artifacts | Protocol fingerprints and full dataset validator |
| Batch 8, fixed accumulation 4, 220 epochs, seed 13, no early stopping | `configs/benchmark.yaml`, model launch plans | Patched backends, protocol assertions, config verifier, dry-runs |
| No dropped images; sample-correct short window | `training.incomplete_batch` | Backend patches and accumulation regression tests |
| Validation cannot change training state | `validation_intervention: checkpoint_retention_only` | D-FINE reload removal and config-verifier source check |
| Pinned official architecture recipes | Recipe hashes and optimization blocks | YOLO `optimizer=auto` (expected MuSGD); D-FINE AdamW `0.0008/0.0004` |
| Closed seven-item recipe adaptation list | `training.recipe_policy.allowed_adaptations` | Exact ordered-list assertion; zero tuning trials |
| Validation-only checkpoint/threshold selection | Evaluation configuration | Immutable artifacts, fixed ranking/grid/ties, unit tests |
| Single protected test pass | `test_policy` | Manifest checks, explicit gate, append-only ledger |
| RTX 4060 enforcement | Environment manifest | Protected command calls full validator before test access |
| Common inference precision | Profiling configuration | FP32 weights/input and CUDA autocast FP16 in every adapter |
| Forward and tensor-to-final-detections timing | Profiling boundaries | CUDA events plus synchronized high-resolution wall clock in the same pass |
| Comparable storage | Standardized artifact policy | Inference-only FP16 state dictionary; hash and bytes recorded |
| FLOP uncertainty visible | Dual-estimator policy | THOP and `torch.profiler` methods/status recorded |
| Results remain pending | Documentation/manuscript | No empirical field populated before authorized runs |

## Safe commands

```powershell
.venv\Scripts\python.exe scripts\benchmark\preflight.py
.venv\Scripts\python.exe scripts\benchmark\validate_backends.py --synthetic
.venv\Scripts\python.exe scripts\benchmark\verify_training_configs.py
.venv\Scripts\python.exe scripts\maintenance\check_links.py --external
.venv\Scripts\python.exe -m pytest -q

# Dry-run only
.venv\Scripts\python.exe scripts\benchmark\train_yolo.py --model-id yolo11n
.venv\Scripts\python.exe scripts\benchmark\train_yolo.py --model-id yolo26n
.venv\Scripts\python.exe scripts\benchmark\train_dfine.py
```

Do not add `--execute-training` until the frozen Paragraph A and this readiness evidence have been approved.

## Post-training lifecycle

After explicit authorization: train each model once; export retained validation predictions; rank checkpoints by validation mAP; calibrate the confidence threshold on validation; freeze the manifest; then run one environment-gated protected test pass per model. That pass produces quality metrics, both timing boundaries, peak VRAM, dual FLOP estimates, and the standardized FP16 artifact without a second test traversal.

## Interpretation limits

Implementation readiness does not make the manuscript publishable by itself. Equal epochs mean equal data exposure rather than equal compute. Native postprocessing and architecture capacity differ, FLOP tools have incomplete coverage, and one run cannot establish statistical superiority. The final paper still requires authorized empirical results, bounded analysis, PI review, and venue review.
