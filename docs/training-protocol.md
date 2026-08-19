# Training Protocol

[← Back to the DMS-Eval landing page](../README.md) · [Execution Checklist](./execution-checklist.md)

> [!NOTE]
> This document contains protocol information extracted from the DMS-Eval README. Frozen decisions and unresolved values retain their original status.

> **Jump to:** [Shared controls](#shared-training-controls) · [Initialization and recipes](#initialization--fine-tuning) · [Removed deterministic requirement](#removed)

- [x] Official pretrained initialization and full-model fine-tuning are frozen.
- [x] Model-specific optimizer, learning rate, schedule, weight decay, and augmentation are retained.
- [x] Shared training-control rules are documented.
- [x] Maximum epochs, shared seed, AMP training policy, and worker count are frozen.

---
 
### 🧊 Frozen

> Shared training controls are frozen where architectural fairness requires a common rule. Architecture-specific optimization behavior remains model-specific where forcing one recipe across fundamentally different model families could unfairly disadvantage a model.

<details>
<summary><strong>Show initialization, fine-tuning, and model-specific recipe rules</strong></summary>

#### Initialization & Fine-Tuning

* **YOLO11n, D-FINE-N, and YOLO26n start from their official pretrained weights.**
* The models are **not trained from scratch**.
* All three models use **full-model fine-tuning** on the DMS-Eval training split.
* **No pretrained layers are intentionally frozen.**
* The pretrained starting points are **not assumed to be identical across architectures**. Their original pretraining datasets/setups may differ and must be documented transparently as part of the benchmark's reproducibility record and limitations.

#### Model-Specific Training Recipe

* Each model uses its **official/model-specific recommended training recipe**, except where DMS-Eval explicitly freezes a shared training control below.
* DMS-Eval does **not** force one common optimizer, learning rate, learning-rate schedule, weight decay, or augmentation policy across all architectures.
* **Data augmentation remains part of each model's official/model-specific training recipe.**
* The actual training settings used for each model must be **recorded and reported for reproducibility**.

</details>

#### Shared Training Controls

<p align="center"><sub><b>Table 1.</b> Shared training controls.</sub></p>

| Training Parameter | 🧊 Frozen Rule |
| :--- | :--- |
| **Maximum training epochs** | `220` for all three models |
| **Early stopping** | Disabled for all three models |
| **Batch size** | `1` for all three models |
| **Gradient accumulation** | Disabled; one image produces one weight update before moving to the next image |
| **Training runs** | One training run per model; no multi-seed averaging |
| **Random seed** | `13` for all three models wherever the shared benchmark seed applies |
| **Training hardware** | NVIDIA RTX 4060 with 8 GB VRAM for all three models |
| **Training precision** | Automatic Mixed Precision (AMP) for all three models, using each model/framework's official AMP implementation |
| **Data-loader workers** | `4` for all three models |

> [!IMPORTANT]
> The final checkpoint for each model is selected on validation data using the shared DMS-Eval evaluator. The test split is not used for checkpoint selection, and the epoch-220 checkpoint is not automatically selected.

> [!NOTE]
> The shared AMP training precision policy does not imply that every operation is literally executed in FP16. Each model uses its framework's official AMP implementation. Full-model fine-tuning and architecture-specific training recipes remain unchanged.

<p align="center"><sub><b>Table 2.</b> Controlled benchmark budget vs. architecture-specific training recipes.</sub></p>

| Parameter Dimension | Shared Controlled Benchmark Policy | YOLO11n / YOLO26n Recipe | D-FINE-N Recipe |
| :--- | :--- | :--- | :--- |
| **Fine-Tuning Budget** | **220 Epochs** (Early stopping disabled) | 220 Epochs | 220 Epochs |
| **Batch Size & Accumulation** | **Batch size = 1**, Gradient accumulation = 0 | Batch size = 1 | Batch size = 1 |
| **Random Seed & Hardware** | **Seed = 13**, Dedicated NVIDIA RTX 4060 GPU | Seed = 13, RTX 4060 | Seed = 13, RTX 4060 |
| **Numerical Precision** | **Automatic Mixed Precision (FP16 AMP)** | PyTorch AMP (Ultralytics) | PyTorch AMP (D-FINE) |
| **Optimizer Family** | Model-Specific Official Recipe | SGD (`lr0=0.01, momentum=0.937`) | AdamW (`lr=0.00025, weight_decay=0.0001`) |
| **Learning Rate Schedule** | Model-Specific Official Recipe | Linear / Cosine LR Decay | Step / Cosine Annealing |
| **Data Augmentation** | Model-Specific Official Recipe | Mosaic, Mixup, HSV, Flips | Multi-scale jitter, Random Crop, Flips |
| **Model Selection** | **Validation-Only $F_1$ Score Sweep** | Validation $F_1$ Sweep ($\tau^*$) | Validation $F_1$ Sweep ($\tau^*$) |

---

<details>
<summary><strong>Show removed deterministic requirement</strong></summary>

### Removed

* **Mandatory framework-level deterministic training mode** is not required.
* The shared random seed remains frozen, but strict bitwise-identical reruns are not required.

</details>

---

## ⚠️ Resolve Later Checklist

<div align="center">

| Status | Item / Open Decision | Protocol Role | Target Resolution Milestone |
| :---: | :--- | :--- | :--- |
| [ ] | **Validation Confidence Thresholds ($\tau^*$)** | Numerical threshold values $(\tau_{\text{YOLO11n}}, \tau_{\text{D-FINE-N}}, \tau_{\text{YOLO26n}})$ selected via validation $F_1$ sweep | [Module 4.3](./execution-checklist.md#module-4-shared-evaluation-harness--validation-model-selection) |
| [ ] | **Host Environment Manifest Pinning** | Exact pinned versions for CUDA, cuDNN, PyTorch, Ultralytics commit, D-FINE commit, and THOP | [Module 3.1](./execution-checklist.md#module-3-environment-configuration--controlled-model-training) |
| [ ] | **Custom / Unsupported Operator Profiling** | Local operator handler audit for THOP GFLOPs computation ($1 \times 3 \times 640 \times 640$) | [Module 5.2](./execution-checklist.md#module-5-computational-complexity--footprint-profiling) |
| [ ] | **Non-Integer FPS Frame Mapping** | Exact frame-index rounding rule for source video extraction at non-integer framerates | [Module 1.1](./execution-checklist.md#module-1-data-pipeline--annotation-integrity) |
| [ ] | **Checkpoint Storage Measurement** | Uniform disk footprint measurement protocol (MB) for final selected model weights | [Module 5.3](./execution-checklist.md#module-5-computational-complexity--footprint-profiling) |

</div>
