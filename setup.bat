@echo off
REM NexStep AI Pro - Automated Setup Script (Windows)
REM Author: Anubhab Mondal

echo ====================================
echo 🚀 NexStep AI Pro - Setup Script
echo ====================================
echo.

REM Check Python installation
echo 📋 Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found. Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✓ Python %PYTHON_VERSION% found
echo.

REM Create virtual environment
echo 🔧 Creating virtual environment...
if exist venv (
    echo ⚠️  Virtual environment already exists. Skipping...
) else (
    python -m venv venv
    echo ✓ Virtual environment created
)
echo.

REM Activate virtual environment
echo 🔌 Activating virtual environment...
call venv\Scripts\activate.bat
echo ✓ Virtual environment activated
echo.

REM Upgrade pip
echo ⬆️  Upgrading pip...
python -m pip install --upgrade pip --quiet
echo ✓ pip upgraded
echo.

REM Install dependencies
echo 📦 Installing dependencies...
pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo ❌ Error installing dependencies
    pause
    exit /b 1
)
echo ✓ Dependencies installed
echo.

REM Create .env file
if not exist .env (
    echo 📝 Creating .env file...
    copy .env.template .env >nul
    echo ✓ .env file created
    echo.
    echo ⚠️  IMPORTANT: Edit .env file and add your Google API key!
    echo    Get your API key at: https://makersuite.google.com/app/apikey
) else (
    echo ✓ .env file already exists
)

echo.
echo ====================================
echo ✅ Setup Complete!
echo ====================================
echo.
echo 📝 Next Steps:
echo 1. Edit .env file and add your GOOGLE_API_KEY
echo 2. Run the app: streamlit run nexstep_pro.py
echo.
echo 💡 Quick start:
echo    venv\Scripts\activate
echo    streamlit run nexstep_pro.py
echo.
echo 📚 For deployment instructions, see DEPLOYMENT.md
echo 📖 For full documentation, see README.md
echo.
echo 🎉 Happy career planning!
echo.
pause
