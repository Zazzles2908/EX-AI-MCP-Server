# 🔌 Connect Claude Code to EXAI MCP Server - Complete Guide

## 🎯 Overview

This guide shows how to connect Claude Code to the EXAI MCP Server using EXAI tools and configurations that have been pre-built for you.

---

## ✅ Prerequisites Checklist

### 1. EXAI MCP Server Status
```bash
cd /c/Project/EX-AI-MCP-Server
python check_port.py
```
**Expected Output:** `SUCCESS: Port 8079 is LISTENING!` ✅

### 2. Environment Configuration
The following are already configured in `/c/Project/EX-AI-MCP-Server/.env`:

```bash
# WebSocket Connection
EXAI_WS_HOST=127.0.0.1
EXAI_WS_PORT=8079

# Authentication Token (JWT)
EXAI_JWT_TOKEN_CLAUDE=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjbGF1ZGVAZXhhaS1tY3AubG9jYWwiLCJpc3MiOiJleGFpLW1jcC1zZXJ2ZXIiLCJhdWQiOiJleGFpLW1jcC1jbGllbnQiLCJpYXQiOjE3NjIxMjUwNzMsImV4cCI6MTc5MzY2MTA3M30.hVzyioI0JRDgGnbVIq7NYZOsPiiOYjjuRXwAPBVtFn0
```

---

## 🚀 Method 1: Per-Project Connection (Recommended)

### For Each Project, Create `.mcp.json`

**Example for a new project:**

```json
{
  "mcpServers": {
    "claude-enhancements": {
      "command": "python",
      "args": ["c:/Users/Jazeel-Home/.claude/claude_enhancements_mcp/server.py"],
      "env": {
        "PYTHONPATH": "c:/Users/Jazeel-Home/.claude"
      }
    },
    "exai-mcp": {
      "command": "C:/Project/EX-AI-MCP-Server/.venv/Scripts/python.exe",
      "args": [
        "-u",
        "C:/Project/EX-AI-MCP-Server/scripts/runtime/run_ws_shim.py"
      ],
      "env": {
        "ENV_FILE": "C:/Project/EX-AI-MCP-Server/.env",
        "PYTHONUNBUFFERED": "1",
        "PYTHONIOENCODING": "utf-8",
        "LOG_LEVEL": "INFO",
        "EXAI_WS_HOST": "127.0.0.1",
        "EXAI_WS_PORT": "8079",
        "EXAI_JWT_TOKEN": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjbGF1ZGVAZXhhaS1tY3AubG9jYWwiLCJpc3MiOiJleGFpLW1jcC1zZXJ2ZXIiLCJhdWQiOiJleGFpLW1jcC1jbGllbnQiLCJpYXQiOjE3NjIxMjUwNzMsImV4cCI6MTc5MzY2MTA3M30.hVzyioI0JRDgGnbVIq7NYZOsPiiOYjjuRXwAPBVtFn0"
      }
    }
  }
}
```

### Usage in Claude Code

Once connected, you can use EXAI tools directly:

```bash
@exai-mcp status
@exai-mcp chat "Help me with this code"
@exai-mcp analyze "analyze this file"
@exai-mcp planner "create a plan for this project"
```

---

## 🚀 Method 2: Global Connection (All Projects)

### 1. Add to Claude Code Global Settings

Edit: `c:/Users/Jazeel-Home/.claude/settings.json`

```json
{
  "alwaysThinkingEnabled": true,
  "model": "minimax-m2",
  "claudeCode.environmentVariables": [
    {
      "name": "ANTHROPIC_BASE_URL",
      "value": "https://api.minimax.io/anthropic"
    },
    {
      "name": "ANTHROPIC_MODEL",
      "value": "MiniMax-M2"
    }
  ],
  "enableAllProjectMcpServers": true
}
```

### 2. Add EXAI to MCP Servers

Create: `c:/Users/Jazeel-Home/.claude/mcp_config_exai.json`

```json
{
  "mcpServers": {
    "exai-mcp": {
      "command": "C:/Project/EX-AI-MCP-Server/.venv/Scripts/python.exe",
      "args": [
        "-u",
        "C:/Project/EX-AI-MCP-Server/scripts/runtime/run_ws_shim.py"
      ],
      "env": {
        "ENV_FILE": "C:/Project/EX-AI-MCP-Server/.env",
        "PYTHONUNBUFFERED": "1",
        "LOG_LEVEL": "INFO",
        "EXAI_WS_HOST": "127.0.0.1",
        "EXAI_WS_PORT": "8079",
        "EXAI_JWT_TOKEN": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjbGF1ZGVAZXhhaS1tY3AubG9jYWwiLCJpc3MiOiJleGFpLW1jcC1zZXJ2ZXIiLCJhdWQiOiJleGFpLW1jcC1jbGllbnQiLCJpYXQiOjE3NjIxMjUwNzMsImV4cCI6MTc5MzY2MTA3M30.hVzyioI0JRDgGnbVIq7NYZOsPiiOYjjuRXwAPBVtFn0"
      }
    }
  }
}
```

---

## 🧪 Testing the Connection

### 1. Verify MCP Server List

```bash
# In Claude Code terminal or VS Code
claude mcp list
```

**Expected Output:**
```
✅ exai-mcp: Connected
✅ claude-enhancements: Connected
```

### 2. Test EXAI Connection

```bash
# In Claude Code
@exai-mcp status
```

**Expected Output:**
```
EXAI MCP Server Status: ONLINE
Available Tools: 33
Connected Sessions: 1
Uptime: XXX seconds
```

### 3. Test a Simple Tool

```bash
# In Claude Code
@exai-mcp chat "Hello, can you help me?"
```

**Expected Response:**
```
EXAI AI: Hello! I'm here to help you with your project...
```

---

## 🔧 Troubleshooting

### Issue: "Connection refused" on port 8079

**Solution:**
```bash
cd /c/Project/EX-AI-MCP-Server
docker-compose up -d
python check_port.py
```

### Issue: "Command not found" for python.exe

**Solution:**
Update the path to your Python executable in `.mcp.json`:

```json
"command": "C:/Path/To/Your/python.exe"
```

### Issue: "JWT Token invalid"

**Solution:**
Generate a new JWT token:

```bash
cd /c/Project/EX-AI-MCP-Server
python scripts/generate_all_jwt_tokens.py
```

Then update the token in your `.mcp.json` file.

### Issue: "Tools not loading"

**Solution:**
Check the shim logs:

```bash
cd /c/Project/EX-AI-MCP-Server
tail -f logs/ws_shim.log
```

---

## 📊 Available EXAI Tools

Once connected, you have access to **33 EXAI tools**:

### Essential Tools (Always Visible)
- ✅ `status` - Check server status
- ✅ `chat` - General AI chat
- ✅ `planner` - Create project plans

### Core Tools (10 Total)
- ✅ `analyze` - Code analysis
- ✅ `codereview` - Code review
- ✅ `debug` - Debugging assistance
- ✅ `refactor` - Code refactoring
- ✅ `testgen` - Generate tests
- ✅ `thinkdeep` - Deep analysis
- ✅ `smart_file_query` - File search

### Advanced Tools (7 Total)
- ✅ `consensus` - Multi-model consensus
- ✅ `docgen` - Documentation generation
- ✅ `secaudit` - Security audit
- ✅ `tracer` - Execution tracing
- ✅ `precommit` - Pre-commit checks

---

## 🎯 Quick Start Commands

Once connected, try these commands in Claude Code:

```bash
# 1. Check status
@exai-mcp status

# 2. Chat with EXAI
@exai-mcp chat "What can you help me with?"

# 3. Analyze your code
@exai-mcp analyze "analyze the main.py file"

# 4. Create a plan
@exai-mcp planner "plan a Python web API project"

# 5. Code review
@exai-mcp codereview "review my code for security issues"
```

---

## 📝 Summary

**What You Have:**
✅ EXAI MCP Server running on port 8079
✅ Pre-configured JWT tokens for Claude
✅ WebSocket-to-stdio bridge (shim) ready
✅ 33 EXAI tools available

**What You Need to Do:**
1. ✅ Ensure server is running: `python check_port.py`
2. ✅ Create `.mcp.json` in your project (or use global config)
3. ✅ Test connection: `@exai-mcp status`
4. ✅ Start using EXAI tools!

**Result:**
- 🎉 Claude Code can now use ALL 33 EXAI tools
- 🎉 Access to MiniMax models via global configuration
- 🎉 Seamless integration with your development workflow

---

**Last Updated:** 2025-11-05
**Status:** ✅ READY TO CONNECT
