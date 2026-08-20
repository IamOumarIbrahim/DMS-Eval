# DMS-Eval Processing & Execution Scripts

[← Back to the DMS-Eval Landing Page](../README.md)

This directory contains the complete Python workflow suite for **DMS-Eval**, grouped by responsibility so dataset generation, benchmark execution, and publication production remain visibly separate.

---

## 📂 Directory Layout

```text
scripts/
├── README.md                          # Scripts documentation suite (this file)
├── data/
│   ├── extract_and_crop_dmd.py         # [Stage 1] Video extraction and 640×640 cropping
│   ├── assemble_master_coco.py         # [Stage 2] Master COCO assembly
│   ├── split_annotations_per_subject.py# [Stage 3] Per-subject ground truth
│   ├── balance_splits.py               # [Stage 4] Exhaustive 8/3/3 optimizer
│   ├── create_shuffled_annotations.py  # [Stage 5] Deterministic split hierarchy
│   ├── convert_coco_to_yolo.py         # [Stage 6] YOLO labels and manifests
│   └── prepare_dfine_coco.py           # [Stage 7] D-FINE COCO partitions
├── benchmark/
│   ├── preflight.py                    # Read-only full repository gate
│   ├── setup_backends.py               # Pinned backend and weight setup
│   ├── validate_environment.py         # Frozen RTX 4060 environment check
│   ├── validate_dataset.py             # Frozen-data audit
│   ├── validate_backends.py            # Backend and synthetic inference check
│   ├── verify_training_configs.py      # No-training final configuration gate
│   ├── train_yolo.py                   # [Stage 8] Guarded YOLO launchers
│   ├── train_dfine.py                  # [Stage 8] Guarded D-FINE-N launcher
│   ├── evaluate_benchmark.py           # [Stage 9] Protected evaluation lifecycle
│   ├── profile_runtime.py              # Synthetic profiler smoke test
│   └── aggregate_results.py            # Protected result aggregation
├── publication/
│   ├── generate_publication_tables.py  # Aggregate-to-Markdown/LaTeX tables
│   ├── generate_figures.py             # Aggregate-to-publication trade-off figure
│   └── generate_crop_geometry.py       # Reproducible crop schematic
├── maintenance/
│   └── check_links.py                   # Local and optional external link audit
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
python scripts/data/extract_and_crop_dmd.py

# Custom path or multi-processing parameters
python scripts/data/extract_and_crop_dmd.py --dmd-dir dataset/DMD --out-cropped dataset/images --sample-fps 1.0 --workers 6

# Quality & sharpness verification only
python scripts/data/extract_and_crop_dmd.py --verify-only
```

---

### 2. `assemble_master_coco.py` — Master Ground Truth Assembly
Reads raw Label Studio annotation export tasks, standardizes category IDs and class names against the frozen 4-cue ontology, and compiles the master COCO ground-truth file at [`dataset/annotations.json`](../dataset/annotations.json).

```bash
# Assemble and validate master annotations
python scripts/data/assemble_master_coco.py
```

---

### 3. `split_annotations_per_subject.py` — Per-Subject Annotation Partitioning
Partitions [`dataset/annotations.json`](../dataset/annotations.json) into 14 distinct per-subject directories (`dataset/annotations_per_subject/subject_01/` ... `subject_14/`), producing isolated COCO JSONs and task lists for modular subject-level tracking.

```bash
# Partition master annotations per subject
python scripts/data/split_annotations_per_subject.py
```

---

### 4. `balance_splits.py` — Subject-Disjoint Partition Optimizer
Evaluates all $\binom{14}{8} \times \binom{6}{3} = 60{,}060$ possible 8/3/3 subject partitions to find the globally optimal split that preserves exact class balance, subject disjointness ($S_{\text{train}} \cap S_{\text{val}} = \emptyset$, etc.), and matching target frame and cue distributions (57.8% Train, 21.8% Val, 20.4% Test; $\le 5.48\%$ relative divergence).

```bash
# Run exhaustive split balance search and verify dataset/splits.json
python scripts/data/balance_splits.py
```

---

### 5. `create_shuffled_annotations.py` — Shuffled Split Hierarchy Generator
Duplicates per-subject annotations and reorganizes them into [`dataset/annotations_per_subject_shuffled/`](../dataset/annotations_per_subject_shuffled/) (`Training/`, `Validation/`, `Test/`). Applies deterministic pseudo-random shuffling (seed 13) strictly to the 8 training subjects while keeping validation and test splits in sequential order.

```bash
# Generate shuffled per-subject dataset hierarchy
python scripts/data/create_shuffled_annotations.py
```

---

### 6. `convert_coco_to_yolo.py` — COCO to YOLO Label Conversion
Converts [`dataset/annotations.json`](../dataset/annotations.json) into YOLO format `.txt` label files under [`dataset/labels/`](../dataset/labels/) matching the 0-indexed ontology (`yawning: 0, hand_over_mouth: 1, drinking: 2, phone_use: 3`). Creates empty label files for negative background frames and generates `dataset/yolo/train.txt`, `val.txt`, `test.txt` and `dataset/yolo/dms_eval.yaml`.

```bash
# Convert master COCO annotations to YOLO label hierarchy & config
python scripts/data/convert_coco_to_yolo.py
```

---

### 7. `prepare_dfine_coco.py` — D-FINE-N / DETR COCO Split Partitioning
Splits [`dataset/annotations.json`](../dataset/annotations.json) into standalone COCO JSON instances per split (`dataset/coco/instances_train.json`, `instances_val.json`, `instances_test.json`) and writes the D-FINE configuration at `dataset/coco/dfine_dataset.yml`.

```bash
# Generate partitioned COCO JSON splits for D-FINE-N
python scripts/data/prepare_dfine_coco.py
```

---

### 8. `train_yolo.py` — Guarded YOLO Training Launcher
Configures the pinned Ultralytics recipe with physical batch 8, fixed four-step accumulation from the first batch, 220 epochs, an explicitly selected frozen seed from 13/37/73, disabled early stopping, AMP FP16, and the RTX 4060 gate. A pinned trainer patch sample-normalizes incomplete accumulation windows. YOLO retains `optimizer=auto` from Ultralytics 8.4.123 (expected to resolve to MuSGD for these plans).

```bash
# Dry-run frozen plans (no training)
python scripts/benchmark/train_yolo.py --model-id yolo11n --seed 13
python scripts/benchmark/train_yolo.py --model-id yolo26n --seed 13
python scripts/benchmark/train_dfine.py --seed 13

# Authorized full runs require --execute-training
python scripts/benchmark/train_yolo.py --model-id yolo11n --seed 13 --execute-training
```

---

### 9. `evaluate_benchmark.py` — Standardized Evaluation Harness & Profiler
Separates validation export, validation-only checkpoint selection, validation-only confidence calibration, immutable model–seed manifest creation, and one protected test pass per frozen run. Each pass validates the RTX 4060 environment and collects predictions, model-forward timing, tensor-to-final-detections timing (including required postprocessing/NMS), peak VRAM, dual FLOP estimates, standardized FP16 inference-artifact size, and pre-registered qualitative/error candidates without traversing that run's test frames twice.

```bash
# Safe protocol dry-run; never defaults to test
python scripts/benchmark/evaluate_benchmark.py

# List guarded lifecycle commands
python scripts/benchmark/evaluate_benchmark.py --help
```

See [`docs/benchmark-readiness.md`](../docs/benchmark-readiness.md) for the complete future command sequence. No shortcut for repeated test evaluation exists.

### 10. `verify_training_configs.py` — Final Configuration Gate

Verifies the exact seven-item recipe-adaptation list, pinned upstream recipe fingerprints, physical batch and accumulation controls, incomplete-window handling, absence of validation-guided D-FINE reloads, and all nine model–seed dry-run plans. It never starts training or accesses test images.

---

## 📊 Visualization & Presentation Builders

### `scripts/publication/` (Tracked Manuscript Outputs)

- **`generate_crop_geometry.py`**: Rebuilds the fixed source-to-crop schematic in both asset locations.
- **`generate_figures.py`**: Builds the result-driven quality-versus-latency figure after aggregation.
- **`generate_publication_tables.py`**: Converts the aggregate result artifact to Markdown and LaTeX tables.
- **`generate_qualitative_error_analysis.py`**: Builds the fixed-seed contact sheet and three-seed error-count report from hashed protected artifacts without reading the test dataset.

### `scripts/maintenance/` (Repository Integrity)

```bash
# Check every tracked/current Markdown, HTML, and LaTeX file reference.
python scripts/maintenance/check_links.py

# Include unique HTTP(S) targets.
python scripts/maintenance/check_links.py --external
```

### `scripts/charts/` (Legacy/Development Figures)
- **`generate_distribution_charts.py`**: Generates high-resolution class frequency, frame retention, and subject distribution charts for the manuscript.
- **`generate_pipeline_and_split_charts.py`**: Generates dataset split balance comparisons and flow diagrams.
- **`generate_pipeline_diagram_redesign.py`**: Generates the authoritative 6-module system architecture diagram saved to `assets/diagrams/dms_eval_pipeline.png` and `manuscript/figures/dms_eval_pipeline.png`.

### `scripts/presentation/` (Slide Decks)
- **`build_presentation_pptx.py`**: Compiles the 16-slide 16:9 widescreen PowerPoint presentation (`docs/presentation/DMS-Eval-Presentation-15min.pptx` and `docs/presentation/presentation.pptx`) with embedded figures, design palette tokens, and speaker notes.

```bash
# Build presentation slide decks
uv run --with python-pptx python scripts/presentation/build_presentation_pptx.py
```
