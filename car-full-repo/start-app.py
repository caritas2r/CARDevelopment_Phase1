#!/usr/bin/env python3
"""
Car Management System - Application Launcher with Inference Environment (Python)
This script sets up the inference venv and starts both backend and frontend servers
"""
import os
import sys
import subprocess
import time
import platform
import argparse
from pathlib import Path

# -----------------------------
# Inference Model Configuration
# -----------------------------
# IMPORTANT: Update HF_BASE_MODEL_ID to match the exact base model you trained against.
# Adapter path is assumed to be inside the repo under car-models/<adapter_folder_name>
HF_BASE_MODEL_ID = "Qwen/Qwen2.5-3B"
MODEL_DIR_NAME = "qwen25_3b_base_MAPPED_v2"

# Optional inference controls (uncomment if you want to override defaults)
# INFERENCE_DEVICE = "auto"
# MAX_NEW_TOKENS = 512
# TEMPERATURE = 0.0
# TOP_P = 1.0
# END_JSON_TOKEN = "<END_JSON>"
# HF_TOKEN = "your_token_if_needed"

def check_python_available():
    """Check if Python is available"""
    try:
        result = subprocess.run([sys.executable, "--version"], 
                              capture_output=True, text=True, check=True)
        print(f"Found: {result.stdout.strip()}")
        return True
    except Exception as e:
        print(f"ERROR: Python is not available: {e}")
        return False

def check_nvidia_gpu():
    """Check if NVIDIA GPU is available"""
    try:
        result = subprocess.run(["nvidia-smi"], 
                              capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except Exception:
        return False

def verify_imports(python_exe):
    """Verify that all required packages can be imported"""
    try:
        result = subprocess.run(
            [str(python_exe), "-c", 
             "import torch; import transformers; import peft; import accelerate; import safetensors; import flask; import orjson"],
            capture_output=True,
            timeout=30
        )
        return result.returncode == 0
    except Exception:
        return False

def setup_venv(backend_dir, venv_dir, reinstall=False):
    """Set up the virtual environment"""
    venv_path = Path(venv_dir)
    
    # Remove existing venv if reinstall flag is set
    if reinstall and venv_path.exists():
        print("--reinstall flag detected. Recreating virtual environment...")
        print("Removing existing virtual environment...")
        try:
            if platform.system() == "Windows":
                subprocess.run(["rmdir", "/s", "/q", str(venv_path)], 
                             shell=True, check=True)
            else:
                import shutil
                shutil.rmtree(venv_path)
            print("Virtual environment removed.")
        except Exception as e:
            print(f"ERROR: Failed to remove existing virtual environment: {e}")
            print("Please close any processes using the venv and try again.")
            return False
    
    # Create venv if it doesn't exist
    if not venv_path.exists():
        print("Creating virtual environment: car_inference_env...")
        try:
            subprocess.run([sys.executable, "-m", "venv", str(venv_path)], 
                         cwd=backend_dir, check=True)
            print("Virtual environment created successfully.")
        except Exception as e:
            print(f"ERROR: Failed to create virtual environment: {e}")
            return False
    else:
        print("Virtual environment already exists.")
    
    return True

def install_packages(venv_dir):
    """Install required packages in the virtual environment"""
    is_windows = platform.system() == "Windows"
    if is_windows:
        python_exe = Path(venv_dir) / "Scripts" / "python.exe"
        pip_exe = Path(venv_dir) / "Scripts" / "pip.exe"
    else:
        python_exe = Path(venv_dir) / "bin" / "python"
        pip_exe = Path(venv_dir) / "bin" / "pip"
    
    print("Installing / updating packages (idempotent)...")
    print()
    
    # Upgrade pip first
    print("Upgrading pip...")
    try:
        subprocess.run([str(python_exe), "-m", "pip", "install", "--upgrade", "pip", "--quiet"], 
                      check=True, timeout=120)
    except Exception as e:
        print(f"ERROR: Failed to upgrade pip: {e}")
        return False
    
    # Install torch with GPU support if possible; otherwise fallback to CPU
    # NOTE: torch is intentionally NOT in requirements.inference.txt to avoid platform-specific wheel issues.
    print("Installing PyTorch...")
    try:
        has_gpu = check_nvidia_gpu()
        if has_gpu:
            print("NVIDIA GPU detected. Attempting CUDA 12.4 PyTorch...")
            try:
                subprocess.run([str(pip_exe), "install", "torch", 
                               "--index-url", "https://download.pytorch.org/whl/cu124"], 
                              check=True, timeout=600)
            except Exception:
                print("WARNING: CUDA PyTorch install failed. Falling back to CPU PyTorch...")
                subprocess.run([str(pip_exe), "install", "torch"], 
                              check=True, timeout=600)
        else:
            print("No NVIDIA GPU detected. Installing CPU PyTorch...")
            subprocess.run([str(pip_exe), "install", "torch"], 
                          check=True, timeout=600)
    except Exception as e:
        print(f"ERROR: Failed to install PyTorch: {e}")
        return False
    
    # Install other requirements
    print("Installing inference requirements...")
    try:
        backend_dir = Path(venv_dir).parent
        requirements_file = backend_dir / "requirements.inference.txt"
        subprocess.run([str(pip_exe), "install", "-r", str(requirements_file)], 
                      check=True, timeout=300)
    except Exception as e:
        print(f"ERROR: Failed to install inference requirements: {e}")
        return False
    
    # Quick import check to catch obvious env issues early
    print("Verifying imports...")
    if verify_imports(python_exe):
        print("Import verification successful.")
        print()
        print("Packages installed successfully!")
        return True
    else:
        print("ERROR: Import verification failed. Check pip output above for details.")
        return False

def main():
    parser = argparse.ArgumentParser(description="Start Car Management System with inference environment")
    parser.add_argument("--reinstall", action="store_true", 
                       help="Force recreation of virtual environment and reinstall packages")
    args = parser.parse_args()
    
    print("=" * 50)
    print("Car Management System - Starting...")
    print("=" * 50)
    print()
    
    # Get the directory where this script is located
    script_dir = Path(__file__).parent.absolute()
    backend_dir = script_dir / "car-back-end"
    frontend_dir = script_dir / "car-front-end"
    venv_dir = backend_dir / "car_inference_env"
    model_dir = script_dir / "car-models" / MODEL_DIR_NAME
    requirements_file = backend_dir / "requirements.inference.txt"
    
    # Check if directories exist
    if not backend_dir.exists():
        print(f"ERROR: Backend directory not found at {backend_dir}")
        input("Press Enter to exit...")
        sys.exit(1)
    
    if not frontend_dir.exists():
        print(f"ERROR: Frontend directory not found at {frontend_dir}")
        input("Press Enter to exit...")
        sys.exit(1)
    
    if not model_dir.exists():
        print(f"ERROR: Model adapter directory not found at {model_dir}")
        print(f"Ensure you copied your adapter folder into: {script_dir / 'car-models' / ''}")
        input("Press Enter to exit...")
        sys.exit(1)
    
    if not requirements_file.exists():
        print(f"ERROR: requirements.inference.txt not found at {requirements_file}")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Check if Python is available
    if not check_python_available():
        input("Press Enter to exit...")
        sys.exit(1)
    
    print("Setting up inference environment...")
    print()
    
    # Set up venv
    if not setup_venv(backend_dir, venv_dir, args.reinstall):
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Determine Python executable path
    is_windows = platform.system() == "Windows"
    if is_windows:
        python_exe = venv_dir / "Scripts" / "python.exe"
    else:
        python_exe = venv_dir / "bin" / "python"
    
    # Install packages (always run - pip handles idempotency)
    if not install_packages(venv_dir):
        input("Press Enter to exit...")
        sys.exit(1)
    
    print()
    print("Starting Backend Server (Port 5000)...")
    
    # Set environment variables for backend
    backend_env = os.environ.copy()
    backend_env["HF_BASE_MODEL_ID"] = HF_BASE_MODEL_ID
    backend_env["LORA_ADAPTER_PATH"] = str(model_dir)
    backend_env["HF_TOKEN"] = os.getenv("HF_TOKEN", "")
    backend_env["HF_HOME"] = str(script_dir / "hf_cache")
    
    # Start backend
    if is_windows:
        # Windows: Use cmd to set env vars and run in new window
        hf_token = os.getenv("HF_TOKEN", "")
        hf_home = script_dir / "hf_cache"
        cmd = f'cd /d {backend_dir} && set "HF_BASE_MODEL_ID={HF_BASE_MODEL_ID}" && set "LORA_ADAPTER_PATH={model_dir}" && set "HF_TOKEN={hf_token}" && set "HF_HOME={hf_home}" && {python_exe} app.py'
        subprocess.Popen(
            f'start /MIN cmd /k "{cmd}"',
            shell=True
        )
    else:
        # Unix/Linux/Mac: Run in background with env vars
        subprocess.Popen(
            [str(python_exe), "app.py"],
            cwd=backend_dir,
            env=backend_env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    
    # Wait for backend to start and check if it's ready (model load may take longer on first run)
    print("Waiting for backend to initialize (this may take 10-30 seconds on first run)...")
    import urllib.request
    backend_ready = False
    max_attempts = 15
    attempt = 0
    
    while not backend_ready and attempt < max_attempts:
        time.sleep(2)
        try:
            response = urllib.request.urlopen("http://localhost:5000/api/health", timeout=2)
            if response.getcode() == 200:
                backend_ready = True
                print("Backend is ready!")
        except Exception:
            attempt += 1
            if attempt < max_attempts:
                print(f"Backend still starting, waiting... ({attempt}/{max_attempts})")
    
    if not backend_ready:
        print("WARNING: Backend health check timed out, but continuing anyway...")
    
    print("Starting Frontend Server (Port 8000)...")
    if is_windows:
        subprocess.Popen(
            f'start /MIN cmd /k "cd /d {frontend_dir} && {python_exe} -m http.server 8000"',
            shell=True
        )
    else:
        subprocess.Popen(
            [str(python_exe), "-m", "http.server", "8000"],
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
        except Exception:
            attempt += 1
            if attempt < max_attempts:
                print(f"Frontend still starting, waiting... ({attempt}/{max_attempts})")
    
    # Open browser to frontend
    print()
    print("Opening browser to http://localhost:8000...")
    import webbrowser
    webbrowser.open("http://localhost:8000")
    
    print()
    print("=" * 50)
    print("Application is running!")
    print("=" * 50)
    print()
    print("Backend:  http://localhost:5000")
    print("Frontend: http://localhost:8000 (opened in browser)")
    print()
    print(f"Virtual Environment: {venv_dir}")
    print(f"Adapter Path: {model_dir}")
    print(f"Base Model: {HF_BASE_MODEL_ID}")
    print()
    print("Servers are running in the background.")
    print("Close this window or run stop-app.py to stop the servers.")
    print()
    input("Press Enter to exit this launcher...")

if __name__ == "__main__":
    main()
