# Fairness Audit

[Back to repository](../README.md) · [Documentation hub](./README.md) · [Training protocol](./training-protocol.md) · [Evaluation protocol](./evaluation-protocol.md)

This is a pre-training implementation audit. It records controls and residual interpretation risks; it does not report empirical effects.

## Paragraph A — frozen methodological goal

All models use the same underlying training/test data, subject-disjoint test split, 640×640 resolution, evaluation annotations, shared metric implementation, RTX 4060 benchmark environment, FP32 model/input storage under CUDA AMP FP16, physical training batch size 8, fixed four-step gradient accumulation, batch-1 inference protocol, and protected test-access policy. Shared controls include 220 epochs, disabled early stopping, retention of every training image with sample-correct incomplete-window normalization, three predeclared training seeds (13, 37, and 73), and validation-only checkpoint selection that never changes training state. Every run is retained, results are aggregated as mean ± sample SD, and best-run selection is prohibited. Architecture-specific optimizer, learning-rate, scheduler, weight-decay, and augmentation settings follow pinned official recipes. The only recipe adaptations are the DMS-Eval dataset and four classes, 640×640 input, physical batch 8, fixed four-step accumulation, 220 epochs, the three training seeds, and disabled early stopping; no model-specific tuning is performed.

This paragraph is the goal enforced by configuration and verification. It does not imply equal compute, statistical significance, or publication readiness.

## Corrections implemented before training

| Former asymmetry | Implemented control | Verification |
|---|---|---|
| D-FINE validation-guided stage reloads | Removed; epoch-148 transition is predefined and continues the current model/optimizer state | Backend patch and config verifier reject the old reload |
| YOLO accumulation warm-up ramp | Fixed accumulation at four from the first training batch | Pinned Ultralytics trainer patch |
| D-FINE dropped incomplete batches | `drop_last=false` for all; short final windows are sample-correct for mean- or sum-reduced losses | Configuration and accumulation unit tests |
| Benchmark-selected optimizer settings | Restored pinned official recipes; YOLO `optimizer=auto` (expected MuSGD), D-FINE AdamW `0.0008/0.0004` | Source recipe fingerprints and final-plan verifier |
| Unequal inference precision | FP32 model weights/input tensors for all, with CUDA autocast FP16 around model forward | Adapter and protocol assertions |
| Forward-only timing | Both model-forward and tensor-to-final-detections latency/FPS are reported | Shared one-pass profiler |
| Raw checkpoint size | Replaced by a standardized inference-only FP16 state-dictionary artifact | Artifact schema and unit test |
| Ambiguous equal-epoch claim | Described as equal epoch/data exposure, never equal FLOPs or wall time | Documentation/manuscript wording |
| Native postprocessing hidden from timing | Architecture-required postprocessing/NMS is included in the second timing boundary | Profiler finalization path |
| Environment policy was documentary only | Protected test calls the complete RTX 4060 validator before ledger/test access | Environment gate and unit test |
| Single-tool FLOP estimate | THOP and `torch.profiler` estimates are stored with method/status and an operator-coverage caveat | Protected/synthetic result schema |
| One seed and one run | Replaced by the same three fixed seeds for every model; all runs are reported as mean ± sample SD with no best-run selection | Protocol assertions, nine-plan verifier, model–seed manifests, ledger, and aggregate completeness gate |
| Post-hoc qualitative example selection | Five error categories, deterministic ranking, three candidates/category, and publication reference seed 13 are frozen before training | Same-pass collector, artifact hashes, known-answer tests, and publication generator |

## Residual, non-removable scope limitations

| Limitation | Fairness implication | Required interpretation |
|---|---|---|
| Architecture capacities and per-epoch compute differ | Equal data passes do not equal parameters, FLOPs, or wall time | Compare configured systems and accuracy–efficiency trade-offs; do not claim architecture-only causation |
| Native postprocessing differs | YOLO11n uses NMS while end-to-end detectors have different output semantics | Use tensor-to-final-detections latency for deployable-system comparison and disclose native postprocessing |
| Three seeds per model remain a small sample | Mean ± sample SD characterizes limited run-to-run variation but may not capture every stochastic outcome | Report all seeds and uncertainty; avoid broad claims of statistical superiority |
| FLOP tools have incomplete/operator-dependent coverage | CNN/transformer estimates may disagree for tooling reasons | Report both estimates and avoid false precision |
| Official recipes originated under different upstream tasks/batches | Recipe faithfulness does not make optimization mathematically identical | State the closed adaptation list and avoid unrestricted fairness claims |
| Early stopping is disabled | A model can overtrain by epoch 220, but all retained checkpoints remain eligible under the same validation-only rule | Report selected validation epoch and never use test performance to diagnose or correct overtraining |
| Common AMP scaling can skip different initial update attempts when gradients overflow | Identical AMP policy does not guarantee an identical count of successful numerical updates | Keep the scaler policy unchanged for all models, retain full logs, and describe any observed skips as architecture/loss-dependent numerical behavior rather than a tuned budget difference |

## Verdict boundary

After all automated checks pass, the protocol supports the frozen Paragraph A as a transparent system-level benchmark claim. It still does not establish that architecture alone caused a result, that three runs exhaust stochastic uncertainty, or that the paper is publishable before real results, analysis, and scientific review exist.
