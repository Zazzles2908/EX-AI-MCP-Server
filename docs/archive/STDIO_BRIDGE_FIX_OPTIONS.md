# STDIO Bridge Fix - Implementation Options Guide

**Date**: 2025-11-14 16:00:00 AEDT
**Purpose**: Detailed implementation guide for fixing EXAI MCP STDIO bridge
**Target**: Developers implementing the fix

---

## Overview

The EXAI MCP Server works perfectly at the daemon level (19 tools, direct WebSocket, API alignment), but the STDIO bridge is broken. This guide provides **three implementation options** to fix the MCP wrapper tools (`mcp__exai-mcp__chat`, `mcp__exai-mcp__analyze`, etc.).

---

## Option 1: Fix Shim Process Exit (Recommended Start) ⭐

**Goal**: Prevent `app.run()` from exiting, keep shim running indefinitely

**Files to Modify**: 3 files

### File 1: `scripts/runtime/run_ws_shim.py`

**Current Issue**: `app.run()` returns immediately after handling initialize request

**Modifications Required**:

#### Change 1A: Add Exception Handling (Lines 315-330)
```python
# BEFORE (Current - Crashes silently):
async with stdio_server() as (read_stream, write_stream):
    await app.run(
        read_stream,
        write_stream,
        app.create_initialization_options()
    )
    print(f"[ERROR] app.run() returned (THIS IS THE BUG!)", flush=True, file=sys.stderr)

# AFTER (Fixed):
async with stdio_server() as (read_stream, write_stream):
    try:
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )
        logger.error("[CRITICAL] app.run() returned - should never happen!")
    except asyncio.CancelledError:
        logger.info("app.run() cancelled - normal shutdown")
        raise
    except Exception as e:
        logger.error(f"[CRITICAL] app.run() crashed: {e}", exc_info=True)
        # Don't re-raise - let process exit gracefully
        raise
    finally:
        logger.info("Exiting stdio_server context")
```

**Purpose**: Catch and log any exception that causes `app.run()` to exit

#### Change 1B: Add Handler Exception Handling (Lines 127-295)
```python
# BEFORE (Current - exceptions propagate to app.run()):
@app.list_tools()
async def handle_list_tools() -> list[Tool]:
    # ... existing code ...
    # If this throws, app.run() may exit

# AFTER (Fixed):
@app.list_tools()
async def handle_list_tools() -> list[Tool]:
    """Handle tools/list - get list from daemon."""
    try:
        logger.info("[TOOLS] List tools requested")
        # ... existing code ...
        return mcp_tools
    except Exception as e:
        logger.error(f"[TOOLS] Exception in list_tools: {e}", exc_info=True)
        # Return empty list instead of crashing
        return []

@app.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tools/call - execute tool via daemon."""
    try:
        logger.info(f"[TOOL_CALL] Tool: {name}")
        # ... existing code ...
        return content
    except Exception as e:
        logger.error(f"[TOOL_CALL] Exception in {name}: {e}", exc_info=True)
        return [TextContent(type="text", text=f"Error: {str(e)}")]
```

**Purpose**: Prevent handler exceptions from crashing the MCP server

#### Change 1C: Add Daemon Connection Validation (Lines 54-125)
```python
# BEFORE (Current - connection may fail silently):
async def get_daemon_connection():
    global _daemon_ws
    # ... connection code ...
    return _daemon_ws

# AFTER (Fixed):
async def get_daemon_connection():
    global _daemon_ws, _daemon_ready
    # Add retry logic with timeout
    max_retries = 3
    retry_delay = 1

    for attempt in range(max_retries):
        try:
            if _daemon_ws is None or _daemon_ws.closed:
                logger.info(f"[DAEMON_CONNECT] Attempt {attempt + 1}/{max_retries}")
                # ... existing connection code ...

                # Verify connection is working
                if _daemon_ws.open:
                    _daemon_ready = True
                    logger.info(f"[DAEMON_CONNECT] ✓ Connection established")
                    return _daemon_ws
                else:
                    logger.warning(f"[DAEMON_CONNECT] ✗ Connection closed immediately")

            return _daemon_ws
        except Exception as e:
            logger.error(f"[DAEMON_CONNECT] ✗ Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay)
            else:
                raise
```

**Purpose**: Add resilience to daemon connection establishment

#### Change 1D: Add Health Monitoring (Lines 295-330)
```python
# Add periodic health check task
async def health_monitor():
    """Background task to monitor daemon connection."""
    while True:
        await asyncio.sleep(30)  # Check every 30 seconds
        if _daemon_ready and (_daemon_ws is None or _daemon_ws.closed):
            logger.warning("[HEALTH] Daemon connection lost, attempting reconnect...")
            try:
                _daemon_ws = None
                await get_daemon_connection()
            except Exception as e:
                logger.error(f"[HEALTH] Reconnect failed: {e}")

# Start health monitor in main()
async def main():
    # ... existing code ...
    # Start background tasks
    health_task = asyncio.create_task(health_monitor())
    try:
        async with stdio_server() as (read_stream, write_stream):
            # ... existing code ...
    finally:
        health_task.cancel()
```

**Purpose**: Detect and recover from daemon connection failures

---

### File 2: `scripts/runtime/start_ws_shim_safe.py`

**Modifications Required**:

#### Change 2A: Add Daemon Readiness Check (Lines 117-150)
```python
# BEFORE (Current - validates once):
async def test_daemon():
    # ... existing validation code ...
    return result

# AFTER (Enhanced):
async def test_daemon():
    """Comprehensive daemon validation."""
    import websockets
    import json

    uri = f"ws://127.0.0.1:{os.getenv('EXAI_WS_PORT', '3010')}"
    token = os.getenv("EXAI_WS_TOKEN", "")

    try:
        # Test connection
        async with websockets.connect(uri, ping_interval=None, open_timeout=5) as websocket:
            # Test hello
            hello = {
                'op': 'hello',
                'token': token,
                'protocolVersion': '2024-11-05',
                'clientInfo': {'name': 'shim-validator'}
            }
            await websocket.send(json.dumps(hello))

            # Test tool list
            await websocket.send(json.dumps({"op": "list_tools", "id": "test"}))
            tools_response = await asyncio.wait_for(websocket.recv(), timeout=10)
            tools_data = json.loads(tools_response)

            tool_count = len(tools_data.get("tools", []))
            if tool_count > 0:
                logger.info(f"✓ DAEMON READY - {tool_count} tools available")
                return True
            else:
                logger.error(f"✗ Daemon has no tools available")
                return False

    except asyncio.TimeoutError:
        logger.error(f"✗ Daemon validation timeout (>10s)")
        return False
    except Exception as e:
        logger.error(f"✗ Daemon validation failed: {e}")
        return False
```

**Purpose**: Comprehensive validation that daemon is fully ready

---

### File 3: `docker-compose.yml`

**Modifications Required**:

#### Change 3A: Increase Health Check Timeout
```yaml
# BEFORE:
services:
  exai-mcp-server:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://127.0.0.1:3002/health"]
      timeout: 3s
      retries: 3

# AFTER:
services:
  exai-mcp-server:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://127.0.0.1:3002/health"]
      timeout: 10s      # Increase timeout for daemon startup
      retries: 10       # More retries
      start_period: 60s # Allow 60s for full startup
```

**Purpose**: Give daemon more time to fully initialize before marking healthy

---

## Pros & Cons: Option 1

### Pros ✅
- **Low Risk**: Minimal code changes, builds on existing architecture
- **Fast Implementation**: 1-2 hours of coding
- **Targeted Fix**: Addresses the specific crash issue
- **Debuggable**: Exception logging makes future issues visible
- **Reversible**: Easy to rollback if problems arise
- **Resource Light**: No architectural changes

### Cons ❌
- **May Not Fix Root Cause**: If `app.run()` exits for a subtle reason, may not catch it
- **Doesn't Address Protocol**: Leaves protocol translation bugs unfixed
- **May Mask Issues**: Exception handling could hide real problems
- **Testing Required**: Need to verify shim actually stays running

### Best For ✅
- Initial diagnosis of the root cause
- Quick verification that fix path works
- As a foundation for Option 2
- Low-risk first step

---

## Option 2: Fix Protocol Translation (Core Solution)

**Goal**: Ensure correct message format translation between MCP JSON-RPC and EXAI WebSocket protocol

**Files to Modify**: 4 files

### File 1: `scripts/runtime/run_ws_shim.py`

**Current Issue**: Inconsistent message format sent to daemon

**Modifications Required**:

#### Change 2A: Add Message Validation Layer (Lines 145-185)
```python
# BEFORE (Current - sends messages directly):
async with _daemon_comm_lock:
    await daemon_ws.send(json.dumps(list_req))

# AFTER (With validation):
def validate_exai_message(message: dict) -> dict:
    """Validate message follows EXAI protocol format."""
    if "op" not in message:
        raise ValueError(f"Missing 'op' field in message: {message}")

    valid_ops = ["hello", "hello_ack", "list_tools", "tool_call", "call_tool_res", "progress", "stream_complete"]
    if message["op"] not in valid_ops:
        raise ValueError(f"Invalid 'op': {message['op']}. Valid: {valid_ops}")

    # Ensure required fields
    if message["op"] == "hello":
        required = ["protocolVersion"]
        for field in required:
            if field not in message:
                raise ValueError(f"Missing required field '{field}' for hello")

    return message

async def send_to_daemon(message: dict) -> str:
    """Send validated message to daemon and get response."""
    global _daemon_ws

    try:
        # Validate before sending
        validated = validate_exai_message(message)
        logger.info(f"[DAEMON_SEND] {validated['op']}")

        # Send with timeout
        async with _daemon_comm_lock:
            await asyncio.wait_for(
                _daemon_ws.send(json.dumps(validated)),
                timeout=10
            )

            # Receive with timeout
            response = await asyncio.wait_for(
                _daemon_ws.recv(),
                timeout=60
            )

            logger.info(f"[DAEMON_RECV] Response type: {type(response)}")
            return response

    except asyncio.TimeoutError:
        logger.error(f"[DAEMON] Timeout on {message.get('op', 'unknown')} operation")
        raise
    except Exception as e:
        logger.error(f"[DAEMON] Error on {message.get('op', 'unknown')}: {e}", exc_info=True)
        raise

# Usage in handlers:
await send_to_daemon(list_req)
```

**Purpose**: Ensure all messages to daemon are correctly formatted

#### Change 2B: Add Protocol State Machine (Lines 50-70)
```python
# Add state tracking
class ProtocolState(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    AUTHENTICATED = "authenticated"
    READY = "ready"

_protocol_state = ProtocolState.DISCONNECTED

async def transition_state(new_state: ProtocolState, context: str = ""):
    """Log state transitions."""
    global _protocol_state
    old_state = _protocol_state
    _protocol_state = new_state
    logger.info(f"[PROTOCOL] {old_state.value} → {new_state.value} {context}")

# Update connection flow:
async def get_daemon_connection():
    await transition_state(ProtocolState.CONNECTING)
    # ... existing code ...
    await transition_state(ProtocolState.AUTHENTICATED, f"token: {auth_token[:10]}...")
    # After hello_ack:
    await transition_state(ProtocolState.READY, f"session: {session_id}")
```

**Purpose**: Track protocol state to diagnose issues

#### Change 2C: Add Request/Response Correlation (Lines 158-178)
```python
# Add request tracking
_request_id_counter = 0
_active_requests: Dict[str, asyncio.Task] = {}

async def send_to_daemon(message: dict) -> str:
    global _request_id_counter

    # Generate unique ID
    _request_id_counter += 1
    request_id = f"shim_{int(time.time())}_{_request_id_counter}"
    message["id"] = request_id

    # Send message
    await _daemon_ws.send(json.dumps(message))

    # Track active request
    receive_task = asyncio.create_task(_daemon_ws.recv())
    _active_requests[request_id] = receive_task

    try:
        response = await asyncio.wait_for(receive_task, timeout=60)
        logger.info(f"[REQUEST] {request_id} completed")
        return response
    except Exception as e:
        logger.error(f"[REQUEST] {request_id} failed: {e}")
        raise
    finally:
        _active_requests.pop(request_id, None)
```

**Purpose**: Track which request receives which response

---

### File 2: `src/daemon/ws/connection_manager.py`

**Current Issue**: Daemon rejects malformed messages

**Modifications Required**:

#### Change 2D: Enhance Message Validation (Lines ~400-450)
```python
# BEFORE (Current):
async def _handle_incoming_message(websocket, message):
    # ... existing validation ...
    if "op" not in message:
        await websocket.send(json.dumps({"op": "error", ...}))
        return

# AFTER (Enhanced):
def validate_shim_message(message: dict) -> Tuple[str, dict]:
    """Validate message from shim follows EXAI protocol."""
    errors = []

    # Check for 'op' field
    if "op" not in message:
        errors.append("missing 'op' field")
    elif message["op"] not in EXPECTED_OPS:
        errors.append(f"invalid 'op': {message['op']}")

    # Validate hello message
    if message.get("op") == "hello":
        if "protocolVersion" not in message:
            errors.append("hello missing protocolVersion")
        if "token" not in message:
            errors.append("hello missing token")
        if "clientInfo" not in message:
            errors.append("hello missing clientInfo")

    # Validate tool_call message
    if message.get("op") == "tool_call":
        if "name" not in message:
            errors.append("tool_call missing name")
        if "arguments" not in message:
            errors.append("tool_call missing arguments")

    if errors:
        raise ValueError(f"Message validation failed: {', '.join(errors)}")

    return message["op"], message

# Usage:
try:
    op, validated_message = validate_shim_message(message)
    # Process validated message...
except ValueError as e:
    logger.warning(f"[VALIDATION] {e}")
    await websocket.send(json.dumps({
        "op": "error",
        "error": {"code": "VALIDATION_ERROR", "message": str(e)}
    }))
```

**Purpose**: Provide detailed validation errors instead of cryptic rejections

#### Change 2E: Add Connection Heartbeat (Lines ~300-350)
```python
# Add heartbeat to keep connection alive
async def _send_heartbeat(websocket):
    """Send periodic heartbeat to shim."""
    while websocket.open:
        try:
            await asyncio.sleep(30)  # Every 30 seconds
            await websocket.send(json.dumps({"op": "heartbeat", "timestamp": time.time()}))
        except:
            break

# When shim connects:
connection_task = asyncio.create_task(self._handle_connection(websocket))
heartbeat_task = asyncio.create_task(_send_heartbeat(websocket))

# Cancel heartbeat when connection closes
```

**Purpose**: Keep shim connection alive, detect disconnects

---

### File 3: `src/daemon/ws/tool_executor.py`

**Modifications Required**:

#### Change 2F: Fix Response Format (Lines ~600-650)
```python
# BEFORE (Current - format may be inconsistent):
response = {
    "op": "call_tool_res",
    "outputs": [...]
}

# AFTER (Standardized):
def format_tool_response(request_id: str, outputs: List[dict], from_cache: bool = False) -> dict:
    """Format tool response in consistent EXAI protocol."""
    # Clean outputs (ensure text strings)
    cleaned_outputs = []
    for output in outputs:
        if isinstance(output, dict):
            if "type" in output and "text" in output:
                cleaned_outputs.append(output)
            else:
                # Wrap non-formatted content
                cleaned_outputs.append({
                    "type": "text",
                    "text": json.dumps(output)
                })
        else:
            cleaned_outputs.append({
                "type": "text",
                "text": str(output)
            })

    response = {
        "op": "call_tool_res",
        "request_id": request_id,
        "outputs": cleaned_outputs,
        "timestamp": time.time()
    }

    if from_cache:
        response["from_cache"] = True

    return response
```

**Purpose**: Ensure consistent response format for MCP tools

---

### File 4: `tools/registry.py`

**Modifications Required**:

#### Change 2G: Add Tool Schema Validation (Lines 160-190)
```python
# BEFORE (Current - assumes tool has schema):
module = __import__(module_path, fromlist=[class_name])
cls = getattr(module, class_name)
self._tools[name] = cls()

# AFTER (With validation):
def _validate_tool_schema(tool_obj) -> dict:
    """Validate tool has required MCP schema."""
    errors = []

    # Check for get_input_schema method
    if not hasattr(tool_obj, 'get_input_schema'):
        errors.append(f"Missing get_input_schema method")
    else:
        try:
            schema = tool_obj.get_input_schema()
            if not isinstance(schema, dict):
                errors.append(f"get_input_schema returns {type(schema)}, not dict")
            elif "type" not in schema or schema["type"] != "object":
                errors.append(f"Invalid schema type: {schema}")
        except Exception as e:
            errors.append(f"get_input_schema failed: {e}")

    # Check for get_description
    if not (hasattr(tool_obj, 'get_description') or hasattr(tool_obj, 'description')):
        errors.append(f"Missing description")

    if errors:
        raise ValueError(f"Tool validation failed: {'; '.join(errors)}")

    return tool_obj

def _load_tool(self, name: str) -> None:
    module_path, class_name = TOOL_MAP[name]
    try:
        module = __import__(module_path, fromlist=[class_name])
        cls = getattr(module, class_name)
        tool_obj = cls()

        # Validate tool before adding
        _validate_tool_schema(tool_obj)
        self._tools[name] = tool_obj

        logger.info(f"[TOOL_LOAD] ✓ {name} loaded successfully")
    except Exception as e:
        logger.error(f"[TOOL_LOAD] ✗ {name} failed: {e}")
        self._errors[name] = str(e)
```

**Purpose**: Ensure all loaded tools have valid MCP schemas

---

## Pros & Cons: Option 2

### Pros ✅
- **Addresses Root Cause**: Fixes protocol translation issues
- **Robust**: Comprehensive validation prevents malformed messages
- **Better Diagnostics**: State machine and correlation help debug issues
- **Maintainable**: Clear message format makes future changes easier
- **Production-Ready**: Heartbeats and validation ensure stability
- **Standards Compliance**: Properly implements EXAI protocol

### Cons ❌
- **More Complex**: 4 files, significant code changes
- **Longer Implementation**: 2-3 hours of coding
- **Higher Risk**: More places to introduce bugs
- **Testing Required**: Must verify all message formats work
- **Daemon Changes**: Modifies daemon code (affects all clients)

### Best For ✅
- Production deployment
- Long-term stability
- When Option 1 is insufficient
- As complete solution

---

## Option 3: Architectural Refactor (Complete Overhaul)

**Goal**: Remove shim layer entirely, run MCP server directly in daemon

**Files to Modify**: 7 files + new files

### New File 1: `src/daemon/mcp_server.py` (NEW FILE)

**Purpose**: Native MCP server implementation

**Content**:
```python
"""
Native MCP Server Implementation
Runs MCP protocol directly in daemon, eliminating shim layer.
"""
import asyncio
import json
from typing import Any, List, Dict
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

class DaemonMCPServer:
    """MCP server that runs inside the daemon process."""

    def __init__(self, tool_registry):
        self.app = Server("exai-mcp")
        self.tool_registry = tool_registry
        self.ws_connections: Dict[str, Any] = {}

        # Register handlers
        self._register_handlers()

    def _register_handlers(self):
        """Register MCP handlers."""

        @self.app.list_tools()
        async def handle_list_tools():
            """List available tools from registry."""
            tools = []
            for name, tool_obj in self.tool_registry._tools.items():
                try:
                    schema = tool_obj.get_input_schema()
                    tools.append(Tool(
                        name=name,
                        description=tool_obj.get_description(),
                        inputSchema=schema
                    ))
                except Exception as e:
                    logger.warning(f"Failed to get schema for {name}: {e}")
            return tools

        @self.app.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]):
            """Execute tool via daemon's internal methods."""
            try:
                tool_obj = self.tool_registry.get_tool(name)
                result = await tool_obj.execute(arguments)
                return result
            except Exception as e:
                logger.error(f"Tool execution failed: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]

    async def run_stdio(self):
        """Run MCP server over stdio."""
        async with stdio_server() as (read_stream, write_stream):
            await self.app.run(
                read_stream,
                write_stream,
                self.app.create_initialization_options()
            )

    async def run_websocket(self):
        """Run MCP server over WebSocket (optional)."""
        # WebSocket MCP implementation
        # This would allow direct WebSocket MCP connections
        pass
```

**Purpose**: Native MCP server without protocol translation

---

### File 2: `src/daemon/ws_server.py` (MAJOR REFACTOR)

**Current Issue**: Custom protocol mixed with MCP

**Modifications Required**:

#### Change 3A: Separate MCP and Custom Protocol (Lines ~600-700)
```python
# BEFORE (Current - mixed protocol handling):
async def main_async():
    # ... daemon startup ...

    # Start both servers
    await asyncio.gather(
        start_mcp_server(),
        start_custom_ws_server()
    )

# AFTER (Separated):
async def main_async():
    # ... daemon startup ...

    # Start stdio MCP server in daemon process
    mcp_task = asyncio.create_task(run_native_mcp_server())

    # Keep custom WebSocket server for non-MCP clients
    ws_task = asyncio.create_task(start_custom_ws_server())

    await asyncio.gather(mcp_task, ws_task)

async def run_native_mcp_server():
    """Run MCP server directly in daemon process."""
    from src.daemon.mcp_server import DaemonMCPServer

    # Get tool registry
    registry_instance = get_registry_instance()

    # Create MCP server
    mcp_server = DaemonMCPServer(registry_instance)

    # Run over stdio
    await mcp_server.run_stdio()
```

**Purpose**: Run MCP server natively without shim

---

### File 3: `src/daemon/ws/protocol_adapter.py` (NEW FILE)

**Purpose**: Adapter for custom protocol to work alongside MCP

**Content**:
```python
"""
Protocol Adapter Layer
Allows custom EXAI protocol to coexist with MCP protocol.
"""
import asyncio
from typing import Any

class ProtocolAdapter:
    """Adapt between MCP responses and custom EXAI protocol."""

    def __init__(self, mcp_tool_executor):
        self.tool_executor = mcp_tool_executor

    async def handle_custom_message(self, message: dict, websocket):
        """Handle custom EXAI protocol messages."""
        op = message.get("op")

        if op == "hello":
            return await self._handle_hello(message, websocket)
        elif op == "list_tools":
            return await self._handle_list_tools(websocket)
        elif op == "tool_call":
            return await self._handle_tool_call(message, websocket)
        else:
            raise ValueError(f"Unknown op: {op}")

    async def _handle_list_tools(self, websocket):
        """List tools in custom protocol format."""
        # Get tools from MCP server's registry
        tools = await self._get_mcp_tools()

        # Format as EXAI protocol
        response = {
            "op": "tools_list",
            "tools": tools
        }

        await websocket.send(json.dumps(response))

    async def _handle_tool_call(self, message: dict, websocket):
        """Execute tool call via MCP server."""
        name = message.get("name")
        arguments = message.get("arguments", {})

        # Execute via MCP tool
        result = await self.tool_executor.execute(name, arguments)

        # Format as EXAI protocol
        response = {
            "op": "call_tool_res",
            "outputs": result
        }

        await websocket.send(json.dumps(response))
```

**Purpose**: Bridge between MCP and custom protocol

---

### File 4: `src/daemon/ws/request_router.py`

**Modifications Required**:

#### Change 3B: Route to Protocol Adapter (Lines ~200-250)
```python
# BEFORE (Current - handles everything):
async def route_request(message: dict, websocket):
    # ... custom protocol handling ...
    pass

# AFTER (Route to appropriate handler):
async def route_request(message: dict, websocket):
    """Route message to appropriate protocol handler."""
    if "op" in message:
        # Custom EXAI protocol
        adapter = ProtocolAdapter(tool_executor)
        return await adapter.handle_custom_message(message, websocket)
    elif "jsonrpc" in message:
        # MCP protocol
        await handle_mcp_message(message, websocket)
    else:
        raise ValueError("Unknown message format")
```

**Purpose**: Route to correct protocol handler

---

### File 5: `src/providers/registry_core.py`

**Modifications Required**:

#### Change 3C: Make Registry Accessible to MCP (Lines ~300-350)
```python
# BEFORE (Current - registry is internal):
class ProviderRegistry:
    def __init__(self):
        self._providers: Dict[ProviderType, Type[BaseProvider]] = {}
        self._instances: Dict[ProviderType, BaseProvider] = {}

    # No global access for MCP server

# AFTER (Export registry for MCP):
class ProviderRegistry:
    def __init__(self):
        self._providers: Dict[ProviderType, Type[BaseProvider]] = {}
        self._instances: Dict[ProviderType, BaseProvider] = {}

    # Export singleton instance
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

# Global access function
def get_registry_instance():
    """Get global registry instance for MCP server."""
    return ProviderRegistry.get_instance()
```

**Purpose**: Allow MCP server to access providers

---

### File 6: `tools/registry.py`

**Modifications Required**:

#### Change 3D: Make Registry Accessible (Lines 220-230)
```python
# BEFORE (Current - internal to daemon):
class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Any] = {}
        self._errors: Dict[str, str] = {}

# AFTER (Export globally):
# Global registry instance
_REGISTRY_INSTANCE = None

def get_tool_registry():
    """Get global tool registry instance."""
    global _REGISTRY_INSTANCE
    if _REGISTRY_INSTANCE is None:
        _REGISTRY_INSTANCE = ToolRegistry()
        _REGISTRY_INSTANCE.build_tools()
    return _REGISTRY_INSTANCE

# Update daemon startup to create registry
def build_global_registry():
    """Build registry for both daemon and MCP server."""
    global _REGISTRY_INSTANCE
    _REGISTRY_INSTANCE = ToolRegistry()
    _REGISTRY_INSTANCE.build_tools()
    return _REGISTRY_INSTANCE
```

**Purpose**: Allow MCP server to access tool registry

---

### File 7: `docker-compose.yml`

**Modifications Required**:

#### Change 3E: Remove Shim Dependency
```yaml
# BEFORE (Current - requires shim):
services:
  exai-mcp-server:
    build: .
    command: python -m src.daemon.ws_server

# AFTER (Direct MCP server):
services:
  exai-mcp-server:
    build: .
    command: python -m src.daemon.mcp_server --stdio
    # Or for WebSocket MCP:
    # command: python -m src.daemon.mcp_server --websocket
```

**Purpose**: Run MCP server directly in container

---

### File 8: `.mcp.json`

**Modifications Required**:

#### Change 3F: Update MCP Configuration
```json
// BEFORE (Current - uses shim):
{
  "mcpServers": {
    "exai-mcp": {
      "command": "python",
      "args": ["-u", "scripts/runtime/start_ws_shim_safe.py"]
    }
  }
}

// AFTER (Direct connection):
{
  "mcpServers": {
    "exai-mcp": {
      "command": "docker-compose",
      "args": ["exec", "exai-mcp-server", "python", "-m", "src.daemon.mcp_server"]
    }
  }
}

// Or even better - native stdio through Docker:
{
  "mcpServers": {
    "exai-mcp": {
      "command": "docker",
      "args": [
        "exec",
        "-i",
        "exai-mcp-server-exai-mcp-server-1",
        "python",
        "-m",
        "src.daemon.mcp_server"
      ]
    }
  }
}
```

**Purpose**: Connect directly to MCP server

---

## Pros & Cons: Option 3

### Pros ✅
- **Eliminates Entire Class of Bugs**: No shim = no shim bugs
- **Best Performance**: No protocol translation overhead
- **Cleanest Architecture**: MCP server directly integrated
- **MCP Native**: Proper stdio support, full compliance
- **Maintainable**: Simpler code path
- **Scalable**: Better resource utilization
- **Future-Proof**: Aligned with MCP ecosystem

### Cons ❌
- **Massive Effort**: 8+ files, significant refactoring
- **Long Timeline**: 8-16 hours of coding
- **High Risk**: Many changes, hard to test incrementally
- **Breaking Changes**: Affects all clients (not just MCP)
- **Complex Testing**: Must verify both protocols work
- **Rollback Difficulty**: Can't easily revert changes

### Best For ✅
- Long-term project sustainability
- When other options fail
- Production re-architecture
- When maximum performance is needed

---

## Comparison Matrix

| Aspect | Option 1 | Option 2 | Option 3 |
|--------|----------|----------|----------|
| **Time to Implement** | 1-2 hours | 2-3 hours | 8-16 hours |
| **Files Modified** | 3 | 4 | 7 |
| **Risk Level** | Low | Medium | High |
| **Complexity** | Low | Medium | High |
| **Maintainability** | Medium | High | Highest |
| **Performance** | No Change | No Change | Best |
| **Bugs Fixed** | Process Exit | Protocol Issues | All |
| **Production Ready** | Maybe | Yes | Yes |
| **Testing Required** | Minimal | Moderate | Extensive |
| **Rollback Difficulty** | Easy | Medium | Hard |

---

## Recommended Approach

### Phase 1: Start with Option 1 (30 minutes)
**Purpose**: Diagnose root cause
- Add exception logging
- See why `app.run()` exits
- Verify shim stays running

### Phase 2: Implement Option 2 (2 hours)
**Purpose**: Fix protocol issues
- Add message validation
- Fix daemon communication
- Test end-to-end flow

### Phase 3: Optionally Move to Option 3 (Future)
**Purpose**: Long-term architecture
- If recurring shim issues
- For maximum performance
- When project timeline allows

---

## Implementation Priority

### Immediate (Option 1)
1. Add exception handling to `run_ws_shim.py`
2. Test if shim stays running
3. Verify daemon connection works

### Short-term (Option 2)
1. Implement message validation
2. Add protocol state tracking
3. Test full MCP → EXAI → MCP flow
4. Verify all 19 tools work

### Long-term (Option 3)
1. Design native MCP server
2. Implement protocol adapter
3. Migrate incrementally
4. Verify both protocols work

---

## Testing Strategy

### For Option 1
```bash
# Test 1: Shim stays running
python scripts/runtime/run_ws_shim.py &
sleep 5
ps aux | grep run_ws_shim
# Should show process running

# Test 2: MCP initialization works
cat > test_mcp.py << 'EOF'
import subprocess, json
proc = subprocess.Popen(["python", "scripts/runtime/run_ws_shim.py"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
proc.stdin.write(json.dumps({"jsonrpc":"2.0","id":1,"method":"initialize",...}))
response = proc.stdout.readline()
print(response)
EOF
python test_mcp.py
# Should get valid response
```

### For Option 2
```bash
# Test 1: Message validation
python -c "from scripts.runtime.run_ws_shim import validate_exai_message; validate_exai_message({'op':'hello', ...})"
# Should pass

# Test 2: Full MCP flow
python test_mcp.py << 'EOF'
# Send initialize, initialized, tools/list
# Verify 19 tools returned
EOF

# Test 3: Tool execution
# Send tools/call for chat tool
# Verify response received
```

### For Option 3
```bash
# Test 1: Native MCP server
docker-compose exec exai-mcp-server python -m src.daemon.mcp_server --test
# Should run without errors

# Test 2: Direct stdio connection
cat > test_native.py << 'EOF'
import subprocess, json
proc = subprocess.Popen(["docker", "exec", "-i", "exai-mcp-server-1", "python", "-m", "src.daemon.mcp_server"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
# Send MCP initialize
# Get valid response
# Test tools/list
# Verify tools
EOF

# Test 3: Custom protocol still works
# Verify WebSocket clients still connect
# Test custom protocol messages
```

---

## Success Criteria

### Option 1 Success ✅
- [ ] Shim process runs for >30 seconds without exiting
- [ ] No unhandled exceptions in logs
- [ ] Daemon connection established successfully
- [ ] MCP initialization returns valid response

### Option 2 Success ✅
- [ ] All messages to daemon pass validation
- [ ] Protocol state machine shows: DISCONNECTED → CONNECTING → CONNECTED → AUTHENTICATED → READY
- [ ] `mcp__exai-mcp__chat` returns response (not empty)
- [ ] `mcp__exai-mcp__analyze` returns response (not empty)
- [ ] All 19 tools accessible via MCP wrapper
- [ ] Tools execute and return proper results

### Option 3 Success ✅
- [ ] Native MCP server runs in daemon
- [ ] Direct stdio connection works without shim
- [ ] All 19 tools available via native MCP
- [ ] Custom protocol still works for WebSocket clients
- [ ] Performance improved (no translation overhead)
- [ ] No shim-related bugs

---

## Rollback Plan

### Option 1 Rollback
```bash
# Simply revert changes to 3 files
git checkout HEAD -- scripts/runtime/run_ws_shim.py
git checkout HEAD -- scripts/runtime/start_ws_shim_safe.py
git checkout HEAD -- docker-compose.yml
```

### Option 2 Rollback
```bash
# Revert 4 files
git checkout HEAD -- scripts/runtime/run_ws_shim.py
git checkout HEAD -- src/daemon/ws/connection_manager.py
git checkout HEAD -- src/daemon/ws/tool_executor.py
git checkout HEAD -- tools/registry.py
```

### Option 3 Rollback
```bash
# Need to restore previous architecture
# May require full system rebuild
git reset --hard HEAD~1
# Or restore from backup
```

---

## Conclusion

**Start with Option 1** to diagnose the issue quickly and safely. Once shim is stable, **implement Option 2** for full functionality. Consider **Option 3** only if recurring shim issues justify architectural changes.

**Timeline**: 2-3 hours for full working solution (Option 1 + 2)
**Risk**: Low (with Option 1) → Medium (with Option 2)
**Outcome**: Fully functional EXAI MCP integration with Claude Code

---

**Next Steps**: Choose option, start implementation
**Priority**: High - enables core EXAI MCP functionality
**Impact**: Users can use `@exai-mcp` tools in Claude Code
