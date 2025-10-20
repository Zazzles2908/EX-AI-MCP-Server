# Cleanup all EXAI MCP Server processes
# This script kills all daemon and shim processes to ensure clean restart

Write-Host "🧹 Cleaning up EXAI MCP Server processes..." -ForegroundColor Cyan

# Kill all ws_daemon processes
$daemonProcesses = Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    $cmdLine = (Get-WmiObject Win32_Process -Filter "ProcessId = $($_.Id)" -ErrorAction SilentlyContinue).CommandLine
    $cmdLine -like "*run_ws_daemon.py*"
}

if ($daemonProcesses) {
    Write-Host "Found $($daemonProcesses.Count) daemon process(es)" -ForegroundColor Yellow
    foreach ($proc in $daemonProcesses) {
        Write-Host "  Killing daemon PID $($proc.Id)..." -ForegroundColor Yellow
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
    }
} else {
    Write-Host "No daemon processes found" -ForegroundColor Green
}

# Kill all ws_shim processes
$shimProcesses = Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    $cmdLine = (Get-WmiObject Win32_Process -Filter "ProcessId = $($_.Id)" -ErrorAction SilentlyContinue).CommandLine
    $cmdLine -like "*run_ws_shim.py*"
}

if ($shimProcesses) {
    Write-Host "Found $($shimProcesses.Count) shim process(es)" -ForegroundColor Yellow
    foreach ($proc in $shimProcesses) {
        Write-Host "  Killing shim PID $($proc.Id)..." -ForegroundColor Yellow
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
    }
} else {
    Write-Host "No shim processes found" -ForegroundColor Green
}

# Wait for processes to terminate
Start-Sleep -Seconds 2

# Clean up stale PID files
$pidFiles = @(
    "logs\ws_daemon.pid",
    "logs\ws_shim.pid"
)

foreach ($pidFile in $pidFiles) {
    if (Test-Path $pidFile) {
        Write-Host "Removing stale PID file: $pidFile" -ForegroundColor Yellow
        Remove-Item $pidFile -Force -ErrorAction SilentlyContinue
    }
}

Write-Host "✅ Cleanup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "You can now restart the server with:" -ForegroundColor Cyan
Write-Host "  powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\ws_start.ps1 -Restart" -ForegroundColor White

