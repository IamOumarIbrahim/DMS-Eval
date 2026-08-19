# Label Studio - DMS-Eval

This directory contains the project-isolated setup and configuration for **Label Studio**, used for data annotation and quality control across the DMS-Eval dataset.

---

## Directory Structure

```
tools/label-studio/
├── .venv/               # Isolated virtual environment (Git-ignored)
├── data/                # Label Studio SQLite DB & project configs (Git-ignored)
├── media/               # Label Studio uploaded/cached media (Git-ignored)
├── config/              # Tracked Label Studio XML labeling templates
│   └── dms_labeling_config.xml
├── start.ps1            # PowerShell launcher script
├── run.bat              # Batch/CMD launcher script
└── README.md            # Setup and usage guide (this file)
```

---

## Quick Start

### Option 1: Using the launcher scripts (Recommended)

**PowerShell:**
```powershell
.\tools\label-studio\start.ps1
```

**Command Prompt / Windows Terminal:**
```cmd
tools\label-studio\run.bat
```

The launcher will:
1. Activate the local virtual environment (`tools/label-studio/.venv`).
2. Set the data storage directory to `tools/label-studio/data`.
3. Enable local file serving for importing images directly from the `dataset/` directory.
4. Launch Label Studio on `http://localhost:8080`.

---

### Option 2: Manual Activation & Launch

**PowerShell:**
```powershell
# 1. Activate the virtual environment
.\tools\label-studio\.venv\Scripts\Activate.ps1

# 2. Set environment variables to keep data inside tools/label-studio
$env:LABEL_STUDIO_BASE_DATA_DIR = "$PWD\tools\label-studio\data"
$env:LABEL_STUDIO_LOCAL_FILES_SERVING_ENABLED = "true"
$env:LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT = "$PWD"

# 3. Start Label Studio
label-studio start --port 8080
```

**Command Prompt:**
```cmd
:: 1. Activate
tools\label-studio\.venv\Scripts\activate.bat

:: 2. Set environment variables
set LABEL_STUDIO_BASE_DATA_DIR=%CD%\tools\label-studio\data
set LABEL_STUDIO_LOCAL_FILES_SERVING_ENABLED=true
set LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT=%CD%

:: 3. Start
label-studio start --port 8080
```

---

## Importing Local Dataset Images

Because `LABEL_STUDIO_LOCAL_FILES_SERVING_ENABLED` is enabled:
1. In your Label Studio project, go to **Settings > Cloud Storage > Add Source Storage**.
2. Set **Storage Type** to **Local files**.
3. Set **Absolute local path** to:
   - `c:/Dev/repos/Public repos/DMS-Eval/dataset/images` (or relative path if applicable).
4. Click **Treat every bucket object as a source file** and **Save**.
5. Click **Sync Storage** to load the dataset frames directly without duplicate copying.

---

## Labeling Templates (`config/`)

Tracked XML configuration templates for Label Studio labeling interfaces are located in [`config/`](config/). You can paste the contents of these XML files into **Project Settings > Labeling Interface > Code**.

---

## ⚠️ Resolve Later Checklist

<div align="center">

| Status | Item / Open Decision | Protocol Role | Target Resolution Milestone |
| :---: | :--- | :--- | :--- |
| [ ] | **Validation Confidence Thresholds ($\tau^*$)** | Numerical threshold values $(\tau_{\text{YOLO11n}}, \tau_{\text{D-FINE-N}}, \tau_{\text{YOLO26n}})$ selected via validation $F_1$ sweep | [Module 4.3](../../docs/execution-checklist.md#module-4-shared-evaluation-harness--validation-model-selection) |
| [ ] | **Host Environment Manifest Pinning** | Exact pinned versions for CUDA, cuDNN, PyTorch, Ultralytics commit, D-FINE commit, and THOP | [Module 3.1](../../docs/execution-checklist.md#module-3-environment-configuration--controlled-model-training) |
| [ ] | **Custom / Unsupported Operator Profiling** | Local operator handler audit for THOP GFLOPs computation ($1 \times 3 \times 640 \times 640$) | [Module 5.2](../../docs/execution-checklist.md#module-5-computational-complexity--footprint-profiling) |
| [ ] | **Non-Integer FPS Frame Mapping** | Exact frame-index rounding rule for source video extraction at non-integer framerates | [Module 1.1](../../docs/execution-checklist.md#module-1-data-pipeline--annotation-integrity) |
| [ ] | **Checkpoint Storage Measurement** | Uniform disk footprint measurement protocol (MB) for final selected model weights | [Module 5.3](../../docs/execution-checklist.md#module-5-computational-complexity--footprint-profiling) |

</div>
