# DMS-Eval

**DMS-Eval** is a benchmark for evaluating lightweight object detection architectures for real-time driver monitoring systems. It compares detection accuracy, inference performance, and deployment efficiency across a custom multi-condition dataset covering normal driving, distraction, fatigue, and low-visibility nighttime scenarios.

![Status: In Development](https://img.shields.io/badge/Status-In_Development-orange?style=flat) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Table of Contents

* [Overview](#overview)

  * [Paper Scope](#paper-scope)
* [Evaluated Models](#evaluated-models)
* [Evaluation Metrics](#evaluation-metrics)
* [Project Structure](#project-structure)
* [Authors & Acknowledgments](#authors--acknowledgments)
* [License](#license)


# Overview

> ### Paper Scope

DMS-Eval benchmarks lightweight object detection architectures for **driver state monitoring**, with a focus on detecting drowsiness and distraction under realistic operating conditions.

The study evaluates models on a custom multi-condition dataset covering **normal driving, distraction, fatigue, and low-visibility nighttime scenarios**, with emphasis on the trade-off between **detection accuracy, inference speed, and deployment efficiency**.


## Evaluated Models

Compute-Constrained Comparison: All models are lightweight variants operating within a narrow 2.4–4.0M parameter and 5.4–7.0 GFLOP budget at 640×640 input resolution. This constrains model capacity while preserving architectural diversity across convolutional, attention-based, DETR-style, and end-to-end detectors.

Controlled Evaluation: All models are evaluated using the same dataset split, 640×640 input resolution, hardware, batch size, numerical precision, and evaluation protocol. Accuracy and runtime measurements therefore provide a controlled comparison of the practical accuracy–efficiency trade-offs among the selected architectures.

<div align="center">

<table>
  <tr>
    <th>Model</th>
    <th>Parameters (M)</th>
    <th>FLOPs (G)</th>
    <th>Architectural Focus</th>
  </tr>
  <tr>
    <td>YOLO11n</td>
    <td>2.6</td>
    <td>6.5</td>
    <td>Convolutional baseline (C3k2 / CSP-style)</td>
  </tr>
  <tr>
    <td>YOLOv12n</td>
    <td>2.6</td>
    <td>6.5</td>
    <td>Area Attention / R-ELAN</td>
  </tr>
  <tr>
    <td>D-FINE-N</td>
    <td>4.0</td>
    <td>7.0</td>
    <td>DETR-style fine-grained distribution refinement</td>
  </tr>
  <tr>
    <td>YOLO26n</td>
    <td>2.4</td>
    <td>5.4</td>
    <td>DFL-free native end-to-end inference</td>
  </tr>
</table>

</div>



## Evaluation Metrics


The benchmark evaluates each model across both **detection quality** and **deployment efficiency** under a controlled evaluation protocol.

> **Primary Detection Metric**

* **mAP@0.5:0.95:** Primary detection metric, averaged across IoU thresholds from 0.50 to 0.95.

> **Threshold-Controlled Metrics**

All models use the same confidence and IoU thresholds.

* **Precision:** Proportion of predicted detections that are correct.
* **Recall:** Proportion of ground-truth objects successfully detected.
* **F1-Score:** Harmonic mean of precision and recall.

> **Runtime Performance**

All models are evaluated using the same hardware, batch size, numerical precision, input resolution, backend, warm-up procedure, and timing methodology.

* **End-to-End FPS:** Processing throughput of the complete inference pipeline.
* **Model-Only Latency (ms):** Raw model inference time excluding preprocessing and post-processing.

> **Deployment Characteristics**

* **Parameters (M):** Total number of model parameters.
* **FLOPs (G):** Approximate computational cost per 640×640 input.
* **Model File Size (MB):** Stored model footprint for deployment.

> **Optional Metrics**

* **mAP@0.5:** Detection performance at an IoU threshold of 0.50.
* **Peak Inference Memory:** Maximum memory consumption observed during inference.



## Project Structure
```text
.
├── REFERENCES/
│   └── references.bib    // BibTeX sources
├── .gitignore            // Ignored files
├── CHANGELOG.md          // Version history
├── LICENSE               // Usage license
└── README.md             // Project documentation
```
## Authors & Acknowledgments

* **Dr. Mohamad Khairi bin Ishak** (Associate Professor)  
  Department of Computer Engineering, University of Sharjah  
  📧 [mishak@sharjah.ac.ae](mailto:mishak@sharjah.ac.ae)

* **Oumar Mamoun Ibrahim** (Senior Undergraduate Researcher)  
  Department of Computer Engineering, University of Sharjah  
  📧 [U22200741@sharjah.ac.ae](mailto:U22200741@sharjah.ac.ae)

> [!NOTE]
> This research and codebase are prepared for submission to the 5th International Conference on Artificial Intelligence Science and Applications in Industry and Society (CAISAIS 2026).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.