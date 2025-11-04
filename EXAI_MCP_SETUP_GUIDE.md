# EXAI MCP Setup Guide for Claude Code

## Overview

EXAI provides **19 workflow tools** that Claude Code can use via the Model Context Protocol (MCP). This guide explains how to set up Claude Code to connect to EXAI and use these tools.

---

## What You Get

✅ **19 Workflow Tools Available:**
1. `analyze` - Comprehensive code analysis
2. `chat` - AI chat with models
3. `codereview` - Code review and feedback
4. `consensus` - Multi-model consensus
5. `debug` - Debug code issues
6. `docgen` - Generate documentation
7. `glm_payload_preview` - Preview GLM API payloads
8. `kimi_chat_with_tools` - Chat with Kimi model
9. `listmodels` - List available AI models
10. `planner` - Task planning
11. `precommit` - Pre-commit validation
12. `refactor` - Code refactoring
13. `secaudit` - Security audit
14. `smart_file_query` - Query files with AI
15. `status` - System status
16. `testgen` - Generate tests
17. `thinkdeep` - Deep analysis
18. `tracer` - Code tracing
19. `version` - Version information

---

## Prerequisites

✅ **Docker containers running:**
```bash
docker-compose ps
# Should show: exai-mcp-daemon (healthy)
```

---

## Step 1: VSCode Configuration

### Create/Update `.vscode/settings.json` in your project:

```json
{
  "chat.mcp.autostart": "never",
  "chat.mcp.servers": {
    "exai-mcp": {
      "transport": "stdio",
      "command": "python",
      "args": ["-u", "C:\\Project\\EX-AI-MCP-Server\\scripts\\runtime\\run_ws_shim.py"],
      "cwd": "C:\\Project\\EX-AI-MCP-Server",
      "env": {
        "VIRTUAL_ENV": "C:\\Project\\EX-AI-MCP-Server\\.venv",
        "PATH": "C:\\Project\\EX-AI-MCP-Server\\.venv\\Scripts;C:\\Project\\EX-AI-MCP-Server\\.venv\\Scripts\\Scripts\\Windows;$PATH",
        "PYTHONPATH": "C:\\Project\\EX-AI-MCP-Server",
        "ENV_FILE": "C:\\Project\\EX-AI-MCP-Server\\.env",
        "EXAI_WS_HOST": "127.0.0.1",
        "EXAI_WS_PORT": "8079",
        "LOG_LEVEL": "INFO"
      }
    }
  },
  "chat.mcp.access": "all"
}
```

**Key Configuration Notes:**
- ✅ Uses `"python"` command with `VIRTUAL_ENV` to force virtual environment
- ✅ `"chat.mcp.access": "all"` enables MCP connections
- ✅ Adjust paths for your OS if needed:
  - **Windows:** `C:\\Project\\EX-AI-MCP-Server\\.venv\\Scripts\\python.exe`
  - **Linux/Mac:** `/path/to/EX-AI-MCP-Server/.venv/bin/python`

---

## Step 2: Verify Connection

### Check if EXAI is running:
```bash
docker exec exai-mcp-daemon python -c "import requests; print(requests.get('http://localhost:8082/health').json()['status'])"
```

**Expected Output:** `healthy`

---

## Step 3: Connect VSCode

### Option A: Use VSCode UI
1. Open your project in VSCode
2. Create `.vscode/settings.json` with the config above
3. Reload VSCode window (`Ctrl/Cmd + Shift + P` → "Developer: Reload Window")
4. Look for "EXAI MCP Server connected" in the output

### Option B: Use Command Line
```bash
code /path/to/your/project
```

Then create the `.vscode/settings.json` file.

---

## Step 4: Use EXAI Tools in Claude Code

Once connected, you can use EXAI tools in Claude Code:

### Basic Usage

```
@exai analyze <file_or_path>
```

**Examples:**

```markdown
# Analyze a file
@exai analyze src/monitoring/resilient_websocket.py

# Debug an issue
@exai debug "I have a memory leak in my WebSocket manager"

# Generate tests
@exai testgen test_user_login.py

# Code review
@exai codereview --focus security --path src/

# Deep analysis
@exai thinkdeep "How does this monitoring system work?"

# Multi-model consensus
@exai consensus "What's the best approach to fix this bug?"

# Security audit
@exai secaudit --focus authentication --path src/auth/

# Refactor code
@exai refactor --pattern simplify --path src/utils/

# List available models
@exai listmodels
```

---

## Step 5: Multi-Instance Setup

### Multiple VSCode Windows (Same Machine)

Each VSCode window gets its own connection to EXAI:

1. **Window 1:** Open with `.vscode/settings.json` → Connection #1
2. **Window 2:** Same config → Connection #2
3. **Window N:** Same config → Connection #N

**Each connection is independent** - no bottlenecks!

### Different Machines (Network Access)

**On EXAI Server:**
```bash
# Server already listens on 0.0.0.0 in Docker
# No changes needed
```

**On Client Machines:**
```json
{
  "chat.mcp.servers": {
    "exai-mcp": {
      "command": "/path/to/python",
      "args": ["-u", "/path/to/run_ws_shim.py"],
      "env": {
        "EXAI_WS_HOST": "192.168.1.100",  ← Server IP
        "EXAI_WS_PORT": "8079"
      }
    }
  }
}
```

---

## Connection Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    VSCode with Claude Code                  │
│                                                                  │
│  Claude Code (MCP Client)                                       │
│  ↓ (MCP stdio protocol)                                         │
│  .vscode/settings.json                                          │
│  ↓                                                              │
│  scripts/runtime/run_ws_shim.py (MCP ⇄ WebSocket bridge)       │
└────────────────────────┬────────────────────────────────────────┘
                         ↓ (WebSocket)
┌────────────────────────┴────────────────────────────────────────┐
│                  Docker Container: exai-mcp-daemon               │
│                                                                  │
│  WebSocket Server (ws://0.0.0.0:8079/ws)                        │
│  - Handles authentication                                       │
│  - Routes tool calls                                            │
│  - Executes workflows (analyze, debug, etc.)                    │
│  - Returns results                                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## Verification Checklist

- [x] Docker containers running (`docker-compose ps`) ✅
- [x] EXAI health check passing (`healthy`) ✅
- [x] `.vscode/settings.json` created with correct paths ✅
- [x] VSCode reloaded with new config ⚠️ **(reload now if not done)**
- [ ] "EXAI MCP Server connected" message visible ⏳ **(check after reload)**
- [ ] Can run `@exai listmodels` successfully ⏳ **(test after connection)**

### Verification Steps in VSCode

After configuring VSCode and reloading the window:

1. **Open Output Panel:**
   - Press `Ctrl+Shift+U` (Windows/Linux) or `Cmd+Shift+U` (Mac)
   - Select "Claude Code" from the dropdown

2. **Look for Connection Message:**
   ```
   [SHIM_STARTUP] Starting EXAI MCP WebSocket Shim...
   [EXAI_WS] Connected to daemon
   EXAI MCP Server connected
   ```

3. **Test Tool Discovery:**
   In Claude Code, type: `@exai listmodels`
   **Expected:** List of 21 available models/tools

4. **Test a Tool:**
   Try: `@exai version`
   **Expected:** Version information from EXAI

---

## Troubleshooting

### "Connection Failed" Error

**Check:**
1. Docker containers running: `docker-compose ps`
2. EXAI_WS_PORT correct (default: 8079)
3. Path to `run_ws_shim.py` correct

### "Tool Not Found" Error

**Check:**
1. Tool name spelling (e.g., `analyze`, not `Analyse`)
2. Tools registered: `@exai listmodels`

### "Server Not Running" Error

**Fix:**
```bash
cd C:/Project/EX-AI-MCP-Server
docker-compose up -d exai-mcp-daemon
```

---

## Available Tools Reference

| Tool | Purpose | Example |
|------|---------|---------|
| `analyze` | Code analysis | `@exai analyze src/file.py` |
| `chat` | Chat with models | `@exai chat "Explain this code"` |
| `codereview` | Code review | `@exai codereview --path src/` |
| `consensus` | Multi-model | `@exai consensus "Best approach?"` |
| `debug` | Debug issues | `@exai debug "Error in my code"` |
| `docgen` | Generate docs | `@exai docgen src/utils.py` |
| `listmodels` | List models | `@exai listmodels` |
| `planner` | Plan tasks | `@exai plan "Build a website"` |
| `refactor` | Refactor code | `@exai refactor --path src/` |
| `secaudit` | Security audit | `@exai secaudit --path src/` |
| `smart_file_query` | Query files | `@exai smart_file_query "Where is X?"` |
| `thinkdeep` | Deep analysis | `@exai thinkdeep "How does this work?"` |

---

## Summary

✅ **Setup:** Add `.vscode/settings.json` config
✅ **Connect:** Reload VSCode
✅ **Use:** Run `@exai <tool_name>` in Claude Code
✅ **Scale:** Open multiple VSCode windows for independent connections

**You're ready to use EXAI with Claude Code!** 🚀
