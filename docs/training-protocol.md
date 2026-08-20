# 🏋️ Training Protocol & Optimization Controls

[← Back to Main Landing Page](../README.md) · [Documentation Hub](./README.md) · [Evaluation Protocol](./evaluation-protocol.md) · [Pipeline Scripts](../scripts/README.md)

This authoritative protocol governs the model initialization, shared training constraints, hardware controls, and framework-native optimization recipes for the **DMS-Eval** benchmark.

---

## 🔒 Controlled-Comparison Principle

To establish an equitable benchmark without introducing artificial hyperparameter degradation, DMS-Eval enforces a clear separation:
1. **Shared Experimental Constraints:** Compute budget (220 epochs), nominal effective batch size (32), dedicated hardware (RTX 4060 GPU, 8 GB VRAM), precision (FP16 AMP), and random seed (13) are strictly locked across all candidate architectures.
2. **Architecture-Native Optimization Recipes:** Optimizers (SGD vs. AdamW), learning rate schedules, and augmentation pipelines are retained from each architecture's authoritative repository to evaluate each model under its intended optimization dynamics.

---

## 1. Initialization & Full-Model Fine-Tuning

- **Pretrained Initialization:** All models start from official pretrained checkpoint weights (`yolo11n.pt`, `yolo26n.pt`, `dfine_n.pt`). No models are trained from scratch.
- **Full-Model Fine-Tuning:** All backbone, neck, and detection head layers are fully trainable (0 frozen layers).
- **Single Training Run:** Exactly one full training trajectory per model is executed (Seed 13), reflecting deterministic single-run reproducibility under standard edge compute budgets.

---

## 2. Standardized Training Controls & Native Recipes

<div align="center">

<sub><b>Table 1.</b> Authoritative training specification: Shared benchmark controls vs. framework-native optimization recipes. (⭕ indicates model-specific variations).</sub>

| Parameter Dimension | Shared Controlled Benchmark Policy | Ultralytics YOLO11n Recipe | Ultralytics YOLO26n Recipe | D-FINE-N Recipe | Scientific Rationale |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Fine-Tuning Budget** | **220 Epochs** (No Early Stopping) | 220 Epochs | 220 Epochs | 220 Epochs | Fixed compute budget matching D-FINE schedule |
| **Mini-Batch Size** | **Physical Batch = 8** | Batch 8 | Batch 8 | Batch 8 | Comfortably fits RTX 4060 8 GB VRAM in FP16 |
| **Gradient Accumulation** | **4 Steps (Nominal Batch 32)** | `nbs=32` | `nbs=32` | `accum=4` | Stabilizes BatchNorm & Hungarian matching |
| **Hardware Platform** | **NVIDIA RTX 4060 (8 GB)** | RTX 4060 | RTX 4060 | RTX 4060 | Standardized automotive edge GPU environment |
| **Training Precision** | **Automatic Mixed Precision (FP16)** | PyTorch AMP | PyTorch AMP | PyTorch AMP | Halves VRAM overhead; standard Tensor Core mode |
| **Deterministic Seed** | **Seed = 13** across all frameworks | Seed 13 | Seed 13 | Seed 13 | Enforces deterministic data ordering |
| **DataLoader Workers** | **4 Multi-Processing Workers** | 4 Workers | 4 Workers | 4 Workers | Prevents CPU-to-GPU data starvation |
| **Optimizer Family** | Model-Specific Official Recipe | ⭕ SGD (`momentum=0.937`) | ⭕ SGD (`momentum=0.937`) | ⭕ AdamW | Preserves framework-native gradient dynamics |
| **Base LR & Weight Decay** | Model-Specific Official Recipe | ⭕ `lr0=0.01, wd=0.0005` | ⭕ `lr0=0.01, wd=0.0005` | ⭕ `lr=0.00025, wd=0.0001` | Official fine-tuning hyperparameters |
| **LR Schedule** | Model-Specific Official Recipe | ⭕ Linear / Cosine decay | ⭕ Linear / Cosine decay | ⭕ Step / Cosine annealing | Official decay schedule |
| **Data Augmentation** | Model-Specific Official Recipe | ⭕ Mosaic, Mixup, HSV, Flips | ⭕ Mosaic, Mixup, Flips | ⭕ Multi-scale, Crop, Flips | Preserves model-native augmentation pipeline |
| **Model Selection** | **Validation mAP@0.5:0.95 Checkpoint** | Peak Val mAP | Peak Val mAP | Peak Val mAP | 100% test-isolated model selection |

</div>

---

## 3. Execution Commands

```bash
# 1. Train Ultralytics YOLO11n (220 Epochs, Physical Batch 8, Accum 4)
python scripts/train_yolo.py \
  --model weights/pretrained/yolo11n.pt \
  --data configs/yolo/dms_eval.yaml \
  --epochs 220 \
  --batch 8 \
  --accumulate 4 \
  --imgsz 640 \
  --seed 13 \
  --amp \
  --name yolo11n_dms

# 2. Train Ultralytics YOLO26n (220 Epochs, Physical Batch 8, Accum 4)
python scripts/train_yolo.py \
  --model weights/pretrained/yolo26n.pt \
  --data configs/yolo/dms_eval.yaml \
  --epochs 220 \
  --batch 8 \
  --accumulate 4 \
  --imgsz 640 \
  --seed 13 \
  --amp \
  --name yolo26n_dms

# 3. Train D-FINE-N (220 Epochs, Physical Batch 8, Accum 4)
python -m torch.distributed.run --nproc_per_node=1 train.py \
  -c configs/dfine/dfine_n_dms.yml \
  --amp
```

