param(
  [switch]$Force
)

$ErrorActionPreference = "Stop"

# Resolve repo root
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Root = (Resolve-Path (Join-Path $ScriptDir "..")).Path
$PidFile = Join-Path $Root "logs\ws_daemon.pid"
$HealthFile = Join-Path $Root "logs\ws_daemon.health.json"
$WsHost = $env:EXAI_WS_HOST; if ([string]::IsNullOrWhiteSpace($WsHost)) { $WsHost = "127.0.0.1" }
$WsPort = $env:EXAI_WS_PORT; if ([string]::IsNullOrWhiteSpace($WsPort)) { $WsPort = 8765 } else { $WsPort = [int]$WsPort }

function Test-Listening {
  try {
    $conn = Get-NetTCPConnection -LocalPort $WsPort -State Listen -ErrorAction SilentlyContinue
    return $null -ne $conn
  } catch { return $false }
}

function Stop-ByPid($DaemonPid) {
  if (-not $DaemonPid) { return }
  try { Stop-Process -Id $DaemonPid -ErrorAction SilentlyContinue } catch {}
  if ($Force) { try { taskkill /PID $DaemonPid /T /F | Out-Null } catch {} }
}

# Determine PID from health if available
$DaemonPid = $null
if (Test-Path $HealthFile) {
  try {
    $json = Get-Content $HealthFile -Raw | ConvertFrom-Json
    $DaemonPid = $json.pid
  } catch {}
}

# Fallback: owning process of listening port
if (-not $DaemonPid) {
  try {
    $conn = Get-NetTCPConnection -LocalPort $WsPort -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($conn) { $DaemonPid = $conn.OwningProcess }
  } catch {}
}

if ($DaemonPid) {
  Write-Host "Stopping WS daemon (PID=$DaemonPid)..." -ForegroundColor Yellow
  Stop-ByPid $DaemonPid
} else {
  Write-Host "No daemon PID found; ensuring port is free..." -ForegroundColor Yellow
}

# Stop all shim processes to prevent orphaned shims from respawning daemon
Write-Host "Stopping all shim processes..." -ForegroundColor Yellow
$shimCount = 0
Get-Process python -ErrorAction SilentlyContinue | ForEach-Object {
  try {
    $cmdLine = (Get-WmiObject Win32_Process -Filter "ProcessId = $($_.Id)" -ErrorAction SilentlyContinue).CommandLine
    if ($cmdLine -like "*run_ws_shim.py*") {
      Write-Host "  Killing shim PID $($_.Id)..." -ForegroundColor Yellow
      Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
      $shimCount++
    }
  } catch {}
}
if ($shimCount -gt 0) {
  Write-Host "Stopped $shimCount shim process(es)." -ForegroundColor Green
} else {
  Write-Host "No shim processes found." -ForegroundColor Gray
}

# Wait for port to close (up to 8s)
$deadline = (Get-Date).AddSeconds(8)
while (Test-Listening) {
  if ((Get-Date) -gt $deadline) { break }
  Start-Sleep -Milliseconds 250
}

# Remove stale PID file if present
if (Test-Path $PidFile) {
  try { Remove-Item $PidFile -Force -ErrorAction SilentlyContinue } catch {}
}

if (Test-Listening) {
  Write-Host ("Warning: Port {0}:{1} still listening after stop attempt." -f $WsHost, $WsPort) -ForegroundColor Red
  exit 1
} else {
  Write-Host "WS daemon stopped (port free)." -ForegroundColor Green
  exit 0
}

