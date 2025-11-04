# 🔌 MCP Integration Guide - Claude Code + EX-AI

## The Confusion Explained

You have **TWO SEPARATE** things that both use "MCP":

### 1️⃣ EX-AI MCP Server (Your Docker Container)
- **What it is:** Real MCP (Model Context Protocol) server
- **Purpose:** Provides @exai-mcp tools to Claude Code
- **Running:** In Docker container on port 8079
- **Status:** ✅ Already connected in your MCP list

### 2️⃣ Claude Enhancements Python Package (What I Created)
- **What it is:** Python library/package
- **Purpose:** Import and use in Python scripts
- **Running:** Not a server, just a package to import
- **Status:** ❌ Not connected via MCP

---

## 🎯 The Issue

### Docker Networking Problem

When EX-AI MCP Server runs in Docker:
```
Claude Code (on host) → Docker Container Port 8079
```

Docker's network isolation prevents direct communication unless ports are properly exposed.

### Symptoms
- ✅ `claude mcp list` shows "exai-mcp: ✓ Connected"
- ❌ `@exai-mcp` commands don't work
- ❌ Claude Code is "confused"

---

## ✅ Solutions

### Option 1: Fix EX-AI Docker Port Exposure (For EX-AI MCP)

**Check your Docker configuration:**

```bash
# In docker-compose.yml, ensure ports are exposed:
services:
  exai-mcp:
    ports:
      - "8079:8079"  # REQUIRED
    environment:
      - EXAI_WS_HOST=0.0.0.0  # NOT localhost!
      - EXAI_WS_PORT=8079
```

**Test if port is accessible:**

```bash
# From outside Docker
curl http://localhost:8079/health
# or
netstat -an | grep 8079
```

### Option 2: Use Stdio Connection (Recommended)

**Much better than WebSocket - no networking issues!**

Change EX-AI MCP Server to use stdio:

```json
{
  "mcpServers": {
    "exai-mcp": {
      "command": "python",
      "args": ["-m", "exai_mcp_server.cli"],
      "env": {
        "EXAI_MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

This bypasses ALL Docker networking issues.

### Option 3: Use the MCP Server I Created

I've created an MCP server version of the enhancements package!

**Install the package:**

```bash
cd c:/Users/Jazeel-Home/.claude
pip install -e .
```

**Use it via MCP:**

```json
{
  "mcpServers": {
    "claude-enhancements": {
      "command": "python",
      "args": ["c:/Users/Jazeel-Home/.claude/claude_enhancements_mcp/server.py"]
    }
  }
}
```

**Then in Claude Code:**

```bash
@claude-enhancements cache_stats
@claude-enhancements minimax_monitor_stats
@claude-enhancements batch_add_request "analyze file.py"
```

---

## 🧪 Testing

### Test 1: Check EX-AI MCP Connection

```bash
# In Claude Code
@exai-mcp ping
```

**Expected:** Should return "pong" or similar

**If it fails:** Docker networking issue

### Test 2: Check Claude Enhancements MCP

```bash
# In Claude Code
@claude-enhancements cache_stats
```

**Expected:** Returns cache statistics

**If it fails:** MCP server not installed properly

---

## 📋 Step-by-Step Fix

### For EX-AI MCP Server:

1. **Check Docker is running:**
   ```bash
   docker ps | grep exai
   ```

2. **Check port is exposed:**
   ```bash
   docker port <exai-container>
   # Should show: 8079/tcp -> 0.0.0.0:8079
   ```

3. **Test connectivity:**
   ```bash
   curl http://localhost:8079/health
   ```

4. **If curl fails, restart Docker with port mapping:**
   ```bash
   docker run -p 8079:8079 exai-mcp-server
   ```

### For Claude Enhancements MCP:

1. **Install the package:**
   ```bash
   cd c:/Users/Jazeel-Home/.claude
   pip install -e .
   ```

2. **Test the server manually:**
   ```bash
   python c:/Users/Jazeel-Home/.claude/claude_enhancements_mcp/server.py
   ```

3. **Add to MCP config** (already done in `mcp_config_claude_enhancements.json`)

4. **Test in Claude Code:**
   ```bash
   @claude-enhancements cache_stats
   ```

---

## 🎯 Recommended Approach

### Phase 1: Fix EX-AI MCP (Quick)
```bash
# 1. Restart Docker with proper port mapping
docker run -p 8079:8079 --network host exai-mcp-server

# 2. Test in Claude Code
@exai-mcp test-connection
```

### Phase 2: Add Enhancements MCP (Optional)
```bash
# 1. Install package
pip install -e .

# 2. Use in Claude Code
@claude-enhancements minimax_monitor_stats
```

---

## 📦 Files Created

### For MCP Integration:
- `EXAI_MCP_CONNECTION_FIX.md` - Detailed fix guide
- `claude_enhancements_mcp/server.py` - MCP server implementation
- `mcp_config_claude_enhancements.json` - MCP config
- `MCP_INTEGRATION_GUIDE.md` - This file

### For Python Package:
- `claude_enhancements/` - Main package
- `pyproject.toml` - Package configuration
- `README.md` - Documentation

---

## 🔍 Debugging

### Check MCP Server Status

```bash
# List all MCP servers
claude mcp list

# Check specific server health
@exai-mcp ping
@claude-enhancements cache_stats
```

### View Logs

```bash
# EX-AI MCP Docker logs
docker logs <exai-container>

# Claude Code logs
# (Check ~/.claude/logs/)
```

### Common Errors

**"Connection refused"**
→ Docker port not exposed properly

**"Command not found"**
→ MCP server path incorrect

**"No such file or directory"**
→ Python path issue or server not installed

---

## 💡 Pro Tips

1. **Always prefer stdio over WebSocket** for MCP servers (fewer networking issues)

2. **Test MCP servers outside Claude Code first**:
   ```bash
   python server.py
   # Should start without errors
   ```

3. **Check port accessibility**:
   ```bash
   netstat -an | grep 8079
   ```

4. **Use @mentions in Claude Code**:
   ```bash
   @exai-mcp list-tools
   @claude-enhancements batch_stats
   ```

---

## 🎊 Summary

**You have TWO separate MCP setups:**

1. **EX-AI MCP Server** (in Docker) - For EX-AI tools
   - Fix: Expose ports properly or use stdio mode

2. **Claude Enhancements MCP** (Python server) - For monitoring, caching, etc.
   - Install: `pip install -e .`
   - Use: `@claude-enhancements <command>`

Both can run simultaneously in Claude Code!

---

## 🆘 Need Help?

1. Run `claude mcp list` - What do you see?
2. Try `@exai-mcp ping` - What error?
3. Check `docker ps` - Is EX-AI running?
4. Let me know what happens!

---

**TL;DR:** EX-AI MCP Server has Docker networking issues. Fix with port exposure or stdio mode. I've also created an MCP server version of the enhancements package you can use directly!
