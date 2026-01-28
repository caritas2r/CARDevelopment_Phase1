@echo off
setlocal enabledelayedexpansion

echo Testing environment variable passing...
echo.

set "SCRIPT_DIR=%~dp0"
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
cd /d "%SCRIPT_DIR%"
set "SCRIPT_DIR=%CD%"

set "HF_BASE_MODEL_ID=Qwen/Qwen2.5-3B"
set "LORA_ADAPTER_PATH=%SCRIPT_DIR%\car-models\qwen25_3b_base_MAPPED_v2"
set "HF_HOME=%SCRIPT_DIR%\hf_cache"

echo Variables in batch file:
echo HF_BASE_MODEL_ID = %HF_BASE_MODEL_ID%
echo LORA_ADAPTER_PATH = %LORA_ADAPTER_PATH%
echo HF_HOME = %HF_HOME%
echo.

set "TEST_CMD=cd /d "%SCRIPT_DIR%\car-back-end" && set \"HF_BASE_MODEL_ID=!HF_BASE_MODEL_ID!\" && set \"LORA_ADAPTER_PATH=!LORA_ADAPTER_PATH!\" && set \"HF_HOME=!HF_HOME!\" && python -c \"import os; print('HF_BASE_MODEL_ID:', os.getenv('HF_BASE_MODEL_ID', 'NOT SET')); print('LORA_ADAPTER_PATH:', os.getenv('LORA_ADAPTER_PATH', 'NOT SET')); print('HF_HOME:', os.getenv('HF_HOME', 'NOT SET'))\""

echo Testing command that will be executed:
echo %TEST_CMD%
echo.

echo Running test in new window...
start "Test Env Vars" cmd /k "!TEST_CMD!"
pause
