# Scientific Contributions & Future Research Directions

**Project:** DMS-Eval — Controlled Lightweight Object Detection Benchmark for Driver Monitoring Systems  
**Primary Research Question:**  
> *“Under a controlled compute-constrained evaluation, how do lightweight object detectors compare in accuracy, inference efficiency, and robustness when detecting visual cues associated with driver distraction and drowsiness across normal and low-light/nighttime driving conditions?”*

---

## 1. Overview & Research Motivation

Driver Monitoring Systems (DMS) are increasingly critical for intelligent vehicle safety, driver assistance (ADAS), and regulatory compliance (e.g., Euro NCAP requirements for driver drowsiness and distraction detection). However, deploying deep computer vision models in production automotive environments faces severe challenges:
1. **Tight Compute & Power Constraints:** Embedded automotive Electronic Control Units (ECUs) and edge vision processors possess strictly bounded compute budgets (VRAM, thermal envelope, memory bandwidth).
2. **Challenging In-Cabin Illumination:** Vision systems must operate reliably across extreme variations in lighting, from harsh direct sunlight to low-light nighttime driving conditions.
3. **Confounded Existing Benchmarks:** Prior DMS detector evaluations often lack experimental fairness—frequently mixing disparate pretraining data, inconsistent input resolutions, uncontrolled data splits with subject leakage, and conflating frame-level cue detection with temporal state classification.

**DMS-Eval** addresses these gaps through a strictly controlled empirical benchmark protocol, a unified dataset ontology, multi-dimensional Pareto profiling, and fine-grained condition-wise robustness analyses.

---

## 2. Core Planned Contributions

### Contribution 1: Controlled Benchmark of Lightweight Detector Paradigms

DMS-Eval provides a rigorous, controlled empirical comparison of modern lightweight 2D object detection architectures representing fundamentally distinct design paradigms:

* **Evaluated Architectural Paradigms:**
  * **Convolutional / CSP Baseline (`YOLO11n`):** Evaluates traditional CSPNet-style cross-stage partial convolutions and C3k2 feature extraction blocks with conventional Non-Maximum Suppression (NMS).
  * **Transformer / DETR-Based Refinement (`D-FINE-N`):** Evaluates query-based object detection utilizing fine-grained distribution refinement and native end-to-end NMS-free bounding box prediction.
  * **Native End-to-End Convolutional Architecture (`YOLO26n`):** Evaluates one-to-one label assignment and Distribution Focal Loss (DFL)-free native end-to-end inference without post-processing NMS latency overhead.
* **Strict Fairness & Control Protocol:**
  * **Standardized Resolution:** Fixed $640\times640$ RGB input across all models.
  * **Pretrained Equivalence:** All architectures are initialized exclusively from official COCO-pretrained weights.
  * **Hardware & Runtime Isolation:** All profiling is performed on identical hardware (NVIDIA GeForce RTX 4060, 8 GB VRAM) under standardized warm-up cycles, synchronization barriers, and PyTorch runtime backends.
  * **Untouched Test Isolation:** Operating confidence and IoU thresholds are determined strictly on validation data; the held-out test set is evaluated in a single, unadjusted pass.

---

### Contribution 2: Unified In-Cabin Dataset & Annotation Ontology

DMS-Eval establishes a custom, unified benchmark dataset derived from the real-car RGB streams of the public **Driver Monitoring Dataset (DMD)** across 14 authorized subjects:

* **Subject-Disjoint Partitioning:**
  * Strict subject-level partitioning (8 Train / 3 Val / 3 Test) guaranteeing zero subject identity leakage across splits.
  * Video sequence confinement ensuring all frames from a specific recording session remain within a single split.
* **Unified 6-Class Multi-Task Ontology:**
  * **Drowsiness-Associated Visual Cues:** Fine-grained facial cues including `eyes_open`, `eyes_closed`, and `yawning`.
  * **Distraction-Associated Objects:** Common handheld distraction objects including `cellphone`, `bottle`, and `hair_comb`.
* **Multi-Camera & Operating Condition Coverage:**
  * Dual viewpoints combining Face and Body in-cabin camera streams.
  * Systematic coverage of four core operating scenarios: **normal daylight**, **distracted behaviors**, **fatigued/drowsy episodes**, and **low-light/nighttime illumination**.

---

### Contribution 3: Multi-Dimensional Accuracy–Efficiency Trade-Off Analysis

Rather than relying on isolated scalar metrics, DMS-Eval evaluates model performance across three complementary axes:

* **Detection Quality:**
  * $\text{AP}_{50:95}$ (Primary evaluation metric averaged across IoU $0.50$–$0.95$).
  * Secondary threshold-controlled metrics: $\text{AP}_{50}$, Precision, Recall, Macro F1-Score, and Balanced Frame-Level Accuracy.
* **Inference Efficiency & Latency Distributions:**
  * Latency percentiles: Median latency and 95th-percentile (p95) tail latency (ms) to quantify timing jitter and worst-case execution time critical for real-time safety systems.
  * End-to-End processing throughput (FPS).
* **Model Complexity & Deployment Footprint:**
  * Parameter count (M) and computational complexity (GFLOPs at $640\times640$).
  * Serialized on-disk weight footprint (MB) and peak GPU runtime memory allocation (MB).
* **Safety Diagnostic Profiling:**
  * **False Positives per Normal Image (FP/image):** Measures the rate of spurious warning detections during normal driving, quantifying driver alert fatigue and nuisance trip risk.

---

### Contribution 4: Condition-Wise Slice & Robustness Analysis

DMS-Eval introduces disaggregated slice analysis to expose the operational boundaries, failure modes, and architectural trade-offs of lightweight detectors under environmental and behavioral stress:

* **Environmental Robustness Slice:**
  * Quantifies accuracy degradation ($\Delta\text{AP}_{50:95}$ and $\Delta\text{F1}$) when transitioning from high-visibility normal daylight to low-contrast low-light/nighttime driving.
* **Behavioral Scenario Slices:**
  * Measures model sensitivity and class confusion across normal, distracted, and fatigued driver behaviors.
* **Scale & Target Granularity Analysis:**
  * Compares architectural performance on small, deformable facial cues (`eyes_closed`, $10\times15$ pixels) versus larger, distinct handheld objects (`bottle`, `cellphone`).

---

## 3. Investigated Future Work & Research Horizons

Following the completion of the baseline benchmark, several research extensions are planned:

### 1. Attention-Centric Lightweight Architectures (`YOLOv12n Turbo`)
* **Scope:** Explore attention-centric YOLO architectures featuring area attention, residual efficient layer aggregation (R-ELAN), and attention-driven feature pyramids.
* **Rationale:** While YOLOv12n demonstrates promising representation capacity, it was deferred from the initial benchmark to allow downstream deployment runtimes (ONNX/TensorRT) and custom CUDA attention operators to stabilize across embedded hardware backends.

### 2. Temporal Driver-State Modeling & Sequence Aggregation
* **Scope:** Integrate frame-level cue detections into temporal sequence models (e.g., Hidden Markov Models, Temporal Convolutional Networks, or lightweight GRU/LSTM recurrent heads).
* **Rationale:** Transitioning from discrete frame-level cue detection to clinical driver state inference requires modeling cue duration (e.g., PERCLOS — percentage of eye closure over time), blink frequencies, and sustained distraction intervals over sliding temporal windows.

### 3. Benchmark Expansion & In-Cabin Environmental Diversity
* **Scope:** Expand dataset diversity to include Near-Infrared (NIR) / Thermal camera streams, extreme glare/shadow artifacts, adverse weather conditions, and diverse driver demographic factors (e.g., eyewear, sunglasses, head coverings).
* **Rationale:** Enhances domain generalizability and addresses optical occlusion challenges common in real-world automotive deployment.

### 4. Cross-Dataset Generalization & Transferability
* **Scope:** Conduct zero-shot evaluation and cross-dataset fine-tuning across complementary driver monitoring datasets (such as StateFarm, AUC Distracted Driver, and Drive-AIMS).
* **Rationale:** Validates whether feature representations learned on DMD generalize effectively across different vehicle interior geometries, seating positions, and sensor placements.

### 5. Embedded Edge Hardware Deployment & Quantization
* **Scope:** Benchmark optimized model variants on physical automotive edge platforms (e.g., NVIDIA Jetson Orin Nano, NXP BlueBox, Raspberry Pi 5 / Coral Edge TPU).
* **Rationale:** Quantifies the real-world impact of post-training INT8 / FP16 quantization, TensorRT engine compilation, and memory bus bandwidth limitations on latency jitter and energy efficiency.
