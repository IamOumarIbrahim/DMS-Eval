# Benchmark Results & Official Reference Performance

**Project:** DMS-Eval — Controlled Lightweight Object Detection Benchmark for Driver Monitoring Systems  
**Evaluation Protocol:** Controlled Compute-Constrained Benchmark Protocol (`docs/benchmark/benchmark-protocol.md`)  
**Hardware Baseline:** NVIDIA GeForce RTX 4060 (8 GB VRAM)  
**Input Resolution:** $640\times640$ (RGB)  
**Status:** Evaluation Harness & Tables Locked (Awaiting Phase 3 Benchmark Execution)

---

## 1. Official Reference Benchmarks (COCO val2017)

> [!NOTE]
> The table below lists **official COCO validation metrics reported by the respective model authors**. These values serve strictly as external reference baselines and do **not** represent DMS-Eval in-cabin benchmark results.

| Model | Architecture Family | Input | $\text{AP}^{\text{val}}_{50:95}$ | T4 Latency (ms) | Params (M) | GFLOPs | Source / Implementation |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **YOLO11n** | Convolutional / CSP | $640\times640$ | 39.5 | 1.50 | 2.6 | 6.5 | [Ultralytics YOLO11](https://docs.ultralytics.com/models/yolo11/) |
| **D-FINE-N** | DETR / Distribution Refine | $640\times640$ | 42.8 | 2.12 | 4.0 | 7.0 | [Official D-FINE](https://github.com/Peterande/D-FINE) |
| **YOLO26n** | Native End-to-End YOLO | $640\times640$ | 40.1<sup>e2e</sup> | 1.70 | 2.4 | 5.4 | [Ultralytics YOLO26](https://docs.ultralytics.com/models/yolo26/) |

*Note: YOLO26n reports $40.1\text{ AP}_{50:95}$ for its native end-to-end inference path ($40.9\text{ AP}_{50:95}$ for its conventional detection path).*

---

## 2. Planned DMS-Eval Benchmark Results

### Table 1: Detection Performance & Low-Light Robustness

Evaluated on the held-out test partition (3 subjects, zero sequence leakage) across all 6 target classes (`eyes_open`, `eyes_closed`, `yawning`, `cellphone`, `bottle`, `hair_comb`).

| Model | Architecture Paradigm | $\text{AP}_{50:95}$ | $\text{AP}_{50}$ | Precision | Recall | F1-Score | Balanced Acc | Low-Light $\text{AP}_{50:95}$ |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **YOLO11n** | CSPNet / Convolutional | — | — | — | — | — | — | — |
| **D-FINE-N** | DETR Query Refinement | — | — | — | — | — | — | — |
| **YOLO26n** | Native End-to-End (NMS-Free) | — | — | — | — | — | — | — |

---

### Table 2: Inference Efficiency & Deployment Footprint

Benchmarked on standardized hardware (**NVIDIA GeForce RTX 4060**, Batch Size = 1, PyTorch FP32 backend, 50 warm-up runs, 500 synchronized timed iterations).

| Model | Parameters (M) | Complexity (GFLOPs) | Median Latency (ms) | p95 Latency (ms) | Throughput (FPS) | Weight Size (MB) | Peak VRAM (MB) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **YOLO11n** | 2.6 | 6.5 | — | — | — | — | — |
| **D-FINE-N** | 4.0 | 7.0 | — | — | — | — | — |
| **YOLO26n** | 2.4 | 5.4 | — | — | — | — | — |

---

## 3. Disaggregated Condition-Wise & Diagnostic Slices

### Environmental Robustness Slice (Daylight vs. Low-Light/Nighttime)
* **Objective:** Quantify performance degradation ($\Delta\text{AP}_{50:95}$) induced by low-illumination and sensor noise.
* **Evaluation Manifests:** `test_daylight.txt` vs. `test_night.txt`.

### Behavioral Slices (Normal vs. Distracted vs. Drowsy)
* **Normal Driving:** Background negative validation; evaluates False Positives per Normal Image (FP/image).
* **Distracted Driving:** Class-specific detection of handheld interference objects (`cellphone`, `bottle`, `hair_comb`).
* **Fatigued / Drowsy Driving:** Localization and classification of facial cues (`eyes_closed`, `yawning`).

### Safety Diagnostic: False Alarm Profiling
* **Metric:** $\text{FP/Image} = \frac{\text{Total False Positive Cue Detections on Normal Frames}}{\text{Total Normal Frames}}$
* **Target:** Lower is better (minimizes driver alert fatigue and nuisance triggering in ADAS).
