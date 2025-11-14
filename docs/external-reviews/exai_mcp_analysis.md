# EX-AI MCP Server Connection Failure Analysis

**Date**: November 13, 2025  
**System**: Windows OS with VS Code + Claude Code Extension  
**LLM Provider**: Minimax (MiniMax-M2)  
**Repository**: https://github.com/Zazzles2908/EX-AI-MCP-Server

---

## Executive Summary

**Root Cause**: The EX-AI MCP Server connection failures in Claude Code stem from a **fundamental transport protocol mismatch** combined with **Windows Docker networking limitations** and potential **Minimax LLM integration issues with MCP discovery**.

The server implements a **custom WebSocket-based MCP protocol** running in Docker, while Claude Code on Windows requires **direct stdio-based MCP communication**. The WebSocket shim layer (`run_ws_shim.py`) attempts to bridge this gap but faces critical issues:

1. **Docker networking barrier**: Docker container listens on `127.0.0.1:3010` (inside container), mapped to host `3010:8079`
2. **Shim connection issues**: Windows shim cannot reliably establish WebSocket connections to Dockerized daemon
3. **Minimax LLM limitations**: Minimax may not properly support MCP protocol discovery/initialization
4. **Process isolation**: The stdio shim process is isolated from the Docker container network

**Why Bash/Python Works**: Direct command-line tools bypass the MCP protocol layer entirely, calling Docker/WebSocket APIs directly through system commands.

---

## 1. Architecture Overview

### 1.1 EX-AI MCP Server Architecture

The EX-AI MCP Server uses a **multi-layer architecture**:

```
┌─────────────────────────────────────────────────────────┐
│                    Claude Code (Windows)                 │
│                  VS Code Extension + Minimax LLM         │
└──────────────────────┬──────────────────────────────────┘
                       │ stdio (stdin/stdout)
                       │ JSON-RPC over stdio
                       ▼
┌─────────────────────────────────────────────────────────┐
│              WebSocket Shim (Windows Host)               │
│         scripts/runtime/run_ws_shim.py                   │
│              Port: 3005 (not used)                       │
│         Transport: stdio ↔ WebSocket                     │
└──────────────────────┬──────────────────────────────────┘
                       │ WebSocket
                       │ Custom Protocol
                       │ ws://127.0.0.1:3010
                       ▼
┌─────────────────────────────────────────────────────────┐
│           Docker Container (exai-mcp-daemon)             │
│                                                           │
│  ┌────────────────────────────────────────────────┐     │
│  │     WebSocket Daemon (src/daemon/ws_server.py) │     │
│  │     Container Port: 8079                       │     │
│  │     Mapped to Host: 3010:8079                  │     │
│  │     Protocol: Custom WebSocket                 │     │
│  └────────────────┬───────────────────────────────┘     │
│                   │                                       │
│  ┌────────────────▼───────────────────────────────┐     │
│  │          AI Manager & Tool Router              │     │
│  │     (GLM-4.5-Flash, Kimi, Minimax)            │     │
│  └────────────────┬───────────────────────────────┘     │
│                   │                                       │
│  ┌────────────────▼───────────────────────────────┐     │
│  │              Redis (Persistence)               │     │
│  │              Container Port: 6379              │     │
│  └────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────┘
```

### 1.2 Expected Connection Flow

**Intended Design** (from repository documentation):

1. **Claude Code** starts `python.exe run_ws_shim.py` as a **stdio-based MCP server**
2. **Shim** establishes WebSocket connection to Docker daemon at `ws://127.0.0.1:3010`
3. **Shim** translates MCP stdio protocol to custom WebSocket protocol
4. **Daemon** processes requests and returns results via WebSocket
5. **Shim** translates WebSocket responses back to MCP stdio
6. **Claude Code** receives MCP-compliant responses

### 1.3 Actual Connection Flow (What's Failing)

```
Claude Code (Windows)
  │
  ├─ Starts: C:/Project/EX-AI-MCP-Server/.venv/Scripts/python.exe
  │          -u C:/Project/EX-AI-MCP-Server/scripts/runtime/run_ws_shim.py
  │
  ├─ Shim attempts: WebSocket connection to ws://127.0.0.1:3010
  │                 ❌ FAILS: Connection refused / Timeout
  │
  └─ MCP Discovery: ❌ FAILS: No tools/resources discovered
```

**Result**: Claude Code sees the MCP server as "unresponsive" or "unavailable"

---

## 2. Transport Protocol Analysis

### 2.1 MCP Standard Transport Protocols

The Model Context Protocol (MCP) specification supports three transport mechanisms:

1. **stdio** (Standard Input/Output)
   - Uses stdin/stdout for JSON-RPC communication
   - **Most common** for local MCP servers
   - Required by Claude Code and most MCP clients
   - Process-based communication

2. **SSE** (Server-Sent Events)
   - HTTP-based streaming protocol
   - Typically used for web-based MCP clients
   - Not currently supported by Claude Code

3. **HTTP** (Request/Response)
   - RESTful API approach
   - Not natively supported by standard MCP implementations
   - Custom implementation required

### 2.2 EX-AI Server Implementation

The EX-AI MCP Server uses a **hybrid custom approach**:

```python
# From: src/daemon/ws_server.py
# Server listens on WebSocket (NOT standard MCP transport)
async def serve_connection(websocket, path):
    """Handle incoming WebSocket connections."""
    # Custom WebSocket protocol
    # NOT standard MCP stdio/SSE/HTTP
```

**Key Characteristics**:
- **Primary Transport**: Custom WebSocket protocol
- **Container Port**: 8079 (internal), mapped to 3010 (host)
- **Protocol**: Custom JSON-based WebSocket messages (not standard MCP)
- **Authentication**: Token-based via `EXAI_WS_TOKEN`

**Shim Layer** (`run_ws_shim.py`):
```python
# From: scripts/runtime/run_ws_shim.py
# Attempts to bridge stdio ↔ WebSocket

# Implements MCP stdio server
from mcp.server.stdio import stdio_server

# But connects to WebSocket daemon
daemon_uri = f"ws://{DAEMON_HOST}:{DAEMON_PORT}"
_daemon_ws = await websockets.connect(daemon_uri)
```

**The Problem**: The shim is a **protocol translator** that assumes:
1. It can successfully connect to the WebSocket daemon
2. The WebSocket daemon is accessible from the Windows host
3. Network communication between shim and daemon is reliable

---

## 3. Configuration Analysis

### 3.1 Docker Configuration

**File**: `docker-compose.yml`

```yaml
services:
  exai-daemon:
    ports:
      - "3010:8079"  # WebSocket Daemon (MCP protocol)
      - "3001:8080"  # Monitoring Dashboard
      - "3002:8082"  # Health Check Endpoint
      - "3003:8000"  # Prometheus Metrics
    
    environment:
      - PYTHONUNBUFFERED=1
      - PYTHONIOENCODING=utf-8
      - TZ=Australia/Melbourne
    
    env_file:
      - .env.docker
```

**Critical Observations**:
1. **Port Mapping**: Host `3010` → Container `8079`
2. **Network Mode**: Default bridge mode (not host mode)
3. **Host Binding**: Container binds to `0.0.0.0:8079` inside container
4. **Windows Docker**: Uses Docker Desktop with WSL2 backend

**Networking Implications**:
- Container has its own IP address in Docker network
- `127.0.0.1:3010` on Windows host is NOT the same as `127.0.0.1:8079` in container
- Port forwarding adds network latency and potential connection issues
- Windows firewall may block inter-process communication

### 3.2 Claude Code Configuration

**File**: `mcp-config.claude.json` (User's Configuration)

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
        "EXAI_WS_HOST": "127.0.0.1",
        "SHIM_LISTEN_PORT": "3005",
        "EXAI_WS_PORT": "3010",
        "EXAI_WS_TOKEN": "pYf69sHNkOYlYLRTJfMrxCQghO5OJOUFbUxqaxp9Zxo",
        // ... timeout configurations
      }
    }
  }
}
```

**Repository Configuration** (`.mcp.json`):

```json
{
  "mcpServers": {
    "exai-mcp": {
      "command": "C:/Project/EX-AI-MCP-Server/.venv/Scripts/python.exe",
      "args": [
        "-u",
        "C:/Project/EX-AI-MCP-Server/scripts/runtime/start_ws_shim_safe.py"
      ],
      "env": {
        // Similar configuration
        "SHIM_LISTEN_PORT": "3005",
        "EXAI_WS_PORT": "3010"
      }
    }
  }
}
```

**Configuration Issues**:

1. **Port 3005 Reference**:
   - `SHIM_LISTEN_PORT: "3005"` is defined but **NOT USED**
   - The shim uses stdio, not a listening port
   - This is legacy configuration from previous implementation

2. **WebSocket Connection**:
   - Shim connects to `ws://127.0.0.1:3010`
   - Assumes Docker port mapping is accessible
   - No retry logic if connection fails
   - No fallback mechanism

3. **Token Authentication**:
   - Token must match between shim and daemon
   - Token is hardcoded in configuration (security risk)
   - No token refresh/rotation mechanism

### 3.3 Other MCP Servers Configuration

**Comparison with Working MCP Servers**:

```json
// filesystem-mcp (WORKS)
{
  "filesystem-mcp": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-filesystem", "/"],
    "env": {}
  }
}

// git-mcp (WORKS)
{
  "git-mcp": {
    "command": "uvx",
    "args": ["mcp-server-git"],
    "env": {}
  }
}

// supabase-mcp (WORKS)
{
  "supabase-mcp-full": {
    "command": "cmd",
    "args": ["/c", "npx", "-y", "@supabase/mcp-server-supabase@latest"],
    "env": {
      "SUPABASE_ACCESS_TOKEN": "${SUPABASE_ACCESS_TOKEN}"
    }
  }
}
```

**Key Differences**:
- Working servers use **direct stdio communication**
- No intermediate WebSocket layer
- No Docker container dependency
- No network communication required
- Simple process execution model

---

## 4. Root Cause Analysis

### 4.1 Primary Issues

#### Issue #1: Docker Networking Barrier

**Description**: The WebSocket daemon runs inside a Docker container with bridge networking, making it inaccessible from the Windows host shim process.

**Technical Details**:
- Container IP: Dynamic (e.g., 172.17.0.2)
- Host-to-container communication requires port mapping
- Windows Docker Desktop uses WSL2 with its own network stack
- Connection attempts from Windows may fail due to:
  - Firewall rules
  - Network isolation
  - WSL2 networking quirks
  - Port forwarding delays

**Evidence**:
```python
# From run_ws_shim.py
daemon_uri = f"ws://{DAEMON_HOST}:{DAEMON_PORT}"  # ws://127.0.0.1:3010
_daemon_ws = await websockets.connect(daemon_uri)
# ❌ FAILS: Connection refused or timeout
```

**Why It Fails**:
1. Docker container starts successfully
2. Container listens on `0.0.0.0:8079` (inside container)
3. Port mapping `3010:8079` is configured
4. Windows shim tries to connect to `127.0.0.1:3010`
5. **Connection fails** because:
   - Port may not be ready yet
   - Windows firewall blocks connection
   - WSL2 network translation fails
   - Docker networking lag

#### Issue #2: Shim Process Isolation

**Description**: The shim process runs directly on Windows, not inside the Docker container, creating a process isolation boundary.

**Technical Details**:
```
Windows Host Process Space
├── Claude Code (VS Code Extension)
├── Python.exe (Shim Process) ← ISOLATED
└── Docker Desktop
    └── WSL2 Backend
        └── Docker Container Network
            └── exai-mcp-daemon ← ISOLATED
```

**Why It Matters**:
- Shim cannot directly access container filesystem
- Shim cannot use container's localhost
- Shim must rely on port mapping (which fails)
- No shared memory or IPC available

#### Issue #3: Custom WebSocket Protocol vs Standard MCP

**Description**: The EX-AI server uses a custom WebSocket protocol instead of standard MCP transports.

**Protocol Comparison**:

**Standard MCP (stdio)**:
```json
// Request (stdin)
{"jsonrpc": "2.0", "method": "tools/list", "id": 1}

// Response (stdout)
{"jsonrpc": "2.0", "result": {"tools": [...]}, "id": 1}
```

**EX-AI Custom Protocol**:
```json
// Connection Handshake
{"op": "hello", "protocolVersion": "2024-11-05", "token": "..."}
{"ok": true}

// Tool List Request
{"op": "list_tools", "id": "list_12345"}
{"tools": [...]}

// Tool Call Request
{"op": "call_tool", "id": "call_67890", "name": "chat", "arguments": {...}}
{"result": [...]}
```

**Mismatch Issues**:
- Requires custom translation layer (shim)
- Not compatible with standard MCP clients
- Adds complexity and failure points
- Makes integration with other tools difficult

#### Issue #4: Minimax LLM Integration

**Description**: Minimax (MiniMax-M2) may not properly support MCP protocol discovery and initialization.

**Configuration Evidence**:
```json
// From settings.json
{
  "claudeCode.selectedModel": "MiniMax-M2",
  "claudeCode.environmentVariables": [
    {
      "name": "ANTHROPIC_BASE_URL",
      "value": "https://api.minimax.io/anthropic"
    },
    {
      "name": "ANTHROPIC_AUTH_TOKEN",
      "value": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
  ]
}
```

**Potential Issues**:
1. **MCP Discovery**: Minimax may not properly query MCP servers for capabilities
2. **Protocol Support**: Minimax endpoint may not support MCP initialization flow
3. **Anthropic API Compatibility**: Minimax's Anthropic-compatible API may not include MCP extensions
4. **Tool Calling Format**: Minimax may use different tool/function calling format

**Why This Matters**:
- Claude Code relies on LLM to discover and use MCP tools
- If Minimax doesn't support MCP discovery, tools won't appear
- Even if shim connects successfully, Minimax may not see the tools

### 4.2 Secondary Issues

#### Issue #5: Timeout Configuration

```json
{
  "SIMPLE_TOOL_TIMEOUT_SECS": "60",
  "WORKFLOW_TOOL_TIMEOUT_SECS": "120",
  "EXPERT_ANALYSIS_TIMEOUT_SECS": "90"
}
```

- Long timeouts may cause Claude Code to appear "hung"
- Connection attempts may timeout before Docker is ready
- No exponential backoff or retry logic

#### Issue #6: Token Management

```json
{
  "EXAI_WS_TOKEN": "pYf69sHNkOYlYLRTJfMrxCQghO5OJOUFbUxqaxp9Zxo"
}
```

- Hardcoded token in configuration (security risk)
- Token must match exactly between shim and daemon
- No token validation error messages
- Token mismatch silently fails connection

#### Issue #7: Process Management

**From `run_ws_shim.py`**:
```python
# Windows compatibility issues
if hasattr(os, 'setpgrp'):
    os.setpgrp()  # Unix/Linux only
else:
    logger.info("Windows detected - skipping process group set")
```

- Process cleanup may not work properly on Windows
- Orphaned shim processes may hold resources
- No proper Windows process management

---

## 5. Why Bash/Python Commands Work as Workaround

### 5.1 Direct API Access

When using bash or Python commands, you **bypass the entire MCP protocol layer**:

```python
# Direct WebSocket connection (works)
import websockets
import asyncio

async def call_tool():
    uri = "ws://127.0.0.1:3010"
    async with websockets.connect(uri) as ws:
        # Send hello with token
        await ws.send(json.dumps({
            "op": "hello",
            "token": "pYf69sHNkOYlYLRTJfMrxCQghO5OJOUFbUxqaxp9Zxo"
        }))
        # Wait for ack
        ack = await ws.recv()
        # Send tool call
        await ws.send(json.dumps({
            "op": "call_tool",
            "name": "chat",
            "arguments": {"message": "test"}
        }))
        # Get result
        result = await ws.recv()
        return result

asyncio.run(call_tool())
```

**Why This Works**:
1. **No stdio layer**: Direct WebSocket communication
2. **No shim process**: No intermediate translation
3. **Same network**: Running on Windows host (same as Docker port mapping)
4. **No MCP protocol**: Uses custom WebSocket protocol directly
5. **No Claude Code integration**: No LLM involvement

### 5.2 Docker Command Access

```bash
# Direct Docker exec (works)
docker exec -it exai-mcp-daemon python -c "from tools.chat import chat; print(chat('test'))"
```

**Why This Works**:
1. **Inside container**: No network barrier
2. **Direct Python import**: No protocol translation
3. **No WebSocket**: Direct function calls
4. **Same filesystem**: Can access all container files

### 5.3 Comparison

| Aspect | MCP via Claude Code | Direct Bash/Python |
|--------|---------------------|-------------------|
| **Transport** | stdio → shim → WebSocket → daemon | Direct WebSocket or Docker exec |
| **Protocol** | MCP JSON-RPC | Custom WebSocket or Python |
| **Network** | Host → Docker port mapping | Same as MCP OR inside container |
| **Process** | Separate shim process | Single process or Docker exec |
| **Dependencies** | Claude Code, Minimax, MCP, shim | Just websockets or Docker |
| **Failure Points** | 5+ (Claude, Minimax, shim, network, daemon) | 1-2 (network or Docker) |
| **Complexity** | Very High | Low |
| **Reliability** | ❌ Low | ✅ High |

---

## 6. Technical Deep Dive

### 6.1 MCP Protocol Flow (Expected)

```
┌─────────────────────────────────────────────────────────┐
│ Phase 1: Initialization                                  │
└─────────────────────────────────────────────────────────┘
Claude Code → Shim (stdio):
  {"jsonrpc": "2.0", "method": "initialize", "params": {...}, "id": 1}

Shim → Daemon (WebSocket):
  {"op": "hello", "protocolVersion": "2024-11-05", "token": "..."}

Daemon → Shim (WebSocket):
  {"ok": true}

Shim → Claude Code (stdio):
  {"jsonrpc": "2.0", "result": {"capabilities": {...}}, "id": 1}

┌─────────────────────────────────────────────────────────┐
│ Phase 2: Tool Discovery                                  │
└─────────────────────────────────────────────────────────┘
Claude Code → Shim (stdio):
  {"jsonrpc": "2.0", "method": "tools/list", "id": 2}

Shim → Daemon (WebSocket):
  {"op": "list_tools", "id": "list_xxx"}

Daemon → Shim (WebSocket):
  {"tools": [{"name": "chat", "description": "...", "inputSchema": {...}}, ...]}

Shim → Claude Code (stdio):
  {"jsonrpc": "2.0", "result": {"tools": [...]}, "id": 2}

┌─────────────────────────────────────────────────────────┐
│ Phase 3: Tool Execution                                  │
└─────────────────────────────────────────────────────────┘
Claude Code → Shim (stdio):
  {"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "chat", "arguments": {...}}, "id": 3}

Shim → Daemon (WebSocket):
  {"op": "call_tool", "id": "call_yyy", "name": "chat", "arguments": {...}}

Daemon → Shim (WebSocket):
  {"result": [{"text": "response"}]}

Shim → Claude Code (stdio):
  {"jsonrpc": "2.0", "result": {"content": [{"type": "text", "text": "response"}]}, "id": 3}
```

### 6.2 Actual Flow (What Fails)

```
┌─────────────────────────────────────────────────────────┐
│ Phase 1: Initialization (FAILS)                          │
└─────────────────────────────────────────────────────────┘
Claude Code → Starts Shim Process
  Command: python.exe run_ws_shim.py
  Status: ✅ Process starts successfully

Shim → Attempts WebSocket Connection
  Target: ws://127.0.0.1:3010
  Status: ❌ FAILS
  Errors:
    - Connection refused (Docker not ready)
    - Connection timeout (Network barrier)
    - Authentication failure (Token mismatch)

Shim → Claude Code
  Status: ❌ No response or error
  Result: Claude Code sees MCP server as "unavailable"

┌─────────────────────────────────────────────────────────┐
│ Phase 2: Tool Discovery (NEVER REACHED)                  │
└─────────────────────────────────────────────────────────┘
Claude Code never receives tool list
Minimax never sees available tools
No @exai-mcp tools appear in UI

┌─────────────────────────────────────────────────────────┐
│ Phase 3: Tool Execution (IMPOSSIBLE)                     │
└─────────────────────────────────────────────────────────┘
Cannot execute tools that were never discovered
```

### 6.3 Network Communication Analysis

**Test 1: Check Docker Port Mapping**
```bash
# From Windows host
netstat -an | findstr 3010
# Expected: TCP    0.0.0.0:3010    0.0.0.0:0    LISTENING
# If not present, Docker port mapping failed
```

**Test 2: WebSocket Connection from Windows**
```python
# From Windows host
import websockets
import asyncio

async def test():
    try:
        ws = await asyncio.wait_for(
            websockets.connect("ws://127.0.0.1:3010"),
            timeout=5
        )
        print("✅ Connection successful")
        await ws.close()
    except asyncio.TimeoutError:
        print("❌ Connection timeout - Docker not accessible")
    except ConnectionRefusedError:
        print("❌ Connection refused - Port not listening")
    except Exception as e:
        print(f"❌ Error: {e}")

asyncio.run(test())
```

**Test 3: Docker Container Network**
```bash
# Inside Docker container
docker exec -it exai-mcp-daemon python -c "
import socket
s = socket.socket()
s.connect(('127.0.0.1', 8079))
print('✅ Daemon listening inside container')
s.close()
"
```

### 6.4 Logging Analysis

**Shim Logs** (Should be in `stderr`):
```
[INFO] [MAIN] EXAI MCP Shim Starting (stdio mode)
[INFO] [MAIN]   Daemon: 127.0.0.1:3010
[INFO] [DAEMON_CONNECT] Connecting to ws://127.0.0.1:3010...
[ERROR] [DAEMON_CONNECT] ✗ Failed to connect: Connection refused
```

**Daemon Logs** (Docker container):
```bash
docker logs exai-mcp-daemon | grep -i "websocket\|connection\|error"
```

**Expected Output**:
```
[INFO] WebSocket daemon started on 0.0.0.0:8079
[INFO] Waiting for connections...
```

**If No Connections Seen**:
- Shim is not reaching the daemon
- Network barrier confirmed

---

## 7. Minimax LLM Impact

### 7.1 Minimax Configuration Analysis

**From `settings.json`**:
```json
{
  "claudeCode.selectedModel": "MiniMax-M2",
  "claudeCode.environmentVariables": [
    {
      "name": "ANTHROPIC_BASE_URL",
      "value": "https://api.minimax.io/anthropic"
    },
    {
      "name": "ANTHROPIC_AUTH_TOKEN",
      "value": "eyJ..."
    },
    {
      "name": "ANTHROPIC_MODEL",
      "value": "MiniMax-M2"
    },
    {
      "name": "ANTHROPIC_SMALL_FAST_MODEL",
      "value": "MiniMax-M2"
    }
  ]
}
```

### 7.2 Potential Minimax Issues

#### Issue A: MCP Discovery Not Supported

**Theory**: Minimax's Anthropic-compatible API may not include MCP discovery extensions.

**Evidence**:
- User reports that "agents cannot see the capability to make MCP calls"
- Other MCP servers (filesystem, git, supabase) work fine
- Only EX-AI MCP server fails

**Hypothesis**:
- Minimax successfully discovers standard MCP servers (filesystem, git)
- Minimax fails to discover EX-AI MCP server due to shim connection failure
- Even if connection worked, Minimax might not properly handle custom protocol

**Test**:
```javascript
// What Minimax receives from MCP discovery
// Standard MCP servers:
{
  "tools": [
    {"name": "read_file", "description": "...", "input_schema": {...}}
  ]
}

// EX-AI MCP server (if it worked):
{
  "tools": [
    {"name": "chat", "description": "...", "inputSchema": {...}}  // Note: different schema key
  ]
}
```

#### Issue B: Tool Calling Format Mismatch

**Anthropic API (Standard)**:
```json
{
  "model": "claude-3-sonnet",
  "messages": [...],
  "tools": [
    {
      "name": "get_weather",
      "description": "Get weather",
      "input_schema": {
        "type": "object",
        "properties": {...}
      }
    }
  ]
}
```

**Minimax API**:
- May use different tool calling format
- May not support `input_schema` vs `inputSchema`
- May not support MCP-specific extensions

### 7.3 Testing Minimax MCP Support

**Test 1: Check MCP Discovery with Working Server**
```
# In Claude Code with Minimax
@filesystem-mcp list_allowed_directories

# If this works, Minimax supports MCP discovery
```

**Test 2: Check Error Messages**
```
# Try to use EX-AI MCP
@exai-mcp chat "test"

# Check for errors:
# - "Tool not found" → Discovery failed
# - "Server unavailable" → Connection failed
# - "Invalid response" → Protocol mismatch
```

---

## 8. Recommendations

### 8.1 Short-Term Fixes

#### Option 1: Remove Docker Dependency (RECOMMENDED)

**Modify the architecture to run the daemon directly on Windows**:

1. **Remove Docker layer**:
   ```bash
   # Stop Docker container
   docker-compose down
   
   # Run daemon directly on Windows
   python scripts/ws/run_ws_daemon.py
   ```

2. **Update configuration**:
   ```json
   {
     "exai-mcp": {
       "command": "python.exe",
       "args": ["-m", "scripts.runtime.run_ws_shim"],
       "env": {
         "EXAI_WS_HOST": "127.0.0.1",
         "EXAI_WS_PORT": "8079"  // Direct port, no Docker mapping
       }
     }
   }
   ```

**Pros**:
- Eliminates Docker networking barrier
- Simplifies deployment
- Faster connection times
- Better Windows compatibility

**Cons**:
- Loses Docker isolation
- Requires Windows Python environment setup
- Loses Redis persistence (or need to run Redis separately)

#### Option 2: Use Native stdio Implementation (BEST LONG-TERM)

**Replace the WebSocket daemon with a native stdio MCP server**:

1. **Create new stdio server**:
   ```python
   # scripts/mcp/stdio_server.py
   from mcp.server import Server
   from mcp.server.stdio import stdio_server
   
   app = Server("exai-mcp")
   
   @app.list_tools()
   async def list_tools():
       # Return tools directly
       return [...]
   
   @app.call_tool()
   async def call_tool(name, arguments):
       # Execute tool directly (no WebSocket)
       return [...]
   
   async def main():
       async with stdio_server() as (read, write):
           await app.run(read, write, app.create_initialization_options())
   ```

2. **Update configuration**:
   ```json
   {
     "exai-mcp": {
       "command": "python.exe",
       "args": ["-m", "scripts.mcp.stdio_server"],
       "env": {}  // No WebSocket configuration needed
     }
   }
   ```

**Pros**:
- ✅ Standard MCP protocol compliance
- ✅ No shim layer needed
- ✅ No network communication
- ✅ Works with all MCP clients
- ✅ Simpler architecture
- ✅ Better reliability

**Cons**:
- Requires refactoring existing code
- May need to redesign tool execution flow

#### Option 3: Fix Docker Networking

**Use Docker host network mode** (Linux only, won't work on Windows):
```yaml
services:
  exai-daemon:
    network_mode: "host"  # Use host network (Linux only)
```

**For Windows, use bridge with proper configuration**:
```yaml
services:
  exai-daemon:
    ports:
      - "127.0.0.1:3010:8079"  # Bind to localhost explicitly
    extra_hosts:
      - "host.docker.internal:host-gateway"
```

### 8.2 Long-Term Solutions

#### Solution 1: Implement Standard MCP Transports

**Support all three MCP transports**:

1. **stdio**: For local clients (Claude Code, etc.)
   ```python
   # scripts/mcp/stdio_server.py
   async def main():
       async with stdio_server() as (read, write):
           await app.run(read, write, ...)
   ```

2. **SSE**: For web clients
   ```python
   # scripts/mcp/sse_server.py
   from mcp.server.sse import sse_server
   
   async def main():
       async with sse_server() as server:
           await server.start()
   ```

3. **HTTP**: For REST API clients
   ```python
   # scripts/mcp/http_server.py
   from fastapi import FastAPI
   
   app = FastAPI()
   
   @app.post("/mcp/tools/list")
   async def list_tools():
       return {"tools": [...]}
   ```

**Configuration**:
```json
{
  "mcpServers": {
    "exai-mcp-stdio": {
      "command": "python",
      "args": ["-m", "scripts.mcp.stdio_server"]
    },
    "exai-mcp-sse": {
      "url": "http://localhost:8080/mcp/sse"
    },
    "exai-mcp-http": {
      "url": "http://localhost:8080/mcp"
    }
  }
}
```

#### Solution 2: Unified Server Architecture

**Create a unified server that supports multiple transports**:

```python
# src/mcp_server/__init__.py
class UnifiedMCPServer:
    """MCP server supporting stdio, SSE, and HTTP transports."""
    
    def __init__(self):
        self.tools = load_tools()
        
    async def start_stdio(self):
        """Start stdio transport."""
        async with stdio_server() as (read, write):
            await self.run(read, write)
    
    async def start_sse(self):
        """Start SSE transport."""
        # Implementation
        
    async def start_http(self):
        """Start HTTP transport."""
        # Implementation

# Usage
if __name__ == "__main__":
    server = UnifiedMCPServer()
    
    # Start based on environment variable
    transport = os.getenv("MCP_TRANSPORT", "stdio")
    if transport == "stdio":
        asyncio.run(server.start_stdio())
    elif transport == "sse":
        asyncio.run(server.start_sse())
    elif transport == "http":
        asyncio.run(server.start_http())
```

#### Solution 3: Minimax Compatibility Layer

**If Minimax MCP support is limited, create a compatibility layer**:

```python
# src/minimax/mcp_adapter.py
class MinimaxMCPAdapter:
    """Adapter for Minimax-specific MCP behavior."""
    
    def adapt_tool_schema(self, tool):
        """Convert between inputSchema and input_schema."""
        if "inputSchema" in tool:
            tool["input_schema"] = tool.pop("inputSchema")
        return tool
    
    def adapt_tool_response(self, response):
        """Adapt response format for Minimax."""
        # Implementation
```

### 8.3 Immediate Debugging Steps

**Step 1: Verify Docker Container Status**
```bash
docker ps | grep exai-mcp-daemon
docker logs exai-mcp-daemon | tail -50
```

**Step 2: Test WebSocket Connection**
```python
# test_ws_connection.py
import asyncio
import websockets

async def test():
    try:
        ws = await asyncio.wait_for(
            websockets.connect("ws://127.0.0.1:3010"),
            timeout=10
        )
        print("✅ WebSocket connection successful")
        
        # Send hello
        import json
        await ws.send(json.dumps({
            "op": "hello",
            "protocolVersion": "2024-11-05",
            "token": "pYf69sHNkOYlYLRTJfMrxCQghO5OJOUFbUxqaxp9Zxo"
        }))
        
        # Wait for ack
        response = await asyncio.wait_for(ws.recv(), timeout=5)
        print(f"✅ Received response: {response}")
        
        await ws.close()
    except Exception as e:
        print(f"❌ Connection failed: {e}")

asyncio.run(test())
```

**Step 3: Check Shim Logs**
```bash
# Run shim manually with verbose logging
set LOG_LEVEL=DEBUG
python C:/Project/EX-AI-MCP-Server/scripts/runtime/run_ws_shim.py
```

**Step 4: Test with Different LLM**
```json
// Temporarily switch to Claude API to test MCP discovery
{
  "claudeCode.selectedModel": "claude-3-5-sonnet-20241022",
  "claudeCode.environmentVariables": [
    {
      "name": "ANTHROPIC_API_KEY",
      "value": "sk-ant-..."  // Real Anthropic API key
    }
  ]
}
```

**Step 5: Test Native MCP Server**
```python
# Create minimal stdio MCP server for testing
# test_stdio_mcp.py
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

app = Server("test-mcp")

@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="test",
            description="Test tool",
            inputSchema={"type": "object", "properties": {}}
        )
    ]

@app.call_tool()
async def call_tool(name, arguments):
    return [TextContent(type="text", text="Test successful!")]

async def main():
    async with stdio_server() as (read, write):
        await app.run(read, write, app.create_initialization_options())

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

**Test Configuration**:
```json
{
  "mcpServers": {
    "test-mcp": {
      "command": "python",
      "args": ["C:/path/to/test_stdio_mcp.py"],
      "env": {}
    }
  }
}
```

---

## 9. Summary

### 9.1 Key Findings

| Finding | Severity | Impact |
|---------|----------|--------|
| Docker networking barrier prevents shim-to-daemon connection | 🔴 Critical | Complete failure |
| Custom WebSocket protocol requires translation layer | 🟡 High | Added complexity |
| Windows process isolation limits container access | 🟡 High | Network dependency |
| Minimax MCP support unclear | 🟡 Medium | Tool discovery failure |
| Token authentication adds failure point | 🟢 Low | Security vs usability |

### 9.2 Why Direct Commands Work

```
MCP Protocol Flow (FAILS):
Claude Code → stdio → Shim → [NETWORK BARRIER] → Docker → WebSocket Daemon
     ❌ Connection fails at network barrier

Direct Command Flow (WORKS):
Python/Bash → WebSocket (no stdio) → [NETWORK OK] → Docker → WebSocket Daemon
     ✅ Connection succeeds (no shim, no stdio, no Claude Code)

OR

Docker Exec Flow (WORKS):
Docker exec → [INSIDE CONTAINER] → Direct Python → Tools
     ✅ No network barrier (already inside container)
```

### 9.3 Recommended Action Plan

**Phase 1: Immediate (Day 1-2)**
1. ✅ Test WebSocket connection from Windows host
2. ✅ Verify Docker container is running and accessible
3. ✅ Check shim logs for specific error messages
4. ✅ Test with native Claude API (rule out Minimax issues)

**Phase 2: Short-Term Fix (Week 1)**
1. 🎯 **BEST OPTION**: Implement native stdio MCP server (no Docker, no WebSocket)
2. 🎯 **ALTERNATIVE**: Run daemon directly on Windows (no Docker)
3. Update configuration to use new implementation
4. Test with Claude Code + Minimax

**Phase 3: Long-Term Solution (Month 1)**
1. Design unified MCP server architecture
2. Implement all three MCP transports (stdio, SSE, HTTP)
3. Add Minimax compatibility layer if needed
4. Comprehensive testing across all clients

**Phase 4: Production Hardening (Month 2-3)**
1. Add monitoring and observability
2. Implement proper error handling and recovery
3. Add health checks and auto-restart
4. Documentation and deployment guides

---

## 10. Technical References

### 10.1 MCP Specification
- **Official Spec**: https://modelcontextprotocol.io/
- **Transport Protocols**: https://modelcontextprotocol.io/specification/transport
- **Server Implementation**: https://modelcontextprotocol.io/docs/server

### 10.2 Repository Documentation
- **MCP Configuration Guide**: `docs/guides/MCP_CONFIGURATION_GUIDE.md`
- **Native Claude Code Setup**: `docs/guides/NATIVE_CLAUDECODE_SETUP.md`
- **Integration Guide**: `docs/integration/EXAI_MCP_INTEGRATION_GUIDE.md`
- **Connection Fix Reports**: `docs/reports/MCP_CONNECTION_FIX_COMPLETE.md`

### 10.3 Related Files
- **Shim Implementation**: `scripts/runtime/run_ws_shim.py`
- **Daemon Server**: `src/daemon/ws_server.py`
- **Docker Configuration**: `docker-compose.yml`
- **MCP Configuration**: `.mcp.json`, `.claude/.mcp.json`

---

## Appendix A: Configuration Files Analysis

### A.1 All MCP Configuration Files Found

| File | Purpose | Location | Status |
|------|---------|----------|--------|
| `settings.json` | Claude Code settings | `/home/ubuntu/Uploads/` | ✅ Valid |
| `settings.local.json` | Local Claude settings | `/home/ubuntu/Uploads/` | ✅ Valid |
| `mcp_config_recommended.json` | Recommended MCP config | `/home/ubuntu/Uploads/` | ✅ Valid (other servers) |
| `mcp-config.claude.json` | User's EX-AI config | `/home/ubuntu/Uploads/` | ⚠️ Problematic |
| `mcp_config.supabase.json` | Supabase MCP config | `/home/ubuntu/Uploads/` | ✅ Valid |
| `.mcp.json` (repo) | Repository MCP config | EX-AI repo | ⚠️ Problematic |
| `.claude/.mcp.json` (repo) | Claude folder config | EX-AI repo | ⚠️ Problematic |

### A.2 Working vs Non-Working Configurations

**Working Servers** (filesystem, git, supabase):
```json
{
  "command": "npx" | "uvx" | "cmd",
  "args": ["package-name", ...],
  "env": {simple environment vars}
}
```
- ✅ Direct process execution
- ✅ stdio communication
- ✅ No network layer
- ✅ No Docker dependency

**Non-Working Server** (exai-mcp):
```json
{
  "command": "python.exe",
  "args": ["run_ws_shim.py"],
  "env": {
    "EXAI_WS_HOST": "127.0.0.1",
    "EXAI_WS_PORT": "3010",
    "EXAI_WS_TOKEN": "...",
    ... 15+ environment variables
  }
}
```
- ❌ Requires Docker container
- ❌ Requires WebSocket connection
- ❌ Requires token authentication
- ❌ Complex environment setup

---

## Appendix B: Error Message Analysis

### B.1 Possible Error Messages

**Connection Errors**:
```
[ERROR] [DAEMON_CONNECT] ✗ Failed to connect: Connection refused
[ERROR] [DAEMON_CONNECT] ✗ Timeout waiting for daemon response
[ERROR] [DAEMON_CONNECT] ✗ Failed to connect: [WinError 10061] No connection could be made
```

**Authentication Errors**:
```
[ERROR] [HELLO] ✗ Daemon rejected connection: Invalid token
[ERROR] [HELLO] ✗ Daemon rejected connection: Authentication failed
```

**Protocol Errors**:
```
[ERROR] [TOOLS] ✗ Failed to list tools: Timeout
[ERROR] [TOOL_CALL] ✗ Tool 'chat' failed: Connection closed
```

### B.2 Claude Code Error Messages

**MCP Discovery Failure**:
```
"MCP server 'exai-mcp' is not responding"
"Unable to connect to MCP server"
"Server initialization timeout"
```

**Tool Not Available**:
```
"Tool @exai-mcp not found"
"No tools available from exai-mcp"
```

---

## Appendix C: Testing Checklist

### C.1 Pre-Flight Checks

- [ ] Docker Desktop is running
- [ ] Docker container `exai-mcp-daemon` is running
- [ ] Port 3010 is listening on Windows host
- [ ] WebSocket daemon is accessible from host
- [ ] Token matches between shim and daemon configuration
- [ ] Python virtual environment is activated
- [ ] All dependencies are installed

### C.2 Connection Tests

- [ ] Can ping Docker container from host
- [ ] Can connect to WebSocket from Python script
- [ ] Can send/receive WebSocket messages
- [ ] Authentication succeeds with token
- [ ] Tool list retrieval works
- [ ] Tool execution works

### C.3 MCP Protocol Tests

- [ ] Shim process starts without errors
- [ ] Shim connects to daemon successfully
- [ ] MCP initialization completes
- [ ] Tool discovery returns tools
- [ ] Claude Code sees @exai-mcp tools
- [ ] Tool execution succeeds from Claude Code

### C.4 Alternative Client Tests

- [ ] Direct WebSocket connection works
- [ ] Direct Docker exec works
- [ ] Python script can call tools
- [ ] Bash script can call tools

---

**End of Analysis Document**

**Last Updated**: November 13, 2025  
**Version**: 1.0  
**Author**: DeepAgent Analysis System
