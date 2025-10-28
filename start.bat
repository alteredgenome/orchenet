@echo off
REM OrcheNet Startup Script (Windows)
REM Starts both backend and frontend in development mode

echo ========================================
echo   OrcheNet Startup Script
echo ========================================
echo.

REM Check if running in correct directory
if not exist "backend\" (
    echo Error: backend directory not found
    echo Please run this script from the orchenet root directory
    pause
    exit /b 1
)

if not exist "frontend\" (
    echo Error: frontend directory not found
    echo Please run this script from the orchenet root directory
    pause
    exit /b 1
)

REM Check prerequisites
echo Checking prerequisites...

where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)
echo * Python found

where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Node.js is not installed or not in PATH
    pause
    exit /b 1
)
echo * Node.js found

where npm >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: npm is not installed or not in PATH
    pause
    exit /b 1
)
echo * npm found

echo.

REM Setup backend
echo Setting up backend...
cd backend

REM Create virtual environment if it doesn't exist
if not exist "venv\" (
    echo Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment and install dependencies
echo Installing Python dependencies...
call venv\Scripts\activate.bat
pip install -q -r requirements.txt

REM Check for .env file
if not exist ".env" (
    echo Creating .env file from template...
    copy .env.example .env
    echo WARNING: Please edit backend\.env with your configuration
)

REM Initialize database
echo Initializing database...
python init_db.py

cd ..
echo * Backend setup complete
echo.

REM Setup frontend
echo Setting up frontend...
cd frontend

REM Install dependencies
if not exist "node_modules\" (
    echo Installing Node.js dependencies...
    call npm install
)

REM Check for .env file
if not exist ".env" (
    echo Creating .env file from template...
    copy .env.example .env
)

cd ..
echo * Frontend setup complete
echo.

REM Start services
echo ========================================
echo   Starting Services
echo ========================================
echo.

REM Start backend
echo Starting backend server...
cd backend
start "OrcheNet Backend" cmd /k "call venv\Scripts\activate.bat && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
cd ..
echo * Backend started
echo   API: http://localhost:8000
echo   Docs: http://localhost:8000/docs
echo.

REM Wait for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend
echo Starting frontend server...
cd frontend
start "OrcheNet Frontend" cmd /k "npm run dev"
cd ..
echo * Frontend started
echo   URL: http://localhost:5173
echo.

echo ========================================
echo   OrcheNet is running!
echo ========================================
echo.
echo   Frontend: http://localhost:5173
echo   Backend API: http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo.
echo   Close the backend and frontend windows to stop
echo.
pause
