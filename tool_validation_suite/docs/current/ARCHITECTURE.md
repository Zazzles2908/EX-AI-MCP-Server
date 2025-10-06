# Architecture - Tool Validation Suite

**Last Updated:** 2025-10-05

---

## 🏗️ System Architecture (NEW Approach)

### Full Stack Flow

```
Test Script
    ↓
utils/mcp_client.py (WebSocket client)
    ↓
WebSocket Daemon (ws://127.0.0.1:8765)
    ↓
src/daemon/ws_server.py (WebSocket server)
    ↓
server.py (MCP server - TOOLS, handle_call_tool)
    ↓
tools/workflows/*.py (30 tool implementations)
    ↓
src/providers/ (GLM/Kimi routing)
    ↓
External APIs (api.z.ai, api.moonshot.ai)
```

**Result:** Tests entire stack end-to-end ✅

---

## 🔄 Execution Flow

### 1. Test Initialization
- Test script imports `mcp_client.py`
- MCP client connects to WebSocket daemon
- Hello handshake exchanged

### 2. Tool Call
- Test calls `mcp_client.call_tool(tool_name, arguments)`
- Client sends "call_tool" message to daemon
- Daemon routes to `server.py`

### 3. Tool Execution
- `server.py` calls `handle_call_tool()`
- Tool implementation in `tools/workflows/` executes
- Provider routing selects GLM or Kimi
- External API called

### 4. Response
- API response flows back through stack
- Progress messages sent during execution
- Final result returned to test script

### 5. Validation
- Test validates response
- Results collected
- Reports generated

---

## 📦 Key Components

### MCP Client (`utils/mcp_client.py`)
- WebSocket client
- MCP protocol implementation
- Connects to daemon

### WebSocket Daemon (`src/daemon/ws_server.py`)
- Listens on port 8765
- Imports from `server.py`
- Routes tool calls

### MCP Server (`server.py`)
- Exports TOOLS and handle_call_tool
- Tool registration
- Execution logic

### Tools (`tools/workflows/*.py`)
- 30 tool implementations
- Actual business logic
- Provider integration

### Providers (`src/providers/`)
- GLM/Kimi routing
- API integration
- Response handling

---

## 🎯 What Gets Tested

✅ MCP Protocol (WebSocket handshake, messages)
✅ WebSocket Daemon (connection, routing)
✅ MCP Server (tool registration, execution)
✅ Tool Implementations (actual code)
✅ Provider Routing (GLM vs Kimi selection)
✅ External APIs (connectivity, responses)

**Result:** Full stack validation

---

## 📊 Test Coverage

**30 Tools:**
- 14 core tools (chat, analyze, debug, etc.)
- 8 advanced tools (listmodels, version, etc.)
- 8 provider tools (kimi_upload, glm_web_search, etc.)

**Test Variations:**
- Basic functionality
- Different models
- Error handling
- Edge cases

---

## 🔧 OLD vs NEW Architecture

### OLD (Deprecated)
```
Test → api_client.py → External APIs
```
**Problem:** Bypasses MCP server, daemon, tools

### NEW (Current)
```
Test → mcp_client.py → Daemon → Server → Tools → APIs
```
**Benefit:** Tests entire stack

---

## 📁 Directory Structure

```
tool_validation_suite/
├── utils/
│   ├── mcp_client.py       ⭐ Primary client
│   ├── test_runner.py      Test orchestration
│   ├── prompt_counter.py   Cost tracking
│   └── ...                 Supporting utilities
├── tests/
│   ├── MCP_TEST_TEMPLATE.py  ⭐ Working example
│   ├── core_tools/          14 test files
│   ├── advanced_tools/      8 test files
│   ├── provider_tools/      8 test files
│   └── integration/         6 test files
├── results/
│   └── latest/             Test results
└── docs/
    └── current/            Documentation
```

---

## 🚀 How to Use

### 1. Start Daemon
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\ws_start.ps1 -Restart
```

### 2. Run Test
```python
from utils.mcp_client import MCPClient

mcp_client = MCPClient()
result = mcp_client.call_tool(
    tool_name="chat",
    arguments={"prompt": "Hello", "model": "glm-4.5-flash"}
)
```

### 3. Validate
```python
assert result["success"]
assert len(result["outputs"]) > 0
```

---

## ✅ Summary

**Architecture:** Full stack testing through WebSocket daemon
**Coverage:** All 30 tools, multiple variations
**Validation:** End-to-end from MCP protocol to external APIs
**Status:** Infrastructure ready, test scripts need regeneration

