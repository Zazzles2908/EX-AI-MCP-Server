# EX-AI MCP Server - Process Cleanup Script
# Removes stale processes older than the specified time threshold

param(
    [Parameter(Mandatory=$false)]
    [int]$HoursOld = 2,

    [Parameter(Mandatory=$false)]
    [switch]$DryRun = $false
)

$ErrorActionPreference = "Stop"

Write-Host "=== EX-AI MCP Process Cleanup ===`n" -ForegroundColor Cyan
Write-Host "Threshold: Processes older than $HoursOld hours`n" -ForegroundColor Yellow

$threshold = (Get-Date).AddHours(-$HoursOld)
$removedCount = 0
$errorCount = 0
$keepCount = 0

# Get all relevant processes
$processes = Get-Process | Where-Object {
    $_.ProcessName -match "bash|cmd|node|python"
} | Sort-Object StartTime

Write-Host "Total processes found: $($processes.Count)`n" -ForegroundColor Yellow

foreach ($proc in $processes) {
    $ageMinutes = [math]::Round(((Get-Date) - $proc.StartTime).TotalMinutes, 1)

    if ($proc.StartTime -lt $threshold) {
        # Process is stale
        if ($DryRun) {
            Write-Host "[DRY RUN] Would kill PID $($proc.Id) | $($proc.ProcessName) | Age: $ageMinutes min" -ForegroundColor Red
            $removedCount++
        } else {
            try {
                Write-Host "Killing PID $($proc.Id) | $($proc.ProcessName) | Age: $ageMinutes min..." -ForegroundColor Red -NoNewline

                # Try graceful shutdown first
                $proc.CloseMainWindow()
                Start-Sleep -Milliseconds 500

                # Force kill if still running
                if (!$proc.HasExited) {
                    $proc.Kill()
                    Start-Sleep -Milliseconds 500
                }

                if ($proc.HasExited) {
                    Write-Host " [SUCCESS]" -ForegroundColor Green
                    $removedCount++
                } else {
                    Write-Host " [FAILED - Still running]" -ForegroundColor Red
                    $errorCount++
                }
            } catch {
                Write-Host " [ERROR: $($_.Exception.Message)]" -ForegroundColor Red
                $errorCount++
            }
        }
    } else {
        # Process is active, keep it
        $keepCount++
    }
}

Write-Host "`n=== CLEANUP COMPLETE ===" -ForegroundColor Cyan
Write-Host "Processes removed: $removedCount" -ForegroundColor Green
Write-Host "Processes kept: $keepCount" -ForegroundColor Yellow
Write-Host "Errors: $errorCount" -ForegroundColor Red

if (-not $DryRun) {
    Write-Host "`nEstimated resources freed:" -ForegroundColor Cyan
    Write-Host "- RAM: ~$(($removedCount * 30) / 1024) GB" -ForegroundColor White
    Write-Host "- File handles: ~$($removedCount * 40)" -ForegroundColor White
}
