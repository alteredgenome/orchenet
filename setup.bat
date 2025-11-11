@echo off
REM OrcheNet Setup Script - Clean Installation
REM This script sets up the environment from scratch

echo ========================================
echo   OrcheNet Setup
echo ========================================
echo.

REM Check prerequisites
echo Checking prerequisites...

where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://python.org
    pause
    exit /b 1
)
echo * Python found

where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js 18+ from https://nodejs.org
    pause
    exit /b 1
)
echo * Node.js found

where npm >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: npm is not installed or not in PATH
    pause
    exit /b 1
)
echo * npm found

echo.
echo ========================================
echo   Setting Up Backend
echo ========================================
echo.

cd backend

REM Clean previous installation if exists
if exist "venv\" (
    echo Removing old virtual environment...
    rmdir /s /q venv
)

if exist "orchenet.db" (
    echo Removing old database...
    del orchenet.db
)

REM Create virtual environment
echo Creating Python virtual environment...
python -m venv venv
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip -q

REM Install dependencies
echo Installing Python dependencies...
echo This may take a few minutes...
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to install Python dependencies
    echo.
    echo If you see Rust-related errors, some packages were removed.
    echo The system will still work for basic functionality.
    pause
)

REM Create .env file
if not exist ".env" (
    echo Creating .env file from template...
    copy .env.example .env >nul
    echo Please edit backend\.env with your configuration
)

REM Initialize database
echo.
echo Initializing database with sample data...
call venv\Scripts\activate.bat
python init_db.py --seed
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to initialize database
    echo.
    echo Try running manually from backend directory:
    echo   cd backend
    echo   venv\Scripts\activate.bat
    echo   python init_db.py --seed
    pause
    exit /b 1
)

cd ..
echo.
echo * Backend setup complete
echo.

REM Setup Frontend
echo ========================================
echo   Setting Up Frontend
echo ========================================
echo.

cd frontend

REM Clean previous installation if exists
if exist "node_modules\" (
    echo Removing old node_modules...
    rmdir /s /q node_modules
)

if exist "package-lock.json" (
    del package-lock.json
)

REM Install dependencies
echo Installing Node.js dependencies...
echo This may take a few minutes...
call npm install
if %ERRORLEVEL% NEQ 0 (
    echo WARNING: npm install had issues
    echo Trying with --legacy-peer-deps...
    call npm install --legacy-peer-deps
)

REM Create .env file
if not exist ".env" (
    echo Creating .env file from template...
    copy .env.example .env >nul
)

cd ..
echo.
echo * Frontend setup complete
echo.

REM Create logs directory
if not exist "logs\" (
    mkdir logs
)

echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo To start OrcheNet, you have two options:
echo.
echo Option 1 - Individual windows (Recommended):
echo   1. Run: start-backend.bat
echo   2. Run: start-frontend.bat (in new window)
echo.
echo Option 2 - All-in-one:
echo   Run: start.bat
echo.
echo The application will be available at:
echo   Frontend: http://localhost:5173
echo   Backend:  http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo.
pause
