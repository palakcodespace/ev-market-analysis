@echo off
title Electric Vehicle Market Analysis and Intelligence System
color 0B
echo ======================================================================
echo    Electric Vehicle Market Analysis and Intelligence System
echo    Skill Wallet Capstone Project Launcher
echo ======================================================================
echo.

:: Detect Python
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python was not found in your system PATH!
    echo Please install Python 3.11+ or add Python to your PATH.
    pause
    exit /b 1
)

:: Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo [INFO] Activating virtual environment...
    call venv\Scripts\activate.bat
)

:: Verify database exists
if not exist "database\ev_market_db.sqlite" (
    echo [INFO] Database not detected. Initializing database and data pipeline...
    python database\seed_or_import.py
)

echo [INFO] Starting Flask web server...
echo [INFO] Application will open at: http://127.0.0.1:5000
echo.

:: Open browser after 2 seconds in background
start "" timeout /t 2 /nobreak >nul & start http://127.0.0.1:5000

:: Run the application
python app.py

pause
