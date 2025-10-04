# Force Restart Script - Kills all Python processes and restarts daemon
# Use this when .env changes aren't being picked up

$ErrorActionPreference = "Stop"

Write-Host "=== FORCE RESTART ===" -ForegroundColor Cyan
Write-Host "This will kill ALL Python processes and restart the daemon" -ForegroundColor Yellow
Write-Host ""

# Resolve repo root
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Root = (Resolve-Path (Join-Path $ScriptDir "..")).Path
$WsPort = 8765

Write-Host "Step 1: Stopping WS daemon gracefully..." -ForegroundColor Cyan
try {
    powershell -ExecutionPolicy Bypass -File "$Root\scripts\ws_stop.ps1" -Force | Write-Host
} catch {
    Write-Host "Graceful stop failed: $_" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Step 2: Killing all Python processes..." -ForegroundColor Cyan
try {
    $pythonProcesses = Get-Process python* -ErrorAction SilentlyContinue
    if ($pythonProcesses) {
        $pythonProcesses | ForEach-Object {
            Write-Host "  Killing Python process PID=$($_.Id)" -ForegroundColor Yellow
            Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
        }
        Write-Host "  All Python processes killed" -ForegroundColor Green
    } else {
        Write-Host "  No Python processes found" -ForegroundColor Green
    }
} catch {
    Write-Host "  Error killing Python processes: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "Step 3: Waiting for port to be free..." -ForegroundColor Cyan
$deadline = (Get-Date).AddSeconds(10)
while ((Get-Date) -lt $deadline) {
    try {
        $conn = Get-NetTCPConnection -LocalPort $WsPort -State Listen -ErrorAction SilentlyContinue
        if (-not $conn) {
            Write-Host "  Port $WsPort is free" -ForegroundColor Green
            break
        }
        Write-Host "  Port $WsPort still in use, waiting..." -ForegroundColor Yellow
        Start-Sleep -Milliseconds 500
    } catch {
        Write-Host "  Port $WsPort is free" -ForegroundColor Green
        break
    }
}

Write-Host ""
Write-Host "Step 4: Cleaning up PID and health files..." -ForegroundColor Cyan
try {
    $pidFile = Join-Path $Root "logs\ws_daemon.pid"
    $healthFile = Join-Path $Root "logs\ws_daemon.health.json"
    
    if (Test-Path $pidFile) {
        Remove-Item $pidFile -Force
        Write-Host "  Removed PID file" -ForegroundColor Green
    }
    
    if (Test-Path $healthFile) {
        Remove-Item $healthFile -Force
        Write-Host "  Removed health file" -ForegroundColor Green
    }
} catch {
    Write-Host "  Error cleaning up files: $_" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Step 5: Starting WS daemon..." -ForegroundColor Cyan
try {
    Push-Location $Root
    powershell -ExecutionPolicy Bypass -File "$Root\scripts\ws_start.ps1" | Write-Host
    Pop-Location
} catch {
    Write-Host "Error starting daemon: $_" -ForegroundColor Red
    Pop-Location
    exit 1
}

Write-Host ""
Write-Host "=== FORCE RESTART COMPLETE ===" -ForegroundColor Green
Write-Host "The daemon should now be running with fresh configuration" -ForegroundColor Green

