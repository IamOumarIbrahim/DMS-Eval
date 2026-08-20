# Benchmark Readiness and Traceability

**Status:** READY FOR BENCHMARK TRAINING; PROTECTED TEST NOT READY UNTIL NINE POST-TRAINING MANIFESTS ARE FROZEN

**Verified:** 2026-08-20 19:19 GST (+04:00)

**Machine-readable evidence:** [`benchmark-readiness.json`](./benchmark-readiness.json)

`configs/benchmark.yaml` remains the machine-readable protocol source of truth. The readiness audit verified the actual derived datasets, backend code, pinned configurations, launcher behavior, real training batches, evaluator tests, and isolation gates. It did not start any 220-epoch benchmark run or any protected test inference/metric pass. Read-only integrity validation did decode and hash every dataset image, including the test partition.

## Frozen claim boundary

All models use the same underlying data/classes, subject-disjoint split, 640×640 input, physical batch 8, fixed accumulation 4, 220 epochs, disabled early stopping, the same three predeclared training seeds (13, 37, 73), sample-correct retention of every training image, validation-only checkpoint selection without training-state intervention, RTX 4060 environment, FP32 model/input storage under CUDA AMP FP16, shared evaluator, batch-1 dual-boundary profiling, and protected test policy. Every run is retained and per-model results are mean ± sample SD; best-run selection is prohibited.

Architecture-specific optimizer, learning-rate, scheduler, weight-decay, and augmentation settings follow pinned official recipes. The only recipe adaptations are dataset/classes, 640×640 input, batch 8, accumulation 4, 220 epochs, the three training seeds, and disabled early stopping.

## Readiness verdict by requirement

| Requirement | Result | Direct evidence |
|---|---|---|
| Authoritative data and ontology | PASS | Pinned master/split SHA-256 values; 15,723 images, 3,001 boxes, four classes, at most one box/frame |
| Subject isolation and class coverage | PASS | Exact 8/3/3 subjects, no overlap, expected class counts in every split |
| Image and annotation compatibility | PASS | 15,723 distinct JPEG decodes/hashes; all boxes bounded; all YOLO and D-FINE paths resolve |
| Adapter-facing class mapping | PASS | Master IDs 1–4 map to YOLO and D-FINE labels 0–3; adapters map predictions back to shared IDs 1–4 |
| Pinned model availability | PASS | Ultralytics 8.4.123; D-FINE commit `956d170...`; all three official weight hashes and sizes match |
| Locked environment and hardware | PASS | Python 3.12.10, Torch 2.4.1+cu121, RTX 4060 8 GB, CUDA AMP smoke, 73-package compatibility check |
| Frozen shared training controls | PASS | Nine-plan verifier: epochs 220, batch 8, accumulation 4, seeds 13/37/73, no early stop/drop, unique outputs |
| Pinned architecture recipes | PASS | YOLO `optimizer=auto` resolves to MuSGD; D-FINE AdamW uses base/backbone LR `0.0008/0.0004` |
| Real training-path smoke | PASS | Complete four-batch windows until verified trainable-parameter movement; one successful update/model; finite losses; peak allocated VRAM ≤2.490 GB |
| Validation/checkpoint lifecycle | PASS | Every one of 220 retained epochs is required; selection and threshold calibration are validation-only and immutable |
| Protected test isolation | PASS, not yet eligible | Exactly nine hash-verified manifests and a frozen suite are required; ledger starts before any test annotation/image read |
| Output safety and auditability | PASS | Run/output reuse and aggregate overwrite are rejected; every model–seed result is required and retained |
| Shared evaluator and aggregation | PASS | Known-answer COCO/F1/FAR tests; all seed results preserved; mean ± sample SD uses the `n-1` denominator |
| Inference protocol/resources | PASS | Synthetic adapters and dual-boundary profiler pass at batch 1 with common AMP; parameters, VRAM, dual FLOPs, artifact bytes supported |
| Qualitative/error analysis | PASS | Five pre-registered categories, deterministic ranking, three candidates/category, reference seed 13, same-pass collection |
| Repository verification | PASS | 42 tests, 110 local links, 13/13 external links, dependency check, Git object integrity, and diff whitespace check |
| Capacity for execution | PASS | 34.19 GB physical RAM and 436.43 GB free disk; smoke peak is below the 8 GB GPU budget |

## Smoke-gate audit trail

The readiness smoke was intentionally fail-closed. Audit-only attempts exposed derived-data defects and then tightened the definition of a successful AMP update; none was a benchmark run or protected test pass.

| Attempt | Outcome | Finding |
|---|---|---|
| `training-smoke-20260820T184619+0400` | FAIL | YOLO lists omitted the canonical `images/` path component |
| `training-smoke-20260820T185007+0400` | FAIL | D-FINE derived COCO names duplicated the configured image root |
| `training-smoke-20260820T185322+0400` | FAIL | D-FINE received one-based class IDs for a zero-based four-class loss |
| `training-smoke-20260820T185612+0400` | SUPERSEDED | Finite backward paths passed, but the earlier harness did not prove that AMP had not skipped the step |
| `training-smoke-20260820T190752+0400` through `T191501+0400` | FAIL / DIAGNOSTIC | Stricter instrumentation exposed skipped initial `GradScaler` attempts and replaced unreliable counters with direct optimizer-state and parameter-change checks |
| `training-smoke-20260820T191304+0400` and `T191619+0400` | DIAGNOSTIC PASS | D-FINE-N and YOLO11n individually proved successful updates under the stricter probe |
| `training-smoke-20260820T191715+0400` | PASS | Canonical all-three smoke proved one successful update/model under frozen controls |

The canonical passing report has SHA-256 `0dc700f8fa12a96cd59a0e81d40ca602e0319d1019728eb19f079912ca26f16a`. YOLO11n, YOLO26n, and D-FINE-N required 9, 7, and 8 attempted four-batch windows respectively before their first verified parameter update; their unchanged scalers stabilized from 65,536 to 256, 1,024, and 512. Regression checks also resolve every derived image path and verify D-FINE’s internal 0–3 mapping against the authoritative 1–4 ontology.

## Requirement traceability

| Frozen control | Configuration / source | Enforcement |
|---|---|---|
| Three pinned models and official initialization | `configs/backends.yaml` | Package/commit/recipe/weight hashes plus adapter and training smokes |
| Four classes, 640×640, subject-disjoint 8/3/3 split | `configs/benchmark.yaml`, authoritative data | Fingerprints, full decode/hash scan, split/coverage tests |
| Batch 8, fixed accumulation 4, 220 epochs, seeds 13/37/73, no early stop | Training protocol and nine plans | Patched backends, source/config assertions, real optimizer-step smoke |
| No dropped images; sample-correct short window | `training.incomplete_batch` | Loader assertions and accumulation known-answer tests |
| Validation cannot change training state | `validation_intervention: checkpoint_retention_only` | D-FINE reload removal and source verifier |
| Pinned official architecture recipes | Recipe hashes and optimization blocks | YOLO MuSGD resolution; D-FINE AdamW `0.0008/0.0004` |
| Closed seven-item adaptation list | `training.recipe_policy.allowed_adaptations` | Exact ordered-list assertion; zero tuning trials |
| Validation-only checkpoint/threshold selection | Evaluation configuration | Complete 220-epoch coverage, immutable artifacts, fixed ranking/grid/ties |
| One protected pass per frozen model–seed run | `test_policy` | Seed-bound manifests, nine-run suite, RTX gate, append-only ledger |
| No best-run selection | `run_selection: none` | Aggregate requires all nine and reports mean ± sample SD |
| Pre-registered qualitative/error analysis | Frozen qualitative configuration | Same protected pass, deterministic collector, hashes, generator tests |
| Common inference precision and timing | Profiling configuration | FP32 storage/input, CUDA AMP FP16, synchronized dual timing boundaries |
| Comparable resources | Standard artifact/resource policy | Parameters, peak VRAM, dual FLOP estimates, inference-only FP16 artifact bytes |

## Safe readiness commands

```powershell
.venv\Scripts\python.exe scripts\benchmark\preflight.py
.venv\Scripts\python.exe scripts\benchmark\validate_backends.py --synthetic
.venv\Scripts\python.exe scripts\benchmark\verify_training_configs.py
.venv\Scripts\python.exe scripts\benchmark\smoke_training.py --output-root NEW_OUTPUT --report NEW_REPORT.json --execute-training-smoke
.venv\Scripts\python.exe scripts\maintenance\check_links.py --external
.venv\Scripts\python.exe -m pytest -q
```

Training launchers are dry-runs unless `--execute-training` is present. Never reuse a run directory. After all nine trainings finish, export validation predictions for every retained epoch, select/checkpoint and calibrate on validation only, freeze all nine manifests into one suite, then perform exactly one protected pass per run.

## Post-training lifecycle

For each model–seed pair, export validation predictions for all 220 retained checkpoints; select by validation mAP50–95 with frozen tie-breakers; calibrate the operating threshold on the selected validation predictions; and freeze the manifest. The first protected test pass remains blocked until the suite contains exactly YOLO11n, YOLO26n, and D-FINE-N at seeds 13, 37, and 73 with valid hashes. After the nine single passes, aggregate all individual results as mean ± sample SD and generate tables, figures, and qualitative/error artifacts from the preserved results.

## Interpretation limits

Implementation readiness does not make the manuscript publishable by itself. Equal epochs mean equal data exposure rather than equal compute or an identical count of successful AMP updates. Native postprocessing and architecture capacity differ, three seeds provide limited uncertainty evidence, and FLOP estimators have operator-dependent coverage. Final scientific claims still require the complete benchmark, artifact verification, bounded analysis, PI review, and venue review.
