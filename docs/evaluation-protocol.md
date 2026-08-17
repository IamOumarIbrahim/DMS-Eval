# Evaluation Protocol

[← Back to the DMS-Eval landing page](../README.md)

> [!NOTE]
> This document contains protocol information extracted from the DMS-Eval README. Frozen decisions and unresolved values retain their original status.

> **Jump to:** [Metrics](#frozen-metrics) · [Shared evaluator](#shared-evaluation-harness) · [Test usage](#validation--test-usage) · [Thresholding](#confidence-threshold-selection) · [Runtime](#runtime-profiling) · [Unresolved choices](#unresolved-choices)

- [x] Metrics, reporting granularity, shared evaluator, matching rules, and checkpoint selection are frozen.
- [x] Validation/test isolation and one final test pass are frozen.
- [x] Shared runtime hardware, batch size, test coverage, and median-latency reporting are frozen.
- [x] Confidence-threshold candidate generation, selection objective, matching rules, and tie-breaking procedure are frozen.
- [x] Native PyTorch + CUDA, FP16 inference, 10 warm-ups, model-only timing, and CUDA-event latency and throughput procedures are frozen.
- [ ] Exact CUDA, PyTorch, model-framework, and NVIDIA GPU-driver versions remain unresolved.

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
| **Runtime Efficiency** | Inference Latency (ms/image) | Full Test Set | Median model-inference latency; batch size 1; PyTorch CUDA events |
| | FPS / Throughput | Full Test Set | Report latency-derived FPS and separately measured continuous-test-set throughput |
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

<a id="runtime-profiling"></a>

### Runtime Profiling — 🧊 Frozen

* Final runtime benchmarking uses the **same NVIDIA RTX 4060 with 8 GB VRAM** for all three models.
* The common runtime backend is **native PyTorch + CUDA**.
* Runtime inference precision is **FP16** for YOLO11n, D-FINE-N, and YOLO26n.
* Runtime batch size is **1**.
* Runtime measurements cover the **entire test split**.
* The final test/runtime pass is performed **once**.
* Report **median inference latency** across the measured test images.
* Report both:
  * FPS derived from measured latency.
  * A separately measured throughput/FPS result.

> [!IMPORTANT]
> The primary runtime comparison does not use TensorRT, ONNX Runtime, OpenVINO, or another exported backend.

#### Warm-up Procedure

Before each model's timed runtime measurement, complete **10 untimed warm-up inference passes** under these conditions:

* Batch size: `1`
* Input: 640×640
* Backend: native PyTorch + CUDA
* Inference precision: FP16
* The warm-up passes are excluded from reported latency and throughput measurements.
* The identical procedure is applied to all three models.

#### Latency Timing Boundary

Latency measures **model inference only**.

Inside the latency timer:

* Model forward/inference execution

Outside the latency timer:

* Disk I/O
* Image/file loading
* External dataset preprocessing
* Annotation/evaluator logic
* Benchmark metric computation
* Other non-model work

The timing-boundary definition is identical for all three architectures.

#### Per-Image Latency Timing Method

1. Complete the 10 untimed warm-up passes.
2. Use PyTorch CUDA events around each timed model inference.
3. Synchronize appropriately before reading elapsed GPU time.
4. Record per-image inference latency.
5. Report the already-frozen **median latency** across the entire test split.

Unsynchronized Python wall-clock timing is not used for GPU latency.

#### Separate Throughput/FPS Procedure

1. Complete the 10 untimed warm-up passes.
2. Process the **entire test split continuously**.
3. Keep runtime batch size at `1`.
4. Measure **model inference only**.
5. Place one CUDA start event before the first timed inference.
6. Place one CUDA end event after the final timed inference.
7. Synchronize after the end event.
8. Obtain total elapsed GPU inference time.
9. Compute:

```text
throughput FPS = number of test images / total measured inference time in seconds
```

This result is reported separately from:

```text
latency-derived FPS
```

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

| Color | Still unresolved | What must be finalized | Claim affected |
| ----- | ---------------- | ---------------------- | -------------- |
| 🔴 | **Exact subject IDs / `splits.json`** | Freeze the exact 8 train / 3 validation / 3 test subjects after annotation makes subject-level target-cue distributions available; keep every subject strictly within one split. | **same training/test data**, **subject-disjoint test split** |
| 🟠 | **CUDA / PyTorch / model-framework / NVIDIA GPU-driver versions** | Record the exact software environment actually used for training and evaluation. | Supports reproducibility and the **same inference timing protocol** |
| 🟢 | **Exact validation-selected confidence thresholds** | Record the numerical threshold selected for YOLO11n, D-FINE-N, and YOLO26n using the frozen validation-only procedure. | Evaluation reporting; the shared selection procedure is already frozen |
| 🟢 | **Comparable FLOPs source/value** | Select comparable official/published 640×640 values for all three exact variants. | Deployment reporting; **not required for the fairness paragraph** |
| 🟢 | **Comparable model file-size source/artifact** | Define the comparable artifact/source used for all three models. | Deployment reporting; **not required for the fairness paragraph** |

**🔴 = must get right for the paragraph to remain literally true**
**🟠 = important protocol definition**
**🟢 = reproducibility/reporting; does not currently threaten the core fairness claim**

The **confidence-threshold search procedure is frozen**; only the three numerical thresholds produced from future validation predictions remain unresolved.

</details>
