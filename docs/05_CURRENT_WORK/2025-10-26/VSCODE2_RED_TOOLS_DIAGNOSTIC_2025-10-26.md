# VSCode2 Red Tools Diagnostic - 2025-10-26

**Date:** 2025-10-26  
**Issue:** VSCode2 shows all EXAI tools as RED (unavailable) while VSCode1 works fine  
**Status:** 🔍 INVESTIGATING

---

## 📊 **Current System Status**

### ✅ **What's Working:**
- Docker daemon: HEALTHY (PID 1, 4 sessions, 31 tools)
- Port 8079: LISTENING (12 active connections)
- Shim connections: SUCCESSFUL (logs show "Successfully connected")
- Health checks: PASSING
- VSCode1: ALL TOOLS WORKING

### ❌ **What's Broken:**
- VSCode2: ALL TOOLS SHOWING RED

---

## 🔍 **Root Cause Analysis**

### **Key Observation:**
Shim logs show **successful connections** to the daemon, but VSCode2 still shows red tools. This indicates:

**The daemon connection is working, but the VSCode MCP client is not recognizing the tools.**

### **Most Likely Causes (in order of probability):**

1. **VSCode2 is not using the correct MCP config file** (90% likely)
   - VSCode settings.json doesn't point to `mcp-config.augmentcode.vscode2.json`
   - OR it's pointing to the wrong file

2. **VSCode MCP extension hasn't loaded the config** (5% likely)
   - Extension needs restart/reload
   - Extension cache issue

3. **MCP extension bug/crash** (5% likely)
   - Extension crashed silently
   - Extension not installed/enabled

---

## 🛠️ **Diagnostic Steps**

### **Step 1: Run Connection Test (RECOMMENDED)**

I've created a diagnostic script that tests the connection directly:

```bash
# Run this in VSCode2's terminal
python scripts/test_vscode2_connection.py
```

**What it tests:**
1. Port connectivity (can reach 8079?)
2. WebSocket connection (can connect?)
3. Hello handshake (authentication working?)
4. List tools (can retrieve tool list?)
5. Call chat tool (can execute tools?)

**Expected outcome:**
- If ALL TESTS PASS → Issue is VSCode MCP client-side
- If ANY TEST FAILS → Issue is daemon/network-side

---

### **Step 2: Verify VSCode2 MCP Configuration**

**In VSCode2:**

1. Press `Ctrl+Shift+P`
2. Type: **"Preferences: Open User Settings (JSON)"**
3. Look for the `mcp` section
4. **Expected:**
   ```json
   {
     "mcp": {
       "configPath": "C:/Project/EX-AI-MCP-Server/Daemon/mcp-config.augmentcode.vscode2.json"
     }
   }
   ```

5. **If missing or wrong:**
   - Add/update the `mcp.configPath` setting
   - Save the file
   - Proceed to Step 3

---

### **Step 3: Reload VSCode2 Window**

**In VSCode2:**

1. Press `Ctrl+Shift+P`
2. Type: **"Developer: Reload Window"**
3. Press Enter
4. Wait 10 seconds
5. Check if tools are still red

---

### **Step 4: Restart MCP Server (if Step 3 didn't work)**

**In VSCode2:**

1. Press `Ctrl+Shift+P`
2. Type: **"MCP: Restart Server"** (if this command exists)
3. OR try: **"MCP: Show Status"** to see error messages

---

### **Step 5: Check MCP Extension Logs**

**In VSCode2:**

1. Press `Ctrl+Shift+P`
2. Type: **"Output: Show Output Channels"**
3. Select **"MCP"** from the dropdown
4. Look for error messages

Common errors:
- "Failed to load config file"
- "Connection timeout"
- "Invalid config format"

---

## 🔧 **Quick Fixes to Try**

### **Fix 1: Reload Window (Fastest)**
```
Ctrl+Shift+P → "Developer: Reload Window"
```

### **Fix 2: Update MCP Config Path**
```json
// In VSCode2 settings.json
{
  "mcp": {
    "configPath": "C:/Project/EX-AI-MCP-Server/Daemon/mcp-config.augmentcode.vscode2.json"
  }
}
```

### **Fix 3: Nuclear Option (Last Resort)**
1. Close VSCode2 completely
2. Delete workspace storage:
   - Windows: `%APPDATA%\Code\User\workspaceStorage\`
   - Find folders related to your project
   - Delete them
3. Reopen VSCode2
4. Reconfigure MCP settings

---

## 📝 **Configuration Files**

### **VSCode1 Config (Working)**
**File:** `Daemon/mcp-config.augmentcode.vscode1.json`
```json
{
  "mcpServers": {
    "EXAI-WS-VSCode1": {
      "type": "stdio",
      "env": {
        "EXAI_SESSION_ID": "vscode-instance-1",
        "MCP_SERVER_ID": "exai-ws-vscode1"
      }
    }
  }
}
```

### **VSCode2 Config (Should be used)**
**File:** `Daemon/mcp-config.augmentcode.vscode2.json`
```json
{
  "mcpServers": {
    "EXAI-WS-VSCode2": {
      "type": "stdio",
      "env": {
        "EXAI_SESSION_ID": "vscode-instance-2",
        "MCP_SERVER_ID": "exai-ws-vscode2"
      }
    }
  }
}
```

---

## 🔬 **Advanced Diagnostics**

### **Check Which Session ID is Being Used**

Run this in VSCode2's terminal:
```bash
# Check environment variables
echo $env:EXAI_SESSION_ID  # PowerShell
echo %EXAI_SESSION_ID%     # CMD
```

### **Check Active Sessions in Daemon**
```bash
docker logs exai-mcp-daemon --tail 50 | findstr "SESSION"
```

Should show both:
- `vscode-instance-1`
- `vscode-instance-2`

### **Check Shim Logs for Session ID**
```bash
Get-Content logs\ws_shim.log -Tail 100 | Select-String "session_id"
```

---

## 📊 **Expected vs Actual Behavior**

### **Expected (Both VSCode instances):**
- ✅ All EXAI tools visible (green)
- ✅ Can call tools successfully
- ✅ Separate session IDs in logs
- ✅ Independent request processing

### **Actual:**
- ✅ VSCode1: All tools working
- ❌ VSCode2: All tools RED
- ✅ Daemon: Healthy and accepting connections
- ✅ Shim: Successfully connecting

**Conclusion:** Issue is VSCode MCP client-side, not daemon-side.

---

## 🎯 **Next Steps**

1. **Run diagnostic script** in VSCode2: `python scripts/test_vscode2_connection.py`
2. **Check VSCode2 settings.json** for `mcp.configPath`
3. **Reload VSCode2 window**
4. **Report results** - Did the diagnostic script pass? Are tools still red?

---

## 📞 **If Issue Persists**

If all diagnostic steps pass but tools are still red:

1. **Check VSCode MCP extension version**
   - Extensions panel → Search "MCP"
   - Check if update available

2. **Reinstall MCP extension**
   - Uninstall MCP extension
   - Restart VSCode2
   - Reinstall MCP extension

3. **Check VSCode logs**
   - Help → Toggle Developer Tools
   - Console tab → Look for MCP-related errors

---

**Created:** 2025-10-26  
**Purpose:** Diagnostic guide for VSCode2 red tools issue  
**Status:** 🔍 Awaiting diagnostic script results

