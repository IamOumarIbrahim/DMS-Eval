# DMS-Eval


**DMS-Eval** is a planned benchmark framework currently in development for evaluating lightweight object detection architectures for detecting visual cues associated with driver drowsiness and distraction in real-time across diverse cabin operating conditions.

![Status: In Development](https://img.shields.io/badge/Status-In_Development-orange?style=flat) [![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE) ![Input: 640×640](https://img.shields.io/badge/Input-640%C3%97640-555?style=flat) ![Detectors: YOLO | DETR](https://img.shields.io/badge/Detectors-YOLO%20%7C%20DETR-4c1?style=flat)

<p align="center">
  <img src="assets/socialpreview.png" width="640" alt="DMS-Eval">
</p>

## Table of Contents

* [Overview](#overview)
  * [Paper Scope](#paper-scope)
  * [Research Question](#research-question)
  * [Planned Contributions](#planned-contributions)
* [Evaluation Setup](#evaluation-setup)
* [Evaluated Models](#evaluated-models)
  * [Official Reference Benchmark](#official-reference-benchmark)
* [Evaluation Metrics](#evaluation-metrics)
* [Evaluation Dataset](#evaluation-dataset)
* [Evaluation Scope](#evaluation-scope)
* [Evaluation Results](#evaluation-results)
* [Execution Timeline](#execution-timeline)
* [Future Work](#future-work)
* [Project Structure](#project-structure)
* [Authors & Credits](#authors--credits)
  * [Authors](#authors)
  * [Acknowledgments](#acknowledgments)
* [License](#license)



## Overview

> ### Paper Scope
>
> This study will conduct a controlled empirical comparison of lightweight 2D object detectors, assessing the multi-dimensional trade-offs between **detection accuracy, inference speed, and deployment footprint** under diverse cabin environments.

> ### Research Question
>
> **RQ**: ”Under a controlled compute-constrained evaluation, how do lightweight object detectors compare in accuracy, inference efficiency, and robustness when detecting visual cues associated with driver distraction and drowsiness across normal and low-light/nighttime driving conditions?"

### Planned Contributions

1. **Controlled lightweight benchmark:** A strictly controlled empirical evaluation of candidate lightweight object detectors under standardized hardware, resolution, and optimization constraints.
2. **Unified dataset & ontology:** A custom unified benchmark dataset and annotation ontology covering normal driving, distraction-related objects, drowsiness-associated visual cues, and low-visibility nighttime conditions.
3. **Accuracy–efficiency trade-offs:** Comprehensive accuracy–efficiency comparison evaluating mAP (AP<sub>50:95</sub>, AP<sub>50</sub>), Precision, Recall, F1, latency percentiles (median, p95), FPS throughput, parameter count, and model weight size.
4. **Condition-wise slice analysis:** Disaggregated condition-wise analysis identifying where each architectural paradigm succeeds or degrades across environmental and behavioral variations.

## Evaluation Setup

> **Identical experimental opportunity, identical data exposure, identical external preprocessing/evaluation/hardware, architecture-native internal mechanisms, and zero model-specific access to the held-out test set.**

> [!TIP]
> All target models represent diverse lightweight pretrained detector systems spanning conventional YOLO, DETR, and native end-to-end architectures. All models use standardized **640×640 inputs** and are initialized from official **COCO-pretrained weights** under a strictly controlled evaluation protocol.


<div align="center">

<img src="assets/640X640.png" width="34%" alt="640×640 benchmark input resolution">


<sub><strong>Figure 1.</strong> Standardized 640×640 input resolution.</sub>


<table>
  <tr>
    <th align="center">Evaluation Setting</th>
    <th align="center">Configuration</th>
  </tr>
  <tr>
    <td align="center"><strong>Dataset Split</strong></td>
    <td align="center">—</td>
  </tr>
  <tr>
    <td align="center"><strong>Hardware</strong></td>
    <td align="center">NVIDIA GeForce RTX 4060 (8 GB VRAM)</td>
  </tr>
  <tr>
    <td align="center"><strong>Batch Size</strong></td>
    <td align="center">—</td>
  </tr>
  <tr>
    <td align="center"><strong>Numerical Precision</strong></td>
    <td align="center">—</td>
  </tr>
  <tr>
    <td align="center"><strong>Input Resolution</strong></td>
    <td align="center">—</td>
  </tr>
  <tr>
    <td align="center"><strong>Evaluation Protocol</strong></td>
    <td align="center">—</td>
  </tr>
</table>


<sub><strong>Table 1.</strong> Planned evaluation configuration.</sub>

</div>

## Evaluated Models

<div align="center">

<table>
  <tr>
    <th align="center">Model</th>
    <th align="center">Family</th>
    <th align="center">Architectural Focus</th>
    <th align="center">Post-processing</th>
    <th align="center">Source</th>
  </tr>

  <tr>
    <td align="center">YOLO11n</td>
    <td align="center">YOLO</td>
    <td align="center">C3k2 / CSP-style convolutional baseline</td>
    <td align="center">NMS-based</td>
    <td align="center">
      <a href="https://docs.ultralytics.com/models/yolo11/"><strong>Ultralytics</strong></a>
    </td>
  </tr>

  <tr>
    <td align="center">D-FINE-N</td>
    <td align="center">DETR</td>
    <td align="center">Fine-grained distribution refinement</td>
    <td align="center">End-to-end / NMS-free</td>
    <td align="center">
      <a href="https://github.com/Peterande/D-FINE"><strong>Official Repo</strong></a>
    </td>
  </tr>

  <tr>
    <td align="center">YOLO26n</td>
    <td align="center">YOLO</td>
    <td align="center">DFL-free native end-to-end inference</td>
    <td align="center">Native NMS-free</td>
    <td align="center">
      <a href="https://docs.ultralytics.com/models/yolo26/"><strong>Ultralytics</strong></a>
    </td>
  </tr>
</table>

<p>
  <sub><strong>Table 2.</strong> Architectural characteristics of lightweight object detectors selected for evaluation.</sub>
</p>

</div>

### Official Reference Benchmark

> [!NOTE]
> The values below are **official COCO validation benchmarks reported by the respective model authors** and are provided only as reference points. They are **not DMS-Eval results**.

<div align="center">

<table>
  <tr>
    <th align="center">Model</th>
    <th align="center">Input</th>
    <th align="center">AP<sup>val</sup><sub>50:95</sub></th>
    <th align="center">T4 Latency<br>(ms)</th>
    <th align="center">Params (M)</th>
    <th align="center">GFLOPs</th>
  </tr>

  <tr>
    <td align="center">
      <a href="https://docs.ultralytics.com/models/yolo11#performance-metrics"><strong>YOLO11n</strong></a>
    </td>
    <td align="center">640×640</td>
    <td align="center">39.5</td>
    <td align="center">1.50</td>
    <td align="center">2.6</td>
    <td align="center">6.5</td>
  </tr>

  <tr>
    <td align="center">
      <a href="https://github.com/Peterande/D-FINE#coco"><strong>D-FINE-N</strong></a>
    </td>
    <td align="center">640×640</td>
    <td align="center">42.8</td>
    <td align="center">2.12</td>
    <td align="center">4.0</td>
    <td align="center">7.0</td>
  </tr>

  <tr>
    <td align="center">
      <a href="https://docs.ultralytics.com/models/yolo26#performance-metrics"><strong>YOLO26n</strong></a>
    </td>
    <td align="center">640×640</td>
    <td align="center">40.1<sup>e2e</sup></td>
    <td align="center">1.70</td>
    <td align="center">2.4</td>
    <td align="center">5.4</td>
  </tr>
</table>

<p>
  <sub><strong>Table 3.</strong> Official COCO reference performance reported for candidate lightweight detector variants. YOLO26n reports 40.1 AP<sub>50:95</sub> for its native end-to-end inference path (40.9 AP<sub>50:95</sub> for the conventional detection path).</sub>
</p>

</div>

## Evaluation Metrics


The planned benchmark will evaluate each model across both **detection quality** and **deployment efficiency** under a controlled evaluation protocol.

<div align="center">

<table>
  <tr>
    <th>Category</th>
    <th>Metrics</th>
  </tr>
  <tr>
    <td><strong>Detection Quality</strong></td>
    <td>AP<sub>50:95</sub> (Primary), AP<sub>50</sub>, Precision, Recall, F1, Balanced Accuracy</td>
  </tr>
  <tr>
    <td><strong>Robustness & Slice Analysis</strong></td>
    <td>Condition-wise breakdown (normal daylight vs. low-light/nighttime, behavioral slices)</td>
  </tr>
  <tr>
    <td><strong>Safety Diagnostics</strong></td>
    <td>False Positives per Normal Image (FP/image)</td>
  </tr>
  <tr>
    <td><strong>Runtime Efficiency</strong></td>
    <td>End-to-End FPS, Latency (Median & p95, ms)</td>
  </tr>
  <tr>
    <td><strong>Complexity & Deployment</strong></td>
    <td>Params (M), GFLOPs, Weight Size (MB), Peak Inference Memory (MB)</td>
  </tr>
</table>

<p>
  <sub><strong>Table 4.</strong> Planned evaluation metrics to assess detection quality, runtime performance, model complexity, and deployment characteristics.</sub>
</p>



</div>

> **Primary Detection Metric**

* **AP<sub>50:95</sub>:** Primary detection metric, averaged across IoU thresholds from 0.50 to 0.95.

> **Secondary Detection Metrics**

All models will use standardized confidence and IoU thresholds.

* **AP<sub>50</sub>:** Detection performance at an IoU threshold of 0.50.
* **Precision:** Proportion of predicted detections that are correct.
* **Recall:** Proportion of ground-truth objects successfully detected.
* **F1:** Macro arithmetic mean of per-class F1 scores at the frozen operating point.
* **Balanced Accuracy:** Macro balanced frame-level cue presence/absence accuracy across evaluable classes.

> **Robustness & Slice Analysis**

* **Condition-wise Breakdown:** Stratified slice evaluation reporting primary detection metrics (AP<sub>50:95</sub>, AP<sub>50</sub>, Precision, Recall, F1) disaggregated across environmental conditions (normal daylight vs. low-light/nighttime) and behavioral scenarios (normal, distracted, fatigued/drowsy) to evaluate operational sensitivity and failure modes.

> **Safety Diagnostic**

* **False Positives per Normal Image:** Total predicted warning cues on normal frames divided by the number of normal frames.

> **Runtime Performance**

All models will be evaluated using standardized hardware, batch size, numerical precision, input resolution, backend, warm-up procedure, and timing methodology.

* **End-to-End FPS:** Processing throughput of the complete inference pipeline.
* **Latency (Median / p95 ms):** Model inference latency distributions measured across synchronized inference iterations.

> **Deployment Footprint & Complexity**

* **Params (M):** Total number of model parameters.
* **GFLOPs:** Approximate computational cost per 640×640 input.
* **Weight Size (MB):** On-disk serialized model weight footprint for deployment.
* **Peak Inference Memory (MB):** Maximum runtime GPU/VRAM allocation during inference.

## Evaluation Dataset

DMS-Eval curates a **custom unified benchmark dataset** derived from the public RGB real-car streams of the **[Driver Monitoring Dataset (DMD)](https://dmd.vicomtech.org/)** ([GitHub](https://github.com/Vicomtech/DMD-Driver-Monitoring-Dataset)) across 14 authorized subjects partitioned under a strict subject-disjoint split (8 Train / 3 Val / 3 Test).

* **Condition Coverage:** Spans four core operating environments across Face and Body camera angles: **normal daylight**, **distracted**, **fatigued/drowsy**, and **low-light/nighttime**.
* **Target Classes:** Evaluates drowsiness-associated visual cues (`eyes_open`, `eyes_closed`, `yawning`) and distraction-associated objects (`cellphone`, `bottle`, `hair_comb`).
* **Licensing:** Original source data terms are governed by Vicomtech under [CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/).

## Evaluation Scope

> [!IMPORTANT]
> DMS-Eval will evaluate lightweight 2D object detection architectures at the **frame level** under a controlled single-frame detection protocol.

The planned benchmark focuses strictly on spatially observable driver-monitoring cues associated with drowsiness and distraction. Temporal aggregation across video sequences, cue duration modeling, and temporal driver-state inference are outside the scope of the planned study.

## Evaluation Results

### Detection Performance & Robustness

| Model | AP<sub>50:95</sub> | AP<sub>50</sub> | Precision | Recall | F1 | Low-light AP<sub>50:95</sub> |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **YOLO11n** | — | — | — | — | — | — |
| **D-FINE-N** | — | — | — | — | — | — |
| **YOLO26n** | — | — | — | — | — | — |

<p>
  <sub><strong>Table 5.</strong> Planned detection performance and low-light robustness evaluation results (to be populated upon benchmark execution).</sub>
</p>

### Inference Efficiency & Deployment Footprint

| Model | Params (M) | Median Latency (ms) | p95 Latency (ms) | FPS | Weight Size (MB) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **YOLO11n** | 2.6 | — | — | — | — |
| **D-FINE-N** | 4.0 | — | — | — | — |
| **YOLO26n** | 2.4 | — | — | — | — |

<p>
  <sub><strong>Table 6.</strong> Planned runtime efficiency, latency percentiles, throughput, and model footprint on NVIDIA RTX 4060 (to be populated upon benchmark execution).</sub>
</p>

## Execution Timeline

| Date Range | Phase | Key Deliverables & Tasks |
| :--- | :--- | :--- |
| **Aug 16–17** | **Phase 1: Scope & Protocol Lock** | Freeze RQ, model choices, ontology, dataset sources, splits, and evaluator harness. |
| **Aug 18–20** | **Phase 2: Data Pipeline & Setup** | Finish annotation/conversion, leakage checks, dataset manifests, and training pipeline. *(Hard Freeze at end of Aug 20)* |
| **Aug 21–24** | **Phase 3: Training & Test Eval** | Train/retrain all 3 models; run untouched test-set evaluation. |
| **Aug 25** | **Phase 4: Analysis & Visuals** | Condition-wise evaluation, plots/tables generation, and error analysis. |
| **Aug 26–28** | **Phase 5: Manuscript Drafting** | Write the complete 6-page IEEE paper. |
| **Aug 29** | **Phase 6: Reproducibility Audit** | Reproducibility & fairness audit (no redesign unless an actual blocker is found). |
| **Aug 30** | **Phase 7: Final Polish & Review** | IEEE formatting check, reference validation, figures alignment, PDF checks, final PI review. |
| **Aug 31** | **Phase 8: Paper Submission** | Final submission ahead of the September 1, 2026 deadline. |

<p>
  <sub><strong>Table 7.</strong> Project execution schedule and milestones leading to final paper submission.</sub>
</p>

> [!IMPORTANT]
> **After August 20, no new dataset, model, metric, ontology, or benchmark design change unless an existing choice is scientifically invalid.**

## Future Work

Future extensions of DMS-Eval may investigate:

* **Attention-centric YOLO architectures:** Investigate models such as YOLOv12n (Turbo) featuring area attention and R-ELAN backbones once downstream deployment runtimes and tooling mature.
* **Temporal driver-state modeling:** Aggregate frame-level detections across video sequences to capture cue persistence, duration, frequency, and temporal evolution.
* **Benchmark expansion:** Extend the dataset with additional subjects, driving environments, camera viewpoints, and challenging low-illumination conditions.
* **Cross-dataset evaluation:** Assess model generalization across independently collected driver-monitoring datasets.
* **Edge deployment:** Evaluate optimized models on resource-constrained embedded hardware using deployment-oriented inference backends and numerical precision settings.

## Project Structure

```text
.
├── assets/                       # Visual assets and documentation diagrams
│   ├── 640X640.png               # Standardized input resolution diagram
│   └── socialpreview.png         # Repository preview banner
├── core/                         # [Planned] Benchmark evaluation harness and dataset pipelines
├── docs/                         # Specifications, protocols, and planning documentation
│   ├── README.md                 # Documentation index / navigation
│   ├── benchmark/
│   │   ├── benchmark-protocol.md # Master experimental contract
│   │   ├── models.md             # YOLO11n / YOLO26n / D-FINE-N
│   │   ├── scope.md              # In-scope / out-of-scope
│   │   └── setup.md              # Hardware, software, environment
│   ├── experiments/
│   │   ├── execution-timeline.md # Schedule / freeze dates
│   │   └── results.md            # Experimental outputs
│   ├── literature/
│   │   └── related-works.md      # Related-work notes / comparison matrix
│   ├── methodology/
│   │   ├── contribution.md       # Claimed contributions
│   │   └── limitations.md        # Known methodological limitations
│   └── quick-start.md            # How to reproduce/run DMS-Eval
├── manuscript/                   # IEEE conference manuscript source files
│   ├── bib/
│   │   └── references.bib        # BibTeX bibliography references
│   ├── figures/                  # Manuscript figure assets
│   │   └── fig1.png              # Overview system methodology figure
│   ├── style/                    # IEEEtran LaTeX style and formatting classes
│   │   ├── IEEEtran.bst
│   │   └── IEEEtran.cls
│   └── main.tex                  # Primary LaTeX manuscript file
├── third-party/                  # External dataset specs and third-party references
│   └── docs/
│       └── DMD/
│           └── DMD-README.md     # Upstream DMD dataset documentation & notes
├── .gitignore                    # Git ignore rules and build artifact exclusions
├── CHANGELOG.md                  # Project version history and milestone tracking
├── LICENSE                       # Apache 2.0 open-source license
└── README.md                     # Project overview and benchmark specification
```

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
