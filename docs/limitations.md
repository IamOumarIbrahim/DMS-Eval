# Limitations & Experimental Constraints

**Project:** DMS-Eval — Controlled Lightweight Object Detection Benchmark for Driver Monitoring Systems  
**Document Purpose:** Transparently documents the empirical constraints, sensor boundaries, and methodological limitations of the DMS-Eval study.

---

## 1. Dataset & Sensor Modality Constraints

* **RGB-Only Visual Modality:**
  * DMS-Eval benchmarks visible-spectrum RGB real-car video streams.
  * *Constraint:* Commercial automotive DMS frequently employ active Near-Infrared (NIR) illumination with narrow bandpass optical filters ($850\text{ nm}$ or $940\text{ nm}$) to achieve total invariant illumination at night. While RGB low-light evaluation captures extreme challenging vision scenarios, NIR-specific reflectance characteristics are not modeled.
* **Single Source Benchmark Dataset:**
  * The dataset is curated exclusively from the public subsets of the Driver Monitoring Dataset (DMD).
  * *Constraint:* While DMD provides authentic in-cabin automotive streams across multiple camera angles, cross-dataset transferability to independently collected datasets (e.g., StateFarm, Drive-AIMS) remains an unverified hypothesis reserved for future work.
* **Subject Cohort Size:**
  * The evaluation partition comprises 14 total subjects (8 Train / 3 Val / 3 Test).
  * *Constraint:* While the split strictly enforces subject-disjoint isolation, the cohort size represents a bounded demographic sample. Extreme demographic variations (e.g., heavy prescription eyewear, tinted sunglasses, dense facial hair) are not comprehensively covered.

---

## 2. Methodological & Temporal Constraints

* **Frame-Level Discrete Detection vs. Temporal State Modeling:**
  * DMS-Eval evaluates spatial 2D object detection at the individual frame level ($640\times640$).
  * *Constraint:* Single-frame detections do not incorporate temporal context, eye blink duration (PERCLOS), gaze fixation velocity, or distraction persistence over time. Single-frame cue detections must be integrated into downstream temporal state machines for full clinical driver state classification.
* **Fixed Single Operating Point Thresholding:**
  * Precision, Recall, and F1 metrics are reported at a single standardized validation-tuned confidence threshold.
  * *Constraint:* Real-world deployment often requires dynamic threshold adaptation depending on vehicle speed, operating domain, or driving context.

---

## 3. Hardware & Architecture Constraints

* **Single Target GPU Environment:**
  * Profiling is conducted on a dedicated desktop workstation GPU (NVIDIA GeForce RTX 4060, 8 GB VRAM).
  * *Constraint:* Embedded automotive system-on-chips (e.g., NVIDIA DRIVE Orin, Texas Instruments TDA4x, Ambarella CVflow, Raspberry Pi / Edge TPU) feature different memory bus architectures, hardware NPU tensor engines, and thermal throttling behaviors.
* **Deferred Attention-Centric Models (`YOLOv12n Turbo`):**
  * YOLOv12n was excluded from the primary benchmark due to nascent downstream deployment tooling (ONNX / TensorRT custom kernel support).
  * *Constraint:* Benchmarking attention-centric YOLO variants is documented as future work once runtime export pipelines achieve parity with standard YOLO architectures.
