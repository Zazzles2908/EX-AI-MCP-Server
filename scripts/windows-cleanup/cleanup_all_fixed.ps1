# EX-AI MCP Server - Comprehensive Cleanup Script
# Removes both stale processes AND old shell snapshots

param(
    [Parameter(Mandatory=$false)]
    [int]$ProcessHoursOld = 2,

    [Parameter(Mandatory=$false)]
    [int]$SnapshotDaysOld = 7,

    [Parameter(Mandatory=$false)]
    [switch]$DryRun = $false,

    [Parameter(Mandatory=$false)]
    [switch]$SkipSnapshots = $false
)

$ErrorActionPreference = "Stop"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "     EX-AI MCP Server - Comprehensive Cleanup       " -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Write-Host ""
Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host "  Process threshold: $ProcessHoursOld hours" -ForegroundColor White
Write-Host "  Snapshot threshold: $SnapshotDaysOld days" -ForegroundColor White
Write-Host "  Dry run: $DryRun" -ForegroundColor White
Write-Host "  Skip snapshots: $SkipSnapshots" -ForegroundColor White
Write-Host ""

# ====================
# CLEANUP PROCESSES
# ====================
Write-Host "=== PHASE 1: Cleaning Up Stale Processes ===" -ForegroundColor Cyan
Write-Host ""

$threshold = (Get-Date).AddHours(-$ProcessHoursOld)
$removedProcesses = 0
$keptProcesses = 0
$errorProcesses = 0

$processes = Get-Process | Where-Object {
    $_.ProcessName -match "bash|cmd|node|python"
} | Sort-Object StartTime

Write-Host "Total processes found: " $processes.Count "" -ForegroundColor Yellow
Write-Host ""

foreach ($proc in $processes) {
    $ageMinutes = [math]::Round(((Get-Date) - $proc.StartTime).TotalMinutes, 1)

    if ($proc.StartTime -lt $threshold) {
        # Process is stale
        if ($DryRun) {
            $msg = "[DRY RUN] Would kill PID " + $proc.Id + " | " + $proc.ProcessName + " | Age: " + $ageMinutes + " min"
            Write-Host $msg -ForegroundColor Red
            $removedProcesses++
        } else {
            try {
                $msg = "Killing PID " + $proc.Id + " | " + $proc.ProcessName + " | Age: " + $ageMinutes + " min..."
                Write-Host $msg -ForegroundColor Red -NoNewline

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
                    $removedProcesses++
                } else {
                    Write-Host " [FAILED]" -ForegroundColor Red
                    $errorProcesses++
                }
            } catch {
                Write-Host " [ERROR: $($_.Exception.Message)]" -ForegroundColor Red
                $errorProcesses++
            }
        }
    } else {
        # Process is active
        $keptProcesses++
    }
}

Write-Host ""
Write-Host "Process Cleanup Summary:" -ForegroundColor Cyan
Write-Host "  Removed: $removedProcesses processes" -ForegroundColor Green
Write-Host "  Kept: $keptProcesses processes" -ForegroundColor Yellow
Write-Host "  Errors: $errorProcesses processes" -ForegroundColor Red
Write-Host ""

# ====================
# CLEANUP SNAPSHOTS
# ====================
if (-not $SkipSnapshots) {
    Write-Host "=== PHASE 2: Cleaning Up Shell Snapshots ===" -ForegroundColor Cyan
    Write-Host ""

    $threshold = (Get-Date).AddDays(-$SnapshotDaysOld)
    $snapshotDir = "$env:USERPROFILE\.claude\shell-snapshots"

    if (-not (Test-Path $snapshotDir)) {
        Write-Host "Snapshot directory not found: $snapshotDir" -ForegroundColor Yellow
        $keptSnapshots = 0
        $removedSnapshots = 0
        $totalSize = 0
    } else {
        $snapshots = Get-ChildItem -Path $snapshotDir -Filter "*.sh" | Sort-Object LastWriteTime
        Write-Host "Total snapshots found: " $snapshots.Count "" -ForegroundColor Yellow
        Write-Host ""

        $removedSnapshots = 0
        $keptSnapshots = 0
        $totalSize = 0

        foreach ($snap in $snapshots) {
            if ($snap.LastWriteTime -lt $threshold) {
                # Snapshot is old
                $totalSize += $snap.Length

                if ($DryRun) {
                    $msg = "[DRY RUN] Would delete " + $snap.Name
                    Write-Host $msg -ForegroundColor Red
                    $removedSnapshots++
                } else {
                    try {
                        $msg = "Deleting " + $snap.Name + "..."
                        Write-Host $msg -ForegroundColor Red -NoNewline
                        Remove-Item -Path $snap.FullName -Force

                        if (-not (Test-Path $snap.FullName)) {
                            Write-Host " [SUCCESS]" -ForegroundColor Green
                            $removedSnapshots++
                        } else {
                            Write-Host " [FAILED]" -ForegroundColor Red
                        }
                    } catch {
                        Write-Host " [ERROR: $($_.Exception.Message)]" -ForegroundColor Red
                    }
                }
            } else {
                # Snapshot is recent
                $keptSnapshots++
            }
        }

        $totalSizeMB = [math]::Round($totalSize / 1KB, 2)
    }

    Write-Host ""
    Write-Host "Snapshot Cleanup Summary:" -ForegroundColor Cyan
    Write-Host "  Removed: $removedSnapshots snapshots" -ForegroundColor Green
    Write-Host "  Kept: $keptSnapshots snapshots" -ForegroundColor Yellow
    if ($totalSize -gt 0) {
        Write-Host "  Disk space freed: $totalSizeMB KB" -ForegroundColor Cyan
    }
    Write-Host ""
} else {
    Write-Host "=== PHASE 2: Skipping Shell Snapshots ===" -ForegroundColor Yellow
    Write-Host ""
    $removedSnapshots = 0
    $keptSnapshots = 0
}

# ====================
# FINAL SUMMARY
# ====================
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "              CLEANUP COMPLETE                       " -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Summary:" -ForegroundColor Yellow
Write-Host "  Processes removed: $removedProcesses" -ForegroundColor Green
Write-Host "  Snapshots removed: $removedSnapshots" -ForegroundColor Green
Write-Host "  Active processes: $keptProcesses" -ForegroundColor Yellow
Write-Host "  Recent snapshots: $keptSnapshots" -ForegroundColor Yellow
Write-Host ""

if (-not $DryRun -and ($removedProcesses -gt 0 -or $removedSnapshots -gt 0)) {
    Write-Host "Resources freed:" -ForegroundColor Cyan
    $ramFreed = [math]::Round(($removedProcesses * 30) / 1024, 2)
    Write-Host "  RAM: ~$ramFreed GB" -ForegroundColor White
    Write-Host "  File handles: ~$($removedProcesses * 40)" -ForegroundColor White
    Write-Host "  Disk space: ~$([math]::Round($totalSize / 1KB, 2)) KB" -ForegroundColor White
    Write-Host ""
}

Write-Host "Tip: Run this script periodically to prevent bloat!" -ForegroundColor Green
Write-Host ""

# Exit with appropriate code
if ($errorProcesses -gt 0) {
    exit 1
} else {
    exit 0
}
