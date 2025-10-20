# EXAI Direct Interaction Roadmap
**Date:** 2025-10-14  
**Status:** Analysis Complete - Implementation Pending  
**Author:** EXAI Team

---

## 🎯 Problem Statement

**User Feedback:** *"Currently you can't directly interact with EXAI without using scripts"*

### Current State
- ✅ Docker daemon running on port 8079 (WebSocket)
- ✅ Shims connect from VSCode, Claude, Auggie CLI
- ❌ **No direct interaction method** without writing Python scripts
- ❌ Requires technical knowledge: WebSocket protocol, JSON-RPC, auth tokens

### Impact on Deployment Roadmap

| Phase | Deployment | Current Limitation |
|-------|-----------|-------------------|
| **Phase 1** | Localhost (multiple apps) | Barrier for quick testing/debugging |
| **Phase 2** | LAN (other devices) | Unusable for non-technical users |
| **Phase 3** | Cloud (Supabase) | No standard API for integrations |

---

## 📊 Gap Analysis

### What's Missing?

1. **Human-Friendly Interface**
   - No web UI for chat/interaction
   - No visual dashboard for monitoring
   - No simple way to test tools

2. **Developer-Friendly Interface**
   - No REST API for HTTP clients
   - No CLI tool for command-line usage
   - No API documentation (Swagger/OpenAPI)

3. **Standard Interfaces**
   - Only WebSocket (non-standard for AI services)
   - No HTTP endpoints
   - No health/status endpoints

### Industry Standards for AI Services

Most AI/LLM services provide:
- ✅ **Web UI** - Browser-based chat interface
- ✅ **REST API** - HTTP/JSON endpoints
- ✅ **CLI Tool** - Command-line interface
- ✅ **Health Endpoints** - `/health`, `/status`, `/metrics`
- ✅ **Documentation** - API docs, examples, SDKs

**EXAI Currently Has:** WebSocket only ❌

---

## 🗺️ Prioritized Roadmap

### Phase 1: Localhost (IMMEDIATE)

#### 1. Simple Web UI ⭐ **HIGHEST PRIORITY**
**Goal:** Enable direct interaction without scripts

**Features:**
- Chat interface at `http://localhost:8080`
- Tool selection dropdown
- Real-time responses
- Session history
- Health dashboard

**Tech Stack:**
- Backend: FastAPI (Python) - lightweight, async
- Frontend: Simple HTML + JavaScript (no framework needed)
- WebSocket client to daemon (port 8079)

**Effort:** 4-6 hours  
**Value:** Solves immediate problem ✅

#### 2. Health Dashboard
**Goal:** Monitor daemon status

**Features:**
- Active sessions count
- Tool call metrics
- Provider status (Kimi, GLM)
- Recent errors
- Uptime/performance

**Endpoint:** `http://localhost:8080/health`

**Effort:** 2-3 hours  
**Value:** Debugging aid ✅

#### 3. CLI Tool (Optional)
**Goal:** Command-line interaction

**Usage:**
```bash
exai chat "Explain Docker networking"
exai debug --file app.py --issue "memory leak"
exai analyze --path src/
```

**Effort:** 3-4 hours  
**Value:** Power user tool, automation-friendly

---

### Phase 2: LAN (SOON)

#### 4. REST API Wrapper ⭐ **CRITICAL FOR LAN**
**Goal:** Standard HTTP interface for all devices

**Endpoints:**
```
POST /api/v1/chat
POST /api/v1/tools/{tool_name}
GET  /api/v1/health
GET  /api/v1/tools
```

**Why Critical:**
- Mobile devices can't run MCP shims
- Web apps need HTTP, not WebSocket
- Third-party integrations expect REST
- Language-agnostic (any HTTP client works)

**Effort:** 6-8 hours  
**Value:** Enables LAN deployment ✅

#### 5. API Documentation
**Goal:** Self-service integration

**Features:**
- Swagger/OpenAPI spec
- Interactive API explorer
- Code examples (Python, JavaScript, curl)
- Authentication guide

**Endpoint:** `http://localhost:8080/docs`

**Effort:** 2-3 hours  
**Value:** Developer experience ✅

---

### Phase 3: Cloud (FUTURE)

#### 6. Enterprise Features
- OAuth2 authentication
- API key management
- Rate limiting
- Multi-tenancy
- Usage quotas
- Audit logging
- Metrics/observability (Prometheus, Grafana)

**Effort:** 20-30 hours  
**Value:** Production-ready cloud deployment

---

## 🏗️ Proposed Architecture

### Phase 1: Web UI + Health Dashboard

```
┌─────────────────────────────────────────────────────────┐
│                    Host Machine                         │
│                                                         │
│  ┌──────────────┐                                      │
│  │   Browser    │                                      │
│  │ localhost:   │                                      │
│  │    8080      │                                      │
│  └──────┬───────┘                                      │
│         │ HTTP                                         │
│         ▼                                              │
│  ┌──────────────────────────────────────┐             │
│  │   FastAPI Web Server                 │             │
│  │   - Serves HTML/JS                   │             │
│  │   - WebSocket client to daemon       │             │
│  │   - Health dashboard                 │             │
│  │   Port: 8080                         │             │
│  └──────────────┬───────────────────────┘             │
│                 │ WebSocket                            │
│                 │ (ws://localhost:8079)                │
│                 ▼                                      │
│  ┌─────────────────────────────────────────────────┐  │
│  │         Docker Container                        │  │
│  │  ┌─────────────────────────────────────────┐   │  │
│  │  │   EXAI Daemon                           │   │  │
│  │  │   WebSocket Server                      │   │  │
│  │  │   Port: 8079                            │   │  │
│  │  └─────────────────────────────────────────┘   │  │
│  └─────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Phase 2: REST API for LAN

```
┌─────────────────────────────────────────────────────────┐
│                  LAN Network                            │
│                                                         │
│  ┌──────────────┐    ┌──────────────┐                 │
│  │   Mobile     │    │   Laptop     │                 │
│  │   Device     │    │   Browser    │                 │
│  └──────┬───────┘    └──────┬───────┘                 │
│         │ HTTP              │ HTTP                     │
│         │                   │                          │
│         └───────────┬───────┘                          │
│                     ▼                                  │
│  ┌──────────────────────────────────────┐             │
│  │   FastAPI REST API Server            │             │
│  │   - HTTP endpoints                   │             │
│  │   - WebSocket client to daemon       │             │
│  │   - Swagger docs                     │             │
│  │   Port: 8080 (exposed to LAN)        │             │
│  └──────────────┬───────────────────────┘             │
│                 │ WebSocket                            │
│                 ▼                                      │
│  ┌─────────────────────────────────────────────────┐  │
│  │         Docker Container                        │  │
│  │         EXAI Daemon (port 8079)                 │  │
│  └─────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 Immediate Next Steps

### Recommended: Start with Web UI (Phase 1)

**Why?**
1. ✅ Solves immediate problem ("can't interact directly")
2. ✅ Quick to implement (4-6 hours)
3. ✅ High value for testing/debugging
4. ✅ Foundation for Phase 2 REST API
5. ✅ Works with current Docker setup (no changes needed)

**Implementation Plan:**
1. Create `web_ui/` directory
2. Build FastAPI server with WebSocket client
3. Create simple HTML chat interface
4. Add health dashboard
5. Test with Docker daemon
6. Document usage

**Files to Create:**
- `web_ui/server.py` - FastAPI server
- `web_ui/static/index.html` - Chat interface
- `web_ui/static/health.html` - Health dashboard
- `web_ui/requirements.txt` - Dependencies (fastapi, websockets, uvicorn)
- `scripts/web_ui_start.ps1` - Startup script
- `docs/WEB_UI_GUIDE.md` - Usage documentation

---

## 📋 Decision Points

### Questions for User:

1. **Priority:** Should we implement Web UI now (Phase 1)?
   - ✅ Yes → Proceed with implementation
   - ❌ No → Continue with current Docker-only setup

2. **Scope:** What features are essential for Phase 1?
   - Chat interface (essential)
   - Health dashboard (nice-to-have)
   - CLI tool (optional)

3. **Timeline:** When do you need LAN access (Phase 2)?
   - Affects prioritization of REST API

4. **Authentication:** Should Web UI require auth token?
   - Localhost: Optional (low risk)
   - LAN: Required (security risk)

---

## 🔄 Integration with Current Setup

### No Changes Needed to Docker Setup ✅

The Web UI will:
- Run as a **separate process** (not in Docker)
- Connect to Docker daemon via WebSocket (port 8079)
- Use existing auth token (`test-token-12345`)
- Serve HTTP on port 8080

### Why Not in Docker?

**Pros of Separate Process:**
- ✅ Easier development/iteration
- ✅ Can restart UI without restarting daemon
- ✅ Simpler debugging
- ✅ No Docker rebuild needed

**Cons:**
- ❌ One more process to manage
- ❌ Not containerized (yet)

**Future:** Can containerize Web UI in Phase 2 if needed.

---

## 📊 Summary

| Component | Phase 1 | Phase 2 | Phase 3 |
|-----------|---------|---------|---------|
| **Docker Daemon** | ✅ Done | ✅ Done | Enhance |
| **Web UI** | 🔨 Build | Enhance | Enhance |
| **REST API** | - | 🔨 Build | Enhance |
| **CLI Tool** | Optional | Optional | Enhance |
| **Health Dashboard** | 🔨 Build | Enhance | Enhance |
| **API Docs** | - | 🔨 Build | Enhance |
| **Auth/Multi-tenancy** | - | - | 🔨 Build |

**Legend:**
- ✅ Done
- 🔨 Build
- Enhance = Add features

---

## 🚀 Ready to Proceed?

**Recommendation:** Implement Web UI now (4-6 hours) to enable direct interaction.

**Next Steps:**
1. Get user approval
2. Create Web UI implementation plan
3. Build and test
4. Document usage
5. Move to Phase 2 (REST API for LAN)

