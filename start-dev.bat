@echo off
REM ========================================================================
REM Car App Development Launcher
REM ========================================================================
REM
REM This script launches both the Flask backend and Node frontend:
REM
REM 1. Starts Flask backend server (port 5000)
REM 2. Starts Node/Vite frontend server (port 5173)
REM 3. Opens browser to frontend
REM
REM Requirements:
REM - Python 3.10+ installed and in PATH
REM - Node.js and npm installed and in PATH
REM - Flask backend dependencies installed (car-full-repo/car-back-end)
REM - Node frontend dependencies installed (car_app-main/car_app-main)
REM
REM Usage:
REM   start-dev.bat              - Start both services
REM   start-dev.bat --noinference - Start backend in mock mode
REM ========================================================================

setlocal enabledelayedexpansion

REM Check for --noinference flag
set USE_MOCK=0
if /i "%~1"=="--noinference" set USE_MOCK=1

echo ========================================
echo Car App - Starting Development Servers
if "%USE_MOCK%"=="1" (
    echo Backend: MOCK MODE ^(--noinference^)
) else (
    echo Backend: INFERENCE MODE ^(full support^)
)
echo Frontend: Node/Vite (car_app-main)
echo ========================================
echo.

REM Get script directory
set "SCRIPT_DIR=%~dp0"
REM Remove trailing backslash
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

REM Convert to absolute path
cd /d "%SCRIPT_DIR%"
set "SCRIPT_DIR=%CD%"

REM Set directory paths
set "BACKEND_DIR=%SCRIPT_DIR%\car-full-repo\car-back-end"
set "FRONTEND_DIR=%SCRIPT_DIR%\car_app-main\car_app-main"

REM Set ports (changed from defaults to allow running alongside Downloads version)
set "BACKEND_PORT=5001"
set "FRONTEND_PORT=5174"

REM Debug: Show paths being checked
echo Checking directories...
echo Backend path: %BACKEND_DIR%
echo Frontend path: %FRONTEND_DIR%
echo.
echo Ports:
echo Backend port: %BACKEND_PORT%
echo Frontend port: %FRONTEND_PORT%
echo.

REM Check if directories exist
if not exist "%BACKEND_DIR%" (
    echo ERROR: Backend directory not found: %BACKEND_DIR%
    echo Please ensure you're running this from CARDevelopment_Phase1 directory
    pause
    exit /b 1
)

if not exist "%FRONTEND_DIR%" (
    echo ERROR: Frontend directory not found: %FRONTEND_DIR%
    echo Please ensure you're running this from CARDevelopment_Phase1 directory
    pause
    exit /b 1
)

echo Directories found!
echo.

REM Check for Python
echo Checking for Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found in PATH
    echo Please install Python 3.10+ and add it to PATH
    pause
    exit /b 1
)
echo Python found!
echo.

REM Check for Node.js - try with common installation paths if not in PATH
echo Checking for Node.js...
set "NODE_FOUND=0"
node --version >nul 2>&1
if not errorlevel 1 (
    set "NODE_FOUND=1"
)

REM If not in PATH, try common installation paths
if "!NODE_FOUND!"=="0" (
    if exist "C:\Program Files\nodejs\node.exe" (
        set "PATH=%PATH%;C:\Program Files\nodejs"
        set "NODE_FOUND=1"
        echo Node.js found at default location, added to PATH
    )
)

if "!NODE_FOUND!"=="0" (
    echo ERROR: Node.js not found in PATH
    echo Please install Node.js and add it to PATH
    echo Or ensure Node.js is installed at: C:\Program Files\nodejs\
    pause
    exit /b 1
)
echo Node.js found!
echo.

REM Check for npm (should be available if Node.js is found)
echo Checking for npm...
REM Just verify npm.cmd exists - don't try to run it (it might not be in PATH)
set "NPM_FOUND=0"
if exist "C:\Program Files\nodejs\npm.cmd" (
    set "NPM_FOUND=1"
    echo npm found at Node.js installation directory
) else (
    echo WARNING: npm.cmd not found, but will try anyway
)
echo.

REM Load Stripe API key from env_var file (if it exists)
REM Format: API_KEY = <your_key_here>
set "STRIPE_API_KEY="
set "ENV_VAR_FILE=%SCRIPT_DIR%\car-full-repo\env_var"
if exist "%ENV_VAR_FILE%" (
    REM Read API_KEY from env_var file and set as STRIPE_API_KEY
    for /f "usebackq tokens=1,* delims==" %%a in ("%ENV_VAR_FILE%") do (
        REM Trim whitespace from variable name and value
        for /f "tokens=*" %%n in ("%%a") do set "VAR_NAME=%%n"
        for /f "tokens=*" %%v in ("%%b") do set "VAR_VALUE=%%v"
        REM Remove any remaining leading/trailing spaces
        set "VAR_NAME=!VAR_NAME: =!"
        set "VAR_VALUE=!VAR_VALUE: =!"
        REM Check if this is API_KEY (case-insensitive)
        if /i "!VAR_NAME!"=="API_KEY" (
            set "STRIPE_API_KEY=!VAR_VALUE!"
        )
    )
)

REM Debug: Check if API key was loaded
if "!STRIPE_API_KEY!"=="" (
    echo WARNING: STRIPE_API_KEY not found in env_var file - payment processing will be disabled
) else (
    echo Stripe API key loaded from env_var file
)

echo.
echo Starting Flask backend...
echo Backend directory: %BACKEND_DIR%
echo Backend will run on: http://localhost:%BACKEND_PORT%
echo.

REM Start Flask backend in a new window
REM Set STRIPE_API_KEY environment variable before running Python
if "%USE_MOCK%"=="1" (
    start "Flask Backend (MOCK MODE) - Port %BACKEND_PORT%" cmd /k "cd /d %BACKEND_DIR% && set PORT=%BACKEND_PORT% && set STRIPE_API_KEY=!STRIPE_API_KEY! && python app.py --noinference --port %BACKEND_PORT%"
) else (
    start "Flask Backend - Port %BACKEND_PORT%" cmd /k "cd /d %BACKEND_DIR% && set PORT=%BACKEND_PORT% && set STRIPE_API_KEY=!STRIPE_API_KEY! && python app.py --port %BACKEND_PORT%"
)

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

echo.
echo Starting Node/Vite frontend...
echo Frontend directory: %FRONTEND_DIR%
echo Frontend will run on: http://localhost:%FRONTEND_PORT%
echo.

REM Start Node frontend in a new window
REM Ensure npm is available by adding Node.js to PATH in the new window
REM Set VITE_API_BASE_URL to point to the backend on the new port
start "Node Frontend - Port %FRONTEND_PORT%" cmd /k "cd /d %FRONTEND_DIR% && set PATH=%PATH%;C:\Program Files\nodejs && set VITE_API_BASE_URL=http://localhost:%BACKEND_PORT% && npm run dev -- --port %FRONTEND_PORT%"

REM Wait a moment for frontend to start
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo Development servers started!
echo.
echo Backend:  http://localhost:%BACKEND_PORT%
echo Frontend: http://localhost:%FRONTEND_PORT%
echo.
echo Press any key to open the frontend in your browser...
echo Or close this window (servers will continue running)
echo ========================================
pause >nul

REM Open browser to frontend
start http://localhost:%FRONTEND_PORT%

echo.
echo Browser opened! Both servers are running in separate windows.
echo Close those windows to stop the servers.
echo.
pause

