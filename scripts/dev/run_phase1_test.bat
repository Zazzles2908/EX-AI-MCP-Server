@echo off
REM Phase 1 Verification Test Runner
REM Run this to test the emergency fixes

echo.
echo ========================================
echo   PHASE 1 VERIFICATION TEST
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

REM Check if websockets is installed
python -c "import websockets" >nul 2>&1
if errorlevel 1 (
    echo Installing websockets package...
    pip install websockets
)

REM Run the test
echo Running Phase 1 verification tests...
echo.
python tests\phase1_verification_test.py

echo.
echo ========================================
echo   TEST COMPLETE
echo ========================================
echo.
echo To check Docker logs for cache behavior:
echo   docker-compose logs -f ^| findstr REQUEST_CACHE
echo.
pause

