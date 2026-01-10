# How to Start the Application

This repository includes several launcher scripts to start both the backend and frontend servers automatically with full inference support.

## Quick Start (Windows - Recommended)

**Double-click `create-venv.bat`** - This is the recommended way to start the application with inference end-to-end!

The script will:
1. **Create/verify the inference virtual environment** (`car_inference_env`)
2. **Install PyTorch** (with GPU support if NVIDIA is detected, otherwise CPU)
3. **Install all inference dependencies** (transformers, peft, accelerate, etc.)
4. **Start the backend server** (port 5000) with inference model configured in a new window
   - Sets up environment variables for model loading (`HF_BASE_MODEL_ID`, `LORA_ADAPTER_PATH`, `HF_HOME`)
   - Uses the virtual environment Python to run `app.py` with full inference capabilities
5. **Start the frontend server** (port 8000) in a new window
6. **Automatically open your default browser** to http://localhost:8000

**Note:** 
- The servers run in visible windows so you can see logs. You can minimize them if needed.
- First-time setup may take several minutes to download and install dependencies.
- Model loading on first run may take 10-30 seconds.
- If the browser page doesn't load immediately, wait a few more seconds and refresh.

**Requirements:**
- Python 3.10+ installed and in PATH
- Model adapter directory at `car-models/qwen25_3b_base_MAPPED_v2` (or update the script)
- `requirements.inference.txt` in the `car-back-end` directory

## Alternative Methods

### Windows - Batch File with Inference Support
- **File:** `create-venv.bat`
- **Usage:** Double-click the file
- **Best for:** Windows users who want full inference support (recommended)
- **Features:** Sets up venv, installs PyTorch and ML dependencies, starts application with inference model

### Windows - PowerShell Script (Alternative)
- **File:** `start-app.ps1`
- **Usage:** Right-click → "Run with PowerShell"
- **Note:** If you get an execution policy error, run:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```
- **Note:** This script also sets up the inference environment and starts both servers

### Cross-platform - Python Script (Alternative)
- **File:** `start-app.py`
- **Usage:** 
  - Windows: Double-click (if Python is associated with .py files)
  - Or run: `python start-app.py`
- **Best for:** Cross-platform compatibility
- **Note:** This script also sets up the inference environment and starts both servers

### Legacy Script (Not Recommended)
- **File:** `start-app.bat`
- **Status:** Redundant/nonfunctional - use `create-venv.bat` instead

## Manual Start (If Scripts Don't Work)

If the launcher scripts don't work, you can start the servers manually:

### Step 1: Set up the Inference Environment

First, create and activate the virtual environment:

```bash
cd car-back-end
python -m venv car_inference_env

# Windows:
car_inference_env\Scripts\activate

# macOS/Linux:
source car_inference_env/bin/activate
```

Then install dependencies:

```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install PyTorch (GPU if NVIDIA available, otherwise CPU)
# For GPU (NVIDIA):
pip install torch --index-url https://download.pytorch.org/whl/cu124

# For CPU:
pip install torch

# Install inference requirements
pip install -r requirements.inference.txt
```

### Step 2: Set Environment Variables

Set the following environment variables before starting:

**Windows (Command Prompt):**
```cmd
set HF_BASE_MODEL_ID=Qwen/Qwen2.5-3B
set LORA_ADAPTER_PATH=path\to\car-models\qwen25_3b_base_MAPPED_v2
set HF_HOME=path\to\repo\hf_cache
```

**Windows (PowerShell):**
```powershell
$env:HF_BASE_MODEL_ID = "Qwen/Qwen2.5-3B"
$env:LORA_ADAPTER_PATH = "path\to\car-models\qwen25_3b_base_MAPPED_v2"
$env:HF_HOME = "path\to\repo\hf_cache"
```

**macOS/Linux:**
```bash
export HF_BASE_MODEL_ID=Qwen/Qwen2.5-3B
export LORA_ADAPTER_PATH=path/to/car-models/qwen25_3b_base_MAPPED_v2
export HF_HOME=path/to/repo/hf_cache
```

### Step 3: Start the Servers

**Terminal 1 - Backend:**
```bash
cd car-back-end
# Make sure the virtual environment is activated
car_inference_env\Scripts\python.exe app.py  # Windows
# or
car_inference_env/bin/python app.py          # macOS/Linux
```

**Terminal 2 - Frontend:**
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

