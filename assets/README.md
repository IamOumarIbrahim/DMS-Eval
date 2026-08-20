# DMS-Eval Visual Assets & Media Suite

[← Back to the DMS-Eval Landing Page](../README.md)

This directory contains the visual media, benchmark distribution charts, framework architecture diagrams, and annotation reference examples for the **DMS-Eval** benchmark framework.

---

## 📂 Directory Layout

```text
assets/
├── README.md                                 # Assets directory documentation (this file)
│
├── branding/                                 # Repository branding & social cards
│   └── socialpreview.png                     # Repository social preview banner (820 px)
│
├── diagrams/                                 # System architecture & lifecycle diagrams
│   ├── dms_eval_pipeline.png                 # End-to-end 6-module benchmark framework flowchart
│   └── dms_crop_geometry.png                 # 1280×720 source-to-640×640 fixed-crop schematic
│
├── charts/                                   # Publication-grade distribution & split figures
│   ├── benchmark_distributions_combined.png  # 2-panel figure: frame composition & warning cue share
│   ├── cue_class_distribution_pie.png        # Pie chart of 4 target warning cues (3,001 boxes)
│   ├── dataset_frame_composition_pie.png     # Donut chart of negative vs positive frames (15,723 frames)
│   ├── split_cue_proportions_comparison.png  # Grouped bar chart across 8/3/3 subject-disjoint partitions
│   ├── pareto_efficiency_frontier.png        # 2D scatter plot: mAP@0.5:0.95 vs. latency/throughput
│   └── qualitative_activation_heatmaps.png   # 2x4 activation grid: Grad-CAM vs. cross-scale attention
│
└── examples/                                 # Annotation & spatial cropping visual examples
    ├── 640X640.png                           # Fixed source-to-crop geometry schematic used in the manuscript
    ├── drinking_annotation_example.png       # Label Studio bounding box: drinking (hand + bottle)
    ├── hand_over_mouth_annotation_example.png# Label Studio bounding box: hand_over_mouth (full head)
    ├── phone_use_annotation_example.png      # Label Studio bounding box: phone_use (hand + phone at ear)
    └── yawning_annotation_example.png        # Label Studio bounding box: yawning (mouth aperture only)
```

---

## 📊 Asset Catalog & Details

<div align="center">

| Subfolder | File | Description | Target Usage |
| :--- | :--- | :--- | :--- |
| **`branding/`** | [`socialpreview.png`](./branding/socialpreview.png) | High-contrast header social card for GitHub repository preview | README header, OpenGraph |
| **`diagrams/`** | [`dms_eval_pipeline.png`](./diagrams/dms_eval_pipeline.png) | 6-module architecture flowchart from video ingestion to test evaluation | README, Manuscript (Fig. 3) |
| **`diagrams/`** | [`dms_crop_geometry.png`](./diagrams/dms_crop_geometry.png) | Fixed crop at `(272,71,640,640)` within each 1280×720 source frame | Manuscript (Fig. 1) |
| **`charts/`** | [`benchmark_distributions_combined.png`](./charts/benchmark_distributions_combined.png) | 2-panel publication figure: (a) frame composition & (b) cue distribution | README, Docs, Manuscript |
| **`charts/`** | [`cue_class_distribution_pie.png`](./charts/cue_class_distribution_pie.png) | Class distribution across 4 cues: `phone_use`, `drinking`, `yawning`, `hand_over_mouth` | Technical documentation |
| **`charts/`** | [`dataset_frame_composition_pie.png`](./charts/dataset_frame_composition_pie.png) | Negative background (80.9%) vs. positive cue (19.1%) frame proportions | Technical documentation |
| **`charts/`** | [`split_cue_proportions_comparison.png`](./charts/split_cue_proportions_comparison.png) | Class proportion preservation ($\le 5.48\%$ relative divergence) across splits | README, Quick-Start, Manuscript |
| **`charts/`** | [`pareto_efficiency_frontier.png`](./charts/pareto_efficiency_frontier.png) | 2-panel Pareto scatter plot: accuracy vs. latency ($p50$) and throughput (FPS) | Technical documentation, Results |
| **`charts/`** | [`qualitative_activation_heatmaps.png`](./charts/qualitative_activation_heatmaps.png) | $2\times 4$ qualitative activation grid: CNN Grad-CAM vs. Transformer attention | Technical documentation, Results |
| **`examples/`** | [`640X640.png`](./examples/640X640.png) | Copy of the fixed source-to-crop geometry schematic | Annotation protocol, Manuscript |
| **`examples/`** | [`yawning_annotation_example.png`](./examples/yawning_annotation_example.png) | Ground truth annotation example enclosing mouth region during yawning | README, Annotation protocol |
| **`examples/`** | [`hand_over_mouth_annotation_example.png`](./examples/hand_over_mouth_annotation_example.png) | Ground truth annotation example enclosing head and occluding hand | README, Annotation protocol |
| **`examples/`** | [`drinking_annotation_example.png`](./examples/drinking_annotation_example.png) | Ground truth annotation example enclosing interacting hand and container | README, Annotation protocol |
| **`examples/`** | [`phone_use_annotation_example.png`](./examples/phone_use_annotation_example.png) | Ground truth annotation example enclosing handheld phone at ear in calling posture | README, Annotation protocol |

</div>

---

## 🛠️ Regeneration Scripts

All charts and architecture diagrams in `assets/charts/` and `assets/diagrams/` are programmatically reproducible via the Python scripts in [`scripts/charts/`](../scripts/charts/):

```bash
# Generate distribution pie charts and 2-panel publication figure
uv run python scripts/charts/generate_distribution_charts.py

# Generate split comparison bar chart and baseline pipeline diagram
uv run python scripts/charts/generate_pipeline_and_split_charts.py

# Generate high-DPI redesigned 6-module pipeline architecture diagram
uv run python scripts/charts/generate_pipeline_diagram_redesign.py

# Generate the tracked source-to-crop geometry schematic
python scripts/publication/generate_crop_geometry.py
```
