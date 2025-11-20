@echo off
echo 🚀 Setting up Meeting Value Estimator...

REM Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH. Please install Python.
    pause
    exit /b 1
)

REM Create virtual environment
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
) else (
    echo 📦 Virtual environment already exists.
)

REM Activate and install
echo ⬇️ Installing dependencies...
call venv\Scripts\activate.bat
pip install -r requirements.txt

echo ✅ Setup complete!
echo.
echo To run the estimator:
echo   run.bat ^<your_calendar.json^>
pause
