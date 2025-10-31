# Root Cause Analysis: System Crash 2025-10-31

**Date**: 2025-10-31 23:33:05  
**Severity**: CRITICAL  
**Status**: IDENTIFIED - Multiple root causes found

---

## 🔴 Critical Issues Identified

### Issue #1: Tool Execution Timeout Hardcoded to 300s (CRITICAL)

**Location**: `src/daemon/ws/request_router.py` line 863

```python
call_timeout = float(validated_env.get("WORKFLOW_TOOL_TIMEOUT_SECS", 300.0))
```

**Problem**:
- Default timeout is 300 seconds (5 minutes)
- When WORKFLOW_TOOL_TIMEOUT_SECS is not set in .env, it defaults to 300s
- This causes tools to hang for 5 minutes before timing out
- The log shows: `Tool execution timed out after 300.0s`

**Evidence from logs**:
```
2025-10-31 23:33:05 WARNING src.daemon.ws.request_router: [7fa1ecaa-24cb-438e-ad45-601ed6fb4d72] Tool execution timed out after 300.0s
2025-10-31 23:33:05 ERROR src.daemon.error_handling: [req:7fa1ecaa-24cb-438e-ad45-601ed6fb4d72] [INTERNAL_ERROR] Tool execution timed out after 300.0s
```

**Root Cause**: `.env.docker.template` sets `WORKFLOW_TOOL_TIMEOUT_SECS=180` but the actual `.env` file in the container may not have this set, causing fallback to 300s.

---

### Issue #2: Semaphore Leak - Double Release Pattern (CRITICAL)

**Location**: `src/daemon/middleware/semaphores.py` lines 241-263

**Problem**:
- Semaphore recovery system releases semaphores
- But the SemaphoreGuard context manager also tries to release
- This causes double-release or release-without-acquire pattern
- Logs show: `Semaphore leak detected: global expected=5, actual=4`

**Evidence from logs**:
```
2025-10-31 23:33:05 WARNING src.monitoring.metrics: Semaphore leak detected: global expected=5, actual=4
2025-10-31 23:33:05 WARNING src.daemon.middleware.semaphores: SEMAPHORE HEALTH: Global semaphore leak: expected 5, got 4
2025-10-31 23:33:05 WARNING src.daemon.middleware.semaphores: Semaphore global_sem_debug already at max value (5/5), skipping release (likely recovered by recovery system)
```

**Root Cause**: Race condition between recovery system and context manager cleanup.

---

### Issue #3: ResilientWebSocketManager Disabled (CRITICAL)

**Location**: `src/daemon/ws_server.py` lines 764-772

**Problem**:
- ResilientWebSocketManager is **disabled** with a temporary workaround
- Comment says: "TEMPORARY WORKAROUND (2025-10-28): Disable resilient WebSocket manager for load testing"
- This means WebSocket messages are NOT queued when client disconnects
- When client disconnects, all pending messages are lost
- System falls back to legacy send which doesn't handle disconnects gracefully

**Evidence from code**:
```python
# Line 769 in ws_server.py
_resilient_ws = None  # ❌ DISABLED
# _resilient_ws = ResilientWebSocketManager(fallback_send=_safe_send)
```

**Root Cause**: Temporary workaround left in production code. When client disconnects, the 100+ socket.send() failures occur because there's no resilient manager to queue messages.

---

### Issue #4: Kimi API Rate Limiting (SECONDARY)

**Location**: Kimi API (external)

**Problem**:
- Kimi API returning retries with exponential backoff
- 0.8s delay, then 1.6s delay
- Indicates rate limiting or API overload

**Evidence from logs**:
```
2025-10-31 23:27:16 INFO zhipuai.core._http_client: Retrying request to /chat/completions in 0.807217 seconds
2025-10-31 23:27:48 INFO zhipuai.core._http_client: Retrying request to /chat/completions in 1.645739 seconds
```

**Root Cause**: External API issue, not code issue.

---

## 🔧 Why You Had to Restart

**Sequence of Events**:

1. **Tool hangs for 300s** (Issue #1)
   - EXAI workflow tool (debug/analyze) starts
   - Waits for response from Kimi API
   - Kimi API is rate-limited (Issue #4)
   - Tool waits full 300 seconds

2. **WebSocket connection breaks** (Issue #3)
   - During the 300s wait, VSCode client disconnects
   - Daemon tries to send responses but socket is broken
   - 100+ send failures occur

3. **Semaphore leak occurs** (Issue #2)
   - Recovery system tries to clean up
   - Context manager also tries to release
   - Semaphore count goes from 5 to 4
   - System becomes partially deadlocked

4. **System becomes unresponsive**
   - Semaphore leak prevents new tool executions
   - WebSocket is broken
   - Daemon is stuck waiting for 300s timeout
   - **You restart the server to recover**

---

## ✅ Fixes Required

### Fix #1: Set WORKFLOW_TOOL_TIMEOUT_SECS in .env

**File**: `.env` (or `.env.docker`)

```bash
# Change from default 300s to 180s (3 minutes)
WORKFLOW_TOOL_TIMEOUT_SECS=180
```

**Why**: Prevents tools from hanging for 5 minutes.

---

### Fix #2: Fix Semaphore Double-Release

**File**: `src/daemon/middleware/semaphores.py`

**Current code** (lines 241-263):
```python
async def __aexit__(self, exc_type, exc_val, exc_tb):
    if self.acquired:
        try:
            if hasattr(self.semaphore, '_value') and hasattr(self.semaphore, '_bound_value'):
                if self.semaphore._value >= self.semaphore._bound_value:
                    logger.warning(...)
                    self.acquired = False
                    return False  # ❌ PROBLEM: Returns False, doesn't prevent double-release
```

**Issue**: Returning False doesn't prevent the exception from propagating. Need to return True.

---

### Fix #3: Re-enable ResilientWebSocketManager

**File**: `src/daemon/ws_server.py` lines 764-772

**Current code** (BROKEN):
```python
_resilient_ws = None  # ❌ DISABLED
# _resilient_ws = ResilientWebSocketManager(fallback_send=_safe_send)
```

**Fix**: Re-enable the manager:
```python
_resilient_ws = ResilientWebSocketManager(fallback_send=_safe_send)
await _resilient_ws.start_background_tasks()
```

**Why**: ResilientWebSocketManager queues messages when client disconnects and retries when reconnected. This prevents the 100+ socket.send() failures.

---

## 📊 Impact Assessment

| Issue | Severity | Impact | Fix Time |
|-------|----------|--------|----------|
| #1: 300s timeout | CRITICAL | Tools hang for 5 min | 5 min |
| #2: Semaphore leak | CRITICAL | System deadlock | 15 min |
| #3: WebSocket failures | CRITICAL | Client disconnect | 20 min |
| #4: Kimi rate limit | SECONDARY | Slow responses | N/A (external) |

**Total Fix Time**: ~40 minutes

---

## 🎯 Next Steps

1. **Immediate**: Update .env with WORKFLOW_TOOL_TIMEOUT_SECS=180
2. **High Priority**: Fix semaphore double-release in SemaphoreGuard
3. **High Priority**: Implement WebSocket reconnection logic
4. **Monitor**: Watch for Kimi API rate limiting patterns


