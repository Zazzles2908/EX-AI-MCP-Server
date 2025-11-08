# Port Strategy & MCP Connection Guide
*Updated: 2025-11-08*

## 🎯 Current Port Allocation

### EXAI Services (3000-3999)
| Port | Service | Description | Status |
|------|---------|-------------|--------|
| **3000** | WebSocket Daemon | MCP Protocol - Main EXAI service | ✅ UP & HEALTHY |
| 3001 | Monitoring Dashboard | Real-time metrics & health | ✅ OPERATIONAL |
| 3002 | Health Check | HTTP health endpoint | ✅ RESPONDING |
| 3003 | Prometheus Metrics | Metrics collection | ✅ RESPONDING |

### Orchestrator APIs (8000-8999)
| Port | Service | Description | Status |
|------|---------|-------------|--------|
| 8001 | Cognee | Knowledge Graph | ✅ UP & HEALTHY |
| 8002 | Local LLM | Qwen2.5 7B | ✅ UP & HEALTHY |
| 8091 | Auth Proxy | MiniMax API Gateway | ✅ UP |

### Supporting Services
| Port | Service | Description | Status |
|------|---------|-------------|--------|
| 6379 | Redis | Conversation storage | ✅ HEALTHY |
| 8081 | Redis Commander | Redis monitoring UI | ✅ HEALTHY |

## 🔌 How to Connect to EXAI MCP Server

### 1. VSCode with Claude Code
**MCP Config File:** `C:\Project\EX-AI-MCP-Server\.mcp.json`

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
        "ENV_FILE": "C:/Project/EX-AI-MCP-Server/.env.docker",
        "EXAI_WS_HOST": "127.0.0.1",
        "EXAI_WS_PORT": "3000",
        ...
      }
    }
  }
}
```

**Action Required:** 
- VSCode should auto-reload the MCP config
- If not, press `Ctrl+Shift+P` → "Developer: Reload Window"
- Or restart VSCode

### 2. Claude Desktop (via .mcp.json)
**Location:** Usually `C:\Users\[Username]\AppData\Local\Claude\claude_desktop_config.json`

Add this to your Claude Desktop config:

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
        "ENV_FILE": "C:/Project/EX-AI-MCP-Server/.env.docker",
        "EXAI_WS_HOST": "127.0.0.1",
        "EXAI_WS_PORT": "3000",
        "PYTHONUNBUFFERED": "1",
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

**Action Required:** Restart Claude Desktop

### 3. Augment Code / VSCode Extensions
**Config File:** `C:\Project\EX-AI-MCP-Server\config\daemon\mcp-config.augmentcode.json`

This file is already updated with the new port. To activate:
1. In VSCode, open Settings
2. Search for "MCP" or "Augment"
3. Point the MCP configuration to: `C:\Project\EX-AI-MCP-Server\config\daemon\mcp-config.augmentcode.json`
4. Reload VSCode

### 4. Custom MCP Clients
If you're building a custom MCP client, connect to:

```python
import asyncio
import websockets
import json

async def connect_to_exai():
    uri = "ws://127.0.0.1:3000"
    
    async with websockets.connect(uri) as websocket:
        # Send hello
        await websocket.send(json.dumps({
            "op": "hello",
            "session_id": "your-session-id",
            "token": "your-token-if-required"
        }))
        
        # Receive ack
        ack = await websocket.recv()
        print(f"Connected: {ack}")
        
        # List tools
        await websocket.send(json.dumps({
            "op": "list_tools",
            "request_id": "req-1"
        }))
        
        tools = await websocket.recv()
        print(f"Tools: {tools}")

# Run
asyncio.run(connect_to_exai())
```

## 🔍 Verify Connection

### Check WebSocket is Listening
```bash
netstat -an | findstr :3000
```

Expected output:
```
TCP    127.0.0.1:3000         0.0.0.0:0              LISTENING
```

### Test Health Endpoint
```bash
curl http://localhost:3002/health
```

### Check Docker Container
```bash
docker ps | findstr exai
```

Expected:
```
exai-mcp-daemon            Up 22 seconds (healthy)     0.0.0.0:3003->8000/tcp, 0.0.0.0:3000->8079/tcp
```

## 📋 Troubleshooting

### Issue: Still connecting to port 8079
**Solution:** Clear MCP server cache
1. Kill all Python processes running the shim
2. Restart your MCP client (VSCode/Claude)
3. The config files are already updated - no manual changes needed

### Issue: Connection refused
**Solution:** Verify Docker is running
```bash
docker-compose ps
```
Should show `exai-mcp-daemon` as "Up"

### Issue: "No module named 'resilience'"
**Solution:** Already fixed in the latest build. If still happening:
```bash
docker-compose build --no-cache exai-daemon
docker-compose restart exai-daemon
```

## 📝 Configuration Files Updated

All these files now use port **3000** and `.env.docker`:

1. ✅ `C:\Project\EX-AI-MCP-Server\.mcp.json` - Main MCP config
2. ✅ `C:\Project\EX-AI-MCP-Server\.claude\.mcp.json` - Claude-specific config
3. ✅ `C:\Project\EX-AI-MCP-Server\config\daemon\mcp-config.augmentcode.json` - Augment Code
4. ✅ `C:\Project\EX-AI-MCP-Server\config\daemon\mcp-config.claude.json` - Claude Desktop
5. ✅ `C:\Project\EX-AI-MCP-Server\config\daemon\mcp-config.auggie.json` - Auggie
6. ✅ `C:\Project\EX-AI-MCP-Server\config\daemon\mcp-config.template.json` - Template
7. ✅ `C:\Project\EX-AI-MCP-Server\config\daemon\mcp-config.augmentcode.vscode1.json` - VSCode 1
8. ✅ `C:\Project\EX-AI-MCP-Server\config\daemon\mcp-config.augmentcode.vscode2.json` - VSCode 2

## 🚀 Next Steps

1. **For VSCode users:** Just reload VSCode window (`Ctrl+Shift+P` → "Developer: Reload Window")
2. **For Claude Desktop:** Restart the application
3. **For Augment Code:** Reload the extension or restart VSCode
4. **For custom clients:** Use port 3000 in your WebSocket connection

The system is fully operational and ready to accept connections! 🎉
