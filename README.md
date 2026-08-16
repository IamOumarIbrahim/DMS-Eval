# DMS-Eval

**DMS-Eval** is a planned benchmark framework currently in development for evaluating nano-scale (lightweight) object detection architectures for detecting visual cues associated with driver drowsiness and distraction in real time across diverse cabin operating conditions.

![Status: In Development](https://img.shields.io/badge/Status-In_Development-orange?style=flat) [![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE) ![Input: 640×640](https://img.shields.io/badge/Input-640%C3%97640-555?style=flat) ![Detectors: YOLO | DETR](https://img.shields.io/badge/Detectors-YOLO%20%7C%20DETR-4c1?style=flat)

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

Longer videos are allowed to contribute more sampled frames than shorter videos.

Frames are sampled systematically across the **full videos**, rather than selecting only frames containing target cues.

Frames containing none of the target warning cues remain valid **background / negative frames**.

## Frame Extraction & Preprocessing

### Frozen

The source videos are processed using the following rules:

* Source videos run at **29.76 FPS**.
* Source video lengths range from approximately **55.28 s to 519.39 s**.
* Extract **1 frame every 1 second**.
* Use the **same sampling rule for every video**.
* Longer videos are allowed to produce more sampled frames than shorter videos.
* Extracted frames are saved as **JPG**.
* Frames are stored at **640×640** from the start.
* **No padding / letterboxing** is used.
* **No stretching** is used.
* The source frame is instead **cropped**.
* The crop targets the **driver-facing side of the image**.
* The **same fixed crop area** is used for every video and every sampled frame.
* The crop is selected once using a representative driver-facing frame.
* The resulting crop coordinates are reused across the entire dataset.

### Preprocessing Configuration

The fixed crop configuration will be stored in:

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

The dataset contains **14 unique subjects**.

The dataset will be divided into:

| Split | Subjects | Approx. proportion |
| :--- | ---: | ---: |
| Training | 8 | 57.1% |
| Validation | 3 | 21.4% |
| Test | 3 | 21.4% |

The split unit is the **individual/subject**, not individual frames or individual videos.

The splits must be **fully subject-disjoint**:

* A person may appear in **only one** split.
* The same individual cannot appear in both training and validation.
* The same individual cannot appear in both training and testing.
* The same individual cannot appear in both validation and testing.
* All videos belonging to one person must remain in the same split.
* All sampled frames from that person must therefore remain in the same split.

This prevents identity leakage between training, validation, and testing.

The subject split must be **finalized before any model training begins**.

The split must not later be changed because of model performance or benchmark results.

### Split Manifest

The exact split assignments will be saved in:

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

The saved `splits.json` file is the **source of truth** for subject assignments.

A random seed is **not required** because the saved split file itself permanently records the selected subjects.

#### Resolve Later

* Which specific subject IDs belong to each split.
* How the 14 subjects are assigned to the frozen 8/3/3 split, including whether assignment is random or considers cue representation.
* Whether the six target cues should be kept approximately balanced across train, validation, and test.

## Annotation Format

### Frozen

The benchmark will use **one master annotation format**.

The dataset is annotated once, and model-specific formats are generated from that master annotation rather than maintaining separate manually created annotations for different models.

The master format is:

**COCO JSON**

One COCO JSON file will contain the annotations for the **entire dataset**.

Conceptually:

```text
dataset/
├── images/
├── annotations.json
├── splits.json
└── preprocessing.json
```

The master COCO annotation file stores:

* sampled image information
* the six target categories
* bounding boxes
* category IDs
* annotation IDs
* image IDs

The separate `splits.json` determines which subjects belong to training, validation, and testing.

Model-specific annotation files may later be generated from the master COCO annotations when required.

## Frame Naming

### Frozen

Frame filenames must contain:

* subject ID
* video ID
* original source frame number

Example:

```text
subject_07_video_03_frame_002980.jpg
```

This preserves the origin of every sampled frame and makes the dataset easier to trace and audit.

## Target Warning Cues

There are currently **6 frozen target warning cues**.

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

All target warning cues are judged using the **individual sampled frame only**.

Surrounding video frames are **not** used to determine the ground-truth class.

A frame may contain **multiple target warning cues simultaneously**.

When two or more cues are clearly visible:

* annotate all applicable cues
* overlapping bounding boxes are allowed

### `eyes_closed`

Annotate when the driver's eyes are visibly:

* fully closed
* visibly partially closed
* heavy-lidded

Each eye receives its **own separate bounding box**.

Do not use:

* one box around both eyes
* a full-face box

The label is decided from the **single frame only**.

No temporal blink-filtering rule is used because the benchmark model receives individual frames rather than video sequences.

### `yawning`

Annotate only when the sampled frame **visibly shows a yawn**.

An ordinary open mouth is not automatically considered `yawning`.

Bounding box:

**Mouth region only**

`mouth_open` is **not** a separate class.

### `head_down`

Annotate when the driver's head is **clearly and substantially lowered/forward** relative to normal forward-facing driving posture.

Bounding box:

**Full head/face**

Do not annotate:

* minor downward movement
* small downward glances

`head_down` is used instead of `head_nodding` because `head_nodding` requires temporal information across multiple frames.

### `hand_over_mouth`

Annotate when the driver's hand visibly covers or occludes the mouth.

Bounding box:

**Full head/face**

If another cue such as `eyes_closed` is also clearly visible in the same frame, annotate **both cues**.

### `phone_use`

Annotate when the driver is visibly:

* texting
* actively interacting with a phone held in the hand

Bounding box:

**Hand + phone together**

Do not annotate:

* a phone resting on the seat
* a phone on the center console
* a phone on the dashboard
* a phone near the gear area
* other non-interacted-with phones
* phone calls

The current class is specifically focused on **active handheld interaction / texting**.

### `head_turned_away`

Annotate when the driver's head is substantially turned:

* left
* right
* away from the forward driving direction

Bounding box:

**Full head/face**

## Cue Categories

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

This ordering represents the **strongest/directest visual warning cue to the weakest/more ambiguous cue from a single frame**.

It does **not** represent expected model accuracy.

### Drowsiness-related

1. `eyes_closed`
2. `yawning`
3. `head_down`
4. `hand_over_mouth`

### Attention/distraction-related

1. `phone_use`
2. `head_turned_away`

## Removed

The following classes are deliberately excluded from the current ontology and should not be reintroduced unless explicitly reconsidered:

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

Additional decisions:

* Only **meaningful warning cues** are target classes.
* Normal-state classes are not included.
* `eyes_open` remains background rather than a warning class.
* `talk_passenger` was removed because it substantially overlaps with `head_turned_away`.
* `mouth_open` is handled under `yawning`, not as a separate class.
* `eyes_partially_closed` is handled under `eyes_closed`, not as a separate class.
* `hand_on_face` was rejected in favor of the more specific `hand_over_mouth`.
* `face_occluded` is treated as an annotation/visibility issue rather than a target warning cue.
* The previous temporal ±5-frame blink-check rule for `eyes_closed` has been removed.
* The previous full-face/head annotation rule for `yawning` has been replaced by a **mouth-only box**.
* The previous hand + mouth annotation rule for `hand_over_mouth` has been replaced by a **full head/face box**.

## Annotation / Data Quality

### Frozen

#### Ambiguous / uncertain cues

* If the presence of a cue is uncertain or ambiguous, do **not** make a final annotation immediately.
* Flag the uncertain cue for **later review**.
* The frame itself remains in the dataset.
* The uncertain cue stays **out of the master COCO annotations** until it is reviewed.
* After review, the cue is either accepted and annotated or rejected and left unannotated.
* All flagged uncertain cues must be resolved before the affected image is used for training.

#### Partial occlusion and truncation

* A partially occluded cue may still be annotated when it is visibly identifiable.
* Bounding boxes must cover **only the visible portion** of the defined target region.
* **Never estimate, extrapolate, or invent hidden portions** of the target.
* If a target is cut off by the 640×640 image/crop boundary but the cue remains visibly identifiable, annotate the **visible portion only**.
* Bounding boxes should be drawn **as tightly as practical** around the visible target region with minimal extra background.

#### Small targets

* Very small targets should still be annotated if the cue is visibly identifiable in the 640×640 image.
* No minimum pixel-size threshold is currently required.

#### Annotation consistency

* Perform a **second review pass over the full dataset** after annotation is complete.
* During this pass, review labels and bounding boxes for consistency and correct mistakes before finalizing the master COCO annotations.
* A separate mandatory missed-cue audit of every image is **not** required.
* Keep the six class definitions visible as a **reference sheet** while annotating.
* Keep an **annotation decision log** for unusual examples, borderline cases, and rule clarifications.
* Use that log during annotation and the second review pass to maintain consistent decisions.

#### Class-choice behavior

* If a cue is clearly present but there is uncertainty about **which class** it belongs to, choose the class **immediately** rather than flagging class choice for later review.
* This is different from uncertain **cue presence**, which remains flagged for later review.

#### Instance annotation rules

* One visible instance of a cue receives **one annotation box for that class**.
* Do not create duplicate boxes for the same instance.
* If multiple separate instances of the same class are visible, **each instance receives its own bounding box**.
* This includes the existing `eyes_closed` rule: each visible closed eye is a separate instance.

#### Unusable sampled frames

* Genuinely unusable sampled frames are **removed from the dataset**.
* Examples include corrupted frames, completely black frames, and frames so severely blurred that reliable annotation is impossible.
* Every removed unusable frame must be logged in:

```text
excluded_frames.csv
```

The CSV must contain at least:

```text
filename
exclusion_reason
```

## Evaluation Protocol

### Frozen Metrics

#### Detection quality

* **mAP@0.5:0.95** — primary detection metric.
* **mAP@0.5** — secondary detection metric.
* **Precision**
* **Recall**
* **F1-score**

DMS-Eval uses **mAP as the benchmark's detection-accuracy measure**. A separate generic `Accuracy` metric is not included.

#### Runtime performance

* **Inference latency (ms/image)**
* **FPS**

The exact runtime timing procedure remains unresolved.

#### Model / deployment characteristics

* **Parameters (M)**
* **Model file size (MB)**
* **FLOPs (G)**

### Reporting Structure

* **Overall test-set reporting:** mAP@0.5:0.95, mAP@0.5, Precision, Recall, F1-score, inference latency, FPS, Parameters, model file size, and FLOPs.
* **Per-class reporting:** mAP@0.5:0.95 and mAP@0.5 only.
* Per-class Precision, Recall, and F1-score are not currently included.

### Shared Evaluation Harness

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

### Confidence-Threshold Selection

Each model may use its **own confidence threshold**.

For each model:

1. Evaluate candidate confidence thresholds on the **validation split only**.
2. Select the threshold that gives the **highest overall F1-score** on the validation split using the shared evaluator.
3. Freeze that model-specific threshold.
4. Apply it unchanged to the test split for final Precision, Recall, and F1-score reporting.

### Checkpoint Selection

For each model, select the final checkpoint using the **highest validation mAP@0.5:0.95**, measured using the shared DMS-Eval evaluator.

The selected checkpoint is then used for final test evaluation.

### Removed from Current Benchmark

**Condition-wise evaluation** is removed from the current benchmark.

The current dataset does not contain the required low-light/nighttime content, so low-light/nighttime evaluation is not part of the current paper.

## Resolve Later

The following benchmark decisions are intentionally **not frozen yet**.

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

Checkpoint selection is no longer unresolved: it is frozen under **Evaluation Protocol**.

### Evaluation

* Exact IoU threshold(s) used for threshold-controlled Precision / Recall / F1 matching.
* Exact object-detection matching rules.
* Exact runtime measurement procedure.
* Exact FPS measurement procedure.
* Exact latency measurement procedure.

The following are no longer unresolved and are frozen under **Evaluation Protocol**:

* Final evaluation metrics.
* Confidence-threshold selection procedure.
* Evaluation harness.

Condition-wise evaluation is **removed from the current benchmark**, not unresolved.

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

The following cue was **skipped**, not removed and not frozen:

```text
hands_off_wheel / hands_free
```

It should remain unresolved unless explicitly reconsidered.

## Future Work

* **Low-light/nighttime evaluation** — out of scope for the current benchmark because the current dataset does not contain the required content.

> Future work may extend the ontology with cues deliberately outside the current benchmark scope.

* `reach_behind`
* `hair_makeup`
* `reach_side`
* `head_nodding` — temporal cue requiring multiple frames

## Authors & Credits

> ### Authors

* **Oumar Mamoun Ibrahim** (Senior Undergraduate Researcher)  
  Department of Computer Engineering, University of Sharjah  

  [![ORCID: Oumar](https://img.shields.io/badge/ORCID-0009--0008--0312--1605-A6CE39?logo=orcid&logoColor=white)](https://orcid.org/0009-0008-0312-1605)  
  📧 | [U22200741@sharjah.ac.ae](mailto:U22200741@sharjah.ac.ae)

* **Dr. Mohamad Khairi bin Ishak** (Associate Professor)  
  Department of Computer Engineering, University of Sharjah  

  [![ORCID: Dr. Mohamad](https://img.shields.io/badge/ORCID-0000--0002--3554--0061-A6CE39?logo=orcid&logoColor=white)](https://orcid.org/0000-0002-3554-0061)  
  📧 | [mishak@sharjah.ac.ae](mailto:mishak@sharjah.ac.ae)

> ### Acknowledgments

This benchmark builds upon the excellent work of the teams behind [YOLO11](https://docs.ultralytics.com/models/yolo11/), [D-FINE](https://github.com/Peterande/D-FINE), and [YOLO26](https://docs.ultralytics.com/models/yolo26/).

We sincerely thank their authors, contributors, and maintainers for making these architectures and their implementations available to the research community. Their work makes comparative studies such as **DMS-Eval** possible.

> [!NOTE]
> This research and codebase are prepared for submission to the 5th International Conference on Artificial Intelligence Science and Applications in Industry and Society (CAISAIS 2026), held November 25–27, 2026.

## License

This project is licensed under the **Apache License 2.0** — see the [LICENSE](LICENSE) file for details.