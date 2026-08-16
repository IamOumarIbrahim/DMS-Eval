# Project Schedule & Benchmark Paper Plan

**Related Pages:** `100-checklist`

---

## 1. Overview & Objective

- **Objective:** Write and submit a simple 6-page IEEE conference benchmark paper comparing lightweight object detection models for driver drowsiness and distraction cue detection.
- **Final Submission Deadline:** September 1, 2026 (Targeting submission on August 31, 2026).

### Authors
- **Oumar Mamoun Ibrahim** — [U22200741@sharjah.ac.ae](mailto:U22200741@sharjah.ac.ae)
- **Mohamad Khairi Bin Ishak** — [mishak@sharjah.ac.ae](mailto:mishak@sharjah.ac.ae)

---

## 2. Requirements & Important Deadlines

### Paper Requirements
- **Format:** 6-page IEEE two-column format (including references).
- **Plagiarism Ceiling:** Similarity index $\le 20\%$.
- **Content:** Must contain original research results or innovative applications.

### Conference Timeline
| Milestone / Event | Date |
| :--- | :--- |
| **Call for Papers** | May 15, 2026 |
| **Final Paper Submission** | September 1, 2026 |
| **Acceptance Notification** | October 15, 2026 |
| **Camera-Ready & Registration Deadline** | October 25, 2026 |
| **Conference Dates** | November 25–27, 2026 |

---

## 3. Scope & Research Definition

### Scope
- **Domain:** Benchmarking lightweight models in driver state monitoring (drowsiness and distraction).
- **Dataset Contribution:** Developing a custom unified benchmark dataset spanning **normal**, **distracted**, **fatigued/drowsy**, and **low-visibility nighttime** conditions.
- **Model Selection:** 3–4 lightweight detectors (including existing **YOLO11n** and **D-FINE** results plus 1–2 additional suitable lightweight models).

### Research Question (RQ)
> *"Under a controlled compute-constrained evaluation, how do lightweight object detectors compare in accuracy, inference efficiency, and robustness when detecting visual cues associated with driver distraction and drowsiness across normal and low-light driving conditions?"*

### Terminology & Scope Boundary Rule
- **Frame-Level Cues vs. Temporal Inference:** Strictly refer to targets as **visual cues associated with distraction/drowsiness**. Do *not* claim that a single frame clinically determines whether a driver "is drowsy." The benchmark is frame-level object/cue detection, not temporal driver-state inference.

---

## 4. Experimental Fairness & Evaluation Protocol

### Fairness & Control Matrix
All models receive:
- Identical training and test data partitions.
- Strictly subject-disjoint test splits.
- Standardized image resolution.
- Unified evaluation annotations & metric implementations.
- Identical evaluation hardware, numerical precision, batch size, and inference timing protocol.
- Strict test-set access policy (untouched until final evaluation).
- Architecture-specific training hyperparameters documented transparently rather than artificially forced to be identical.

### Evaluation Metrics
- **Detection & Classification:** mean Average Precision (mAP), Accuracy, Precision, Recall, F1-score.
- **Efficiency & Footprint:** Inference time (FPS / Latency), Parameter count, Model size.
- **Robustness:** Condition-wise breakdown (normal vs. low-light / nighttime, behavioral conditions).

---

## 5. Core Contributions & Target Conclusion

### Contributions
1. A controlled benchmark of 3–4 lightweight detectors.
2. A unified dataset/ontology covering normal, distraction, drowsiness-related cues, and low-light/night conditions.
3. Accuracy–efficiency comparison using mAP, precision, recall, F1, FPS/latency, parameters, and model size.
4. Condition-wise analysis showing where each architecture succeeds or fails.

### Conclusion Framing
- **Approved Framing:** *"Model A provides the highest detection accuracy, Model B provides the lowest latency, and Model C provides a different accuracy–efficiency trade-off; performance also changes substantially under low-light and specific behavioral conditions."*
- **Avoid:** Broad generalizations such as *"Model A is objectively the best lightweight driver-monitoring detector."*

---

## 6. Two-Week Execution Schedule

> **Strict Freeze Rule:** After **August 20**, no new dataset, model, metric, ontology, or benchmark design changes unless an existing choice is scientifically invalid.

| Date Range | Phase | Key Deliverables & Tasks |
| :--- | :--- | :--- |
| **Aug 16–17** | **Phase 1: Scope & Protocol Lock** | Freeze RQ, model choices, ontology, dataset sources, splits, and evaluator harness. |
| **Aug 18–20** | **Phase 2: Data Pipeline & Setup** | Finish annotation/conversion, leakage checks, dataset manifests, and training pipeline. *(Hard Freeze at end of Aug 20)* |
| **Aug 21–24** | **Phase 3: Training & Test Eval** | Train/retrain all 3–4 models; run untouched test-set evaluation. |
| **Aug 25** | **Phase 4: Analysis & Visuals** | Condition-wise evaluation, plots/tables generation, and error analysis. |
| **Aug 26–28** | **Phase 5: Manuscript Drafting** | Write the complete 6-page IEEE paper. |
| **Aug 29** | **Phase 6: Reproducibility Audit** | Reproducibility & fairness audit (no redesign unless an actual blocker is found). |
| **Aug 30** | **Phase 7: Final Polish & Review** | IEEE formatting check, reference validation, figures alignment, PDF checks, final PI review. |
| **Aug 31** | **Phase 8: Paper Submission** | Final submission ahead of the September 1, 2026 deadline. |

---

## 7. Audit & Validation Check (Ask Codex)

### Evaluation Query Prompt
> *"Does this experimental design support the specific claims made by RQ1, and are there any remaining issues that would materially bias the ranking or invalidate the comparison? Separate BLOCKERS from DISCLOSABLE LIMITATIONS and OPTIONAL IMPROVEMENTS. Do not penalize unavoidable architectural differences merely because the models are not identical."*

### Audit Rule
- If the audit identifies **zero blockers** and several disclosable limitations, proceed with writing and submission. Disclose limitations transparently in the paper.
