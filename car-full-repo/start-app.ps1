# Car Management System - Application Launcher with Inference Environment (PowerShell)
# This script sets up the inference venv and starts both backend and frontend servers

param(
    [switch]$Reinstall
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Car Management System - Starting..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get the directory where this script is located
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendDir = Join-Path $ScriptDir "car-back-end"
$FrontendDir = Join-Path $ScriptDir "car-front-end"
$VenvDir = Join-Path $BackendDir "car_inference_env"
$PythonExe = Join-Path $VenvDir "Scripts\python.exe"
$PipExe = Join-Path $VenvDir "Scripts\pip.exe"

# -----------------------------
# Inference Model Configuration
# -----------------------------
# IMPORTANT: Update HF_BASE_MODEL_ID to match the exact base model you trained against.
# Adapter path is assumed to be inside the repo under \car-models\<adapter_folder_name>
# IMPORTANT: Update HF_BASE_MODEL_ID to match the exact base model you trained against.
# Adapter path is assumed to be inside the repo under \car-models\<adapter_folder_name>
$env:HF_BASE_MODEL_ID = "qwen/qwen2.5-3b"
$ModelDir = Join-Path $ScriptDir "car-models\qwen25_3b_base_MAPPED_v2"
$env:LORA_ADAPTER_PATH = $ModelDir

# Optional inference controls (uncomment if you want to override defaults)
# $env:INFERENCE_DEVICE = "auto"
# $env:MAX_NEW_TOKENS = "512"
# $env:TEMPERATURE = "0.0"
# $env:TOP_P = "1.0"
# $env:END_JSON_TOKEN = "<END_JSON>"
# $env:HF_TOKEN = "your_token_if_needed"

# Check if directories exist
if (-not (Test-Path $BackendDir)) {
    Write-Host "ERROR: Backend directory not found at $BackendDir" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

if (-not (Test-Path $FrontendDir)) {
    Write-Host "ERROR: Frontend directory not found at $FrontendDir" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

if (-not (Test-Path $ModelDir)) {
    Write-Host "ERROR: Model adapter directory not found at $ModelDir" -ForegroundColor Red
    Write-Host "Ensure you copied your adapter folder into: $(Join-Path $ScriptDir 'car-models\')" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

$RequirementsFile = Join-Path $BackendDir "requirements.inference.txt"
if (-not (Test-Path $RequirementsFile)) {
    Write-Host "ERROR: requirements.inference.txt not found at $RequirementsFile" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python (3.10+ recommended for modern ML stacks) and try again." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Setting up inference environment..." -ForegroundColor Yellow
Write-Host ""

# Recreate venv if --Reinstall is provided
if ($Reinstall) {
    Write-Host "--Reinstall flag detected. Recreating virtual environment..." -ForegroundColor Yellow
    if (Test-Path $VenvDir) {
        Write-Host "Removing existing virtual environment..." -ForegroundColor Yellow
        try {
            Remove-Item -Path $VenvDir -Recurse -Force -ErrorAction Stop
            Write-Host "Virtual environment removed." -ForegroundColor Green
        } catch {
            Write-Host "ERROR: Failed to remove existing virtual environment" -ForegroundColor Red
            Write-Host "Please close any processes using the venv and try again." -ForegroundColor Red
            Write-Host $_.Exception.Message -ForegroundColor Red
            Read-Host "Press Enter to exit"
            exit 1
        }
    }
}

# Create venv if it doesn't exist
if (-not (Test-Path $VenvDir)) {
    Write-Host "Creating virtual environment: car_inference_env..." -ForegroundColor Yellow
    try {
        Set-Location $BackendDir
        python -m venv car_inference_env
        if ($LASTEXITCODE -ne 0) {
            throw "venv creation failed"
        }
        Write-Host "Virtual environment created successfully." -ForegroundColor Green
    } catch {
        Write-Host "ERROR: Failed to create virtual environment" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    } finally {
        Set-Location $ScriptDir
    }
} else {
    Write-Host "Virtual environment already exists." -ForegroundColor Green
}

Write-Host ""
Write-Host "Installing / updating packages (idempotent)..." -ForegroundColor Yellow
Write-Host ""

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
try {
    & $PythonExe -m pip install --upgrade pip --quiet
    if ($LASTEXITCODE -ne 0) {
        throw "pip upgrade failed"
    }
} catch {
    Write-Host "ERROR: Failed to upgrade pip" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Install torch with GPU support if possible; otherwise fallback to CPU
# NOTE: torch is intentionally NOT in requirements.inference.txt to avoid platform-specific wheel issues.
Write-Host "Installing PyTorch..." -ForegroundColor Yellow
try {
    $nvidiaSmi = Get-Command nvidia-smi -ErrorAction SilentlyContinue
    if ($nvidiaSmi) {
        Write-Host "NVIDIA GPU detected. Attempting CUDA 12.4 PyTorch..." -ForegroundColor Yellow
        & $PipExe install torch --index-url https://download.pytorch.org/whl/cu124
        if ($LASTEXITCODE -ne 0) {
            Write-Host "WARNING: CUDA PyTorch install failed. Falling back to CPU PyTorch..." -ForegroundColor Yellow
            & $PipExe install torch
            if ($LASTEXITCODE -ne 0) {
                throw "CPU PyTorch installation failed"
            }
        }
    } else {
        Write-Host "No NVIDIA GPU detected. Installing CPU PyTorch..." -ForegroundColor Yellow
        & $PipExe install torch
        if ($LASTEXITCODE -ne 0) {
            throw "CPU PyTorch installation failed"
        }
    }
} catch {
    Write-Host "ERROR: Failed to install PyTorch" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Install other inference requirements (pip will skip already-satisfied packages)
Write-Host "Installing inference requirements..." -ForegroundColor Yellow
try {
    & $PipExe install -r $RequirementsFile
    if ($LASTEXITCODE -ne 0) {
        throw "requirements installation failed"
    }
} catch {
    Write-Host "ERROR: Failed to install inference requirements" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Quick import check to catch obvious env issues early
Write-Host "Verifying imports..." -ForegroundColor Yellow
try {
    & $PythonExe -c "import torch; import transformers; import peft; import accelerate; import safetensors; import flask; import orjson" 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Import verification failed"
    }
    Write-Host "Import verification successful." -ForegroundColor Green
} catch {
    Write-Host "ERROR: Import verification failed. Check pip output above for details." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Starting Backend Server (Port 5000)..." -ForegroundColor Yellow
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$BackendDir'; `$env:HF_BASE_MODEL_ID='$($env:HF_BASE_MODEL_ID)'; `$env:LORA_ADAPTER_PATH='$($env:LORA_ADAPTER_PATH)'; `$env:HF_TOKEN='$($env:HF_TOKEN)'; `$env:HF_HOME='$(Join-Path $ScriptDir 'hf_cache')'; '$PythonExe' app.py" -WindowStyle Minimized

# Wait for backend to start and check if it's ready (model load may take longer on first run)
Write-Host "Waiting for backend to initialize (this may take 10-30 seconds on first run)..." -ForegroundColor Yellow
$backendReady = $false
$maxAttempts = 15
$attempt = 0

while (-not $backendReady -and $attempt -lt $maxAttempts) {
    Start-Sleep -Seconds 2
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:5000/api/health" -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $backendReady = $true
            Write-Host "Backend is ready!" -ForegroundColor Green
        }
    } catch {
        $attempt++
        if ($attempt -lt $maxAttempts) {
            Write-Host "Backend still starting, waiting... ($attempt/$maxAttempts)" -ForegroundColor Yellow
        }
    }
}

if (-not $backendReady) {
    Write-Host "WARNING: Backend health check timed out, but continuing anyway..." -ForegroundColor Yellow
}

Write-Host "Starting Frontend Server (Port 8000)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$FrontendDir'; '$PythonExe' -m http.server 8000" -WindowStyle Minimized

# Wait for frontend to start and check if it's ready
Write-Host "Waiting for frontend to initialize..." -ForegroundColor Yellow
$frontendReady = $false
$attempt = 0

while (-not $frontendReady -and $attempt -lt $maxAttempts) {
    Start-Sleep -Seconds 2
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000" -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $frontendReady = $true
            Write-Host "Frontend is ready!" -ForegroundColor Green
        }
    } catch {
        $attempt++
        if ($attempt -lt $maxAttempts) {
            Write-Host "Frontend still starting, waiting... ($attempt/$maxAttempts)" -ForegroundColor Yellow
        }
    }
}

# Open browser to frontend
Write-Host ""
Write-Host "Opening browser to http://localhost:8000..." -ForegroundColor Cyan
Start-Process "http://localhost:8000"

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Application is running!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Backend:  http://localhost:5000" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:8000 (opened in browser)" -ForegroundColor Cyan
Write-Host ""
Write-Host "Virtual Environment: $VenvDir" -ForegroundColor Cyan
Write-Host "Adapter Path: $($env:LORA_ADAPTER_PATH)" -ForegroundColor Cyan
Write-Host "Base Model: $($env:HF_BASE_MODEL_ID)" -ForegroundColor Cyan
Write-Host ""
Write-Host "Servers are running in minimized windows." -ForegroundColor Yellow
Write-Host "Close those windows or run stop-app.ps1 to stop the servers." -ForegroundColor Yellow
Write-Host ""
Read-Host "Press Enter to exit this launcher"
