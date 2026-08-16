# Execution Timeline & Delivery Checklist

**Project:** DMS-Eval — Controlled Lightweight Object Detection Benchmark for Driver Monitoring Systems  
**Target Venue:** CAISAIS 2026 (5th International Conference on Artificial Intelligence Science and Applications in Industry and Society)  
**Submission Deadline:** September 1, 2026 (23:59 AoE)  
**Execution Window:** August 16, 2026 – August 31, 2026  
**Evaluated Models:** YOLO11n, D-FINE-N, YOLO26n (3 Frozen Architectures)  
**Hardware Baseline:** NVIDIA GeForce RTX 4060 (8 GB VRAM)

---

## Executive Summary & Milestones

| Date Range | Phase | Primary Objective & Critical Deliverables | Gate / Milestone | Status |
| :--- | :--- | :--- | :--- | :---: |
| **Aug 16–17** | **Phase 1: Scope & Protocol Lock** | Freeze RQ, model choices, ontology, dataset sources, splits, and evaluator harness. | **Protocol Freeze** | In Progress |
| **Aug 18–20** | **Phase 2: Data Pipeline & Setup** | Finish annotation/conversion, leakage checks, dataset manifests, and training pipeline. | **Data & Environment Hard Freeze (Aug 20)** | Planned |
| **Aug 21–24** | **Phase 3: Training & Test Eval** | Train/retrain all 3 models; run untouched test-set evaluation. | **Model Weights & Raw Eval Lock** | Planned |
| **Aug 25** | **Phase 4: Analysis & Visuals** | Condition-wise evaluation, plots/tables generation, and error analysis. | **Results & Visuals Freeze** | Planned |
| **Aug 26–28** | **Phase 5: Manuscript Drafting** | Write the complete 6-page IEEE paper. | **Draft Complete (V1.0)** | Planned |
| **Aug 29** | **Phase 6: Reproducibility Audit** | Reproducibility & fairness audit (no redesign unless an actual blocker is found). | **Audit Sign-Off** | Planned |
| **Aug 30** | **Phase 7: Final Polish & Review** | IEEE formatting check, reference validation, figures alignment, PDF checks, final PI review. | **Final Camera-Ready Check** | Planned |
| **Aug 31** | **Phase 8: Paper Submission** | Final submission ahead of the September 1, 2026 deadline. | **Paper Submitted** | Planned |

---

## Detailed Phase-by-Phase Execution Checklist

### Phase 1: Scope & Protocol Lock (Aug 16–17)

**Goal:** Formally freeze the research question, architectural candidates, dataset boundaries, unified annotation ontology, and evaluation harness to prevent scope creep.

- [x] **Research Question & Scope Definition:**
  - [x] Lock Research Question to frame-level observable cues across normal and low-light/nighttime conditions under compute constraints.
  - [x] Enforce non-negotiable Fairness Principles (identical data exposure, identical hardware/preprocessing, zero test set tuning).
  - [x] Restrict benchmark boundaries to 2D frame-level cue detection, explicitly excluding temporal driver-state inference.
- [x] **Model Scope Lock:**
  - [x] Select and freeze 3 lightweight candidate architectures: **YOLO11n**, **D-FINE-N**, and **YOLO26n**.
  - [x] Designate YOLOv12n (Turbo) exclusively to Future Work.
- [x] **Dataset & Ontology Definition:**
  - [x] Lock 6-class unified ontology: Drowsiness cues (`eyes_open`, `eyes_closed`, `yawning`) + Distraction cues (`cellphone`, `bottle`, `hair_comb`).
  - [x] Define subject-disjoint split specification: 14 total DMD subjects (8 Train / 3 Val / 3 Test).
  - [x] Map the 4 target operating conditions: normal daylight, distracted, fatigued/drowsy, and low-light/nighttime.
- [x] **Phase 1 Deliverables & Sign-Off:**
  - [x] Lock protocol specification in [`docs/benchmark/benchmark-protocol.md`](../benchmark/benchmark-protocol.md).
  - [x] Document evaluated model catalog in [`docs/benchmark/models.md`](../benchmark/models.md).
  - [x] Establish execution timeline and milestones in [`docs/experiments/execution-timeline.md`](execution-timeline.md).
  - [x] Synchronize repository [`README.md`](../../README.md) specification and LaTeX [`manuscript/main.tex`](../../manuscript/main.tex) headers.

---

### Phase 2: Data Pipeline & Environment Setup (Aug 18–20)

**Goal:** Establish reproducible data extraction, label conversion, leakage validation, and training harnesses across all 3 candidate models.

- [ ] **Data Ingestion & Annotation Conversion:**
  - [ ] Extract and index raw DMD video streams across Face and Body RGB camera angles.
  - [ ] Convert source annotations into standardized YOLO (`.txt`) and COCO (`.json`) bounding box formats.
  - [ ] Generate immutable train, validation, and test dataset manifests (`train.txt`, `val.txt`, `test.txt`).
- [ ] **Leakage & Partition Validation:**
  - [ ] Run automated subject-disjoint verification: Assert zero subject ID overlap between train, val, and test partitions.
  - [ ] Run video-sequence isolation check: Assert all frames from a single driving session remain confined to one split.
  - [ ] Validate bounding box coordinate ranges ($0.0 \le x, y, w, h \le 1.0$) and class ID mappings ($0$–$5$).
- [ ] **Training & Profiling Environment Preparation:**
  - [ ] Configure training harnesses for YOLO11n, D-FINE-N, and YOLO26n initialized from official COCO-pretrained weights.
  - [ ] Standardize $640\times640$ input resolution and matching data augmentation pipelines.
  - [ ] Validate CUDA/PyTorch acceleration and establish inference latency profiling harness on NVIDIA RTX 4060.
- [ ] **Phase 2 Hard Freeze (End of Aug 20):**
  - [ ] Compute and record SHA-256 checksums for dataset manifests and label files.
  - [ ] Lock training scripts and dependency environment (`requirements.txt`).

---

### Phase 3: Model Training & Untouched Test Evaluation (Aug 21–24)

**Goal:** Train all 3 candidate models to convergence under standardized budgets, select best checkpoints using validation data only, and execute single-pass evaluation on the untouched held-out test set.

- [ ] **Model Training (Aug 21–23):**
  - [ ] Train **YOLO11n** under standardized effective batch size and epoch budget.
  - [ ] Train **D-FINE-N** with native loss functions and architecture-recommended optimizer settings.
  - [ ] Train **YOLO26n** with native end-to-end regression loss.
  - [ ] Log telemetry: Training loss curves, validation mAP per epoch, peak VRAM, and step time.
- [ ] **Validation Selection & Operating Point Lock (Aug 23–24):**
  - [ ] Select best checkpoint per model strictly based on validation $\text{AP}_{50:95}$.
  - [ ] Determine standardized confidence and IoU operating thresholds using the validation set only.
- [ ] **Single-Pass Untouched Test Set Evaluation (Aug 24):**
  - [ ] Execute single-pass evaluation on the held-out test set ground truth.
  - [ ] Compute primary detection metrics: $\text{AP}_{50:95}$, $\text{AP}_{50}$, Precision, Recall, F1, and Balanced Accuracy.
  - [ ] Measure deployment efficiency: Model latency distributions (median and p95 ms), pipeline throughput (FPS), peak memory (MB), and on-disk weight size (MB).

---

### Phase 4: Condition-Wise Analysis, Visuals & Diagnostics (Aug 25)

**Goal:** Compute condition-specific slice breakdowns, safety diagnostic metrics, and generate publication-quality figures and tables.

- [ ] **Stratified Slice Evaluation:**
  - [ ] Evaluate environmental robustness slice: Compare $\text{AP}_{50:95}$ and F1 on Normal Daylight vs. Low-Light/Nighttime subsets.
  - [ ] Evaluate behavioral slices: Disaggregate detection metrics across Normal, Distracted, and Drowsy/Fatigued driving episodes.
  - [ ] Evaluate class granularity: Compare small face cues (`eyes_closed`, `yawning`) against larger handheld objects (`cellphone`, `bottle`).
- [ ] **Safety Diagnostic Metrics:**
  - [ ] Calculate False Positives per Normal Image (FP/image) to quantify nuisance trip and driver alert fatigue risk.
- [ ] **Visual Asset & Plot Generation:**
  - [ ] Plot Precision-Recall curves across all 3 evaluated architectures.
  - [ ] Generate Latency vs. $\text{AP}_{50:95}$ Pareto frontier scatter plots.
  - [ ] Export qualitative detection comparison crops highlighting normal vs. low-light success and failure modes.

---

### Phase 5: Complete Manuscript Drafting (Aug 26–28)

**Goal:** Author a complete, self-contained 6-page IEEE format research paper adhering strictly to conference guidelines.

- [ ] **Day 1: Abstract, Introduction & Related Work (Aug 26):**
  - [ ] Write Abstract, keywords, automotive DMS background, and real-time embedded compute constraints.
  - [ ] Draft Introduction outlining candidate paradigms (CSP, DETR, NMS-free) and 4 core planned contributions.
  - [ ] Write Related Work reviewing lightweight detectors, DMS benchmarks, and illumination challenges.
- [ ] **Day 2: Methodology & Experimental Protocol (Aug 27):**
  - [ ] Document custom unified benchmark dataset, 14-subject disjoint partitioning, and 4 operating conditions.
  - [ ] Document Fairness & Control Matrix, hardware configuration, and evaluation metric definitions.
  - [ ] Detail candidate detector architectural specifications and training protocols.
- [ ] **Day 3: Results, Discussion & Conclusion (Aug 28):**
  - [ ] Populate Table 5 (Detection Quality & Robustness) and Table 6 (Inference Efficiency & Footprint).
  - [ ] Draft Discussion analyzing accuracy–speed Pareto trade-offs and low-light degradation characteristics.
  - [ ] Write Conclusion, Limitations, and Future Work (attention-based YOLOv12n, temporal integration).

---

### Phase 6: Reproducibility & Fairness Audit (Aug 29)

**Goal:** Conduct an independent verification of all experimental claims, scripts, data hashes, and manuscript statements.

- [ ] **Audit Verification Checklist:**
  - [ ] Verify dataset manifest integrity: Confirm zero subject leakage and zero sequence overlap across splits.
  - [ ] Verify test set isolation: Confirm no model hyperparameters, thresholds, or architectures were altered post-test evaluation.
  - [ ] Verify numerical exactness: Confirm all numbers in Table 5, Table 6, and LaTeX text match evaluation logs exactly.
  - [ ] Verify hardware reproducibility: Confirm timing reproducibility on the standardized NVIDIA RTX 4060 environment.
- [ ] **Audit Sign-Off:**
  - [ ] Sign off on experimental fairness (no redesign or re-evaluation permitted unless a fatal blocker is identified).

---

### Phase 7: Final Polish, Verification & PI Sign-Off (Aug 30)

**Goal:** Finalize manuscript formatting, check IEEE compliance, validate references, and complete senior co-author / PI review.

- [ ] **IEEE Conference Compliance Checks:**
  - [ ] Enforce strict 6-page limit in IEEEtran format.
  - [ ] Check column balances, figure alignments, typography, and caption formatting.
- [ ] **Bibliography & Reference Validation:**
  - [ ] Verify all citations in `manuscript/bib/references.bib` for complete metadata (DOIs, authors, venue names).
- [ ] **PDF Artifact Inspection:**
  - [ ] Compile LaTeX source via `pdflatex` / `bibtex` and inspect output PDF.
  - [ ] Resolve all overfull/underfull `\hbox` warnings and layout anomalies.
- [ ] **Co-Author & PI Sign-Off:**
  - [ ] Final manuscript review and approval with Associate Professor Dr. Mohamad Khairi bin Ishak.

---

### Phase 8: Paper Submission (Aug 31)

**Goal:** Submit the final manuscript, metadata, and supplementary artifacts to the CAISAIS 2026 conference portal ahead of the deadline.

- [ ] **Submission Portal Preparation:**
  - [ ] Validate author metadata, affiliations, ORCIDs, paper title, and abstract in conference submission system.
  - [ ] Perform upload check of the compiled PDF manuscript in the portal viewer.
- [ ] **Submission Execution:**
  - [ ] Complete formal submission by **August 31, 2026** (24 hours ahead of the September 1 AoE deadline).
- [ ] **Repository & Artifact Archival:**
  - [ ] Tag Git release commit (`v1.0.0-paper-submission`).
  - [ ] Archive trained model weights, evaluation logs, and visual assets.
