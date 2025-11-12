@echo off
REM Automated cleanup for orphaned WebSocket shims
REM Can be run via Task Scheduler every 5 minutes

echo [%DATE% %TIME%] WebSocket Shim Cleanup Started

cd /d "C:\Project\EX-AI-MCP-Server"

REM Clean up orphaned shims
C:\Project\EX-AI-MCP-Server\.venv\Scripts\python.exe scripts\runtime\cleanup_orphaned_shims.py

REM Log result
echo [%DATE% %TIME%] Cleanup completed
