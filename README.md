# DMS-Eval

**DMS-Eval** is a planned benchmark framework currently in development for evaluating nano-scale (lightweight) object detection architectures for detecting visual cues associated with driver drowsiness and distraction in real time across diverse cabin operating conditions.

![Status: In Development](https://img.shields.io/badge/Status-In_Development-orange?style=flat) [![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE) ![Input: 640×640](https://img.shields.io/badge/Input-640%C3%97640-555?style=flat) ![Detectors: YOLO | DETR](https://img.shields.io/badge/Detectors-YOLO%20%7C%20DETR-4c1?style=flat)

> **Benchmark Mission:** DMS-Eval establishes a standardized evaluation framework comparing real-time nano-scale object detectors (YOLO vs. DETR families) for in-cabin driver state monitoring under single-frame operational constraints.

## Table of Contents

* [🧊 Frozen Benchmark Scope](#-frozen-benchmark-scope)
* [Frame Extraction & Preprocessing](#frame-extraction--preprocessing)
* [Dataset Splits](#dataset-splits)
* [Annotation Format](#annotation-format)
* [Frame Naming](#frame-naming)
* [Target Warning Cues](#target-warning-cues)
* [Annotation Rules](#annotation-rules)
  * [General](#general)
  * [`eyes_closed`](#eyes_closed)
  * [`yawning`](#yawning)
  * [`head_down`](#head_down)
  * [`hand_over_mouth`](#hand_over_mouth)
  * [`phone_use`](#phone_use)
  * [`head_turned_away`](#head_turned_away)
* [Cue Categories & Visual Salience](#cue-categories--visual-salience)
* [Removed Classes](#removed-classes)
* [Annotation / Data Quality](#annotation--data-quality)
* [Training Protocol](#training-protocol)
* [Evaluation Protocol](#evaluation-protocol)
* [⚠️ Resolve Later / Unresolved](#️-resolve-later--unresolved)
* [Future Work](#future-work)
* [Authors & Credits](#authors--credits)
* [License](#license)

## 🧊 Frozen Benchmark Scope

| Setting | 🧊 Frozen value | Specification Notes |
| :--- | :--- | :--- |
| **Dataset** | DMD-derived dataset | Real-cabin RGB video sequences |
| **Models** | YOLO11n, D-FINE-N, YOLO26n | Nano-scale real-time detectors (YOLO vs. DETR) |
| **Input resolution** | 640×640 | Direct spatial crop |
| **Model input unit** | Individual image frames | Single static frame evaluation |
| **Source video frame rate** | 29.76 FPS | Normalized video capture rate |
| **Source video duration range** | 55.28–519.39 s | Variable naturalistic duration |
| **Frame sampling** | 1 frame every 1 second | Systematic 1 FPS temporal rate |
| **Sampling policy** | Fixed uniform sampling | Same sampling rule for every video |
| **Saved frame format** | JPG | Standard lossy compression |
| **Master annotation format** | COCO JSON | Single source of truth |
| **Master annotation files** | One COCO JSON for full dataset | `annotations.json` |
| **Split file format** | JSON | `splits.json` |
| **Train / val / test split** | 8 / 3 / 3 subjects | 57.1% / 21.4% / 21.4% whole-subject partition |
| **Split unit** | Individual / subject | Strictly subject-disjoint |
| **Split timing** | Finalized prior to training | Permanent partition freeze |

> [!NOTE]
> * **Proportional Frame Yield:** Longer videos naturally contribute more sampled frames than shorter videos due to the uniform 1 FPS temporal sampling across full video durations.
> * **Background / Negative Frames:** Frames containing none of the target warning cues remain valid negative samples to ensure robust false-positive evaluation.

## Frame Extraction & Preprocessing

### 🧊 Frozen

> Standardized spatial cropping and temporal sampling procedure:

| Preprocessing Parameter | 🧊 Frozen Value | Implementation Specification |
| :--- | :--- | :--- |
| **Source Video Frame Rate** | 29.76 FPS | Native temporal rate across synchronized streams |
| **Video Duration Range** | 55.28–519.39 s | Natural session lengths across 14 volunteer participants |
| **Temporal Sampling** | 1 frame / 1 second | Fixed uniform interval across all videos |
| **Saved Image Format** | JPG | Compressed standard image container |
| **Stored Image Resolution** | 640×640 | Direct benchmark model input dimension |
| **Spatial Cropping Target** | Driver-facing cabin region | Selected once on a reference frame; the exact same crop coordinates are reused for every video and subject |
| **Crop coordinate representation** | Source-image pixels | Stored directly as `(x, y, width, height)` |
| **Aspect Ratio Handling** | Direct spatial crop | Zero padding / letterboxing borders; zero non-uniform stretching |

> [!IMPORTANT]
> **Spatial Preprocessing Constraints:**
> * **No Letterboxing / Padding:** Zero gray/black padding borders are introduced.
> * **No Aspect-Ratio Stretching:** Image proportions are strictly preserved via direct spatial cropping.
> * **Dataset-wide fixed crop:** Once the crop geometry is finalized, it is applied unchanged to every source video and subject.

### Preprocessing Configuration

> Fixed cabin crop bounding coordinates are saved to:

```text
preprocessing.json
```

The configuration will contain source-image pixel values:

```text
x
y
width
height
```

#### ⚠️ Resolve Later

* Exact crop coordinates `(x, y, width, height)`.

## Dataset Splits

### 🧊 Frozen

> Subject-disjoint partition across **14 unique subjects**:

| Split | Subjects | Approx. proportion |
| :--- | ---: | ---: |
| Training | 8 | 57.1% |
| Validation | 3 | 21.4% |
| Test | 3 | 21.4% |

> [!WARNING]
> **Strict Subject-Disjoint Protocol:**
> * The split unit is the **individual/subject**, not individual frames or videos.
> * A participant may appear in **only one** split across all their videos and sampled frames to prevent identity leakage.
> * Subject assignments must be **finalized in `splits.json` before any model training begins** and must never be altered based on validation or benchmark performance.

### Subject Assignment Policy

* The 14 subjects are **not assigned purely at random**.
* Subject assignment to the frozen 8/3/3 partition will consider **target-cue representation**.
* The six frozen target cues should be kept **approximately balanced across training, validation, and test at the subject level**, while preserving strict subject disjointness.
* Exact subject IDs remain unresolved until the subject-level cue distribution is inspected.

### Split Manifest

> The final exact split partition will be frozen in:

```text
splits.json
```

The file will list subject IDs under:

```json
{
  "train": [],
  "validation": [],
  "test": []
}
```

> **Source of Truth:** Once finalized, the saved `splits.json` file permanently defines the benchmark splits without reliance on runtime random seeds.

#### ⚠️ Resolve Later

* Which specific subject IDs belong to each split.

## Annotation Format

### 🧊 Frozen

> Master annotation structure and data layout:

The benchmark uses **one master annotation format**. The dataset is annotated once, and model-specific formats are generated from that master annotation rather than maintaining separate manually created annotations for different models.

**Master Format:** `COCO JSON`

One COCO JSON file contains the annotations for the **entire dataset**.

```text
dataset/
├── images/
├── annotations.json
├── splits.json
└── preprocessing.json
```

The master COCO annotation file stores:

* Sampled image information
* Six target categories
* Bounding boxes
* Category IDs
* Annotation IDs
* Image IDs

> [!TIP]
> **Single Source of Truth:**
> Maintain only `annotations.json` as the ground-truth annotation artifact. Model-specific format converters (e.g., YOLO TXT or DETR formats) derive their inputs directly from this master file and `splits.json`.

## Frame Naming

### 🧊 Frozen

> Traceable, audit-ready naming schema encoding subject identity, source video, and absolute frame index:

Frame filenames must contain:

* Subject ID
* Video ID
* Original source frame number

```text
subject_07_video_03_frame_002980.jpg
```

> This preserves the origin of every sampled frame and makes the dataset fully auditable and traceable.

## Target Warning Cues

> The DMS-Eval benchmark targets **6 🧊 frozen visual warning cues** with specified bounding-box extents:

| 🧊 Frozen cue | Meaning | Bounding box |
| :--- | :--- | :--- |
| `eyes_closed` | Driver's eyes are visibly closed, including fully closed and visibly partially closed / heavy-lidded eyes | Separate box per eye |
| `yawning` | Driver is visibly yawning; an ordinary open mouth is not sufficient | Mouth region only |
| `head_down` | Head is clearly and substantially lowered/forward relative to normal forward-facing driving posture | Full head/face |
| `hand_over_mouth` | Hand visibly covers or occludes the mouth | Full head/face |
| `phone_use` | Driver is texting or actively interacting with a handheld phone; resting phones and phone calls are excluded | Hand + phone together |
| `head_turned_away` | Head is substantially turned left/right or away from the forward driving direction | Full head/face |

## Annotation Rules

### General

> [!IMPORTANT]
> **Static Frame Context & Co-occurrence:**
> * All target warning cues are judged using the **individual sampled frame only**. Surrounding video frames are not referenced.
> * A frame may contain **multiple target warning cues simultaneously** (e.g., `eyes_closed` alongside `hand_over_mouth`). In such cases, annotate all applicable cues; overlapping bounding boxes are fully permitted.

### `eyes_closed`

> Annotate when the driver's eyes are visibly fully closed, partially closed, or heavy-lidded.

* Each eye receives its **own separate bounding box**.
* **Prohibited:** A single bounding box spanning both eyes or a full-face box.
* The label is decided from the **single frame only** with no temporal blink filtering applied.

### `yawning`

> Annotate only when the sampled frame visibly depicts an active yawn.

* An ordinary open mouth is not automatically considered `yawning`.
* **Bounding Box Extent:** Mouth region only.
* `mouth_open` is **not** an independent class.

### `head_down`

> Annotate when the driver's head is clearly and substantially lowered/forward relative to a normal forward-facing driving posture.

* **Bounding Box Extent:** Full head/face.
* **Exclusions:** Minor downward movements or brief glances at the instrument cluster.
* `head_down` is used instead of `head_nodding` because `head_nodding` is an inherently multi-frame temporal event.

### `hand_over_mouth`

> Annotate when the driver's hand visibly covers or occludes the mouth.

* **Bounding Box Extent:** Full head/face.
* If another cue (e.g., `eyes_closed`) is also visible in the same frame, annotate **both cues**.

### `phone_use`

> Annotate when the driver is visibly texting or actively interacting with a handheld phone.

* **Bounding Box Extent:** Hand + phone together.
* **Exclusions:** Phones resting on seats, consoles, or dashboards, and hands-free phone calls.
* Focus is strictly on **active handheld interaction / texting**.

### `head_turned_away`

> Annotate when the driver's head is substantially turned left, right, or away from the road forward.

* **Bounding Box Extent:** Full head/face.

## Cue Categories & Visual Salience

> **Ontological Hierarchy:** Ranked from the most direct/unambiguous single-frame visual indicator to weaker/more ambiguous postural cues. *(Visual salience does not dictate expected model detection accuracy).*

| Behavioral Domain | Target Warning Cue | Salience Rank | Single-Frame Visual Trigger | Bounding Box Extent |
| :--- | :--- | :---: | :--- | :--- |
| **Drowsiness** | `eyes_closed` | 1 *(Highest)* | Visibly fully closed, partially closed, or heavy-lidded eyes | Separate box per eye |
| | `yawning` | 2 | Visible yawning with wide oral opening and facial elongation | Mouth region only |
| | `head_down` | 3 | Pronounced forward/downward head slouch | Full head/face |
| | `hand_over_mouth` | 4 *(Lowest)* | Hand visibly covering or occluding the mouth region | Full head/face |
| **Distraction** | `phone_use` | 1 *(Highest)* | Active handheld interaction or texting on smartphone | Hand + phone together |
| | `head_turned_away` | 2 *(Lowest)* | Head substantially rotated left, right, or away from the roadway | Full head/face |

## Removed Classes

> Deliberately excluded classes and merged concepts to eliminate label ambiguity:

| Excluded / Merged Candidate | Category Disposition | Rationale / Benchmark Decision |
| :--- | :--- | :--- |
| `eyes_open`, `drive_safe` | Background / Negative | Normal driving baselines; evaluated as true negatives rather than positive targets |
| `talk_passenger` | Removed | Substantial visual ambiguity and overlap with `head_turned_away` |
| `mouth_open` | Merged | Subsumed directly under `yawning` |
| `eyes_partially_closed` | Merged | Subsumed directly under `eyes_closed` |
| `hand_on_face` | Narrowed | Refined specifically to `hand_over_mouth` |
| `face_occluded` | Quality Flag | Handled as a data-quality / visibility condition rather than an object class |
| `drinking`, `smoking`, `eating` | Removed | Secondary non-core object interactions outside the 6-cue benchmark scope |
| `adjust_radio`, `switch_gear` | Removed | Momentary vehicle operation controls |
| `gaze_away`, `eye_rubbing` | Removed | Highly ambiguous in single static frames without temporal gaze tracking |
| `hands_off_wheel`, `hands_free` | Removed | Explicitly excluded from the current benchmark ontology |

## Annotation / Data Quality

### 🧊 Frozen

#### Ambiguous / uncertain cues

* If cue presence is ambiguous, do **not** annotate immediately.
* Flag the uncertain cue for **secondary review**.
* The frame remains in the dataset, but the unverified cue stays **out of the master COCO annotations** until resolved.
* All flagged cues must be settled before model training.

#### Partial occlusion and truncation

* Partially occluded cues remain annotatable if visibly identifiable.
* Bounding boxes must cover **only the visible portion** of the defined target region.
* **Never estimate, extrapolate, or invent hidden anatomical regions.**
* Targets truncated by the 640×640 boundary are annotated for their **visible area only**.
* Draw bounding boxes as tightly as practical around the visible target.

#### Small targets

* Small targets remain valid annotations as long as the cue is visually discernable at 640×640.
* No arbitrary minimum pixel cutoff is enforced.

#### Annotation consistency

* Perform a **second-pass review over the entire dataset** after initial annotation.
* Annotators must keep the class definition sheet accessible during labeling.
* Log unusual cases and edge-rule clarifications in an **annotation decision log** to ensure consistent multi-annotator decisions.

#### Class-choice behavior

* When cue presence is definite but the exact class is borderline, choose the category **immediately** rather than deferring to review.

#### Instance annotation rules

* Each distinct physical instance of a cue receives **one annotation box**.
* If multiple separate instances occur (e.g., both eyes closed), **each instance receives its own box**.

#### Unusable sampled frames

* Genuinely corrupt, blacked-out, or severely motion-blurred frames are **removed from the dataset**.
* Excluded frames must be logged in:

```text
excluded_frames.csv
```

The CSV contains:

```text
filename
exclusion_reason
```

> [!CAUTION]
> **Data Integrity Controls:**
> * **No Extrapolation:** Annotators must never draw boxes around occluded or out-of-frame anatomy.
> * **Strict Logging:** Any excluded frame must be logged with a concrete reason in `excluded_frames.csv` to ensure auditable dataset curation.

## Training Protocol

### 🧊 Frozen

> Shared training controls are frozen where architectural fairness requires a common rule. Architecture-specific optimization behavior remains model-specific where forcing one recipe across fundamentally different model families could unfairly disadvantage a model.

#### Initialization & Fine-Tuning

* **YOLO11n, D-FINE-N, and YOLO26n start from their official pretrained weights.**
* The models are **not trained from scratch**.
* All three models use **full-model fine-tuning** on the DMS-Eval training split.
* **No pretrained layers are intentionally frozen.**
* The pretrained starting points are **not assumed to be identical across architectures**. Their original pretraining datasets/setups may differ and must be documented transparently as part of the benchmark's reproducibility record and limitations.

#### Model-Specific Training Recipe

* Each model uses its **official/model-specific recommended training recipe**, except where DMS-Eval explicitly freezes a shared training control below.
* DMS-Eval does **not** force one common optimizer, learning rate, learning-rate schedule, weight decay, or augmentation policy across all architectures.
* **Data augmentation remains part of each model's official/model-specific training recipe.**
* The actual training settings used for each model must be **recorded and reported for reproducibility**.

#### Shared Training Controls

| Training Parameter | 🧊 Frozen Rule |
| :--- | :--- |
| **Maximum training epochs** | Same maximum epoch limit for all three models; exact value ⚠️ Resolve Later |
| **Early stopping** | Disabled for all three models |
| **Batch size** | `1` for all three models |
| **Gradient accumulation** | Disabled; one image produces one weight update before moving to the next image |
| **Training runs** | One training run per model; no multi-seed averaging |
| **Random seed** | Same seed for all three models; exact seed value ⚠️ Resolve Later |
| **Training hardware** | NVIDIA RTX 4060 with 8 GB VRAM for all three models |
| **Training precision** | Same precision mode for all three models; exact mode ⚠️ Resolve Later |
| **Data-loader workers** | Same worker count for all three models; exact count ⚠️ Resolve Later |

> [!IMPORTANT]
> The final checkpoint for each model is selected on validation data using the shared DMS-Eval evaluator. The test split is not used for checkpoint selection.

### Removed

* **Mandatory framework-level deterministic training mode** is not required.
* The shared random seed remains frozen, but strict bitwise-identical reruns are not required.

### ⚠️ Resolve Later

The following training values remain intentionally unfrozen:

* Exact shared maximum number of training epochs.
* Exact shared random seed value.
* Exact shared training precision mode.
* Exact shared data-loader worker count.

## Evaluation Protocol

### 🧊 Frozen Metrics

> Comprehensive multi-dimensional evaluation matrix:

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

### Reporting Structure

* **Overall test-set reporting:** `mAP@0.5:0.95`, `mAP@0.5`, Precision, Recall, F1-score, inference latency, FPS, Parameters, model file size, and FLOPs.
* **Per-class reporting:** `mAP@0.5:0.95` and `mAP@0.5` only.
* Per-class Precision, Recall, and F1-score are not currently included.

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

### Precision / Recall / F1 Matching Rules

* Precision, Recall, and F1-score use an **IoU threshold of 0.50**.
* Matching uses a **COCO-style one-to-one rule** within each image and class.
* Predictions are processed in descending confidence order.
* A normal ground-truth instance may be matched to at most one prediction.
* Additional duplicate detections for an already matched ground-truth instance count as false positives.
* The same matching procedure is applied identically to YOLO11n, D-FINE-N, and YOLO26n.

### Validation / Test Usage

* The **validation split** is used for model selection, checkpoint selection, and confidence-threshold selection.
* The **test split only** is used for final reported benchmark results.
* The test split must remain untouched until all training and model-selection decisions are complete.
* No training decision, checkpoint choice, confidence-threshold choice, or other tuning decision may be based on test-set performance.
* The final test evaluation is performed **once after the protocol and all validation-based model-selection decisions are frozen**.

> [!IMPORTANT]
> **Strict Validation/Test Isolation:**
> Never inspect or compute test-set metrics to guide hyperparameter selection, checkpoint filtering, or threshold sweeps. There is no returning to the test set for additional tuning after the final evaluation pass.

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

> The exact procedure used to generate/test candidate confidence thresholds remains ⚠️ **Resolve Later**.

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

### Deployment Profile Sources

* **Parameter counts:** use official published model information rather than independently recounting parameters.
* **Model file size:** use official/published information, but the exact comparable artifact/source for each model must be frozen before reporting.
* **FLOPs:** use official/published information rather than calculating FLOPs locally, but the exact comparable source/value for each model must be frozen before reporting.
* Published values must refer to **comparable model variants and measurement conditions** before they are placed side by side in the final benchmark table.

### Removed from Current Benchmark

* **Condition-wise evaluation** is removed from the current benchmark because the working dataset does not contain the required low-light/nighttime cabin footage.

## ⚠️ Resolve Later / Unresolved

> The following choices are intentionally **not frozen yet**. They must not be silently assumed during implementation.

| Benchmark Domain | ⚠️ Unresolved Parameter | Current State / Next Action |
| :--- | :--- | :--- |
| **Dataset Partitioning** | Exact split subject IDs | Assign specific subjects to the frozen 8 train / 3 validation / 3 test structure after inspecting subject-level cue representation |
| **Spatial Preprocessing** | Exact fixed crop geometry | Freeze source-pixel `(x, y, width, height)` in `preprocessing.json`; the representation and dataset-wide reuse rule are already frozen |
| **Model Training** | Maximum epoch count | Same maximum for all three models; exact count remains unfrozen |
| **Model Training** | Shared random seed | Same seed for all three models; exact value remains unfrozen |
| **Model Training** | Training precision mode | Same mode for all three models; exact mode remains unfrozen |
| **Model Training** | Data-loader worker count | Same worker count for all three models; exact count remains unfrozen |
| **Confidence Thresholding** | Candidate threshold search procedure | Highest validation F1 and tie-breakers are frozen; exact candidate-generation/search procedure remains unfrozen |
| **Runtime Profiling** | Inference precision | Exact runtime precision remains unfrozen |
| **Runtime Profiling** | Runtime backend | Native PyTorch vs. another common backend remains unfrozen |
| **Runtime Profiling** | Warm-up procedure | Number/procedure for inference warm-up runs remains unfrozen |
| **Runtime Profiling** | Timing boundary | Decide exactly what is included in timed inference, e.g. forward pass only versus a broader inference boundary |
| **Runtime Profiling** | Separate throughput/FPS procedure | Define the independent throughput measurement procedure |
| **Runtime Environment** | CUDA / framework / driver versions | Freeze exact CUDA, PyTorch/model-framework, GPU-driver, and relevant software versions |
| **Deployment Profile** | FLOPs source/value | Select comparable official/published GFLOPs information for each exact model variant at 640×640 |
| **Deployment Profile** | Model file-size source/artifact | Select comparable official/published file-size information and define which artifact is reported |

## Future Work

* **Low-light/nighttime evaluation** — out of scope for the current benchmark because the current dataset does not contain the required content.

> Future work may extend the ontology with cues deliberately outside the current benchmark scope:

* `reach_behind`
* `hair_makeup`
* `reach_side`
* `head_nodding` — temporal cue requiring multiple frames

## Authors & Credits

### Authors

* **Oumar Mamoun Ibrahim** (Senior Undergraduate Researcher)  
  Department of Computer Engineering, University of Sharjah  

  [![ORCID: Oumar](https://img.shields.io/badge/ORCID-0009--0008--0312--1605-A6CE39?logo=orcid&logoColor=white)](https://orcid.org/0009-0008-0312-1605)  
  📧 | [U22200741@sharjah.ac.ae](mailto:U22200741@sharjah.ac.ae)

* **Dr. Mohamad Khairi bin Ishak** (Associate Professor)  
  Department of Computer Engineering, University of Sharjah  

  [![ORCID: Dr. Mohamad](https://img.shields.io/badge/ORCID-0000--0002--3554--0061-A6CE39?logo=orcid&logoColor=white)](https://orcid.org/0000-0002-3554-0061)  
  📧 | [mishak@sharjah.ac.ae](mailto:mishak@sharjah.ac.ae)

### Acknowledgments

This benchmark builds upon the excellent work of the teams behind [YOLO11](https://docs.ultralytics.com/models/yolo11/), [D-FINE](https://github.com/Peterande/D-FINE), and [YOLO26](https://docs.ultralytics.com/models/yolo26/).

We sincerely thank their authors, contributors, and maintainers for making these architectures and their implementations available to the research community. Their work makes comparative studies such as **DMS-Eval** possible.

> [!NOTE]
> This research and codebase are prepared for submission to the 5th International Conference on Artificial Intelligence Science and Applications in Industry and Society (CAISAIS 2026), held November 25–27, 2026.

## License

This project is licensed under the **Apache License 2.0** — see the [LICENSE](LICENSE) file for details.