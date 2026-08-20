# 🏋️ Training Protocol & Optimization Controls

[← Back to Main Landing Page](../README.md) · [Documentation Hub](./README.md) · [Evaluation Protocol](./evaluation-protocol.md) · [Fairness Audit](./fairness.md) · [Pipeline Scripts](../scripts/README.md)

This authoritative protocol governs model initialization, shared training constraints, hardware controls, and benchmark-pinned model-specific optimization configurations for **DMS-Eval**.

---

## 🔒 Controlled-Comparison Principle

The benchmark separates shared experimental controls from disclosed model-specific behavior:

1. **Shared controls:** underlying training data, physical batch 8, 220-epoch ceiling, disabled early stopping, RTX 4060 target, FP16 training policy, seed 13, one trajectory, and validation-only final checkpoint ranking.
2. **Nominal rather than literal accumulation equality:** all models target a nominal effective batch of 32. D-FINE uses fixed four-step accumulation; Ultralytics ramps accumulation from 1 toward 4 during warm-up and then settles at 4.
3. **Benchmark-pinned recipes:** optimizer, learning rate, schedule, weight decay, and augmentation are explicit model-specific benchmark choices. They are documented but are not represented as unchanged copies of every current upstream default.

These controls equalize data and the epoch ceiling, not total FLOPs, wall-clock training time, optimizer-update count, or stochastic trajectory. Known asymmetries are recorded in the [fairness audit](./fairness.md).

---

## 1. Initialization & Full-Model Fine-Tuning

- **Pretrained Initialization:** All models start from verified official checkpoints (`yolo11n.pt`, `yolo26n.pt`, and the official COCO `dfine_n_coco.pth`). No model is trained from scratch; URLs and SHA-256 values are pinned in `configs/backends.yaml`.
- **Full-Model Fine-Tuning:** All backbone, neck, and detection head layers are fully trainable (0 frozen layers).
- **Single Training Run:** Exactly one trajectory per model is planned with seed 13. This is reproducible as a protocol but does not quantify multi-seed uncertainty.

---

## 2. Shared Controls and Model-Specific Recipes

<div align="center">

<sub><b>Table 1.</b> Authoritative training specification: shared benchmark controls and explicitly pinned model-specific variations.</sub>

| Parameter Dimension | Shared Controlled Benchmark Policy | Ultralytics YOLO11n Recipe | Ultralytics YOLO26n Recipe | D-FINE-N Recipe | Scientific Rationale |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Fine-Tuning Budget** | **220 Epochs** (No Early Stopping) | 220 Epochs | 220 Epochs | 220 Epochs | Equal epoch/data-pass ceiling, not equal training compute |
| **Mini-Batch Size** | **Physical Batch = 8** | Batch 8 | Batch 8 | Batch 8 | Comfortably fits RTX 4060 8 GB VRAM in FP16 |
| **Gradient Accumulation** | **Nominal Batch 32** | `nbs=32`; warm-up ramps 1→4 | `nbs=32`; warm-up ramps 1→4 | Fixed `accum=4` | Exact early optimizer-update schedules differ |
| **Hardware Platform** | **NVIDIA RTX 4060 (8 GB)** | RTX 4060 | RTX 4060 | RTX 4060 | Standardized automotive edge GPU environment |
| **Training Precision** | **Automatic Mixed Precision (FP16 policy)** | PyTorch AMP | PyTorch AMP | PyTorch AMP | Common policy; backend operator casting may differ |
| **Random Seed** | **Seed = 13** across all frameworks | Seed 13 | Seed 13 | Seed 13 | Shared seed without claiming identical stochastic trajectories |
| **DataLoader Workers** | **4 Multi-Processing Workers** | 4 Workers | 4 Workers | 4 Workers | Prevents CPU-to-GPU data starvation |
| **Training remainder policy** | Model-specific | `drop_last=false` | `drop_last=false` | `drop_last=true` | D-FINE drops seven frames per epoch; disclosed fairness limitation |
| **Optimizer Family** | Benchmark-Pinned Recipe | SGD (`momentum=0.937`) | SGD (`momentum=0.937`) | AdamW | Explicit benchmark choice |
| **Base LR & Weight Decay** | Benchmark-Pinned Recipe | `lr0=0.01, wd=0.0005` | `lr0=0.01, wd=0.0005` | `lr=0.00025, backbone_lr=0.0000125, wd=0.0001` | Explicit values; not unchanged upstream defaults |
| **LR Schedule** | Model-Specific Pinned Recipe | ⭕ Ultralytics linear decay | ⭕ Ultralytics linear decay | ⭕ D-FINE `MultiStepLR` (milestone 500) | Exact schedule from each pinned backend |
| **Data Augmentation** | Model-Specific Pinned Recipe | ⭕ Mosaic, HSV, flips (`mixup=0`) | ⭕ Mosaic, HSV, flips (`mixup=0`) | ⭕ Photometric, zoom-out, crop, flips; fixed 640 | Preserves the exact pinned-backend pipeline |
| **Training-stage restart** | Model-specific | None | None | Best stage-1 checkpoint reloaded at epoch 148 by the pinned solver | D-FINE receives a validation-guided trajectory intervention |
| **Final Model Selection** | **Shared validation ranking** | Peak Val mAP | Peak Val mAP | Peak Val mAP | mAP50:95, then mAP50, then later epoch; test isolated |

</div>

---

## 3. Execution Commands

```bash
# Omit --execute-training to inspect the immutable plan without training.
python scripts/train_yolo.py --model-id yolo11n --execute-training
python scripts/train_yolo.py --model-id yolo26n --execute-training
python scripts/train_dfine.py --execute-training
```

All epoch, physical-batch, image-size, seed, AMP, checkpoint-frequency, and early-stopping controls are locked in configuration rather than exposed as casual CLI overrides. Accumulation semantics and D-FINE's stage transition remain backend-specific and are disclosed above. See [benchmark readiness](./benchmark-readiness.md) for the guarded post-training lifecycle and [fairness audit](./fairness.md) for interpretation limits.
