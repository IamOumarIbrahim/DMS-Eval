# DMS-Eval Dataset Processing & Extraction Scripts

This folder contains the implemented preprocessing pipeline used to prepare the Driver Monitoring Dataset (DMD) for model evaluation and benchmarking.

> **Status:** The frame-extraction pipeline is implemented under `scripts/`. Generated images under `dataset/images/` are local dataset artifacts and are not intended to be committed to Git.

---

## 1. `extract_and_crop_dmd.py`

An end-to-end multi-processed Python CLI pipeline that extracts, crops, and verifies frames from DMD videos.

### Pipeline Stages:
1. **1 FPS Frame Sampling**:
   - Discovers all 1280x720 `rgb_face` videos across `distraction`, `gaze`, and `di21-dmd-dataset-drowsiness`.
   - Applies the frozen intent of sampling 1 frame every 1 second.
   - The exact implementation mapping to source frames at approximately 29.76 FPS remains unresolved; no timestamp, rounding, accumulated-time, floor/ceiling, or other mapping rule is frozen.
   - Outputs full-resolution (1280x720) frames to `dataset/DMD/Images/` using standardized naming:
     ```
     <category>_<group>_<subject>_<session>_<framenumber:04d>.jpg
     ```
2. **640×640 Face Region Cropping**:
   - Crops each frame to the standardized driver-face bounding box:
     - `x = 272`, `y = 71`, `width = 640`, `height = 640`
     - Corners: `(272, 71)` to `(912, 711)`
   - Uses no resizing, padding, letterboxing, or stretching.
   - Saves cropped frames under `dataset/images/subject_<ID>/video_<ID>/`.
   - Final cropped filenames use the sequential sampled-frame index within each video:
     ```
     subject_<SUBJECT_ID>_video_<VIDEO_ID>_frame_<SAMPLED_FRAME_INDEX>.jpg
     ```
   - Numbering begins at `0001`, is zero-padded to four digits, and restarts for each video.
   - The sampled-frame index is not claimed to be the original MP4 source-frame index.
3. **Automated Quality Verification**:
   - Detects any pure black or corrupt frames (`max_pixel == 0`).
   - Measures Laplacian Variance ($\sigma^2(\nabla^2 I)$) sharpness across all frames.

---

### Requirements

```bash
pip install opencv-python numpy
```

---

### Usage Examples

```bash
# Run full pipeline (extraction + cropping + verification)
python scripts/extract_and_crop_dmd.py

# Custom parameters example
python scripts/extract_and_crop_dmd.py --dmd-dir dataset/DMD --out-cropped dataset/images --sample-fps 1.0 --crop-box 272 71 640 640 --workers 6

# Run only cropping on existing extracted frames
python scripts/extract_and_crop_dmd.py --skip-extract

# Run quality & sharpness verification only
python scripts/extract_and_crop_dmd.py --verify-only
```

---

### Output Directory Structure:

```
dataset/
├── images/                                  # 640x640 cropped dataset; not committed to Git
│   ├── subject_01/
│   │   ├── video_01/
│   │   │   ├── subject_01_video_01_frame_0001.jpg
│   │   │   ├── subject_01_video_01_frame_0002.jpg
│   │   │   ├── subject_01_video_01_frame_0003.jpg
│   │   │   └── ...
│   │   ├── video_02/
│   │   └── ...
│   ├── subject_02/
│   │   └── ...
│   └── ...
└── DMD/
    ├── Images/                              # 1280x720 Raw Extracted Frames
    ├── distraction/                         # Original Videos & Annotations
    ├── gaze/
    └── di21-dmd-dataset-drowsiness/
```

---

## ⚠️ Resolve Later Checklist

<div align="center">

| Status | Item / Open Decision | Protocol Role | Target Resolution Milestone |
| :---: | :--- | :--- | :--- |
| [ ] | **Validation Confidence Thresholds ($\tau^*$)** | Numerical threshold values $(\tau_{\text{YOLO11n}}, \tau_{\text{D-FINE-N}}, \tau_{\text{YOLO26n}})$ selected via validation $F_1$ sweep | [Module 4.3](../docs/execution-checklist.md#module-4-shared-evaluation-harness--validation-model-selection) |
| [ ] | **Host Environment Manifest Pinning** | Exact pinned versions for CUDA, cuDNN, PyTorch, Ultralytics commit, D-FINE commit, and THOP | [Module 3.1](../docs/execution-checklist.md#module-3-environment-configuration--controlled-model-training) |
| [ ] | **Custom / Unsupported Operator Profiling** | Local operator handler audit for THOP GFLOPs computation ($1 \times 3 \times 640 \times 640$) | [Module 5.2](../docs/execution-checklist.md#module-5-computational-complexity--footprint-profiling) |
| [ ] | **Non-Integer FPS Frame Mapping** | Exact frame-index rounding rule for source video extraction at non-integer framerates | [Module 1.1](../docs/execution-checklist.md#module-1-data-pipeline--annotation-integrity) |
| [ ] | **Checkpoint Storage Measurement** | Uniform disk footprint measurement protocol (MB) for final selected model weights | [Module 5.3](../docs/execution-checklist.md#module-5-computational-complexity--footprint-profiling) |

</div>
