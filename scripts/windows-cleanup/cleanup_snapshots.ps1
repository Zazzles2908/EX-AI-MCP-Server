# EX-AI MCP Server - Shell Snapshot Cleanup Script
# Removes old Claude Code shell snapshot files

param(
    [Parameter(Mandatory=$false)]
    [int]$DaysOld = 7,

    [Parameter(Mandatory=$false)]
    [switch]$DryRun = $false
)

$ErrorActionPreference = "Stop"

Write-Host "=== EX-AI MCP Shell Snapshot Cleanup ===`n" -ForegroundColor Cyan
Write-Host "Threshold: Snapshots older than $DaysOld days`n" -ForegroundColor Yellow

$threshold = (Get-Date).AddDays(-$DaysOld)
$snapshotDir = "$env:USERPROFILE\.claude\shell-snapshots"

if (-not (Test-Path $snapshotDir)) {
    Write-Host "Snapshot directory not found: $snapshotDir" -ForegroundColor Red
    exit 1
}

Write-Host "Snapshot directory: $snapshotDir`n" -ForegroundColor Yellow

# Get all snapshot files
$snapshots = Get-ChildItem -Path $snapshotDir -Filter "*.sh" | Sort-Object LastWriteTime

Write-Host "Total snapshots found: $($snapshots.Count)`n" -ForegroundColor Yellow

$removedCount = 0
$keepCount = 0
$totalSize = 0

foreach ($snap in $snapshots) {
    if ($snap.LastWriteTime -lt $threshold) {
        # Snapshot is old
        $sizeMB = [math]::Round($snap.Length / 1KB, 2)
        $totalSize += $snap.Length

        if ($DryRun) {
            Write-Host "[DRY RUN] Would delete $($snap.Name) | Size: $sizeMB KB | Age: $([math]::Round(((Get-Date) - $snap.LastWriteTime).TotalDays, 1)) days" -ForegroundColor Red
            $removedCount++
        } else {
            try {
                Write-Host "Deleting $($snap.Name) | Size: $sizeMB KB..." -ForegroundColor Red -NoNewline
                Remove-Item -Path $snap.FullName -Force

                if (-not (Test-Path $snap.FullName)) {
                    Write-Host " [SUCCESS]" -ForegroundColor Green
                    $removedCount++
                } else {
                    Write-Host " [FAILED - Still exists]" -ForegroundColor Red
                }
            } catch {
                Write-Host " [ERROR: $($_.Exception.Message)]" -ForegroundColor Red
            }
        }
    } else {
        # Snapshot is recent, keep it
        $keepCount++
    }
}

$totalSizeMB = [math]::Round($totalSize / 1KB, 2)

Write-Host "`n=== CLEANUP COMPLETE ===" -ForegroundColor Cyan
Write-Host "Snapshots removed: $removedCount" -ForegroundColor Green
Write-Host "Snapshots kept: $keepCount" -ForegroundColor Yellow
Write-Host "Disk space freed: $totalSizeMB KB" -ForegroundColor Cyan

if ($removedCount -gt 0) {
    Write-Host "`nSnapshot bloat prevented!" -ForegroundColor Green
    Write-Host "Before: $($snapshots.Count) snapshots" -ForegroundColor White
    Write-Host "After: $($snapshots.Count - $removedCount) snapshots" -ForegroundColor White
    Write-Host "Reduction: $([math]::Round(($removedCount / $snapshots.Count) * 100, 1))%" -ForegroundColor Cyan
}
