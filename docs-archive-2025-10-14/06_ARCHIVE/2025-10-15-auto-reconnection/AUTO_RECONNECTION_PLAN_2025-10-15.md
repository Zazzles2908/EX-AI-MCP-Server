# Auto-Reconnection Implementation Plan
**Date:** 2025-10-15  
**Status:** Investigation & Planning Phase  
**Goal:** Achieve zero-manual-intervention reconnection when Docker restarts

---

## 🔍 Root Cause Analysis

### What We Discovered

1. **Health File Staleness Issue** ⚠️
   - Shim checks if `ws_daemon.health.json` is >20 seconds old
   - During long operations (web search, rate limits, streaming), daemon doesn't update health file
   - **FALSE POSITIVES**: Shim thinks daemon is down when it's actually processing requests
   - **Example**: GLM streaming hung for 6+ hours (13:38:43 → 20:19:50), health file not updated

2. **Health Monitor Auto-Exit Working** ✅
   - Added `_connection_health_monitor()` that checks every 30s
   - Exits shim after 3 consecutive failures (90 seconds)
   - **CONFIRMED**: Shim exited after detecting 6-hour hang
   - Augment auto-restarts shim when user toggles settings

3. **Configuration Confusion** ⚠️
   - `EXAI_WS_SKIP_HEALTH_CHECK` - unclear what this controls
   - Was "true", changed to "false" - no clear documentation
   - MCP config has many timeout settings - may be redundant

4. **Volume Mount Working** ✅
   - `./logs:/app/logs` correctly shares health file between host and container
   - Both host and container see same (stale) health file

---

## 🎯 Core Problems to Solve

### Problem 1: Health File Not Updated During Long Operations
**Impact:** Shim can't distinguish between "daemon is down" vs "daemon is busy"

**Options:**
- **A)** Increase staleness threshold from 20s to 120s+
- **B)** Make daemon update health file during long operations (background task)
- **C)** Remove health file check entirely, rely only on WebSocket ping/pong

### Problem 2: Augment Doesn't Auto-Restart Shim
**Impact:** User must manually toggle Augment settings after Docker restart

**Current Behavior:**
- Shim exits after 90s of failed health checks ✅
- Augment SHOULD auto-restart stdio MCP servers when they exit
- **BUT**: User reports needing to manually toggle settings

**Questions:**
- Does Augment auto-restart on clean exit (sys.exit(0))?
- Does it auto-restart on crash (exception)?
- Is there a delay before restart?
- Does it only restart when user tries to use a tool?

### Problem 3: Long-Running Operations Cause Cascading Failures
**Impact:** One stuck request (like 6-hour GLM hang) blocks everything

**Root Cause:**
- GLM streaming can hang indefinitely
- No timeout on streaming responses
- Fallback chain works but takes too long to trigger
- Health file not updated during the hang

---

## 📋 Proposed Solutions

### Solution 1: Fix Health File Updates (IMMEDIATE)

**Approach:** Make daemon update health file even during long operations

**Implementation:**
```python
# In ws_server.py - add background task
async def _health_file_updater():
    """Update health file every 10 seconds regardless of request processing"""
    while True:
        await asyncio.sleep(10)
        update_health_file()  # Existing function
```

**Benefits:**
- Simple, minimal code change
- Fixes false positives immediately
- No need to change staleness threshold
- Works with existing shim logic

**Risks:**
- Adds another background task
- Health file might show "healthy" even if daemon is stuck

### Solution 2: Increase Staleness Threshold (BACKUP)

**Approach:** Change shim's health check from 20s to 120s

**Implementation:**
```python
# In run_ws_shim.py - _check_daemon_health()
HEALTH_FILE_MAX_AGE = 120  # Was 20
```

**Benefits:**
- One-line change
- Allows for longer operations
- No daemon changes needed

**Risks:**
- Slower detection of actual daemon failures
- Doesn't solve root cause
- Still fails on 6-hour hangs

### Solution 3: Remove Health File Check (RADICAL)

**Approach:** Rely only on WebSocket ping/pong for health checks

**Implementation:**
- Remove `_check_daemon_health()` call before connection
- Let `_connection_health_monitor()` handle all health checks via WebSocket
- Health file becomes informational only

**Benefits:**
- Eliminates false positives entirely
- Simpler logic
- Real-time connection status

**Risks:**
- No pre-connection health check
- Slower initial connection if daemon is down
- Loses informational value of health file

### Solution 4: Add Streaming Timeouts (CRITICAL)

**Approach:** Prevent 6-hour hangs by adding timeouts to streaming responses

**Implementation:**
```python
# In glm_chat.py and kimi_chat.py
async def _stream_with_timeout(stream, timeout=300):  # 5 minutes
    """Wrap streaming with timeout to prevent infinite hangs"""
    start_time = time.time()
    async for chunk in stream:
        if time.time() - start_time > timeout:
            raise TimeoutError(f"Streaming exceeded {timeout}s")
        yield chunk
```

**Benefits:**
- Prevents cascading failures
- Faster fallback to alternative models
- Configurable per provider

**Risks:**
- Might interrupt legitimate long responses
- Needs careful timeout tuning

---

## 🔧 Recommended Implementation Plan

### Phase 1: Quick Fixes (Do First)
1. **Add health file background updater** (Solution 1)
   - File: `src/daemon/ws_server.py`
   - Add `_health_file_updater()` task
   - Start it in `main()`

2. **Add streaming timeouts** (Solution 4)
   - Files: `src/providers/glm_chat.py`, `src/providers/kimi_chat.py`
   - Wrap streaming with timeout
   - Use env vars: `GLM_STREAM_TIMEOUT`, `KIMI_STREAM_TIMEOUT`

3. **Increase staleness threshold as backup** (Solution 2)
   - File: `scripts/run_ws_shim.py`
   - Change from 20s to 120s
   - Add comment explaining why

### Phase 2: Configuration Cleanup
1. **Simplify MCP config**
   - Remove unclear settings like `EXAI_WS_SKIP_HEALTH_CHECK`
   - Document what each setting does
   - Remove redundant timeout settings

2. **Test auto-restart behavior**
   - Verify Augment auto-restarts shim on exit
   - Test with clean exit vs crash
   - Document actual behavior

### Phase 3: Testing & Validation
1. **Test Docker restart scenario**
   - Stop Docker container
   - Wait for shim to exit (90s)
   - Verify Augment restarts shim
   - Verify EXAI tools work without manual toggle

2. **Test long operation scenario**
   - Trigger web search with Kimi
   - Verify health file updates during operation
   - Verify no false positives

3. **Test streaming timeout**
   - Simulate slow streaming response
   - Verify timeout triggers
   - Verify fallback works

---

## 📝 Configuration Changes Needed

### `.env` Changes
```bash
# Add streaming timeouts
GLM_STREAM_TIMEOUT=300  # 5 minutes
KIMI_STREAM_TIMEOUT=600  # 10 minutes (Kimi can be slower)

# Increase health file staleness threshold
HEALTH_FILE_MAX_AGE=120  # Was 20

# Remove unclear settings
# EXAI_WS_SKIP_HEALTH_CHECK=false  # Remove this - unclear purpose
```

### `Daemon/mcp-config.augmentcode.json` Simplification
**Current Issues:**
- Too many timeout settings (13 different timeouts!)
- Unclear which ones are actually used
- `EXAI_WS_SKIP_HEALTH_CHECK` - what does this do?

**Proposed Simplification:**
```json
{
  "mcpServers": {
    "EXAI-WS": {
      "type": "stdio",
      "trust": true,
      "command": "C:/Project/EX-AI-MCP-Server/.venv/Scripts/python.exe",
      "args": ["-u", "C:/Project/EX-AI-MCP-Server/scripts/run_ws_shim.py"],
      "cwd": "C:/Project/EX-AI-MCP-Server",
      "env": {
        "ENV_FILE": "C:/Project/EX-AI-MCP-Server/.env",
        "PYTHONUNBUFFERED": "1",
        "PYTHONIOENCODING": "utf-8",
        "LOG_LEVEL": "INFO",
        "EXAI_WS_HOST": "127.0.0.1",
        "EXAI_WS_PORT": "8079"
      }
    }
  }
}
```

**Rationale:**
- All timeouts should come from `.env` file (centralized)
- MCP config should only have connection settings
- Simpler = easier to debug

---

## 🧪 Testing Checklist

### Test 1: Health File Updates During Long Operations
- [ ] Start daemon
- [ ] Trigger long operation (web search)
- [ ] Monitor health file - should update every 10s
- [ ] Verify no "stale health file" errors

### Test 2: Streaming Timeout
- [ ] Trigger GLM request
- [ ] Simulate slow/hung streaming
- [ ] Verify timeout triggers after 5 minutes
- [ ] Verify fallback to Kimi works

### Test 3: Docker Restart Auto-Reconnection
- [ ] Use EXAI tool successfully
- [ ] Restart Docker: `docker-compose restart`
- [ ] Wait 90 seconds
- [ ] Verify shim exits
- [ ] Verify Augment restarts shim (check logs)
- [ ] Use EXAI tool - should work without manual toggle

### Test 4: Shim Exit Behavior
- [ ] Kill Docker container
- [ ] Monitor shim logs
- [ ] Verify health monitor detects failure
- [ ] Verify shim exits after 90s
- [ ] Check Augment behavior

---

## 🚨 Open Questions

1. **Does Augment auto-restart stdio MCP servers?**
   - On clean exit (sys.exit(0))?
   - On crash (exception)?
   - Immediately or on next tool use?

2. **What does EXAI_WS_SKIP_HEALTH_CHECK actually do?**
   - Skips health file check before connection?
   - Skips WebSocket health monitor?
   - Should we remove it entirely?

3. **Why did GLM streaming hang for 6 hours?**
   - Network issue?
   - GLM API bug?
   - Missing timeout in SDK?

4. **Should health file show "healthy" during long operations?**
   - Or should it show "busy" status?
   - Should it include "last_request_started" timestamp?

---

## 📊 Success Criteria

### Must Have
- ✅ No manual Augment settings toggle required after Docker restart
- ✅ No false positive "daemon is down" errors during long operations
- ✅ Streaming requests timeout after reasonable duration (5-10 minutes)
- ✅ Health file updates every 10 seconds regardless of request processing

### Nice to Have
- ✅ Simplified MCP configuration (remove redundant settings)
- ✅ Clear documentation of what each setting does
- ✅ Faster detection of actual daemon failures (<30 seconds)
- ✅ Better logging of reconnection events

---

## 🔄 Implementation Status

### ✅ Phase 1: Quick Fixes (COMPLETED)

1. **Health File Background Updater** ✅
   - Already implemented in `src/daemon/ws_server.py` (line 1130)
   - Updates every 10 seconds via `_health_writer()` task
   - Has timeout protection to prevent blocking on session locks

2. **Streaming Timeouts** ✅
   - Added to `src/providers/glm_chat.py` (line 190-237)
   - Added to `streaming/streaming_adapter.py` (line 45-106)
   - GLM timeout: 300s (5 minutes) via `GLM_STREAM_TIMEOUT`
   - Kimi timeout: 600s (10 minutes) via `KIMI_STREAM_TIMEOUT`

3. **Increased Staleness Threshold** ✅
   - Updated `scripts/run_ws_shim.py` (line 56-66)
   - Changed from 20s to 120s
   - Added detailed comment explaining rationale

4. **Environment Variables** ✅
   - Added `GLM_STREAM_TIMEOUT=300` to `.env`
   - Added `KIMI_STREAM_TIMEOUT=600` to `.env`
   - Kept `KIMI_STREAM_TIMEOUT_SECS=240` for backward compatibility

### ✅ Phase 2: Configuration Cleanup (COMPLETED)

1. **Simplified MCP Config** ✅
   - Removed all timeout settings from `Daemon/mcp-config.augmentcode.json`
   - Removed unclear settings (`EXAI_WS_SKIP_HEALTH_CHECK`, etc.)
   - Now only contains essential connection settings
   - All timeouts now come from `.env` file (centralized)

### 🔄 Next Steps

1. **Restart Docker container** (to load new code changes)
2. **Restart Augment settings** (to reload simplified MCP config)
3. **Test with simple EXAI call** (verify basic functionality)
4. **Run full test suite** (all 4 tests above)
5. **Test actual Docker restart scenario** (verify auto-reconnection)
6. **Document findings** (update this file with results)

---

## 📚 Related Files

- `scripts/run_ws_shim.py` - Shim with health monitor
- `src/daemon/ws_server.py` - Daemon that needs health file updater
- `src/providers/glm_chat.py` - Needs streaming timeout
- `src/providers/kimi_chat.py` - Needs streaming timeout
- `Daemon/mcp-config.augmentcode.json` - Needs simplification
- `.env` - Needs new timeout settings

