# Redis Backup Script for EXAI MCP Server (PowerShell)
# Date: 2025-10-16
# Description: Creates timestamped backups of Redis data

# Configuration
$BackupDir = ".\backups\redis"
$ContainerName = "exai-redis"
$Date = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupFile = "redis-backup-$Date.rdb"

# Create backup directory if it doesn't exist
if (-not (Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
}

Write-Host "[BACKUP] Starting Redis backup..." -ForegroundColor Yellow

# Trigger background save in Redis
Write-Host "[BACKUP] Triggering BGSAVE in Redis..." -ForegroundColor Yellow
$result = docker exec $ContainerName redis-cli BGSAVE 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to trigger BGSAVE in Redis" -ForegroundColor Red
    Write-Host $result -ForegroundColor Red
    exit 1
}

# Wait for BGSAVE to complete (check every second, max 30 seconds)
Write-Host "[BACKUP] Waiting for BGSAVE to complete..." -ForegroundColor Yellow
$timeout = 30
$elapsed = 0

$lastSave = docker exec $ContainerName redis-cli LASTSAVE
Start-Sleep -Seconds 1

for ($i = 1; $i -le $timeout; $i++) {
    $newSave = docker exec $ContainerName redis-cli LASTSAVE
    
    if ([int]$newSave -gt [int]$lastSave) {
        Write-Host "[BACKUP] BGSAVE completed successfully" -ForegroundColor Green
        break
    }
    
    if ($i -eq $timeout) {
        Write-Host "[ERROR] BGSAVE timeout after $timeout seconds" -ForegroundColor Red
        exit 1
    }
    
    Start-Sleep -Seconds 1
}

# Copy RDB file from container
Write-Host "[BACKUP] Copying RDB file from container..." -ForegroundColor Yellow
$backupPath = Join-Path $BackupDir $BackupFile
docker cp "${ContainerName}:/data/dump.rdb" $backupPath

if ($LASTEXITCODE -eq 0) {
    # Get file size
    $fileSize = (Get-Item $backupPath).Length
    $fileSizeMB = [math]::Round($fileSize / 1MB, 2)
    
    Write-Host "[SUCCESS] Redis backup completed: $BackupFile (Size: $fileSizeMB MB)" -ForegroundColor Green
    Write-Host "[SUCCESS] Backup location: $backupPath" -ForegroundColor Green
    
    # Optional: Keep only last 7 backups
    Write-Host "[CLEANUP] Removing old backups (keeping last 7)..." -ForegroundColor Yellow
    Get-ChildItem -Path $BackupDir -Filter "redis-backup-*.rdb" | 
        Sort-Object LastWriteTime -Descending | 
        Select-Object -Skip 7 | 
        Remove-Item -Force
    
    # List current backups
    Write-Host "[INFO] Current backups:" -ForegroundColor Green
    Get-ChildItem -Path $BackupDir -Filter "redis-backup-*.rdb" | 
        Sort-Object LastWriteTime -Descending | 
        Format-Table Name, @{Label="Size (MB)"; Expression={[math]::Round($_.Length / 1MB, 2)}}, LastWriteTime -AutoSize
} else {
    Write-Host "[ERROR] Failed to copy RDB file from container" -ForegroundColor Red
    exit 1
}

Write-Host "[BACKUP] Backup process completed successfully" -ForegroundColor Green
exit 0

