# Training Protocol and Optimization Controls

[Back to repository](../README.md) · [Documentation hub](./README.md) · [Evaluation protocol](./evaluation-protocol.md) · [Fairness audit](./fairness.md)

This document is the authoritative training specification for DMS-Eval. Training is not authorized merely because these controls pass verification.

## Frozen comparison policy

Every model receives the same underlying training data and four-class ontology, 640×640 input, physical batch 8, fixed four-step gradient accumulation, 220 epochs, disabled early stopping, the same three predeclared training seeds (13, 37, 73), and validation-only checkpoint ranking. All training images are retained with `drop_last=false`; the last incomplete accumulation window is sample-correct for each backend's loss reduction. All three runs are reported as mean ± sample SD and best-run selection is prohibited.

Architecture-specific optimizer, learning-rate, scheduler, weight-decay, and augmentation settings follow pinned upstream recipes. The only permitted recipe adaptations are the following closed list:

1. DMS-Eval dataset and four classes.
2. 640×640 input.
3. Physical batch size 8.
4. Fixed four-step gradient accumulation.
5. 220 epochs.
6. Training seeds 13, 37, and 73.
7. Disabled early stopping.

There are zero model-specific tuning trials. Any eighth adaptation invalidates the frozen protocol until it is explicitly reviewed and documented.

## Initialization

All models start from checksum-verified official pretrained checkpoints: `yolo11n.pt`, `yolo26n.pt`, and `dfine_n_coco.pth`. The full model remains trainable. Exactly three trajectories per model are planned with identical seed identities; all are retained for aggregate reporting, so no favorable trajectory may be selected.

## Final model plans

| Dimension | Shared policy | YOLO11n | YOLO26n | D-FINE-N |
|---|---|---|---|---|
| Data/classes | Frozen DMS-Eval train split; four classes | Same | Same | Same |
| Input | 640×640 | Same | Same | Same |
| Epoch/data exposure | 220 epochs; no early stopping | Same | Same | Same |
| Physical batch | 8 | 8 | 8 | 8 |
| Accumulation | Fixed 4 from the first batch | Fixed 4 | Fixed 4 | Fixed 4 |
| Remainder | `drop_last=false`; sample-correct final window | Sum-reduced loss normalization | Sum-reduced loss normalization | Mean-reduced loss normalization |
| Seeds/runs | Seeds 13, 37, 73; three runs; mean ± sample SD; no run selection | Same | Same | Same |
| Precision | PyTorch CUDA AMP FP16 | Same policy | Same policy | Same policy |
| Checkpoint use during training | Retention/reporting only; validation never changes training state | Continuous state | Continuous state | Predefined epoch-148 augmentation/EMA transition; continuous model/optimizer state |
| Final selection | Validation mAP@0.5:0.95; ties by mAP@0.5 then later epoch | Same | Same | Same |
| Optimizer recipe | Pinned official backend recipe | Ultralytics 8.4.123 `optimizer=auto` → expected MuSGD | Same | AdamW |
| Learning rate / decay | Pinned official backend recipe | Package default `lr0=0.01`, `weight_decay=0.0005` | Same | Base LR `0.0008`, backbone LR `0.0004`, `weight_decay=0.0001` |
| Scheduler/augmentation | Pinned official backend recipe | Linear schedule and package-default augmentation | Same | Official D-FINE-N schedule and augmentation; predefined stop epoch 148 |

The Ultralytics trainer is patched only to keep accumulation at four throughout warm-up and to normalize a short final window. D-FINE is patched only for accumulation/remainder correctness, continuous training state at the predefined stage transition, checkpoint retention, and the FP16 dtype compatibility needed by the shared execution policy. Patch application is verified against pinned sources.

## What equal epochs mean

The budget equalizes epoch count and data exposure. It does not equalize parameter count, FLOPs, wall-clock training time, architecture capacity, native postprocessing, or stochastic trajectories. Those are reported as scope limitations rather than silently treated as controlled variables.

## Safe verification and gated execution

```powershell
.venv\Scripts\python.exe scripts\benchmark\verify_training_configs.py
.venv\Scripts\python.exe scripts\benchmark\train_yolo.py --model-id yolo11n --seed 13
.venv\Scripts\python.exe scripts\benchmark\train_yolo.py --model-id yolo26n --seed 13
.venv\Scripts\python.exe scripts\benchmark\train_dfine.py --seed 13
```

These commands are dry-runs. Repeat them with seeds 37 and 73. Training starts only when the explicit `--execute-training` gate is added after authorization.
