# 🔌 Fixing EX-AI MCP Server Connection in Claude Code

## The Problem

You're running EX-AI MCP Server **inside Docker**, but Claude Code can't connect to it properly. This is a **Docker networking issue**.

---

## 🎯 Quick Diagnosis

Run this in Claude Code to see current MCP servers:

```bash
claude mcp list
```

You should see:
```
exai-mcp: C:/Project/EX-AI-MCP-Server/.venv/Scripts/python.exe -u ... - ✓ Connected
```

But Claude Code can't execute commands through it. Why?

---

## 🔍 The Issue

### Docker Networking Problem

1. **EX-AI MCP Server** runs in Docker container
2. **Docker** exposes ports internally
3. **Claude Code** (running outside Docker) can't reach Docker's internal network
4. **Result:** Connection appears active but commands fail

### What You See
- ✅ MCP server shows as "Connected"
- ❌ @exai-mcp commands don't work
- ❌ "confused" behavior from Claude Code

---

## ✅ Solutions

### Solution 1: Fix Docker Port Exposure (Recommended)

**In your Docker Compose or Dockerfile:**

```yaml
services:
  exai-mcp:
    build: .
    ports:
      - "8079:8079"  # EXPOSE THE MCP PORT
    environment:
      - EXAI_WS_HOST=0.0.0.0  # LISTEN ON ALL INTERFACES
      - EXAI_WS_PORT=8079
```

**Or run Docker with port mapping:**

```bash
docker run -p 8079:8079 exai-mcp-server
```

### Solution 2: Use Host Network Mode

```bash
docker run --network host exai-mcp-server
```

This makes the container use your host's network directly.

### Solution 3: Configure EX-AI MCP Server

**In EX-AI MCP Server config:**

```python
# In your EX-AI MCP Server
if __name__ == "__main__":
    # Bind to 0.0.0.0, not localhost
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8079)
```

### Solution 4: Use Stdio Connection (Better)

**Instead of WebSocket, use stdio connection:**

```json
{
  "mcpServers": {
    "exai-mcp": {
      "command": "C:/Project/EX-AI-MCP-Server/.venv/Scripts/python.exe",
      "args": [
        "-m", "exai_mcp_server.cli"
      ],
      "env": {
        "EXAI_MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

This bypasses Docker networking issues entirely!

---

## 🧪 Testing the Fix

### Test 1: Check Port is Exposed

```bash
# On your host machine (outside Docker)
curl http://localhost:8079/health
# or
netstat -an | grep 8079
```

Should show the port is listening.

### Test 2: Test from Claude Code

```bash
@exai-mcp Please list available tools
```

Should work without errors.

### Test 3: Check Docker Logs

```bash
docker logs exai-mcp-container
```

Look for connection attempts.

---

## 🔧 Recommended Fix Steps

### Step 1: Verify Docker Configuration

**Check your docker-compose.yml:**

```yaml
version: '3.8'
services:
  exai-mcp:
    build: .
    ports:
      - "8079:8079"  # MUST BE PRESENT
    environment:
      - EXAI_WS_HOST=0.0.0.0  # NOT localhost!
      - EXAI_WS_PORT=8079
```

### Step 2: Restart Docker

```bash
docker-compose down
docker-compose up -d
```

### Step 3: Verify Connection in Claude Code

```bash
@exai-mcp ping
```

Should return: "pong" or similar.

---

## 🎯 Alternative: Convert Package to MCP Server

I can convert the `claude_enhancements` Python package into a **proper MCP server** that Claude Code can connect to!

### Benefits:
- ✅ Native MCP protocol support
- ✅ No Docker networking issues
- ✅ Direct integration with Claude Code
- ✅ @claude-enhancements commands

### Would you like me to:

1. **Fix the Docker networking** to connect to EX-AI MCP Server?
2. **Convert the Python package** into an MCP server?
3. **Both**?

---

## 📋 Current Status

### What Works ✅
- EX-AI MCP Server container is running
- Docker port 8079 is exposed (from your config)
- Claude Code shows "Connected"

### What's Broken ❌
- Commands through @exai-mcp don't execute
- Docker networking prevents communication
- Claude Code can't send/receive data properly

### Quick Test

Try this in Claude Code:

```bash
@exai-mcp test-connection
```

If it fails with a timeout or connection error, the Docker networking is the issue.

---

## 💡 Pro Tip

**For MCP servers, stdio connection is almost always better than WebSocket** because:
- No networking complexity
- Better performance
- More reliable
- Easier to debug

If EX-AI MCP Server supports stdio mode, switch to that!

---

## 🆘 Need Help?

1. Run `docker ps` to see if EX-AI MCP container is running
2. Run `docker logs <container>` to check for errors
3. Try the stdio connection option
4. Let me know what error messages you see in Claude Code

---

**TL;DR:** Your EX-AI MCP Server is running in Docker, but Docker's network isolation prevents Claude Code from communicating with it. Fix by exposing ports properly or using stdio connection mode.
