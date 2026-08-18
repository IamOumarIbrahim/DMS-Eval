<h1 align="center">DMS-Eval</h1>

<p align="center">
  <strong>A planned benchmark for nano-scale object detectors in frame-level driver monitoring</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Status-In_Development-orange?style=flat" alt="Status: In Development">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg" alt="License: Apache 2.0"></a>
  <img src="https://img.shields.io/badge/Input-640%C3%97640-555?style=flat" alt="Input: 640×640">
  <img src="https://img.shields.io/badge/Detectors-YOLO%20%7C%20DETR-4c1?style=flat" alt="Detectors: YOLO | DETR">
</p>

<p align="center">
  <img src="./assets/socialpreview.png" alt="DMS-Eval social preview" width="820">
</p>

**DMS-Eval** is a planned benchmark framework currently in development for evaluating nano-scale (lightweight) object detection architectures for detecting visual cues associated with driver drowsiness and distraction in real time across diverse cabin operating conditions.

> **Benchmark Mission:** DMS-Eval establishes a standardized evaluation framework comparing real-time nano-scale object detectors (YOLO vs. DETR families) for in-cabin driver state monitoring under single-frame operational constraints.

> [!IMPORTANT]
> **Controlled-comparison principle**
>
> All models receive the same training/test data, subject-disjoint test split, image resolution, evaluation annotations, metric implementation, hardware, numerical precision, batch size, inference timing protocol, and test-set access policy. Shared training-budget controls—such as maximum epochs, early stopping policy, batch size, gradient accumulation, number of runs, and checkpoint-selection procedure—are kept consistent across models. Architecture-specific optimization settings—such as optimizer, learning rate, scheduler, weight decay, augmentation, and other model-specific recipe choices—follow each architecture’s official training recipe and are documented rather than artificially forced to be identical.

---

## Benchmark at a glance

<p align="center"><sub><b>Table 1.</b> Frozen benchmark scope summary.</sub></p>

| Setting | Frozen value | Setting | Frozen value |
| :--- | :--- | :--- | :--- |
| **Dataset** | DMD-derived real-cabin RGB video | **Models** | YOLO11n, D-FINE-N, YOLO26n |
| **Input** | 640×640 individual frames | **Sampling** | 1 frame every 1 second |
| **Split** | 8 / 3 / 3 subjects | **Split unit** | Strictly subject-disjoint |
| **Annotations** | Direct manual human annotation (Label Studio) → master COCO JSON | **Hardware** | NVIDIA RTX 4060, 8 GB VRAM |
| **Training batch** | 1, no gradient accumulation | **Runtime batch** | 1 |
| **Primary metric** | mAP@0.5:0.95 | **Input unit** | Single static frame |


> [!NOTE]
> **Source DMD Composition & Negative Sample Richness:**
> The original DMD dataset is organized into three behavioral session folders: `distraction`, `drowsiness`, and `gaze`. DMS-Eval incorporates all 81 videos across all three folders. Retaining the `gaze` sessions alongside non-cue driving periods in `distraction` and `drowsiness` supplies a substantial volume of naturalistic negative frames (0 bounding boxes), preventing lightweight object detectors from overtraining on positive cues and training them to suppress false alarms during alert driving. Longer videos naturally contribute proportionally more sampled frames under the uniform 1 FPS policy.

> [!IMPORTANT]
> **14 subjects are partitioned into 8 training, 3 validation, and 3 test subjects with strict subject disjointness. All four target cues must be represented in every split, and their cue distributions should be kept roughly proportionally similar across the three splits. Final subject IDs are selected only after annotation provides per-subject cue counts.**

---

## Dataset Preprocessing & Frame Extraction

The implemented frame-extraction and 640×640 cropping pipeline is maintained under [`scripts/`](./scripts/). Extracted images are generated locally under `dataset/images/` and are not intended to be committed to Git.

```text
dataset/images/
├── subject_01/
│   ├── video_01/
│   └── ...
├── subject_02/
│   └── ...
└── ...
```

> [!NOTE]
> The frozen preprocessing rules and the unresolved non-integer-FPS sampling detail are maintained in [Benchmark scope, data & splits](./docs/quick-start.md).

> [!IMPORTANT]
> Annotation uses **Label Studio** (Community Edition) with one project (**DMS-Eval**) and one task per image. Subject, video, filename, and sampled-frame index are retained as task metadata. All 15,723 sampled frames are directly and manually annotated by the human expert annotator under the frozen 4-cue ontology to produce the authoritative master COCO ground truth in `dataset/annotations.json`. See the [annotation protocol](./docs/annotation-protocol.md) and [manual annotation guide (1-page PDF)](./docs/manual-annotation-guide.pdf).

---

## Documentation

<p align="center"><sub><b>Table 2.</b> Detailed protocol documentation and execution resources.</sub></p>

| Document | What it contains | Status covered |
| :--- | :--- | :--- |
| [**Benchmark scope, data & splits**](./docs/quick-start.md) | Frozen scope, preprocessing, subject splits, annotation format, frame naming, and future work | Frozen + resolve later |
| [**Annotation protocol & cue ontology**](./docs/annotation-protocol.md) | Four warning cues, bounding-box rules, removed classes, and data-quality controls | Frozen |
| [**Manual annotation field guide (PDF)**](./docs/manual-annotation-guide.pdf) | Single-page desktop PDF reference: hotkey cheat sheet, bounding-box extents, and decision matrix | Practical field guide |
| [**Training protocol**](./docs/training-protocol.md) | Initialization, model-specific recipes, and shared training controls | Frozen |
| [**Evaluation protocol**](./docs/evaluation-protocol.md) | Metrics, evaluator, test isolation, thresholding, checkpoint selection, runtime, and unresolved choices | Frozen + resolve later |
| [**Execution checklist & roadmap**](./docs/execution-checklist.md) | Step-by-step 7-module implementation roadmap, dependencies, quality controls, and deliverables | Actionable checklist |

> [!TIP]
> Start with [**Benchmark scope, data & splits**](./docs/quick-start.md), then use the annotation, training, and evaluation documents as the source for implementation details. Refer to the [**Execution checklist & roadmap**](./docs/execution-checklist.md) for current implementation progress.

---

## Frozen target cues

<p align="center"><sub><b>Table 3.</b> Single-frame warning-cue ontology.</sub></p>

| Drowsiness Cue | Distraction / Inattention Cue |
| :--- | :--- |
| `yawning` | `drinking` |
| `hand_over_mouth` | `phone_use` *(calling)* |

<p align="center">
  <img src="./assets/yawning_annotation_example.png" alt="An example of our annotation of yawning in Label Studio" width="160">
  <img src="./assets/hand_over_mouth_annotation_example.png" alt="An example of our annotation of hand_over_mouth in Label Studio" width="160">
  <img src="./assets/drinking_annotation_example.png" alt="An example of our annotation of drinking in Label Studio" width="160">
  <img src="./assets/phone_use_annotation_example.png" alt="An example of our annotation of phone_use in Label Studio" width="160"><br>
  <sub><b>Figure 2.</b> Examples of our manual annotations in Label Studio across the 4 frozen target warning cues: <code>yawning</code> (orange box around mouth), <code>hand_over_mouth</code> (purple box), <code>drinking</code> (blue box enclosing face + beverage container), and <code>phone_use</code> (pink box enclosing phone and hand held at ear in calling posture).</sub>
</p>

> [!NOTE]
> **Ontological Design Decisions:**
> - **Single-Annotation Policy (At Most One Annotation Per Image):** Each sampled frame contains at most one bounding box annotation (0 or 1 annotation per frame). `yawning` and `hand_over_mouth` must **never be labeled twice in one image**; if a driver yawns while a hand covers the mouth, the instance is uniquely labeled as `hand_over_mouth`.
> - **`head_turned_away` & `gaze_away` Removal:** Drivers routinely perform mirror checks (side/rearview mirrors) and visual scanning during safe driving. In isolated 1 FPS static frames without temporal sequence context or 3D gaze tracking, there is no objective or consistent boundary to distinguish brief, safe mirror glances (false positives) from dangerous, prolonged inattention (true positives). To eliminate subjective label noise from split datasets, head rotation is excluded in favor of the 4 self-contained visual warning cues.
> - **`eyes_closed` Removal:** Single-frame 2D object detectors suffer from substantial false positives on momentary physiological blinks and downward road glances; reliable eye-state tracking requires continuous temporal sequence modeling.

> [!TIP]
> Cue definitions, bounding-box extents, exclusions, priority rules, and annotation-quality controls are maintained in the [annotation protocol](./docs/annotation-protocol.md).

---

## Current protocol status

> [!NOTE]
> Frozen decisions are marked **🧊 Frozen** in the detailed documents. Exact values that remain open are marked **⚠️ Resolve Later** and must not be silently assumed during implementation.

<details>
<summary><strong>Show the resolve-later checklist</strong></summary>

- [ ] Exact train, validation, and test subject IDs in `splits.json`
- [ ] Exact algorithm/method used to choose the best 8/3/3 subject assignment from annotated per-subject cue distributions
- [ ] Exact numerical validation-selected confidence threshold for each model
- [ ] CUDA, PyTorch, model-framework versions/commits, NVIDIA GPU-driver, and THOP versions from the actual environment
- [ ] Handling of unsupported/custom operators if THOP does not count them correctly
- [ ] Exact implementation mapping “1 frame every 1 second” to source frames at non-integer source FPS

See [Benchmark scope, data & splits](./docs/quick-start.md) and the [evaluation protocol](./docs/evaluation-protocol.md) for the existing descriptions of these unresolved values.

</details>

---

## Authors & credits

- **Oumar Mamoun Ibrahim** — Senior Undergraduate Researcher, Department of Computer Engineering, University of Sharjah<br>
  [![ORCID: Oumar](https://img.shields.io/badge/ORCID-0009--0008--0312--1605-A6CE39?logo=orcid&logoColor=white)](https://orcid.org/0009-0008-0312-1605)<br>
  [U22200741@sharjah.ac.ae](mailto:U22200741@sharjah.ac.ae)

- **Dr. Mohamad Khairi bin Ishak** — Associate Professor, Department of Computer Engineering, University of Sharjah<br>
  [![ORCID: Dr. Mohamad](https://img.shields.io/badge/ORCID-0000--0002--3554--0061-A6CE39?logo=orcid&logoColor=white)](https://orcid.org/0000-0002-3554-0061)<br>
  [mishak@sharjah.ac.ae](mailto:mishak@sharjah.ac.ae)

<details>
<summary><strong>Acknowledgments and submission note</strong></summary>

This benchmark builds upon the excellent work of the teams behind [YOLO11](https://docs.ultralytics.com/models/yolo11/), [D-FINE](https://github.com/Peterande/D-FINE), and [YOLO26](https://docs.ultralytics.com/models/yolo26/).

We sincerely thank their authors, contributors, and maintainers for making these architectures and their implementations available to the research community. Their work makes comparative studies such as **DMS-Eval** possible.

> [!NOTE]
> This research and codebase are prepared for submission to the 5th International Conference on Artificial Intelligence Science and Applications in Industry and Society (CAISAIS 2026), held November 25–27, 2026.

</details>

---

## License

This project is licensed under the **Apache License 2.0** — see the [LICENSE](LICENSE) file for details.
