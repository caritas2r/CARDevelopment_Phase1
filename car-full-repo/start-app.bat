@echo off
REM Car Management System - Application Launcher
REM This script starts both the backend and frontend servers and opens the browser

echo ========================================
echo Car Management System - Starting...
echo ========================================
echo.

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
set BACKEND_DIR=%SCRIPT_DIR%car-back-end
set FRONTEND_DIR=%SCRIPT_DIR%car-front-end

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

echo Starting Backend Server (Port 5000)...
echo Starting in a new window - you can minimize it if needed.
start "Car Backend - Port 5000" cmd /k "cd /d %BACKEND_DIR% && python app.py"

REM Wait for backend to start (give it more time)
echo Waiting for backend to initialize (this may take 10-15 seconds)...
timeout /t 10 /nobreak >nul

echo Starting Frontend Server (Port 8000)...
echo Starting in a new window - you can minimize it if needed.
start "Car Frontend - Port 8000" cmd /k "cd /d %FRONTEND_DIR% && python -m http.server 8000"

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
echo Two windows have opened - one for each server.
echo You can minimize them or keep them open to see logs.
echo Close those windows to stop the servers.
echo.
echo Press any key to exit this launcher...
pause >nul
