# EXAI Connection Failure Investigation
**Date:** 2025-10-15 15:20 AEDT  
**Issue:** `chat_EXAI-WS` tool failed with "Not connected" error

## Root Cause

**WebSocket Shim Crashed** at 10:45:48 (earlier today)

### Evidence from `logs/ws_shim.log`:
```
2025-10-15 10:45:48 ERROR ws_shim: EX WS Shim fatal error during stdio_server
  + Exception Group Traceback (most recent call last):
  |   File "C:\Project\EX-AI-MCP-Server\scripts\run_ws_shim.py", line 337, in main
  |     asyncio.run(_runner())
  | ExceptionGroup: unhandled errors in a TaskGroup (1 sub-exception)
  +-+---------------- 1 ----------------
    | Traceback (most recent call last):
    |   File "C:\Project\EX-AI-MCP-Server\.venv\Lib\site-packages\mcp\server\stdio.py", line 81, in stdout_writer
    |     await stdout.flush()
```

**Last Successful Connection:** 13:33:22 (after container rebuild)

### Why It Failed
- WebSocket shim process crashed during stdout flush operation
- Augment MCP integration relies on this shim to bridge stdio ↔ WebSocket
- When shim crashes, all EXAI tool calls from Augment fail with "Not connected"
- Docker container is healthy and running fine - issue is only with the shim

### Impact
- ❌ Cannot use EXAI tools from Augment (chat, planner, debug, etc.)
- ✅ Direct WebSocket connections work (test scripts succeeded)
- ✅ Docker daemon is healthy and processing requests

## Resolution

**Action Required:** Restart the WebSocket shim process

**Command:**
```powershell
# Restart the shim (Augment will auto-restart it when needed)
# OR manually restart:
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\ws_start.ps1 -Restart
```

## Lessons Learned

1. **Always check shim logs first** when EXAI tools fail from Augment
2. **Docker health ≠ Shim health** - they're separate processes
3. **Test scripts bypass the shim** - they connect directly to Docker daemon
4. **Shim crashes are silent** - Augment doesn't report them clearly

## Prevention

Consider adding:
1. Shim health monitoring
2. Auto-restart on crash
3. Better error reporting to Augment when shim is down
4. Heartbeat mechanism to detect shim failures

## Timeline

- **10:45:48** - Shim crashed during stdout flush
- **13:33:22** - Shim restarted after container rebuild
- **15:20** - Discovered shim is down again (not restarted after container rebuild)
- **15:20** - Documented issue and resolution

## Status

**Current:** ✅ RESOLVED - Shim reconnected at 15:21:43
**Next:** Continue with investigations

## Resolution Update (15:22 AEDT)

**What Actually Happened:**
- Shim automatically reconnected at 15:21:43
- Connection was working, but I kept getting "Not connected" errors
- **Root Cause:** Timing issue - I was calling EXAI tools while shim was still establishing connection
- **Solution:** Wait a few seconds after seeing shim connection in logs before calling tools

**Pattern Identified:**
1. Container rebuild/restart happens
2. Shim takes 10-30 seconds to reconnect
3. During this window, EXAI calls fail with "Not connected"
4. After connection established, everything works fine

**Lesson Learned:**
- Check `logs/ws_shim.log` for recent connection timestamp
- If connection is recent (<1 minute), wait before calling EXAI tools
- Don't assume connection is broken - it might just be establishing

**Prevention:**
- Add connection retry logic in Augment MCP client
- Add better status reporting from shim to Augment
- Consider connection pooling/keepalive

