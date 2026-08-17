<#
.SYNOPSIS
    Launches Label Studio isolated within the DMS-Eval project workspace.
.DESCRIPTION
    Activates the local virtual environment in tools/label-studio/.venv, sets the data
    directory to tools/label-studio/data, enables local file serving for DMS-Eval dataset,
    and starts the Label Studio server on port 8080.
#>

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$RepoRoot = Split-Path -Parent (Split-Path -Parent $ScriptDir)

$LabelStudioExe = Join-Path $ScriptDir ".venv\Scripts\label-studio.exe"
$DataDir = Join-Path $ScriptDir "data"
$MediaDir = Join-Path $ScriptDir "media"

# Ensure data and media directories exist
if (-not (Test-Path $DataDir)) { New-Item -ItemType Directory -Path $DataDir -Force | Out-Null }
if (-not (Test-Path $MediaDir)) { New-Item -ItemType Directory -Path $MediaDir -Force | Out-Null }

# Set environment variables for local isolation and local file serving
$env:LABEL_STUDIO_BASE_DATA_DIR = $DataDir
$env:LABEL_STUDIO_LOCAL_FILES_SERVING_ENABLED = "true"
$env:LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT = $RepoRoot

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host " Starting Label Studio for DMS-Eval      " -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host " Repo Root: $RepoRoot"
Write-Host " Data Dir:  $DataDir"
Write-Host " URL:       http://localhost:8080"
Write-Host ""

# Run Label Studio using the virtual environment executable
& $LabelStudioExe start --port 8080
