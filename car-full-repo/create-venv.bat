@echo off
REM ========================================================================
REM Car Management System - Application Launcher
REM ========================================================================
REM
REM This script launches the application:
REM
REM 1. Finds Python executable (python or py command)
REM 2. Starts the backend server (port 5000)
REM 3. Starts the frontend server (port 8000)
REM 4. Opens the browser to the frontend
REM
REM Requirements:
REM - Python 3.10+ installed and in PATH
REM - All dependencies already installed (install separately if needed)
REM - Model adapter directory at car-models/qwen25_3b_base_MAPPED_v2 (for inference mode)
REM
REM Usage:
REM   create-venv.bat              - Start with inference (requires dependencies)
REM   create-venv.bat --noinference - Start in mock mode (minimal dependencies)
REM ========================================================================

setlocal enabledelayedexpansion

REM Check for --noinference flag
set USE_MOCK=0
if /i "%~1"=="--noinference" set USE_MOCK=1
if /i "%~2"=="--noinference" set USE_MOCK=1

echo ========================================
echo Car Management System - Starting...
if "%USE_MOCK%"=="1" (
    echo MOCK MODE: --noinference - no GPU/model required
    echo Using mock query service - accepts: pass, fail, insufficient
) else (
    echo INFERENCE MODE: Full inference support enabled
)
echo ========================================
echo;

REM Get script directory and convert to absolute path (remove trailing backslash)
set "SCRIPT_DIR=%~dp0"
REM Remove trailing backslash if present for cleaner path handling
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

REM Convert to absolute paths using cd (most reliable method)
cd /d "%SCRIPT_DIR%"
set "SCRIPT_DIR=%CD%"

set "BACKEND_DIR=%SCRIPT_DIR%\car-back-end"
set "FRONTEND_DIR=%SCRIPT_DIR%\car-front-end"

REM Model configuration (using absolute paths)
set "HF_BASE_MODEL_ID=Qwen/Qwen2.5-3B"
set "MODEL_DIR=%SCRIPT_DIR%\car-models\qwen25_3b_base_MAPPED_v2"
set "LORA_ADAPTER_PATH=%MODEL_DIR%"
set "HF_TOKEN="
set "HF_HOME=%SCRIPT_DIR%\hf_cache"

REM Auto-detect: If model directory doesn't exist and flag not set, automatically use mock mode
if "%USE_MOCK%"=="0" (
    if not exist "%MODEL_DIR%" (
        echo;
        echo ========================================
        echo WARNING: Model directory not found
        echo ========================================
        echo Model directory not found at: %MODEL_DIR%
        echo;
        echo Inference mode requires the model adapter.
        echo Automatically switching to MOCK mode --noinference.
        echo;
        echo To use inference mode, ensure the model directory exists.
        echo To explicitly use mock mode: create-venv.bat --noinference
        echo ========================================
        echo;
        set USE_MOCK=1
    )
)

echo Backend directory: %BACKEND_DIR%
echo Frontend directory: %FRONTEND_DIR%
echo;

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


REM Find Python executable - check both 'python' and 'py' commands
set PYTHON_EXE=
set PYTHON_CMD=

REM Try 'python' first
python --version >nul 2>&1
if not errorlevel 1 (
    REM Find the full path to python.exe
    for /f "delims=" %%i in ('where python 2^>nul') do (
        if exist "%%i" (
            set "PYTHON_EXE=%%i"
            set "PYTHON_CMD=python"
            goto :python_found
        )
    )
)

REM Try 'py' launcher
py --version >nul 2>&1
if not errorlevel 1 (
    REM Use py launcher to get actual Python path
    for /f "tokens=*" %%i in ('py -c "import sys; print(sys.executable)" 2^>nul') do (
        if exist "%%i" (
            set "PYTHON_EXE=%%i"
            set "PYTHON_CMD=py"
            goto :python_found
        )
    )
    REM If py launcher works but we can't get path, just use 'py'
    set "PYTHON_EXE=py"
    set "PYTHON_CMD=py"
    goto :python_found
)

REM Python not found
echo ERROR: Python is not installed or not in PATH
echo Please install Python 3.10+ from https://www.python.org/
echo Make sure to check "Add Python to PATH" during installation
pause
exit /b 1

:python_found
echo Found Python at: %PYTHON_EXE%
%PYTHON_CMD% --version
echo;

REM Resolve Python to absolute path (if it's a command name, keep it as-is)
if exist "%PYTHON_EXE%" (
    REM It's a file path, resolve to absolute
    for %%F in ("%PYTHON_EXE%") do set "PYTHON_EXE=%%~fF"
) else (
    REM It's a command name like "py" or "python", use as-is
    REM Don't resolve - it will be found via PATH
)
echo Using Python: %PYTHON_EXE%
echo;



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
echo;
echo Starting in a new window - you can minimize it if needed.

REM Build command with optional --noinference flag
REM Check if PYTHON_EXE is a file path or a command name
if exist "%PYTHON_EXE%" (
    REM It's a file path - quote it for paths with spaces
    set "PYTHON_CMD_QUOTED=%PYTHON_EXE%"
) else (
    REM It's a command name like "py" or "python" - use as-is
    set "PYTHON_CMD_QUOTED=%PYTHON_EXE%"
)

set "BACKEND_CMD=cd /d "%BACKEND_DIR%""
if "%USE_MOCK%"=="0" (
    set "BACKEND_CMD=%BACKEND_CMD% && set HF_BASE_MODEL_ID=%HF_BASE_MODEL_ID% && set LORA_ADAPTER_PATH=%LORA_ADAPTER_PATH% && set HF_TOKEN=%HF_TOKEN% && set HF_HOME=%HF_HOME%"
)
if "%USE_MOCK%"=="1" (
    set "BACKEND_CMD=%BACKEND_CMD% && "%PYTHON_CMD_QUOTED%" app.py --noinference"
) else (
    set "BACKEND_CMD=%BACKEND_CMD% && "%PYTHON_CMD_QUOTED%" app.py"
)

REM Debug: Show what will be executed
echo Executing backend command in new window...
echo;

REM Launch backend in new window
start "Car Backend - Port 5000" cmd /k "%BACKEND_CMD%"

REM Wait for backend to start (model load may take longer on first run)
echo Waiting for backend to initialize (this may take 10-30 seconds on first run)...
timeout /t 10 /nobreak >nul

echo Starting Frontend Server (Port 8000)...
echo Starting in a new window - you can minimize it if needed.
REM Use the same PYTHON_CMD_QUOTED variable
start "Car Frontend - Port 8000" cmd /k "cd /d "%FRONTEND_DIR%" && "%PYTHON_CMD_QUOTED%" -m http.server 8000"

REM Wait for frontend to start
echo Waiting for frontend to initialize...
timeout /t 5 /nobreak >nul

REM Open browser to frontend using default browser
echo;
echo Opening default browser to http://localhost:8000...
echo If the page doesn't load, wait a few more seconds and refresh.
REM Use rundll32 to explicitly open in default browser
rundll32 url.dll,FileProtocolHandler http://localhost:8000

echo;
echo ========================================
echo Application is starting!
echo ========================================
echo;
echo Backend: http://localhost:5000
echo Frontend: http://localhost:8000
echo;
echo Both servers are running in separate windows.
echo Close those windows to stop the servers.
echo;
pause
