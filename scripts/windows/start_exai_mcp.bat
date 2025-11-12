@echo off
REM Safe startup script for EX-AI MCP WebSocket Shim
REM Ensures clean startup by killing orphaned processes

echo ========================================
echo EX-AI MCP Safe Startup
echo ========================================

cd /d "C:\Project\EX-AI-MCP-Server"

REM Kill any orphaned shims first
echo Cleaning up orphaned processes...
C:\Project\EX-AI-MCP-Server\.venv\Scripts\python.exe scripts\runtime\cleanup_orphaned_shims.py

REM Start the safe wrapper
echo Starting WebSocket Shim...
C:\Project\EX-AI-MCP-Server\.venv\Scripts\python.exe scripts\runtime\start_ws_shim_safe.py

pause
