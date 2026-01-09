@echo off
REM Car Management System - Application Launcher with Inference Environment
REM This script sets up the inference venv and starts both backend and frontend servers.

setlocal enabledelayedexpansion

echo ========================================
echo Car Management System - Starting...
echo ========================================
echo.

REM Parse command line arguments
set REINSTALL=0
if not "%~1"=="" if "%~1"=="--reinstall" set REINSTALL=1

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"
set BACKEND_DIR=%SCRIPT_DIR%car-back-end
set FRONTEND_DIR=%SCRIPT_DIR%car-front-end
set VENV_DIR=%BACKEND_DIR%\car_inference_env
set PYTHON_EXE=%VENV_DIR%\Scripts\python.exe
set PIP_EXE=%VENV_DIR%\Scripts\pip.exe

REM -----------------------------
REM Inference Model Configuration
REM -----------------------------
REM IMPORTANT: Update HF_BASE_MODEL_ID to match the exact base model you trained against.
REM Adapter path is assumed to be inside the repo under car-models/adapter_folder_name
set "HF_BASE_MODEL_ID=Qwen/Qwen2.5-3B"
set MODEL_DIR=%SCRIPT_DIR%car-models\qwen25_3b_base_MAPPED_v2
set LORA_ADAPTER_PATH=%MODEL_DIR%

REM Optional inference controls (uncomment if you want to override defaults)
REM set INFERENCE_DEVICE=auto
REM set MAX_NEW_TOKENS=512
REM set TEMPERATURE=0.0
REM set TOP_P=1.0
REM set END_JSON_TOKEN=END_JSON
REM set HF_TOKEN=your_token_if_needed
REM set HF_HOME=%SCRIPT_DIR%hf_cache

REM Check if directories exist
if not exist "%BACKEND_DIR%" (
    echo ERROR: Backend directory not found at %BACKEND_DIR%
    pause
    exit /b 1
)

if not exist "%FRONTEND_DIR%" (
    echo ERROR: Frontend directory not found at %FRONTEND_DIR%
    pause
    exit /b 1
)

if not exist "%MODEL_DIR%" (
    echo ERROR: Model adapter directory not found at %MODEL_DIR%
    echo Ensure you copied your adapter folder into: %SCRIPT_DIR%car-models
    pause
    exit /b 1
)

if not exist "%BACKEND_DIR%\requirements.inference.txt" (
    echo ERROR: requirements.inference.txt not found at %BACKEND_DIR%\requirements.inference.txt
    pause
    exit /b 1
)

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python (3.10+ recommended for modern ML stacks) and try again.
    pause
    exit /b 1
)

echo Setting up inference environment...
echo.

REM Recreate venv if --reinstall is provided
if "%REINSTALL%"=="1" (
    echo --reinstall flag detected. Recreating virtual environment...
    if exist "%VENV_DIR%" (
        echo Removing existing virtual environment...
        rmdir /s /q "%VENV_DIR%"
        if errorlevel 1 (
            echo ERROR: Failed to remove existing virtual environment
            echo Please close any processes using the venv and try again.
            pause
            exit /b 1
        )
    )
)

REM Create venv if it doesn't exist
if not exist "%VENV_DIR%" (
    echo Creating virtual environment: car_inference_env...
    cd /d "%BACKEND_DIR%"
    python -m venv car_inference_env
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully.
) else (
    echo Virtual environment already exists.
)

echo.
echo Installing / updating packages (idempotent)...
echo.

REM Upgrade pip
echo Upgrading pip...
"%PYTHON_EXE%" -m pip install --upgrade pip --quiet
if errorlevel 1 (
    echo ERROR: Failed to upgrade pip
    pause
    exit /b 1
)

REM Install torch with GPU support if possible; otherwise fallback to CPU
REM NOTE: torch is intentionally NOT in requirements.inference.txt to avoid platform-specific wheel issues.
echo Installing PyTorch...
where nvidia-smi >nul 2>&1
if not errorlevel 1 (
    echo NVIDIA GPU detected. Attempting CUDA 12.4 PyTorch...
    "%PIP_EXE%" install torch --index-url https://download.pytorch.org/whl/cu124
    if errorlevel 1 (
        echo WARNING: CUDA PyTorch install failed. Falling back to CPU PyTorch...
        "%PIP_EXE%" install torch
        if errorlevel 1 (
            echo ERROR: Failed to install CPU PyTorch
            pause
            exit /b 1
        )
    )
) else (
    echo No NVIDIA GPU detected. Installing CPU PyTorch...
    "%PIP_EXE%" install torch
    if errorlevel 1 (
        echo ERROR: Failed to install CPU PyTorch
        pause
        exit /b 1
    )
)

REM Install other inference requirements (pip will skip already-satisfied packages)
echo Installing inference requirements...
"%PIP_EXE%" install -r "%BACKEND_DIR%\requirements.inference.txt"
if errorlevel 1 (
    echo ERROR: Failed to install inference requirements
    pause
    exit /b 1
)

REM Quick import check to catch obvious env issues early
echo Verifying imports...
"%PYTHON_EXE%" -c "import torch; import transformers; import peft; import accelerate; import safetensors; import flask; import orjson" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Import verification failed. Check pip output above for details.
    pause
    exit /b 1
)

echo.
echo Starting Backend Server (Port 5000)...
echo Starting in a new window - you can minimize it if needed.

start "Car Backend - Port 5000" cmd /k ^
"cd /d %BACKEND_DIR% && ^
set "HF_BASE_MODEL_ID=%HF_BASE_MODEL_ID%" && ^
set "LORA_ADAPTER_PATH=%LORA_ADAPTER_PATH%" && ^
set "HF_TOKEN=%HF_TOKEN%" && ^
set "HF_HOME=%SCRIPT_DIR%hf_cache" && ^
%PYTHON_EXE% app.py"

REM Wait for backend to start (model load may take longer on first run)
echo Waiting for backend to initialize (this may take 10-30 seconds on first run)...
timeout /t 10 /nobreak >nul

echo Starting Frontend Server (Port 8000)...
echo Starting in a new window - you can minimize it if needed.
start "Car Frontend - Port 8000" cmd /k "cd /d %FRONTEND_DIR% && %PYTHON_EXE% -m http.server 8000"

REM Wait for frontend to start
echo Waiting for frontend to initialize...
timeout /t 5 /nobreak >nul

REM Open browser to frontend
echo.
echo Opening browser to http://localhost:8000...
echo If the page doesn't load, wait a few more seconds and refresh.
start http://localhost:8000

echo.
echo ========================================
echo Application is starting!
echo ========================================
echo.
echo Backend:  http://localhost:5000
echo Frontend: http://localhost:8000 (opened in browser)
echo.
echo Virtual Environment: %VENV_DIR%
echo Adapter Path: %LORA_ADAPTER_PATH%
echo Base Model: %HF_BASE_MODEL_ID%
echo.
echo Two windows have opened - one for each server.
echo You can minimize them or keep them open to see logs.
echo Close those windows to stop the servers.
echo.
echo Press any key to exit this launcher...
pause >nul
