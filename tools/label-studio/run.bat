@echo off
setlocal

set SCRIPT_DIR=%~dp0
for %%I in ("%SCRIPT_DIR%..\..") do set REPO_ROOT=%%~fI

set LABEL_STUDIO_EXE=%SCRIPT_DIR%.venv\Scripts\label-studio.exe
set DATA_DIR=%SCRIPT_DIR%data
set MEDIA_DIR=%SCRIPT_DIR%media

if not exist "%DATA_DIR%" mkdir "%DATA_DIR%"
if not exist "%MEDIA_DIR%" mkdir "%MEDIA_DIR%"

set LABEL_STUDIO_BASE_DATA_DIR=%DATA_DIR%
set LABEL_STUDIO_LOCAL_FILES_SERVING_ENABLED=true
set LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT=%REPO_ROOT%

echo =========================================
echo  Starting Label Studio for DMS-Eval      
echo =========================================
echo  Repo Root: %REPO_ROOT%
echo  Data Dir:  %DATA_DIR%
echo  URL:       http://localhost:8080
echo.

"%LABEL_STUDIO_EXE%" start --port 8080
