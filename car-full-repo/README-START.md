# How to Start the Application

This repository includes several launcher scripts to start both the backend and frontend servers automatically.

## Quick Start (Windows - Recommended)

**Double-click `start-app.bat`** - This is the easiest way to start both servers!

The script will:
1. Start the backend server (port 5000) in a new window
2. Wait 10 seconds for the backend to initialize
3. Start the frontend server (port 8000) in a new window
4. Wait 5 seconds for the frontend to initialize
5. **Automatically open your default browser to http://localhost:8000**

**Note:** The servers run in visible windows so you can see logs. You can minimize them if needed. If the browser page doesn't load immediately, wait a few more seconds and refresh.

## Alternative Methods

### Option 1: Batch File (Windows)
- **File:** `start-app.bat`
- **Usage:** Double-click the file
- **Best for:** Windows users who want the simplest solution

### Option 2: PowerShell Script (Windows)
- **File:** `start-app.ps1`
- **Usage:** Right-click → "Run with PowerShell"
- **Note:** If you get an execution policy error, run:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

### Option 3: Python Script (Cross-platform)
- **File:** `start-app.py`
- **Usage:** 
  - Windows: Double-click (if Python is associated with .py files)
  - Or run: `python start-app.py`
- **Best for:** Cross-platform compatibility

## Manual Start (If Scripts Don't Work)

If the launcher scripts don't work, you can start the servers manually:

### Terminal 1 - Backend:
```bash
cd car-back-end
python app.py
```

### Terminal 2 - Frontend:
```bash
cd car-front-end
python -m http.server 8000
```

## Accessing the Application

Once both servers are running:
- **Backend API:** http://localhost:5000
- **Frontend UI:** http://localhost:8000

## Stopping the Servers

Simply close the command windows that opened for each server, or press `Ctrl+C` in each terminal.

## Troubleshooting

### "Python is not recognized"
- Make sure Python is installed and added to your PATH
- Try using `py` instead of `python` on Windows

### "Port already in use"
- Another process is using port 5000 or 8000
- Close other applications using those ports
- Or modify the ports in the scripts

### Scripts won't run
- For `.bat` files: Make sure you're on Windows
- For `.ps1` files: Check PowerShell execution policy
- For `.py` files: Make sure Python is installed

