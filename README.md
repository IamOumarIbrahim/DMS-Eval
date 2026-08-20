<h1 align="center">DMS-Eval: Real-Time Driver Behavior Detection Using Lightweight Object Detection Models with Subject-Disjoint Evaluation</h1>

<p align="center">
  <strong>An empirical benchmark comparing sub-5M parameter YOLO and DETR architectures for frame-level in-cabin driver monitoring</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Status-In_Development-orange?style=flat" alt="Status: In Development">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg" alt="License: Apache 2.0"></a>
  <img src="https://img.shields.io/badge/Input-640%C3%97640-555?style=flat" alt="Input: 640×640">
  <img src="https://img.shields.io/badge/Detectors-YOLO%20%7C%20DETR-4c1?style=flat" alt="Detectors: YOLO | DETR">
  <img src="https://img.shields.io/badge/Hardware-NVIDIA%20RTX%204060-76b900?style=flat&logo=nvidia" alt="Hardware: RTX 4060">
</p>

<p align="center">
  <a href="https://raw.githubusercontent.com/IamOumarIbrahim/DMS-Eval/main/manuscript/main.pdf" download="DMS-Eval-Manuscript.pdf">
    <img src="https://img.shields.io/badge/📄_Full_Manuscript-Read_PDF_here-e02424?style=for-the-badge&logo=adobeacrobatreader&logoColor=white" alt="Read PDF here">
  </a>
</p>

<p align="center">
  <strong><a href="https://raw.githubusercontent.com/IamOumarIbrahim/DMS-Eval/main/manuscript/main.pdf" download="DMS-Eval-Manuscript.pdf">Read Full Conference Manuscript (PDF)</a></strong> · <strong><a href="./docs/README.md">Documentation Suite</a></strong> · <strong><a href="./scripts/README.md">Pipeline Scripts</a></strong>
</p>

---

## 📑 Table of Contents
- [Abstract](#abstract)
- [🚀 Quick Start & Reproducibility](#-quick-start--reproducibility)
  - [1. Environment Setup](#1-environment-setup)
  - [2. Dataset Extraction & Preprocessing Pipeline](#2-dataset-extraction--preprocessing-pipeline)
  - [3. Model Training One-Liners](#3-model-training-one-liners)
  - [4. Threshold Calibration & Evaluation](#4-threshold-calibration--evaluation)
- [1. Introduction & Benchmark Scope](#1-introduction--benchmark-scope)
  - [1.1 Research Gap](#11-research-gap)
  - [1.2 Key Contributions](#12-key-contributions)
  - [1.3 Research Question](#13-research-question)
- [2. Dataset Formulation & Annotation Protocol](#2-dataset-formulation--annotation-protocol)
  - [2.1 Source Video Corpus & Spatial Window](#21-source-video-corpus--spatial-window)
  - [2.2 Target Warning Cue Ontology](#22-target-warning-cue-ontology)
  - [2.3 Single-Annotation Policy & Negative Sample Richness](#23-single-annotation-policy--negative-sample-richness)
- [3. Methodology & Subject-Disjoint Partitioning](#3-methodology--subject-disjoint-partitioning)
  - [3.1 Strict Subject-Disjoint Partitioning Principle](#31-strict-subject-disjoint-partitioning-principle)
  - [3.2 Authoritative Combinatorial Optimization](#32-authoritative-combinatorial-optimization)
  - [3.3 Verified Dataset Partition Statistics](#33-verified-dataset-partition-statistics)
- [4. Evaluated Detector Architectures](#4-evaluated-detector-architectures)
- [5. Experimental Setup & Master Benchmark Control Matrix](#5-experimental-setup--master-benchmark-control-matrix)
- [6. Validation Calibration & Isolated Test Evaluation](#6-validation-calibration--isolated-test-evaluation)
- [7. Comparative Results Framework](#7-comparative-results-framework)
- [8. Repository Structure & Documentation Hub](#8-repository-structure--protocol-documentation)
- [Authors, Citation & License](#authors--citation)

---

## Abstract

Driver Monitoring Systems (DMS) are critical safety components of modern Advanced Driver Assistance Systems (ADAS). Automotive edge deployments motivate lightweight, low-latency detectors that localize warning cues in individual frames. **DMS-Eval** is a reproducible empirical benchmark of compact convolutional detectors (**Ultralytics YOLO11n** and **YOLO26n**) and a lightweight Real-Time Detection Transformer (**D-FINE-N**). It uses 15,723 manually annotated $640 \times 640$ frames derived from 81 driver-facing DMD recordings across 14 subjects, with four warning cues and 12,722 naturalistic negative frames. A frozen 8/3/3 subject-disjoint split prevents identity leakage. All models use the same data/classes, resolution, physical batch 8, fixed accumulation 4, 220 epochs, disabled early stopping, three predeclared training seeds (13, 37, 73), shared evaluator, RTX 4060 environment gate, FP32 model/input storage under CUDA AMP FP16, batch-1 timing protocol, and protected test policy. Every seed is reported and per-model results use mean ± sample SD; best-run selection is prohibited. Architecture-specific optimization and augmentation settings follow pinned official recipes; the closed adaptation list is dataset/classes, 640×640 input, batch 8, accumulation 4, 220 epochs, the three training seeds, and disabled early stopping. Results remain pending until authorized frozen runs are completed.

<p align="center">
  <img src="./assets/diagrams/dms_eval_pipeline.png" alt="DMS-Eval End-to-End Benchmark Framework" width="880"><br>
  <sub><b>Figure 1.</b> DMS-Eval end-to-end benchmark framework and evaluation lifecycle: from naturalistic DMD video extraction and authoritative Label Studio annotation through deterministic 8/3/3 subject-disjoint partitioning, controlled three-seed model training, validation calibration ($\tau^*$), and one isolated test pass per frozen model–seed run.</sub>
</p>

---

## 🚀 Quick Start & Reproducibility

### 1. Environment Setup

```bash
# Clone the benchmark repository
git clone https://github.com/IamOumarIbrahim/DMS-Eval.git
cd DMS-Eval

# Create and synchronize the exact frozen Windows/Python 3.12 environment
uv venv --python 3.12.10 .venv
uv pip sync --python .venv\Scripts\python.exe requirements.lock.txt
```

> [!IMPORTANT]
> The frozen benchmark environment is an NVIDIA RTX 4060 (8 GB), CUDA FP16, and Python 3.12.10. Training launchers reject a nonmatching device and remain dry-runs unless the explicit execution gate is supplied.

### 2. Dataset Extraction & Preprocessing Pipeline

```bash
# Read-only full preflight (including all 15,723 image decodes and content hashes)
python scripts/benchmark/preflight.py

# Verify pinned model checkouts, weights, and synthetic FP16 inference
python scripts/benchmark/setup_backends.py
python scripts/benchmark/validate_backends.py --synthetic
```

The protected master annotations and split are already frozen. Conversion scripts only regenerate deterministic derived YOLO and D-FINE artifacts; extraction refuses non-empty output directories and resolves duplicate source recordings deterministically.

Derived adapter formats are verified against real loader behavior: YOLO lists resolve from `dataset/yolo` to canonical `dataset/images/...` files, while D-FINE's derived COCO uses paths relative to its configured `dataset/images` root and contiguous internal labels 0–3. Both adapters return the authoritative evaluator category IDs 1–4.

### 3. Model Training One-Liners

All models use **physical batch size 8**, **fixed four-step accumulation** (effective batch 32), FP16 AMP, disabled early stopping, and 220 epochs on the RTX 4060 for each of the fixed seeds **13, 37, and 73**. Every image is retained and incomplete accumulation windows are sample-correct.

```bash
# Train Ultralytics YOLO11n, seed 13 (repeat identically for --seed 37 and --seed 73)
python scripts/benchmark/train_yolo.py --model-id yolo11n --seed 13 --execute-training

# Train Ultralytics YOLO26n
python scripts/benchmark/train_yolo.py --model-id yolo26n --seed 13 --execute-training

# Train D-FINE-N (Real-Time Detection Transformer)
python scripts/benchmark/train_dfine.py --seed 13 --execute-training
```

### 4. Threshold Calibration & Evaluation

```bash
# Safe default: fingerprinted protocol dry-run only
python scripts/benchmark/evaluate_benchmark.py
```

Checkpoint selection, calibration, freeze, protected test, aggregation, and publication commands are documented in [`docs/benchmark-readiness.md`](docs/benchmark-readiness.md). There is intentionally no casual test-split command.

---

## 1. Introduction & Benchmark Scope

In-cabin Driver Monitoring Systems (DMS) aim to prevent roadway collisions through early visual detection of driver drowsiness and inattention. While high-level driver state assessment frequently leverages complex multi-frame temporal models, automotive edge deployments impose strict constraints on compute, on-chip SRAM, and per-frame latency. Consequently, there is an urgent practical demand for lightweight 2D object detectors capable of real-time single-frame inference on embedded automotive hardware.

### 1.1 Research Gap
Despite substantial progress in driver monitoring, reproducible head-to-head evidence for nano-scale convolutional and Real-Time Detection Transformer systems remains limited for in-cabin cue localization under subject-disjoint data, shared hardware, and a protected evaluation protocol. DMS-Eval addresses four practical gaps:
1. **Classification without spatial localization:** Previous benchmarks classify full images into posture categories without bounding boxes localizing specific objects or facial cues. Spatial localization is essential for downstream tracking and alert subsystems.
2. **Multi-stage pipelines with compounding latency:** Chaining detectors with pose estimators and recurrent LSTM networks introduces multi-model latency penalties that preclude real-time edge execution.
3. **Single-family evaluations:** Lightweight CNN detectors and real-time DETRs are benchmarked exclusively on general-purpose COCO datasets and never compared against each other within the in-cabin DMS domain.
4. **Absent evaluation rigor:** Many prior studies use random frame-level splits (introducing identity leakage) and report theoretical GFLOPs or large-batch throughput rather than batch-size-1 latency.

### 1.2 Key Contributions
- **Cross-Paradigm Nano-Scale DMS Benchmark:** A controlled system-level comparison of nano-scale CNNs (YOLO11n, YOLO26n) and a nano-scale DETR (D-FINE-N) for spatial in-cabin warning-cue localization.
- **Rigorous Subject-Disjoint Data Curation:** 15,723 frames ($640\times640$) with 100% manual annotation across 4 warning cues and 80.91% naturalistic negatives, partitioned via exhaustive combinatorial optimization ($\le 5.48\%$ divergence).
- **Unified Precision–Efficiency Protocol:** Shared RTX 4060 hardware, physical batch 8, fixed accumulation 4, 220 epochs, FP32 model/input storage under CUDA AMP FP16, and batch-1 model-forward plus tensor-to-final-detections latency ($p50/p95/p99$).
- **Open Reproducibility:** Public release of all COCO annotations, partitioning scripts, configuration recipes, and evaluation tooling.

### 1.3 Research Question

> [!NOTE]
> **Core Benchmark Research Question (RQ):**
> *Under a subject-disjoint shared-data and shared-hardware protocol, how do three sub-5M-parameter detector systems compare in detection quality, model-forward and tensor-to-final-detections latency, resource demand, and false-alarm suppression for spatial driver-monitoring warning cues?*

---

## 2. Dataset Formulation & Annotation Protocol

### 2.1 Source Video Corpus & Spatial Window
The benchmark is constructed from the Driver Monitoring Dataset (DMD), recorded in real vehicle cabins under variable daylight and ambient lighting conditions. The dataset encompasses 14 human subjects ($S_1\text{--}S_{14}$) across 68 distinct driving sessions, recorded as 81 driver-facing RGB video sequences ($\approx 29.76$ FPS) across three behavioral domains: `distraction`, `drowsiness`, and `gaze`.

To eliminate background noise outside the driver's operational workspace while preserving high spatial fidelity for fine-grained cues, every frame is uniformly sampled at 1 FPS and cropped to a standardized $640 \times 640$ pixel spatial bounding window ($x = 272, y = 71, w = 640, h = 640$) without letterboxing, border padding, or non-uniform aspect ratio distortion. This yields exactly **15,723 standardized images**.

```text
dataset/
├── images/
│   ├── subject_01/
│   │   ├── video_01/
│   │   └── ...
│   └── ...
├── annotations.json                          # Authoritative master COCO ground truth
├── splits.json                               # Frozen 8/3/3 subject-disjoint partitions
└── preprocessing.json                        # Frozen spatial crop geometry (272, 71, 640, 640)
```

### 2.2 Target Warning Cue Ontology
Ground truth is generated through 100% manual human inspection in Label Studio with format conversion managed via `label-studio-converter`. Bounding box boundaries are defined with strict anatomical extents:
- **`phone_use` (ID 4):** Encloses the handheld mobile device and interacting hand held to the ear/head in calling posture.
- **`drinking` (ID 3):** Encloses the interacting hand and the beverage container together during active consumption posture.
- **`yawning` (ID 1):** Encloses only the active mouth aperture during wide distension. Head and cheeks are excluded to prevent confusing open-mouth speech with yawning.
- **`hand_over_mouth` (ID 2):** Encloses the full head and face including the occluding hand when placed over the mouth area.

<p align="center">
  <img src="./assets/examples/phone_use_annotation_example.png" alt="phone_use annotation" width="180">
  <img src="./assets/examples/drinking_annotation_example.png" alt="drinking annotation" width="180">
  <img src="./assets/examples/yawning_annotation_example.png" alt="yawning annotation" width="180">
  <img src="./assets/examples/hand_over_mouth_annotation_example.png" alt="hand_over_mouth annotation" width="180"><br>
  <sub><b>Figure 2.</b> Authoritative ground-truth manual annotations in Label Studio across the 4 frozen target warning cues: <code>phone_use</code> (pink box), <code>drinking</code> (blue box), <code>yawning</code> (orange box), and <code>hand_over_mouth</code> (purple box).</sub>
</p>

### 2.3 Single-Annotation Policy & Negative Sample Richness

> [!IMPORTANT]
> **Strict Single-Annotation Policy ($\le 1$ label/frame):**
> Each sampled frame contains at most one bounding box annotation. In particular, `yawning` and `hand_over_mouth` are strictly mutually exclusive: if a driver yawns while a hand covers the mouth, the instance is uniquely labeled as `hand_over_mouth` (full head/face).

> [!WARNING]
> **Deliberate Cue Exclusions (`head_turned_away`, `eyes_closed`):**
> Drivers perform frequent, safe mirror glances during routine driving; in static 1 FPS frames without 3D gaze tracking, safe glances cannot be distinguished from prolonged inattention. Similarly, single-frame blink detection produces unacceptable false alarms on natural physiological blinks without multi-frame temporal modeling.

- **Naturalistic Negative Frames (80.91%):** Incorporating all three DMD session folders (`distraction`, `drowsiness`, and `gaze`) supplies **12,722 true negative background frames (80.91%)** alongside **3,001 positive cue frames (19.09%)**, training detectors to suppress false alarms during alert driving.

<p align="center">
  <img src="./assets/charts/benchmark_distributions_combined.png" alt="Dataset Frame Composition and Cue Distribution" width="880"><br>
  <sub><b>Figure 3.</b> Benchmark ground-truth distributions: (a) Frame-level composition across all 15,723 frames (80.91% negative background vs. 19.09% positive cue frames); (b) Annotation distribution across the 4 frozen warning cues (2,437 <code>phone_use</code>, 264 <code>drinking</code>, 159 <code>yawning</code>, 141 <code>hand_over_mouth</code>).</sub>
</p>

---

## 3. Methodology & Subject-Disjoint Partitioning

### 3.1 Strict Subject-Disjoint Partitioning Principle
To eliminate identity leakage, the 14 participants are partitioned into 8 Training, 3 Validation, and 3 Test subjects such that no individual appears in more than one partition:
$$S_{\text{train}} \cap S_{\text{val}} = \emptyset, \quad S_{\text{train}} \cap S_{\text{test}} = \emptyset, \quad S_{\text{val}} \cap S_{\text{test}} = \emptyset$$

> [!CAUTION]
> **Zero Identity Leakage Requirement:**
> Splitting datasets at the random frame level introduces massive biometric identity leakage between training and testing sets, creating artificially inflated accuracy numbers that collapse in real-world deployment. DMS-Eval enforces strictly subject-disjoint whole-participant partitions.

### 3.2 Authoritative Combinatorial Optimization
Because volunteer participants exhibit varying behavioral frequencies, random assignment leads to severe class imbalance. We formalize an authoritative selection rule implemented in [`scripts/data/balance_splits.py`](./scripts/data/balance_splits.py):

> **Authoritative Selection Objective:** *Select the 8/3/3 subject split whose negative/positive frame proportion and four class proportions most closely match the complete dataset distribution.*

The algorithm exhaustively evaluates all $\binom{14}{8} \times \binom{6}{3} = 3003 \times 20 = 60,060$ candidate partitions. For each partition $\mathcal{P}$ and split $s \in \{\text{train}, \text{val}, \text{test}\}$, relative deviations across 5 quantities $\mathcal{Q} = \{\text{pos-rate}, \text{phone}, \text{drinking}, \text{yawning}, \text{hand-over-mouth}\}$ are minimized:
$$\text{Dev}(q, s) = \frac{\lvert V(q, s) - V_{\text{global}}(q) \rvert}{V_{\text{global}}(q)}$$

$$\mathcal{P}^* = \arg\min_{\mathcal{P} \in \Omega} \left( \max_{q \in \mathcal{Q}, s \in \mathcal{S}} \text{Dev}(q, s), \quad \text{RMSE}(\mathcal{P}), \quad \text{Dev}_{\text{test}}(\mathcal{P}) \right)$$

### 3.3 Verified Dataset Partition Statistics
The optimal assignment is permanently frozen in [`dataset/splits.json`](./dataset/splits.json):
- **Train ($S_{\text{train}}$ — 8 subjects):** `subject_01`, `subject_04`, `subject_06`, `subject_07`, `subject_08`, `subject_09`, `subject_13`, `subject_14` (shuffled with seed 13)
- **Validation ($S_{\text{val}}$ — 3 subjects):** `subject_02`, `subject_03`, `subject_11` (chronological order)
- **Test ($S_{\text{test}}$ — 3 subjects):** `subject_05`, `subject_10`, `subject_12` (chronological order)

<div align="center">

<sub><b>Table 1.</b> Verified dataset split composition and warning cue distributions across 8/3/3 subject-disjoint partitions.</sub>

| Split | Subjects | Total Frames | Negative Frames (0 boxes) | Positive Frames (1 box) | `phone_use` | `drinking` | `yawning` | `hand_over_mouth` | Max Relative Dev. |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Global** | **14** | **15,723** | **12,722 (80.91%)** | **3,001 (19.09%)** | **2,437 (81.21%)** | **264 (8.80%)** | **159 (5.30%)** | **141 (4.70%)** | — |
| **Train (S_train)** | 8 | 9,087 | 7,339 (80.76%) | 1,748 (19.24%) | 1,417 (81.06%) | 154 (8.81%) | 94 (5.38%) | 83 (4.75%) | ≤ 1.48% |
| **Val (S_val)** | 3 | 3,423 | 2,784 (81.33%) | 639 (18.67%) | 523 (81.85%) | 54 (8.45%) | 32 (5.01%) | 30 (4.69%) | ≤ 5.48% |
| **Test (S_test)** | 3 | 3,213 | 2,599 (80.89%) | 614 (19.11%) | 497 (80.94%) | 56 (9.12%) | 33 (5.37%) | 28 (4.56%) | ≤ 3.68% |

</div>

<p align="center">
  <img src="./assets/charts/split_cue_proportions_comparison.png" alt="Split Cue Proportions Comparison" width="880"><br>
  <sub><b>Figure 4.</b> Proportional warning cue alignment across Training, Validation, and Testing partitions (≤ 5.48% maximum relative divergence from global dataset distribution).</sub>
</p>

---

## 4. Evaluated Detector Architectures

We benchmark three state-of-the-art nano-scale real-time object detector architectures operating below 5M parameters:

<div align="center">

<sub><b>Table 2.</b> Candidate real-time detector architectures evaluated in DMS-Eval.</sub>

| Model Architecture | Architectural Family | Pinned COCO Params | Setup-only THOP estimate (640×640) | Detection Paradigm / Key Feature | Repository Source |
| :--- | :---: | :---: | :---: | :--- | :---: |
| **Ultralytics YOLO11n** | Single-Stage CNN | 2.624 M | 6.612 G | C3k2 feature extractors & SPPF modules; optimizes CIoU + BCE + DFL | [Ultralytics](https://github.com/ultralytics/ultralytics) |
| **Ultralytics YOLO26n** | End-to-End CNN | 2.572 M | 6.117 G | Anchor-free, NMS-free direct bounding box prediction via dual-label assignment | [Ultralytics](https://github.com/ultralytics/ultralytics) |
| **D-FINE-N** | Real-Time DETR | 3.724 M | 7.436 G | HGNetv2 backbone with Fine-grained Distribution Refinement (FDR) & Hungarian set loss | [D-FINE](https://github.com/Peterande/D-FINE) |

</div>

These are setup-only diagnostics of pinned COCO checkpoints and are not benchmark results. Final four-class artifacts report both THOP and `torch.profiler` estimates with operator-coverage caveats.

---

## 5. Experimental Setup & Benchmark Controls

DMS-Eval holds the data/classes, subject split, resolution, annotations, physical batch, fixed accumulation, epoch/data exposure, three training seeds (13, 37, 73), early-stopping rule, hardware, precision policy, evaluator, checkpoint rule, and protected test access constant. Architecture-specific optimizer, scheduler, weight decay, and augmentation settings follow pinned official recipes. The only recipe adaptations are dataset/classes, 640×640 input, batch 8, accumulation 4, 220 epochs, the three training seeds, and disabled early stopping; no model-specific tuning is performed and no run is selected as "best."

> [!IMPORTANT]
> **Controlled Training & Gradient Dynamics:**
> Training uses physical mini-batch 8 and fixed four-step accumulation from the first batch under FP16 AMP. `drop_last=false` applies to all models, and the final incomplete window is normalized according to each backend's mean- or sum-reduced loss.

### 5.1 Master Benchmark Control Matrix

> [!NOTE]
> **Table Legend:** Entries governed by a shared benchmark policy have **no symbol**. Entries with architecture-specific variations or model differences are marked with **⭕**; the shared-policy entries should still be read with the qualifications in the fairness audit.

<div align="center">

<sub><b>Table 3.</b> Comprehensive master control matrix across all three evaluated models in DMS-Eval.</sub>

| Benchmark Dimension | Controlled Parameter | Ultralytics YOLO11n | D-FINE-N | Ultralytics YOLO26n | Shared Controlled Policy / Specification |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Dataset & Ingestion** | **Source Dataset** | DMD RGB Video | DMD RGB Video | DMD RGB Video | 81 driver-facing video recordings (68 public sessions across 14 subjects) |
| | **Temporal Sampling** | 1 FPS | 1 FPS | 1 FPS | 1 frame sampled every 1 second across all videos |
| | **Input Spatial Resolution** | 640×640 | 640×640 | 640×640 | Direct spatial cabin crop (`x=272, y=71, w=640, h=640`); zero letterbox padding or distortion |
| | **Input Representation** | Single static frame | Single static frame | Single static frame | Isolated 2D RGB image frame (emulating streaming single-frame edge ingestion) |
| | **Total Dataset Volume** | 15,723 frames | 15,723 frames | 15,723 frames | 12,722 negative background frames (80.91%) + 3,001 positive cue frames (19.09%) |
| | **Target Cue Ontology** | 4 warning classes | 4 warning classes | 4 warning classes | `phone_use`, `drinking`, `yawning`, `hand_over_mouth` |
| | **Annotation Policy** | 100% human manual | 100% human manual | 100% human manual | Label Studio ground truth; at most 1 bounding box per frame (≤ 1 label/frame) |
| | **Master Ground Truth** | Master COCO JSON | Master COCO JSON | Master COCO JSON | `dataset/annotations.json` as the authoritative single source of truth |
| **Partitioning & Splits** | **Partition Scheme** | 8 / 3 / 3 subjects | 8 / 3 / 3 subjects | 8 / 3 / 3 subjects | Strictly subject-disjoint (S_train ∩ S_val = ∅, S_train ∩ S_test = ∅, S_val ∩ S_test = ∅) |
| | **Training Split (S_train)** | 8 subjects | 8 subjects | 8 subjects | 9,087 frames (1,748 boxes): S1, S4, S6, S7, S8, S9, S13, S14 |
| | **Validation Split (S_val)** | 3 subjects | 3 subjects | 3 subjects | 3,423 frames (639 boxes): S2, S3, S11 |
| | **Test Split (S_test)** | 3 subjects | 3 subjects | 3 subjects | 3,213 frames (614 boxes): S5, S10, S12 |
| | **Split Balance Deviation** | ≤ 5.48% | ≤ 5.48% | ≤ 5.48% | Exhaustive combinatorial optimization ensuring balanced cue proportions |
| | **Temporal Sequencing** | Shuffled (Seed 13) | Shuffled (Seed 13) | Shuffled (Seed 13) | Shuffling applied *only* to train split; val/test preserved in native video order |
| **Training & Optimization** | **Initialization** | Official pretrained | Official pretrained | Official pretrained | Full-model fine-tuning from official pretraining (no training from scratch) |
| | **Frozen Layers** | None (0 layers) | None (0 layers) | None (0 layers) | All backbone and head layers are fully trainable |
| | **Training Budget** | 220 Epochs | 220 Epochs | 220 Epochs | Fixed fine-tuning budget |
| | **Early Stopping** | Disabled | Disabled | Disabled | Full 220 epochs executed without early termination |
| | **Physical Batch Size** | `8` | `8` | `8` | Physical batch size = 8 during training (fitting RTX 4060 8 GB VRAM budget at 640×640) |
| | **Gradient Accumulation** | Fixed 4 steps | Fixed 4 steps | Fixed 4 steps | Effective batch 32 from the first update window |
| | **Training Remainder** | `drop_last=false`; sample-correct | `drop_last=false`; sample-correct | `drop_last=false`; sample-correct | Every training image is retained |
| | **Training Precision** | FP16 AMP | FP16 AMP | FP16 AMP | Shared AMP policy implemented by each pinned framework |
| | **Training Seeds** | `13, 37, 73` | `13, 37, 73` | `13, 37, 73` | Three predeclared equal seeds; framework-specific kernels need not produce identical trajectories |
| | **Hardware Platform** | NVIDIA RTX 4060 | NVIDIA RTX 4060 | NVIDIA RTX 4060 | Dedicated GPU with 8 GB VRAM |
| | **Training Runs** | 3 | 3 | 3 | All runs reported as mean ± sample SD; no best-run selection |
| | **Optimizer Family** | ⭕ Ultralytics `auto` → expected MuSGD | ⭕ AdamW | ⭕ Ultralytics `auto` → expected MuSGD | Pinned official architecture recipes; zero model-specific tuning trials |
| | **Base LR & Weight Decay** | ⭕ Package default `lr0=0.01, wd=0.0005` | ⭕ Official N recipe `lr=0.0008, backbone_lr=0.0004, wd=0.0001` | ⭕ Package default `lr0=0.01, wd=0.0005` | Pinned upstream values except the closed shared adaptations |
| | **LR Schedule** | ⭕ Ultralytics linear decay | ⭕ Pinned D-FINE `MultiStepLR` (milestone 500) | ⭕ Ultralytics linear decay | Exact model-specific schedule from each pinned backend |
| | **Data Augmentation** | ⭕ Mosaic, HSV, flips (`mixup=0`) | ⭕ Photometric, zoom-out, crop, flips; fixed 640 | ⭕ Mosaic, HSV, flips (`mixup=0`) | Exact model-specific augmentation pipeline from each pinned backend |
| **Validation & Calibration** | **Test Isolation Rule** | Zero test access | Zero test access | Zero test access | Test split untouched during training, tuning, checkpointing, and calibration |
| | **Checkpoint Selection** | Highest Val mAP | Highest Val mAP | Highest Val mAP | 1st: Val mAP@0.5:0.95; 2nd: Val mAP@0.5; 3rd: Later epoch |
| | **Threshold Search Space** | τ ∈ [0.01, 0.99] | τ ∈ [0.01, 0.99] | τ ∈ [0.01, 0.99] | Fixed 99-point numerical grid sweep (Δτ = 0.01) on validation split only |
| | **Threshold Objective** | Max Validation F1 | Max Validation F1 | Max Validation F1 | Uniform objective maximizing micro-averaged validation F1 score |
| | **Calibrated Threshold (τ*)** | ⭕ τ* (YOLO11n) | ⭕ τ* (D-FINE-N) | ⭕ τ* (YOLO26n) | Model-specific optimal confidence threshold calibrated on validation split |
| | **Threshold Tie-Breaker** | Higher Precision | Higher Precision | Higher Precision | 1st tie-breaker: Higher Precision; 2nd tie-breaker: Higher confidence value |
| | **Parameter Freezing** | Checkpoint & τ* per seed | Checkpoint & τ* per seed | Checkpoint & τ* per seed | Each model–seed checkpoint and τ* is frozen before its one protected test pass |
| **Runtime & Profiling** | **Runtime Backend** | PyTorch + CUDA | PyTorch + CUDA | PyTorch + CUDA | Native PyTorch (no TensorRT / ONNX Runtime / OpenVINO exports) |
| | **Runtime Hardware** | NVIDIA RTX 4060 | NVIDIA RTX 4060 | NVIDIA RTX 4060 | Consistent 8 GB VRAM GPU environment |
| | **Runtime Precision** | FP32 model/input + CUDA AMP FP16 | FP32 model/input + CUDA AMP FP16 | FP32 model/input + CUDA AMP FP16 | Identical storage and autocast policy |
| | **Runtime Batch Size** | `1` | `1` | `1` | Single-frame edge stream latency profiling |
| | **Warm-up Protocol** | 10 passes | 10 passes | 10 passes | Untimed warm-up passes on 640×640 frames before latency capture |
| | **Timing Scope / Boundary** | Forward + tensor→final detections | Forward + tensor→final detections | Forward + tensor→final detections | Second boundary includes architecture-required postprocessing/NMS |
| | **Timing Mechanism** | CUDA events + synchronized wall clock | Same | Same | CUDA events for forward; high-resolution wall clock for tensor→detections |
| | **Test Set Coverage** | 3,213 frames/run | 3,213 frames/run | 3,213 frames/run | One complete pass for each of the nine frozen model–seed runs |
| | **Latency Metrics** | p50, p95, p99 (ms) | p50, p95, p99 (ms) | p50, p95, p99 (ms) | Median, 95th, and 99th percentile inference latency |
| | **Throughput Profiling** | Sustained FPS | Sustained FPS | Sustained FPS | Continuous test split pass (FPS = 3,213 / T_total) |
| | **VRAM Measurement** | Peak allocated MB | Peak allocated MB | Peak allocated MB | Captured via `torch.cuda.max_memory_allocated()` |
| **Evaluation Harness** | **Shared Evaluator** | DMS-Eval Harness | DMS-Eval Harness | DMS-Eval Harness | Single unified evaluation script; predictions mapped to COCO JSON format |
| | **IoU Matching Rule** | COCO One-to-One | COCO One-to-One | COCO One-to-One | Greedy matching in descending confidence order at IoU ≥ 0.50 |
| | **Detection Metrics** | mAP@0.5:0.95, mAP@0.5 | mAP@0.5:0.95, mAP@0.5 | mAP@0.5:0.95, mAP@0.5 | Full test set and per-class Average Precision |
| | **Operating Point Metrics** | P, R, F1 | P, R, F1 | P, R, F1 | Evaluated at frozen validation-optimal threshold τ* (IoU = 0.50) |
| | **False Alarm Rate (FAR)** | FP detections per 100 negative frames | FP detections per 100 negative frames | FP detections per 100 negative frames | Test denominator is 2,599 negative frames; the value is not necessarily bounded by 100 |
| | **Workload Profiling** | THOP + PyTorch profiler | THOP + PyTorch profiler | THOP + PyTorch profiler | Two tool-dependent estimates with operator-coverage status |
| | **Inference Artifact Size** | Standardized FP16 state dictionary | Same | Same | Excludes optimizer, scheduler, scaler, EMA wrapper, and training history |

</div>

---

## 6. Validation Calibration & Isolated Test Evaluation

### 6.1 Checkpoint Selection Protocol
Final model weights are selected strictly using the Validation split ($S_{\text{val}}$) via the shared DMS-Eval evaluator:
1. **Primary:** Highest validation $\text{mAP}@0.5:0.95$.
2. **First Tie-Breaker:** Highest validation $\text{mAP}@0.5$.
3. **Second Tie-Breaker:** Later epoch checkpoint.

### 6.2 Validation-Only Confidence Threshold Calibration ($\tau^*$)
To evaluate real-world operating performance ($P, R, F_1$), each detector's confidence threshold is calibrated exclusively on the Validation split:
$$\tau^* = \arg\max_{\tau \in [0.01, 0.99]} F_1(\tau; S_{\text{val}}) = \frac{2 \cdot P(\tau) \cdot R(\tau)}{P(\tau) + R(\tau)}$$
under COCO one-to-one $\text{IoU} \ge 0.50$ matching. Once identified, $\tau^*$ and the selected checkpoint weights are permanently frozen.

### 6.3 Isolated Per-Run Single-Pass Test Evaluation

> [!CAUTION]
> **Strict Zero-Test-Access Protocol:**
> Neither candidate model weights nor confidence thresholds ($\tau^*$) have access to the $3,213$ test frames during training, tuning, or calibration. Each of the nine predeclared frozen model–seed runs receives exactly one test pass; test results cannot select runs or change any configuration.

The unseen Test split ($S_{\text{test}}$, 3,213 frames) is evaluated once per frozen model–seed run without post-hoc tuning:
- **Detection Accuracy:** $\text{mAP}@0.5:0.95$ and $\text{mAP}@0.5$ computed against master COCO ground truth.
- **Operating Performance:** Precision, Recall, and $F_1$ score evaluated at the frozen threshold $\tau^*$.
- **Background False Alarm Rate (FAR):** false-positive detections per 100 negative test frames, with $N_{\text{neg}}=2{,}599$.
- **Latency & Throughput:** Both model-forward and tensor-to-final-detections latency ($p50, p95, p99$) and sustained FPS at batch size 1; the second boundary includes required postprocessing/NMS.
- **Memory Footprint:** Peak VRAM allocated via `torch.cuda.max_memory_allocated()`.

---

## 7. Comparative Results Framework

<div align="center">

<sub><b>Table 4.</b> Pre-registered system comparison on the protected test split (RTX 4060, batch 1, CUDA AMP FP16).</sub>

| Model | Params | FLOPs (THOP / profiler) | Peak VRAM | FP16 artifact | Forward p50 | Tensor→detections p50 / p95 / p99 | Tensor→detections FPS | FAR / 100 negatives | mAP@0.5:0.95 | mAP@0.5 | Precision | Recall | F1 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Ultralytics YOLO11n** | *[PENDING]* | *[PENDING]* | *[PENDING]* | *[PENDING]* | *[PENDING]* | *[PENDING]* | *[PENDING]* | *[PENDING]* | *[PENDING]* | *[PENDING]* | *[PENDING]* | *[PENDING]* | *[PENDING]* |
| **Ultralytics YOLO26n** | *[PENDING]* | *[PENDING]* | *[PENDING]* | *[PENDING]* | *[PENDING]* | *[PENDING]* | *[PENDING]* | *[PENDING]* | *[PENDING]* | *[PENDING]* | *[PENDING]* | *[PENDING]* | *[PENDING]* |
| **D-FINE-N** | *[PENDING]* | *[PENDING]* | *[PENDING]* | *[PENDING]* | *[PENDING]* | *[PENDING]* | *[PENDING]* | *[PENDING]* | *[PENDING]* | *[PENDING]* | *[PENDING]* | *[PENDING]* | *[PENDING]* |

</div>

<div align="center">

<sub><b>Table 5.</b> Per-class detection performance breakdown (mAP@0.5:0.95 / mAP@0.5 on unseen test split).</sub>

| Model Architecture | `phone_use` (mAP 50:95 / 50) | `drinking` (mAP 50:95 / 50) | `yawning` (mAP 50:95 / 50) | `hand_over_mouth` (mAP 50:95 / 50) |
| :--- | :---: | :---: | :---: | :---: |
| **Ultralytics YOLO11n** | *[PENDING]* | *[PENDING]* | *[PENDING]* | *[PENDING]* |
| **Ultralytics YOLO26n** | *[PENDING]* | *[PENDING]* | *[PENDING]* | *[PENDING]* |
| **D-FINE-N** | *[PENDING]* | *[PENDING]* | *[PENDING]* | *[PENDING]* |

</div>

---

## 8. Repository Structure & Protocol Documentation

```text
DMS-Eval/
├── configs/                                  # Frozen protocol, backend pins, and model configs
│   ├── benchmark.yaml                        # Machine-readable shared benchmark policy
│   ├── backends.yaml                         # Pinned repositories and pretrained weights
│   ├── dfine/dfine_n_dms.yml                 # D-FINE-N training configuration
│   └── yolo/dms_eval.yaml                    # Shared Ultralytics training arguments
├── core/                                     # Adapters, validation, evaluation, isolation, profiling
├── dataset/                                  # Annotation files & subject partitions
│   ├── annotations.json                      # Authoritative master COCO JSON
│   ├── splits.json                           # Frozen 8/3/3 subject-disjoint partitions
│   └── preprocessing.json                    # Frozen spatial cropping parameters
├── docs/                                     # Authoritative protocol documentation
│   ├── quick-start.md                        # Benchmark scope, data ingestion & splits
│   ├── annotation-protocol.md                # 4-cue ontology & annotation guide
│   ├── training-protocol.md                  # Locked training controls & recipe rules
│   ├── evaluation-protocol.md                # Evaluator harness, metrics & runtime profiling
│   ├── benchmark-readiness.md                # Guarded lifecycle and readiness evidence
│   ├── fairness.md                           # Cross-model comparability audit
│   └── manual-annotation-guide.pdf           # 1-page desktop annotation quick-reference
├── manuscript/                               # Full conference paper source & PDF
│   ├── main.tex                              # LaTeX source manuscript
│   ├── main.pdf                              # Compiled conference paper PDF
│   └── figures/                              # Publication charts and figures
└── scripts/                                  # Reproducible workflow entry points
    ├── data/                                 # Extraction, annotations, formats, and split generation
    ├── benchmark/                            # Setup, validation, training, profiling, and evaluation
    ├── publication/                          # Manuscript figures and result tables
    └── README.md                             # Command index and lifecycle documentation
```

<div align="center">

<sub><b>Table 6.</b> Authoritative protocol documentation index.</sub>

| Document | Key Contents | Status |
| :--- | :--- | :---: |
| [**Benchmark Scope & Splits**](./docs/quick-start.md) | Scope, 640×640 preprocessing, subject splits, annotation layout, and frame naming | 🧊 Frozen |
| [**Annotation Protocol & Ontology**](./docs/annotation-protocol.md) | 4 warning cues, anatomical extents, mutual exclusivity, and quality controls | 🧊 Frozen |
| [**Manual Annotation Guide (PDF)**](./docs/manual-annotation-guide.pdf) | 1-page field reference: hotkeys, bounding-box extents, and decision matrix | 📋 Field Guide |
| [**Training Protocol**](./docs/training-protocol.md) | Initialization, locked training controls, and model-specific optimization recipes | 🧊 Frozen |
| [**Evaluation Protocol**](./docs/evaluation-protocol.md) | Metrics, shared evaluator, test isolation, threshold sweep, and runtime profiling | 🧊 Frozen |
| [**Benchmark Readiness**](./docs/benchmark-readiness.md) | Machine-readable controls, guarded commands, and verification coverage | ✅ Implemented |
| [**Fairness Audit**](./docs/fairness.md) | Disclosed asymmetries, likely directional effects, and recommended corrections | ⚠️ Disclosed |

</div>

---

## Authors & Citation

- **Oumar Mamoun Ibrahim** — Senior Undergraduate Researcher, Department of Computer Engineering, University of Sharjah<br>
  [![ORCID: Oumar](https://img.shields.io/badge/ORCID-0009--0008--0312--1605-A6CE39?logo=orcid&logoColor=white)](https://orcid.org/0009-0008-0312-1605) · [U22200741@sharjah.ac.ae](mailto:U22200741@sharjah.ac.ae)

- **Dr. Mohamad Khairi bin Ishak** — Associate Professor, Department of Computer Engineering, University of Sharjah<br>
  [![ORCID: Dr. Mohamad](https://img.shields.io/badge/ORCID-0000--0002--3554--0061-A6CE39?logo=orcid&logoColor=white)](https://orcid.org/0000-0002-3554-0061) · [mishak@sharjah.ac.ae](mailto:mishak@sharjah.ac.ae)

```bibtex
@inproceedings{ibrahim2026dmseval,
  title     = {Real-Time Driver Behavior Detection Using Lightweight Object Detection Models with Subject-Disjoint Evaluation},
  author    = {Ibrahim, Oumar Mamoun and bin Ishak, Mohamad Khairi},
  booktitle = {Proceedings of the 5th International Conference on Artificial Intelligence Science and Applications in Industry and Society (CAISAIS 2026)},
  year      = {2026},
  pages     = {1--6}
}
```

---

## Acknowledgments & License

This benchmark builds upon the open-source architectures and tools developed by the teams behind [Ultralytics YOLO](https://github.com/ultralytics/ultralytics), [D-FINE](https://github.com/Peterande/D-FINE), and [Label Studio](https://github.com/HumanSignal/label-studio). We sincerely thank their authors and maintainers for making these frameworks available to the research community.

This project is licensed under the **Apache License 2.0** — see the [LICENSE](LICENSE) file for details.
