@echo off
REM Supabase MCP Configuration Verification Script
REM Run this to verify everything is set up correctly

echo ========================================
echo Supabase MCP Configuration Verification
echo ========================================
echo.

echo [1/5] Checking .env file...
if exist .env (
    echo [OK] .env file exists
    for /f "tokens=1,2 delims==" %%i in (.env) do (
        if "%%i"=="SUPABASE_ACCESS_TOKEN" (
            echo [OK] SUPABASE_ACCESS_TOKEN found in .env
            set "TOKEN_FOUND=1"
        )
    )
    if not defined TOKEN_FOUND (
        echo [FAIL] SUPABASE_ACCESS_TOKEN not found in .env
        goto :end
    )
) else (
    echo [FAIL] .env file not found
    goto :end
)

echo.
echo [2/5] Checking .mcp.json files...
if exist .mcp.json (
    echo [OK] .mcp.json exists
) else (
    echo [FAIL] .mcp.json not found
    goto :end
)

if exist .claude\.mcp.json (
    echo [OK] .claude/.mcp.json exists
) else (
    echo [FAIL] .claude/.mcp.json not found
    goto :end
)

echo.
echo [3/5] Checking wrapper script...
if exist scripts\load_env_and_run_supabase_mcp.py (
    echo [OK] Wrapper script exists
) else (
    echo [FAIL] Wrapper script not found
    goto :end
)

echo.
echo [4/5] Checking .gitignore...
findstr /C:".mcp.json" .gitignore >nul
if %errorlevel%==0 (
    echo [OK] .mcp.json is in .gitignore
) else (
    echo [WARN] .mcp.json may not be in .gitignore
)

echo.
echo [5/5] Testing Supabase MCP server...
echo Starting Supabase MCP server (will timeout in 5 seconds)...
timeout /t 2 /nobreak >nul
python scripts\load_env_and_run_supabase_mcp.py 2>&1 | findstr /C:"Please provide" /C:"access token" >nul
if %errorlevel%==0 (
    echo [OK] Supabase MCP server is ready
) else (
    echo [WARN] Could not verify MCP server
)

echo.
echo ========================================
echo Verification Complete!
echo ========================================
echo.
echo Next Steps:
echo 1. Restart Claude Code
echo 2. Try: @supabase-mcp-full list_projects
echo.
echo Documentation:
echo - SUPABASE_MCP_FINAL_FIX.md
echo - SUPABASE_MCP_SETUP_GUIDE.md
echo.

:end
pause
