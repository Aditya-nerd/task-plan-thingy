@echo off
REM Smart Task Planner - Quick Run Script for Windows

echo 🎯 Starting Smart Task Planner...

REM Check if virtual environment exists
if not exist "venv" (
    echo ❌ Virtual environment not found. Please run setup.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment and run application
call venv\Scripts\activate.bat
python main.py