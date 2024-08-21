@echo off

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed.
    exit /b 1
)

pip install -r ./requirements.txt

python -m uvicorn apps.main:app --host 0.0.0.0 --port 8000
