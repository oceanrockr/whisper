@echo off
REM Veleron Whisper Voice-to-Text - Test Runner Script
REM Run comprehensive test suite with various options

echo ================================================
echo Veleron Whisper Voice-to-Text - Test Suite
echo ================================================
echo.

REM Check if pytest is installed
python -m pytest --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pytest not found. Installing test dependencies...
    pip install -r requirements-test.txt
    if errorlevel 1 (
        echo ERROR: Failed to install test dependencies
        exit /b 1
    )
)

REM Parse command line arguments
if "%1"=="" goto :run_all
if "%1"=="all" goto :run_all
if "%1"=="unit" goto :run_unit
if "%1"=="integration" goto :run_integration
if "%1"=="coverage" goto :run_coverage
if "%1"=="fast" goto :run_fast
if "%1"=="slow" goto :run_slow
if "%1"=="dictation" goto :run_dictation
if "%1"=="voiceflow" goto :run_voiceflow
if "%1"=="office" goto :run_office
if "%1"=="help" goto :show_help

echo Unknown option: %1
goto :show_help

:run_all
echo Running ALL tests...
python -m pytest
goto :end

:run_unit
echo Running UNIT tests only...
python -m pytest -m "not integration"
goto :end

:run_integration
echo Running INTEGRATION tests only...
python -m pytest -m integration
goto :end

:run_coverage
echo Running tests with COVERAGE report...
python -m pytest --cov=. --cov-report=html --cov-report=term
echo.
echo Coverage report generated in htmlcov\index.html
start htmlcov\index.html
goto :end

:run_fast
echo Running FAST tests only (excluding slow tests)...
python -m pytest -m "not slow"
goto :end

:run_slow
echo Running SLOW tests only...
python -m pytest -m slow
goto :end

:run_dictation
echo Running tests for VELERON DICTATION...
python -m pytest tests\test_veleron_dictation.py -v
goto :end

:run_voiceflow
echo Running tests for VELERON VOICE FLOW...
python -m pytest tests\test_veleron_voice_flow.py -v
goto :end

:run_office
echo Running tests for WHISPER TO OFFICE...
python -m pytest tests\test_whisper_to_office.py -v
goto :end

:show_help
echo.
echo Usage: run_tests.bat [option]
echo.
echo Options:
echo   all           Run all tests (default)
echo   unit          Run unit tests only
echo   integration   Run integration tests only
echo   coverage      Run tests with coverage report
echo   fast          Run fast tests only (exclude slow tests)
echo   slow          Run slow tests only
echo   dictation     Run tests for veleron_dictation.py
echo   voiceflow     Run tests for veleron_voice_flow.py
echo   office        Run tests for whisper_to_office.py
echo   help          Show this help message
echo.
echo Examples:
echo   run_tests.bat              (run all tests)
echo   run_tests.bat coverage     (run with coverage report)
echo   run_tests.bat fast         (run fast tests only)
echo   run_tests.bat dictation    (test dictation module)
echo.
goto :end

:end
echo.
echo ================================================
echo Test execution complete
echo ================================================
