# WebSocket Server Integration Plan
**Date:** 2025-10-21  
**Branch:** refactor/ws-server-modularization-2025-10-21  
**Status:** IN PROGRESS

## Overview

This document outlines the step-by-step plan for integrating the extracted WebSocket modules back into ws_server.py.

## Extracted Modules (COMPLETE ✅)

1. **connection_manager.py** (418 lines) - Connection lifecycle, auth, message routing
2. **request_router.py** (680 lines) - Message routing, tool execution, caching
3. **session_handler.py** (145 lines) - Session lifecycle, periodic cleanup
4. **health_monitor.py** (245 lines) - Health monitoring, semaphore health checks

**Total Extracted:** 1,488 lines

## Current State

- ✅ All 4 modules extracted and committed
- ✅ Imports added to ws_server.py (lines 78-86)
- ⏳ Functions still exist in ws_server.py (need removal)
- ⏳ main_async() still uses old functions (needs update)

## Functions to Remove from ws_server.py

### Connection Manager Functions
- `_safe_recv()` - Line 500-507
- `_safe_send()` - Line 509-596
- `_serve_connection()` - Line 1409-1670

### Request Router Functions
- `_handle_message()` - Line 602-1402

### Session Handler Functions
- `_periodic_session_cleanup()` - Line 1709-1729

### Health Monitor Functions
- `_recover_semaphore_leaks()` - Line 1673-1681
- `_check_semaphore_health()` - Line 1684-1692
- `_periodic_semaphore_health()` - Line 1695-1706
- `_health_writer()` - Line 1732-1802

**Total to Remove:** ~1,500 lines

## Integration Steps

### Step 1: Initialize Modules in main_async() ✅ PLANNED

Add after line 1905 (after session semaphore manager initialization):

```python
# Week 3 Fix #15 (2025-10-21): Initialize extracted WebSocket modules
logger.info("Initializing WebSocket modules...")

# Initialize SessionHandler
session_handler = SessionHandler(session_manager=_sessions)

# Initialize HealthMonitor
health_monitor = HealthMonitor(
    health_path=_health_path,
    global_sem=_global_sem,
    provider_sems=_provider_sems,
    session_handler=session_handler,
    server_tools=SERVER_TOOLS,
    host=EXAI_WS_HOST,
    port=EXAI_WS_PORT,
    started_at=STARTED_AT,
    global_max_inflight=GLOBAL_MAX_INFLIGHT,
    provider_max_inflight={"KIMI": KIMI_MAX_INFLIGHT, "GLM": GLM_MAX_INFLIGHT}
)

# Initialize RequestRouter
request_router = RequestRouter(
    session_manager=_sessions,
    server_tools=SERVER_TOOLS,
    global_sem=_global_sem,
    provider_sems=_provider_sems,
    validated_env=_validated_env,
    use_per_session_semaphores=USE_PER_SESSION_SEMAPHORES
)

logger.info("WebSocket modules initialized successfully")
```

### Step 2: Update _connection_wrapper ✅ PLANNED

Replace line 1935 (`await _serve_connection(ws)`) with:

```python
await serve_connection(
    ws,
    connection_manager=get_connection_manager(),
    rate_limiter=get_rate_limiter(),
    session_manager=_sessions,
    auth_token_manager=_auth_token_manager,
    message_handler=request_router.handle_message,
    hello_timeout=HELLO_TIMEOUT,
    resilient_ws_manager=_resilient_ws
)
```

### Step 3: Update Background Task Startup ✅ PLANNED

Replace lines 1973-1977 with:

```python
# Start health monitoring tasks
health_writer_task, semaphore_health_task = health_monitor.start_monitoring_tasks(stop_event)

# Start session cleanup task
session_cleanup_task = session_handler.start_cleanup_task(stop_event)

logger.info("[BACKGROUND_TASKS] Started health monitoring and session cleanup tasks")
```

### Step 4: Remove Extracted Functions ✅ PLANNED

Remove the following line ranges:
- Lines 500-507: `_safe_recv()`
- Lines 509-596: `_safe_send()`
- Lines 602-1402: `_handle_message()`
- Lines 1409-1670: `_serve_connection()`
- Lines 1673-1681: `_recover_semaphore_leaks()`
- Lines 1684-1692: `_check_semaphore_health()`
- Lines 1695-1706: `_periodic_semaphore_health()`
- Lines 1709-1729: `_periodic_session_cleanup()`
- Lines 1732-1802: `_health_writer()`

**Expected Result:** ws_server.py reduced from 2,010 lines to ~500 lines

### Step 5: Test Integration ✅ PLANNED

1. Restart Docker container
2. Check Docker logs for errors
3. Run test suite: `docker exec exai-mcp-daemon python /app/test_suite.py`
4. Verify health endpoint: `curl http://localhost:8082/health`
5. Test WebSocket connection manually

## Dependencies to Pass

### RequestRouter Dependencies
- `session_manager`: _sessions
- `server_tools`: SERVER_TOOLS
- `global_sem`: _global_sem
- `provider_sems`: _provider_sems
- `validated_env`: _validated_env
- `use_per_session_semaphores`: USE_PER_SESSION_SEMAPHORES

### SessionHandler Dependencies
- `session_manager`: _sessions

### HealthMonitor Dependencies
- `health_path`: _health_path
- `global_sem`: _global_sem
- `provider_sems`: _provider_sems
- `session_handler`: session_handler
- `server_tools`: SERVER_TOOLS
- `host`: EXAI_WS_HOST
- `port`: EXAI_WS_PORT
- `started_at`: STARTED_AT
- `global_max_inflight`: GLOBAL_MAX_INFLIGHT
- `provider_max_inflight`: {"KIMI": KIMI_MAX_INFLIGHT, "GLM": GLM_MAX_INFLIGHT}

### serve_connection Dependencies
- `ws`: WebSocket connection
- `connection_manager`: get_connection_manager()
- `rate_limiter`: get_rate_limiter()
- `session_manager`: _sessions
- `auth_token_manager`: _auth_token_manager
- `message_handler`: request_router.handle_message
- `hello_timeout`: HELLO_TIMEOUT
- `resilient_ws_manager`: _resilient_ws

## Risk Mitigation

1. **Backup:** All changes committed to feature branch
2. **Testing:** Comprehensive testing after each step
3. **Rollback:** Can revert to previous commit if issues arise
4. **Validation:** EXAI consultation at each critical step

## Expected Outcome

- ws_server.py: 2,010 → ~500 lines (75% reduction)
- All functionality preserved
- Better code organization
- Easier maintenance and testing
- Clearer separation of concerns

## Next Steps

1. Execute Step 1: Initialize modules
2. Execute Step 2: Update connection wrapper
3. Execute Step 3: Update background tasks
4. Execute Step 4: Remove extracted functions
5. Execute Step 5: Test integration
6. Commit and push if successful

