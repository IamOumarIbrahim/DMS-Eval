# Experimental Setup & Configuration Guide

**Project:** DMS-Eval — Controlled Lightweight Object Detection Benchmark for Driver Monitoring Systems  
**Protocol Version:** Protocol 2.0.0-fairness-lock (`docs/benchmark-protocol.md`)  
**Hardware Platform:** NVIDIA GeForce RTX 4060 (8 GB GDDR6 VRAM)  
**Input Resolution:** $640\times640$ RGB

---

## 1. Hardware & Software Environment

All models in DMS-Eval are evaluated within a strictly isolated, standardized hardware and software environment to guarantee reproducible latency and accuracy metrics:

| Component | Specification | Operational Role |
| :--- | :--- | :--- |
| **GPU** | NVIDIA GeForce RTX 4060 (8 GB GDDR6) | Primary acceleration engine for training and timing |
| **CUDA / Driver** | CUDA 12.x / NVIDIA Driver | Standardized GPU compute runtime |
| **Framework** | PyTorch 2.x | Base deep learning and tensor execution environment |
| **Numerical Precision** | FP32 (Primary) / AMP Equivalence Gate | Standardized numerical precision for inference latency |
| **Input Dimensions** | $640\times640\times3$ (RGB) | Unified spatial input resolution across all architectures |
| **Batch Size** | 1 (Inference) / 16 (Effective Training) | Simulates real-time single-frame video stream ingestion |

---

## 2. Evaluated Candidate Architectures

The benchmark evaluates three lightweight candidate object detectors chosen across distinct structural paradigms:

### 1. YOLO11n (CSPNet / Convolutional Baseline)
* **Architecture:** C3k2 convolutional feature extractor with CSP-style cross-stage partial connections.
* **Parameters / Complexity:** 2.6M Parameters / 6.5 GFLOPs.
* **Post-Processing:** Conventional Non-Maximum Suppression (NMS).
* **Source:** Official Ultralytics Repository (`ultralytics>=8.3.0`).

### 2. D-FINE-N (DETR Query Refinement Baseline)
* **Architecture:** Vision Transformer query-based detection utilizing fine-grained distribution refinement.
* **Parameters / Complexity:** 4.0M Parameters / 7.0 GFLOPs.
* **Post-Processing:** Native end-to-end / NMS-free direct set prediction.
* **Source:** Official D-FINE Repository (`Peterande/D-FINE`).

### 3. YOLO26n (Native End-to-End Convolutional)
* **Architecture:** One-to-one matching head eliminating Distribution Focal Loss (DFL) and dual-label assignment.
* **Parameters / Complexity:** 2.4M Parameters / 5.4 GFLOPs.
* **Post-Processing:** Native NMS-free inference.
* **Source:** Official Ultralytics Repository (`ultralytics>=8.3.0`).

---

## 3. Dataset Configuration & Partitioning

### Dataset Source
* Derived from the public RGB real-car streams of the **Driver Monitoring Dataset (DMD)** across 14 authorized subjects.
* Includes synchronized Face and Body camera viewpoints.

### Subject-Disjoint Partitioning Specification
To prevent identity overfitting and sequence leakage, subjects are strictly partitioned:
* **Train Set (8 Subjects):** Used exclusively for model optimization with COCO-pretrained weights.
* **Validation Set (3 Subjects):** Used exclusively for checkpoint selection ($\text{AP}_{50:95}$) and threshold tuning.
* **Test Set (3 Subjects):** Held-out partition evaluated in a single unadjusted pass.

### Unified 6-Class Annotation Ontology
| Class ID | Class Name | Target Category | Annotation Description |
| :---: | :--- | :--- | :--- |
| `0` | `eyes_open` | Drowsiness Cue | Bounding box enclosing clearly open driver eye region |
| `1` | `eyes_closed` | Drowsiness Cue | Bounding box enclosing closed driver eye region |
| `2` | `yawning` | Drowsiness Cue | Bounding box enclosing open mouth exhibiting yawning gesture |
| `3` | `cellphone` | Distraction Object | Bounding box enclosing handheld mobile phone |
| `4` | `bottle` | Distraction Object | Bounding box enclosing beverage bottle or drink container |
| `5` | `hair_comb` | Distraction Object | Bounding box enclosing hair grooming comb or brush |

---

## 4. Standardized Inference Profiling Protocol

To eliminate timing jitter, OS scheduling artifacts, and GPU thermal throttling:
1. **Warm-up Phase:** Execute 50 forward passes on dummy input ($640\times640$) to warm GPU caches and initialize CUDA kernels.
2. **Synchronization Barriers:** Wrap each forward iteration in `torch.cuda.synchronize()` before and after execution.
3. **Timed Iterations:** Execute 500 forward passes on held-out test frames.
4. **Reported Metrics:**
   - **Median Latency (ms):** 50th-percentile execution time.
   - **p95 Latency (ms):** 95th-percentile tail latency.
   - **Throughput (FPS):** $\frac{500}{\sum \text{latencies}}$.
   - **Peak VRAM (MB):** Measured via `torch.cuda.max_memory_allocated()`.
