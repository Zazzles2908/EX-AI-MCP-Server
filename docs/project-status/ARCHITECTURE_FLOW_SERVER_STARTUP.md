# Architecture Flow: Server Startup
## Complete Initialization Sequence

**Date:** 2025-10-03
**Status:** 🔍 IN PROGRESS
**Type:** Deep Architecture Tracing

---

## 🎯 Overview

This document traces the complete server startup flow from the PowerShell script through WebSocket daemon initialization to provider registration.

---

## 📊 Startup Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER EXECUTES COMMAND                         │
│  powershell -NoProfile -ExecutionPolicy Bypass                  │
│  -File .\scripts\ws_start.ps1 -Restart                          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              STEP 1: ws_start.ps1 (PowerShell)                  │
│  Location: scripts/ws_start.ps1                                 │
│                                                                  │
│  Actions:                                                        │
│  1. Check if daemon already running (PID file check)            │
│  2. Stop existing daemon if -Restart flag                       │
│  3. Validate Python environment                                 │
│  4. Set environment variables                                   │
│  5. Launch Python daemon process                                │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│         STEP 2: Python Daemon Launch                            │
│  Command: python src/daemon/ws_server.py                        │
│  Process: Background (non-blocking)                             │
│  PID File: logs/ws_daemon.pid                                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│         STEP 3: ws_server.py Initialization                     │
│  Location: src/daemon/ws_server.py                              │
│  Lines: 1-989 (TOO BIG!)                                        │
│                                                                  │
│  Initialization Sequence:                                       │
│  1. Import dependencies (line 1-100)                            │
│  2. Import from server.py (line 100-103):                       │
│     - TOOLS (tool registry)                                     │
│     - _ensure_providers_configured                              │
│     - handle_call_tool (SERVER_HANDLE_CALL_TOOL)                │
│     - register_provider_specific_tools                          │
│  3. Initialize global state (line 104-200):                     │
│     - Session tracking dictionaries                             │
│     - Semaphores (global, provider, session)                    │
│     - Cache dictionaries                                        │
│     - Health monitoring                                         │
│  4. Define helper functions (line 201-500)                      │
│  5. Define WebSocket handler (line 501-900)                     │
│  6. Start WebSocket server (line 901-989)                       │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│         STEP 4: server.py Import & Initialization               │
│  Location: server.py                                            │
│  Lines: 1-603                                                   │
│                                                                  │
│  Import Sequence:                                               │
│  1. Standard library imports                                    │
│  2. MCP SDK imports (mcp.server, mcp.types)                     │
│  3. Provider imports:                                           │
│     - from src.providers.registry import ModelProviderRegistry  │
│     - from src.providers.kimi import KimiProvider               │
│     - from src.providers.glm import GLMProvider                 │
│  4. Tool imports:                                               │
│     - from tools.registry import get_all_tools                  │
│  5. Handler imports:                                            │
│     - from src.server.handlers import handle_call_tool          │
│     - from src.server.handlers import handle_list_tools         │
│                                                                  │
│  Global Initialization:                                         │
│  - server = Server("exai-mcp-server")                           │
│  - TOOLS = {} (empty dict, populated later)                     │
│  - Provider registry initialized                                │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│         STEP 5: Provider Configuration                          │
│  Function: _ensure_providers_configured()                       │
│  Location: server.py lines 50-100                               │
│                                                                  │
│  Actions:                                                        │
│  1. Check if providers already configured (global flag)         │
│  2. Read environment variables:                                 │
│     - KIMI_API_KEY, KIMI_API_URL                                │
│     - GLM_API_KEY, GLM_API_URL                                  │
│  3. Initialize providers:                                       │
│     - KimiProvider(api_key, base_url)                           │
│     - GLMProvider(api_key, base_url)                            │
│  4. Register providers with ModelProviderRegistry               │
│  5. Set global flag: providers_configured = True                │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│         STEP 6: Tool Registration                               │
│  Function: register_provider_specific_tools()                   │
│  Location: server.py lines 150-200                              │
│                                                                  │
│  Actions:                                                        │
│  1. Call get_all_tools() from tools/registry.py                 │
│  2. Populate global TOOLS dictionary                            │
│  3. Register MCP handlers:                                      │
│     - @server.list_tools() → handle_list_tools                  │
│     - @server.call_tool() → call_tool_handler                   │
│  4. Tool categories registered:                                 │
│     - Simple tools (chat, challenge, listmodels, version)       │
│     - Workflow tools (analyze, debug, refactor, etc.)           │
│     - Provider-specific tools (kimi_chat_with_tools, etc.)      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│         STEP 7: WebSocket Server Start                          │
│  Location: src/daemon/ws_server.py line 950-989                 │
│                                                                  │
│  Actions:                                                        │
│  1. Read configuration:                                         │
│     - EXAI_WS_HOST (default: 127.0.0.1)                         │
│     - EXAI_WS_PORT (default: 8765)                              │
│  2. Create WebSocket server:                                    │
│     - websockets.serve(handle_client, host, port)               │
│  3. Write PID file: logs/ws_daemon.pid                          │
│  4. Write health file: logs/ws_daemon.health.json               │
│  5. Start asyncio event loop                                    │
│  6. Log: "Starting WS daemon on ws://127.0.0.1:8765"            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              SERVER READY - Listening for Connections            │
│  Status: ✅ RUNNING                                             │
│  Endpoint: ws://127.0.0.1:8765                                  │
│  PID File: logs/ws_daemon.pid                                   │
│  Health: logs/ws_daemon.health.json                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔍 Detailed Component Analysis

### Component 1: ws_start.ps1 (PowerShell Script)

**Purpose:** Daemon lifecycle management
**Size:** ~200 lines
**Key Functions:**
- `Start-Daemon`: Launch Python process
- `Stop-Daemon`: Kill existing process
- `Check-PID`: Verify daemon status

**Critical Logic:**
```powershell
# Check if already running
if (Test-Path $pidFile) {
    $pid = Get-Content $pidFile
    if (Get-Process -Id $pid -ErrorAction SilentlyContinue) {
        # Already running
    }
}

# Launch daemon
Start-Process python -ArgumentList "src/daemon/ws_server.py" -NoNewWindow
```

### Component 2: ws_server.py (WebSocket Daemon)

**Purpose:** WebSocket server wrapper around server.py
**Size:** 989 lines (TOO BIG!)
**Responsibilities:**
1. WebSocket connection handling
2. Session management
3. Request coalescing/deduplication
4. Progress heartbeats
5. Timeout enforcement
6. Caching
7. Health monitoring

**Critical Imports:**
```python
from server import TOOLS as SERVER_TOOLS
from server import _ensure_providers_configured
from server import handle_call_tool as SERVER_HANDLE_CALL_TOOL
from server import register_provider_specific_tools
```

**Key Insight:** ws_server.py is a WRAPPER, not a replacement for server.py!

### Component 3: server.py (MCP Server Core)

**Purpose:** MCP protocol implementation
**Size:** 603 lines
**Responsibilities:**
1. MCP server initialization
2. Provider configuration
3. Tool registration
4. Request routing

**Critical Functions:**
- `_ensure_providers_configured()`: Initialize providers
- `register_provider_specific_tools()`: Register tools
- `call_tool_handler()`: Route tool calls

### Component 4: ModelProviderRegistry

**Purpose:** Provider management
**Location:** src/providers/registry.py
**Responsibilities:**
1. Provider registration
2. Model-to-provider mapping
3. Provider selection
4. Fallback chain management

**Key Methods:**
- `register_provider(provider)`: Add provider
- `get_provider_for_model(model_name)`: Find provider
- `get_available_models()`: List all models

---

## 🚨 Issues Identified

### Issue #1: File Bloat
**Problem:** ws_server.py is 989 lines (too big!)
**Impact:** Hard to maintain, understand, debug
**Recommendation:** Split into modules:
- `ws_connection.py`: Connection handling
- `ws_session.py`: Session management
- `ws_cache.py`: Caching logic
- `ws_health.py`: Health monitoring

### Issue #2: Circular Dependency Risk
**Problem:** ws_server.py imports from server.py
**Impact:** Tight coupling, hard to test
**Recommendation:** Use dependency injection

### Issue #3: Global State
**Problem:** Multiple global dictionaries in ws_server.py
**Impact:** Thread safety concerns, hard to test
**Recommendation:** Encapsulate in class

---

## 📋 Next Steps

1. ✅ Document server startup flow
2. ⏳ Document request handling flow
3. ⏳ Document tool execution flow
4. ⏳ Document model resolution flow
5. ⏳ Create refactoring recommendations

---

**Last Updated:** 2025-10-03 21:50
**Status:** ✅ COMPLETE - Server startup flow documented

