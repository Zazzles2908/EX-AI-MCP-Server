# Architecture Documentation
**System design, patterns, and architectural decisions**

**Last Updated:** 2025-10-17
**Analysis Date:** 2025-10-17
**Analyzed By:** EXAI Architectural Analysis (Kimi K2-0905-preview)

---

## 📚 Contents

### Core Documents

- **`DEPENDENCY_MAP.md`** - Complete dependency graph and module relationships
- **`DESIGN_INTENT.md`** - Design philosophy and architectural principles
- **`SYSTEM_ARCHITECTURE.md`** - Comprehensive system architecture analysis (this document)

---

## 🏗️ Architecture Overview

The EX-AI MCP Server follows a **multi-layer modular architecture** with intelligent routing, semantic caching, and production-ready concurrency control.

### **System Layers**

1. **WebSocket Daemon Layer** (`src/daemon/ws_server.py`)
   - Connection management and authentication
   - Session lifecycle management
   - Semantic request coalescing
   - 3-tier concurrency control (Global: 24, Kimi: 6, GLM: 4, Session: 8)
   - Request deduplication across reconnects

2. **MCP Server Layer** (`server.py`)
   - MCP protocol compliance
   - Tool discovery and registration
   - Provider configuration

3. **Request Handler Layer** (`src/server/handlers/request_handler.py`)
   - Thin orchestrator pattern (93% code reduction: 1,345 → 95 lines)
   - Context reconstruction from continuation_id
   - Model resolution and validation
   - Tool execution orchestration

4. **Routing Layer** (`src/router/service.py`)
   - Intelligent model selection (auto routing)
   - Cost-aware routing with caching (3min TTL)
   - Provider priority ordering (Kimi → GLM → Custom → OpenRouter)
   - Agentic routing hints support

5. **Tool Execution Layer** (`tools/`)
   - Simple tools (chat, status, health)
   - Workflow tools (debug, analyze, thinkdeep, consensus, etc.)
   - Provider-specific tools

6. **Provider Layer** (`src/providers/`)
   - Kimi (Moonshot) integration
   - GLM (ZhipuAI) integration
   - Health-wrapped providers for monitoring
   - Model capability management

7. **Storage Layer**
   - Redis for conversation persistence
   - Multi-layer caching (L1: TTLCache, L2: Redis, L3: planned)
   - Supabase integration (planned/partial)

---

## 🎯 Key Architectural Patterns

### **1. Semantic Request Coalescing**
- Deduplicates requests by `call_key` (tool name + normalized arguments)
- Prevents duplicate work across reconnects
- Fast-fail duplicate requests with 409-style response
- TTL-based cleanup (default: 180s)

### **2. Multi-Tier Concurrency Control**
```
Global Semaphore (24)
├── Provider Semaphores
│   ├── Kimi (6 concurrent)
│   └── GLM (4 concurrent)
└── Session Semaphores (8 per session)
```

### **3. Thin Orchestrator Pattern**
- Request handler delegates to 7 specialized helper modules
- Clean separation of concerns
- 93% code reduction through modularization

### **4. Intelligent Routing**
- Manager-first architecture (GLM-4.5-flash for routing decisions)
- Cost-aware model selection
- Routing cache (3min TTL) for performance
- Fallback mechanisms for unavailable models

### **5. Health-Wrapped Providers**
- Automatic health monitoring
- Circuit breaker pattern (planned)
- Provider availability tracking

---

## 🐳 Docker Deployment Architecture

### **Container Structure**
```yaml
services:
  exai-daemon:
    - Python 3.13-slim base
    - Multi-stage build (builder + runtime)
    - Resource limits: 2 CPU, 2GB RAM
    - File descriptors: 4096 soft, 8192 hard
    - Health check: 30s interval, 60s start period

  redis:
    - Redis 7-alpine
    - 4GB memory limit
    - Persistence enabled (AOF + RDB)
    - Health check: redis-cli ping

  redis-commander:
    - Web UI for Redis monitoring
    - Port 8081
```

### **Volume Mounts**
- `./logs:/app/logs` - Log persistence
- `redis-data:/data` - Redis persistence
- `.env.docker` → `/app/.env` - Environment configuration

---

## 🔒 Security Architecture

### **Authentication**
- Thread-safe token manager with rotation support
- Token validation on every WebSocket connection
- Audit logging for auth events
- Graceful handling of unauthorized connections

### **Input Validation**
- **Layer 1:** WebSocket message structure validation
- **Layer 2:** SecureInputValidator for path containment
- **Layer 3:** File size validation (32MB max message)
- **Layer 4:** Cross-platform path normalization and security

### **Security Controls**
- Environment-based external path allowlist (`EX_ALLOW_EXTERNAL_PATHS`)
- Repository root containment by default
- Image count/size validation
- Session limits (max 100 concurrent sessions)

---

## 📊 Performance Characteristics

### **Concurrency Limits**
| Level | Limit | Purpose |
|-------|-------|---------|
| Global | 24 | Total concurrent requests across all sessions |
| Kimi Provider | 6 | Prevent Kimi API rate limiting |
| GLM Provider | 4 | Prevent GLM API rate limiting |
| Per Session | 8 | Fair resource allocation per client |

### **Caching Strategy**
| Layer | Technology | TTL | Purpose |
|-------|-----------|-----|---------|
| L1 | TTLCache (in-memory) | Varies | <1ms access, fastest |
| L2 | Redis | Varies | 1-5ms access, persistent across restarts |
| L3 | Planned | N/A | 10-50ms access, long-term storage |
| Routing Cache | In-memory | 3min | Model selection optimization |
| Results Cache | In-memory + Redis | 600s | Request deduplication |

### **Timeout Configuration**
- HTTP Client: 30s
- Tool Execution: 180s (3min)
- Daemon Call: 270s (4.5min = 1.5x tool timeout)
- Hello Handshake: 15s
- WebSocket Ping: 45s interval, 30s timeout

---

---

## 📋 Comprehensive Analysis

### **SYSTEM_ARCHITECTURE_ANALYSIS.md** (2025-10-17)

**Complete architectural analysis including:**
- ✅ System architecture flow and request pipeline
- ✅ Scalability and performance analysis
- ✅ Security posture assessment
- ✅ Maintainability evaluation
- ✅ Docker deployment analysis
- ✅ Critical recommendations (P0, P1, P2)
- ✅ Effectiveness improvements
- ✅ Production readiness assessment

**Key Findings:**
- **Overall Rating:** 8.5/10 (Production-ready for single-instance deployment)
- **Strengths:** Excellent concurrency control, semantic caching, clean modular design
- **Areas for Improvement:** Horizontal scaling, rate limiting, Redis authentication
- **Immediate Actions:** Add rate limiting, enable Redis auth, move file validation earlier

[Read Full Analysis →](./SYSTEM_ARCHITECTURE_ANALYSIS.md)

---

## 🔗 Related Documentation

- **API Reference:** `../03_API_REFERENCE/`
- **System Reference:** `../system-reference/`
- **Current Work:** `../05_CURRENT_WORK/`

---

**Last Updated:** 2025-10-14

