# Benchmark Scope, Data & Splits

[← Back to Main Landing Page](../README.md) · [Documentation Hub](./README.md) · [Annotation Protocol](./annotation-protocol.md)

This authoritative protocol document defines the data formulation, spatial preprocessing ($640 \times 640$), uniform 1 FPS temporal sampling, and deterministic 8/3/3 subject-disjoint partitioning for the **DMS-Eval** benchmark.

---

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
> * **Source DMD Session Composition:** The original Driver Monitoring Dataset (DMD) contains three distinct session folders: `distraction`, `drowsiness`, and `gaze` across 81 video recordings. DMS-Eval incorporates all 68 public driver-facing video sessions across the 14 participants.
> * **Negative Frame Abundance & Overfitting Prevention:** Retaining the `gaze` session videos alongside safe driving intervals within `distraction` and `drowsiness` provides a large natural corpus of true negative background frames (0 bounding boxes). This rich abundance of negative frames is essential to prevent compact object detectors from overtraining on positive targets, ensuring models maintain low false-positive rates during alert driving and normal gaze/mirror checks.
> * **Proportional Frame Yield:** Longer videos naturally contribute more sampled frames than shorter videos due to the uniform 1 FPS temporal sampling across full video durations.

---

<a id="frame-extraction--preprocessing"></a>
## Frame Extraction & Preprocessing

### 🧊 Frozen

> Standardized spatial cropping and temporal sampling procedure:

<p align="center"><sub><b>Table 2.</b> Frozen frame extraction and preprocessing controls.</sub></p>

| Preprocessing Parameter | 🧊 Frozen Value | Implementation Specification |
| :--- | :--- | :--- |
| **Source RGB Video Resolution** | 1280×720 | Source dimensions before the dataset-wide crop |
| **Source RGB Video File Type** | MP4 | RGB-face source videos |
| **Total RGB-Face Videos** | 68 (14 Subjects) / 81 (Full Study) | 68 public face video sessions across the 14 subjects (from 81 total study recordings) |
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

> Subject-disjoint partition across **14 unique subjects** (8 Train / 3 Validation / 3 Test):

<p align="center"><sub><b>Table 3.</b> Subject-disjoint train, validation, and test allocation.</sub></p>

| Split | Subjects | Approx. proportion | Frozen Subject IDs |
| :--- | ---: | ---: | :--- |
| **Training** | 8 | 57.1% | `subject_01`, `subject_04`, `subject_06`, `subject_07`, `subject_08`, `subject_09`, `subject_13`, `subject_14` |
| **Validation** | 3 | 21.4% | `subject_02`, `subject_03`, `subject_11` |
| **Test** | 3 | 21.4% | `subject_05`, `subject_10`, `subject_12` |

> [!WARNING]
> **Strict Subject-Disjoint Protocol:**
> * The split unit is the **individual/subject**, not individual frames or videos.
> * A participant appears in **only one** split across all their videos and sampled frames to prevent identity leakage ($S_{\text{train}} \cap S_{\text{val}} = \emptyset$, $S_{\text{train}} \cap S_{\text{test}} = \emptyset$, $S_{\text{val}} \cap S_{\text{test}} = \emptyset$).
> * Subject assignments are **permanently frozen in `dataset/splits.json`** prior to any model fine-tuning and are never modified based on validation or benchmark performance.

---

### Authoritative Split-Selection Rule & Algorithm

The benchmark split is selected via the authoritative optimization rule:
> **Select the 8/3/3 subject split whose negative/positive frame proportion and four class proportions most closely match the complete dataset distribution.**

#### Selection Algorithm (Implemented in [`scripts/balance_splits.py`](../scripts/balance_splits.py)):
1. Read master annotations from `dataset/annotations.json` and derive subject IDs from relative image paths.
2. For each subject, compute total frames, negative frames ($0$ boxes), positive frames ($\ge 1$ box), and class-specific positive frames for `phone_use`, `drinking`, `yawning`, and `hand_over_mouth`.
3. Exhaustively evaluate all $\binom{14}{8} \times \binom{6}{3} = 3003 \times 20 = 60,060$ ordered 8/3/3 subject assignments.
4. Filter out any candidate that is not subject-disjoint, does not contain all 14 subjects, or lacks positive samples for any of the 4 classes in any split.
5. For the global dataset and candidate splits, compute `positive_rate = positive_frames / total_images` and `class_proportion[c] = positive_frames[c] / total_positive_frames`.
6. Compute absolute relative deviation for five equally weighted quantities per split (15 values total):
   $$\text{Dev}(q, s) = \frac{\lvert V(q, s) - V_{\text{global}}(q) \rvert}{V_{\text{global}}(q)}$$
7. Select the optimal candidate using the deterministic lexicographic objective:
   1. **Minimum worst absolute relative deviation** across all 15 quantities (Train, Val, Test).
   2. **Minimum overall RMSE** across all 15 relative deviations.
   3. **Minimum test-split worst relative deviation** across 5 test quantities.
   4. **Minimum test-split RMSE** across 5 test quantities.
   5. **Lexicographically smallest subject-ID assignment**.

---

### Verified Dataset Split Statistics

<p align="center"><sub><b>Table 4.</b> Verified dataset split composition and warning cue distributions across 8/3/3 subject-disjoint partitions.</sub></p>

| Split | Subjects | Total Frames | Negative Frames (0 boxes) | Positive Frames (1 box) | `phone_use` | `drinking` | `yawning` | `hand_over_mouth` | Max Relative Dev. |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Global** | **14** | **15,723** | **12,722 (80.91%)** | **3,001 (19.09%)** | **2,437 (81.21%)** | **264 (8.80%)** | **159 (5.30%)** | **141 (4.70%)** | — |
| **Train ($S_{\text{train}}$)** | 8 | 9,087 | 7,339 (80.76%) | 1,748 (19.24%) | 1,417 (81.06%) | 154 (8.81%) | 94 (5.38%) | 83 (4.75%) | $\le 1.48\%$ |
| **Val ($S_{\text{val}}$)** | 3 | 3,423 | 2,784 (81.33%) | 639 (18.67%) | 523 (81.85%) | 54 (8.45%) | 32 (5.01%) | 30 (4.69%) | $\le 5.48\%$ |
| **Test ($S_{\text{test}}$)** | 3 | 3,213 | 2,599 (80.89%) | 614 (19.11%) | 497 (80.94%) | 56 (9.12%) | 33 (5.37%) | 28 (4.56%) | $\le 3.68\%$ |

* Maximum absolute relative deviation across all 15 split quantities: **5.4812%** ($\le 5.48\%$).
* Detailed selection audit log saved at [`dataset/split_selection_report.json`](../dataset/split_selection_report.json).

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
├── annotations_per_subject/                  # 14 baseline per-subject folders (COCO + Raw JSON)
├── annotations_per_subject_shuffled/         # Split hierarchy (Training/ [Seed 13], Validation/, Test/)
├── annotations.json                          # Authoritative master COCO annotations
├── splits.json                               # Frozen 8/3/3 subject-disjoint partitions
└── preprocessing.json                        # Preprocessing & spatial crop parameters
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

<p align="center">
  <img src="../assets/charts/benchmark_distributions_combined.png" alt="DMS-Eval Dataset Frame Composition and Warning Cue Distribution" width="850"><br>
  <sub><b>Figure 2.</b> Benchmark ground-truth distributions: (a) Frame composition across all 15,723 frames (80.9% negative background frames vs. 19.1% positive cue frames); (b) Proportion of bounding box annotations across the 4 frozen target warning cues (3,001 total annotations: 81.2% <code>phone_use</code>, 8.8% <code>drinking</code>, 5.3% <code>yawning</code>, 4.7% <code>hand_over_mouth</code>).</sub>
</p>

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
