@echo off
REM Veleron Voice Flow Launcher
REM Double-click this file to start Veleron Voice Flow

echo ============================================================
echo Starting Veleron Voice Flow
echo ============================================================
echo.

cd /d "%~dp0"
py veleron_voice_flow.py

REM If Python fails, try with 'python' command
if errorlevel 1 (
    echo.
    echo Trying with 'python' command...
    python veleron_voice_flow.py
)

REM If both fail, show error
if errorlevel 1 (
    echo.
    echo ERROR: Could not start application.
    echo Please ensure Python is installed and in your PATH.
    echo.
    pause
)
