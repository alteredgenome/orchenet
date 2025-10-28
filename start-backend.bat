@echo off
REM Start OrcheNet Backend Only

cd backend

if not exist "venv\" (
    echo ERROR: Virtual environment not found!
    echo Please run start.bat first to set up the environment.
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Starting backend server...
echo.
echo Backend will be available at:
echo   API: http://localhost:8000
echo   Docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
