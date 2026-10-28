@echo off
title Push EV Market Analysis to GitHub
color 0A
echo ======================================================================
echo    Pushing Electric Vehicle Market Intelligence System to GitHub
echo    Target: https://github.com/palakcodespace/ev-market-analysis.git
echo ======================================================================
echo.

:: Ensure in correct directory
cd /d "%~dp0"

:: Check git command
where git >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    if exist "C:\Program Files\Git\cmd\git.exe" (
        set "GIT_EXE=C:\Program Files\Git\cmd\git.exe"
    ) else (
        echo [ERROR] Git was not found in PATH or standard installation path.
        echo Please ensure Git is installed.
        pause
        exit /b 1
    )
) else (
    set "GIT_EXE=git"
)

echo [1/3] Checking current branch status...
"%GIT_EXE%" branch -M main

echo.
echo [2/3] Adding any remaining updates...
"%GIT_EXE%" add .
"%GIT_EXE%" commit -m "Complete EV Market Analysis and Intelligence Platform" >nul 2>&1

echo.
echo [3/3] Pushing to GitHub (origin main)...
echo If prompted, authorize in your browser window...
echo.
"%GIT_EXE%" push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ======================================================================
    echo  SUCCESS! Your project has been deployed to GitHub!
    echo  View it online at: https://github.com/palakcodespace/ev-market-analysis
    echo ======================================================================
) else (
    echo.
    echo [NOTICE] Push encountered a prompt or error.
    echo If GitHub requested credentials, please authenticate using Git Credential Manager or Personal Access Token.
)

echo.
pause
