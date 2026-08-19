# Benchmark Scope, Data & Splits

[← Back to the DMS-Eval landing page](../README.md) · [Execution Checklist](./execution-checklist.md)

> [!NOTE]
> This document contains protocol information extracted from the DMS-Eval README. Frozen decisions and unresolved values retain their original status.

> **Jump to:** [Frozen scope](#frozen-benchmark-scope) · [Preprocessing](#frame-extraction--preprocessing) · [Dataset splits](#dataset-splits) · [Annotation format](#annotation-format)

<details>
<summary><strong>Show protocol-status checklist</strong></summary>

- [x] Dataset, model set, input resolution, sampling policy, annotation format, and 8/3/3 subject allocation are frozen.
- [x] The split unit is strictly subject-disjoint.
- [x] All four target cues must occur in every split with roughly similar proportional representation based on per-subject frame counts.
- [x] The dataset-wide 640×640 crop is frozen at `x = 272`, `y = 71`, `width = 640`, `height = 640`.
- [x] The frame-extraction pipeline is implemented under `scripts/`; generated images are not committed to Git.
- [ ] Exact train, validation, and test subject IDs remain unresolved.
- [ ] The exact method used to choose the best 8/3/3 assignment remains unresolved.
- [ ] The exact mapping from “1 frame every 1 second” to source frames at non-integer source FPS remains unresolved.

</details>

---

<a id="frozen-benchmark-scope"></a>

## 🧊 Frozen Benchmark Scope

<p align="center"><sub><b>Table 1.</b> Frozen benchmark scope.</sub></p>

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
> * **Source DMD Session Composition:** The original Driver Monitoring Dataset (DMD) contains three distinct session folders: `distraction`, `drowsiness`, and `gaze`. DMS-Eval incorporates all 81 videos across all three session folders.
> * **Negative Frame Abundance & Overfitting Prevention:** Retaining the `gaze` session videos alongside safe driving intervals within `distraction` and `drowsiness` provides a large natural corpus of true negative background frames (0 bounding boxes). This rich abundance of negative frames is essential to prevent compact object detectors from overtraining on positive targets, ensuring models maintain low false-positive rates during alert driving and normal gaze/mirror checks.
> * **Proportional Frame Yield:** Longer videos naturally contribute more sampled frames than shorter videos due to the uniform 1 FPS temporal sampling across full video durations.

---

## Frame Extraction & Preprocessing

### 🧊 Frozen

> Standardized spatial cropping and temporal sampling procedure:

<p align="center"><sub><b>Table 2.</b> Frozen frame extraction and preprocessing controls.</sub></p>

| Preprocessing Parameter | 🧊 Frozen Value | Implementation Specification |
| :--- | :--- | :--- |
| **Source RGB Video Resolution** | 1280×720 | Source dimensions before the dataset-wide crop |
| **Source RGB Video File Type** | MP4 | RGB-face source videos |
| **Total RGB-Face Videos** | 81 | Dataset-wide source-video count |
| **Camera Framing** | Effectively consistent | Supports one unchanged dataset-wide crop |
| **Source Video Frame Rate** | 29.76 FPS | Native temporal rate across synchronized streams |
| **Video Duration Range** | 55.28–519.39 s | Natural session lengths across 14 volunteer participants |
| **Temporal Sampling** | 1 frame / 1 second | Fixed uniform interval across all videos |
| **Saved Image Format** | JPG | Compressed standard image container |
| **Stored Image Resolution** | 640×640 | Direct benchmark model input dimension |
| **Spatial Cropping Target** | Driver-facing cabin region | Fixed consistently across the dataset |
| **Fixed Crop Geometry** | `x = 272`, `y = 71`, `width = 640`, `height = 640` | The exact same crop is reused for every video and subject |
| **Crop Coordinate Representation** | Source-image pixels | Stored as `(x, y, width, height)` |
| **Resizing** | None | The 640×640 output is produced directly by the frozen crop |
| **Aspect Ratio Handling** | Direct spatial crop | Zero padding / letterboxing borders; zero non-uniform stretching |

> [!IMPORTANT]
> **Spatial Preprocessing Constraints:**
> * **No Letterboxing / Padding:** Zero gray/black padding borders are introduced.
> * **No Aspect-Ratio Stretching:** Image proportions are strictly preserved via direct spatial cropping.
> * **Dataset-wide fixed crop:** The frozen crop is applied unchanged to every source video and subject.

### Frame-Extraction Pipeline — Implemented

The implemented extraction, cropping, and verification pipeline is maintained under [`scripts/`](../scripts/). Extracted images are generated locally and are **not intended to be committed to Git**.

```text
dataset/
└── images/
    ├── subject_01/
    │   ├── video_01/
    │   ├── video_02/
    │   └── ...
    ├── subject_02/
    │   └── ...
    └── ...
```

<p align="center"><sub><b>Table 2b.</b> Extracted 640×640 single-frame crops per subject folder (<code>dataset/images/</code>).</sub></p>

| Subject Folder | Video Count | Extracted Frames (1 FPS) | Relative Yield (%) |
| :--- | :---: | :---: | :---: |
| `subject_01` | 5 | 1,114 | 7.09% |
| `subject_02` | 5 | 1,095 | 6.96% |
| `subject_03` | 5 | 1,173 | 7.46% |
| `subject_04` | 5 | 1,113 | 7.08% |
| `subject_05` | 5 | 1,080 | 6.87% |
| `subject_06` | 5 | 1,195 | 7.60% |
| `subject_07` | 5 | 1,082 | 6.88% |
| `subject_08` | 5 | 1,105 | 7.03% |
| `subject_09` | 5 | 1,200 | 7.63% |
| `subject_10` | 3 | 920 | 5.85% |
| `subject_11` | 5 | 1,155 | 7.35% |
| `subject_12` | 5 | 1,213 | 7.71% |
| `subject_13` | 5 | 1,189 | 7.56% |
| `subject_14` | 5 | 1,089 | 6.93% |
| **Total (14 Subjects)** | **68** | **15,723** | **100.00%** |


#### ⚠️ Resolve Later — Non-Integer-FPS Sampling

The exact implementation rule mapping **“1 frame every 1 second”** to source frames when the source FPS is approximately `29.76` remains unresolved.

No timestamp-sampling rule, rounded-frame-index rule, accumulated-time rule, floor/ceiling rule, or other mapping method is currently frozen.

<details>
<summary><strong>Show frozen preprocessing configuration and crop geometry</strong></summary>

### Preprocessing Configuration

> Fixed cabin crop coordinates are saved to:

```text
preprocessing.json
```

The authoritative stored representation is:

```json
{
  "x": 272,
  "y": 71,
  "width": 640,
  "height": 640
}
```

Equivalent geometric corners are:

```text
Top-left:     (272, 71)
Top-right:    (912, 71)
Bottom-left:  (272, 711)
Bottom-right: (912, 711)
```

> [!NOTE]
> The stored `(x, y, width, height)` representation above is authoritative and avoids ambiguity about inclusive or exclusive zero-based pixel-index conventions.

</details>

---

## Dataset Splits

### 🧊 Frozen

> Subject-disjoint partition across **14 unique subjects**:

<p align="center"><sub><b>Table 3.</b> Subject-disjoint train, validation, and test allocation.</sub></p>

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

> [!IMPORTANT]
> **14 subjects are partitioned into 8 training, 3 validation, and 3 test subjects with strict subject disjointness. All four target cues must be represented in every split, and their cue distributions should be kept roughly proportionally similar across the three splits. Final subject IDs are selected only after annotation provides per-subject cue counts.**

<details>
<summary><strong>Show subject-assignment policy and split manifest</strong></summary>

### Subject Assignment Policy

* The 14 subjects are **not assigned purely at random**.
* Use the **annotated sampled frames** to determine each subject's target-cue distribution.
* Measure cue distribution using **frame counts per cue**, not bounding-box counts.
* If one sampled frame contains multiple target cues, count that frame **once toward each cue present**.
* Keep the four target cues **roughly proportionally similar across training, validation, and test**.
* **All four target cues must appear in all three splits:** training, validation, and test.
* Do **not** additionally balance the total number of sampled frames between splits.
* Select and freeze the exact subject IDs only after annotation is complete and per-subject cue counts are available.

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

* The exact train, validation, and test subject IDs.
* The exact algorithm/method used to choose the best 8/3/3 subject assignment from the annotated cue distributions.

> [!CAUTION]
> No optimization function, exhaustive-search procedure, tolerance, distance metric, weighting rule, random-search method, or numerical balancing threshold is currently frozen.

</details>

---

## Annotation Format

### 🧊 Frozen

> Master annotation structure and data layout:

The benchmark uses **one master annotation format**. The dataset is annotated once, and model-specific formats are generated from that master annotation rather than maintaining separate manually created annotations for different models.

**Master Format:** `COCO JSON`

One COCO JSON file contains the annotations for the **entire dataset**.

```text
dataset/
├── images/
│   ├── subject_01/
│   │   ├── video_01/
│   │   └── ...
│   └── ...
├── annotations.json
├── splits.json
└── preprocessing.json
```

The master COCO annotation file stores:

* Sampled image information
* Four target categories
* Bounding boxes
* Category IDs
* Annotation IDs
* Image IDs

> [!TIP]
> **Single Source of Truth:**
> Authoritative annotations exported from direct manual human annotation in [Label Studio](https://github.com/HumanSignal/label-studio) via [`label-studio-converter`](https://github.com/HumanSignal/label-studio-converter) construct `dataset/annotations.json`. Model-specific format converters (e.g., YOLO TXT or DETR formats) derive their inputs directly from this master file and `splits.json`. See the [annotation protocol](./annotation-protocol.md) and [manual annotation guide (1-page PDF)](./manual-annotation-guide.pdf) for the complete workflow.

<details>
<summary><strong>Show frame-naming convention</strong></summary>

## Frame Naming

### 🧊 Frozen

> Frozen naming schema encoding the canonical subject, canonical video, and sequential sampled-frame number:

Frame filenames must contain:

* Canonical DMS-Eval subject ID
* Canonical video ID for that subject
* Sequential sampled-frame index within that video

```text
subject_<SUBJECT_ID>_video_<VIDEO_ID>_frame_<SAMPLED_FRAME_INDEX>.jpg
```

```text
subject_01_video_01_frame_0001.jpg
subject_01_video_01_frame_0002.jpg
subject_01_video_01_frame_0003.jpg
```

* Sampled-frame numbering begins at `0001`.
* The sampled-frame index is zero-padded to four digits.
* Numbering restarts for each video.
* The frame component is **not** the original MP4 source-frame index.

> [!NOTE]
> The filename provides the subject, video, and sampled-frame sequence number. Additional source-video provenance may rely on the subject/video organization and dataset manifest; the filename itself makes no stronger claim.

</details>

---

<details>
<summary><strong>Future work</strong></summary>

* **Low-light/nighttime evaluation** — out of scope for the current benchmark because the current dataset does not contain the required content.

> Future work may extend the ontology with cues deliberately outside the current benchmark scope:

* `reach_behind`
* `hair_makeup`
* `reach_side`
* `head_nodding` — temporal cue requiring multiple frames

</details>
