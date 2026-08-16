# Benchmark Scope Boundaries & Terminology Protocol

**Project:** DMS-Eval — Controlled Lightweight Object Detection Benchmark for Driver Monitoring Systems  
**Document Purpose:** Defines precise scientific scope boundaries, in-scope vs. out-of-scope criteria, and mandatory terminology rules to preserve experimental validity.

---

## 1. Core Benchmark Scope (In-Scope)

DMS-Eval is strictly defined as an **empirical 2D object detection benchmark** evaluating lightweight vision models for driver monitoring:

1. **Spatial Visual Cue Detection:**
   - Detecting and localizing predefined 2D bounding boxes corresponding to observable facial cues (`eyes_open`, `eyes_closed`, `yawning`) and handheld distraction objects (`cellphone`, `bottle`, `hair_comb`).
2. **Single-Frame Discrete Inference:**
   - Each video frame is processed as an independent, single-frame input ($640\times640$ RGB) under a standard computer vision detection harness.
3. **Lightweight & Edge-Feasible Architectures:**
   - Evaluates models with parameter counts under $5.0\text{M}$ and computational demands suitable for resource-constrained automotive embedded processors.
4. **Controlled Multi-Condition Evaluation:**
   - Rigorously evaluating models across four cabin operating environments: **normal daylight**, **distracted behavior**, **fatigued/drowsy behavior**, and **low-light/nighttime driving**.

---

## 2. Explicit Out-of-Scope Boundaries

To maintain rigorous scientific clarity and avoid overclaiming, the following aspects are explicitly declared **out of scope** for DMS-Eval:

* **No Temporal Driver-State Inference:**
  * DMS-Eval does **not** perform end-to-end temporal driver drowsiness classification or distraction diagnosis.
  * A single frame exhibiting `eyes_closed` or `cellphone` does **not** clinically prove that a driver "is drowsy" or "is distracted".
* **No Temporal Duration or Sequence Modeling:**
  * Metric aggregation across video sequences (e.g., PERCLOS, blink duration histograms, gaze fixation duration) is excluded from the primary benchmark.
* **No Multi-Sensor Fusion:**
  * Physiological sensors (EEG, ECG), CAN bus vehicle dynamics (steering wheel angle, lane keeping), and active Near-Infrared / depth sensors are outside the current scope.
* **No Online Driver Alert Systems:**
  * Designing user-interface warning chimes, alert fatigue suppression logic, or vehicle intervention actuators is outside the scope.

---

## 3. Mandatory Terminology & Nomenclature Rules

All project documentation, codebase comments, and manuscript sections must adhere strictly to these terminology rules:

| Domain | Mandated Terminology | Disallowed / Inaccurate Phrasing | Rationale |
| :--- | :--- | :--- | :--- |
| **Detection Target** | *"Visual cues associated with drowsiness/distraction"*, *"Observable driver monitoring targets"* | *"Drowsiness detection"*, *"Detecting if the driver is asleep"*, *"Distraction classification"* | Single-frame detection localizes visual artifacts, not cognitive physiological states. |
| **Operating Conditions** | *"Normal daylight"*, *"Low-light/nighttime"*, *"Distracted"*, *"Fatigued/drowsy"* | *"Bad weather"*, *"Night vs day"*, *"Sleepy driving"* | Standardizes environmental and behavioral slice descriptions. |
| **Model Class** | *"Lightweight object detectors"*, *"Real-time 2D detectors"* | *"Full DMS pipeline"*, *"Driver state classifier"* | Accurately describes the architectural class under evaluation. |
| **Metric Notation** | $\text{AP}_{50:95}$, $\text{AP}_{50}$, Precision, Recall, F1, Balanced Accuracy | $mAP$, $AP$, $Accuracy$ (without specification) | Enforces formal COCO evaluation and threshold-controlled metric definitions. |
| **Timing & Latency** | *"Median latency (ms)"*, *"p95 latency (ms)"*, *"FPS throughput"* | *"Speed"*, *"Average latency"*, *"Lag"* | Distinguishes central tendency from tail latency execution jitter. |
| **Model Footprint** | *"Weight size (MB)"*, *"Parameter count (M)"*, *"Peak VRAM (MB)"* | *"Size"*, *"Weight"* | Disambiguates parameter count from serialized disk storage and runtime memory. |
