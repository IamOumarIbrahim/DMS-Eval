# DMS-Eval: Resource Budget & Feasibility Check

**Milestone:** M0 — Scope Lock (16 Aug 2026)  
**Target Deadline:** 31 August 2026 (~15 days remaining)  
**Author / Assignee:** [@IamOumarIbrahim](https://github.com/IamOumarIbrahim)

---

## 1. Hardware & Compute Specifications

| Component | Specification | Operational Limits & Risk Controls |
| :--- | :--- | :--- |
| **GPU** | NVIDIA GeForce RTX 4060 (8 GB VRAM) | Memory constrained for transformer-based / larger attention heads. Microbatch size to be determined experimentally per architecture; use gradient accumulation to maintain a uniform effective batch size. |
| **Storage Available** | **200+ GB** (SSD) | Sufficient for raw datasets, sampled frames, caches, checkpoints, and evaluation artifacts. |
| **Compute Type** | Local dedicated workstation | Full control over scheduling; supports unattended overnight execution. |

---

## 2. Training Strategy & Methodology Decision

- **Primary Benchmark:** **Full-network fine-tuning** initialized from comparable **official COCO-pretrained detection checkpoints**.
- **Definition:** All network weights are updated during training (not backbone-frozen), with classification heads reinitialized for the target canonical DMS ontology.
- **Rationale:**
  1. Matches realistic edge/automotive deployment where practitioners adapt proven lightweight backbones.
  2. Ensures stable convergence within the 15-day timeline and avoids architecture-specific scratch hyperparameter bias.
  3. Conserves compute budget for **three seeds**, ablation/subgroup profiling, and statistical uncertainty modeling.
- **Scratch Training Policy:** Random-initialization training from scratch is **out of scope** for the primary paper and deferred to optional post-submission/exploratory analysis.

---

## 3. Recommended Experiment Design

| Component | Specification / Policy |
| :--- | :--- |
| **Model Shortlist** | **YOLO11n, YOLO12n Turbo, D-FINE-N, YOLO26n** (Lightweight parameter regime ~2.4–4.0M) |
| **Initialization** | Official COCO-pretrained detection checkpoints across all models (no mixed Objects365 pretraining) |
| **Output Heads** | Reinitialized/adapted for the frozen canonical DMS class ontology |
| **Trainable Params** | Full-network adaptation (all layers unfrozen) |
| **Seeds & Repetitions** | **3 seeds per model** ($4 \times 3 = 12$ primary training runs) |
| **Contingency Slots** | **4 additional run slots** reserved for unexpected failures or gradient instabilities |
| **Batch Policy** | Architecture-specific microbatch (to fit 8 GB VRAM) with gradient accumulation to a common effective batch size |
| **Precision** | AMP (Automatic Mixed Precision / FP16) where numerically stable |
| **Epoch / Early Stopping** | Common maximum epoch ceiling + identical patience early-stopping rule (calibrated via M3/M4 pilot runs) |
| **Checkpoint Selection** | Best validation checkpoint selected strictly under one pre-registered primary validation metric |
| **Test Set Contract** | Single-pass evaluation on frozen test partition only after all checkpoints and thresholds are locked |
| **Uncertainty Reporting** | Mean $\pm$ SD across seeds + driver/session-clustered bootstrap confidence intervals |

---

## 4. Storage & Compute Time Budget

### Storage Allocation Budget
| Data Category | Estimated Size | Status |
| :--- | :---: | :--- |
| **Raw Datasets (DMD / NTHU / Fallback)** | ~25 – 40 GB | Download & archive storage |
| **Processed Manifests & Extracted Frames** | ~15 – 30 GB | Deterministic frame subsets ($640 \times 640$) |
| **Model Weights & Pretrained Checkpoints** | ~2 – 5 GB | Upstream baselines & checkpoints |
| **Training Run Artifacts (Logs, CSVs, Plots)** | ~5 – 10 GB | Run logs, checkpoints, TensorBoard |
| **Total Storage Required** | **~50 – 85 GB** | 🟢 **GREEN** (Comfortably within 200+ GB available) |

### Compute Duration & Runway Budget
- **Raw Training Duration:** To be measured empirically via two pilot runs:
  - 1 CNN-based pilot (**YOLO11n**)
  - 1 DETR/Transformer-based pilot (**D-FINE-N**)
- **Overhead Multiplier:** Total GPU allocation planned at **$2.5\times$ raw training duration** to account for validation passes, export profiling (ONNX/TensorRT), data caching, and metric computations.
- **Run Budget:** **12 primary runs + 4 contingency slots = 16 total runs maximum**.

---

## 5. Human Availability Budget

- **Daily Working Window:** **6+ hours / day**
- **Total Human Runway:** **~90 – 100 person-hours** across the 15-day timeline (16–31 Aug 2026).
- **Execution Phases:**
  - **M0–M1 (16–18 Aug):** Scope, Dataset Acquisition & Benchmark Protocol (~18h)
  - **M2–M4 (19–22 Aug):** Repo Setup, Adapters, Profiler, Pilot Runs & Data Pipeline (~24h)
  - **M5 (23–26 Aug):** 12 Controlled Training Runs & Statistical Aggregations (~24h)
  - **M6 (27–29 Aug):** Analysis, Pareto Plots, Subgroup Breakdowns & Manuscript (~20h)
  - **M7–M8 (30–31 Aug):** Reproduction Audit, Validation & Submission (~10h)

---

## 6. Feasibility Verdict

> **Resource Status: 🟡 CONDITIONAL / APPROVED FOR PRETRAINED FULL-NETWORK FINE-TUNING**

**Rationale:**
Storage and human availability are fully green. However, per-architecture training duration, usable microbatch sizes, and VRAM overhead on the 8 GB GPU must be empirically validated via one YOLO and one D-FINE pilot run before declaring the compute matrix unconditionally green. Random-initialization training from scratch is excluded from the primary submission scope.
