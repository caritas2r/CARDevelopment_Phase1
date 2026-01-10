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

REM Check for --noinference flag
set USE_MOCK=0
if not "%~1"=="" if "%~1"=="--noinference" set USE_MOCK=1
if not "%~2"=="" if "%~2"=="--noinference" set USE_MOCK=1

echo ========================================
echo Car Management System - Starting...
if "%USE_MOCK%"=="1" (
    echo MOCK MODE: --noinference flag detected
    echo No inference/database - using mock service
) else (
    echo Creating Inference Virtual Environment
)
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

REM Try to find Python - check both 'python' and 'py' commands
set PYTHON_CMD=
python --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python
    echo Found Python: 
    python --version
) else (
    py --version >nul 2>&1
    if not errorlevel 1 (
        set PYTHON_CMD=py
        echo Found Python: 
        py --version
    ) else (
        echo ERROR: Python is not installed or not in PATH
        echo Please install Python 3.10+ from https://www.python.org/
        echo Make sure to check "Add Python to PATH" during installation
        pause
        exit /b 1
    )
)
echo.

REM Only create venv if not in mock mode (mock mode doesn't need ML dependencies)
if "%USE_MOCK%"=="0" (
    REM Check if venv exists and is valid
    set VENV_VALID=0
    if exist "%VENV_DIR%" (
        if exist "%VENV_DIR%\Scripts\python.exe" (
            set VENV_VALID=1
        )
    )
    
    if "%VENV_VALID%"=="0" (
        REM Clean up broken/incomplete venv if it exists
        if exist "%VENV_DIR%" (
            echo Removing incomplete or broken virtual environment...
            rmdir /s /q "%VENV_DIR%" 2>nul
            timeout /t 1 /nobreak >nul
        )
        
        echo Creating virtual environment: car_inference_env...
        cd /d "%BACKEND_DIR%"
        %PYTHON_CMD% -m venv car_inference_env
        if errorlevel 1 (
            echo ERROR: Failed to create virtual environment
            echo Make sure Python is properly installed and 'venv' module is available
            echo Try running: %PYTHON_CMD% -m venv --help
            pause
            exit /b 1
        )
        
        REM Wait a moment for file system to catch up
        timeout /t 2 /nobreak >nul
        
        REM Verify the venv was created correctly
        if not exist "%VENV_DIR%" (
            echo ERROR: Virtual environment directory was not created
            echo Check if you have write permissions in: %BACKEND_DIR%
            pause
            exit /b 1
        )
        
        if not exist "%VENV_DIR%\Scripts\python.exe" (
            echo ERROR: Virtual environment was created but python.exe not found
            echo Expected at: %VENV_DIR%\Scripts\python.exe
            echo.
            echo Checking what was created:
            if exist "%VENV_DIR%\Scripts" (
                echo Scripts directory exists. Contents:
                dir /b "%VENV_DIR%\Scripts" 2>nul
            ) else (
                echo Scripts directory does not exist!
                echo Venv directory contents:
                dir /b "%VENV_DIR%" 2>nul
            )
            echo.
            echo This may indicate:
            echo   - Python 3.13.2 venv module issue
            echo   - Antivirus blocking file creation
            echo   - Insufficient permissions
            pause
            exit /b 1
        )
        echo Virtual environment created successfully.
        echo Verified Python at: %PYTHON_EXE%
        echo.
    ) else (
        echo Virtual environment already exists and appears valid.
        echo.
    )
) else (
    echo Mock mode: Skipping virtual environment setup (not needed)
    echo Using system Python...
    set PYTHON_EXE=%PYTHON_CMD%
    set PIP_EXE=pip
    echo.
)

REM Only install packages if not in mock mode
if "%USE_MOCK%"=="0" (
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
) else (
    echo Mock mode: Skipping ML package installation (only need Flask and basic packages)
    echo Installing minimal requirements...
    "%PYTHON_EXE%" -m pip install flask flask-cors --quiet
    if errorlevel 1 (
        echo WARNING: Failed to install Flask - you may need to install manually
    )
    echo.
)

echo ========================================
echo Virtual environment setup complete!
echo ========================================
echo.

REM Verify venv exists before launching
if "%USE_MOCK%"=="0" (
    echo Verifying virtual environment...
    echo Expected Python path: %PYTHON_EXE%
    if not exist "%VENV_DIR%" (
        echo ERROR: Virtual environment directory not found: %VENV_DIR%
        echo The venv creation may have failed silently.
        pause
        exit /b 1
    )
    
    if not exist "%VENV_DIR%\Scripts" (
        echo ERROR: Scripts directory not found in venv: %VENV_DIR%\Scripts
        echo The venv structure may be incorrect.
        echo Directory contents:
        dir /b "%VENV_DIR%"
        pause
        exit /b 1
    )
    
    REM Use full path resolution for the check
    cd /d "%BACKEND_DIR%"
    set FULL_PYTHON_EXE=%CD%\car_inference_env\Scripts\python.exe
    if not exist "car_inference_env\Scripts\python.exe" (
        echo ERROR: Python executable not found at: %PYTHON_EXE%
        echo Full path checked: %FULL_PYTHON_EXE%
        echo Current directory: %CD%
        echo Virtual environment directory exists but python.exe is missing.
        echo.
        echo Checking Scripts directory contents:
        if exist "car_inference_env\Scripts" (
            dir /b "car_inference_env\Scripts" | findstr /i "python"
        ) else (
            echo Scripts directory does not exist!
            if exist "car_inference_env" (
                echo Venv directory contents:
                dir /b "car_inference_env"
            )
        )
        echo.
        echo This may indicate:
        echo   1. Venv creation failed partially
        echo   2. Python 3.13.2 has a different venv structure
        echo   3. Antivirus blocked file creation
        echo   4. Path resolution issue
        echo.
        echo Trying to recreate virtual environment...
        if exist "car_inference_env" (
            rmdir /s /q "car_inference_env" 2>nul
            timeout /t 2 /nobreak >nul
        )
        %PYTHON_CMD% -m venv car_inference_env
        if errorlevel 1 (
            echo ERROR: Failed to recreate virtual environment
            pause
            exit /b 1
        )
        timeout /t 2 /nobreak >nul
        if not exist "car_inference_env\Scripts\python.exe" (
            echo ERROR: Python executable still not found after recreation
            echo Please check your Python 3.13.2 installation
            echo Try manually: %PYTHON_CMD% -m venv test_venv
            pause
            exit /b 1
        )
        echo Virtual environment recreated successfully.
        REM Reset PYTHON_EXE to use the verified path
        set PYTHON_EXE=%CD%\car_inference_env\Scripts\python.exe
        set PIP_EXE=%CD%\car_inference_env\Scripts\pip.exe
    ) else (
        echo Virtual environment verified successfully.
        echo Using Python at: %FULL_PYTHON_EXE%
        REM Ensure paths use current directory context
        set PYTHON_EXE=%CD%\car_inference_env\Scripts\python.exe
        set PIP_EXE=%CD%\car_inference_env\Scripts\pip.exe
    )
    echo.
)

REM Check if model directory exists (skip in mock mode)
if "%USE_MOCK%"=="0" (
    if not exist "%MODEL_DIR%" (
        echo WARNING: Model adapter directory not found at %MODEL_DIR%
        echo The application may fail to start without the model.
        echo.
    )
)

REM Check if app.py exists
if not exist "%BACKEND_DIR%\app.py" (
    echo ERROR: app.py not found at %BACKEND_DIR%\app.py
    pause
    exit /b 1
)

echo Starting Backend Server (Port 5000)...
if "%USE_MOCK%"=="1" (
    echo Mode: MOCK (--noinference)
    echo Mock service will accept only: pass, fail, insufficient
) else (
    echo Model: %HF_BASE_MODEL_ID%
    echo Adapter: %LORA_ADAPTER_PATH%
)
echo.
echo Starting in a new window - you can minimize it if needed.

REM Build command with optional --noinference flag
set BACKEND_CMD=cd /d %BACKEND_DIR%
if "%USE_MOCK%"=="0" (
    set BACKEND_CMD=%BACKEND_CMD% && set "HF_BASE_MODEL_ID=%HF_BASE_MODEL_ID%" && set "LORA_ADAPTER_PATH=%LORA_ADAPTER_PATH%" && set "HF_TOKEN=%HF_TOKEN%" && set "HF_HOME=%HF_HOME%"
)
set BACKEND_CMD=%BACKEND_CMD% && %PYTHON_EXE% app.py
if "%USE_MOCK%"=="1" (
    set BACKEND_CMD=%BACKEND_CMD% --noinference
)

start "Car Backend - Port 5000" cmd /k "%BACKEND_CMD%"

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
