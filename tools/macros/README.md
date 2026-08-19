# Auto-Submit Macro (Scroll Wheel Toggle)

A lightweight, zero-dependency global background macro designed for fast single-frame data review and negative frame submission in Label Studio.

---

## Behavior & Controls

| Action | Control |
| :--- | :--- |
| **Toggle ON / OFF** | **Click Scroll Wheel** *(Middle Mouse Button)* |
| **Active State (ON)** | Sends `Ctrl + Enter` continuously every **2.0 seconds** |
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
3. When navigating sequences of negative frames (no warning cues), **click the scroll wheel once** to start auto-advancing through frames every 2.0 seconds.
4. When you encounter an active warning cue to annotate, **click the scroll wheel again** to instantly pause the macro, draw your bounding box, and resume whenever ready.
