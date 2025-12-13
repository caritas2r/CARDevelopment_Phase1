# Car Management System - Application Launcher (PowerShell)
# This script starts both the backend and frontend servers

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Car Management System - Starting..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get the directory where this script is located
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendDir = Join-Path $ScriptDir "car-back-end"
$FrontendDir = Join-Path $ScriptDir "car-front-end"

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

Write-Host "Starting Backend Server (Port 5000)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$BackendDir'; python app.py" -WindowStyle Minimized

# Wait for backend to start and check if it's ready
Write-Host "Waiting for backend to initialize..." -ForegroundColor Yellow
$backendReady = $false
$maxAttempts = 10
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
        Write-Host "Backend still starting, waiting... ($attempt/$maxAttempts)" -ForegroundColor Yellow
    }
}

Write-Host "Starting Frontend Server (Port 8000)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$FrontendDir'; python -m http.server 8000" -WindowStyle Minimized

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
        Write-Host "Frontend still starting, waiting... ($attempt/$maxAttempts)" -ForegroundColor Yellow
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
Write-Host "Servers are running in minimized windows." -ForegroundColor Yellow
Write-Host "Close those windows or run stop-app.ps1 to stop the servers." -ForegroundColor Yellow
Write-Host ""
Read-Host "Press Enter to exit this launcher"

