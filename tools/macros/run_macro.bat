@echo off
title DMS-Eval Auto-Submit Macro (Scroll Wheel Toggle)
cd /d "%~dp0\..\.."

if exist "tools\label-studio\.venv\Scripts\python.exe" (
    "tools\label-studio\.venv\Scripts\python.exe" "tools\macros\scroll_wheel_macro.py"
) else (
    python "tools\macros\scroll_wheel_macro.py"
)

pause
