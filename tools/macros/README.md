# Auto-Submit Macro (Scroll Wheel Toggle)

A lightweight, zero-dependency global background macro designed for fast single-frame data review and negative frame submission in Label Studio.

---

## Behavior & Controls

| Action | Control |
| :--- | :--- |
| **Toggle ON / OFF** | **Click Scroll Wheel** *(Middle Mouse Button)* |
| **Active State (ON)** | Sends `Ctrl + Enter` continuously every **1.0 second** |
| **Inactive State (OFF)** | Pauses immediately and goes idle (consumes ~0% CPU) |
| **Scope** | Works **globally** across all active Windows applications |
| **Audio Feedback** | 🔊 **High Beep (1000 Hz):** Toggled ON<br>🔈 **Low Beep (500 Hz):** Toggled OFF |
| **Exit Macro** | Press `Ctrl + C` in the console window |

---

## How to Run

### Method 1: Double-Click Launcher (Windows)
Double-click [`run_macro.bat`](./run_macro.bat).

### Method 2: Command Line
```powershell
& "tools\label-studio\.venv\Scripts\python.exe" tools/macros/scroll_wheel_macro.py
```
*(or with system Python: `python tools/macros/scroll_wheel_macro.py`)*

---

## Label Studio Usage Workflow
1. Open Label Studio and navigate to your dataset project.
2. Launch the macro in the background.
3. When navigating sequences of negative frames (no warning cues), **click the scroll wheel once** to start auto-advancing through frames every 1.0 second.
4. When you encounter an active warning cue to annotate, **click the scroll wheel again** to instantly pause the macro, draw your bounding box, and resume whenever ready.

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
