# Service Split Architecture Proposal

## Executive Summary

This document explores splitting the EX-AI MCP Server into a **tiny persistent service** (API clients, rate-limiter, caches) and **transport-only layers** (stdio, WebSocket, CLI). This would eliminate the current singleton race conditions and provide better resource management.

---

## Current Architecture (Monolithic)

```
┌─────────────────────────────────────────────────────────────┐
│                    Process Boundary                          │
│                                                              │
│  ┌──────────────┐              ┌──────────────┐            │
│  │  server.py   │              │ ws_server.py │            │
│  │   (stdio)    │              │ (WebSocket)  │            │
│  └──────┬───────┘              └──────┬───────┘            │
│         │                              │                     │
│         └──────────┬───────────────────┘                     │
│                    │                                         │
│         ┌──────────▼──────────┐                             │
│         │  Shared Singletons  │                             │
│         │  - Providers        │                             │
│         │  - Tool Registry    │                             │
│         │  - API Clients      │                             │
│         └─────────────────────┘                             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Problems:**
- Both entry points can race to initialize singletons
- No process isolation between transports
- Difficult to restart one transport without affecting the other
- Resource leaks if one transport crashes

---

## Proposed Architecture (Micro-Service)

```
┌─────────────────────────────────────────────────────────────┐
│              Persistent Service (Always Running)             │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Core Service (HTTP/gRPC API)                        │  │
│  │  - Provider Registry (Kimi, GLM clients)             │  │
│  │  - Tool Registry                                     │  │
│  │  - Rate Limiter (global, per-provider)               │  │
│  │  - Conversation Cache (Kimi cache tokens)            │  │
│  │  - Result Cache (deduplication)                      │  │
│  │  - Health Monitoring                                 │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└──────────────────────┬───────────────────────────────────────┘
                       │ HTTP/gRPC
         ┌─────────────┼─────────────┐
         │             │             │
┌────────▼────┐  ┌────▼─────┐  ┌───▼──────┐
│ stdio shim  │  │ WS shim  │  │ CLI shim │
│ (MCP stdio) │  │ (MCP WS) │  │ (direct) │
└─────────────┘  └──────────┘  └──────────┘
```

**Benefits:**
- Single source of truth for all state
- Transports are stateless and can crash/restart independently
- Better resource management (connection pooling, rate limiting)
- Easier to add new transports (HTTP REST, gRPC, etc.)

---

## Component Breakdown

### Persistent Service Components

| Component | Responsibility | Current Location |
|-----------|---------------|------------------|
| **Provider Registry** | Manage Kimi/GLM API clients, credentials | `src/providers/registry.py` |
| **Tool Registry** | Discover and instantiate tools | `tools/registry.py` |
| **Rate Limiter** | Global and per-provider concurrency limits | `src/daemon/ws_server.py` (semaphores) |
| **Conversation Cache** | Kimi cache tokens, conversation history | `src/conversation/` |
| **Result Cache** | Deduplicate identical requests | `src/daemon/ws_server.py` (_results_cache) |
| **Health Monitor** | Track service health, metrics | `src/daemon/ws_server.py` (_health_writer) |

### Transport Shim Components

| Component | Responsibility | Current Location |
|-----------|---------------|------------------|
| **stdio Shim** | MCP stdio protocol → Service API | `server.py` |
| **WebSocket Shim** | MCP WebSocket protocol → Service API | `src/daemon/ws_server.py` |
| **CLI Shim** | Direct CLI → Service API | (new) |

---

## Pros / Cons / Effort Analysis

### Pros ✅

| Benefit | Impact | Priority |
|---------|--------|----------|
| **Eliminates singleton races** | High - No more inter-process initialization conflicts | 🔥 Critical |
| **Better resource management** | High - Connection pooling, shared rate limiting | 🔥 Critical |
| **Independent transport restarts** | Medium - Can restart stdio without affecting WebSocket | ⚠️ Important |
| **Easier to add new transports** | Medium - HTTP REST, gRPC, etc. | ℹ️ Nice-to-have |
| **Centralized monitoring** | Medium - Single health endpoint for all transports | ℹ️ Nice-to-have |
| **Better testing** | Medium - Can test service independently of transports | ℹ️ Nice-to-have |

### Cons ❌

| Drawback | Impact | Mitigation |
|----------|--------|------------|
| **Additional network hop** | Low - Local HTTP/gRPC is fast (~1ms) | Use Unix sockets or shared memory |
| **More complex deployment** | Medium - Need to manage service lifecycle | Systemd/Docker/PM2 for auto-restart |
| **Debugging complexity** | Low - Need to trace across process boundaries | Structured logging with request IDs |
| **Initial development effort** | High - Significant refactoring required | Incremental migration path |

### Effort Estimation

| Phase | Tasks | Estimated Effort |
|-------|-------|------------------|
| **Phase 1: Service Core** | Extract provider registry, tool registry, caches into standalone service | 2-3 days |
| **Phase 2: API Design** | Design HTTP/gRPC API for tool execution, health checks | 1 day |
| **Phase 3: stdio Shim** | Refactor `server.py` to call service API instead of direct execution | 1-2 days |
| **Phase 4: WebSocket Shim** | Refactor `ws_server.py` to call service API instead of direct execution | 1-2 days |
| **Phase 5: Testing & Migration** | Integration tests, gradual rollout, monitoring | 2-3 days |
| **Total** | | **7-11 days** |

---

## Migration Path (Incremental)

### Step 1: Extract Core Service (No Breaking Changes)
- Create `src/service/core.py` with HTTP API
- Keep existing `server.py` and `ws_server.py` unchanged
- Run service in background, but don't use it yet

### Step 2: Migrate WebSocket First (Lower Risk)
- Update `ws_server.py` to call service API
- Keep `server.py` unchanged (stdio still works)
- Monitor for issues, rollback if needed

### Step 3: Migrate stdio (Complete Migration)
- Update `server.py` to call service API
- Both transports now use service
- Remove duplicate singleton code

### Step 4: Cleanup & Optimize
- Remove unused code from transport shims
- Optimize service API for performance
- Add monitoring and alerting

---

## API Design Sketch

### HTTP API Endpoints

```
POST /api/v1/tools/execute
{
  "tool_name": "chat",
  "arguments": {...},
  "request_id": "uuid",
  "session_id": "uuid"
}

Response:
{
  "outputs": [...],
  "duration_ms": 1234,
  "provider": "kimi",
  "cached": false
}

GET /api/v1/tools/list
Response:
{
  "tools": [
    {"name": "chat", "description": "...", "inputSchema": {...}},
    ...
  ]
}

GET /api/v1/health
Response:
{
  "status": "healthy",
  "uptime_seconds": 12345,
  "tool_count": 42,
  "active_sessions": 5,
  "provider_status": {
    "kimi": "healthy",
    "glm": "healthy"
  }
}
```

---

## Decision Framework

### When to Build This?

**Build Now If:**
- ✅ Singleton races are causing production issues
- ✅ Need to support multiple transports (HTTP REST, gRPC)
- ✅ Resource management is a bottleneck (connection pooling, rate limiting)
- ✅ Team has 1-2 weeks for focused refactoring

**Defer If:**
- ❌ Current singleton solution (Mission 1) is working well
- ❌ Only need stdio and WebSocket transports
- ❌ Resource management is not a concern
- ❌ Team is focused on feature development

### Recommended Decision: **Defer for Now**

**Rationale:**
1. Mission 1 (bootstrap singletons) solves the immediate race condition problem
2. Current architecture is simpler and easier to maintain
3. No immediate need for additional transports
4. Can revisit if requirements change (e.g., need HTTP REST API)

---

## Conclusion

The micro-service architecture provides significant benefits for **scalability**, **reliability**, and **maintainability**, but requires **7-11 days of focused effort**. 

**Recommendation:** Implement Mission 1 (bootstrap singletons) first to solve the immediate singleton race problem. Revisit this micro-service architecture if:
- Production issues arise from shared state
- Need to support additional transports (HTTP REST, gRPC)
- Resource management becomes a bottleneck

The incremental migration path ensures we can adopt this architecture gradually without breaking existing functionality.

