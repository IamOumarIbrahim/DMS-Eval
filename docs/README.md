# DMS-Eval Documentation Suite

[← Back to the DMS-Eval Landing Page](../README.md)

Welcome to the comprehensive technical documentation for **DMS-Eval**, a controlled empirical benchmark evaluating real-time lightweight 2D object detectors (YOLO11n, D-FINE-N, and YOLO26n) for in-cabin driver drowsiness and inattention warning cue detection.

---

## 📚 Benchmark Protocols

<div align="center">

| Document | Core Subject Area | Benchmark Status |
| :--- | :--- | :---: |
| [**Benchmark Scope, Data & Splits**](./quick-start.md) | Single-frame detection scope, $640 \times 640$ spatial crop geometry, 8/3/3 subject-disjoint partitions, dataset schema, and directory layout. | 🧊 Frozen |
| [**Annotation Protocol & Cue Ontology**](./annotation-protocol.md) | 4 frozen visual warning cues, anatomical bounding-box boundaries, single-annotation policy, and mutual exclusivity hierarchy. | 🧊 Frozen |
| [**Manual Annotation Field Guide (PDF)**](./manual-annotation-guide.pdf) | Authoritative 1-page desktop reference: Label Studio hotkeys, visual decision boundaries, and edge-case decision matrix. | 📋 Practical Field Guide |
| [**Training Protocol**](./training-protocol.md) | Official pretrained initialization, full-model fine-tuning recipes, hyperparameters, random seeds, and hardware parity controls. | 🧊 Frozen |
| [**Evaluation Protocol**](./evaluation-protocol.md) | Standardized metrics ($\text{mAP}_{50}$, $\text{mAP}_{50-95}$, Precision, Recall, $F_1$), shared evaluation harness, validation threshold sweeps, and GPU latency/throughput profiling. | 🧊 Frozen |

</div>

---

## 🎯 Frozen Target Warning Cue Ontology

<div align="center">

| Cue Class | Category ID | Visual Cue Definition | Bounding Box Extent |
| :--- | :---: | :--- | :--- |
| **`yawning`** | 1 | Visibly active yawning distension / mouth opening | Mouth region only |
| **`hand_over_mouth`** | 2 | Hand or fingers visibly covering/occluding the mouth region | Full head and face |
| **`drinking`** | 3 | Driver actively drinking from a bottle, cup, or can brought to the mouth | Hand + bottle together |
| **`phone_use`** | 4 | Driver holding handheld mobile phone to the ear in active call posture | Hand + phone at ear |

</div>

---

## 🔒 Core Benchmark Principles

1. **Controlled-Comparison Principle:** Identical 8/3/3 subject-disjoint partitions, unified single-frame $640 \times 640$ input format, identical training hyperparameters (batch size 1, 220 epochs, FP16, fixed seed 13), and identical GPU hardware across all evaluated architectures.
2. **100% Single-Pass Manual Human Ground Truth:** All 15,723 frames extracted at 1 FPS from 81 DMD videos are manually labeled once by an expert annotator in Label Studio, completely free of synthetic/pseudo labels or identity leakage.
3. **Strict Validation/Test Isolation:** Optimal model checkpoints and confidence thresholds ($\tau^*$) are selected strictly on the 3 validation subjects prior to a single-pass evaluation on the 3 unseen test subjects.
