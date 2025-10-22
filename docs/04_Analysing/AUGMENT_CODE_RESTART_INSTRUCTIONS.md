# Augment Code Restart Instructions - 2025-10-21

## 🔄 WHY YOU NEED TO RESTART

We just reorganized the scripts directory and updated the MCP configuration:
- **Old path:** `scripts/run_ws_shim.py`
- **New path:** `scripts/runtime/run_ws_shim.py`

The configuration file `Daemon/mcp-config.augmentcode.json` has been updated with the new path, but **Augment Code is still using the old cached configuration**.

---

## ✅ VERIFICATION

The configuration file is **CORRECT**:

<augment_code_snippet path="Daemon\mcp-config.augmentcode.json" mode="EXCERPT">
````json
{
  "mcpServers": {
    "EXAI-WS": {
      "type": "stdio",
      "trust": true,
      "command": "C:/Project/EX-AI-MCP-Server/.venv/Scripts/python.exe",
      "args": ["-u", "C:/Project/EX-AI-MCP-Server/scripts/runtime/run_ws_shim.py"],
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
````
</augment_code_snippet>

The file exists at the correct location:
```
✅ C:\Project\EX-AI-MCP-Server\scripts\runtime\run_ws_shim.py
```

The Docker container is running and healthy:
```
✅ exai-mcp-daemon - Up 10 minutes (healthy)
✅ WebSocket daemon listening on port 8079
```

---

## 🔧 HOW TO RESTART AUGMENT CODE

### **Option 1: Restart Augment Code (Recommended)**

1. **Close Augment Code completely**
   - Click the Augment icon in the system tray (bottom-right corner)
   - Select "Quit" or "Exit"

2. **Wait 5 seconds**

3. **Reopen Augment Code**
   - The new configuration will be loaded automatically

---

### **Option 2: Reload MCP Configuration (If Available)**

If Augment Code has a "Reload MCP Configuration" option:
1. Open Augment Code settings
2. Look for MCP or Server configuration section
3. Click "Reload" or "Refresh"

---

### **Option 3: Toggle MCP Server (Alternative)**

If restarting doesn't work:
1. Open Augment Code settings
2. Find the EXAI-WS MCP server
3. **Disable** the server
4. Wait 5 seconds
5. **Enable** the server again

---

## ✅ VERIFICATION AFTER RESTART

After restarting Augment Code, verify the connection works:

1. **Try using an EXAI tool** (e.g., `chat_EXAI-WS`)
2. **Check for errors** in the Augment Code console
3. **If it works:** You should see successful tool calls! 🎉

---

## 🐛 TROUBLESHOOTING

### **If you still get errors:**

1. **Check the error message** - Does it mention the old path `scripts/run_ws_shim.py`?
   - If YES: Augment Code is still using the old config
   - Try Option 3 (Toggle MCP Server)

2. **Check Docker is running:**
   ```powershell
   docker-compose ps
   ```
   - Should show `exai-mcp-daemon` as "Up" and "healthy"

3. **Check WebSocket daemon is listening:**
   ```powershell
   Test-NetConnection -ComputerName 127.0.0.1 -Port 8079
   ```
   - Should show "TcpTestSucceeded: True"

4. **Check logs for errors:**
   ```powershell
   docker-compose logs --tail=50 exai-daemon
   ```

---

## 📝 WHAT WE CHANGED

**Files Moved:**
- `scripts/run_ws_shim.py` → `scripts/runtime/run_ws_shim.py`
- `scripts/health_check.py` → `scripts/runtime/health_check.py`

**Configuration Files Updated:**
- ✅ `Daemon/mcp-config.augmentcode.json`
- ✅ `Daemon/mcp-config.claude.json`
- ✅ `Daemon/mcp-config.auggie.json`
- ✅ `Daemon/mcp-config.template.json`
- ✅ `Dockerfile`
- ✅ `docker-compose.yml`

**Everything is correct** - you just need to restart Augment Code to pick up the new configuration! 🚀

---

## 🎯 NEXT STEPS AFTER RESTART

Once Augment Code is working again:
1. ✅ Verify EXAI tools work
2. Continue with Phase 4: Move config.py and server.py to src/
3. Complete Phase 5: Final rebuild and comprehensive testing

---

**Need help?** Check the Docker logs or ask me to investigate further!

