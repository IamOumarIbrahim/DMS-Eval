# DMS-Eval Shuffled Per-Subject Dataset Annotations

[← Back to the DMS-Eval Landing Page](../../README.md)

This directory contains per-subject ground-truth annotations partitioned into the authoritative **8/3/3 subject-disjoint splits** (`Training/`, `Validation/`, `Test/`), with pseudo-random frame sequence shuffling applied strictly to the **Training split** using fixed seed `13`.

---

## 📂 Directory Layout

```text
dataset/annotations_per_subject_shuffled/
├── README.md                                 # Dataset partition documentation (this file)
│
├── Training/                                 # 8 Training Subjects (Shuffled frame order, Seed 13)
│   ├── subject_01/
│   │   ├── coco_annotations.json             # Shuffled COCO format annotations
│   │   └── raw_annotations.json              # Shuffled Label Studio raw task records
│   ├── subject_04/
│   ├── subject_06/
│   ├── subject_07/
│   ├── subject_08/
│   ├── subject_09/
│   ├── subject_13/
│   └── subject_14/
│
├── Validation/                               # 3 Validation Subjects (Unshuffled, original sequence)
│   ├── subject_02/
│   │   ├── coco_annotations.json             # Sequential COCO format annotations
│   │   └── raw_annotations.json              # Sequential Label Studio raw task records
│   ├── subject_03/
│   └── subject_11/
│
└── Test/                                     # 3 Test Subjects (Unshuffled, original sequence)
    ├── subject_05/
    │   ├── coco_annotations.json             # Sequential COCO format annotations
    │   └── raw_annotations.json              # Sequential Label Studio raw task records
    ├── subject_10/
    └── subject_12/
```

---

## 📊 Partition Statistics & Ground Truth Composition

<div align="center">

| Partition | Subjects ($N$) | Subject IDs | Frames ($N$) | Bounding Boxes ($N$) | Category Breakdown (Phone / Drink / Yawn / Hand) | Shuffling Policy |
| :--- | :---: | :--- | :---: | :---: | :---: | :---: |
| **`Training`** | 8 | `01`, `04`, `06`, `07`, `08`, `09`, `13`, `14` | **9,087** | **1,748** | 1,417 / 154 / 94 / 83 | 🔀 **Shuffled (Seed 13)** |
| **`Validation`** | 3 | `02`, `03`, `11` | **3,423** | **639** | 523 / 54 / 32 / 30 | ⏸️ **Unshuffled (Sequential)** |
| **`Test`** | 3 | `05`, `10`, `12` | **3,213** | **614** | 497 / 56 / 33 / 28 | ⏸️ **Unshuffled (Sequential)** |
| **Total** | **14** | All subjects | **15,723** | **3,001** | **2,437 / 264 / 159 / 141** | — |

</div>

---

## 🔀 Shuffling Methodology & Parity Controls

1. **Training Split Shuffling:**
   - Evaluated models trained on single-frame static inputs benefit from non-contiguous batch sample order to prevent correlation across adjacent 1 FPS video frames.
   - For all 8 training subjects, `images` and `annotations` arrays in `coco_annotations.json` as well as task records in `raw_annotations.json` are deterministically permuted using Python `random.Random(13 + subject_id)`.
2. **Validation & Test Sequence Preservation:**
   - `Validation/` and `Test/` splits remain in exact chronological/index order to support temporal error analysis and reproducible metric computation.
3. **Data Integrity:**
   - 100% of all 15,723 sampled frames and 3,001 bounding box annotations are preserved with exact coordinate and category ID fidelity.

---

## 🛠️ Reproduction

To re-generate or verify this shuffled partition hierarchy from the baseline per-subject annotations:

```bash
uv run python scripts/create_shuffled_annotations.py
```
