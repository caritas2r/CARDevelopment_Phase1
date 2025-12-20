@echo off
REM Car Management System - Stop Script
REM This script stops both backend and frontend servers

echo ========================================
echo Car Management System - Stopping...
echo ========================================
echo.

echo Stopping processes on ports 5000 and 8000...

REM Kill processes on port 5000 (Backend)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5000 ^| findstr LISTENING') do (
    echo Stopping backend process (PID: %%a)...
    taskkill /F /PID %%a >nul 2>&1
)

REM Kill processes on port 8000 (Frontend)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    echo Stopping frontend process (PID: %%a)...
    taskkill /F /PID %%a >nul 2>&1
)

REM Also try to kill Python processes that might be running the servers
echo.
echo Checking for Python server processes...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Car Backend*" >nul 2>&1
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Car Frontend*" >nul 2>&1

echo.
echo ========================================
echo Servers stopped!
echo ========================================
echo.
pause

