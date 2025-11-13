# Daemon Module Cleanup Plan

## Overview
The daemon module has **37 files (15% of codebase)** and is severely bloated. This plan will reduce it to ~10 essential files.

## Files to DELETE (27 files - 73% reduction!)

### Monitoring Layer (10 files) - DELETE ALL
```
src/daemon/monitoring/
├── http_endpoints.py       (607 lines - excessive!)
├── memory_monitor.py       (332 lines)
├── websocket_handler.py    (288 lines)
├── session_monitor.py
├── session_tracker.py
├── metrics_broadcaster.py
├── health_tracker.py
├── dashboard_broadcaster.py
├── monitoring_server.py
└── http_server.py
```
**Reason:** Over-engineered monitoring. Keep only basic health endpoint.

### Middleware Layer (3 files) - DELETE ALL
```
src/daemon/middleware/
├── semaphores.py           (445 lines)
├── semaphore_tracker.py    (289 lines)
└── __init__.py
```
**Reason:** Simple semaphores don't need middleware abstraction.

### WS Subdirectory (8 files) - DELETE ALL
```
src/daemon/ws/
├── connection_manager.py   (685 lines - god class!)
├── request_router.py       (543 lines)
├── tool_executor.py        (434 lines)
├── health_monitor.py       (246 lines)
├── cache_manager.py
├── session_handler.py
├── router_utils.py
└── validators.py
```
**Reason:** Over-split. Integrate into daemon root.

### Duplicate Manager Files (6 files) - DELETE
```
src/daemon/
├── multi_user_session_manager.py (313 lines - duplicate!)
├── session_semaphore_manager.py (255 lines - duplicate!)
├── conversation_queue.py         (282 lines - can be simplified)
├── semaphore_manager.py          (312 lines - duplicate!)
└── [move other files here]
```

## Files to KEEP (10 files - 27% of current)

### Core Daemon Files
1. ✅ `ws_server.py` - **REDUCE FROM 922 TO ~300 LINES**
   - Remove monitoring imports
   - Remove middleware calls
   - Simplify to basic WebSocket handling

2. ✅ `session_manager.py` - **KEEP (296 lines)**
   - Single session manager
   - Remove duplicate functionality

3. ✅ `health_endpoint.py` - **KEEP (507 lines)**
   - Simplified health check
   - Remove monitoring bloat

4. ✅ `error_handling.py` - **KEEP (316 lines)**
   - Basic error handling

5. ✅ `input_validation.py` - **KEEP (375 lines)**
   - Essential validation

6. ✅ `env_validation.py` - **REDUCE FROM 638 TO ~200 LINES**
   - Keep only essential validation

7. ✅ `connection_manager.py` - **REDUCE FROM 685 TO ~200 LINES**
   - Remove duplicate code from ws/connection_manager.py
   - Keep only connection pooling

8. ✅ `__init__.py` - Keep

### New Simplified Structure
```
src/daemon/
├── ws_server.py              (300 lines - simplified)
├── session_manager.py        (300 lines - consolidated)
├── connection_manager.py     (200 lines - simplified)
├── health_endpoint.py        (200 lines - simplified)
├── error_handling.py         (200 lines)
├── input_validation.py       (200 lines)
├── env_validation.py         (200 lines - simplified)
├── __init__.py
└── (all monitoring/ and middleware/ DELETED)
```

## Cleanup Commands

### Step 1: Backup Current State
```bash
tar -czf daemon_backup_$(date +%Y%m%d).tar.gz src/daemon/
```

### Step 2: Delete Bloat
```bash
# Delete monitoring layer
rm -rf src/daemon/monitoring/

# Delete middleware layer
rm -rf src/daemon/middleware/

# Delete ws subdirectory
rm -rf src/daemon/ws/

# Delete duplicate managers
rm src/daemon/multi_user_session_manager.py
rm src/daemon/session_semaphore_manager.py
rm src/daemon/semaphore_manager.py
rm src/daemon/conversation_queue.py
```

### Step 3: Simplify Core Files

#### ws_server.py (922 → ~300 lines)
**Remove:**
- Line 28-49: All monitoring/middleware imports
- All PHASE comments
- Complex abstraction layers
- Import from utils.monitoring
- Import from src.monitoring.*
- Import from src.daemon.middleware.*

**Keep:**
- Basic WebSocket server setup
- Session management (via session_manager.py)
- Connection handling (via connection_manager.py)
- Simple health endpoint

#### env_validation.py (638 → ~200 lines)
**Remove:**
- Excessive validation logic
- Complex environment checking
- Monitoring integration

**Keep:**
- Essential environment variable validation
- Basic config loading

#### connection_manager.py (685 → ~200 lines)
**Remove:**
- Duplicate code from ws/connection_manager.py
- Complex connection pooling logic
- Monitoring hooks

**Keep:**
- Basic connection management
- Simple rate limiting

## After Cleanup

### Metrics Comparison
| Metric | Before | After | Reduction |
|--------|--------|-------|-----------|
| Files | 37 | 10 | 73% |
| Lines | ~10,000 | ~2,000 | 80% |
| Managers | 8+ | 2 | 75% |
| Layers | 4 | 1 | 75% |

### Benefits
✅ **Faster startup** - Load 10 files instead of 37
✅ **Lower memory** - Remove 27 files worth of classes
✅ **Easier debugging** - Less abstraction
✅ **Better performance** - Simpler code path
✅ **Maintainable** - Single session manager, not 4

## Implementation Priority

### Phase 1: Delete Bloat (1 hour)
1. Backup daemon module
2. Delete monitoring/ directory
3. Delete middleware/ directory
4. Delete ws/ directory
5. Delete duplicate managers

### Phase 2: Simplify Core (2 hours)
1. Simplify ws_server.py
2. Simplify env_validation.py
3. Simplify connection_manager.py
4. Update imports in remaining files

### Phase 3: Test (1 hour)
1. Run WebSocket shim
2. Test MCP connections
3. Verify health endpoint
4. Check for import errors

## Estimated Impact

- **Time saved:** 80% less code to read/understand
- **Memory saved:** ~5-10 MB (fewer classes loaded)
- **Startup time:** 50-70% faster (fewer imports)
- **Bug surface:** 75% smaller (fewer files to maintain)

## Bottom Line

**This cleanup will transform a 37-file over-engineered daemon into a 10-file simple, maintainable module.**

The port 3005 fix works, but fixing the bloat will make the entire system more stable and maintainable!

