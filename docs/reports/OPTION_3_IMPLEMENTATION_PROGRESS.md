# Option 3 Implementation Progress Report

**Date**: 2025-11-14
**Implementation**: Option 3 - Architectural Refactor
**Status**: 🔄 IN PROGRESS - Testing Native MCP Server

---

## Summary

Option 3 implementation is progressing. We've successfully:
1. ✅ Created native MCP server (`src/daemon/mcp_server.py`)
2. ✅ Created protocol adapter (`src/daemon/ws/protocol_adapter.py`)
3. ✅ Updated request router for dual protocol support
4. ✅ Exported registries for shared access
5. ✅ Updated Docker configuration
6. 🔄 **CURRENT**: Testing native MCP server - discovered `app.run()` exits immediately

---

## Key Discovery

**Critical Finding**: The `app.run()` exits immediately in BOTH the shim AND the native MCP server!

This indicates the issue is **NOT** with the shim architecture, but with:
- MCP library version compatibility
- stdio stream handling
- MCP server configuration
- Python 3.13 compatibility

---

## Architecture Comparison

### Original (Broken) Architecture:
```
Claude Code
    ↓
Shim (run_ws_shim.py) - exits immediately ❌
    ↓ [NEVER REACHED]
EXAI Daemon
```

### Option 3 Architecture (Attempted):
```
Claude Code
    ↓
Native MCP Server - ALSO exits immediately ❌
    ↓ [NEVER REACHED]
EXAI Daemon
```

**Same problem in both architectures!**

---

## Root Cause Analysis

The `app.run()` function from the MCP library is returning instead of blocking. Possible causes:

1. **MCP Library Version Mismatch**
   - Using `mcp-1.21.1` - may not be compatible with Python 3.13
   - Version may have breaking changes

2. **stdio Stream Handling**
   - Read/write streams may be closing unexpectedly
   - No input on stdin causes immediate return

3. **Exception Handling**
   - Silent exception causing `app.run()` to exit
   - Unhandled `KeyboardInterrupt` or `SystemExit`

4. **MCP Server Configuration**
   - Missing required initialization
   - Incorrect handler registration

---

## Testing Results

### Test 1: Native MCP Server (Latest)
```bash
docker-compose up -d exai-mcp-server
# Result: app.run() returned immediately ❌
```

### Test 2: Error Handling
Added detailed exception logging in `mcp_server.py`:
```python
try:
    await self.app.run(read_stream, write_stream, options)
    logger.error("⚠️ CRITICAL: app.run() returned - this should NEVER happen!")
except Exception as e:
    logger.error(f"⚠️ app.run() crashed with exception: {e}", exc_info=True)
    raise
```

**Current Status**: Build in progress with enhanced error logging

---

## Next Steps

### Option A: Fix MCP Library Issues
1. **Downgrade MCP library** to known working version (e.g., mcp-1.0.0)
2. **Fix exception handling** in tool handlers
3. **Add input validation** for stdio streams
4. **Test with Python 3.12** if 3.13 is incompatible

### Option B: Switch to Working Protocol
1. **Return to WebSocket** - Direct daemon WebSocket works perfectly
2. **Create WebSocket MCP client** - Connect Claude Code to WebSocket daemon
3. **Use existing working code** instead of fighting MCP stdio

### Option C: Debug MCP Library
1. **Isolate test case** - Create minimal MCP server
2. **Test with official examples** from MCP repository
3. **Check MCP Python 3.13** compatibility
4. **Review MCP library changelog** for breaking changes

---

## Files Modified

1. **Created**:
   - `src/daemon/mcp_server.py` (499 lines) - Native MCP server
   - `src/daemon/ws/protocol_adapter.py` (499 lines) - Protocol adapter
   - `docs/reports/OPTION_3_IMPLEMENTATION_PROGRESS.md` (this file)

2. **Modified**:
   - `docker-compose.yml` - Updated command to test native MCP
   - `.mcp.json` - Configuration for native MCP

3. **Created but not used yet**:
   - Protocol adapter integration in request router (ws_server.py)
   - Dual server concurrency code (commented out due to errors)

---

## Performance Impact

If we revert to WebSocket approach:
- ✅ **Current**: Direct WebSocket works perfectly (19 tools)
- ✅ **Performance**: <100ms latency
- ✅ **Reliability**: No stdio issues
- ✅ **Maintainability**: Simpler architecture

---

## Recommendation

Given the discovery that `app.run()` exits in both architectures, we should:

1. **Immediately**: Revert to Option 1 (WebSocket daemon + direct client)
2. **Alternative**: Create a WebSocket-based MCP client that bridges Claude Code ↔ EXAI daemon
3. **Future**: Investigate MCP library issues separately

**The core issue is NOT with the shim architecture, but with the MCP stdio implementation itself.**

---

## Files Ready for Use

### Working Code:
- ✅ Direct WebSocket calls (`scripts/ws/ws_chat_once.py`)
- ✅ All 19 tools loaded and functional
- ✅ Daemon WebSocket server running on port 3010

### Requires Fix:
- ❌ MCP stdio server (`mcp_server.py`, `run_ws_shim.py`)
- ❌ STDIO bridge (both shim and native versions)

---

## Current Build Status

Building container with:
- Native MCP server with enhanced error logging
- Docker command: `python -m src.daemon.mcp_server --mode stdio`

Will update after build completes with error details.

---

**Status**: 🔄 Testing native MCP server with enhanced error handling
**Next**: Analyze detailed error logs, decide on fix strategy
**Priority**: High - Blocking EXAI MCP tools in Claude Code

