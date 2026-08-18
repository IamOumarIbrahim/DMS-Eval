# Annotation Protocol & Cue Ontology

[← Back to the DMS-Eval landing page](../README.md) · [Execution Checklist](./execution-checklist.md)

> [!NOTE]
> This document contains protocol information extracted from the DMS-Eval README. Frozen decisions and unresolved values retain their original status.

> **Jump to:** [Target cues](#target-warning-cues) · [Annotation workflow](#annotation-workflow) · [Cue hierarchy](#cue-categories--visual-salience) · [Detailed rules](#annotation-rules) · [Data quality](#annotation--data-quality)

- [x] Four target warning cues are frozen.
- [x] Bounding-box extents and single-frame rules are frozen.
- [x] Removed and merged classes are documented.
- [x] Annotation-quality controls are frozen.
- [x] Label Studio (Community Edition) is frozen as the annotation tool, using one project (DMS-Eval) and one task per image with metadata filtering.
- [x] Direct manual human expert annotation is established across all 15,723 frames to construct the master ground truth.

---

## Target Warning Cues

> The DMS-Eval benchmark targets **4 🧊 frozen visual warning cues** with specified bounding-box extents:

<p align="center"><sub><b>Table 1.</b> Frozen target warning cues and bounding-box extents.</sub></p>

| 🧊 Frozen cue | Meaning | Bounding box |
| :--- | :--- | :--- |
| `yawning` | Driver is visibly yawning; an ordinary open mouth is not sufficient | Mouth region only |
| `hand_over_mouth` | Hand visibly covers or occludes the mouth | Full head/face |
| `drinking` | Driver is actively drinking from a bottle, cup, or can with vessel brought to face/mouth | Face + bottle together |
| `phone_use` | Driver is engaged in an active handheld phone call (holding phone to ear/head); texting/browsing and hands-free calls are excluded | Hand + phone at ear/head |

<details>
<summary><strong>Show detailed per-cue annotation rules</strong></summary>

## Annotation Rules

### General

> [!IMPORTANT]
> **Static Frame Context & Single-Annotation Policy (At Most One Annotation Per Image):**
> * All target warning cues are judged using the **individual sampled frame only**. Surrounding video frames are not referenced.
> * **Strict Single-Annotation Constraint:** Each image should have **at most one annotation** (0 or 1 bounding box per image). An image must **never contain multiple annotations**, and `yawning` and `hand_over_mouth` must **never be labeled twice in one image**.
> * **Drowsiness Salience & Priority Rule:** If the driver is yawning while a hand visibly covers or occludes the mouth, annotate strictly as **`hand_over_mouth`** (full head/face). Do not draw a second box for `yawning`. `yawning` is annotated only when the mouth aperture is unobstructed by a covering hand.

### `yawning`

> Annotate only when the sampled frame visibly depicts an active yawn.

* An ordinary open mouth is not automatically considered `yawning`.
* **Bounding Box Extent:** Mouth region only.
* `mouth_open` is **not** an independent class.

<p align="center">
  <img src="../assets/yawning_annotation_example.png" alt="An example of our annotation of yawning in Label Studio" width="420"><br>
  <sub><b>Figure 1.</b> An example of our annotation of <code>yawning</code> in Label Studio (enclosing mouth region only).</sub>
</p>

### `hand_over_mouth`

> Annotate when the driver's hand visibly covers or occludes the mouth.

* **Bounding Box Extent:** Full head/face.

<p align="center">
  <img src="../assets/hand_over_mouth_annotation_example.png" alt="An example of our annotation of hand_over_mouth in Label Studio" width="420"><br>
  <sub><b>Figure 2.</b> An example of our annotation of <code>hand_over_mouth</code> in Label Studio (enclosing full visible head/face and occluding hand).</sub>
</p>

### `drinking`

> Annotate when the driver is actively drinking from a bottle, cup, can, or container brought up to the face/mouth.

* **Bounding Box Extent:** Face + bottle together (enclosing the driver's face and the beverage container).
* **Exclusions:** Bottles or cups resting passively in cup holders or consoles without active consumption posture.
* Focus is strictly on **active drinking interaction** (face + bottle).

<p align="center">
  <img src="../assets/drinking_annotation_example.png" alt="An example of our annotation of drinking in Label Studio" width="420"><br>
  <sub><b>Figure 3.</b> An example of our annotation of <code>drinking</code> in Label Studio (enclosing driver face and beverage container together in active consumption posture).</sub>
</p>

### `phone_use`

> Annotate when the driver is actively engaged in a handheld phone call (holding the phone to the ear/head).

* **Bounding Box Extent:** Hand + phone held to ear/head (enclosing the interacting hand, phone, and adjacent ear/face region).
* **Scope Definition (Calling Sense Only):** Focus is strictly on **handheld phone calling / holding phone to the ear**.
* **Strict Exclusions:**
  - Texting, lap browsing, or typing on a phone are **excluded**.
  - Hands-free phone calls (Bluetooth/speakerphone) where no device is held to the ear are **excluded**.
  - Phones resting passively on seats, mounts, or consoles are **excluded**.

<p align="center">
  <img src="../assets/phone_use_annotation_example.png" alt="An example of our annotation of phone_use in Label Studio" width="420"><br>
  <sub><b>Figure 4.</b> An example of our annotation of <code>phone_use</code> in Label Studio (enclosing handheld phone and interacting hand held at the ear in calling posture).</sub>
</p>

</details>

---

## Annotation Workflow

### 🧊 Frozen Label Studio Organization

* **Annotation tool:** Label Studio (Community Edition, local pip installation)
* **Project structure:** One Label Studio project (`DMS-Eval`)
* **Task structure:** One Label Studio task per image (15,723 tasks total)
* **Task metadata:** Subject, video, filename, and sampled-frame index are retained as task metadata to allow filtering and processing by subject.
* Every task uses the same four frozen target-cue rectangle labels.

### Direct Manual Human Annotation

The human expert annotator directly annotates all 15,723 frames to construct the authoritative ground truth for the benchmark.

1. **100% Direct Human Annotation:** The human expert inspects every single sampled frame (including zero-cue frames) and manually draws bounding boxes for all visible cues.
2. **Definitive Ground Truth:** All annotations created and submitted in Label Studio are saved directly into the local database as authoritative human annotations.
3. **No Intermediate Workflow Fields in JSON:** There is no need for intermediate review flags or "human check needed" variables in the dataset schema. Submitted annotations represent finalized ground truth.
4. **Zero-Cue Frames & DMD Source Composition:** Source frames are extracted from all three original DMD behavioral folders (`distraction`, `drowsiness`, and `gaze`). Normal alert driving periods, mirror checks, and entire `gaze` session frames containing none of the 4 cues are submitted with zero bounding boxes. This supplies a large, realistic negative sample distribution essential to prevent models from overtraining on positive cues.
5. **Authoritative Export:** Completed annotations are exported from Label Studio directly into the master COCO file at [`dataset/annotations.json`](file:///c:/Dev/repos/Public%20repos/DMS-Eval/dataset/annotations.json).

### Detection Ontology Integrity

Workflow state is not embedded into the detection ontology. The ontology contains **strictly the 4 target visual cues**:
- `yawning`
- `hand_over_mouth`
- `drinking`
- `phone_use`

No synthetic workflow labels (such as `reviewed`, `needs_review`, `ai_generated`, `ambiguous`, or `finalized`) exist in the COCO ground truth classes.

#### External progress ledger

Maintain a machine-readable annotation progress ledger keyed by the real image filename. It must support safe resume without duplicating annotations or overwriting human-reviewed work, and distinguish at minimum:

```text
not_processed
agent_processed
zero_proposals
secondary_review_required
human_reviewed
finalized
failed
```

This state must not be stored in the COCO class ontology.

---

## Cue Categories & Visual Salience

> **Ontological Hierarchy:** Ranked from the most direct/unambiguous single-frame visual indicator to weaker/more ambiguous postural cues. *(Visual salience does not dictate expected model detection accuracy).*

<p align="center"><sub><b>Table 2.</b> Cue categories and visual-salience hierarchy.</sub></p>

| Behavioral Domain | Target Warning Cue | Salience Rank | Single-Frame Visual Trigger | Bounding Box Extent |
| :--- | :--- | :---: | :--- | :--- |
| **Drowsiness** | `yawning` | 1 *(Highest)* | Visible yawning with wide oral opening and facial elongation | Mouth region only |
| | `hand_over_mouth` | 2 *(Lowest)* | Hand visibly covering or occluding the mouth region | Full head/face |
| **Distraction / Inattention** | `drinking` | 1 *(Highest)* | Active drinking from a bottle/cup/can brought to the face | Face + bottle together |
| | `phone_use` | 2 *(Lowest)* | Handheld phone call with phone held to the ear/head | Hand + phone at ear |

<details>
<summary><strong>Show removed, merged, narrowed, and background classes</strong></summary>

## Removed Classes & Ontological Scope Decisions

> Deliberately excluded classes and merged concepts to eliminate label ambiguity and subjective annotation noise:

<p align="center"><sub><b>Table 3.</b> Removed, merged, narrowed, and background classes.</sub></p>

| Excluded / Merged Candidate | Category Disposition | Rationale / Benchmark Decision |
| :--- | :--- | :--- |
| `head_turned_away`, `gaze_away` | Removed | **Mirror Checking vs. True Inattention Ambiguity:** Drivers routinely check side and rearview mirrors and perform active visual scanning as safe driving behavior. In single static 1-FPS split frames without continuous temporal video context or 3D gaze tracking, there is no objective or consistent boundary to distinguish brief, safe mirror glances (false positives) from dangerous, prolonged inattention (true positives). Excluded to eliminate subjective label noise in favor of 4 self-contained visual warning cues. |
| `eyes_open`, `drive_safe` | Background / Negative | Normal driving baselines; evaluated as true negatives rather than positive targets |
| `eyes_closed` | Removed | Frame-based 2D object detectors evaluated on single static frames suffer from high false-positive rates due to normal physiological blinks and downward road/mirror glances; reliable eyelid closure tracking requires temporal sequence modeling |
| `head_down` | Removed | Redundant in static single-frame detection and inherently represents a multi-frame temporal event ("falling asleep" / microsleep nodding); excluded from single-frame static warning cue ontology |
| `talk_passenger` | Removed | Substantial visual ambiguity without continuous audio-visual tracking |
| `mouth_open` | Merged | Subsumed directly under `yawning` |
| `eyes_partially_closed` | Removed | Subsumed with `eyes_closed` removal |
| `hand_on_face` | Narrowed | Refined specifically to `hand_over_mouth` |
| `face_occluded` | Quality Flag | Handled as a data-quality / visibility condition rather than an object class |
| `phone_texting` | Removed | Texting / typing on lap is excluded to focus strictly on calling posture (`phone_use`) and beverage interaction (`drinking`) |
| `smoking`, `eating` | Removed | Secondary non-core object interactions outside the benchmark scope |
| `adjust_radio`, `switch_gear` | Removed | Momentary vehicle operation controls |
| `eye_rubbing` | Removed | Highly ambiguous in single static frames without temporal tracking |
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

#### Single-annotation constraint
 
* **At Most One Annotation Per Image:** Each sampled image must contain at most one bounding box annotation (0 or 1 annotation per frame).
* **Mutual Exclusivity:** `yawning` and `hand_over_mouth` must never be labeled twice in one image. When a covering hand occludes a yawn, prioritize `hand_over_mouth`. No image may contain multiple warning cue bounding boxes.

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
