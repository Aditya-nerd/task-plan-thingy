@echo off
REM Smart Task Planner - Windows Setup and Run Script

echo 🎯 Smart Task Planner - Windows Setup
echo ========================================

REM Check if virtual environment exists
if not exist "venv" (
    echo 🔄 Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
    echo ✅ Virtual environment created
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo 🔄 Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo 🔄 Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

REM Copy environment file if it doesn't exist
if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env"
        echo ✅ Created .env file from .env.example
    )
)

echo.
echo 🎉 Setup completed successfully!
echo.
echo 📋 Next steps:
echo 1. Edit the .env file to add your API keys
echo 2. Run: python main.py
echo 3. Open http://localhost:8000 in your browser
echo.
pause