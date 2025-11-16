# EXAI MCP Integration Guide - Current Implementation

> **Version:** 3.0 (Container-based stdio MCP)
> **Date:** 2025-11-16
> **Status:** ✅ **Current - Container Architecture**

---

## 🎯 Current Status

### ✅ **Live System (Verified 2025-11-16)**
- **MCP Protocol**: stdio-based (not WebSocket)
- **Architecture**: Container deployment (4 containers)
- **Status**: All containers running and healthy
- **Connection**: Direct stdio MCP server in container

### Container Status
```bash
NAME                   STATUS       HEALTH
exai-mcp-server        Up 4min      healthy
exai-mcp-stdio         Up 4min      healthy  
exai-redis             Up 5min      healthy
exai-redis-commander   Up 4min      healthy
```

---

## 🏗️ Current Architecture

```
┌─────────────────────┐
│   Client Application   │
│   (Claude Code,     │
│   VSCode, Custom)   │
└──────────┬──────────┘
           │ stdio MCP Protocol
           ▼
┌─────────────────────────────────────────────────┐
│  Docker Container: exai-mcp-stdio (Port 8079)  │
│                                                 │
│  ┌──────────────────────────────────────────┐   │
│  │           STDIO MCP SERVER                │   │
│  │                                          │   │
│  │  • Direct stdio communication             │   │
│  │  • Tool execution                    │   │
│  │  • Request/response handling           │   │
│  │  • Provider routing                 │   │
│  └──────────────┬───────────────────────┘   │
│                 │                                │
│  ┌─────────────▼───────────────────────┐   │
│  │        REDIS (Port 6379)        │   │
│  │                                     │   │
│  │  • Session management             │   │
│  │  • Cache storage              │   │
│  │  • Queue processing          │   │
│  └─────────────────┬───────────────┘   │
└────────────────────┼─────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────┐
│           EXTERNAL AI PROVIDERS                │
│                                               │
│  ┌─────────┐  ┌─────────┐  ┌───────┐  │
│  │  Z.ai   │  │ Moonshot│  │ Mini  │  │
│  │  (GLM)  │  │ (Kimi) │  │  Max  │  │
│  │          │  │          │  │       │  │
│  │ zai-sdk  │  │ OpenAI  │  │ Ant   │  │
│  │  200K    │  │  256K   │  │ Claude │  │
│  │ Context  │  │ Context │  │ API   │  │
│  └─────┬────┘  └────┬────┘  └───┬───┘  │
└─────────┼──────────────┼────────┼──────┘  │
          │              │        │         │
          └──────────────┴────────┘         │
```

---

## 🔧 Configuration

### .mcp.json Configuration
```json
{
  "mcpServers": {
    "exai-mcp-server": {
      "command": "python",
      "args": ["-m", "src.daemon.stdio_server"],
      "cwd": "/app",
      "env": {
        "PYTHONPATH": "/app/src",
        "EXAI_CONFIG": "/app/.env.docker"
      }
    }
  }
}
```

### Environment Variables
```bash
# Primary configuration
EXAI_CONFIG=/app/.env.docker
PYTHONPATH=/app/src

# Provider API Keys (if needed)
ZAI_API_KEY=your-zai-key
KIMI_API_KEY=your-kimi-key
MINIMAX_API_KEY=your-minimax-key

# Container settings
REDIS_URL=redis://localhost:6379
```

---

## 🚀 Running the System

### Start Containers
```bash
# Navigate to project directory
cd /path/to/EX-AI-MCP-Server

# Start all containers
docker-compose up -d

# Verify containers are running
docker-compose ps

# Check logs
docker-compose logs exai-mcp-stdio
```

### Stop Containers
```bash
# Stop all containers
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

---

## 🔌 Integration Methods

### Method 1: Direct stdio Connection
```python
import asyncio
import subprocess
import json

async def connect_to_exai_mcp():
    """Connect directly to EXAI MCP stdio server"""
    
    # Start MCP server process
    process = await asyncio.create_subprocess_exec(
        'python', '-m', 'src.daemon.stdio_server',
        cwd='/app',
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    # Send MCP initialize request
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
    }
    
    # Send request and get response
    await process.stdin.send(json.dumps(init_request).encode() + b'\n')
    response_line = await process.stdout.readline()
    response = json.loads(response_line.decode())
    
    print("Initialized:", response)
    
    # Send tools/list request
    tools_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    
    await process.stdin.send(json.dumps(tools_request).encode() + b'\n')
    tools_line = await process.stdout.readline()
    tools_response = json.loads(tools_line.decode())
    
    print("Available tools:", tools_response)
    
    return process
```

### Method 2: Claude Code Integration
```json
{
  "mcpServers": {
    "exai-mcp": {
      "command": "python",
      "args": ["-m", "src.daemon.stdio_server"],
      "cwd": "/path/to/EX-AI-MCP-Server",
      "env": {
        "EXAI_CONFIG": "/path/to/EX-AI-MCP-Server/.env.docker"
      }
    }
  }
}
```

---

## 🛠️ Available Tools

### Core Tools (Always Available)
```json
{
  "tools": [
    {
      "name": "chat",
      "description": "General development chat and collaborative thinking"
    },
    {
      "name": "listmodels", 
      "description": "List available AI models from all providers"
    },
    {
      "name": "status",
      "description": "Get EXAI MCP server status and health"
    }
  ]
}
```

### Provider-Specific Tools
```json
{
  "tools": [
    {
      "name": "glm_payload_preview",
      "description": "Preview GLM chat payload before sending"
    },
    {
      "name": "kimi_chat_with_files", 
      "description": "Chat with Kimi using file context"
    }
  ]
}
```

### Workflow Tools
```json
{
  "tools": [
    {
      "name": "analyze",
      "description": "Code analysis and review"
    },
    {
      "name": "debug",
      "description": "Debug and troubleshooting assistance"
    },
    {
      "name": "codereview", 
      "description": "Comprehensive code review"
    }
  ]
}
```

---

## 📡 API Reference

### Initialize Request
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize", 
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {
      "name": "client-name",
      "version": "1.0.0"
    }
  }
}
```

### Tools List Request
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/list",
  "params": {}
}
```

### Tool Call Request
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "chat",
    "arguments": {
      "prompt": "Hello, how can you help me?",
      "model": "glm-4.6",
      "temperature": 0.3
    }
  }
}
```

---

## 🔍 Monitoring

### Health Check Endpoint
```bash
# Check container health
docker-compose ps

# Check specific service health
docker-compose logs exai-mcp-stdio | grep "healthy"

# Manual health check
curl http://localhost:3002/health
```

### Monitoring Dashboard
```bash
# Access monitoring dashboard
open http://localhost:3001

# View metrics
open http://localhost:3003/metrics
```

### Redis Commander
```bash
# Access Redis web interface
open http://localhost:8081
```

---

## 🐛 Troubleshooting

### Common Issues

#### Container Not Running
```bash
# Check container status
docker-compose ps

# Restart containers
docker-compose restart

# Check logs for errors
docker-compose logs exai-mcp-stdio
```

#### Connection Failed
```bash
# Verify stdio server is running
docker-compose exec exai-mcp-stdio ps aux | grep stdio_server

# Check environment
docker-compose exec exai-mcp-stdio env | grep EXAI

# Test direct connection
docker-compose exec exai-mcp-stdio python -m src.daemon.stdio_server --test
```

#### Tools Not Available
```bash
# List available tools
curl -X POST http://localhost:3002/tools

# Check provider health
curl http://localhost:3002/providers/health

# Verify provider API keys
docker-compose exec exai-mcp-stdio env | grep API_KEY
```

### Debug Mode
```bash
# Run with debug logging
docker-compose exec exai-mcp-stdio LOG_LEVEL=DEBUG python -m src.daemon.stdio_server

# Enable verbose MCP logging
docker-compose exec exai-mcp-stdio MCP_DEBUG=1 python -m src.daemon.stdio_server
```

---

## 🔄 Updates & Changes

### Recent Changes (2025-11-16)
- ✅ **Container Architecture**: Migrated to 4-container Docker Compose setup
- ✅ **Port Strategy**: Updated to 3010, 3001-3003 (avoid Orchestrator conflicts)  
- ✅ **Protocol**: Changed from WebSocket to stdio MCP
- ✅ **Provider SDKs**: Migrated GLM from zhipuai to zai-sdk
- ✅ **Non-China Compliance**: All endpoints verified non-China based

### Breaking Changes
- ❌ **WebSocket Shim**: No longer used (removed from architecture)
- ❌ **Port 3005**: No longer relevant (stdio MCP in container)
- ❌ **Legacy SDKs**: zhipuai replaced with zai-sdk

---

## 📚 References

- **Current Architecture**: `docs/architecture/CURRENT_SYSTEM_ARCHITECTURE.md`
- **SDK Integration**: `docs/architecture/SDK_ARCHITECTURE_FINAL.md`
- **Provider APIs**: `docs/api/provider-apis/`
- **Container Config**: `docker-compose.yml`

**Status**: Current as of 2025-11-16 - Container-based stdio MCP system operational
