<div align="center">

# DMS-Eval

**A planned benchmark for nano-scale object detectors in frame-level driver monitoring**

![Status: In Development](https://img.shields.io/badge/Status-In_Development-orange?style=flat)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
![Input: 640×640](https://img.shields.io/badge/Input-640%C3%97640-555?style=flat)
![Detectors: YOLO | DETR](https://img.shields.io/badge/Detectors-YOLO%20%7C%20DETR-4c1?style=flat)

<img src="./assets/socialpreview.png" alt="DMS-Eval social preview" width="820">

</div>

**DMS-Eval** is a planned benchmark framework currently in development for evaluating nano-scale (lightweight) object detection architectures for detecting visual cues associated with driver drowsiness and distraction in real time across diverse cabin operating conditions.

> **Benchmark Mission:** DMS-Eval establishes a standardized evaluation framework comparing real-time nano-scale object detectors (YOLO vs. DETR families) for in-cabin driver state monitoring under single-frame operational constraints.

> [!IMPORTANT]
> **Controlled-comparison principle**
>
> All models receive the same training/test data, subject-disjoint test split, image resolution, evaluation annotations, metric implementation, hardware, numerical precision, batch size, inference timing protocol, and test-set access policy. Shared training-budget controls—such as maximum epochs, early stopping policy, batch size, gradient accumulation, number of runs, and checkpoint-selection procedure—are kept consistent across models. Architecture-specific optimization settings—such as optimizer, learning rate, scheduler, weight decay, augmentation, and other model-specific recipe choices—follow each architecture’s official training recipe and are documented rather than artificially forced to be identical.

---

## Benchmark at a glance

<div align="center">
<table>
<caption><strong>Table 1. Frozen benchmark scope summary</strong></caption>
<thead>
<tr>
<th>Setting</th>
<th>Frozen value</th>
<th>Setting</th>
<th>Frozen value</th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Dataset</strong></td>
<td>DMD-derived real-cabin RGB video</td>
<td><strong>Models</strong></td>
<td>YOLO11n, D-FINE-N, YOLO26n</td>
</tr>
<tr>
<td><strong>Input</strong></td>
<td>640×640 individual frames</td>
<td><strong>Sampling</strong></td>
<td>1 frame every 1 second</td>
</tr>
<tr>
<td><strong>Split</strong></td>
<td>8 / 3 / 3 subjects</td>
<td><strong>Split unit</strong></td>
<td>Strictly subject-disjoint</td>
</tr>
<tr>
<td><strong>Annotations</strong></td>
<td>One master COCO JSON</td>
<td><strong>Hardware</strong></td>
<td>NVIDIA RTX 4060, 8 GB VRAM</td>
</tr>
<tr>
<td><strong>Training batch</strong></td>
<td>1, no gradient accumulation</td>
<td><strong>Runtime batch</strong></td>
<td>1</td>
</tr>
<tr>
<td><strong>Primary metric</strong></td>
<td>mAP@0.5:0.95</td>
<td><strong>Input unit</strong></td>
<td>Single static frame</td>
</tr>
</tbody>
</table>
</div>

<p align="center">
<img src="./assets/640X640.png" alt="Standardized 640 by 640 benchmark input" width="640"><br>
<sub><strong>Figure 1.</strong> Standardized 640×640 benchmark input.</sub>
</p>

> [!NOTE]
> Longer videos naturally contribute more sampled frames under the uniform 1 FPS policy. Frames containing none of the target warning cues remain valid negative samples.

> [!IMPORTANT]
> **14 subjects are partitioned into 8 training, 3 validation, and 3 test subjects with strict subject disjointness. All six target cues must be represented in every split, and their cue distributions should be kept roughly proportionally similar across the three splits. Final subject IDs are selected only after annotation provides per-subject cue counts.**

---

## Dataset Preprocessing & Frame Extraction

The dataset extraction and 640×640 face cropping pipeline is automated via [`scripts/extract_and_crop_dmd.py`](./scripts/extract_and_crop_dmd.py):

```bash
# Run full pipeline (extraction + cropping + verification)
python scripts/extract_and_crop_dmd.py

# Custom parameters example
python scripts/extract_and_crop_dmd.py --dmd-dir dataset/DMD --out-cropped dataset/images --sample-fps 1.0 --crop-box 272 71 640 640 --workers 6
```

---

## Documentation

<div align="center">
<table>
<caption><strong>Table 2. Detailed protocol documentation</strong></caption>
<thead>
<tr>
<th>Document</th>
<th>What it contains</th>
<th>Status covered</th>
</tr>
</thead>
<tbody>
<tr>
<td><a href="./docs/quick-start.md"><strong>Benchmark scope, data &amp; splits</strong></a></td>
<td>Frozen scope, preprocessing, subject splits, annotation format, frame naming, and future work</td>
<td>Frozen + resolve later</td>
</tr>
<tr>
<td><a href="./docs/annotation-protocol.md"><strong>Annotation protocol &amp; cue ontology</strong></a></td>
<td>Six warning cues, bounding-box rules, removed classes, and data-quality controls</td>
<td>Frozen</td>
</tr>
<tr>
<td><a href="./docs/training-protocol.md"><strong>Training protocol</strong></a></td>
<td>Initialization, model-specific recipes, and shared training controls</td>
<td>Frozen</td>
</tr>
<tr>
<td><a href="./docs/evaluation-protocol.md"><strong>Evaluation protocol</strong></a></td>
<td>Metrics, evaluator, test isolation, thresholding, checkpoint selection, runtime, and unresolved choices</td>
<td>Frozen + resolve later</td>
</tr>
</tbody>
</table>
</div>

> [!TIP]
> Start with [**Benchmark scope, data & splits**](./docs/quick-start.md), then use the annotation, training, and evaluation documents as the source for implementation details.

---

## Frozen target cues

<div align="center">
<table>
<caption><strong>Table 3. Single-frame warning-cue ontology</strong></caption>
<thead>
<tr>
<th>Drowsiness</th>
<th>Distraction</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>eyes_closed</code></td>
<td><code>phone_use</code></td>
</tr>
<tr>
<td><code>yawning</code></td>
<td><code>head_turned_away</code></td>
</tr>
<tr>
<td><code>head_down</code></td>
<td rowspan="2">—</td>
</tr>
<tr>
<td><code>hand_over_mouth</code></td>
</tr>
</tbody>
</table>
</div>

> [!TIP]
> Cue definitions, bounding-box extents, exclusions, co-occurrence rules, and annotation-quality controls are maintained in the [annotation protocol](./docs/annotation-protocol.md).

---

## Current protocol status

> [!NOTE]
> Frozen decisions are marked **🧊 Frozen** in the detailed documents. Exact values that remain open are marked **⚠️ Resolve Later** and must not be silently assumed during implementation.

<details>
<summary><strong>Show the resolve-later checklist</strong></summary>

- [ ] Exact train, validation, and test subject IDs in `splits.json`
- [ ] Exact algorithm/method used to choose the best 8/3/3 subject assignment from annotated per-subject cue distributions
- [ ] Exact numerical validation-selected confidence threshold for each model
- [ ] CUDA, PyTorch, model-framework, NVIDIA GPU-driver, and THOP versions from the actual environment
- [ ] Handling of unsupported/custom operators if THOP does not count them correctly

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
