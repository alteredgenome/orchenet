@echo off
REM Database Initialization Script
REM Run this from the backend directory to initialize or reset the database

echo ========================================
echo   OrcheNet Database Initialization
echo ========================================
echo.

REM Check if venv exists
if not exist "venv\" (
    echo ERROR: Virtual environment not found!
    echo Please run setup.bat first to create the environment.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check command line arguments
set "SEED_FLAG="
if "%1"=="--seed" set "SEED_FLAG=--seed"
if "%1"=="--drop" set "SEED_FLAG=--drop --seed"

REM Initialize database
echo.
if "%SEED_FLAG%"=="--drop --seed" (
    echo WARNING: This will DROP all existing data!
    echo.
)

python init_db.py %SEED_FLAG%

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   Database initialized successfully!
    echo ========================================
) else (
    echo.
    echo ========================================
    echo   Database initialization FAILED
    echo ========================================
)

echo.
pause
