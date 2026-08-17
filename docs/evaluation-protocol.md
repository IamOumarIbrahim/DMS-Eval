# Evaluation Protocol

[← Back to the DMS-Eval landing page](../README.md)

> [!NOTE]
> This document contains protocol information extracted from the DMS-Eval README. Frozen decisions and unresolved values retain their original status.

> **Jump to:** [Metrics](#frozen-metrics) · [Shared evaluator](#shared-evaluation-harness) · [Test usage](#validation--test-usage) · [Thresholding](#confidence-threshold-selection) · [Runtime](#runtime-profiling--frozen-so-far) · [Unresolved choices](#unresolved-choices)

- [x] Metrics, reporting granularity, shared evaluator, matching rules, and checkpoint selection are frozen.
- [x] Validation/test isolation and one final test pass are frozen.
- [x] Shared runtime hardware, batch size, test coverage, and median-latency reporting are frozen.
- [x] Confidence-threshold candidate generation, selection objective, matching rules, and tie-breaking procedure are frozen.
- [ ] Exact runtime precision, backend, warm-up, timing boundary, throughput procedure, and environment remain unresolved.

---

<a id="frozen-metrics"></a>

### 🧊 Frozen Metrics

> Comprehensive multi-dimensional evaluation matrix:

<p align="center"><sub><b>Table 1.</b> Frozen detection, runtime, and deployment metrics.</sub></p>

| Dimension | Metric | Reporting Granularity | Optimization / Protocol Role |
| :--- | :--- | :--- | :--- |
| **Detection Quality** | `mAP@0.5:0.95` | Full Test Set & Per-Class | Primary benchmark accuracy metric; drives validation checkpoint selection |
| | `mAP@0.5` | Full Test Set & Per-Class | Secondary detection metric and first checkpoint tie-breaker |
| | Precision | Full Test Set | Evaluated at validation-optimal F1 confidence threshold using IoU = 0.50 |
| | Recall | Full Test Set | Evaluated at validation-optimal F1 confidence threshold using IoU = 0.50 |
| | F1-Score | Full Test Set | Primary criterion for per-model validation confidence-threshold selection |
| **Runtime Efficiency** | Inference Latency (ms/image) | Full Test Set | Median latency; batch size 1; exact timing boundary ⚠️ Resolve Later |
| | FPS / Throughput | Full Test Set | Report latency-derived FPS and separately measured throughput; exact separate procedure ⚠️ Resolve Later |
| **Deployment Profile** | Parameters (M) | Architectural | Use official published model parameter counts |
| | Model File Size (MB) | Architectural | Use published/official information; exact comparable artifact/source ⚠️ Resolve Later |
| | Computational Workload (GFLOPs) | Architectural | Use published/official information at 640×640; exact comparable source/value ⚠️ Resolve Later |

> [!NOTE]
> DMS-Eval uses **mAP as the benchmark's detection-accuracy measure**. A separate generic classification `Accuracy` metric is not included.

<details>
<summary><strong>Show reporting structure</strong></summary>

### Reporting Structure

* **Overall test-set reporting:** `mAP@0.5:0.95`, `mAP@0.5`, Precision, Recall, F1-score, inference latency, FPS, Parameters, model file size, and FLOPs.
* **Per-class reporting:** `mAP@0.5:0.95` and `mAP@0.5` only.
* Per-class Precision, Recall, and F1-score are not currently included.

</details>

### Shared Evaluation Harness

> Architectural fairness guarantee via a unified ground-truth evaluation pipeline:

All benchmark models are evaluated using **one shared evaluation harness** rather than relying on each model repository's evaluator for the final reported detection metrics.

The evaluation flow is:

```text
master COCO ground truth
        +
model predictions converted to a common COCO-style detection format
        ↓
shared DMS-Eval evaluator
        ↓
reported benchmark metrics
```

* The **master COCO annotations** are used directly as ground truth.
* Each model's predictions are converted into a **common COCO-style detection format** before evaluation.
* The shared evaluator is used for mAP, Precision, Recall, and F1-score.

<details>
<summary><strong>Show precision, recall, and F1 matching rules</strong></summary>

### Precision / Recall / F1 Matching Rules

* Precision, Recall, and F1-score use an **IoU threshold of 0.50**.
* Matching uses a **COCO-style one-to-one rule** within each image and class.
* Predictions are processed in descending confidence order.
* A normal ground-truth instance may be matched to at most one prediction.
* Additional duplicate detections for an already matched ground-truth instance count as false positives.
* The same matching procedure is applied identically to YOLO11n, D-FINE-N, and YOLO26n.

</details>

---

### Validation / Test Usage

* The **validation split** is used for model selection, checkpoint selection, and confidence-threshold selection.
* The **test split only** is used for final reported benchmark results.
* The test split must remain untouched until all training and model-selection decisions are complete.
* No training decision, checkpoint choice, confidence-threshold choice, or other tuning decision may be based on test-set performance.
* The final test evaluation is performed **once after the protocol and all validation-based model-selection decisions are frozen**.

> [!IMPORTANT]
> **Strict Validation/Test Isolation:**
> Never inspect or compute test-set metrics to guide hyperparameter selection, checkpoint filtering, or threshold sweeps. There is no returning to the test set for additional tuning after the final evaluation pass.

<details>
<summary><strong>Show confidence-threshold selection rule</strong></summary>

### Confidence-Threshold Selection

> Per-model validation-optimal F1 thresholding protocol:

Each model may use its **own confidence threshold**.

For each model:

1. Evaluate candidate confidence thresholds on the **validation split only**.
2. Select the threshold that gives the **highest overall F1-score** using the shared evaluator.
3. If multiple thresholds have the same highest F1-score, select the threshold with the **higher Precision**.
4. If Precision is also tied, select the **higher confidence threshold**.
5. Freeze that model-specific threshold.
6. Apply it unchanged to the test split for final Precision, Recall, and F1-score reporting.

</details>

### Checkpoint Selection

Final checkpoints are selected using validation results from the shared DMS-Eval evaluator in this order:

1. **Highest validation `mAP@0.5:0.95`.**
2. If tied, choose the checkpoint with the **higher validation `mAP@0.5`**.
3. If still tied, choose the checkpoint from the **later epoch**.

### Runtime Profiling — Frozen So Far

* Final runtime benchmarking uses the **same NVIDIA RTX 4060 with 8 GB VRAM** for all three models.
* Runtime batch size is **1**.
* Runtime measurements cover the **entire test split**.
* The final test/runtime pass is performed **once**.
* Report **median inference latency** across the measured test images.
* Report both:
  * FPS derived from measured latency.
  * A separately measured throughput/FPS result.
* Exact inference precision, backend, warm-up procedure, timing boundary, and separate throughput procedure remain unresolved.

<details>
<summary><strong>Show deployment-profile sources and removed condition-wise evaluation</strong></summary>

### Deployment Profile Sources

* **Parameter counts:** use official published model information rather than independently recounting parameters.
* **Model file size:** use official/published information, but the exact comparable artifact/source for each model must be frozen before reporting.
* **FLOPs:** use official/published information rather than calculating FLOPs locally, but the exact comparable source/value for each model must be frozen before reporting.
* Published values must refer to **comparable model variants and measurement conditions** before they are placed side by side in the final benchmark table.

### Removed from Current Benchmark

* **Condition-wise evaluation** is removed from the current benchmark because the working dataset does not contain the required low-light/nighttime cabin footage.

</details>

---

<details>
<summary><strong>Show frozen confidence-threshold candidate-generation section</strong></summary>

## Confidence-Threshold Candidate Generation

### 🧊 Frozen

Candidate confidence thresholds are derived from each model's **actual validation-set prediction confidence scores** rather than from a manually chosen fixed numerical grid.

For each of YOLO11n, D-FINE-N, and YOLO26n:

1. Generate predictions on the **validation split only**.
2. Extract the confidence scores produced by that model.
3. Use those validation prediction scores to define the candidate confidence thresholds evaluated for that model.
4. Evaluate every candidate threshold using the **same shared DMS-Eval evaluator**.
5. Select the threshold producing the **highest overall validation F1-score**.

The exact same threshold-search algorithm, F1 objective, matching rules, and tie-breaking procedure are applied to all three models.

### Confidence-Threshold Tie-Breaking

If multiple candidate thresholds produce the same highest validation F1-score:

1. Select the threshold with the **higher Precision**.
2. If Precision is also tied, select the **higher confidence threshold**.

The selected threshold is then frozen for that model and applied unchanged during the final test evaluation.

> [!NOTE]
> The numerical candidate thresholds do not need to be identical across models because they are derived from each model's own validation prediction scores. Fairness is maintained by applying the **same threshold-generation and selection procedure** to every model.

### ⚠️ Resolve Later

* Exact numerical confidence threshold selected for YOLO11n.
* Exact numerical confidence threshold selected for D-FINE-N.
* Exact numerical confidence threshold selected for YOLO26n.

</details>

---

<details>
<summary><strong>Show the complete unresolved-protocol table</strong></summary>

<a id="unresolved-choices"></a>

## ⚠️ Resolve Later / Unresolved

> The following choices are intentionally **not frozen yet**. They must not be silently assumed during implementation.

<p align="center"><sub><b>Table 2.</b> Unresolved protocol choices and the claims they affect.</sub></p>

| Color | Still unresolved                               | What must be finalized                                                                                                | Claim affected                                                    |
| ----- | ---------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------- |
| 🔴    | **Exact subject IDs / `splits.json`**          | Freeze the exact 8 train / 3 validation / 3 test subjects before training and use the identical split for all models. | **same training/test data**, **subject-disjoint test split**      |
| 🔴    | **Exact crop coordinates**                     | Freeze one `(x, y, width, height)` crop and apply it identically to every model.                                      | **same training/test data**, **image resolution**                 |
| 🔴    | **Training numerical precision**               | Choose one training precision mode and use it for all three models.                                                   | **same numerical precision**                                      |
| 🔴    | **Runtime inference precision**                | Choose one inference precision and use it for all three runtime evaluations.                                          | **same numerical precision**                                      |
| 🔴    | **Runtime backend**                            | Freeze one common execution/backend basis for runtime comparison.                                                     | **same inference timing protocol**                                |
| 🔴    | **Warm-up procedure**                          | Freeze the same warm-up procedure for every model.                                                                    | **same inference timing protocol**                                |
| 🔴    | **Timing boundary**                            | Define exactly what operations are inside the latency timer and apply that definition identically.                    | **same inference timing protocol**                                |
| 🔴    | **Separate throughput/FPS procedure**          | Define one identical procedure for independently measuring throughput/FPS.                                            | **same inference timing protocol**                                |
| 🟠    | **Exact maximum epoch count**                  | Choose the common maximum training budget for all three models.                                                       | **shared training-budget controls**                               |
| 🟠    | **CUDA / framework / GPU-driver versions**     | Freeze and record the software environment used for the benchmark.                                                    | Supports **same hardware / timing protocol**                      |
| 🟢    | **Exact shared random seed**                   | Choose one value and use it for every model.                                                                          | Reproducibility                                                   |
| 🟢    | **Data-loader worker count**                   | Choose one worker count and use it for every model.                                                                   | Reproducibility                                                   |
| 🟢    | **Comparable FLOPs source/value**              | Select comparable official/published 640×640 values for all three exact variants.                                     | Deployment reporting; **not required for the fairness paragraph** |
| 🟢    | **Comparable model file-size source/artifact** | Define the comparable artifact/source used for all three models.                                                      | Deployment reporting; **not required for the fairness paragraph** |

**🔴 = must get right for the paragraph to remain literally true**
**🟠 = important protocol definition**
**🟢 = reproducibility/reporting; does not currently threaten the core fairness claim**

The **confidence-threshold search procedure is no longer on this table** because we froze it.

</details>
