#!/usr/bin/env python3
"""
Car Management System - Application Launcher (Python)
This script starts both the backend and frontend servers
"""
import os
import sys
import subprocess
import time
import platform
from pathlib import Path

def main():
    print("=" * 50)
    print("Car Management System - Starting...")
    print("=" * 50)
    print()
    
    # Get the directory where this script is located
    script_dir = Path(__file__).parent.absolute()
    backend_dir = script_dir / "car-back-end"
    frontend_dir = script_dir / "car-front-end"
    
    # Check if directories exist
    if not backend_dir.exists():
        print(f"ERROR: Backend directory not found at {backend_dir}")
        input("Press Enter to exit...")
        sys.exit(1)
    
    if not frontend_dir.exists():
        print(f"ERROR: Frontend directory not found at {frontend_dir}")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Determine the command to use based on OS
    is_windows = platform.system() == "Windows"
    
    import urllib.request
    import webbrowser
    
    print("Starting Backend Server (Port 5000)...")
    if is_windows:
        # Windows: Open in minimized window using start command
        subprocess.Popen(
            f'start /MIN cmd /k "cd /d {backend_dir} && python app.py"',
            shell=True
        )
    else:
        # Unix/Linux/Mac: Run in background
        subprocess.Popen(
            ["python", "app.py"],
            cwd=backend_dir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    
    # Wait for backend to start and check if it's ready
    print("Waiting for backend to initialize...")
    backend_ready = False
    max_attempts = 10
    attempt = 0
    
    while not backend_ready and attempt < max_attempts:
        time.sleep(2)
        try:
            response = urllib.request.urlopen("http://localhost:5000/api/health", timeout=2)
            if response.getcode() == 200:
                backend_ready = True
                print("Backend is ready!")
        except:
            attempt += 1
            print(f"Backend still starting, waiting... ({attempt}/{max_attempts})")
    
    print("Starting Frontend Server (Port 8000)...")
    if is_windows:
        # Windows: Open in minimized window using start command
        subprocess.Popen(
            f'start /MIN cmd /k "cd /d {frontend_dir} && python -m http.server 8000"',
            shell=True
        )
    else:
        # Unix/Linux/Mac: Run in background
        subprocess.Popen(
            ["python", "-m", "http.server", "8000"],
            cwd=frontend_dir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    
    # Wait for frontend to start and check if it's ready
    print("Waiting for frontend to initialize...")
    frontend_ready = False
    attempt = 0
    
    while not frontend_ready and attempt < max_attempts:
        time.sleep(2)
        try:
            response = urllib.request.urlopen("http://localhost:8000", timeout=2)
            if response.getcode() == 200:
                frontend_ready = True
                print("Frontend is ready!")
        except:
            attempt += 1
            print(f"Frontend still starting, waiting... ({attempt}/{max_attempts})")
    
    # Open browser to frontend
    print()
    print("Opening browser to http://localhost:8000...")
    webbrowser.open("http://localhost:8000")
    
    print()
    print("=" * 50)
    print("Application is running!")
    print("=" * 50)
    print()
    print("Backend:  http://localhost:5000")
    print("Frontend: http://localhost:8000 (opened in browser)")
    print()
    print("Servers are running in the background.")
    print("Close this window or run stop-app.py to stop the servers.")
    print()
    input("Press Enter to exit this launcher...")

if __name__ == "__main__":
    main()

