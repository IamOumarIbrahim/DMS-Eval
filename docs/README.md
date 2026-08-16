# DMS-Eval Documentation Index


**DMS-Eval Documentation** serves as the central technical reference and navigation hub for the DMS-Eval benchmark suite, covering experimental protocols, evaluated lightweight models, methodology, execution milestones, literature review, and reproduction workflows.

![Status: In Development](https://img.shields.io/badge/Status-In_Development-orange?style=flat) [![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](../LICENSE) ![Input: 640×640](https://img.shields.io/badge/Input-640%C3%97640-555?style=flat) ![Protocol: v2.0](https://img.shields.io/badge/Protocol-2.0.0--fairness--lock-brightgreen?style=flat)

## Table of Contents

* [Overview](#overview)
* [Documentation Map](#documentation-map)
* [Benchmark Specifications](#benchmark-specifications)
* [Methodology & Validity](#methodology--validity)
* [Experiments & Milestones](#experiments--milestones)
* [Literature & Context](#literature--context)
* [Quick Start Guide](#quick-start-guide)
* [Directory Layout](#directory-layout)

---

## Overview

> ### Core Principle
>
> All documentation in this directory adheres to the **strict fairness and methodological transparency protocol** of DMS-Eval. Specifications are modularized to separate experimental contracts, architectural analysis, experimental outputs, and literature synthesis.

> [!TIP]
> If you are new to the repository and looking to set up the environment and reproduce benchmarks, begin with the [Quick Start Guide](quick-start.md). For research questions and evaluation rules, consult the [Benchmark Protocol](benchmark/benchmark-protocol.md).

---

## Documentation Map

<div align="center">

<table>
  <tr>
    <th align="center">Category</th>
    <th align="center">Document</th>
    <th align="left">Description & Focus Area</th>
  </tr>

  <tr>
    <td align="center" rowspan="4"><strong>Benchmark</strong></td>
    <td align="center"><a href="benchmark/benchmark-protocol.md"><strong>benchmark-protocol.md</strong></a></td>
    <td align="left">Master experimental contract, primary research question (RQ), metric suite, and frozen fairness constraints.</td>
  </tr>
  <tr>
    <td align="center"><a href="benchmark/scope.md"><strong>scope.md</strong></a></td>
    <td align="left">Explicit in-scope / out-of-scope boundaries, target cue ontology (6 classes), and single-frame detection framing.</td>
  </tr>
  <tr>
    <td align="center"><a href="benchmark/models.md"><strong>models.md</strong></a></td>
    <td align="left">Evaluated lightweight model architectures (YOLO11n, YOLO26n, D-FINE-N), parameters, FLOPs, and official reference metrics.</td>
  </tr>
  <tr>
    <td align="center"><a href="benchmark/setup.md"><strong>setup.md</strong></a></td>
    <td align="left">Hardware specifications (NVIDIA RTX 4060), execution environment, profiling protocol, and subject-disjoint dataset split.</td>
  </tr>

  <tr>
    <td align="center" rowspan="2"><strong>Methodology</strong></td>
    <td align="center"><a href="methodology/contribution.md"><strong>contribution.md</strong></a></td>
    <td align="left">Claimed scientific contributions, domain impact, and prospective long-term research horizons.</td>
  </tr>
  <tr>
    <td align="center"><a href="methodology/limitations.md"><strong>limitations.md</strong></a></td>
    <td align="left">Methodological limitations, sensor constraints, synthetic artifacts, and single-frame boundaries.</td>
  </tr>

  <tr>
    <td align="center" rowspan="2"><strong>Experiments</strong></td>
    <td align="center"><a href="experiments/execution-timeline.md"><strong>execution-timeline.md</strong></a></td>
    <td align="left">Structured 8-phase execution schedule, freeze milestones, and submission delivery plan.</td>
  </tr>
  <tr>
    <td align="center"><a href="experiments/results.md"><strong>results.md</strong></a></td>
    <td align="left">Experimental output tables, detection accuracy, latency percentiles, FPS throughput, and slice analysis results.</td>
  </tr>

  <tr>
    <td align="center"><strong>Literature</strong></td>
    <td align="center"><a href="literature/related-works.md"><strong>related-works.md</strong></a></td>
    <td align="left">Systematic related work review, taxonomy, and comparative matrix across prior DMS datasets and detectors.</td>
  </tr>

  <tr>
    <td align="center"><strong>Guides</strong></td>
    <td align="center"><a href="quick-start.md"><strong>quick-start.md</strong></a></td>
    <td align="left">Step-by-step developer and researcher instructions to reproduce and run DMS-Eval pipelines.</td>
  </tr>
</table>

<p>
  <sub><strong>Table 1.</strong> Complete index of DMS-Eval documentation modules and technical specifications.</sub>
</p>

</div>

---

## Benchmark Specifications

The `benchmark/` module defines the operational rules and experimental setup for the evaluation suite:

* **[Benchmark Protocol](benchmark/benchmark-protocol.md):** Governs the frozen evaluation rules, evaluation metrics (AP<sub>50:95</sub>, AP<sub>50</sub>, Precision, Recall, F1, Latency Median/p95, FPS, Footprint), and strict identical-treatment policies.
* **[Scope & Ontology](benchmark/scope.md):** Defines the single-frame spatial detection scope across 6 target classes (`eyes_open`, `eyes_closed`, `yawning`, `cellphone`, `bottle`, `hair_comb`) across Face and Body camera streams.
* **[Evaluated Models](benchmark/models.md):** Analyzes the selected lightweight models ($\le 5.0\text{M}$ parameters):
  * **YOLO11n:** Convolutional/CSPNet baseline with NMS post-processing.
  * **YOLO26n:** End-to-end NMS-free convolutional detector with DFL elimination.
  * **D-FINE-N:** DETR-family hybrid with Fine-grained Distribution Refinement (FDR).
* **[Experimental Setup](benchmark/setup.md):** Details the standardized NVIDIA RTX 4060 profiling platform, batch size 1 constraints, FP16/FP32 precision locks, and 14-subject disjoint splits (8 Train / 3 Val / 3 Test).

---

## Methodology & Validity

The `methodology/` module outlines the scientific foundations and boundary conditions:

* **[Scientific Contributions](methodology/contribution.md):** Highlights the four key contributions of DMS-Eval, spanning controlled lightweight benchmarking, unified ontology curation, multi-dimensional trade-off profiling, and stratified condition slicing.
* **[Empirical Limitations](methodology/limitations.md):** Explicitly documents boundary constraints including frame-level detection without temporal recurrent states, RGB camera dependency, and sensor-specific edge cases.

---

## Experiments & Milestones

The `experiments/` module tracks project execution, milestones, and empirical data:

* **[Execution Timeline](experiments/execution-timeline.md):** Details the 8-phase execution schedule leading to conference submission:
  * **Phase 1:** Scope & Protocol Lock (Aug 16–17)
  * **Phase 2:** Data Pipeline & Setup (Aug 18–20)
  * **Phase 3:** Training & Test Eval (Aug 21–24)
  * **Phase 4:** Analysis & Visuals (Aug 25)
  * **Phase 5:** Manuscript Drafting (Aug 26–28)
  * **Phase 6:** Reproducibility Audit (Aug 29)
  * **Phase 7:** Final Polish & Review (Aug 30)
  * **Phase 8:** Paper Submission (Aug 31)
* **[Results & Tables](experiments/results.md):** Houses locked result table schemas and final test-set empirical outputs.

---

## Literature & Context

The `literature/` module contextualizes DMS-Eval within the broader driver monitoring research ecosystem:

* **[Related Works](literature/related-works.md):** Provides taxonomy and comparative matrices across existing driver drowsiness datasets, distraction benchmarks, and real-time detection architectures.

---

## Quick Start Guide

* **[Quick Start](quick-start.md):** Complete guide for installing dependencies, downloading preprocessed dataset splits, verifying model checkpoints, and running unified evaluation scripts.

---

## Directory Layout

```text
docs/
├── README.md                       # Documentation index / navigation
│
├── benchmark/
│   ├── benchmark-protocol.md       # Master experimental contract
│   ├── scope.md                    # In-scope / out-of-scope
│   ├── models.md                   # YOLO11n / YOLO26n / D-FINE-N
│   └── setup.md                    # Hardware, software, environment
│
├── methodology/
│   ├── contribution.md             # Claimed contributions
│   └── limitations.md              # Known methodological limitations
│
├── experiments/
│   ├── execution-timeline.md       # Schedule / freeze dates
│   └── results.md                  # Experimental outputs
│
├── literature/
│   └── related-works.md            # Related-work notes / comparison matrix
│
└── quick-start.md                  # How to reproduce/run DMS-Eval
```
