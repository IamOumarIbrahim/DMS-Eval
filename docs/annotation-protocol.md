# Annotation Protocol & Cue Ontology

[← Back to the DMS-Eval landing page](../README.md) · [Execution Checklist](./execution-checklist.md)

> [!NOTE]
> This document contains protocol information extracted from the DMS-Eval README. Frozen decisions and unresolved values retain their original status.

> **Jump to:** [Target cues](#target-warning-cues) · [Annotation workflow](#annotation-workflow) · [Cue hierarchy](#cue-categories--visual-salience) · [Detailed rules](#annotation-rules) · [Data quality](#annotation--data-quality)

- [x] Six target warning cues are frozen.
- [x] Bounding-box extents and single-frame rules are frozen.
- [x] Removed and merged classes are documented.
- [x] Annotation-quality controls are frozen.
- [x] CVAT is frozen as the annotation tool, using one project and one task per subject.
- [x] AI-assisted pre-annotation is frozen as provisional assistance with mandatory human review of every frame.

---

## Target Warning Cues

> The DMS-Eval benchmark targets **6 🧊 frozen visual warning cues** with specified bounding-box extents:

<p align="center"><sub><b>Table 1.</b> Frozen target warning cues and bounding-box extents.</sub></p>

| 🧊 Frozen cue | Meaning | Bounding box |
| :--- | :--- | :--- |
| `eyes_closed` | Driver's eyes are visibly closed, including fully closed and visibly partially closed / heavy-lidded eyes | Separate box per eye |
| `yawning` | Driver is visibly yawning; an ordinary open mouth is not sufficient | Mouth region only |
| `head_down` | Head is clearly and substantially lowered/forward relative to normal forward-facing driving posture | Full head/face |
| `hand_over_mouth` | Hand visibly covers or occludes the mouth | Full head/face |
| `phone_use` | Driver is texting or actively interacting with a handheld phone; resting phones and phone calls are excluded | Hand + phone together |
| `head_turned_away` | Head is substantially turned left/right or away from the forward driving direction | Full head/face |

<details>
<summary><strong>Show detailed per-cue annotation rules</strong></summary>

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

</details>

---

## Annotation Workflow

### 🧊 Frozen CVAT Organization

* **Annotation tool:** CVAT
* **Project structure:** One CVAT project
* **Task structure:** 14 CVAT tasks, with one task per subject
* Each subject task contains all sampled frames from all videos belonging to that subject.
* Every task uses the same six frozen target-cue labels.

### 🧊 Frozen AI-Assisted Pre-Annotation

The AI/vision agent provides **pre-annotation assistance only**. It reduces manual drawing work but does not replace human ground-truth validation.

1. The agent may attempt to pre-annotate all six target cues.
2. The agent writes proposed annotations directly into CVAT; an intermediate COCO file is not the normal pre-annotation workflow.
3. All agent annotations are provisional proposals, never final ground truth.
4. A human must review every proposed annotation.
5. A human must review every sampled frame, including frames where the agent proposes zero annotations.
6. During review, the human may accept a proposal, move or resize a box, change its class, delete a false positive, or manually add missed annotations.
7. Only human-reviewed annotations may enter the final master COCO ground truth.

> [!IMPORTANT]
> **Human authority:** The human annotator/reviewer has final authority. The AI agent must never overwrite annotations that the human has already reviewed or finalized, and rerunning the agent must preserve all reviewed/finalized human annotations.

> [!NOTE]
> The AI-assisted workflow follows the existing ambiguity rules below. It does not create a separate AI-specific rule for ambiguous cue presence or borderline class choice.

### 🧊 Frozen CVAT Review-State Representation

Workflow state remains separate from the six-class detection ontology.

#### AI proposed

AI-generated annotation objects use CVAT's native:

```text
Source = AUTO
```

AI-created annotations are provisional only.

#### Needs secondary review

When cue presence itself is ambiguous, do not create a speculative ground-truth box. Create an open CVAT Issue associated with the relevant frame/object area stating that secondary review is required. The issue remains unresolved until a human settles it.

#### Human reviewed

Human checking uses the CVAT job workflow:

```text
Annotation
    ↓
Validation
    ↓
Acceptance
```

A job is finalized only after the required human review is complete and unresolved issues have been settled. The AI agent must never mark its own annotation work as human-reviewed, accepted, or final.

#### No fake workflow classes

Do not add `reviewed`, `needs_review`, `ai_generated`, `ambiguous`, or any other workflow-state label to the six-class detection ontology.

#### External progress ledger

Maintain a machine-readable annotation progress ledger keyed by the real image filename. It must support safe resume without duplicating annotations or overwriting human-reviewed work, and distinguish at minimum:

```text
not_processed
ai_processed
secondary_review_required
human_reviewed
finalized
```

This state must not be stored in the COCO class ontology.

---

## Cue Categories & Visual Salience

> **Ontological Hierarchy:** Ranked from the most direct/unambiguous single-frame visual indicator to weaker/more ambiguous postural cues. *(Visual salience does not dictate expected model detection accuracy).*

<p align="center"><sub><b>Table 2.</b> Cue categories and visual-salience hierarchy.</sub></p>

| Behavioral Domain | Target Warning Cue | Salience Rank | Single-Frame Visual Trigger | Bounding Box Extent |
| :--- | :--- | :---: | :--- | :--- |
| **Drowsiness** | `eyes_closed` | 1 *(Highest)* | Visibly fully closed, partially closed, or heavy-lidded eyes | Separate box per eye |
| | `yawning` | 2 | Visible yawning with wide oral opening and facial elongation | Mouth region only |
| | `head_down` | 3 | Pronounced forward/downward head slouch | Full head/face |
| | `hand_over_mouth` | 4 *(Lowest)* | Hand visibly covering or occluding the mouth region | Full head/face |
| **Distraction** | `phone_use` | 1 *(Highest)* | Active handheld interaction or texting on smartphone | Hand + phone together |
| | `head_turned_away` | 2 *(Lowest)* | Head substantially rotated left, right, or away from the roadway | Full head/face |

<details>
<summary><strong>Show removed, merged, narrowed, and background classes</strong></summary>

## Removed Classes

> Deliberately excluded classes and merged concepts to eliminate label ambiguity:

<p align="center"><sub><b>Table 3.</b> Removed, merged, narrowed, and background classes.</sub></p>

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

</details>

---

<details>
<summary><strong>Show annotation and data-quality controls</strong></summary>

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

</details>
