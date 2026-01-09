@echo off
REM ========================================================================
REM Car Management System - Application Launcher with Inference Support
REM ========================================================================
REM
REM This script sets up the inference environment and starts the application
REM with full end-to-end inference capabilities:
REM
REM 1. Creates/verifies the inference virtual environment (car_inference_env)
REM 2. Installs PyTorch (GPU if NVIDIA detected, otherwise CPU)
REM 3. Installs all ML inference dependencies (transformers, peft, accelerate, etc.)
REM 4. Starts the backend server (port 5000) with inference model configured
REM 5. Starts the frontend server (port 8000)
REM 6. Opens the browser to the frontend
REM
REM Requirements:
REM - Python 3.10+ installed and in PATH
REM - Model adapter directory at car-models/qwen25_3b_base_MAPPED_v2 (or update MODEL_DIR)
REM - requirements.inference.txt in car-back-end directory
REM
REM This is the RECOMMENDED way to start the application with inference.
REM See README-START.md for detailed documentation.
REM ========================================================================

setlocal enabledelayedexpansion

echo ========================================
echo Car Management System - Starting...
echo Creating Inference Virtual Environment
echo ========================================
echo.

set "SCRIPT_DIR=%~dp0"
set BACKEND_DIR=%SCRIPT_DIR%car-back-end
set FRONTEND_DIR=%SCRIPT_DIR%car-front-end
set VENV_DIR=%BACKEND_DIR%\car_inference_env
set PYTHON_EXE=%VENV_DIR%\Scripts\python.exe
set PIP_EXE=%VENV_DIR%\Scripts\pip.exe
set REQUIREMENTS_FILE=%BACKEND_DIR%\requirements.inference.txt

REM Model configuration
set "HF_BASE_MODEL_ID=Qwen/Qwen2.5-3B"
set MODEL_DIR=%SCRIPT_DIR%car-models\qwen25_3b_base_MAPPED_v2
set LORA_ADAPTER_PATH=%MODEL_DIR%
set HF_TOKEN=
set HF_HOME=%SCRIPT_DIR%hf_cache

echo Backend directory: %BACKEND_DIR%
echo Virtual environment: %VENV_DIR%
echo.

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

if not exist "%REQUIREMENTS_FILE%" (
    echo ERROR: requirements.inference.txt not found at %REQUIREMENTS_FILE%
    pause
    exit /b 1
)

python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

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
    echo.
) else (
    echo Virtual environment already exists.
    echo.
)

echo Upgrading pip...
"%PYTHON_EXE%" -m pip install --upgrade pip --quiet
if errorlevel 1 (
    echo ERROR: Failed to upgrade pip
    pause
    exit /b 1
)
echo Pip upgraded successfully.
echo.

echo Installing PyTorch...
where nvidia-smi >nul 2>&1
if not errorlevel 1 (
    echo NVIDIA GPU detected. Installing CUDA 12.4 PyTorch...
    "%PIP_EXE%" install torch --index-url https://download.pytorch.org/whl/cu124 --quiet
    if errorlevel 1 (
        echo WARNING: CUDA PyTorch install failed. Falling back to CPU PyTorch...
        "%PIP_EXE%" install torch --quiet
        if errorlevel 1 (
            echo ERROR: Failed to install CPU PyTorch
            pause
            exit /b 1
        )
    ) else (
        echo PyTorch with CUDA support installed successfully.
    )
) else (
    echo No NVIDIA GPU detected. Installing CPU PyTorch...
    "%PIP_EXE%" install torch --quiet
    if errorlevel 1 (
        echo ERROR: Failed to install CPU PyTorch
        pause
        exit /b 1
    ) else (
        echo CPU PyTorch installed successfully.
    )
)
echo.

echo Checking installed packages...
"%PIP_EXE%" show transformers >nul 2>&1
if errorlevel 1 (
    echo Installing inference requirements from %REQUIREMENTS_FILE%...
    "%PIP_EXE%" install -r "%REQUIREMENTS_FILE%" --quiet
    if errorlevel 1 (
        echo ERROR: Failed to install requirements
        pause
        exit /b 1
    )
    echo Requirements installed successfully.
) else (
    echo Requirements already installed. Skipping installation.
)
echo.

echo ========================================
echo Virtual environment setup complete!
echo ========================================
echo.

REM Verify venv exists before launching
if not exist "%PYTHON_EXE%" (
    echo ERROR: Python executable not found at %PYTHON_EXE%
    echo Virtual environment may not be properly set up.
    pause
    exit /b 1
)

REM Check if model directory exists
if not exist "%MODEL_DIR%" (
    echo WARNING: Model adapter directory not found at %MODEL_DIR%
    echo The application may fail to start without the model.
    echo.
)

REM Check if app.py exists
if not exist "%BACKEND_DIR%\app.py" (
    echo ERROR: app.py not found at %BACKEND_DIR%\app.py
    pause
    exit /b 1
)

echo Starting Backend Server (Port 5000)...
echo Model: %HF_BASE_MODEL_ID%
echo Adapter: %LORA_ADAPTER_PATH%
echo.
echo Starting in a new window - you can minimize it if needed.
start "Car Backend - Port 5000" cmd /k "cd /d %BACKEND_DIR% && set \"HF_BASE_MODEL_ID=%HF_BASE_MODEL_ID%\" && set \"LORA_ADAPTER_PATH=%LORA_ADAPTER_PATH%\" && set \"HF_TOKEN=%HF_TOKEN%\" && set \"HF_HOME=%HF_HOME%\" && %PYTHON_EXE% app.py"

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
echo Backend: http://localhost:5000
echo Frontend: http://localhost:8000
echo.
echo Both servers are running in separate windows.
echo Close those windows to stop the servers.
echo.
pause
