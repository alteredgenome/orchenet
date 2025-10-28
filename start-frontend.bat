@echo off
REM Start OrcheNet Frontend Only

cd frontend

if not exist "node_modules\" (
    echo ERROR: Node modules not found!
    echo Please run start.bat first to set up the environment.
    pause
    exit /b 1
)

echo Starting frontend server...
echo.
echo Frontend will be available at:
echo   URL: http://localhost:5173
echo.
echo Press Ctrl+C to stop the server
echo.

npm run dev
