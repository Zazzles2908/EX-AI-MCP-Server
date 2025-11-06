# EXAI MCP Connection Guide - 2025-11-05

## 🎯 OVERVIEW

This guide explains how to connect Claude Desktop and Claude Code to the EXAI MCP Server.

## 📋 PREREQUISITES

### 1. Docker Containers Running
```bash
docker ps | grep exai
```

**Expected Output:**
```
exai-mcp-daemon        ... Up (healthy)   0.0.0.0:8000->8000/tcp
exai-redis             ... Up (healthy)   0.0.0.0:6379->6379/tcp
redis-commander        ... Up (healthy)   0.0.0.0:8081->8081/tcp
```

**If containers are not running:**
```bash
cd C:/Project/EX-AI-MCP-Server
docker-compose up -d
```

### 2. Environment Variables Set
```bash
# Check .env file exists
ls -la C:/Project/EX-AI-MCP-Server/.env

# Verify key variables
grep EXAI_JWT_TOKEN C:/Project/EX-AI-MCP-Server/.env
```

## 🔌 CONNECTING CLAUDE DESKTOP

### Step 1: Locate Config File
```
%APPDATA%\Claude\claude_desktop_config.json
```

Full path:
```
C:\Users\Jazeel-Home\AppData\Roaming\Claude\claude_desktop_config.json
```

### Step 2: Apply Corrected Configuration

**Reference**: `docs/05_CURRENT_WORK/CORRECTED_CLAUDE_DESKTOP_CONFIG__2025-11-05.json`

Copy this configuration to your desktop config file.

### Step 3: Restart Claude Desktop
1. Close Claude Desktop completely
2. Wait 5 seconds
3. Reopen Claude Desktop

### Step 4: Verify Connection

1. Open a new chat in Claude Desktop
2. Look for these log messages:
   ```
   [info] Loading MCP server: gh-mcp
   [info] Loading MCP server: excalidraw-mermaid
   [info] Loading MCP server: exai-mcp
   [info] Loading MCP server: filesystem
   ```

3. Test the connection:
   ```
   @exai-mcp exai_status
   ```

**Expected Response:**
```json
{
  "status": "connected",
  "version": "1.0.0",
  "tools": 21,
  "models": ["glm-4.5-flash", "kimi"]
}
```

## 🔌 CONNECTING CLAUDE CODE (AUGMENT CODE)

### Method 1: Project-Level Config (.mcp.json)

**Create in your project root:**
```bash
cd C:/Project/EX-AI-MCP-Server
cat > .mcp.json << 'EOF'
{
  "mcpServers": {
    "exai-mcp": {
      "command": "C:/Project/EX-AI-MCP-Server/.venv/Scripts/python.exe",
      "args": ["-u", "C:/Project/EX-AI-MCP-Server/scripts/runtime/run_ws_shim.py"],
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
EOF
```

### Method 2: VS Code MCP Extension

1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X)
3. Search for "MCP"
4. Install "Model Context Protocol" extension
5. Configure with same settings as above

### Step 3: Reload VS Code Window
```
Ctrl+Shift+P → "Developer: Reload Window"
```

### Step 4: Verify Connection
```
EXAI tools should appear in Command Palette (Ctrl+Shift+P)
Or test with: @exai-mcp exai_status
```

## 🔍 CONNECTION STATUS CHECKS

### Check 1: WebSocket Service
```bash
# Test WebSocket connection
python -c "
import websockets
import asyncio
async def test():
    async with websockets.connect('ws://127.0.0.1:8079/ws') as ws:
        await ws.send(json.dumps({'action': 'status'}))
        response = await ws.recv()
        print(response)
asyncio.run(test())
"
```

### Check 2: API Endpoint
```bash
# Test REST API
curl -H "Authorization: Bearer <JWT_TOKEN>" http://127.0.0.1:8000/api/status
```

### Check 3: MCP Tools List
```bash
# Test MCP protocol directly
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | \
  python C:/Project/EX-AI-MCP-Server/scripts/runtime/run_ws_shim.py
```

Expected output:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "tools": [
      {"name": "exai_chat", "description": "..."},
      {"name": "exai_search", "description": "..."},
      ...
      // 21 tools total
    ]
  }
}
```

## 🚨 TROUBLESHOOTING

### Problem: "Failed to connect to MCP server"

**Solution:**
1. Check Docker containers are running
2. Verify .env file has EXAI_JWT_TOKEN
3. Restart Docker containers:
   ```bash
   docker-compose restart
   ```

### Problem: "WebSocket connection refused"

**Solution:**
1. Check port 8079 is accessible:
   ```bash
   netstat -an | grep 8079
   ```
2. Check container logs:
   ```bash
   docker logs exai-mcp-daemon
   ```
3. Verify firewall allows connections on port 8079

### Problem: "Invalid JWT token"

**Solution:**
1. Generate new JWT token:
   ```bash
   cd C:/Project/EX-AI-MCP-Server
   python scripts/auth/generate_jwt.py
   ```
2. Update .env file with new token
3. Restart containers:
   ```bash
   docker-compose restart
   ```

### Problem: "Tools not appearing in Claude Code"

**Solution:**
1. Check .mcp.json is in project root
2. Restart VS Code window
3. Check MCP logs in VS Code:
   - View → Output → Extensions → MCP

### Problem: "Connection timeout"

**Solution:**
1. Check Docker container health:
   ```bash
   docker ps -a
   ```
2. Check system resources:
   ```bash
   docker stats
   ```
3. Restart containers with fresh logs:
   ```bash
   docker-compose down
   docker-compose up -d --force-recreate
   ```

## 📊 LOG FILES

### View EXAI MCP Logs
```bash
# Tail live logs
tail -f C:/Project/EX-AI-MCP-Server/logs/exai-mcp.log

# Last 100 lines
tail -100 C:/Project/EX-AI-MCP-Server/logs/exai-mcp.log

# Search for errors
grep -i error C:/Project/EX-AI-MCP-Server/logs/exai-mcp.log
```

### View Docker Logs
```bash
# All EXAI containers
docker logs exai-mcp-daemon
docker logs exai-redis
docker logs exai-redis-commander

# Follow logs (Ctrl+C to stop)
docker logs -f exai-mcp-daemon
```

## 🔐 AUTHENTICATION

### JWT Token Format
```
<base64_header>.<base64_payload>.<base64_signature>
```

### Token Payload Fields
```json
{
  "sub": "claude@exai-mcp.local",
  "iss": "exai-mcp-server",
  "aud": "exai-mcp-client",
  "iat": 1762125073,
  "exp": 1793661073
}
```

**Note**: Token expires on 2035-12-31 (far future)

### Regenerate Token (if needed)
```bash
cd C:/Project/EX-AI-MCP-Server
python -c "
from scripts.auth.generate_jwt import generate_jwt
token = generate_jwt()
print(token)
"
```

## 🎯 VERIFICATION CHECKLIST

- [ ] Docker containers running (exai-mcp-daemon, exai-redis, redis-commander)
- [ ] .env file exists with valid EXAI_JWT_TOKEN
- [ ] claude_desktop_config.json uses corrected format (no id/name/description fields)
- [ ] WebSocket port 8079 is accessible
- [ ] REST API port 8000 is responding
- [ ] Claude Desktop restarted and loaded MCP servers
- [ ] EXAI tools visible in Claude Desktop (@exai-mcp exai_status works)
- [ ] Claude Code connected (if using .mcp.json)
- [ ] Tools list returns 21 EXAI tools

## 📚 RELATED DOCUMENTATION

- **Config Fix Guide**: `docs/05_CURRENT_WORK/FIX_CLAUDE_DESKTOP_CONFIG__2025-11-05.md`
- **Corrected Config**: `docs/05_CURRENT_WORK/CORRECTED_CLAUDE_DESKTOP_CONFIG__2025-11-05.json`
- **Quick Start**: `docs/05_CURRENT_WORK/EXAI_QUICK_START__2025-11-05.md`
- **Architecture**: `docs/02_Architecture/MCP_ARCHITECTURE.md`

## ✅ SUCCESS CRITERIA

When connection is successful, you should be able to:
1. Run `@exai-mcp exai_status` and get a valid response
2. Run `@exai-mcp exai_chat` and receive responses from GLM-4.5-Flash or Kimi
3. Access all 21 EXAI tools from Claude interface
4. Switch between Claude Desktop and Claude Code seamlessly

---

**Status**: ✅ Connection Guide Complete
**Applied**: 2025-11-05 09:50 UTC
**Next Step**: Apply corrected config and restart Claude Desktop
