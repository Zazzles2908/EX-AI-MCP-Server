# EX-AI MCP Server Architecture Map

**Purpose:** This document maps out the server architecture, script interconnections, and execution flow to understand how all components work together.

**Created:** 2025-10-05  
**Status:** Investigation Document (Not for implementation)

---

## 🎯 Executive Summary

The EX-AI MCP Server has a **dual-architecture** design:

1. **Direct MCP Server** (stdio mode) - For direct MCP client connections
2. **WebSocket Daemon + Shim** (WS mode) - For persistent daemon with multiple client connections

Both architectures share the same core components but differ in their transport layer.

---

## 📁 Directory Structure Overview

```
c:\Project\EX-AI-MCP-Server/
├── server.py                    # Main MCP server (stdio mode)
├── config.py                    # Central configuration + TimeoutConfig
├── run-server.ps1/.sh           # Setup & launch scripts (Windows/Unix)
├── .env / .env.example          # Environment configuration
│
├── Daemon/                      # MCP client configuration files
│   ├── mcp-config.auggie.json
│   ├── mcp-config.augmentcode.json
│   └── mcp-config.claude.json
│
├── scripts/                     # Utility scripts
│   ├── mcp_server_wrapper.py   # Auggie compatibility wrapper
│   ├── run_ws_shim.py           # WebSocket shim (MCP stdio ↔ WS daemon)
│   ├── ws_start.ps1             # Start WS daemon or shim
│   ├── ws_stop.ps1              # Stop WS daemon
│   ├── force_restart.ps1        # Force restart (kill all Python + restart)
│   └── ws/                      # WebSocket utilities
│       ├── run_ws_daemon.py     # WS daemon launcher
│       ├── ws_status.py         # Check daemon status
│       └── ws_chat_*.py         # WS client test scripts
│
├── src/                         # Core source code
│   ├── bootstrap/               # Initialization utilities
│   │   ├── __init__.py
│   │   ├── env_loader.py        # Load .env files
│   │   └── logging_setup.py     # Configure logging
│   │
│   ├── daemon/                  # WebSocket daemon
│   │   ├── ws_server.py         # WebSocket server implementation
│   │   └── session_manager.py  # Session management
│   │
│   ├── server/                  # MCP server core modules
│   │   ├── __init__.py
│   │   ├── handlers/            # MCP protocol handlers
│   │   ├── providers/           # Provider configuration
│   │   ├── tools/               # Tool filtering
│   │   └── utils/               # Utilities
│   │
│   ├── providers/               # AI provider implementations
│   │   ├── base.py
│   │   ├── glm.py               # GLM (ZhipuAI) provider
│   │   ├── kimi.py              # Kimi (Moonshot) provider
│   │   └── registry.py          # Provider registry
│   │
│   └── router/                  # Intelligent routing
│       ├── service.py
│       └── unified_router.py
│
├── tools/                       # MCP tools
│   ├── registry.py              # Tool registry
│   ├── chat.py                  # Chat tool
│   ├── shared/                  # Shared base classes
│   ├── simple/                  # Simple tools
│   ├── workflow/                # Workflow tool base classes
│   └── workflows/               # Workflow tool implementations
│       ├── thinkdeep.py
│       ├── analyze.py
│       ├── debug.py
│       └── ...
│
└── systemprompts/               # System prompts for tools
    ├── base_prompt.py
    ├── chat_prompt.py
    ├── thinkdeep_prompt.py
    └── ...
```

---

## 🔄 Execution Flow

### **Architecture 1: Direct MCP Server (stdio mode)**

```
MCP Client (Augment/Claude/Auggie)
    ↓
Daemon/mcp-config.*.json
    ↓
scripts/mcp_server_wrapper.py (optional, for Auggie)
    ↓
server.py (main MCP server)
    ↓
src/bootstrap/ (load .env, setup logging)
    ↓
config.py (load configuration + TimeoutConfig)
    ↓
src/server/handlers/ (handle MCP protocol)
    ↓
tools/registry.py (discover tools)
    ↓
tools/workflows/*.py (execute tool)
    ↓
src/providers/ (call GLM/Kimi API)
    ↓
systemprompts/*.py (get system prompts)
    ↓
Return response to MCP Client
```

### **Architecture 2: WebSocket Daemon + Shim (WS mode)**

```
MCP Client (Augment/Claude/Auggie)
    ↓
Daemon/mcp-config.*.json
    ↓
scripts/run_ws_shim.py (stdio ↔ WebSocket bridge)
    ↓
src/bootstrap/ (load .env, setup logging)
    ↓
config.py (load TimeoutConfig)
    ↓
WebSocket connection to daemon
    ↓
src/daemon/ws_server.py (WebSocket daemon)
    ↓
server.py (import TOOLS and handle_call_tool)
    ↓
src/server/handlers/ (handle tool calls)
    ↓
tools/registry.py (discover tools)
    ↓
tools/workflows/*.py (execute tool)
    ↓
src/providers/ (call GLM/Kimi API)
    ↓
systemprompts/*.py (get system prompts)
    ↓
Return response via WebSocket
    ↓
scripts/run_ws_shim.py (forward to MCP Client)
    ↓
MCP Client receives response
```

---

## 🚀 Entry Points & Launch Scripts

### **1. run-server.ps1 / run-server.sh**
- **Purpose:** Setup and launch script for the MCP server
- **What it does:**
  - Checks Python 3.10+ installation
  - Creates/activates virtual environment (.venv)
  - Installs dependencies from requirements.txt
  - Validates .env file and API keys
  - Cleans Python caches
  - Offers integration with MCP clients (Claude Desktop, Auggie, VSCode, etc.)
  - Launches server.py in stdio mode
- **Used by:** Manual setup, first-time installation
- **Triggers:** `server.py` (direct stdio mode)

### **2. scripts/mcp_server_wrapper.py**
- **Purpose:** Auggie compatibility wrapper
- **What it does:**
  - Auto-discovers project root and .venv
  - Ensures logs directory exists
  - Implements single-instance lock (PID file) to prevent duplicate servers
  - Re-execs with venv Python if needed
  - Sets working directory and sys.path
  - Imports and runs server.py
- **Used by:** Auggie CLI (configured in Daemon/mcp-config.auggie.json)
- **Triggers:** `server.py`

### **3. scripts/ws_start.ps1**
- **Purpose:** Start WebSocket daemon or shim
- **What it does:**
  - `-Shim` flag: Starts `scripts/run_ws_shim.py` (stdio bridge)
  - No flag: Starts `scripts/ws/run_ws_daemon.py` (WebSocket daemon)
  - `-Restart` flag: Stops existing daemon first
- **Used by:** Manual WS daemon management
- **Triggers:** Either `run_ws_shim.py` or `run_ws_daemon.py`

### **4. scripts/ws_stop.ps1**
- **Purpose:** Stop WebSocket daemon
- **What it does:**
  - Reads PID from `logs/ws_daemon.health.json` or `logs/ws_daemon.pid`
  - Stops daemon process gracefully
  - `-Force` flag: Uses taskkill /F for forceful termination
  - Cleans up port 8765
- **Used by:** Manual WS daemon management, force_restart.ps1

### **5. scripts/force_restart.ps1**
- **Purpose:** Nuclear option - kill all Python processes and restart daemon
- **What it does:**
  - Calls `ws_stop.ps1 -Force`
  - Kills ALL Python processes (Get-Process python*)
  - Waits for port 8765 to be free
  - Cleans up PID and health files
  - Restarts daemon via `ws_start.ps1`
- **Used by:** When .env changes aren't picked up, daemon is stuck
- **Triggers:** `ws_stop.ps1` → `ws_start.ps1` → `run_ws_daemon.py`

---

## 🔌 WebSocket Architecture Components

### **scripts/run_ws_shim.py**
- **Purpose:** MCP stdio ↔ WebSocket daemon bridge
- **What it does:**
  - Implements MCP Server (stdio mode) that forwards to WS daemon
  - Connects to WebSocket daemon at `ws://127.0.0.1:8765`
  - Performs health check before connecting (`logs/ws_daemon.health.json`)
  - Auto-starts daemon if `EXAI_WS_AUTOSTART=true`
  - Translates MCP stdio protocol to WebSocket JSON-RPC
  - Handles timeout with `TimeoutConfig.get_shim_timeout()` = 240s
  - Extracts clean content from EXAI MCP JSON responses
- **Used by:** MCP clients (configured in Daemon/mcp-config.*.json)
- **Imports from:** `src/bootstrap`, `config.TimeoutConfig`
- **Connects to:** `src/daemon/ws_server.py`

### **scripts/ws/run_ws_daemon.py**
- **Purpose:** WebSocket daemon launcher
- **What it does:**
  - Minimal launcher script
  - Loads environment via `src/bootstrap.load_env()`
  - Imports and calls `src.daemon.ws_server.main()`
- **Triggers:** `src/daemon/ws_server.py`

### **src/daemon/ws_server.py**
- **Purpose:** WebSocket server implementation
- **What it does:**
  - Listens on `ws://127.0.0.1:8765` (configurable via EXAI_WS_HOST/PORT)
  - Manages WebSocket sessions via `SessionManager`
  - Implements authentication with token rotation
  - Handles tool calls by importing from `server.py`:
    - `from server import TOOLS, handle_call_tool, _ensure_providers_configured`
  - Uses `TimeoutConfig.get_daemon_timeout()` = 180s for tool call timeout
  - Writes health file (`logs/ws_daemon.health.json`) every 10 seconds
  - Writes PID file (`logs/ws_daemon.pid`)
  - Logs to `logs/ws_daemon.log`
  - Implements graceful shutdown on SIGINT/SIGTERM
- **Imports from:** `server.py`, `src/bootstrap`, `config.TimeoutConfig`
- **Used by:** `run_ws_shim.py`, WS client test scripts

### **src/daemon/session_manager.py**
- **Purpose:** Manage WebSocket sessions
- **What it does:**
  - Tracks active sessions by session_id
  - Implements session limits (per-session, global, per-provider)
  - Handles session cleanup
- **Used by:** `src/daemon/ws_server.py`

---

## 📦 Core Components

### **server.py**
- **Purpose:** Main MCP server implementation
- **What it does:**
  - Implements MCP protocol (stdio mode)
  - Loads environment via `src/bootstrap.load_env()`
  - Imports configuration from `config.py`
  - Configures providers via `src/server/providers.configure_providers()`
  - Discovers tools via `tools/registry.py`
  - Handles MCP protocol via `src/server/handlers/`:
    - `handle_list_tools()` - List available tools
    - `handle_call_tool()` - Execute tool
    - `handle_list_prompts()` - List system prompts
    - `handle_get_prompt()` - Get system prompt
  - Sets up logging (server.log, metrics.jsonl, router.jsonl, toolcalls.jsonl)
  - Exports `TOOLS` and `handle_call_tool` for WS daemon to import
- **Imports from:** `src/bootstrap`, `config`, `src/server/*`, `tools/*`, `systemprompts/*`
- **Used by:** Direct MCP clients, `src/daemon/ws_server.py`

### **config.py**
- **Purpose:** Central configuration and constants
- **What it does:**
  - Defines version info (`__version__`, `__author__`, etc.)
  - Defines model configuration (DEFAULT_MODEL, token limits, etc.)
  - Defines feature flags (ROUTER_ENABLED, GLM_ENABLE_WEB_BROWSING, etc.)
  - **NEW:** Defines `TimeoutConfig` class with coordinated timeout hierarchy
    - Tool timeouts: SIMPLE_TOOL_TIMEOUT_SECS=60, WORKFLOW_TOOL_TIMEOUT_SECS=120, EXPERT_ANALYSIS_TIMEOUT_SECS=90
    - Infrastructure timeouts: get_daemon_timeout()=180, get_shim_timeout()=240, get_client_timeout()=300
    - Validates hierarchy on module import
- **Used by:** `server.py`, `src/daemon/ws_server.py`, `scripts/run_ws_shim.py`, `tools/workflow/base.py`, `tools/workflow/expert_analysis.py`

### **src/bootstrap/**
- **Purpose:** Common initialization utilities
- **Components:**
  - `env_loader.py` - Load .env files, get repo root
  - `logging_setup.py` - Configure logging with UTF-8 support
  - `__init__.py` - Exports `load_env()`, `get_repo_root()`, `setup_logging()`
- **Used by:** All entry points (`server.py`, `run_ws_shim.py`, `run_ws_daemon.py`, etc.)

---

## 🛠️ Tool System

### **tools/registry.py**
- **Purpose:** Tool discovery and registration
- **What it does:**
  - Discovers all tool classes from `tools/` directory
  - Filters tools by visibility (core, advanced, experimental)
  - Filters tools by provider capabilities
  - Filters disabled tools (DISABLED_TOOLS env var)
  - Returns list of Tool objects for MCP protocol
- **Used by:** `server.py`, `src/server/handlers/`

### **tools/shared/**
- **Purpose:** Base classes for all tools
- **Components:**
  - `base_tool.py` - BaseTool class (conversation handling, file processing)
  - `base_models.py` - Pydantic models (WorkflowRequest, ConsolidatedFindings, etc.)
  - `schema_builders.py` - Schema generation for MCP protocol
- **Used by:** All tool implementations

### **tools/workflow/**
- **Purpose:** Base classes for workflow (multi-step) tools
- **Components:**
  - `base.py` - WorkflowTool class (inherits BaseTool + BaseWorkflowMixin)
    - **Uses `TimeoutConfig.WORKFLOW_TOOL_TIMEOUT_SECS` = 120s**
    - Implements `execute()` with timeout and error handling
  - `workflow_mixin.py` - BaseWorkflowMixin (workflow orchestration)
  - `expert_analysis.py` - ExpertAnalysisMixin (external model integration)
    - **Uses `TimeoutConfig.EXPERT_ANALYSIS_TIMEOUT_SECS` = 90s**
  - `schema_builders.py` - WorkflowSchemaBuilder (schema generation)
- **Used by:** `tools/workflows/*.py`

### **tools/workflows/**
- **Purpose:** Workflow tool implementations
- **Tools:**
  - `thinkdeep.py` - Deep reasoning tool
  - `analyze.py` - Code analysis tool
  - `debug.py` - Debugging tool
  - `codereview.py` - Code review tool
  - `testgen.py` - Test generation tool
  - `refactor.py` - Refactoring tool
  - `secaudit.py` - Security audit tool
  - `precommit.py` - Pre-commit checks tool
  - `tracer.py` - Execution tracing tool
  - `docgen.py` - Documentation generation tool
  - `planner.py` - Planning tool
  - `consensus.py` - Consensus tool
- **All inherit from:** `tools/workflow/base.WorkflowTool`

### **systemprompts/**
- **Purpose:** System prompts for tools
- **What it does:**
  - Defines system prompts for each tool
  - Provides context and instructions for AI models
  - Used by tools to generate prompts for provider calls
- **Used by:** `tools/workflows/*.py`, `src/server/handlers/`

---

## 🌐 Provider System

### **src/providers/**
- **Purpose:** AI provider implementations
- **Components:**
  - `base.py` - BaseProvider class
  - `glm.py` - GLM (ZhipuAI) provider
  - `kimi.py` - Kimi (Moonshot) provider
  - `registry.py` - ModelProviderRegistry (provider selection)
  - `capabilities.py` - Provider capabilities (web search, file upload, etc.)
- **Used by:** `server.py`, `src/server/handlers/`, `tools/`

### **src/router/**
- **Purpose:** Intelligent routing between providers
- **Components:**
  - `service.py` - RouterService (GLM-4.5-flash as AI manager)
  - `unified_router.py` - UnifiedRouter (routing logic)
  - `classifier.py` - Task classification
  - `synthesis.py` - Response synthesis
- **Used by:** `src/server/handlers/`

---

## 📝 Configuration Files

### **Daemon/mcp-config.*.json**
- **Purpose:** MCP client configuration files
- **Files:**
  - `mcp-config.auggie.json` - Auggie CLI configuration
  - `mcp-config.augmentcode.json` - Augment Code (VSCode) configuration
  - `mcp-config.claude.json` - Claude Desktop configuration
- **What they define:**
  - Server command: `python.exe scripts/run_ws_shim.py` (or `mcp_server_wrapper.py` for Auggie)
  - Environment variables: EXAI_WS_HOST, EXAI_WS_PORT, timeout configs, etc.
  - **NEW:** Timeout environment variables (SIMPLE_TOOL_TIMEOUT_SECS, WORKFLOW_TOOL_TIMEOUT_SECS, etc.)
- **Used by:** MCP clients to launch the server

### **.env / .env.example**
- **Purpose:** Environment configuration
- **What they define:**
  - API keys (KIMI_API_KEY, GLM_API_KEY)
  - Model configuration (DEFAULT_MODEL, KIMI_DEFAULT_MODEL, etc.)
  - Feature flags (ROUTER_ENABLED, GLM_ENABLE_WEB_BROWSING, etc.)
  - **NEW:** Timeout configuration section (coordinated hierarchy)
  - WebSocket configuration (EXAI_WS_HOST, EXAI_WS_PORT)
  - Logging configuration (LOG_LEVEL)
- **Loaded by:** `src/bootstrap/env_loader.py`

---

## 🔗 Key Interconnections

### **TimeoutConfig Flow (NEW - Day 1 Implementation)**

```
.env / .env.example
    ↓ (defines WORKFLOW_TOOL_TIMEOUT_SECS=120, etc.)
config.py::TimeoutConfig
    ↓ (calculates daemon=180, shim=240, client=300)
    ├─→ src/daemon/ws_server.py (CALL_TIMEOUT = 180s)
    ├─→ scripts/run_ws_shim.py (timeout_s = 240s)
    ├─→ tools/workflow/base.py (timeout_secs = 120s)
    └─→ tools/workflow/expert_analysis.py (timeout = 90s)
```

### **Server Import Chain**

```
server.py
    ├─→ src/bootstrap (load_env, setup_logging)
    ├─→ config (TimeoutConfig, DEFAULT_MODEL, etc.)
    ├─→ src/server/providers (configure_providers)
    ├─→ src/server/handlers (handle_call_tool, etc.)
    ├─→ tools/registry (discover tools)
    └─→ systemprompts/* (get system prompts)
```

### **WebSocket Daemon Import Chain**

```
src/daemon/ws_server.py
    ├─→ src/bootstrap (setup_logging, get_repo_root)
    ├─→ config (TimeoutConfig)
    ├─→ server (TOOLS, handle_call_tool, _ensure_providers_configured)
    └─→ .session_manager (SessionManager)
```

### **Tool Execution Flow**

```
MCP Client calls tool
    ↓
server.py::handle_call_tool()
    ↓
src/server/handlers/request_handler.py
    ↓
tools/workflows/thinkdeep.py::execute()
    ↓
tools/workflow/base.py::execute() (with 120s timeout)
    ↓
tools/workflow/base.py::execute_workflow()
    ↓
tools/workflow/expert_analysis.py::call_expert_analysis() (with 90s timeout)
    ↓
src/providers/kimi.py::generate_content()
    ↓
Kimi API (https://api.moonshot.ai/v1)
    ↓
Return response
```

---

## 🎭 Dual Architecture Comparison

| Aspect | Direct MCP Server (stdio) | WebSocket Daemon + Shim |
|--------|---------------------------|-------------------------|
| **Entry Point** | `server.py` | `scripts/run_ws_shim.py` → `src/daemon/ws_server.py` |
| **Transport** | stdio (stdin/stdout) | WebSocket (ws://127.0.0.1:8765) |
| **Process Model** | One process per client | One daemon, multiple clients |
| **Timeout** | Tool timeout (120s) | Tool (120s) → Daemon (180s) → Shim (240s) |
| **Health Check** | N/A | `logs/ws_daemon.health.json` |
| **PID File** | `logs/exai_server.pid` (wrapper) | `logs/ws_daemon.pid` |
| **Logging** | `logs/server.log` | `logs/ws_daemon.log` + `logs/server.log` |
| **Use Case** | Single client, simple setup | Multiple clients, persistent daemon |
| **Restart** | Kill process | `ws_stop.ps1` + `ws_start.ps1` |

---

## 🚨 Critical Observations

### **1. Chaotic Script Organization**
- **Problem:** Scripts are scattered across multiple locations:
  - Root: `run-server.ps1`, `run-server.sh`
  - `scripts/`: `mcp_server_wrapper.py`, `run_ws_shim.py`, `ws_start.ps1`, `ws_stop.ps1`, `force_restart.ps1`
  - `scripts/ws/`: `run_ws_daemon.py`, `ws_status.py`, `ws_chat_*.py`
- **Impact:** Hard to understand which script to use for what purpose
- **Recommendation:** Consider consolidating into clearer categories (setup/, daemon/, client/)

### **2. Dual Architecture Complexity**
- **Problem:** Two completely different execution paths (stdio vs WebSocket)
- **Impact:** Harder to debug, maintain, and understand
- **Benefit:** Flexibility for different use cases
- **Recommendation:** Document clearly when to use which architecture

### **3. Import Cycles**
- **Problem:** `src/daemon/ws_server.py` imports from `server.py`, which imports from `src/server/*`
- **Impact:** Potential for circular dependencies
- **Current Status:** Works because imports are at module level, not circular
- **Recommendation:** Monitor for future issues

### **4. TimeoutConfig Integration (Day 1 Fix)**
- **Status:** ✅ Successfully integrated across all layers
- **Files Modified:** 9 files (config.py, ws_server.py, run_ws_shim.py, base.py, expert_analysis.py, 3x mcp-config.json, .env, .env.example)
- **Impact:** Coordinated timeout hierarchy now prevents timeout inversion
- **Validation:** 25 tests passing

### **5. systemprompts/ Usage**
- **Purpose:** System prompts for tools
- **Used by:** Tools import their corresponding prompt module
- **Example:** `tools/workflows/thinkdeep.py` imports `systemprompts/thinkdeep_prompt.py`
- **Impact:** Centralized prompt management, easy to update

---

## 📊 Dependency Graph

```
MCP Client
    ↓
Daemon/mcp-config.*.json
    ↓
┌─────────────────────────────────────────────────────────┐
│ Entry Point Layer                                       │
├─────────────────────────────────────────────────────────┤
│ • run-server.ps1/.sh (setup + launch)                   │
│ • scripts/mcp_server_wrapper.py (Auggie wrapper)        │
│ • scripts/run_ws_shim.py (WS shim)                      │
│ • scripts/ws/run_ws_daemon.py (WS daemon launcher)      │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│ Bootstrap Layer                                          │
├─────────────────────────────────────────────────────────┤
│ • src/bootstrap/env_loader.py (load .env)               │
│ • src/bootstrap/logging_setup.py (setup logging)        │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│ Configuration Layer                                      │
├─────────────────────────────────────────────────────────┤
│ • config.py (TimeoutConfig, model config, feature flags)│
│ • .env / .env.example (environment variables)           │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│ Server Layer                                             │
├─────────────────────────────────────────────────────────┤
│ • server.py (MCP server, stdio mode)                    │
│ • src/daemon/ws_server.py (WebSocket daemon)            │
│ • src/server/handlers/* (MCP protocol handlers)         │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│ Tool Layer                                               │
├─────────────────────────────────────────────────────────┤
│ • tools/registry.py (tool discovery)                    │
│ • tools/shared/* (base classes)                         │
│ • tools/workflow/* (workflow base classes)              │
│ • tools/workflows/* (workflow implementations)          │
│ • tools/simple/* (simple tools)                         │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│ Provider Layer                                           │
├─────────────────────────────────────────────────────────┤
│ • src/providers/glm.py (GLM provider)                   │
│ • src/providers/kimi.py (Kimi provider)                 │
│ • src/providers/registry.py (provider selection)        │
│ • src/router/* (intelligent routing)                    │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│ Prompt Layer                                             │
├─────────────────────────────────────────────────────────┤
│ • systemprompts/* (system prompts for tools)            │
└─────────────────────────────────────────────────────────┘
    ↓
External APIs (GLM, Kimi)
```

---

## 🎯 Summary

The EX-AI MCP Server has a **layered architecture** with two execution modes:

1. **Direct stdio mode:** Simple, one process per client
2. **WebSocket daemon mode:** Persistent daemon, multiple clients

**Key Components:**
- **Bootstrap:** Environment loading, logging setup
- **Configuration:** TimeoutConfig, model config, feature flags
- **Server:** MCP protocol implementation (stdio or WebSocket)
- **Tools:** Tool discovery, base classes, implementations
- **Providers:** GLM/Kimi API integration, intelligent routing
- **Prompts:** System prompts for tools

**Critical Files:**
- `server.py` - Main MCP server
- `config.py` - Central configuration + TimeoutConfig
- `src/daemon/ws_server.py` - WebSocket daemon
- `scripts/run_ws_shim.py` - WebSocket shim
- `tools/registry.py` - Tool discovery
- `src/bootstrap/` - Initialization utilities

**Timeout Hierarchy (Day 1 Fix):**
- Tool: 120s → Daemon: 180s → Shim: 240s → Client: 300s
- Coordinated via `config.TimeoutConfig` class
- Prevents timeout inversion (outer timeouts no longer prevent inner timeouts)

---

**End of Architecture Map**

