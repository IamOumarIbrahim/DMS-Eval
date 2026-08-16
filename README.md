# DMS-Eval

**DMS-Eval** is a planned benchmark framework currently in development for evaluating nano-scale (lightweight) object detection architectures for detecting visual cues associated with driver drowsiness and distraction in real time across diverse cabin operating conditions.

![Status: In Development](https://img.shields.io/badge/Status-In_Development-orange?style=flat) [![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE) ![Input: 640×640](https://img.shields.io/badge/Input-640%C3%97640-555?style=flat) ![Detectors: YOLO | DETR](https://img.shields.io/badge/Detectors-YOLO%20%7C%20DETR-4c1?style=flat)

> **Benchmark Mission:** DMS-Eval establishes a standardized evaluation framework comparing real-time nano-scale object detectors (YOLO vs. DETR families) for in-cabin driver state monitoring under single-frame operational constraints.

## Table of Contents

* [Frozen Benchmark Scope](#frozen-benchmark-scope)
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
* [Cue Categories](#cue-categories)
* [Cue Strength Ordering](#cue-strength-ordering)
* [Removed Classes](#removed)
* [Annotation / Data Quality](#annotation--data-quality)
* [Evaluation Protocol](#evaluation-protocol)
* [Resolve Later](#resolve-later)
* [Skipped / Unresolved Cue](#skipped--unresolved-cue)
* [Future Work](#future-work)
* [Authors & Credits](#authors--credits)
* [License](#license)

## Frozen Benchmark Scope

| Setting | Frozen value |
| :--- | :--- |
| Dataset | DMD-derived dataset |
| Models | YOLO11n, D-FINE-N, YOLO26n |
| Input resolution | 640×640 |
| Model input unit | Individual image frames |
| Source video frame rate | 29.76 FPS |
| Source video duration range | 55.28–519.39 s |
| Frame sampling | 1 frame every 1 second |
| Sampling policy | Same fixed sampling rule for every video |
| Saved frame format | JPG |
| Master annotation format | COCO JSON |
| Master annotation files | One COCO JSON for the full dataset |
| Split file format | JSON |
| Train / validation / test split | 8 / 3 / 3 subjects |
| Split unit | Individual/subject |
| Split policy | Fully subject-disjoint |
| Split timing | Finalized before any model training |

> [!NOTE]
> * **Proportional Frame Yield:** Longer videos naturally contribute more sampled frames than shorter videos due to the uniform 1 FPS temporal sampling across full video durations.
> * **Background / Negative Frames:** Frames containing none of the target warning cues remain valid negative samples to ensure robust false-positive evaluation.

## Frame Extraction & Preprocessing

### Frozen

> Standardized spatial cropping and temporal sampling procedure:

* Source videos run at **29.76 FPS**.
* Source video lengths range from approximately **55.28 s to 519.39 s**.
* Extract **1 frame every 1 second**.
* Use the **same sampling rule for every video**.
* Longer videos are allowed to produce more sampled frames than shorter videos.
* Extracted frames are saved as **JPG**.
* Frames are stored at **640×640** from the start.
* The source frame is **cropped** to target the driver-facing side of the image.
* The **same fixed crop area** is used for every video and every sampled frame.
* The crop is selected once using a representative driver-facing frame, and the resulting coordinates are reused across the entire dataset.

> [!IMPORTANT]
> **Spatial Preprocessing Constraints:**
> * **No Letterboxing / Padding:** Zero gray/black padding borders are introduced.
> * **No Aspect-Ratio Stretching:** Image proportions are strictly preserved via direct spatial cropping.

### Preprocessing Configuration

> Fixed cabin crop bounding coordinates saved to:

```text
preprocessing.json
```

The configuration will contain:

```text
x
y
width
height
```

#### Resolve Later

The following preprocessing details are not yet frozen:

* Exact crop coordinates.
* Whether the crop coordinates are stored directly in source-image pixels or another coordinate representation.

## Dataset Splits

### Frozen

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

### Split Manifest

> The exact split partition is frozen in:

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

> **Source of Truth:** The saved `splits.json` file permanently defines the benchmark splits without reliance on runtime random seeds.

#### Resolve Later

* Which specific subject IDs belong to each split.
* How the 14 subjects are assigned to the frozen 8/3/3 split, including whether assignment is random or considers cue representation.
* Whether the six target cues should be kept approximately balanced across train, validation, and test.

## Annotation Format

### Frozen

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

### Frozen

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

> The DMS-Eval benchmark targets **6 frozen visual warning cues** with specified bounding-box extents:

| Frozen cue | Meaning | Bounding box |
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

## Cue Categories

> Ontological breakdown of frozen cues by primary behavioral domain:

### Drowsiness-related

```text
eyes_closed
yawning
head_down
hand_over_mouth
```

### Attention/distraction-related

```text
phone_use
head_turned_away
```

## Cue Strength Ordering

> **Visual Salience Hierarchy:** Ranked from the most direct/unambiguous single-frame visual indicator to weaker/more ambiguous postural cues. *(Does not imply expected model detection accuracy).*

### Drowsiness-related

1. `eyes_closed`
2. `yawning`
3. `head_down`
4. `hand_over_mouth`

### Attention/distraction-related

1. `phone_use`
2. `head_turned_away`

## Removed

> The following classes are deliberately excluded from the current ontology to prevent ambiguity and maintain benchmark focus:

```text
gaze_away
eyes_open
drinking
smoking
eating
adjust_radio
talk_passenger
switch_gear
talk_left
talk_right
drive_safe
eye_rubbing
face_occluded
hand_on_face
```

> **Ontology Decisions & Merged Concepts:**
> * Only **meaningful warning cues** are target classes; normal driving states (`eyes_open`, `drive_safe`) are treated as background.
> * `talk_passenger` was removed due to substantial visual overlap with `head_turned_away`.
> * `mouth_open` is subsumed under `yawning` rather than isolated as a distinct class.
> * `eyes_partially_closed` is subsumed under `eyes_closed`.
> * `hand_on_face` was narrowed to `hand_over_mouth`.
> * `face_occluded` is treated as a data-quality flag rather than an object class.
> * `yawning` bounding box was restricted from full-face to **mouth region only**.
> * `hand_over_mouth` bounding box was expanded to **full head/face**.

## Annotation / Data Quality

### Frozen

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

## Evaluation Protocol

### Frozen Metrics

#### Detection quality

* **mAP@0.5:0.95** — primary detection metric.
* **mAP@0.5** — secondary detection metric.
* **Precision**
* **Recall**
* **F1-score**

> [!NOTE]
> DMS-Eval uses **mAP as the benchmark's detection-accuracy measure**. A separate generic classification `Accuracy` metric is not included.

#### Runtime performance

* **Inference latency (ms/image)**
* **FPS**

The exact runtime timing procedure remains unresolved.

#### Model / deployment characteristics

* **Parameters (M)**
* **Model file size (MB)**
* **FLOPs (G)**

### Reporting Structure

> Comprehensive multi-metric reporting schema on the test partition:

* **Overall test-set reporting:** mAP@0.5:0.95, mAP@0.5, Precision, Recall, F1-score, inference latency, FPS, Parameters, model file size, and FLOPs.
* **Per-class reporting:** mAP@0.5:0.95 and mAP@0.5 only.
* Per-class Precision, Recall, and F1-score are not currently included.

### Shared Evaluation Harness

> Architectural fairness guarantee via a unified ground-truth evaluation pipeline:

All benchmark models are evaluated using **one shared evaluation harness** rather than relying on each model repository's evaluator for the final reported metrics.

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

### Validation / Test Usage

* The **validation split** is used for model selection, checkpoint selection, and confidence-threshold selection.
* The **test split only** is used for final reported benchmark results.
* The test split must remain untouched until all training and model-selection decisions are complete.
* No training decision, checkpoint choice, confidence-threshold choice, or other tuning decision may be based on test-set performance.

> [!IMPORTANT]
> **Strict Validation/Test Isolation:**
> Never inspect or compute test-set metrics to guide hyperparameter selection, checkpoint filtering, or threshold sweeps. The test set is evaluated strictly once upon protocol freeze.

### Confidence-Threshold Selection

> Per-model validation-optimal F1 thresholding protocol:

Each model may use its **own confidence threshold**.

For each model:

1. Evaluate candidate confidence thresholds on the **validation split only**.
2. Select the threshold that gives the **highest overall F1-score** on the validation split using the shared evaluator.
3. Freeze that model-specific threshold.
4. Apply it unchanged to the test split for final Precision, Recall, and F1-score reporting.

### Checkpoint Selection

> Checkpoints are selected via highest validation `mAP@0.5:0.95` measured with the shared DMS-Eval evaluator prior to test evaluation.

### Removed from Current Benchmark

> **Condition-wise evaluation** is removed from the current benchmark because the working dataset does not contain the required low-light/nighttime cabin footage.

## Resolve Later

> Unfrozen implementation parameters scheduled for finalization prior to benchmark execution:

### Dataset

* Exact train/validation/test subject IDs.
* How the 14 subjects are assigned to the frozen 8/3/3 split.
* Whether cue distributions should be kept approximately similar across splits.
* Exact fixed driver-facing crop coordinates.
* Coordinate representation used inside `preprocessing.json`.

### Annotation / Data Quality

* Exact minimum visibility required before a partially occluded cue can be annotated.
* Whether the same physical region may receive two different class annotations when the boxes would overlap heavily.
* Any additional visibility or ambiguity rules not already defined above.

### Training

* Training epochs.
* Batch size.
* Optimizer.
* Learning rate.
* Learning-rate schedule.
* Weight decay.
* Initialization / pretrained weights policy.
* Early stopping.
* Data augmentation.
* Other training settings.

> [!NOTE]
> Checkpoint selection is no longer unresolved: it is frozen under [Evaluation Protocol](#evaluation-protocol).

### Evaluation

* Exact IoU threshold(s) used for threshold-controlled Precision / Recall / F1 matching.
* Exact object-detection matching rules.
* Exact runtime measurement procedure.
* Exact FPS measurement procedure.
* Exact latency measurement procedure.

> [!NOTE]
> Final evaluation metrics, confidence-threshold selection procedure, and evaluation harness are frozen under [Evaluation Protocol](#evaluation-protocol). Condition-wise evaluation is **removed from the current benchmark**, not unresolved.

### Compute / Runtime

* Hardware.
* GPU.
* CPU.
* RAM.
* Software environment.
* CUDA version.
* Framework versions.
* Inference backend.
* Inference precision.
* Batch size used for inference.
* Warm-up procedure.

## Skipped / Unresolved Cue

> Open cue candidate held in reserve:

```text
hands_off_wheel / hands_free
```

It remains unresolved unless explicitly reconsidered.

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