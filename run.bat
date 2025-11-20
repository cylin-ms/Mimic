@echo off
REM Wrapper to run the estimator in the isolated environment

set DIR=%~dp0

if not exist "%DIR%venv" (
    echo ❌ Virtual environment not found. Please run setup.bat first.
    exit /b 1
)

call "%DIR%venv\Scripts\activate.bat"
python "%DIR%estimate_value.py" %*
