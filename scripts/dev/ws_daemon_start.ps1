# Start WebSocket Daemon in Background
# This script starts the daemon as a detached background process
# Use this for production/persistent daemon operation

param(
  [switch]$Restart
)

$ErrorActionPreference = "Stop"

# Resolve repo root
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Root = (Resolve-Path (Join-Path $ScriptDir "..")).Path
$Py = Join-Path $Root ".venv\Scripts\python.exe"
$DaemonScript = Join-Path $Root "scripts\ws\run_ws_daemon.py"
$StopScript = Join-Path $Root "scripts\ws_stop.ps1"
$LogFile = Join-Path $Root "logs\ws_daemon_startup.log"

# Ensure logs directory exists
$LogDir = Join-Path $Root "logs"
if (!(Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

if (!(Test-Path $Py)) {
    throw "Python not found at $Py. Ensure the virtualenv exists."
}

if ($Restart) {
    Write-Host "Restart requested: stopping any running daemon..." -ForegroundColor Yellow
    powershell -ExecutionPolicy Bypass -File $StopScript | Write-Host
    Start-Sleep -Seconds 1
}

Write-Host "Starting WS daemon in background..." -ForegroundColor Cyan

# Start daemon as detached background process
$processInfo = New-Object System.Diagnostics.ProcessStartInfo
$processInfo.FileName = $Py
$processInfo.Arguments = "-u `"$DaemonScript`""
$processInfo.WorkingDirectory = $Root
$processInfo.UseShellExecute = $false
$processInfo.RedirectStandardOutput = $true
$processInfo.RedirectStandardError = $true
$processInfo.CreateNoWindow = $true

$process = New-Object System.Diagnostics.Process
$process.StartInfo = $processInfo

# Start the process
$started = $process.Start()

if ($started) {
    $daemonPid = $process.Id
    Write-Host "✅ Daemon started successfully (PID: $daemonPid)" -ForegroundColor Green
    Write-Host "   Logs: logs\ws_daemon.log" -ForegroundColor Gray
    Write-Host "   Health: logs\ws_daemon.health.json" -ForegroundColor Gray
    Write-Host ""
    Write-Host "To stop the daemon:" -ForegroundColor Cyan
    Write-Host "  powershell -ExecutionPolicy Bypass -File .\scripts\ws_stop.ps1" -ForegroundColor Gray

    # Wait a moment for daemon to initialize
    Start-Sleep -Seconds 2

    # Check if daemon is still running
    try {
        $runningProcess = Get-Process -Id $daemonPid -ErrorAction SilentlyContinue
        if ($runningProcess) {
            Write-Host ""
            Write-Host "✅ Daemon is running and healthy" -ForegroundColor Green
        } else {
            Write-Host ""
            Write-Host "⚠️  Warning: Daemon process exited immediately" -ForegroundColor Yellow
            Write-Host "   Check logs\ws_daemon.log for errors" -ForegroundColor Yellow
            exit 1
        }
    } catch {
        Write-Host ""
        Write-Host "⚠️  Warning: Could not verify daemon status" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ Failed to start daemon" -ForegroundColor Red
    exit 1
}

