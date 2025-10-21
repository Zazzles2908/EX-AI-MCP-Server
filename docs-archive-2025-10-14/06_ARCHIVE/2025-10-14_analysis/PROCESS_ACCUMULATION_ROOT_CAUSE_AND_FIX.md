# Process Accumulation - Root Cause Analysis & Fix
**Date:** 2025-10-14
**Status:** ✅ PHASE 1 COMPLETE - Monitoring & Testing Pending
**Priority:** 🔴 CRITICAL

---

## ✅ FIXES IMPLEMENTED (Phase 1)

### 1. Fixed Shim Autostart Path
**File:** `scripts/run_ws_shim.py` line 146
**Change:** `scripts/run_ws_daemon.py` → `scripts/ws/run_ws_daemon.py`
**Impact:** Shim autostart now uses correct daemon path, preventing launch failures

### 2. Enhanced Process Cleanup
**File:** `scripts/ws_stop.ps1`
**Added:** Shim process cleanup after daemon stop
**Impact:** Prevents orphaned shims from respawning daemons via autostart

### 3. Automatic Cleanup on Start
**Existing:** `ws_start.ps1` already calls `ws_stop.ps1` before starting
**Result:** Enhanced cleanup runs automatically on every restart

---

## 🎯 Executive Summary

**Problem:** Random EXAI glitches where WebSocket connection refused on port 8079.

**Root Cause:** Multiple daemon/shim processes accumulate due to:
1. Path inconsistency in `ws_start.ps1` (line 30)
2. Incomplete cleanup in `ws_stop.ps1`
3. Stale health file not validated on startup
4. Multiple MCP clients spawning independent shims
5. Orphaned shims respawning daemons via autostart

**Impact:** Connection failures, stale health files, resource waste, unpredictable behavior.

**Solution:** Robust process management with cleanup, validation, and monitoring.

---

## 🔍 Investigation Summary

### Evidence Collected

**Process Accumulation Found:**
- 2 daemon processes (PID 14664, 15008)
- 10+ shim processes running simultaneously
- Health file showed dead PID 14908
- No `ws_daemon.pid` file existed

**Files Examined:**
1. `scripts/ws_start.ps1` - Main startup script
2. `scripts/ws_stop.ps1` - Stop script
3. `scripts/run_ws_shim.py` - Shim process launcher
4. `src/daemon/ws_server.py` - Daemon server with PID management
5. `Daemon/mcp-config.*.json` - MCP client configurations

---

## 🐛 Root Causes Identified

### 1. PATH INCONSISTENCY (Critical)

**Location:** `scripts/ws_start.ps1` line 30

**Problem:**
```powershell
# WRONG PATH - File doesn't exist here
& $Py "scripts\ws\run_ws_daemon.py"
```

**Correct Path (used by shim):**
```python
# run_ws_shim.py line 146
daemon = str(_repo_root / "scripts" / "run_ws_daemon.py")
```

**Actual Location:** `scripts/ws/run_ws_daemon.py`

**Impact:**
- Manual start may fail or use fallback
- Shim autostart uses correct path → spawns daemon
- Two different launch paths = potential for duplicates

---

### 2. INCOMPLETE CLEANUP (Critical)

**Location:** `scripts/ws_stop.ps1`

**Problem:**
- Only kills daemon by PID (lines 45-47)
- Doesn't kill shim processes
- Doesn't validate cleanup completion

**Impact:**
- Shims remain running after daemon stop
- Orphaned shims can respawn daemons via autostart
- Process accumulation over time

---

### 3. STALE HEALTH FILE (High)

**Location:** `src/daemon/ws_server.py` lines 1174-1189

**Problem:**
- Daemon validates PID file but NOT health file PID
- Health file can show dead PID while new daemons start
- Shims connect based on health file PID

**Impact:**
- Connection attempts target wrong/dead daemon
- Health file becomes stale and misleading
- Debugging becomes difficult

---

### 4. MULTIPLE SHIMS (Normal Behavior)

**Location:** `Daemon/mcp-config.*.json`

**Finding:**
- Each MCP client (Augment, Claude Desktop) spawns its own shim
- 10+ shims = multiple clients or repeated connection attempts
- **This is NORMAL and EXPECTED behavior**

**Impact:**
- Not a bug, but contributes to process count
- Each shim can trigger autostart if daemon is down
- Multiple autostarts = duplicate daemons

---

### 5. AUTOSTART RACE CONDITION (Medium)

**Location:** `scripts/run_ws_shim.py` lines 140-151

**Problem:**
- Multiple shims can simultaneously detect missing daemon
- All attempt autostart at once
- No coordination between shims

**Impact:**
- Race condition can spawn multiple daemons
- First daemon wins port, others fail silently
- Failed daemons may leave stale PID/health files

---

## ✅ Proposed Solutions

### Solution 1: Fix Path Inconsistency

**File:** `scripts/ws_start.ps1` line 30

**Change:**
```powershell
# BEFORE (WRONG)
& $Py "scripts\ws\run_ws_daemon.py"

# AFTER (CORRECT)
& $Py "scripts\run_ws_daemon.py"
```

**Rationale:** Match the path used by shim autostart to prevent duplicate launch mechanisms.

---

### Solution 2: Enhance ws_stop.ps1

**File:** `scripts/ws_stop.ps1`

**Add Shim Cleanup:**
```powershell
# After daemon stop, kill all shims
Write-Host "Stopping all shim processes..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    $cmdLine = (Get-WmiObject Win32_Process -Filter "ProcessId = $($_.Id)").CommandLine
    $cmdLine -like "*run_ws_shim.py*"
} | ForEach-Object {
    Write-Host "  Killing shim PID $($_.Id)..." -ForegroundColor Yellow
    Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
}
```

**Rationale:** Prevent orphaned shims from respawning daemons.

---

### Solution 3: Integrate Cleanup into ws_start.ps1

**File:** `scripts/ws_start.ps1`

**Add Pre-Start Cleanup:**
```powershell
# Before starting daemon, ensure clean state
if ($Restart -or (-not $Shim)) {
    Write-Host "Ensuring clean process state..." -ForegroundColor Cyan
    powershell -ExecutionPolicy Bypass -File "$Root\scripts\cleanup_processes.ps1" | Write-Host
}
```

**Rationale:** Guarantee clean slate on every start, prevent accumulation.

---

### Solution 4: Validate Health File PID

**File:** `src/daemon/ws_server.py`

**Add Health File Validation:**
```python
def _is_health_pid_stale() -> bool:
    """Check if health file PID matches a running process."""
    try:
        if not _health_path.exists():
            return True
        data = json.loads(_health_path.read_text(encoding="utf-8"))
        pid = int(data.get("pid", 0))
        if pid == 0:
            return True
        # Check if process exists
        try:
            import psutil
            return not psutil.pid_exists(pid)
        except ImportError:
            # Fallback: check if PID file matches health file
            if PID_FILE.exists():
                pid_file_pid = int(PID_FILE.read_text(encoding="utf-8").strip())
                return pid != pid_file_pid
            return True
    except Exception:
        return True

# In main_async(), before starting:
if _is_health_pid_stale():
    logger.warning("Stale health file detected; removing %s", _health_path)
    _health_path.unlink(missing_ok=True)
```

**Rationale:** Prevent connections to dead daemons, ensure health file accuracy.

---

### Solution 5: Add Process Monitoring

**New File:** `scripts/monitor_processes.ps1`

**Purpose:** Detect and alert on duplicate daemons

```powershell
# Check for multiple daemon processes
$daemonProcesses = Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    $cmdLine = (Get-WmiObject Win32_Process -Filter "ProcessId = $($_.Id)").CommandLine
    $cmdLine -like "*run_ws_daemon.py*"
}

if ($daemonProcesses.Count -gt 1) {
    Write-Host "⚠️ WARNING: Multiple daemon processes detected!" -ForegroundColor Red
    Write-Host "This indicates a process management issue." -ForegroundColor Red
    $daemonProcesses | ForEach-Object {
        Write-Host "  PID $($_.Id)" -ForegroundColor Yellow
    }
    exit 1
}
```

**Rationale:** Early detection of accumulation, automated alerts.

---

## 📋 Implementation Checklist

### Phase 1: Immediate Fixes ✅ COMPLETE
- [x] Fix path in `run_ws_shim.py` line 146 (was `scripts/run_ws_daemon.py`, now `scripts/ws/run_ws_daemon.py`)
- [x] Add shim cleanup to `ws_stop.ps1` (kills all shim processes after daemon stop)
- [x] Test restart cycle (verified working - shim cleanup executes correctly)

**Note:** `ws_start.ps1` already calls `ws_stop.ps1` before starting, so cleanup is automatic.

### Phase 2: Validation & Monitoring (1 hour) - IN PROGRESS
- [ ] Add health file PID validation to `ws_server.py`
- [ ] Create `monitor_processes.ps1`
- [ ] Add monitoring to startup scripts
- [ ] Test with multiple MCP clients

### Phase 3: Documentation & Testing (30 minutes) - PENDING
- [ ] Update README with process management info
- [ ] Document expected shim count per client
- [ ] Create troubleshooting guide
- [ ] Add to MASTER_CHECKLIST

---

## 🧪 Testing Plan

### Test 1: Clean Restart
1. Run `cleanup_processes.ps1`
2. Start daemon with `ws_start.ps1 -Restart`
3. Verify single daemon process
4. Verify health file PID matches running daemon

### Test 2: Multiple Clients
1. Connect Augment Code
2. Connect Claude Desktop
3. Verify 2 shim processes (one per client)
4. Verify single daemon process
5. Disconnect clients
6. Verify shims terminate

### Test 3: Crash Recovery
1. Kill daemon process forcefully
2. Wait for shim to detect and autostart
3. Verify single new daemon spawned
4. Verify health file updated correctly

### Test 4: Repeated Restarts
1. Restart daemon 10 times in succession
2. Verify no process accumulation
3. Verify health file always accurate
4. Verify no stale PID files

---

## 📊 Success Criteria

- ✅ Single daemon process at all times
- ✅ One shim per MCP client (expected behavior)
- ✅ Health file PID always matches running daemon
- ✅ No stale PID files after restart
- ✅ Clean process state after `ws_stop.ps1`
- ✅ No accumulation after 10+ restart cycles
- ✅ Monitoring detects duplicates within 1 second

---

## 🔄 Related Issues

- **MASTER_CHECKLIST.md** - Add to Phase A stabilization
- **KNOWN_ISSUES.md** - Update with resolution
- **ws_start.ps1** - Path fix required
- **ws_stop.ps1** - Cleanup enhancement required
- **ws_server.py** - Health validation required

---

**Next Action:** Implement Phase 1 fixes and test restart cycle

**Estimated Time:** 2 hours total (30min + 1hr + 30min)

**Priority:** 🔴 CRITICAL - Blocks reliable operation

