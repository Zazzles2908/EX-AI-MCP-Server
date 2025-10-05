# Script Interconnections & Purpose Guide

**Purpose:** Quick reference guide for understanding what each script does and how they connect.

**Created:** 2025-10-05  
**Status:** Investigation Document

---

## 🎯 Quick Reference: Which Script to Use?

| **I want to...** | **Use this script** | **Location** |
|------------------|---------------------|--------------|
| Set up the server for the first time | `run-server.ps1` (Windows) or `run-server.sh` (Unix) | Root directory |
| Start the WebSocket daemon | `ws_start.ps1` | `scripts/` |
| Stop the WebSocket daemon | `ws_stop.ps1` | `scripts/` |
| Restart the daemon (clean restart) | `force_restart.ps1` | `scripts/` |
| Check daemon status | `python scripts/ws/ws_status.py` | `scripts/ws/` |
| Test WebSocket connection | `python scripts/ws/ws_chat_once.py` | `scripts/ws/` |
| Run server for Auggie CLI | Configured in `Daemon/mcp-config.auggie.json` | Auto-launched |
| Run server for Augment Code | Configured in `Daemon/mcp-config.augmentcode.json` | Auto-launched |
| Run server for Claude Desktop | Configured in `Daemon/mcp-config.claude.json` | Auto-launched |

---

## 📁 Script Categories

### **Setup & Installation Scripts**

#### **run-server.ps1 / run-server.sh**
- **Location:** Root directory
- **Purpose:** Complete setup and launch script
- **What it does:**
  1. Checks Python 3.10+ installation
  2. Creates/activates virtual environment (.venv)
  3. Installs dependencies from requirements.txt
  4. Validates .env file and API keys
  5. Cleans Python caches (__pycache__, .pyc)
  6. Offers integration with MCP clients
  7. Launches server.py in stdio mode
- **When to use:** First-time setup, manual server launch
- **Triggers:** `server.py` (direct stdio mode)
- **Platform:** Windows (PowerShell) or Unix (Bash)

---

### **WebSocket Daemon Management Scripts**

#### **scripts/ws_start.ps1**
- **Location:** `scripts/`
- **Purpose:** Start WebSocket daemon or shim
- **Usage:**
  - `.\scripts\ws_start.ps1` - Start WebSocket daemon
  - `.\scripts\ws_start.ps1 -Shim` - Start WebSocket shim (stdio bridge)
  - `.\scripts\ws_start.ps1 -Restart` - Stop existing daemon first, then start
- **What it does:**
  - Resolves repo root and Python path
  - Stops existing daemon if `-Restart` flag is set
  - Launches either `run_ws_daemon.py` or `run_ws_shim.py`
- **When to use:** Manual daemon management
- **Triggers:** `scripts/ws/run_ws_daemon.py` or `scripts/run_ws_shim.py`

#### **scripts/ws_stop.ps1**
- **Location:** `scripts/`
- **Purpose:** Stop WebSocket daemon
- **Usage:**
  - `.\scripts\ws_stop.ps1` - Graceful stop
  - `.\scripts\ws_stop.ps1 -Force` - Forceful stop (taskkill /F)
- **What it does:**
  1. Reads PID from `logs/ws_daemon.health.json` or `logs/ws_daemon.pid`
  2. Stops daemon process
  3. Cleans up port 8765
  4. Removes PID and health files
- **When to use:** Stop daemon, before restart, troubleshooting

#### **scripts/force_restart.ps1**
- **Location:** `scripts/`
- **Purpose:** Nuclear option - kill all Python processes and restart daemon
- **Usage:** `.\scripts\force_restart.ps1`
- **What it does:**
  1. Calls `ws_stop.ps1 -Force`
  2. Kills ALL Python processes (Get-Process python*)
  3. Waits for port 8765 to be free (10 second timeout)
  4. Cleans up PID and health files
  5. Restarts daemon via `ws_start.ps1`
- **When to use:**
  - .env changes aren't being picked up
  - Daemon is stuck or unresponsive
  - Multiple Python processes are running
  - Port 8765 is in use by unknown process
- **⚠️ WARNING:** Kills ALL Python processes, not just the daemon!

---

### **WebSocket Daemon Core Scripts**

#### **scripts/ws/run_ws_daemon.py**
- **Location:** `scripts/ws/`
- **Purpose:** WebSocket daemon launcher (minimal wrapper)
- **What it does:**
  1. Sets up Python path to repo root
  2. Loads environment via `src/bootstrap.load_env()`
  3. Imports and calls `src.daemon.ws_server.main()`
- **When to use:** Launched by `ws_start.ps1`, not called directly
- **Triggers:** `src/daemon/ws_server.py::main()`

#### **src/daemon/ws_server.py**
- **Location:** `src/daemon/`
- **Purpose:** WebSocket server implementation (the actual daemon)
- **What it does:**
  1. Listens on `ws://127.0.0.1:8765` (configurable)
  2. Manages WebSocket sessions via `SessionManager`
  3. Implements authentication with token rotation
  4. Handles tool calls by importing from `server.py`
  5. Uses `TimeoutConfig.get_daemon_timeout()` = 180s
  6. Writes health file every 10 seconds (`logs/ws_daemon.health.json`)
  7. Writes PID file (`logs/ws_daemon.pid`)
  8. Logs to `logs/ws_daemon.log`
  9. Implements graceful shutdown on SIGINT/SIGTERM
- **Imports from:** `server.py` (TOOLS, handle_call_tool), `config.TimeoutConfig`
- **When to use:** Launched by `run_ws_daemon.py`, runs as background daemon

#### **scripts/run_ws_shim.py**
- **Location:** `scripts/`
- **Purpose:** MCP stdio ↔ WebSocket daemon bridge
- **What it does:**
  1. Implements MCP Server (stdio mode)
  2. Connects to WebSocket daemon at `ws://127.0.0.1:8765`
  3. Performs health check before connecting
  4. Auto-starts daemon if `EXAI_WS_AUTOSTART=true`
  5. Translates MCP stdio protocol to WebSocket JSON-RPC
  6. Uses `TimeoutConfig.get_shim_timeout()` = 240s
  7. Extracts clean content from EXAI MCP JSON responses
  8. Logs to `logs/ws_shim.log`
- **When to use:** Launched by MCP clients (configured in Daemon/mcp-config.*.json)
- **Connects to:** `src/daemon/ws_server.py`

---

### **WebSocket Utility Scripts**

#### **scripts/ws/ws_status.py**
- **Location:** `scripts/ws/`
- **Purpose:** Check WebSocket daemon status
- **Usage:** `python scripts/ws/ws_status.py`
- **What it does:**
  1. Reads `logs/ws_daemon.health.json`
  2. Checks if health file is fresh (< 20 seconds old)
  3. Reports PID, sessions, uptime
  4. Checks if port 8765 is listening
- **When to use:** Troubleshooting, verify daemon is running

#### **scripts/ws/ws_chat_once.py**
- **Location:** `scripts/ws/`
- **Purpose:** Test WebSocket connection with single chat message
- **Usage:** `python scripts/ws/ws_chat_once.py`
- **What it does:**
  1. Connects to WebSocket daemon
  2. Sends a test chat message
  3. Prints response
  4. Disconnects
- **When to use:** Testing WebSocket connection, debugging

#### **scripts/ws/ws_chat_roundtrip.py**
- **Location:** `scripts/ws/`
- **Purpose:** Test WebSocket connection with multiple messages
- **Usage:** `python scripts/ws/ws_chat_roundtrip.py`
- **What it does:**
  1. Connects to WebSocket daemon
  2. Sends multiple test messages
  3. Prints responses
  4. Measures round-trip time
  5. Disconnects
- **When to use:** Performance testing, stress testing

#### **scripts/ws/ws_chat_analyze_files.py**
- **Location:** `scripts/ws/`
- **Purpose:** Test WebSocket connection with file analysis
- **Usage:** `python scripts/ws/ws_chat_analyze_files.py`
- **What it does:**
  1. Connects to WebSocket daemon
  2. Sends analyze tool request with file paths
  3. Prints analysis response
  4. Disconnects
- **When to use:** Testing file analysis, debugging workflow tools

---

### **MCP Client Wrapper Scripts**

#### **scripts/mcp_server_wrapper.py**
- **Location:** `scripts/`
- **Purpose:** Auggie CLI compatibility wrapper
- **What it does:**
  1. Auto-discovers project root and .venv
  2. Ensures logs directory exists
  3. Implements single-instance lock (PID file at `logs/exai_server.pid`)
  4. Re-execs with venv Python if needed
  5. Sets working directory and sys.path
  6. Imports and runs `server.py`
- **When to use:** Launched by Auggie CLI (configured in `Daemon/mcp-config.auggie.json`)
- **Triggers:** `server.py`
- **Lock file:** `logs/exai_server.pid`
- **Error log:** `logs/wrapper_error.log`

---

### **Main Server Script**

#### **server.py**
- **Location:** Root directory
- **Purpose:** Main MCP server implementation (stdio mode)
- **What it does:**
  1. Loads environment via `src/bootstrap.load_env()`
  2. Imports configuration from `config.py`
  3. Configures providers via `src/server/providers.configure_providers()`
  4. Discovers tools via `tools/registry.py`
  5. Handles MCP protocol via `src/server/handlers/`
  6. Sets up logging (server.log, metrics.jsonl, router.jsonl, toolcalls.jsonl)
  7. Exports `TOOLS` and `handle_call_tool` for WS daemon to import
  8. Runs MCP server in stdio mode
- **When to use:** Launched by MCP clients, `mcp_server_wrapper.py`, or `run-server.ps1`
- **Imports from:** `src/bootstrap`, `config`, `src/server/*`, `tools/*`, `systemprompts/*`
- **Imported by:** `src/daemon/ws_server.py` (for TOOLS and handle_call_tool)

---

## 🔗 Script Interconnection Chains

### **Chain 1: Direct MCP Server (stdio mode)**

```
MCP Client (Augment/Claude/Auggie)
    ↓
Daemon/mcp-config.*.json (defines command)
    ↓
scripts/mcp_server_wrapper.py (Auggie only)
    ↓
server.py (main MCP server)
    ↓
src/bootstrap/ (load .env, setup logging)
    ↓
config.py (load TimeoutConfig)
    ↓
src/server/handlers/ (handle MCP protocol)
    ↓
tools/registry.py (discover tools)
    ↓
tools/workflows/*.py (execute tool)
    ↓
src/providers/ (call GLM/Kimi API)
    ↓
Return response to MCP Client
```

### **Chain 2: WebSocket Daemon Mode**

```
User runs: .\scripts\ws_start.ps1
    ↓
scripts/ws/run_ws_daemon.py
    ↓
src/daemon/ws_server.py (WebSocket daemon starts)
    ↓
Listens on ws://127.0.0.1:8765
    ↓
Writes logs/ws_daemon.health.json (every 10s)
    ↓
Writes logs/ws_daemon.pid
    ↓
Waits for WebSocket connections...

---

MCP Client (Augment/Claude/Auggie)
    ↓
Daemon/mcp-config.*.json (defines command)
    ↓
scripts/run_ws_shim.py (stdio ↔ WebSocket bridge)
    ↓
Checks logs/ws_daemon.health.json (health check)
    ↓
Connects to ws://127.0.0.1:8765
    ↓
Sends tool call request (JSON-RPC)
    ↓
src/daemon/ws_server.py receives request
    ↓
Imports from server.py (TOOLS, handle_call_tool)
    ↓
Calls handle_call_tool()
    ↓
src/server/handlers/ (handle tool call)
    ↓
tools/workflows/*.py (execute tool)
    ↓
src/providers/ (call GLM/Kimi API)
    ↓
Return response via WebSocket
    ↓
scripts/run_ws_shim.py forwards to MCP Client
    ↓
MCP Client receives response
```

### **Chain 3: Force Restart**

```
User runs: .\scripts\force_restart.ps1
    ↓
Calls: .\scripts\ws_stop.ps1 -Force
    ↓
Reads logs/ws_daemon.health.json (get PID)
    ↓
Stops daemon process (taskkill /F)
    ↓
Kills ALL Python processes (Get-Process python*)
    ↓
Waits for port 8765 to be free (10s timeout)
    ↓
Cleans up logs/ws_daemon.pid
    ↓
Cleans up logs/ws_daemon.health.json
    ↓
Calls: .\scripts\ws_start.ps1
    ↓
Launches: scripts/ws/run_ws_daemon.py
    ↓
src/daemon/ws_server.py (daemon restarts)
```

---

## 📊 File Relationships

### **Configuration Files**

```
.env / .env.example
    ↓ (loaded by)
src/bootstrap/env_loader.py
    ↓ (imported by)
All entry points (server.py, run_ws_shim.py, run_ws_daemon.py)
    ↓ (used by)
config.py (TimeoutConfig, model config, feature flags)
    ↓ (imported by)
All components (server, daemon, shim, tools)
```

### **MCP Client Configuration**

```
Daemon/mcp-config.auggie.json
    ↓ (defines command)
scripts/mcp_server_wrapper.py
    ↓ (launches)
server.py

---

Daemon/mcp-config.augmentcode.json
    ↓ (defines command)
scripts/run_ws_shim.py
    ↓ (connects to)
src/daemon/ws_server.py

---

Daemon/mcp-config.claude.json
    ↓ (defines command)
scripts/run_ws_shim.py
    ↓ (connects to)
src/daemon/ws_server.py
```

### **Logging Files**

```
server.py
    ↓ (writes to)
logs/server.log
logs/metrics.jsonl
logs/router.jsonl
logs/toolcalls.jsonl

---

src/daemon/ws_server.py
    ↓ (writes to)
logs/ws_daemon.log
logs/ws_daemon.health.json (every 10s)
logs/ws_daemon.pid

---

scripts/run_ws_shim.py
    ↓ (writes to)
logs/ws_shim.log

---

scripts/mcp_server_wrapper.py
    ↓ (writes to)
logs/exai_server.pid
logs/wrapper_error.log
```

---

## 🎯 Common Scenarios

### **Scenario 1: First-time setup**

1. Run `.\run-server.ps1` (Windows) or `./run-server.sh` (Unix)
2. Script creates .venv, installs dependencies, validates .env
3. Script offers to configure MCP clients
4. Script launches `server.py` in stdio mode

### **Scenario 2: Start WebSocket daemon**

1. Run `.\scripts\ws_start.ps1`
2. Script launches `scripts/ws/run_ws_daemon.py`
3. Daemon starts at `ws://127.0.0.1:8765`
4. Daemon writes `logs/ws_daemon.health.json` and `logs/ws_daemon.pid`
5. MCP clients connect via `scripts/run_ws_shim.py`

### **Scenario 3: Daemon is stuck**

1. Run `.\scripts\force_restart.ps1`
2. Script kills all Python processes
3. Script waits for port 8765 to be free
4. Script restarts daemon via `ws_start.ps1`

### **Scenario 4: Check daemon status**

1. Run `python scripts/ws/ws_status.py`
2. Script reads `logs/ws_daemon.health.json`
3. Script reports PID, sessions, uptime
4. Script checks if port 8765 is listening

### **Scenario 5: Test WebSocket connection**

1. Ensure daemon is running (`ws_status.py`)
2. Run `python scripts/ws/ws_chat_once.py`
3. Script sends test message to daemon
4. Script prints response

---

## 🚨 Important Notes

### **1. Two Execution Modes**
- **stdio mode:** Direct MCP server (one process per client)
- **WebSocket mode:** Persistent daemon (one daemon, multiple clients)

### **2. Script Locations**
- **Root:** Setup scripts (`run-server.ps1`, `run-server.sh`)
- **scripts/:** Daemon management (`ws_start.ps1`, `ws_stop.ps1`, `force_restart.ps1`)
- **scripts/ws/:** Daemon core and utilities (`run_ws_daemon.py`, `ws_status.py`, `ws_chat_*.py`)

### **3. PID Files**
- **stdio mode:** `logs/exai_server.pid` (created by `mcp_server_wrapper.py`)
- **WebSocket mode:** `logs/ws_daemon.pid` (created by `ws_server.py`)

### **4. Health Files**
- **WebSocket mode only:** `logs/ws_daemon.health.json` (updated every 10 seconds)
- Contains: PID, sessions, uptime, timestamp

### **5. Timeout Hierarchy (Day 1 Fix)**
- **Tool:** 120s (`tools/workflow/base.py`)
- **Daemon:** 180s (`src/daemon/ws_server.py`)
- **Shim:** 240s (`scripts/run_ws_shim.py`)
- **Client:** 300s (MCP client timeout)
- **Coordinated via:** `config.TimeoutConfig`

---

**End of Script Interconnections Guide**

