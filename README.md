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

> [!TIP]
> All models operate within **2.4–4.0M parameters**, **5.4–7.0 GFLOPs**, and use **640×640 inputs**, keeping the comparison compute-constrained while preserving architectural diversity.

**Controlled Evaluation:** All models are evaluated using the same dataset split, hardware, batch size, numerical precision, input resolution, and evaluation protocol. This provides a consistent basis for comparing detection accuracy, inference speed, and deployment efficiency across the selected architectures.

<div align="center">

<table>
  <tr>
    <th align="center">Model</th>
    <th align="center">Architectural Focus</th>
    <th align="center">Post-processing</th>
  </tr>
  <tr>
    <td align="center">YOLO11n</td>
    <td align="center">Convolutional baseline (C3k2 / CSP-style)</td>
    <td align="center">NMS-based</td>
  </tr>
  <tr>
    <td align="center">YOLOv12n</td>
    <td align="center">Area Attention / R-ELAN</td>
    <td align="center">NMS-based</td>
  </tr>
  <tr>
    <td align="center">D-FINE-N</td>
    <td align="center">DETR-style fine-grained distribution refinement</td>
    <td align="center">End-to-end / NMS-free</td>
  </tr>
  <tr>
    <td align="center">YOLO26n</td>
    <td align="center">DFL-free native end-to-end inference</td>
    <td align="center">Native NMS-free</td>
  </tr>
</table>

<br>

<table>
  <tr>
    <td align="center" width="50%">
      <img
        src="assets/Computational%20Characteristics%20of%20Evaluated%20Models%20(a).png"
        width="95%"
        alt="Parameter count comparison"
      />
    </td>
    <td align="center" width="50%">
      <img
        src="assets/Computational%20Characteristics%20of%20Evaluated%20Models%20(b).png"
        width="95%"
        alt="FLOPs comparison"
      />
    </td>
  </tr>
</table>

<p>
  <em>Figure 1. Relative computational footprint of the evaluated lightweight detector variants.</em>
</p>

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