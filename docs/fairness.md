# Fairness Audit

[← Back to Main Landing Page](../README.md) · [Documentation Hub](./README.md) · [Training Protocol](./training-protocol.md) · [Evaluation Protocol](./evaluation-protocol.md)

This audit describes the current implemented protocol before any training or real evaluation has run. It distinguishes shared controls from backend-specific behavior that can affect cross-model interpretation. The entries are methodological risks, not observed performance effects; the named beneficiary is the most plausible direction, not an empirical conclusion.

| Severity | Asymmetry | Likely beneficiary | Fairness impact | Recommended correction |
|---|---|---|---|---|
| High | D-FINE reloads its best stage-1 validation checkpoint at epoch 148 and can perform additional validation-driven reloads afterward | D-FINE-N | D-FINE’s training trajectory receives validation-guided intervention, while YOLO uses validation only for reporting/checkpoint retention | Remove the validation-driven D-FINE restart, or implement an equivalent predefined restart rule that does not inspect validation performance |
| High | YOLO accumulation ramps from 1 to 4 during warm-up; D-FINE uses fixed accumulation 4 | YOLO11n/YOLO26n | YOLO receives substantially more optimizer updates during approximately the first three epochs | Implement fixed four-step accumulation for YOLO or explicitly define different native accumulation as an architecture-specific variable |
| High | D-FINE uses `drop_last=true`; YOLO uses `drop_last=false` | YOLO11n/YOLO26n | D-FINE drops seven training images each epoch—1,540 image presentations over 220 epochs—while YOLO sees every image | Use the same `drop_last` policy and correctly normalize partial accumulation windows |
| High | Optimization settings are benchmark-selected rather than comparably derived official recipes | Uncertain; D-FINE may be disadvantaged | D-FINE-N’s official config uses base/backbone LR `0.0008/0.0004`, while the benchmark uses `0.00025/0.0000125`; Ultralytics’ pinned default uses automatic MuSGD selection, while the benchmark forces SGD | Either preserve upstream recipes except for declared shared controls, or give every model the same validation-only tuning budget |
| High | Inference precision is not identical | Split effect | D-FINE’s autocast may preserve more FP32-sensitive operations, potentially helping accuracy, while YOLO’s pure FP16 weights may help speed and VRAM | Run all inference under the same execution/casting policy, or report the modes as separate deployment configurations |
| High | Timing excludes required postprocessing and NMS | Especially YOLO11n; potentially D-FINE too | YOLO11n’s required NMS cost is omitted, while YOLO26n performs more of its end-to-end detection work inside the timed model boundary | Report both model-only latency and tensor-to-final-detections latency |
| High | Raw training-checkpoint size is compared | YOLO models | YOLO serializes a half-precision EMA-oriented package, whereas D-FINE checkpoints may contain FP32 model, EMA, optimizer, and scheduler states | Export a standardized inference-only FP16 state dictionary for every model and compare that size |
| Medium | Architecture capacities and per-epoch compute differ | D-FINE-N for potential accuracy; YOLO for efficiency | Equal epochs provide equal data passes, not equal FLOPs, wall time, or parameter capacity | Describe the budget as equal epochs/data exposure, not equal compute |
| Medium | Postprocessing differs: YOLO11n uses NMS; D-FINE and YOLO26n are end-to-end | Likely YOLO11n on this ≤1-object-per-frame dataset | NMS can remove duplicate detections before F1/FAR calculation, reducing false positives | Accept this only if comparing deployable systems; otherwise report an additional standardized raw-output analysis |
| Medium | One seed and one run per model | No predictable beneficiary | Random initialization, sampling, and CUDA variance may make one model appear better by chance | Prefer multiple seeds or explicitly characterize conclusions as single-run results |
| Medium | Protected evaluation does not itself reject non-RTX-4060 hardware | Whichever model is accidentally run elsewhere | Separate test invocations could be performed under different hardware despite the documented policy | Call the environment validator inside protected test execution |
| Medium | THOP operator coverage may differ across CNN and transformer operations | Uncertain | Identical tooling does not guarantee equally accurate FLOP accounting for custom attention/deformable operations | Validate FLOPs with a second tool or audited per-operator rules |

## Controls that are consistent

All candidates use the same underlying image and annotation sets, subject-disjoint split, 640×640 resolution, protected master COCO ground truth, physical training batch, epoch ceiling, checkpoint-ranking rule, threshold grid and tie-breakers, shared metric implementation, target RTX 4060 environment, batch-1 model-forward timing procedure, and protected single-pass test policy. Disabled early stopping does not itself favor a model because the best earlier validation checkpoint remains eligible under the shared ranking procedure.

## Interpretation

Until the high-severity items are resolved, results may support a transparent comparison of the three configured systems, but not a claim that architecture alone caused every observed difference. Technical readiness and protocol reproducibility are necessary but insufficient conditions for a publishable paper.
