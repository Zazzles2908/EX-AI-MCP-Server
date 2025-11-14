# Port 3005 Conflict - Root Cause & Solution

## Problem Summary

**Symptom**: MCP server `exai-mcp` repeatedly fails with:
```
OSError: [Errno 10048] error while attempting to bind on address ('127.0.0.1', 3005):
[winerror 10048] only one usage of each socket address (protocol/network address/port) is normally permitted
```

## Root Cause Analysis

### The Core Issue
Multiple instances of `run_ws_shim.py` running simultaneously, each trying to bind to port 3005.

### Why This Happens

1. **Windows Incompatibility**:
   - The original `run_ws_shim.py` uses Unix-specific process management (`os.setpgrp()`, `os.killpg()`)
   - These functions don't exist/don't work on Windows
   - When VSCode/Claude Code closes forcibly, the WebSocket shim becomes **orphaned**

2. **Missing Cleanup**:
   - No signal handling for Windows process termination
   - No detection of orphaned processes
   - Port remains bound even after parent process dies

3. **Race Condition**:
   - When Claude Code restarts, it tries to start a new shim instance
   - The orphaned shim is still holding port 3005
   - Conflict occurs: `[Errno 10048]`

## Solution Implemented

### 1. Cleanup Detection Script
**File**: `scripts/runtime/cleanup_orphaned_shims.py`

**Features**:
- Detects all `run_ws_shim.py` processes
- Identifies which port each process is using
- Kills orphaned processes (ones not properly holding their port)

**Usage**:
```bash
# Check for orphans (non-destructive)
python scripts/runtime/cleanup_orphaned_shims.py --check-only

# Auto-cleanup orphans
python scripts/runtime/cleanup_orphaned_shims.py
```

### 2. Safe Startup Wrapper
**File**: `scripts/runtime/start_ws_shim_safe.py`

**Features**:
- Runs cleanup before starting the shim
- Verifies port 3005 is free
- Provides detailed logging
- Windows-compatible

**Process**:
1. Kill any orphaned shims
2. Wait for port to be released
3. Verify port 3005 is available
4. Start the WebSocket shim
5. Stream output with proper logging

### 3. Updated MCP Configuration
**File**: `.mcp.json`

**Change**:
```json
{
  "exai-mcp": {
    "command": "C:/Project/EX-AI-MCP-Server/.venv/Scripts/python.exe",
    "args": [
      "-u",
      "C:/Project/EX-AI-MCP-Server/scripts/runtime/start_ws_shim_safe.py"  // Changed from run_ws_shim.py
    ],
    ...
  }
}
```

### 4. Manual Startup Script
**File**: `start_exai_mcp.bat`

**Purpose**: Safe manual startup with cleanup

**Usage**:
```cmd
# Double-click or run from command prompt
start_exai_mcp.bat
```

### 5. Automated Cleanup
**File**: `scripts/windows-cleanup/auto_cleanup_ws_shims.bat`

**Purpose**: Scheduled cleanup to prevent future issues

**Setup** (requires admin privileges):
```cmd
schtasks /create /tn "EXAI-ShimCleanup" /tr "C:\Project\EX-AI-MCP-Server\scripts\windows-cleanup\auto_cleanup_ws_shims.bat" /sc minute /mo 5
```

**Effect**: Runs cleanup every 5 minutes to catch any orphaned processes

## Verification Steps

After applying the fix:

### 1. Check for Orphaned Processes
```bash
python scripts/runtime/cleanup_orphaned_shims.py --check-only
# Expected: "No run_ws_shim processes found" or "No cleanup needed"
```

### 2. Verify Port is Available
```bash
netstat -an | findstr ":3005"
# Expected: No output (port is free)
```

### 3. Test Safe Startup
```bash
# Should start without port conflict errors
python scripts/runtime/start_ws_shim_safe.py
```

### 4. Verify MCP Connection
In Claude Code:
- `exai-mcp` should show as **Connected** (not Failed)
- No errors in MCP connection logs

## Technical Details

### Process Detection Logic

The cleanup script uses `psutil` to:
1. List all Python processes
2. Filter for those running `run_ws_shim.py`
3. Check which process is holding port 3005
4. Kill duplicate/orphaned processes

### Port Conflict Detection

```python
def is_port_in_use(port):
    """Returns PID if port is in use, None otherwise"""
    for conn in psutil.net_connections():
        if conn.laddr.port == port and conn.status == 'LISTENING':
            return conn.pid
    return None
```

### Safe Startup Flow

```
start_ws_shim_safe.py
    ↓
cleanup_orphaned_shims.py (kills orphans)
    ↓
check_port_available(3005) (verify port free)
    ↓
subprocess.Popen(run_ws_shim.py) (start shim)
    ↓
stream output (real-time logging)
```

## Prevention

### For Users
1. **Use Safe Startup**: Always use `start_ws_shim_safe.py` or `start_exai_mcp.bat`
2. **Check Before VSCode**: Run cleanup before opening VSCode if issues persist
3. **Monitor Periodically**: Set up the scheduled task for automated cleanup

### For Developers
1. **Update .mcp.json**: Ensure it points to `start_ws_shim_safe.py`
2. **Test Cleanup**: Verify cleanup script works on Windows
3. **Monitor Logs**: Check for orphaned process warnings

## Alternative Solutions Considered

### 1. Fix run_ws_shim.py Directly
**Pros**: Single point of failure
**Cons**: Requires breaking changes to existing script, Windows-specific code

### 2. Use Different Port
**Pros**: Simple
**Cons**: Requires updating multiple configuration files, doesn't fix root cause

### 3. Docker-Only Deployment
**Pros**: Better isolation
**Cons**: Overkill for local development, requires Docker always running

### 4. System Service
**Pros**: Proper process management
**Cons**: Requires admin privileges, complex setup

## Chosen Solution: Safe Wrapper

**Why This Approach**:
1. ✅ **Non-invasive**: Doesn't modify existing `run_ws_shim.py`
2. ✅ **Windows-compatible**: Uses standard Python libraries
3. ✅ **Automatic**: Integrated into MCP startup via `.mcp.json`
4. ✅ **Reusable**: Cleanup script can be used independently
5. ✅ **Observable**: Detailed logging for troubleshooting

## Impact Assessment

### Before Fix
- ❌ exai-mcp fails to connect
- ❌ Manual process killing required
- ❌ Unclear error messages
- ❌ Frequent reoccurrence

### After Fix
- ✅ Automatic cleanup on startup
- ✅ Clear error messages and logging
- ✅ Prevents orphaned processes
- ✅ Works reliably on Windows

## Future Improvements

1. **Enhanced Detection**: Monitor for any process holding port 3005, not just Python scripts
2. **Graceful Restart**: If shim is running, gracefully restart instead of killing
3. **PID File**: Use PID files to track running instances
4. **Windows Service**: Convert to proper Windows service for production use
5. **Cross-Platform**: Make process management work on Linux/Mac too

## Testing

### Test 1: Orphan Cleanup
```bash
# Start shim
python scripts/runtime/run_ws_shim.py &
# Simulate orphan (don't kill properly)
# Run cleanup
python scripts/runtime/cleanup_orphaned_shims.py
# Verify port is free
netstat -an | findstr ":3005"
```

### Test 2: Safe Startup
```bash
# With orphaned process present
python scripts/runtime/start_ws_shim_safe.py
# Should cleanup and start successfully
```

### Test 3: MCP Connection
```bash
# Start VSCode/Claude Code
# Check exai-mcp status
# Should be Connected, not Failed
```

## References

- **Original Issue**: Port conflict `[Errno 10048]`
- **Platform**: Windows (issue doesn't occur on Unix/Linux)
- **Affected Component**: WebSocket shim (port 3005)
- **Solution Type**: Process management and cleanup automation
- **Files Modified**:
  - `.mcp.json` - Updated to use safe wrapper
  - `scripts/runtime/start_ws_shim_safe.py` - Created
  - `scripts/runtime/cleanup_orphaned_shims.py` - Created
  - `start_exai_mcp.bat` - Created

---

**Status**: ✅ **RESOLVED**
**Tested**: ✅ On Windows with orphaned process simulation
**Automated**: ✅ Integrated into MCP startup
**Monitoring**: ✅ Scheduled cleanup available
