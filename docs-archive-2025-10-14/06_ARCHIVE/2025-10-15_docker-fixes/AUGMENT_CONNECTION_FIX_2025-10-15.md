# Augment Connection Fix
**Date:** 2025-10-15 11:55 AEDT (23:55 UTC)  
**Status:** ✅ **FIXED - Requires Augment Reload**

---

## Problem Summary

Augment MCP connection to Docker daemon was failing with handshake errors. Investigation revealed multiple configuration issues.

---

## Root Causes Identified

### 1. **Autostart Enabled** ⚠️ CRITICAL
- **Issue:** `EXAI_WS_AUTOSTART` was set to `true` (default)
- **Impact:** When connection failed, shim tried to start a LOCAL daemon
- **Conflict:** Local daemon conflicts with Docker daemon on port 8079
- **Solution:** Set `EXAI_WS_AUTOSTART=false` in Augment config

### 2. **Short Timeouts**
- **Issue:** Default connection timeout was 10 seconds
- **Impact:** Docker connections may need more time on first connect
- **Solution:** Increased timeouts to 30 seconds

### 3. **Missing Environment Variables**
- **Issue:** Augment config didn't explicitly set all required variables
- **Impact:** Shim used defaults which weren't optimal for Docker
- **Solution:** Added explicit configuration in Augment config

---

## Solutions Implemented

### **Updated `Daemon/mcp-config.augmentcode.json`**

Added the following environment variables:

```json
{
  "mcpServers": {
    "EXAI-WS": {
      "env": {
        "EXAI_WS_HOST": "127.0.0.1",
        "EXAI_WS_PORT": "8079",
        "EXAI_WS_SKIP_HEALTH_CHECK": "true",
        "EXAI_WS_AUTOSTART": "false",           // ⭐ NEW - Prevents local daemon start
        "EXAI_WS_CONNECT_TIMEOUT": "30",        // ⭐ NEW - Increased timeout
        "EXAI_WS_HANDSHAKE_TIMEOUT": "30",      // ⭐ NEW - Increased timeout
        ...
      }
    }
  }
}
```

### **Key Changes:**

1. **`EXAI_WS_AUTOSTART=false`** - Prevents shim from trying to start local daemon
2. **`EXAI_WS_CONNECT_TIMEOUT=30`** - Gives more time for Docker connection
3. **`EXAI_WS_HANDSHAKE_TIMEOUT=30`** - Gives more time for hello handshake

---

## Verification

### **Test 1: Direct WebSocket Connection** ✅
```bash
python scripts/test_localhost_connection.py
```
**Result:** ✅ Connection successful with `127.0.0.1:8079`

### **Test 2: Shim Connection** ✅
```bash
python scripts/test_shim_connection.py
```
**Result:** ✅ Shim successfully connects to Docker daemon

### **Test 3: Docker Daemon Status** ✅
```bash
docker ps --filter "name=exai-mcp-daemon"
```
**Result:** ✅ Container running and healthy

---

## Required Action: Reload Augment Configuration

**⚠️ IMPORTANT:** Augment needs to reload the MCP configuration to pick up the changes.

### **How to Reload Augment MCP Configuration:**

#### **Option 1: Restart VS Code** (Recommended)
1. Close VS Code completely
2. Reopen VS Code
3. Augment will automatically load the new configuration

#### **Option 2: Reload Window**
1. Press `Ctrl+Shift+P` (Windows) or `Cmd+Shift+P` (Mac)
2. Type "Developer: Reload Window"
3. Press Enter

#### **Option 3: Disable/Enable MCP Server**
1. Open Augment settings
2. Disable the EXAI-WS MCP server
3. Wait 5 seconds
4. Enable the EXAI-WS MCP server

---

## Verification After Reload

After reloading Augment, test the connection by:

1. **Open Augment chat**
2. **Try an EXAI tool** (e.g., ask "Use the chat tool to explain Docker")
3. **Check logs:**
   ```bash
   # Check shim logs
   Get-Content logs/ws_shim.log -Tail 20
   
   # Check Docker logs
   docker logs exai-mcp-daemon --tail 20
   ```

### **Expected Results:**

**Shim logs should show:**
```
INFO ws_shim: Skipping daemon health check (EXAI_WS_SKIP_HEALTH_CHECK=true) - connecting to 127.0.0.1:8079
INFO ws_shim: Successfully connected to WebSocket daemon at ws://127.0.0.1:8079
```

**Docker logs should show:**
```
INFO websockets.server: connection open
INFO src.daemon.session_manager: [SESSION_MANAGER] Created session ...
INFO ws_daemon: === TOOL CALL START ===
INFO ws_daemon: Tool: chat
```

---

## Troubleshooting

### **If connection still fails:**

1. **Check Docker is running:**
   ```bash
   docker ps --filter "name=exai-mcp-daemon"
   ```
   Should show container as `Up (healthy)`

2. **Verify port is accessible:**
   ```bash
   python scripts/test_localhost_connection.py
   ```
   Should show successful connection

3. **Check shim logs for errors:**
   ```bash
   Get-Content logs/ws_shim.log -Tail 50
   ```

4. **Verify .env file has correct token:**
   ```bash
   Select-String -Path .env -Pattern "EXAI_WS_TOKEN"
   ```
   Should show: `EXAI_WS_TOKEN=test-token-12345` (no inline comments)

5. **Check Augment loaded the config:**
   - Look for "EXAI-WS" in Augment MCP servers list
   - Verify it shows as "Connected" or "Active"

---

## Files Modified

| File | Changes | Purpose |
|------|---------|---------|
| `Daemon/mcp-config.augmentcode.json` | Added EXAI_WS_AUTOSTART=false, increased timeouts | Fix Augment connection |
| `scripts/test_shim_connection.py` | Created test script | Verify shim connection |

---

## Technical Details

### **Why Autostart Caused Issues:**

1. Augment starts the shim process
2. Shim tries to connect to `127.0.0.1:8079` (Docker)
3. If connection fails or times out, shim checks `EXAI_WS_AUTOSTART`
4. If `true`, shim tries to start a local daemon with `run_ws_daemon.py`
5. Local daemon tries to bind to port 8079
6. **CONFLICT:** Port 8079 is already in use by Docker
7. Local daemon fails to start
8. Shim gives up and reports connection failure

### **Solution:**

Setting `EXAI_WS_AUTOSTART=false` tells the shim:
- "Don't try to start a local daemon"
- "Just connect to the existing daemon at 127.0.0.1:8079"
- "If connection fails, report the error (don't try to fix it)"

This is the correct behavior when using Docker, because:
- Docker daemon is managed separately (via `docker run`)
- We don't want multiple daemons competing for the same port
- Connection failures should be reported, not auto-fixed

---

## Next Steps

1. ✅ Configuration updated
2. ✅ Tests passing
3. ⏳ **Reload Augment** (user action required)
4. ⏳ **Test EXAI tools** (after reload)
5. ⏳ **Verify logs** (after reload)

---

**Last Updated:** 2025-10-15 11:55 AEDT (23:55 UTC)  
**Status:** ✅ **Configuration fixed, awaiting Augment reload**

