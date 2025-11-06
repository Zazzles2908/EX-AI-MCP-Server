# NEXT STEPS - Enable Claude Code to Use EXAI Tools

## Current Status

✅ **Monitoring refactoring:** Complete
✅ **EXAI server:** Running (Docker containers healthy)
✅ **WebSocket connection:** Working (tested successfully)
✅ **19 workflow tools:** Registered and available

⚠️ **Missing:** VSCode MCP configuration for Claude Code to use tools

---

## What You Need to Do

### Step 1: Create VSCode Config in Your Project

**Option A: If you want to use EXAI in THIS project:**
```bash
# Already exists!
cat .vscode/settings.json
```

**Option B: If you want to use EXAI in ANOTHER project:**
```bash
# Create the file in your other project:
code /path/to/your/other/project
# Then create .vscode/settings.json with the config from EXAI_MCP_SETUP_GUIDE.md
```

### Step 2: Verify in VSCode

1. Open VSCode with the project that has `.vscode/settings.json`
2. Look for: `"EXAI MCP Server connected"` in the output
3. Test: Try `@exai listmodels` in Claude Code

### Step 3: Use EXAI Tools

Once connected, you can use all 19 workflow tools:

```markdown
@exai analyze src/monitoring/resilient_websocket.py
@exai debug "I have a bug in my WebSocket manager"
@exai testgen test_file.py
@exai codereview --focus security --path src/
@exai thinkdeep "How does this system work?"
@exai consensus "What's the best fix for this?"
```

---

## Quick Copy-Paste Config

**For ANY project, add this to `.vscode/settings.json`:**

```json
{
  "chat.mcp.autostart": "never",
  "chat.mcp.servers": {
    "exai-mcp": {
      "transport": "stdio",
      "command": "C:/Project/EX-AI-MCP-Server/.venv/Scripts/python.exe",
      "args": ["-u", "C:/Project/EX-AI-MCP-Server/scripts/runtime/run_ws_shim.py"],
      "cwd": "C:/Project/EX-AI-MCP-Server",
      "env": {
        "PYTHONPATH": "C:/Project/EX-AI-MCP-Server",
        "ENV_FILE": "C:/Project/EX-AI-MCP-Server/.env",
        "EXAI_WS_HOST": "127.0.0.1",
        "EXAI_WS_PORT": "8079",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

**Adjust paths for your OS:**
- Windows: `C:/Project/EX-AI-MCP-Server/.venv/Scripts/python.exe`
- Linux/Mac: `/path/to/EX-AI-MCP-Server/.venv/bin/python`

---

## Testing

### Verify EXAI is Running:
```bash
docker exec exai-mcp-daemon python -c "import requests; print(requests.get('http://localhost:8082/health').json()['status'])"
```
**Expected:** `healthy`

### Test WebSocket Connection:
```bash
docker exec exai-mcp-daemon python -c "import websockets, asyncio, json, os; asyncio.run(websockets.connect('ws://localhost:8079/ws').__aenter__().send(json.dumps({'op': 'ping'})))"
```
**Expected:** No errors

### In VSCode:
1. Open Claude Code chat
2. Type: `@exai listmodels`
3. **Expected:** List of available models

---

## What Happens Next

Once you set up VSCode with the MCP config:

1. **Claude Code auto-discovers** EXAI tools
2. **You can call any tool** with `@exai <tool_name>`
3. **Each VSCode window** gets independent connection
4. **No bottlenecks** - all connections run async

---

## Available Tools (19 total)

| Category | Tools |
|----------|-------|
| **Analysis** | `analyze`, `thinkdeep`, `tracer` |
| **Quality** | `codereview`, `testgen`, `docgen` |
| **Debug** | `debug`, `precommit` |
| **Refactor** | `refactor` |
| **Security** | `secaudit` |
| **Planning** | `planner`, `consensus` |
| **Models** | `listmodels`, `kimi_chat_with_tools`, `chat`, `glm_payload_preview` |
| **System** | `status`, `version`, `smart_file_query` |

---

## Files Created

- ✅ `EXAI_MCP_SETUP_GUIDE.md` - Complete setup instructions
- ✅ `REFACTORING_MONITORING_ENDPOINT.md` - Detailed refactoring report
- ✅ `REFACTORING_SUMMARY.md` - Summary with setup notes
- ✅ `NEXT_STEPS.md` - This file

---

## Summary

**To use EXAI tools in Claude Code:**

1. ✅ Docker running (done)
2. ✅ EXAI healthy (done)
3. ⚠️ Add `.vscode/settings.json` (do this)
4. ⚠️ Open project in VSCode (do this)
5. ⚠️ Reload VSCode (do this)
6. ✅ Use `@exai` tools (then you can do this!)

**That's it! Follow these steps and you'll have full access to EXAI's workflow tools in Claude Code.** 🚀
