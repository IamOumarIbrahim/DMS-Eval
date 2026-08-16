# Evaluated Models & Architectural Scope

**Project:** DMS-Eval — Controlled Lightweight Object Detection Benchmark for Driver Monitoring Systems  
**Evaluation Scope:** Lightweight 2D Object Detectors ($\le 5.0\text{M}$ Parameters)  
**Standardized Input Resolution:** $640\times640$ RGB  
**Initialization:** Official COCO-pretrained weights

---

## 1. Evaluated Architecture Candidates

The benchmark evaluates three candidate architectures representing distinct structural paradigms in modern real-time object detection:

| Model | Architecture Family | Structural Paradigm | Key Architectural Mechanisms | Post-Processing | Parameter Count | Complexity (GFLOPs) | Official Repository / Reference |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| **YOLO11n** | YOLO | Convolutional / CSP Baseline | C3k2 convolutional feature extractor with CSPNet-style cross-stage partial connections | NMS-based | 2.6M | 6.5 | [Ultralytics YOLO11](https://docs.ultralytics.com/models/yolo11/) |
| **D-FINE-N** | DETR | Transformer Query Refinement | Fine-grained distribution refinement and localized self-attention query heads | Native End-to-End (NMS-Free) | 4.0M | 7.0 | [Official D-FINE](https://github.com/Peterande/D-FINE) |
| **YOLO26n** | YOLO | Native End-to-End Convolutional | One-to-one matching head eliminating Distribution Focal Loss (DFL) | Native End-to-End (NMS-Free) | 2.4M | 5.4 | [Ultralytics YOLO26](https://docs.ultralytics.com/models/yolo26/) |

---

## 2. Official COCO Reference Benchmarks (Baseline Context)

> [!NOTE]
> These figures are published official COCO val2017 metrics provided for baseline reference and do not represent DMS-Eval in-cabin benchmark results.

* **YOLO11n:** $39.5\text{ AP}_{50:95}$, $1.50\text{ ms}$ latency (NVIDIA T4 TensorRT FP16), $2.6\text{M}$ params, $6.5\text{ GFLOPs}$.
* **D-FINE-N:** $42.8\text{ AP}_{50:95}$, $2.12\text{ ms}$ latency (NVIDIA T4 TensorRT FP16), $4.0\text{M}$ params, $7.0\text{ GFLOPs}$.
* **YOLO26n:** $40.1\text{ AP}_{50:95}$ (native end-to-end path) / $40.9\text{ AP}_{50:95}$ (conventional detection path), $1.70\text{ ms}$ latency (NVIDIA T4 TensorRT FP16), $2.4\text{M}$ params, $5.4\text{ GFLOPs}$.

---

## 3. Future Work Architecture Candidates

* **YOLOv12n (Turbo):**
  * **Architectural Focus:** Attention-centric YOLO variant featuring area attention and residual efficient layer aggregation (R-ELAN).
  * **Status:** Assigned to Future Work due to nascent downstream ONNX/TensorRT export runtimes and custom CUDA kernel requirements on embedded edge hardware.