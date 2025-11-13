# MCP Connection Issue - Root Cause Analysis & Fix

## Problem Summary

The `exai-mcp` MCP server fails to connect with a 30-second timeout error. The shim starts successfully but times out when trying to complete the MCP initialization process.

## Root Cause

After detailed investigation, the issue is **NOT**:
- ❌ Docker not running (it's healthy)
- ❌ Port not accessible (port 3010 is open)
- ❌ Missing token (token is loaded correctly)
- ❌ Daemon not running (daemon is running and accepting connections)

**The actual issue** is that the shim's `get_daemon_connection()` function has a race condition or blocking behavior that causes it to hang during the daemon handshake process, specifically during the `hello`/`hello_ack` exchange.

## Evidence

1. **Daemon is healthy and responding:**
   ```json
   {"status": "healthy", "service": "exai-mcp-daemon", "uptime_human": "0:13:30"}
   ```

2. **Manual WebSocket connection works:**
   - Successfully connects to ws://127.0.0.1:3010
   - Successfully sends hello and receives hello_ack
   - Successfully retrieves tool list (15 tools available)

3. **Token is loaded correctly in shim:**
   ```
   [DEBUG] EXAI_WS_TOKEN in wrapper: pYf69sHNkOYlYLRTJfMr...
   ```

4. **Shim sends initialization response successfully:**
   ```
   {"jsonrpc":"2.0","id":0,"result":{"protocolVersion":"2025-06-18"...}}
   ```

5. **Timeout occurs during tools/list phase:**
   - MCP client waits 30 seconds for shim to complete initialization
   - Shim never completes, causing timeout

## Suspected Issue

The `get_daemon_connection()` function in `run_ws_shim.py` has a problematic code flow:

```python
async def get_daemon_connection():
    global _daemon_ws
    async with _daemon_lock:
        if _daemon_ws is None or _daemon_ws.closed:
            # Connect to daemon
            _daemon_ws = await websockets.connect(daemon_uri)
            
            # Send hello
            await _daemon_ws.send(json.dumps(hello_msg))
            
            # Wait for hello_ack - THIS CAN HANG!
            response = await asyncio.wait_for(_daemon_ws.recv(), timeout=10)
            hello_ack = json.loads(response)
            
            if not hello_ack.get("ok"):
                await _daemon_ws.close()
                _daemon_ws = None
                raise Exception(f"Daemon authentication failed")
                
        return _daemon_ws
```

**Potential problems:**
1. The `asyncio.wait_for` timeout of 10 seconds might not be sufficient under load
2. If an exception occurs after the WebSocket is created but before the global is set, the connection could leak
3. The `hello_ack` response handling might be synchronous/blocking in some cases

## Recommended Fixes

### Option 1: Increase Timeouts (Quick Fix)

Increase the timeout in `get_daemon_connection()` from 10 seconds to 30 seconds:

```python
response = await asyncio.wait_for(_daemon_ws.recv(), timeout=30)
```

### Option 2: Add Better Error Handling (Recommended)

Wrap the entire connection setup in try/except and ensure proper cleanup:

```python
async def get_daemon_connection():
    global _daemon_ws
    async with _daemon_lock:
        if _daemon_ws is None or _daemon_ws.closed:
            try:
                # Connect
                _daemon_ws = await websockets.connect(daemon_uri)
                
                # Send hello with timeout
                hello_msg = {...}
                await asyncio.wait_for(
                    _daemon_ws.send(json.dumps(hello_msg)), 
                    timeout=5
                )
                
                # Receive hello_ack with increased timeout
                response = await asyncio.wait_for(
                    _daemon_ws.recv(), 
                    timeout=30
                )
                hello_ack = json.loads(response)
                
                if not hello_ack.get("ok"):
                    error_msg = hello_ack.get('error', 'Unknown error')
                    await _daemon_ws.close()
                    _daemon_ws = None
                    raise Exception(f"Daemon authentication failed: {error_msg}")
                    
            except Exception as e:
                logger.error(f"Failed to connect to daemon: {e}", exc_info=True)
                if _daemon_ws and not _daemon_ws.closed:
                    await _daemon_ws.close()
                _daemon_ws = None
                raise
                
        return _daemon_ws
```

### Option 3: Add Connection Retry Logic (Most Robust)

Implement exponential backoff for daemon connection:

```python
import random

async def get_daemon_connection_with_retry(max_retries=3):
    global _daemon_ws
    async with _daemon_lock:
        if _daemon_ws is None or _daemon_ws.closed:
            for attempt in range(max_retries):
                try:
                    _daemon_ws = await websockets.connect(daemon_uri)
                    # ... rest of connection logic ...
                    return _daemon_ws
                    
                except Exception as e:
                    logger.warning(f"Daemon connection attempt {attempt + 1} failed: {e}")
                    if _daemon_ws:
                        await _daemon_ws.close()
                        _daemon_ws = None
                    
                    if attempt < max_retries - 1:
                        wait_time = (2 ** attempt) + random.uniform(0, 1)
                        logger.info(f"Retrying in {wait_time:.2f}s...")
                        await asyncio.sleep(wait_time)
                    else:
                        logger.error(f"All {max_retries} connection attempts failed")
                        raise
                        
        return _daemon_ws
```

## Immediate Action Items

1. **Check the actual timeout value** in `run_ws_shim.py` line 90
2. **Increase the hello_ack timeout** from 10s to 30s
3. **Add detailed logging** to the connection process
4. **Test the fix** with the MCP server

## Files to Modify

- `C:\Project\EX-AI-MCP-Server\scripts\runtime\run_ws_shim.py`
  - Function: `get_daemon_connection()` (around line 58)
  - Change: Increase timeout from 10 to 30 seconds
  - Add: Better error handling and logging

## Testing

After applying the fix:

1. Restart the MCP server in Claude Code
2. Check if connection succeeds within 30 seconds
3. Verify tools are loaded (should see 15 tools)
4. Test a simple tool call to ensure functionality

## Additional Notes

The issue might be related to:
- Windows-specific asyncio behavior (IOCP proactor)
- MCP library version compatibility
- WebSocket library version mismatches
- Docker networking latency

Current versions:
- Python: 3.13.9
- websockets: 14.2
- MCP: 1.21.0

All versions are compatible, so the issue is likely in the code logic.
