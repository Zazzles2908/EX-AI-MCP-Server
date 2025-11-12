@echo off
REM This script sets environment variables and starts Claude Code
REM Run this to start Claude Code with all MCP servers properly configured

echo Starting Claude Code with Supabase MCP...
echo.
echo Loading environment variables...

REM Load environment variables from .env file
for /f "usebackq tokens=1,2 delims==" %%i in ("C:\Project\EX-AI-MCP-Server\.env") do (
    if not "%%i"=="" (
        if not "%%i:~0,1"=="#" (
            set "%%i=%%j"
        )
    )
)

REM Set the SUPABASE_ACCESS_TOKEN specifically (already set by setx, but ensuring it's available)
if "%SUPABASE_ACCESS_TOKEN%"=="" (
    set SUPABASE_ACCESS_TOKEN=sbp_ebdcf0465cfac2f3354e815f35818b7f1cef4625
)

echo Environment variables loaded.
echo Starting Claude Code...
echo.
echo After Claude Code starts, try:
echo   @supabase-mcp-full list_projects
echo.

REM Start Claude Code (adjust path as needed)
start "" "C:\Users\Jazeel-Home\AppData\Local\Programs\Microsoft VS Code\Code.exe" "C:\Project\EX-AI-MCP-Server"

echo Claude Code has been started!
pause
