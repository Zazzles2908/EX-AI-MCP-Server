# Architecture: End-to-End Flow - Complete System Overview

**Date:** 2025-10-04 23:15  
**Status:** 📚 COMPREHENSIVE ARCHITECTURE DOCUMENTATION  
**Purpose:** Understand how all components connect

---

## 🎯 ANSWER TO YOUR QUESTION

**Q: Does `force_restart.ps1` connect to running `ws_server.py` in the end?**

**A: YES! Here's the complete flow:**

```
force_restart.ps1
    ↓
ws_stop.ps1 (stops existing daemon)
    ↓
Kill all Python processes
    ↓
ws_start.ps1
    ↓
run_ws_daemon.py
    ↓
src/daemon/ws_server.py (STARTS WEBSOCKET SERVER on port 8765)
```

**Then separately, Auggie CLI runs:**
```
Auggie CLI (when started)
    ↓
Reads mcp-config.auggie.json
    ↓
Launches run_ws_shim.py (MCP server process)
    ↓
run_ws_shim.py CONNECTS TO ws_server.py via WebSocket (port 8765)
```

---

## 🏗️ COMPLETE ARCHITECTURE

### Component 1: WebSocket Daemon (Server Side)

**Purpose:** Long-running server that executes EXAI tools

**Startup Flow:**
```
1. force_restart.ps1 (or ws_start.ps1)
   ↓
2. scripts/ws/run_ws_daemon.py
   ↓
3. src/daemon/ws_server.py
   ↓
4. Starts WebSocket server on 127.0.0.1:8765
   ↓
5. Loads tools from server.py (SERVER_TOOLS)
   ↓
6. Creates SessionManager for managing connections
   ↓
7. Writes health file: logs/ws_daemon.health.json
   ↓
8. Writes PID file: logs/ws_daemon.pid
   ↓
9. Listens for WebSocket connections
```

**Key Files:**
- `scripts/ws/run_ws_daemon.py` - Entry point (21 lines)
- `src/daemon/ws_server.py` - Main server (951 lines)
- `src/daemon/session_manager.py` - Session management
- `server.py` - Tool definitions (imported by ws_server.py)

**What It Does:**
- Listens on port 8765 for WebSocket connections
- Accepts "hello" handshake from clients
- Executes tool calls (debug_exai, thinkdeep_exai, etc.)
- Manages sessions and rate limiting
- Writes metrics to logs/ws_daemon.metrics.jsonl
- Updates health file every few seconds

---

### Component 2: MCP Shim (Client Side)

**Purpose:** Bridges Auggie CLI (MCP client) to WebSocket daemon (EXAI server)

**Startup Flow:**
```
1. Auggie CLI starts
   ↓
2. Reads mcp-config.auggie.json
   ↓
3. Launches: python scripts/run_ws_shim.py
   ↓
4. run_ws_shim.py creates MCP Server instance
   ↓
5. Connects to WebSocket daemon at ws://127.0.0.1:8765
   ↓
6. Sends "hello" handshake with session_id
   ↓
7. Registers MCP tools (proxies to WebSocket daemon)
   ↓
8. Waits for tool calls from Auggie CLI
```

**Key Files:**
- `scripts/run_ws_shim.py` - MCP server that connects to WebSocket daemon (331 lines)
- `mcp-config.auggie.json` - Auggie CLI configuration

**What It Does:**
- Acts as MCP server for Auggie CLI
- Translates MCP tool calls to WebSocket messages
- Forwards requests to WebSocket daemon
- Returns responses back to Auggie CLI
- Handles connection failures and retries

---

### Component 3: Management Scripts

**Purpose:** Start, stop, restart, and monitor the system

#### force_restart.ps1
```powershell
# Complete restart sequence
1. ws_stop.ps1 (graceful stop)
2. Kill all Python processes (force)
3. Wait for port 8765 to be free
4. Clean up PID and health files
5. ws_start.ps1 (start daemon)
```

#### ws_start.ps1
```powershell
# Start daemon or shim
-Shim flag: Starts run_ws_shim.py (for testing)
No flag: Starts run_ws_daemon.py (normal mode)
-Restart flag: Stops existing daemon first
```

#### ws_stop.ps1
```powershell
# Graceful stop
1. Read PID from logs/ws_daemon.pid
2. Send SIGTERM to process
3. Wait for process to exit
4. Verify port 8765 is free
```

#### ws_status.py
```python
# Check daemon status
1. Check if PID file exists
2. Check if process is running
3. Check if port 8765 is listening
4. Check if health file is fresh
5. Report status
```

---

### Component 4: Utility Scripts

**Purpose:** Testing and debugging tools

#### ws_chat_once.py
- Single chat request to WebSocket daemon
- Used for testing chat functionality
- Bypasses MCP layer

#### ws_chat_analyze_files.py
- Analyze files using WebSocket daemon
- Used for testing file analysis
- Bypasses MCP layer

#### ws_chat_review_once.py
- Single code review request
- Used for testing code review functionality
- Bypasses MCP layer

#### ws_chat_roundtrip.py
- Test round-trip communication
- Measures latency and reliability
- Used for performance testing

---

## 🔄 COMPLETE REQUEST FLOW

### Scenario: User calls `thinkdeep_exai()` in Auggie CLI

```
1. USER (in Auggie CLI)
   ↓ Calls thinkdeep_exai()
   
2. AUGGIE CLI
   ↓ Sends MCP tool call to run_ws_shim.py
   
3. RUN_WS_SHIM.PY (MCP Server)
   ↓ Checks daemon health (NEW FIX!)
   ↓ Connects to ws://127.0.0.1:8765
   ↓ Sends WebSocket message: {"op": "call_tool", "name": "thinkdeep", "arguments": {...}}
   
4. WS_SERVER.PY (WebSocket Daemon)
   ↓ Receives WebSocket message
   ↓ Validates session
   ↓ Looks up tool in SERVER_TOOLS
   ↓ Executes tool (calls thinkdeep tool code)
   ↓ Sends progress updates every 2s (NEW FIX!)
   ↓ Returns result
   
5. RUN_WS_SHIM.PY
   ↓ Receives WebSocket response
   ↓ Converts to MCP response
   ↓ Returns to Auggie CLI
   
6. AUGGIE CLI
   ↓ Displays result to user
```

---

## 🔧 WHAT HAPPENS WHEN YOU RUN force_restart.ps1

### Step-by-Step Execution

**Step 1: Stop Existing Daemon**
```powershell
powershell -ExecutionPolicy Bypass -File scripts\ws_stop.ps1 -Force
```
- Reads PID from logs/ws_daemon.pid
- Sends SIGTERM to process
- Waits for process to exit

**Step 2: Kill All Python Processes**
```powershell
Get-Process python* | Stop-Process -Force
```
- Ensures no orphaned processes
- Kills daemon, shim, and any other Python processes
- **WARNING:** This kills ALL Python processes, including Auggie CLI's run_ws_shim.py!

**Step 3: Wait for Port to Be Free**
```powershell
Get-NetTCPConnection -LocalPort 8765 -State Listen
```
- Checks if port 8765 is free
- Waits up to 10 seconds
- Ensures clean restart

**Step 4: Clean Up Files**
```powershell
Remove-Item logs\ws_daemon.pid
Remove-Item logs\ws_daemon.health.json
```
- Removes stale PID file
- Removes stale health file
- Ensures fresh start

**Step 5: Start Daemon**
```powershell
powershell -ExecutionPolicy Bypass -File scripts\ws_start.ps1
```
- Launches run_ws_daemon.py
- Starts WebSocket server on port 8765
- Creates new PID and health files
- Daemon is now running and ready

---

## 🚨 CRITICAL UNDERSTANDING

### Two Separate Processes

**Process 1: WebSocket Daemon (Server)**
- Started by: `force_restart.ps1` → `ws_start.ps1` → `run_ws_daemon.py`
- Runs: `src/daemon/ws_server.py`
- Listens on: port 8765
- Lifetime: Until stopped or killed
- **Restarted by:** `force_restart.ps1` ✅

**Process 2: MCP Shim (Client)**
- Started by: Auggie CLI (when Auggie CLI starts)
- Runs: `scripts/run_ws_shim.py`
- Connects to: ws://127.0.0.1:8765
- Lifetime: Until Auggie CLI closes
- **Restarted by:** Closing and reopening Auggie CLI ✅

### Why Both Need Restart

**When you change code in:**
- `src/daemon/ws_server.py` → Restart daemon (`force_restart.ps1`)
- `scripts/run_ws_shim.py` → Restart Auggie CLI
- `server.py` (tool definitions) → Restart daemon (`force_restart.ps1`)
- `.env` → Restart both (daemon + Auggie CLI)

**Current Situation:**
- ✅ Daemon restarted (has new code)
- ❌ Auggie CLI NOT restarted (has old run_ws_shim.py code)
- **Result:** Mismatch causes connection issues

---

## 📊 FILE RELATIONSHIPS

```
force_restart.ps1
├── ws_stop.ps1
│   └── Reads: logs/ws_daemon.pid
│   └── Kills: WebSocket daemon process
└── ws_start.ps1
    └── run_ws_daemon.py
        └── src/daemon/ws_server.py
            ├── Imports: server.py (tools)
            ├── Imports: session_manager.py
            ├── Creates: logs/ws_daemon.pid
            ├── Creates: logs/ws_daemon.health.json
            ├── Writes: logs/ws_daemon.metrics.jsonl
            └── Listens: ws://127.0.0.1:8765

Auggie CLI (separate process)
└── Reads: mcp-config.auggie.json
    └── Launches: run_ws_shim.py
        ├── Reads: .env
        ├── Connects: ws://127.0.0.1:8765
        ├── Writes: logs/ws_shim.log
        └── Proxies: MCP calls to WebSocket daemon
```

---

## ✅ SUMMARY

**Q: Does force_restart.ps1 connect to running ws_server.py?**

**A: YES, but indirectly:**

1. `force_restart.ps1` **STARTS** `ws_server.py` (the WebSocket daemon)
2. `ws_server.py` **LISTENS** on port 8765
3. `run_ws_shim.py` (launched by Auggie CLI) **CONNECTS** to `ws_server.py`
4. Tool calls flow: Auggie CLI → run_ws_shim.py → ws_server.py → tool execution

**The Two-Process Model:**
- **Server:** `ws_server.py` (restarted by `force_restart.ps1`)
- **Client:** `run_ws_shim.py` (restarted by closing/opening Auggie CLI)

**Current Issue:**
- Server has new code ✅
- Client has old code ❌
- **Solution:** Restart Auggie CLI to load new client code

---

**Created:** 2025-10-04 23:15  
**Status:** COMPREHENSIVE ARCHITECTURE DOCUMENTATION  
**Purpose:** Complete understanding of system components and flow

