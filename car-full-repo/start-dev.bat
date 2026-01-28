@echo off
REM ========================================================================
REM Development Launcher - Start Frontend and Inference-Capable Backend
REM ========================================================================
REM
REM This script starts both servers for development:
REM 1. Backend server (port 5000) with full inference support
REM 2. Frontend server (port 8000)
REM 3. Opens browser to frontend
REM
REM Requirements:
REM - Python 3.10+ installed
REM - Virtual environment at car-back-end\car_inference_env (or system Python)
REM - All dependencies already installed
REM - Model adapter at car-models\qwen25_3b_base_MAPPED_v2
REM ========================================================================

setlocal enabledelayedexpansion

echo ========================================
echo Starting Development Servers
echo ========================================
echo.

REM Get script directory and convert to absolute path
set "SCRIPT_DIR=%~dp0"
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
cd /d "%SCRIPT_DIR%"
set "SCRIPT_DIR=%CD%"

set "BACKEND_DIR=%SCRIPT_DIR%\car-back-end"
set "FRONTEND_DIR=%SCRIPT_DIR%\car-front-end"
set "VENV_DIR=%BACKEND_DIR%\car_inference_env"
set "PYTHON_EXE=%VENV_DIR%\Scripts\python.exe"

REM Check if virtual environment exists, otherwise use system Python
if not exist "%PYTHON_EXE%" (
    echo Virtual environment not found at %VENV_DIR%
    echo Using system Python instead...
    set "PYTHON_EXE=python"
)

REM Model configuration
set "HF_BASE_MODEL_ID=Qwen/Qwen2.5-3B"
set "MODEL_DIR=%SCRIPT_DIR%\car-models\qwen25_3b_base_MAPPED_v2"
set "LORA_ADAPTER_PATH=%MODEL_DIR%"
set "HF_TOKEN="
set "HF_HOME=%SCRIPT_DIR%\hf_cache"

REM Create hf_cache directory if it doesn't exist
if not exist "%HF_HOME%" (
    echo Creating HF cache directory: %HF_HOME%
    mkdir "%HF_HOME%"
)

REM Check if model directory exists
if not exist "%MODEL_DIR%" (
    echo WARNING: Model adapter directory not found at %MODEL_DIR%
    echo Inference will fail. Consider using --noinference mode or setting up the model.
    echo.
)

REM Stripe configuration (load from env_var file if exists)
set "STRIPE_API_KEY="
if exist "%SCRIPT_DIR%\env_var" (
    for /f "usebackq tokens=1,* delims==" %%a in ("%SCRIPT_DIR%\env_var") do (
        for /f "tokens=*" %%n in ("%%a") do set "VAR_NAME=%%n"
        for /f "tokens=*" %%v in ("%%b") do set "VAR_VALUE=%%v"
        set "VAR_NAME=!VAR_NAME: =!"
        set "VAR_VALUE=!VAR_VALUE: =!"
        if /i "!VAR_NAME!"=="API_KEY" (
            set "STRIPE_API_KEY=!VAR_VALUE!"
        )
    )
)

echo Starting Backend Server (Port 5000)...
echo Model: %HF_BASE_MODEL_ID%
echo Adapter: %LORA_ADAPTER_PATH%
echo.
echo Starting in a new window - you can minimize it if needed.

REM Build backend command with environment variables
REM Check if PYTHON_EXE is a file path or a command name
if exist "%PYTHON_EXE%" (
    REM It's a file path - quote it for paths with spaces
    set "PYTHON_CMD_QUOTED=%PYTHON_EXE%"
) else (
    REM It's a command name like "py" or "python" - use as-is
    set "PYTHON_CMD_QUOTED=%PYTHON_EXE%"
)

set "BACKEND_CMD=cd /d "%BACKEND_DIR%""
if not "!STRIPE_API_KEY!"=="" (
    set "BACKEND_CMD=!BACKEND_CMD! && set STRIPE_API_KEY=!STRIPE_API_KEY!"
)
set "BACKEND_CMD=!BACKEND_CMD! && set \"HF_BASE_MODEL_ID=!HF_BASE_MODEL_ID!\" && set \"LORA_ADAPTER_PATH=!LORA_ADAPTER_PATH!\" && set \"HF_TOKEN=!HF_TOKEN!\" && set \"HF_HOME=!HF_HOME!\" && \"%PYTHON_CMD_QUOTED%\" app.py"

REM Debug: Show what will be executed
echo Executing backend command in new window...
echo.

REM Start backend in new window
start "Car Backend - Port 5000" cmd /k "!BACKEND_CMD!"

REM Wait for backend to start
echo Waiting for backend to initialize (this may take 10-30 seconds on first run)...
timeout /t 10 /nobreak >nul

echo Starting Frontend Server (Port 8000)...
echo Starting in a new window - you can minimize it if needed.

REM Start frontend - try Node.js first, fallback to Python
set "FRONTEND_CMD=cd /d "%FRONTEND_DIR%""
where node >nul 2>&1
if not errorlevel 1 (
    REM Node.js available - use dev-server.js
    set "FRONTEND_CMD=!FRONTEND_CMD! && node dev-server.js"
) else (
    REM Fallback to Python dev-server.py
    set "FRONTEND_CMD=!FRONTEND_CMD! && "%PYTHON_EXE%" dev-server.py"
)

start "Car Frontend - Port 8000" cmd /k "!FRONTEND_CMD!"

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
echo Development servers are starting!
echo ========================================
echo.
echo Backend:  http://localhost:5000
echo Frontend: http://localhost:8000 (opened in browser)
echo.
echo Both servers are running in separate windows.
echo Close those windows to stop the servers.
echo.
pause
