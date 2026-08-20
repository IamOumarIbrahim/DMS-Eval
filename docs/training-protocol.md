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

## 2. Shared Training Controls

<div align="center">

<sub><b>Table 1.</b> Frozen shared training controls across all three evaluated architectures.</sub>

| Training Parameter | 🧊 Frozen Rule / Value | Scientific Rationale |
| :--- | :--- | :--- |
| **Maximum Epochs** | `220` epochs for all models | Fixed compute budget matching D-FINE custom schedule |
| **Early Stopping** | Disabled | Ensures complete optimization trajectory without arbitrary halts |
| **Physical Mini-Batch** | `8` for all models | Comfortably fits inside RTX 4060 8 GB VRAM at 640×640 in FP16 |
| **Gradient Accumulation** | `4` steps (`nbs=32` / `accum=4`) | Effective batch 32; stabilizes BatchNorm and Hungarian bipartite matching |
| **Hardware Platform** | NVIDIA RTX 4060 (8 GB VRAM) | Standardized automotive edge / workstation GPU environment |
| **Training Precision** | Automatic Mixed Precision (FP16) | Standard Tensor Core acceleration; halves VRAM overhead |
| **Random Seed** | `13` across PyTorch, CUDA, loaders | Enforces deterministic data ordering and bitwise reproducibility |
| **DataLoader Workers** | `4` workers | Prevents CPU-to-GPU data starvation during streaming |

</div>

---

## 3. Architecture-Specific Optimization Recipes

<div align="center">

<sub><b>Table 2.</b> Controlled benchmark budget vs. architecture-native optimization recipes. (⭕ indicates model-specific variations).</sub>

| Parameter Dimension | Shared Controlled Policy | YOLO11n Recipe | YOLO26n Recipe | D-FINE-N Recipe |
| :--- | :--- | :---: | :---: | :---: |
| **Fine-Tuning Budget** | **220 Epochs** (No Early Stopping) | 220 Epochs | 220 Epochs | 220 Epochs |
| **Batch & Accumulation** | **Batch 8, Accum 4** (Effective 32) | Batch 8 (`nbs=32`) | Batch 8 (`nbs=32`) | Batch 8 (`accum=4`) |
| **Hardware & Seed** | **RTX 4060 GPU, Seed = 13** | RTX 4060, Seed 13 | RTX 4060, Seed 13 | RTX 4060, Seed 13 |
| **Training Precision** | **Automatic Mixed Precision (FP16)** | PyTorch AMP | PyTorch AMP | PyTorch AMP |
| **Optimizer Family** | Model-Specific Official Recipe | ⭕ SGD (`lr0=0.01, mom=0.937`) | ⭕ SGD (`lr0=0.01, mom=0.937`) | ⭕ AdamW (`lr=0.00025, wd=0.0001`) |
| **Learning Rate Schedule** | Model-Specific Official Recipe | ⭕ Linear / Cosine decay | ⭕ Linear / Cosine decay | ⭕ Step / Cosine annealing |
| **Data Augmentation** | Model-Specific Official Recipe | ⭕ Mosaic, Mixup, HSV, Flips | ⭕ Mosaic, Mixup, Flips | ⭕ Multi-scale, Crop, Flips |
| **Model Selection** | **Validation $\text{mAP}@0.5:0.95$ Checkpoint** | Peak Val mAP | Peak Val mAP | Peak Val mAP |

</div>

---

## 4. Execution Commands

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

