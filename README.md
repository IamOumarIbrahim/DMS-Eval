# DMS-Eval

This paper presents a comprehensive benchmark of state-of-the-art lightweight vision architectures across a novel, multi-condition dataset to evaluate the critical trade-offs between real-time inference speed and detection accuracy for intelligent driver monitoring systems.

![Status: In Development](https://img.shields.io/badge/Status-In_Development-orange?style=flat) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Table of Contents

* [Overview](#overview)
  * [Paper Scope](#paper-scope)
  * [Evaluation Metrics](#evaluation-metrics)
  * [Project Structure](#project-structure)
* [Authors & Acknowledgments](#authors--acknowledgments)
* [License](#license)

## Overview 
> ### Paper Scope
Benchmarking lightweight models in driver state monitoring (drowsiness and distraction). This includes developing a novel dataset that spans normal, distracted, fatigued, and low-visibility nighttime conditions.

> ### Evaluation Metrics

* **Mean Average Precision (mAP):** Assess detection accuracy across varying confidence thresholds and IoU levels.
* **Accuracy:** Measure overall classification correctness across the entire test set.
* **Precision:** Evaluate the proportion of true positive predictions among all positive detections.
* **Recall:** Determine the model's ability to identify all ground-truth positive instances.
* **F1-Score:** Compute the harmonic mean of precision and recall to evaluate balanced performance.
* **Inference Speed (FPS):** Benchmark latency and real-time processing throughput in frames per second.
* **Model Size:** Quantify storage footprint, parameter count, and memory overhead for deployment feasibility.



> ### Project Structure
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