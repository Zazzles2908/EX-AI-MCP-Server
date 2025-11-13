# Windows Cleanup Scripts

This directory contains automated cleanup scripts to prevent process bloat and orphaned processes in the EX-AI MCP Server environment.

## Location

```
C:\Project\EX-AI-MCP-Server\scripts\windows-cleanup\
```

## Scripts

### 1. cleanup_all_fixed.ps1 (Recommended)
**Comprehensive cleanup - removes both stale processes AND old shell snapshots**

```powershell
cd C:\Project\EX-AI-MCP-Server\scripts\windows-cleanup
powershell -ExecutionPolicy Bypass -File "cleanup_all_fixed.ps1"
```

**Options**:
```powershell
# Custom thresholds
.\cleanup_all_fixed.ps1 -ProcessHoursOld 1 -SnapshotDaysOld 3

# Dry run (preview only)
.\cleanup_all_fixed.ps1 -DryRun

# Process cleanup only
.\cleanup_all_fixed.ps1 -SkipSnapshots
```

### 2. cleanup_processes.ps1
**Removes only stale processes**

```powershell
.\cleanup_processes.ps1 -HoursOld 2
```

### 3. cleanup_snapshots.ps1
**Removes only old shell snapshots**

```powershell
.\cleanup_snapshots.ps1 -DaysOld 7
```

### 4. auto_cleanup.bat
**Batch file for Task Scheduler (daily automation)**

```powershell
.\auto_cleanup.bat
```

## Usage

### Manual Cleanup

```powershell
# Navigate to script directory
cd C:\Project\EX-AI-MCP-Server\scripts\windows-cleanup

# Run comprehensive cleanup
.\cleanup_all_fixed.ps1

# Or use the batch file
.\auto_cleanup.bat
```

### Scheduled Automation (Recommended)

Set up Task Scheduler to run `auto_cleanup.bat` daily at 2:00 AM:

1. Open **Task Scheduler**
2. Create **Basic Task**
3. **Trigger**: Daily at 2:00 AM
4. **Action**: Start a program
   - Program: `C:\Project\EX-AI-MCP-Server\scripts\windows-cleanup\auto_cleanup.bat`
5. **Finish**

## What Gets Cleaned?

### Processes
- **bash.exe** - Old terminal sessions
- **cmd.exe** - Old command prompts
- **node.exe** - Stale MCP servers and npm processes
- **python.exe** - Old Python scripts and shims

Default: Removes processes older than **2 hours**

### Shell Snapshots
- **Claude Code shell snapshots** - Each bash command creates a snapshot
- These accumulate in `~/.claude/shell-snapshots/`

Default: Removes snapshots older than **7 days**

## Example Output

```
============================================================
     EX-AI MCP Server - Comprehensive Cleanup
============================================================

Configuration:
  Process threshold: 2 hours
  Snapshot threshold: 7 days
  Dry run: False
  Skip snapshots: False

=== PHASE 1: Cleaning Up Stale Processes ===

Total processes found: 80

Process Cleanup Summary:
  Removed: 0 processes
  Kept: 80 processes
  Errors: 0 processes

=== PHASE 2: Cleaning Up Shell Snapshots ===

Total snapshots found: 296

Snapshot Cleanup Summary:
  Removed: 0 snapshots
  Kept: 296 snapshots

============================================================
              CLEANUP COMPLETE
============================================================

Summary:
  Processes removed: 0
  Snapshots removed: 0
  Active processes: 80
  Recent snapshots: 296
```

## Configuration

Edit the scripts to customize thresholds:

```powershell
# In cleanup_all_fixed.ps1
param(
    [int]$ProcessHoursOld = 2,    # Change this (default: 2 hours)
    [int]$SnapshotDaysOld = 7,    # Change this (default: 7 days)
    ...
)
```

## Troubleshooting

### "Execution of scripts is disabled"
```powershell
Set-ExecutionPolicy RemoteSigned
```

### Process won't die
The script tries graceful shutdown first, then force kills.

### Want to preview changes?
```powershell
.\cleanup_all_fixed.ps1 -DryRun
```

## Best Practices

1. **Run before starting development** - Get a clean slate
2. **Schedule daily cleanup** - Use Task Scheduler
3. **Monitor periodically** - Check process count weekly
4. **Keep snapshots for 7 days** - Balance between history and disk space

## Quick Reference

```powershell
# Full cleanup (recommended)
cd C:\Project\EX-AI-MCP-Server\scripts\windows-cleanup
.\cleanup_all_fixed.ps1

# Preview only
.\cleanup_all_fixed.ps1 -DryRun

# Force clean everything
.\cleanup_all_fixed.ps1 -ProcessHoursOld 0
```

## More Information

See `CLEANUP_DOCUMENTATION.md` for detailed information about:
- Root cause analysis
- Technical implementation details
- Docker cleanup service
- Troubleshooting guide
