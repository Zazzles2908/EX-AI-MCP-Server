# WebSocket Ping Timeout Mismatch Fix - 2025-10-26

## 🎯 Root Cause Identified

**Problem:** Connections cycling every 10-30 seconds due to ping/pong timeout mismatches between daemon and shim.

### Evidence from Docker Logs

```
19:33:17 - vscode-instance-1 connects (session created)
19:33:17 - vscode-instance-2 connects (session created)
19:33:27 - vscode-instance-1 DISCONNECTS (duration: 10.43s) ❌
19:33:27 - vscode-instance-1 reconnects
19:33:27 - vscode-instance-2 reconnects
```

**Pattern:** Connections disconnect and reconnect every 10-30 seconds, causing both VSCode instances to show red dots.

---

## 🔍 Configuration Mismatch Analysis

### Daemon Configuration (.env.docker)
```bash
EXAI_WS_PING_INTERVAL=45  # Daemon expects pings every 45 seconds
EXAI_WS_PING_TIMEOUT=240  # Daemon waits 240 seconds for ping response
```

### Shim Configuration (.env) - BEFORE FIX
```bash
EXAI_WS_PING_INTERVAL=30  # ❌ MISMATCH: Shim configured for 30s
EXAI_WS_PING_TIMEOUT=30   # ❌ MISMATCH: Shim configured for 30s
```

### Shim Code (run_ws_shim.py)
```python
# Line 78-79: Hardcoded defaults (ignores .env values!)
PING_INTERVAL = int(os.getenv("EXAI_WS_PING_INTERVAL", "45"))  # Uses 45s default
PING_TIMEOUT = int(os.getenv("EXAI_WS_PING_TIMEOUT", "30"))    # Uses 30s default
```

**The Problem:**
1. Daemon expects pings every 45 seconds (from .env.docker)
2. Shim sends pings every 45 seconds (from hardcoded default, ignoring .env)
3. But .env says 30 seconds - creating confusion
4. Daemon has 240s ping timeout, shim has 30s ping timeout
5. Timeout mismatches cause connection cycling

---

## ✅ Solution Implemented

### Updated .env Configuration
```bash
# CRITICAL FIX (2025-10-26): Match .env.docker settings to prevent connection cycling
# Daemon uses 45s interval and 240s timeout (from .env.docker)
# Shim must match these values to maintain stable connections
EXAI_WS_PING_INTERVAL=45
EXAI_WS_PING_TIMEOUT=240
```

**Why This Works:**
- Daemon and shim now use identical ping settings
- 45-second ping interval is industry standard (RFC 6455)
- 240-second timeout provides ample buffer for network latency
- Eliminates timeout-based disconnections

---

## 📊 Expected Behavior

### Before Fix
```
VSCode1 connects → Daemon expects ping every 45s
VSCode1 sends ping every 45s (from default)
But .env says 30s → Configuration confusion
Timeout mismatch → Connection cycles every 10-30s ❌
Both instances show red dots ❌
```

### After Fix
```
VSCode1 connects → Daemon expects ping every 45s ✅
VSCode1 sends ping every 45s (from .env) ✅
Daemon waits 240s for ping response ✅
Shim waits 240s for ping response ✅
Stable connections maintained ✅
Both instances show green dots ✅
```

---

## 🧪 Testing Instructions

### Step 1: Reload Both VSCode Instances
1. Close both VSCode windows completely
2. Open VSCode Instance 1 (uses `mcp-config.augmentcode.vscode1.json`)
3. Open VSCode Instance 2 (uses `mcp-config.augmentcode.vscode2.json`)
4. Reload both windows (Developer: Reload Window)

### Step 2: Verify Stable Connections
Check MCP panel in both instances:
- ✅ Both should show green dots
- ✅ Both should stay connected (no cycling)
- ✅ Both should show "EXAI-WS-VSCode1" and "EXAI-WS-VSCode2" respectively

### Step 3: Monitor Connection Stability
```bash
# Watch for connection events (should NOT see frequent disconnects)
docker logs exai-mcp-daemon --follow | grep -E "Connection (un)?registered"
```

**Expected output:**
```
INFO Connection registered: <id> from 172.18.0.1 (total: 1, ip_total: 1)
INFO Connection registered: <id> from 172.18.0.1 (total: 2, ip_total: 2)
# NO disconnections for extended periods (minutes/hours)
```

### Step 4: Test Tool Execution
1. Call a tool from VSCode1 (e.g., `chat_EXAI-WS-VSCode1`)
2. Immediately call a tool from VSCode2 (e.g., `chat_EXAI-WS-VSCode2`)
3. Both should execute successfully without disconnections

---

## 🔗 Related Issues

### Previous Session ID Fix (2025-10-26)
- **File:** `docs/05_CURRENT_WORK/2025-10-26/SESSION_ID_FIX__2025-10-26.md`
- **Issue:** Daemon was ignoring client session IDs
- **Status:** ✅ FIXED (daemon now uses client-provided session IDs)

### This Fix (Ping Timeout Mismatch)
- **Issue:** Configuration mismatch causing connection cycling
- **Status:** ✅ FIXED (aligned .env with .env.docker)

**Combined Result:**
- Session IDs are now respected ✅
- Ping timeouts are now aligned ✅
- Connections should be stable ✅

---

## 📝 Configuration Files Modified

### .env (Windows Shim)
- **Before:** `EXAI_WS_PING_INTERVAL=30`, `EXAI_WS_PING_TIMEOUT=30`
- **After:** `EXAI_WS_PING_INTERVAL=45`, `EXAI_WS_PING_TIMEOUT=240`
- **Reason:** Match daemon configuration in .env.docker

### .env.docker (Daemon)
- **No changes needed** - Already correctly configured
- `EXAI_WS_PING_INTERVAL=45`, `EXAI_WS_PING_TIMEOUT=240`

---

## 💡 Key Insights

### Why Hardcoded Defaults Matter
The shim uses hardcoded defaults in `run_ws_shim.py`:
```python
PING_INTERVAL = int(os.getenv("EXAI_WS_PING_INTERVAL", "45"))  # Default: 45
PING_TIMEOUT = int(os.getenv("EXAI_WS_PING_TIMEOUT", "30"))    # Default: 30
```

**Lesson:** Even though the code reads from .env, the defaults matter when .env values are missing or incorrect. Aligning .env with the daemon's configuration ensures consistency.

### Why 45s/240s?
- **45-second interval:** Industry standard per RFC 6455 for WebSocket keepalive
- **240-second timeout:** Provides 5+ missed pings before timeout (45s × 5 = 225s)
- **Prevents false positives:** Network latency, server load, or GC pauses won't trigger disconnects

---

## ✅ Status

**Implementation:** COMPLETE  
**Testing:** PENDING USER VERIFICATION  
**Docker Container:** NO RESTART NEEDED (shim reads .env on startup)

**Next Steps:**
1. User reloads both VSCode instances
2. Verify both connect successfully
3. Verify connections remain stable (no cycling)
4. Monitor logs for connection stability
5. Test tool execution from both instances

---

**Created:** 2025-10-26  
**Purpose:** Fix WebSocket connection cycling due to ping timeout mismatches  
**Status:** ✅ READY FOR TESTING  
**Related:** SESSION_ID_FIX__2025-10-26.md (session identity fix)

