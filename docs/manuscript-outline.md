# Manuscript Outline: DMS-Eval

**Target Venue:** CAISAIS 2026 (Nov 25–27, 2026)  
**Submission Deadline:** 31 August 2026  
**Page Limit:** **6 pages maximum (including references)**

---

## Primary Research Question
> "How do lightweight object detection architectures compare in terms of detection performance, inference efficiency, and deployment footprint for frame-level driver drowsiness and distraction detection under diverse driving conditions?"

---

## 6-Page Budget & Section Breakdown

| Section | Target Length | Core Content & Key Elements |
| :--- | :---: | :--- |
| **Abstract & Title** | — | High-level problem, exact parameter budget (2.4–4.0M), key quantitative trade-off takeaways. |
| **1. Introduction** | **~0.75 – 1.0 p.** | • In-cabin driver monitoring & embedded edge compute constraints.<br>• Scope definition: **Frame-level observable cues** vs. temporal driver-state modeling.<br>• **Primary Research Question** (locked wording).<br>• Core contributions. |
| **2. Related Work** | **~0.5 – 0.75 p.** | • In-cabin DMS datasets and benchmarking gaps.<br>• Lightweight real-time 2D object detection architectures. |
| **3. Benchmark Protocol & Methodology** | **~1.25 – 1.5 p.** | • Observable cue ontology & single-frame annotation schema.<br>• Subject-disjoint split protocol (no cross-split driver/session leakage).<br>• Model selection criteria (2.4–4.0M params, 5.4–7.0 GFLOPs, 640×640 input).<br>• Metric contract (mAP@[.50:.95], mAP50, per-class AP, latency, FPS, memory, GFLOPs) & hardware profiling contract. |
| **4. Empirical Results & Trade-Offs** | **~1.5 – 1.75 p.** | • **Main Benchmark Table**: Accuracy vs. latency vs. footprint.<br>• **Pareto Frontier Plot**: Accuracy vs. inference speed.<br>• Sub-condition robustness breakdown (day/night illumination, occlusion, glasses/accessories). |
| **5. Discussion & Limitations** | **~0.5 p.** | • Key failure modes (fine cues, extreme angles, occlusions).<br>• Explicit limitations: single-frame cues vs. temporal multi-frame inference.<br>• Edge deployment recommendations. |
| **6. Conclusion & Reproducibility** | **~0.25 p.** | • Summary of findings.<br>• Code, weights, and evaluation harness availability. |
| **References** | **~0.5 – 0.75 p.** | • 15–22 targeted, relevant citations (fitting within the final page columns). |
| **Total** | **6.0 pages** | **Strictly compliant with the CAISAIS 2026 page ceiling.** |

