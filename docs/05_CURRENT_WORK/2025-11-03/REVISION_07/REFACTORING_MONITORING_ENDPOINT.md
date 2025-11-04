# Monitoring Endpoint Refactoring Plan

**Date**: 2025-11-03
**Status**: PLANNED - Complex refactoring required
**Original File**: `src/daemon/monitoring_endpoint.py` (1,467 lines)

---

## Overview

The `monitoring_endpoint.py` file is a classic "god object" that violates the Single Responsibility Principle. It handles:
- WebSocket connection management
- HTTP request handling
- Health metrics tracking
- Event broadcasting
- Session tracking
- Dashboard serving

This refactoring will split it into focused, cohesive modules.

---

## Target Architecture

### New File Structure

```
src/daemon/monitoring/
├── __init__.py              # Package initialization
├── health_tracker.py        # Health metrics tracking (✅ Created)
├── session_tracker.py       # Session tracking (✅ Created)
├── dashboard_broadcaster.py # Event broadcasting (⏳ Pending)
├── websocket_handler.py     # WebSocket connection management (⏳ Pending)
├── http_server.py          # HTTP endpoints and file serving (⏳ Pending)
└── monitoring_server.py    # Main server orchestrator (⏳ Pending)
```

---

## Refactoring Progress

### ✅ Completed

1. **health_tracker.py** (Lines 37-129 from original)
   - `WebSocketHealthTracker` class
   - Ping/pong latency tracking
   - Connection uptime tracking
   - Reconnection event tracking
   - Timeout warning tracking
   - Metrics generation

2. **session_tracker.py** (Lines 130-249 from original)
   - `SessionTracker` class
   - Active session tracking
   - Session metrics
   - Session events

### ⏳ Pending

3. **dashboard_broadcaster.py** (Lines 365-446 from original)
   - Event broadcasting logic
   - Client connection management
   - Metrics change detection
   - Dashboard client registry

4. **websocket_handler.py** (Lines 589-790 from original)
   - WebSocket connection handling
   - Event ingestion handler
   - Message processing
   - Client lifecycle management

5. **http_server.py** (Lines 791-1416 from original)
   - Dashboard file serving
   - Status endpoints
   - Metrics endpoints
   - Health check endpoints
   - All HTTP request handlers

6. **monitoring_server.py** (Lines 1417-end from original)
   - Server startup logic
   - Route configuration
   - Broadcast setup
   - Main entry point

---

## Implementation Strategy

### Phase 1: Create New Modules (Current)
- ✅ Create `health_tracker.py`
- ✅ Create `session_tracker.py`
- ⏳ Create `dashboard_broadcaster.py`
- ⏳ Create `websocket_handler.py`
- ⏳ Create `http_server.py`
- ⏳ Create `monitoring_server.py`

### Phase 2: Update Dependencies
1. Update imports in `monitoring_endpoint.py`
2. Test each module independently
3. Verify functionality

### Phase 3: Migrate Code
1. Move broadcasting logic to `dashboard_broadcaster.py`
2. Move WebSocket handlers to `websocket_handler.py`
3. Move HTTP handlers to `http_server.py`
4. Move server startup to `monitoring_server.py`

### Phase 4: Clean Up
1. Remove migrated code from `monitoring_endpoint.py`
2. Update all imports across codebase
3. Run comprehensive tests
4. Update documentation

---

## Key Design Decisions

### 1. Separation of Concerns
- **Health Tracker**: Pure metrics tracking (no I/O)
- **Session Tracker**: Session state management
- **Broadcaster**: Event distribution (async I/O)
- **WebSocket Handler**: Connection lifecycle
- **HTTP Server**: HTTP endpoints only
- **Monitoring Server**: Orchestration

### 2. Dependency Management
- Use dependency injection for cross-module communication
- Avoid circular dependencies
- Keep modules loosely coupled

### 3. Test Strategy
- Unit tests for each module
- Integration tests for WebSocket/HTTP handlers
- End-to-end tests for full server

---

## Risk Mitigation

### Risk 1: Breaking WebSocket Connections
**Mitigation**:
- Test in development environment first
- Use feature flags for gradual rollout
- Keep old code as fallback during transition

### Risk 2: Breaking HTTP Endpoints
**Mitigation**:
- Verify all endpoints work with new structure
- Test with actual monitoring dashboard
- Validate API contracts

### Risk 3: Performance Regression
**Mitigation**:
- Benchmark current performance
- Compare with refactored version
- Monitor after deployment

---

## Estimated Effort

- **Total Time**: 5-7 hours
- **Health Tracker**: 1 hour (completed)
- **Session Tracker**: 1 hour (completed)
- **Broadcaster**: 1 hour
- **WebSocket Handler**: 1 hour
- **HTTP Server**: 1.5 hours
- **Monitoring Server**: 0.5 hours
- **Testing**: 1 hour

---

## Next Steps

1. **Create remaining modules** (dashboard_broadcaster, websocket_handler, http_server, monitoring_server)
2. **Update monitoring_endpoint.py** to use new modules
3. **Test each module** independently
4. **Run integration tests** with full system
5. **Update imports** across codebase
6. **Remove old code** from monitoring_endpoint.py
7. **Update documentation**

---

## Success Criteria

- [ ] No file > 500 lines
- [ ] Each module has single responsibility
- [ ] All tests pass
- [ ] WebSocket connections work
- [ ] HTTP endpoints respond
- [ ] Dashboard updates correctly
- [ ] Performance unchanged or improved

---

## Reference

**Original Analysis**: See `docs/05_CURRENT_WORK/2025-11-03/REVISION_07/CODE_ARCHITECTURE_ANALYSIS_AND_REFACTORING_PLAN.md`
**Issue**: God object violating Single Responsibility Principle
**Priority**: CRITICAL - Fix within 1 week
**Status**: In Progress
