# Duplicate Daemon Process - Root Cause Analysis

**Date:** 2025-10-14  
**Status:** CRITICAL - Blocking EXAI functionality  
**Priority:** P0 - Must fix before proceeding with any other work

## Problem Statement

When starting the EXAI WebSocket daemon using ANY method (PowerShell script, direct Python invocation), **TWO daemon processes are created simultaneously** with a parent-child relationship. This causes:

1. ❌ EXAI tools fail with "Not connected" error
2. ❌ Unpredictable behavior (which daemon handles requests?)
3. ❌ Resource waste (duplicate processes)
4. ❌ Potential race conditions and conflicts

## Investigation Findings

### Evidence

```powershell
# Process tree shows parent-child relationship:
Type     PID ParentPID StartTime
----     --- --------- ---------
DAEMON 26328     39800 14/10/2025 7:34:24 PM  # Child process
DAEMON 39800     40268 14/10/2025 7:34:24 PM  # Parent process (PowerShell)
```

**Key Observations:**
1. ✅ Only ONE "Starting WS daemon" log message per startup
2. ✅ Only ONE process listens on port 8079 (the child process)
3. ✅ Parent process (PID 39800) spawns child process (PID 26328)
4. ✅ Happens with BOTH PowerShell script AND direct Python invocation
5. ✅ No subprocess/multiprocessing code in daemon, bootstrap, or logging
6. ✅ Parent process appears to be a "launcher" that spawns the actual daemon

### Root Cause Hypothesis

**Primary Suspect: Python Virtual Environment Wrapper**

The `.venv\Scripts\python.exe` in Windows virtual environments is often a **launcher/wrapper** that:
1. Activates the virtual environment
2. Spawns the actual Python interpreter as a child process
3. Remains running as a parent process

This is standard Windows venv behavior, but it creates confusion because:
- Process monitoring shows 2 Python processes
- Only the child process actually runs the daemon code
- The parent process is just a wrapper/launcher

**Secondary Suspect: Windows Process Creation**

When using `System.Diagnostics.Process` with `RedirectStandardOutput/Error`, Windows may create an additional process handle or wrapper.

## Impact Analysis

### Current Impact
- **EXAI Tools:** Not connecting (daemon in inconsistent state)
- **Process Management:** Cleanup scripts kill both processes, but unclear which is "real"
- **Monitoring:** Health checks and PID files may reference wrong process
- **User Experience:** Random glitches, connection refused errors

### Multiple MCP Clients
User has multiple applications connected:
- Augment Code (VSCode extension)
- Claude Desktop
- Auggie CLI

Each spawns a shim process that connects to the daemon. If daemon is unstable, ALL clients are affected.

## Proposed Solutions

### Option A: Accept and Document (RECOMMENDED)
**Approach:** This is normal Windows venv behavior - document it and adjust monitoring

**Changes:**
1. Update process monitoring to expect parent-child relationship
2. Modify cleanup scripts to identify and kill only the "real" daemon (child process)
3. Update health checks to validate the listening process, not just PID file
4. Document expected process tree in troubleshooting guide

**Pros:**
- ✅ No code changes to daemon itself
- ✅ Works with standard Python venv
- ✅ Low risk
- ✅ Quick to implement

**Cons:**
- ⚠️ Requires careful process management
- ⚠️ May confuse users/developers

### Option B: Use Direct Python Interpreter
**Approach:** Bypass venv wrapper by using the actual Python interpreter directly

**Changes:**
1. Modify startup scripts to use `.venv\Scripts\python.exe` → `C:\Python313\python.exe`
2. Manually set PYTHONPATH to include venv site-packages
3. Update all startup scripts

**Pros:**
- ✅ Single process (no wrapper)
- ✅ Clearer process tree

**Cons:**
- ❌ Breaks venv isolation
- ❌ Manual dependency path management
- ❌ Not recommended Python practice
- ❌ May cause import issues

### Option C: Use Python `-I` Flag
**Approach:** Use Python's isolated mode to prevent wrapper behavior

**Changes:**
1. Add `-I` flag to Python invocation: `python.exe -I -u scripts\ws\run_ws_daemon.py`
2. Test if this prevents wrapper process creation

**Pros:**
- ✅ Minimal changes
- ✅ Maintains venv usage

**Cons:**
- ⚠️ May not solve the issue (wrapper might still be created)
- ⚠️ Isolated mode disables some Python features

### Option D: Investigate and Fix Wrapper
**Approach:** Deep dive into why venv wrapper is being created and prevent it

**Changes:**
1. Analyze `.venv\Scripts\python.exe` to understand wrapper mechanism
2. Modify venv creation or Python installation
3. Potentially rebuild venv without wrapper

**Pros:**
- ✅ Addresses root cause directly

**Cons:**
- ❌ Time-consuming investigation
- ❌ May not be fixable (Windows venv standard behavior)
- ❌ Could break other functionality

## Recommended Action Plan

**Phase 1: Immediate Fix (Option A) - 30 minutes**
1. ✅ Accept parent-child process relationship as normal
2. ✅ Update cleanup script to kill both processes (already working)
3. ✅ Modify health check to validate listening process
4. ✅ Test with single daemon startup
5. ✅ Verify EXAI tools connect successfully

**Phase 2: Enhanced Monitoring - 1 hour**
1. Add process tree validation to startup scripts
2. Update health file to include both parent and child PIDs
3. Modify monitoring to expect 2 processes per daemon
4. Add warnings if unexpected process count detected

**Phase 3: Documentation - 30 minutes**
1. Document expected process tree in README
2. Add troubleshooting guide for process management
3. Update PROCESS_ACCUMULATION_ROOT_CAUSE_AND_FIX.md with findings

## Testing Plan

1. **Single Daemon Test:**
   - Start daemon with `ws_daemon_start.ps1`
   - Verify 2 processes created (parent + child)
   - Verify only child listens on port 8079
   - Test EXAI tool connection
   - Verify health file accuracy

2. **Multiple Client Test:**
   - Connect Augment Code
   - Connect Claude Desktop
   - Connect Auggie CLI
   - Verify each spawns 1 shim
   - Verify all shims connect to same daemon (child process)
   - Test tool execution from each client

3. **Restart Test:**
   - Stop daemon with `ws_stop.ps1`
   - Verify both processes killed
   - Restart daemon
   - Verify clean startup with 2 new processes

4. **Cleanup Test:**
   - Create multiple daemon instances (simulate accumulation)
   - Run `cleanup_processes.ps1`
   - Verify all processes killed
   - Verify PID file removed

## Success Criteria

- ✅ EXAI tools connect successfully
- ✅ No "Not connected" errors
- ✅ Process count is predictable and documented
- ✅ Cleanup scripts work reliably
- ✅ Health checks validate correct process
- ✅ Multiple MCP clients can connect simultaneously
- ✅ No random glitches or connection refused errors

## Next Steps

**Immediate:**
1. Get user approval for Option A (recommended approach)
2. Implement Phase 1 fixes
3. Test EXAI connectivity
4. Proceed with MASTER_CHECKLIST if successful

**Follow-up:**
1. Implement Phase 2 & 3 after Phase 1 validation
2. Monitor for any issues with multiple clients
3. Update documentation

## Questions for User

1. **Approve Option A?** Accept parent-child process relationship as normal Windows venv behavior?
2. **Test with multiple clients?** Should we test with all 3 MCP clients (Augment, Claude, Auggie) or just Augment for now?
3. **Priority?** Fix this first, or proceed with MASTER_CHECKLIST critical bugs?

---

**Analysis by:** Augment Agent  
**Date:** 2025-10-14 19:35 AEDT  
**Status:** Awaiting user approval to proceed

