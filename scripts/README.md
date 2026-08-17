# DMS-Eval Dataset Processing & Extraction Scripts

This folder contains the complete, reproducible preprocessing pipelines used to prepare the Driver Monitoring Dataset (DMD) for model evaluation and benchmarking.

---

## 1. `extract_and_crop_dmd.py`

An end-to-end multi-processed Python CLI pipeline that extracts, crops, and verifies frames from DMD videos.

### Pipeline Stages:
1. **1 FPS Frame Sampling**:
   - Discovers all 1280x720 `rgb_face` videos across `distraction`, `gaze`, and `di21-dmd-dataset-drowsiness`.
   - Samples 1 frame every 1 second (1 fps) sequentially with zero-drop decoding.
   - Outputs full-resolution (1280x720) frames to `dataset/DMD/Images/` using standardized naming:
     ```
     <category>_<group>_<subject>_<session>_<framenumber:04d>.jpg
     ```
2. **640×640 Face Region Cropping**:
   - Crops each frame to the standardized driver-face bounding box:
     - `x = 272`, `y = 71`, `width = 640`, `height = 640`
     - Corners: `(272, 71)` to `(912, 711)`
   - Saves cropped frames to `dataset/images/`.
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
├── images/                                  # 640x640 Cropped Dataset
│   ├── distraction/
│   │   └── gA/1/s1/
│   │       ├── distraction_gA_1_s1_0001.jpg
│   │       └── ...
│   ├── gaze/
│   │   └── gA/1/s6/
│   │       ├── gaze_gA_1_s6_0001.jpg
│   │       └── ...
│   └── di21-dmd-dataset-drowsiness/
│       └── gA/1/s5/
│           ├── drowsiness_gA_1_s5_0001.jpg
│           └── ...
└── DMD/
    ├── Images/                              # 1280x720 Raw Extracted Frames
    ├── distraction/                         # Original Videos & Annotations
    ├── gaze/
    └── di21-dmd-dataset-drowsiness/
```
