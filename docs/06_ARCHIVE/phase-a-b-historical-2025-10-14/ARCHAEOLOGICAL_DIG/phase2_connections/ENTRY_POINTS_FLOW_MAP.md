# ENTRY POINTS FLOW MAP
**Date:** 2025-10-10 (10th October 2025, Thursday)  
**Phase:** Phase 2 - Map Connections  
**Task:** 2.1 - Entry Point Analysis  
**Status:** ✅ COMPLETE

---

## 🎯 PURPOSE

Map all entry points and their complete execution flow from user interaction to tool execution.

**Entry Points Analyzed:**
1. **scripts/run_ws_shim.py** - MCP Entry Point (stdio transport)
2. **src/daemon/ws_server.py** - WebSocket Daemon (WebSocket transport)
3. **src/server/handlers/request_handler.py** - Request Router (tool orchestration)
4. **server.py** - MCP Server Core (tool registry & protocol)

---

## 📊 COMPLETE EXECUTION FLOW

```
User (Augment IDE)
    ↓
MCP Protocol (stdio or WebSocket)
    ↓
┌─────────────────────────────────────────────────────────────┐
│ ENTRY POINT 1: scripts/run_ws_shim.py (MCP Entry)          │
│ - Bootstraps environment (src.bootstrap)                    │
│ - Loads .env configuration                                  │
│ - Sets up logging (ws_shim.log)                            │
│ - Creates MCP Server instance                               │
│ - Connects to WebSocket daemon (port 8765)                  │
│ - Handles MCP protocol (list_tools, call_tool)             │
└─────────────────────────────────────────────────────────────┘
    ↓ WebSocket Connection (ws://127.0.0.1:8765)
┌─────────────────────────────────────────────────────────────┐
│ ENTRY POINT 2: src/daemon/ws_server.py (WS Daemon)         │
│ - Receives WebSocket messages from shim                     │
│ - Manages sessions (SessionManager)                         │
│ - Enforces concurrency limits (global/provider semaphores)  │
│ - Routes to server.py tool registry                         │
│ - Sends progress updates (8s interval)                      │
│ - Caches results (10min TTL)                                │
└─────────────────────────────────────────────────────────────┘
    ↓ Delegates to server.py
┌─────────────────────────────────────────────────────────────┐
│ ENTRY POINT 3: server.py (MCP Server Core)                 │
│ - Initializes tool registry (TOOLS dict)                    │
│ - Configures providers (Kimi, GLM)                          │
│ - Registers all tools via ToolRegistry                      │
│ - Handles list_tools requests                               │
│ - Delegates call_tool to request_handler                    │
└─────────────────────────────────────────────────────────────┘
    ↓ Delegates to request handler
┌─────────────────────────────────────────────────────────────┐
│ ENTRY POINT 4: request_handler.py (Request Router)         │
│ - Normalizes tool names                                     │
│ - Resolves model selection (auto routing)                   │
│ - Reconstructs conversation context                         │
│ - Creates model context                                     │
│ - Validates file sizes                                      │
│ - Executes tool with monitoring                             │
│ - Handles auto-continuation                                 │
│ - Attaches progress/summary                                 │
└─────────────────────────────────────────────────────────────┘
    ↓ Executes tool
┌─────────────────────────────────────────────────────────────┐
│ TOOL EXECUTION (SimpleTool or WorkflowTool)                │
│ - Calls tool.execute() method                               │
│ - Uses mixins (WebSearchMixin, ContinuationMixin, etc.)    │
│ - Calls AI provider (Kimi or GLM)                          │
│ - Returns ToolOutput                                        │
└─────────────────────────────────────────────────────────────┘
    ↓ Returns result
Response flows back through the stack to user
```

---

## 🔍 ENTRY POINT 1: scripts/run_ws_shim.py

### File Information
- **Path:** `scripts/run_ws_shim.py`
- **Size:** 335 lines
- **Purpose:** MCP Entry Point - Bridges MCP protocol (stdio) to WebSocket daemon
- **Transport:** stdio (standard input/output)

### Key Imports
```python
# Bootstrap
from src.bootstrap import load_env, get_repo_root, setup_logging

# Configuration
from config import TimeoutConfig

# MCP Protocol
import websockets
from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
```

### Execution Flow

**1. Bootstrap Phase:**
```python
# Line 12-20: Path setup and environment loading
_repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_repo_root))
load_env()  # Loads .env file
```

**2. Logging Setup:**
```python
# Line 33: Setup logging
logger = setup_logging("ws_shim", log_file="logs/ws_shim.log")
```

**3. Configuration Loading:**
```python
# Lines 36-46: Load environment variables
EXAI_WS_HOST = os.getenv("EXAI_WS_HOST", "127.0.0.1")
EXAI_WS_PORT = int(os.getenv("EXAI_WS_PORT", "8765"))
EXAI_WS_TOKEN = os.getenv("EXAI_WS_TOKEN", "")
SESSION_ID = os.getenv("EXAI_SESSION_ID", str(uuid.uuid4()))
MAX_MSG_BYTES = int(os.getenv("EXAI_WS_MAX_BYTES", str(32 * 1024 * 1024)))
PING_INTERVAL = int(os.getenv("EXAI_WS_PING_INTERVAL", "45"))
PING_TIMEOUT = int(os.getenv("EXAI_WS_PING_TIMEOUT", "30"))
EXAI_WS_AUTOSTART = os.getenv("EXAI_WS_AUTOSTART", "true").strip().lower() == "true"
EXAI_WS_CONNECT_TIMEOUT = float(os.getenv("EXAI_WS_CONNECT_TIMEOUT", "10"))
EXAI_WS_HANDSHAKE_TIMEOUT = float(os.getenv("EXAI_WS_HANDSHAKE_TIMEOUT", "15"))
EXAI_SHIM_ACK_GRACE_SECS = float(os.getenv("EXAI_SHIM_ACK_GRACE_SECS", "120"))
```

**4. MCP Server Creation:**
```python
# Line 52: Create MCP server instance
server = Server(os.getenv("MCP_SERVER_ID", "ex-ws-shim"))
```

**5. Health Check System:**
```python
# Lines 75-129: Daemon health check before connection
def _check_daemon_health() -> tuple[bool, str]:
    # Checks logs/ws_daemon.health.json
    # Validates health file is fresh (<20s old)
    # Returns (is_healthy, status_message)
```

**6. WebSocket Connection:**
```python
# Lines 146-234: Ensure WebSocket connection
async def _ensure_ws():
    # Check daemon health first
    # Connect to ws://127.0.0.1:8765
    # Send hello handshake with session_id and token
    # Wait for ack with timeout
    # Retry with exponential backoff
    # Auto-start daemon if configured
```

**7. MCP Protocol Handlers:**
```python
# Lines 237-248: List tools handler
@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    ws = await _ensure_ws()
    await ws.send(json.dumps({"op": "list_tools"}))
    raw = await ws.recv()
    msg = json.loads(raw)
    return tools

# Lines 251-314: Call tool handler
@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    ws = await _ensure_ws()
    req_id = str(uuid.uuid4())
    await ws.send(json.dumps({
        "op": "call_tool",
        "request_id": req_id,
        "name": name,
        "arguments": arguments or {},
    }))
    # Wait for call_tool_res with timeout (default: 240s)
    # Handle call_tool_ack to extend deadline
    # Ignore progress messages
    # Return TextContent results
```

**8. Main Entry Point:**
```python
# Lines 318-334: Main function
def main() -> None:
    init_opts = server.create_initialization_options()
    async def _runner():
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, init_opts)
    asyncio.run(_runner())

if __name__ == "__main__":
    main()
```

### Key Features
- **Health Monitoring:** Checks daemon health before connection
- **Auto-Start:** Can automatically start daemon if not running
- **Retry Logic:** Exponential backoff with 10s timeout
- **Timeout Coordination:** Uses TimeoutConfig for coordinated timeouts
- **Progress Handling:** Ignores progress messages, waits for final result
- **Reconnection:** Retries once on timeout/connection errors

---

## 🔍 ENTRY POINT 2: src/daemon/ws_server.py

### File Information
- **Path:** `src/daemon/ws_server.py`
- **Size:** 1,200 lines
- **Purpose:** WebSocket Daemon - Manages WebSocket connections and tool execution
- **Transport:** WebSocket (port 8765)

### Key Imports
```python
# Bootstrap
from src.bootstrap import setup_logging, get_repo_root
from src.core.config import get_config
from src.core.message_bus_client import MessageBusClient

# Session Management
from .session_manager import SessionManager

# Tool Registry (CRITICAL: Shared with server.py)
from server import TOOLS as SERVER_TOOLS
from server import _ensure_providers_configured
from server import handle_call_tool as SERVER_HANDLE_CALL_TOOL
from server import register_provider_specific_tools

# Provider Registry
from src.providers.registry import ModelProviderRegistry
from src.providers.base import ProviderType

# Configuration
from config import TimeoutConfig
```

### Architecture Highlights

**1. Singleton Tool Registry (Mission 2):**
```python
# Lines 110-124: CRITICAL - Shared tool registry
# Import TOOLS from server.py to ensure both entry points share
# the same dict object reference
from server import TOOLS as SERVER_TOOLS
```

**2. Async-Safe Logging:**
```python
# Lines 39-42: Prevent deadlocks in async contexts
from src.utils.async_logging import setup_async_safe_logging
_log_listener = setup_async_safe_logging(level=logging.INFO)
```

**3. Concurrency Control:**
```python
# Lines 197-202: Semaphores for rate limiting
_global_sem = asyncio.BoundedSemaphore(GLOBAL_MAX_INFLIGHT)  # 24 concurrent
_provider_sems: dict[str, asyncio.BoundedSemaphore] = {
    "KIMI": asyncio.BoundedSemaphore(KIMI_MAX_INFLIGHT),  # 6 concurrent
    "GLM": asyncio.BoundedSemaphore(GLM_MAX_INFLIGHT),    # 4 concurrent
}
```

**4. Result Caching:**
```python
# Lines 216-273: Two-level caching
_results_cache: dict[str, dict] = {}  # By request_id (10min TTL)
_results_cache_by_key: dict[str, dict] = {}  # By semantic key (10min TTL)
```

**5. Observability Files:**
```python
# Lines 141-148: JSONL vs JSON intent
_metrics_path = LOG_DIR / "ws_daemon.metrics.jsonl"  # Append-only time-series
_health_path = LOG_DIR / "ws_daemon.health.json"     # Overwrite snapshot
```

### Execution Flow

**1. Daemon Startup:**
- Create PID file (logs/ws_daemon.pid)
- Check if port is already listening
- Start WebSocket server on port 8765
- Initialize session manager
- Setup health monitoring
- Register signal handlers (SIGTERM, SIGINT)

**2. Client Connection:**
- Accept WebSocket connection
- Wait for "hello" message with session_id and token
- Validate authentication token
- Send "ack" message
- Add to session manager

**3. Message Handling:**
- Receive "list_tools" → Return tool list from SERVER_TOOLS
- Receive "call_tool" → Execute tool via SERVER_HANDLE_CALL_TOOL
- Send "call_tool_ack" → Acknowledge receipt, extend timeout
- Send "progress" → Heartbeat every 8s during execution
- Send "call_tool_res" → Return final result

**4. Tool Execution:**
- Acquire global semaphore (max 24 concurrent)
- Acquire provider semaphore (Kimi: 6, GLM: 4)
- Check result cache (by request_id and semantic key)
- Call SERVER_HANDLE_CALL_TOOL (delegates to request_handler.py)
- Send progress updates every 8s
- Cache result (10min TTL)
- Release semaphores

**5. Health Monitoring:**
- Update health file every 10s
- Write metrics to JSONL file
- Track active sessions, in-flight requests
- Monitor uptime, request counts

---

## 🔍 ENTRY POINT 3: server.py

### File Information
- **Path:** `server.py`
- **Size:** 526 lines
- **Purpose:** MCP Server Core - Tool registry and protocol handling
- **Role:** Central tool registry shared by both stdio and WebSocket transports

### Key Imports
```python
# Bootstrap
from src.bootstrap import load_env, get_repo_root

# MCP Protocol
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, Prompt, ServerCapabilities

# Configuration
from config import __version__

# Tools (Auggie wrappers)
from tools import ChatTool, ConsensusTool, ThinkDeepTool

# Modular Components
from src.server.providers import configure_providers
from src.server.tools import filter_disabled_tools, filter_by_provider_capabilities
from src.server.handlers import (
    handle_call_tool,
    handle_get_prompt,
    handle_list_prompts,
    handle_list_tools,
)
```

### Tool Registry Initialization

**1. Tool Registry (TOOLS dict):**
```python
# Initialized via ToolRegistry.discover_tools()
# Shared by both stdio (run_ws_shim.py) and WebSocket (ws_server.py)
# Contains all discovered tools from tools/ directory
```

**2. Provider Configuration:**
```python
# configure_providers() called at startup
# Initializes Kimi and GLM providers
# Registers provider-specific tools
```

**3. Tool Filtering:**
```python
# filter_disabled_tools() - Remove disabled tools
# filter_by_provider_capabilities() - Filter by provider availability
```

### Handlers Delegation

**1. list_tools:**
```python
# Delegates to src.server.handlers.handle_list_tools
# Returns filtered tool list based on provider capabilities
```

**2. call_tool:**
```python
# Delegates to src.server.handlers.handle_call_tool
# Routes to request_handler.py for orchestration
```

**3. list_prompts / get_prompt:**
```python
# Delegates to src.server.handlers.handle_list_prompts
# Delegates to src.server.handlers.handle_get_prompt
```

---

## 🔍 ENTRY POINT 4: src/server/handlers/request_handler.py

### File Information
- **Path:** `src/server/handlers/request_handler.py`
- **Size:** 175 lines (refactored from 1,345 lines - 93% reduction)
- **Purpose:** Request Router - Thin orchestrator for tool execution
- **Architecture:** Delegates to 7 specialized helper modules

### Helper Modules
```python
from .request_handler_init import initialize_request
from .request_handler_routing import normalize_tool_name, handle_unknown_tool
from .request_handler_model_resolution import resolve_auto_model_legacy, validate_and_fallback_model
from .request_handler_context import reconstruct_context, integrate_session_cache, auto_select_consensus_models
from .request_handler_monitoring import execute_with_monitor
from .request_handler_execution import (
    create_model_context,
    validate_file_sizes,
    inject_optional_features,
    execute_tool_with_fallback,
    execute_tool_without_model,
    normalize_result,
)
from .request_handler_post_processing import (
    handle_files_required,
    auto_continue_workflows,
    attach_progress_and_summary,
    write_session_cache,
)
```

### Execution Flow (8 Steps)

**Step 1: Initialize Request**
```python
# initialize_request(name, arguments)
# - Generate request_id (UUID)
# - Build tool registry
# - Setup monitoring config
```

**Step 2: Normalize Tool Name**
```python
# normalize_tool_name(name, tool_map, think_routing_enabled)
# - Strip _EXAI-WS suffix
# - Handle think routing
```

**Step 3: Get Tool from Registry**
```python
# tool_map.get(name)
# - Return tool instance or None
# - Handle unknown tool error
```

**Step 4: Reconstruct Context**
```python
# reconstruct_context(name, arguments, req_id)
# - Load conversation history if continuation_id present
# - Integrate session cache
```

**Step 5: Auto-Select Models (Consensus only)**
```python
# auto_select_consensus_models(name, arguments)
# - Select models for consensus tool
```

**Step 6: Execute Tool**
```python
# If tool.requires_model():
#   - Route auto model (_route_auto_model)
#   - Resolve model (resolve_auto_model_legacy)
#   - Validate model (validate_and_fallback_model)
#   - Create model context
#   - Validate file sizes
#   - Inject optional features
#   - Execute with fallback
# Else:
#   - Execute without model context
```

**Step 7: Normalize Result**
```python
# normalize_result(result)
# - Convert to list[TextContent]
```

**Step 8: Post-Processing**
```python
# handle_files_required() - Handle file upload requirements
# auto_continue_workflows() - Auto-continue multi-step workflows
# attach_progress_and_summary() - Add progress/summary metadata
# write_session_cache() - Save session state
```

---

## 📊 DATA FLOW SUMMARY

### Request Flow (User → AI)
```
User Input (Augment IDE)
  ↓ MCP Protocol (stdio)
scripts/run_ws_shim.py
  ↓ WebSocket (ws://127.0.0.1:8765)
src/daemon/ws_server.py
  ↓ Function Call
server.py (TOOLS registry)
  ↓ Delegation
src/server/handlers/request_handler.py
  ↓ Tool Execution
tools/simple/simple_tool.py OR tools/workflow/workflow_tool.py
  ↓ Provider Call
src/providers/kimi_provider.py OR src/providers/glm_provider.py
  ↓ HTTP Request
Kimi API (api.moonshot.ai) OR GLM API (api.z.ai)
```

### Response Flow (AI → User)
```
AI Response (JSON)
  ↓ HTTP Response
Provider (Kimi or GLM)
  ↓ ToolOutput
Tool (SimpleTool or WorkflowTool)
  ↓ list[TextContent]
request_handler.py (post-processing)
  ↓ call_tool_res
ws_server.py (cache result)
  ↓ WebSocket Message
run_ws_shim.py (extract content)
  ↓ MCP Protocol (stdio)
Augment IDE (display to user)
```

---

## 🔑 KEY INSIGHTS

### 1. Dual Transport Architecture
- **stdio transport:** run_ws_shim.py → ws_server.py (for MCP clients)
- **WebSocket transport:** Direct connection to ws_server.py (for custom clients)
- **Shared registry:** Both use same TOOLS dict from server.py

### 2. Timeout Coordination
- **Workflow Tool:** 120s (default)
- **Daemon:** 180s (1.5x workflow = 120s * 1.5)
- **Shim:** 240s (2x workflow = 120s * 2)
- **Grace Period:** 120s for ack extension

### 3. Concurrency Control
- **Global:** 24 concurrent requests
- **Kimi:** 6 concurrent requests
- **GLM:** 4 concurrent requests
- **Per-Session:** 8 concurrent requests

### 4. Caching Strategy
- **Result Cache:** 10min TTL, by request_id
- **Semantic Cache:** 10min TTL, by call_key (tool name + arguments)
- **Survives Reconnects:** Semantic cache persists across reconnections

### 5. Health Monitoring
- **Health File:** logs/ws_daemon.health.json (overwrite snapshot)
- **Metrics File:** logs/ws_daemon.metrics.jsonl (append-only time-series)
- **Freshness Check:** Health file must be <20s old
- **PID File:** logs/ws_daemon.pid (exclusive lock)

---

## ✅ TASK 2.1 COMPLETE

**Deliverable:** ENTRY_POINTS_FLOW_MAP.md ✅

**Next Task:** Task 2.2 - Tool Execution Flow Tracing

**Time Taken:** ~30 minutes (as estimated)

---

**Status:** ✅ COMPLETE - All entry points mapped with complete execution flow

