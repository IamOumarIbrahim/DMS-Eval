# DMS-Eval Processing & Execution Scripts

[← Back to the DMS-Eval Landing Page](../README.md)

This directory contains the complete Python script suite powering the data extraction, preprocessing, annotation management, split balancing, and visual asset generation pipelines for the **DMS-Eval** benchmark.

---

## 📂 Directory Layout

```text
scripts/
├── README.md                          # Scripts documentation suite (this file)
│
├── extract_and_crop_dmd.py            # [Stage 1] Multi-processed video extraction & 640x640 cropping
├── assemble_master_coco.py            # [Stage 2] Assembles Label Studio exports into master COCO JSON
├── split_annotations_per_subject.py   # [Stage 3] Partitions ground truth into 14 per-subject folders
├── balance_splits.py                  # [Stage 4] Exhaustive 8/3/3 subject-disjoint split optimizer
├── create_shuffled_annotations.py     # [Stage 5] Generates Training/Val/Test hierarchy with seed-13 shuffle
├── convert_coco_to_yolo.py            # [Stage 6] Converts master COCO JSON to YOLO format labels & YAML
├── prepare_dfine_coco.py              # [Stage 7] Partitions master COCO JSON into D-FINE/DETR split JSONs
├── train_yolo.py                      # [Stage 8] YOLO training engine with gradient accumulation & telemetry
├── evaluate_benchmark.py              # [Stage 9] Evaluator harness, validation threshold sweep & profiler
│
├── charts/                            # [Gitignored] Publication chart & diagram generators
│   ├── generate_distribution_charts.py
│   ├── generate_pipeline_and_split_charts.py
│   └── generate_pipeline_diagram_redesign.py
│
└── presentation/                      # [Gitignored] Presentation builder scripts
    └── build_presentation_pptx.py
```

---

## 🛠️ Pipeline Scripts & Usage

### 1. `extract_and_crop_dmd.py` — Video Ingestion & Spatial Cropping
Discovers all `rgb_face` videos across DMD subsets (`distraction`, `gaze`, `drowsiness`), uniformly samples frames at 1 FPS, crops them to the canonical $640 \times 640$ driver-face window (`x: 272, y: 71, w: 640, h: 640`), and runs automated Laplacian variance blur/black-frame checks.

```bash
# Run full extraction + cropping + quality verification
python scripts/extract_and_crop_dmd.py

# Custom path or multi-processing parameters
python scripts/extract_and_crop_dmd.py --dmd-dir dataset/DMD --out-cropped dataset/images --sample-fps 1.0 --workers 6

# Quality & sharpness verification only
python scripts/extract_and_crop_dmd.py --verify-only
```

---

### 2. `assemble_master_coco.py` — Master Ground Truth Assembly
Reads raw Label Studio annotation export tasks, standardizes category IDs and class names against the frozen 4-cue ontology, and compiles the master COCO ground-truth file at [`dataset/annotations.json`](../dataset/annotations.json).

```bash
# Assemble and validate master annotations
python scripts/assemble_master_coco.py
```

---

### 3. `split_annotations_per_subject.py` — Per-Subject Annotation Partitioning
Partitions [`dataset/annotations.json`](../dataset/annotations.json) into 14 distinct per-subject directories (`dataset/annotations_per_subject/subject_01/` ... `subject_14/`), producing isolated COCO JSONs and task lists for modular subject-level tracking.

```bash
# Partition master annotations per subject
python scripts/split_annotations_per_subject.py
```

---

### 4. `balance_splits.py` — Subject-Disjoint Partition Optimizer
Evaluates all $\binom{14}{8} \times \binom{6}{3} = 60{,}060$ possible 8/3/3 subject partitions to find the globally optimal split that preserves exact class balance, subject disjointness ($S_{\text{train}} \cap S_{\text{val}} = \emptyset$, etc.), and matching target frame and cue distributions (57.8% Train, 21.8% Val, 20.4% Test; $\le 5.48\%$ relative divergence).

```bash
# Run exhaustive split balance search and verify dataset/splits.json
python scripts/balance_splits.py
```

---

### 5. `create_shuffled_annotations.py` — Shuffled Split Hierarchy Generator
Duplicates per-subject annotations and reorganizes them into [`dataset/annotations_per_subject_shuffled/`](../dataset/annotations_per_subject_shuffled/) (`Training/`, `Validation/`, `Test/`). Applies deterministic pseudo-random shuffling (seed 13) strictly to the 8 training subjects while keeping validation and test splits in sequential order.

```bash
# Generate shuffled per-subject dataset hierarchy
python scripts/create_shuffled_annotations.py
```

---

### 6. `convert_coco_to_yolo.py` — COCO to YOLO Label Conversion
Converts [`dataset/annotations.json`](../dataset/annotations.json) into YOLO format `.txt` label files under [`dataset/labels/`](../dataset/labels/) matching the 0-indexed ontology (`yawning: 0, hand_over_mouth: 1, drinking: 2, phone_use: 3`). Creates empty label files for negative background frames and generates `dataset/yolo/train.txt`, `val.txt`, `test.txt` and `dataset/yolo/dms_eval.yaml`.

```bash
# Convert master COCO annotations to YOLO label hierarchy & config
python scripts/convert_coco_to_yolo.py
```

---

### 7. `prepare_dfine_coco.py` — D-FINE-N / DETR COCO Split Partitioning
Splits [`dataset/annotations.json`](../dataset/annotations.json) into standalone COCO JSON instances per split (`dataset/coco/instances_train.json`, `instances_val.json`, `instances_test.json`) and writes the D-FINE configuration at `dataset/coco/dfine_dataset.yml`.

```bash
# Generate partitioned COCO JSON splits for D-FINE-N
python scripts/prepare_dfine_coco.py
```

---

### 8. `train_yolo.py` — YOLO Training Engine with Gradient Accumulation
Configures Ultralytics YOLO training with physical batch size 8, gradient accumulation over 4 steps (effective nominal batch size 32), mixed-precision FP16, and CUDA VRAM tracking on NVIDIA RTX 4060 hardware.

```bash
# Sanity check run (2 epochs on YOLO11n)
python scripts/train_yolo.py --epochs 2 --model weights/pretrained/yolo11n.pt --batch 8 --accumulate 4 --device 0

# Full benchmark training run (220 epochs)
python scripts/train_yolo.py --epochs 220 --model weights/pretrained/yolo11n.pt --batch 8 --accumulate 4 --device 0
```

---

### 9. `evaluate_benchmark.py` — Standardized Evaluation Harness & Profiler
Runs the frozen DMS-Eval evaluation protocol: performs validation-only confidence threshold grid sweep ($\tau \in [0.01, 0.99]$) to find $\tau^*$ maximizing micro-averaged $F_1$, executes single-pass evaluation on the unseen test split, and profiles hardware-synchronized batch-1 CUDA-event latency ($p50/p95/p99$), sustained FPS, and peak VRAM.

```bash
# Full validation calibration and single-pass test evaluation
python scripts/evaluate_benchmark.py --weights runs/train/yolo11n_dms/weights/best.pt --config configs/yolo/dms_eval.yaml --device 0

# Fast test split evaluation with fixed confidence threshold
python scripts/evaluate_benchmark.py --weights runs/train/yolo11n_dms/weights/best.pt --split test --threshold 0.45 --device 0
```

---

## 📊 Visualization & Presentation Builders

### `scripts/charts/` (Publication Figures)
- **`generate_distribution_charts.py`**: Generates high-resolution class frequency, frame retention, and subject distribution charts for the manuscript.
- **`generate_pipeline_and_split_charts.py`**: Generates dataset split balance comparisons and flow diagrams.
- **`generate_pipeline_diagram_redesign.py`**: Generates the authoritative 6-module system architecture diagram saved to `assets/diagrams/dms_eval_pipeline.png` and `manuscript/figures/dms_eval_pipeline.png`.

### `scripts/presentation/` (Slide Decks)
- **`build_presentation_pptx.py`**: Compiles the 16-slide 16:9 widescreen PowerPoint presentation (`docs/presentation/DMS-Eval-Presentation-15min.pptx` and `docs/presentation/presentation.pptx`) with embedded figures, design palette tokens, and speaker notes.

```bash
# Build presentation slide decks
uv run --with python-pptx python scripts/presentation/build_presentation_pptx.py
```
