# MCP Connection Fix Applied

## Fix Summary

Applied timeout fix to resolve EX-AI MCP server connection issue.

## Changes Made

### File: `scripts/runtime/run_ws_shim.py`

**Change 1: Increased Timeout (Line 90)**
- **Before:** `timeout=10` (10 seconds)
- **After:** `timeout=30` (30 seconds)
- **Reason:** The daemon was taking longer than 10 seconds to respond under load, causing timeout errors

**Change 2: Better Error Handling (Lines 71-114)**
- Added separate handling for `asyncio.TimeoutError`
- Added proper connection cleanup in error cases
- Added `exc_info=True` to error logging for better debugging
- Ensures `_daemon_ws` is set to None on all error paths

### Why This Fixes the Issue

The root cause was a **10-second timeout** on the daemon handshake (`hello_ack` response). Under certain conditions (system load, Docker networking latency, etc.), the daemon could take longer than 10 seconds to respond, causing:

1. `asyncio.TimeoutError` exception
2. Generic exception handling that didn't properly clean up the connection
3. Shim unable to complete MCP initialization
4. MCP client timeout after 30 seconds

By increasing the timeout to 30 seconds and adding better error handling, the shim now has sufficient time to complete the handshake and properly handle any errors.

## Testing

To verify the fix works:

1. **Restart Claude Code** or the MCP connection
2. **Check logs** for successful daemon connection:
   ```
   [DAEMON_CONNECT] ✓ Connected to daemon
   [HELLO] ✓ Hello sent to daemon
   [HELLO] ✓ Received hello_ack: ok=True
   ```
3. **Verify tools loaded** - should see 15 tools available
4. **Test a tool call** to ensure full functionality

## Expected Behavior After Fix

- ✅ Shim connects to daemon successfully
- ✅ Hello handshake completes within 30 seconds
- ✅ Tools list loads (15 tools)
- ✅ Tool calls work normally
- ✅ No connection timeouts

## Additional Improvements Made

1. **Explicit TimeoutError handling** - ensures connection leaks don't occur
2. **Better error messages** - includes actual error details
3. **Connection cleanup** - WebSocket properly closed on all error paths
4. **Debug logging** - `exc_info=True` shows full stack traces

## Verification Commands

```bash
# Check daemon health
curl http://127.0.0.1:3002/health

# Check daemon logs
docker logs exai-mcp-daemon --tail 50

# Test manual connection
python -c "import asyncio, websockets, json; asyncio.run(async with websockets.connect('ws://127.0.0.1:3010') as ws: print('Connected'))"
```

## Files Modified

- `C:\Project\EX-AI-MCP-Server\scripts\runtime\run_ws_shim.py` (lines 71-114)

## Status

✅ **FIX APPLIED** - Ready for testing

---

**Applied on:** 2025-11-13  
**Issue:** MCP server connection timeout  
**Fix:** Increased daemon handshake timeout from 10s to 30s with better error handling
