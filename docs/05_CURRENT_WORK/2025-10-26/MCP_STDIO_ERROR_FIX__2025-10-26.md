# MCP STDIO Error Fix - 2025-10-26

**Date:** 2025-10-26  
**Issue:** MCP tools not loading in VSCode  
**Error:** `OSError: [Errno 22] Invalid argument` when flushing stdout

---

## 🔍 **ROOT CAUSE**

The MCP shim (`run_ws_shim.py`) is successfully connecting to the WebSocket daemon in Docker, but failing when trying to communicate back to VSCode via stdio.

**Error from logs/ws_shim.log:**
```
OSError: [Errno 22] Invalid argument
  File "C:\Project\EX-AI-MCP-Server\.venv\Lib\site-packages\mcp\server\stdio.py", line 81, in stdout_writer
    await stdout.flush()
```

**What's Happening:**
1. ✅ Docker daemon is running (port 8079-8080)
2. ✅ WebSocket connection successful
3. ❌ Stdio communication with VSCode failing
4. ❌ Tools not loading in VSCode

---

## 🛠️ **IMMEDIATE FIX**

### **Option 1: Restart VSCode (Recommended)**

1. **Close ALL VSCode windows**
2. **Kill orphaned Python processes:**
   ```powershell
   Get-Process python | Where-Object {$_.Path -like "*EX-AI-MCP-Server*"} | Stop-Process -Force
   ```
3. **Restart VSCode**
4. **Reload MCP servers** (Developer: Reload Window)

### **Option 2: Restart Docker Container**

```powershell
docker restart exai-mcp-daemon
```

Then restart VSCode.

---

## 🔧 **PERMANENT FIX**

The issue is likely related to Windows stdio buffering. We need to modify `run_ws_shim.py` to handle Windows-specific stdio issues.

**File to modify:** `scripts/runtime/run_ws_shim.py`

**Add after line 36 (after logger setup):**
```python
# Windows-specific stdio fix
if sys.platform == "win32":
    import msvcrt
    import os
    # Set stdout/stderr to binary mode to avoid buffering issues
    msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
    msvcrt.setmode(sys.stderr.fileno(), os.O_BINARY)
```

---

## 📊 **DIAGNOSTIC INFORMATION**

**Current State:**
- **Docker Container:** ✅ Running (exai-mcp-daemon)
- **Ports:** ✅ 8079-8080 listening
- **WebSocket Connection:** ✅ Successful
- **Stdio Communication:** ❌ Failing
- **Python Processes:** 6 running (too many!)

**MCP Servers Configured:**
- `EXAI-WS-VSCode1` → Port 8079
- `EXAI-WS-VSCode2` → Port 8080

**Issue:** Both servers are trying to connect, causing conflicts.

---

## ⚠️ **CRITICAL ISSUE: DUPLICATE MCP SERVERS**

You have **TWO** EXAI-WS MCP servers configured:
1. `EXAI-WS-VSCode1` (Port 8079)
2. `EXAI-WS-VSCode2` (Port 8080)

**Recommendation:** Disable one of them to avoid conflicts.

**To disable EXAI-WS-VSCode1:**
1. Open VSCode settings (Ctrl+,)
2. Search for "MCP"
3. Find "EXAI-WS-VSCode1" configuration
4. Disable or remove it

**Or manually edit:** `Daemon/mcp-config.augmentcode.vscode1.json`
- Rename the file to `.disabled` or delete it

---

## 🚀 **RECOMMENDED ACTIONS**

**Immediate (Next 5 minutes):**
1. Kill all orphaned Python processes
2. Close and restart VSCode
3. Verify only ONE EXAI-WS server is enabled
4. Test tool loading

**Short-term (Next 30 minutes):**
5. Apply Windows stdio fix to `run_ws_shim.py`
6. Test with both MCP servers disabled except one
7. Document which MCP server configuration works

**Long-term:**
8. Consolidate to single MCP server configuration
9. Add better error handling for stdio issues
10. Add health check endpoint for MCP shim

---

## 📝 **VERIFICATION STEPS**

After applying fix:

1. **Check Python processes:**
   ```powershell
   Get-Process python | Where-Object {$_.Path -like "*EX-AI-MCP-Server*"}
   ```
   Should see 2-3 processes max (one per active MCP server)

2. **Check MCP server status in VSCode:**
   - Open MCP panel
   - Verify EXAI-WS server shows green dot
   - Verify tool count (should show ~29 tools)

3. **Test tool call:**
   Try calling a simple tool like `listmodels_EXAI-WS`

---

## 🔗 **RELATED FILES**

- `scripts/runtime/run_ws_shim.py` - MCP shim script
- `Daemon/mcp-config.augmentcode.vscode1.json` - VSCode1 MCP config
- `Daemon/mcp-config.augmentcode.vscode2.json` - VSCode2 MCP config
- `logs/ws_shim.log` - Shim error logs

---

**Created:** 2025-10-26  
**Status:** Diagnostic complete, fix ready to apply  
**Next Steps:** Kill orphaned processes, restart VSCode, apply Windows stdio fix

