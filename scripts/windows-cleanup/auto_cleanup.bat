@echo off
REM EX-AI MCP Server - Automatic Cleanup Batch File
REM This should be run via Task Scheduler to prevent process bloat
REM Recommended: Run daily at 2 AM

echo.
echo ╔════════════════════════════════════════════════════╗
echo ║     EX-AI MCP Server - Automatic Cleanup           ║
echo ╚════════════════════════════════════════════════════╝
echo.
echo Starting cleanup at %DATE% %TIME%...
echo.

REM Change to script directory
cd /d "%~dp0"

REM Run the cleanup script
powershell -ExecutionPolicy Bypass -File "cleanup_all_fixed.ps1" -ProcessHoursOld 2 -SnapshotDaysOld 7

REM Capture exit code
set EXIT_CODE=%ERRORLEVEL%

echo.
if %EXIT_CODE% equ 0 (
    echo ✓ Cleanup completed successfully
) else (
    echo ✗ Cleanup completed with errors (exit code: %EXIT_CODE%)
)

echo.
echo Cleanup finished at %DATE% %TIME%
echo.

exit /b %EXIT_CODE%
