@echo off
echo ========================================
echo Veleron Dictation Launcher
echo ========================================
echo.
echo Starting real-time voice dictation...
echo.
echo IMPORTANT: This requires Administrator privileges!
echo.
echo Once started:
echo   - Hold Ctrl+Shift+Space to speak
echo   - Release to transcribe and type
echo   - Works in any application!
echo.
echo ========================================
echo.

cd /d "%~dp0"
py veleron_dictation.py

pause
