# Current System Architecture Overview

> **Version:** 2.0 (Current Implementation)
> **Last Updated:** 2025-11-16
> **Status:** ✅ **Current - Container-Based Architecture**

---

## 🎯 Executive Summary

The EX-AI MCP Server is a production-ready, container-based AI orchestration system that provides AI-powered tools through the Model Context Protocol (MCP). It features a modern 4-container architecture with zai-sdk integration, intelligent routing, and comprehensive monitoring.

### Key Architecture Highlights:
- **Container-Native**: 4-container Docker Compose deployment
- **Port Strategy**: 3010, 3001-3003 (avoiding Orchestrator conflicts)  
- **Modern SDK Integration**: zai-sdk for GLM, OpenAI SDK for Kimi
- **Non-China Compliance**: All base URLs verified non-China based
- **Production-Ready**: Health monitoring, circuit breakers, graceful degradation

---

## 🏗️ Current Container Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                             │
│  (Claude Code, VSCode Extension, Custom Applications)          │
│                          │                                       │
│                   ┌──────▼──────┐                                │
│                   │  .mcp.json  │                                │
│                   │ (Config)    │                                │
│                   └──────┬──────┘                                │
└──────────────────────────┼────────────────────────────────────────┘
                           │ MCP stdio Protocol
┌──────────────────────────▼────────────────────────────────────────┐
│                    CONTAINER INFRASTRUCTURE                    │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              DOCKER COMPOSE NETWORK                   │  │
│  │                                                         │  │
│  │  ┌──────────────┐  ┌──────────────┐                 │  │
│  │  │   CLIENT    │  │   CONTAINER │                 │  │
│  │  │ APPLICATIONS│  │  NETWORK   │                 │  │
│  │  │             │  │             │                 │  │
│  │  │ • Claude   │◄─┤ • Port     │                 │  │
│  │  │   Code     │  │   Mapping  │                 │  │
│  │  │ • VSCode   │  │ • Service  │                 │  │
│  │  │ • Custom   │  │   Discovery│                 │  │
│  │  │   Apps     │  │             │                 │  │
│  │  └──────────────┘  └──────────────┘                 │  │
│  └─────────────────────────────┬───────────────────────┘  │
│                              │                           │
│  ┌───────────────────────────▼───────────────────────┐  │
│  │            CONTAINER SERVICES (4 Containers)         │  │
│  │                                                       │  │
│  │  ┌─────────────────┐  ┌─────────────────┐           │  │
│  │  │ exai-mcp-server│  │  exai-mcp-stdio │           │  │
│  │  │                 │  │                 │           │  │
│  │  │ • Port 3010    │  │ • Port 8079    │           │  │
│  │  │ • WebSocket    │  │ • stdio MCP    │           │  │
│  │  │ • Port 3001   │  │ • Tool         │           │  │
│  │  │ • Monitoring  │  │   Execution   │           │  │
│  │  │ • Port 3002   │  │                 │           │  │
│  │  │ • Health      │  │                 │           │  │
│  │  │ • Port 3003   │  │                 │           │  │
│  │  │ • Metrics     │  │                 │           │  │
│  │  └───────┬───────┘  └─────────┬─────┘           │  │
│  │          │                    │                   │  │
│  │  ┌───────▼────────────────┴──────┐           │  │
│  │  │         REDIS SERVICES          │           │  │
│  │  │                               │           │  │
│  │  │  ┌─────────────────┐  ┌───────┐ │           │  │
│  │  │  │  exai-redis    │  │ exai- │ │           │  │
│  │  │  │                │  │ redis │ │           │  │
│  │  │  │ • Port 6379   │  │ cmd   │ │           │  │
│  │  │  │ • Session     │  │       │ │           │  │
│  │  │  │   Storage    │  │ • Port│ │           │  │
│  │  │  │ • Cache      │  │   8081│ │           │  │
│  │  │  │ • Queue      │  │ • Web │ │           │  │
│  │  │  │   Management │  │   UI  │ │           │  │
│  │  │  └──────┬───────┘  └───────┘ │           │  │
│  │  └─────────┬─────────────────────┘           │  │
│  └────────────┼───────────────────────────────┘  │
│               │                                   │
│  ┌───────────▼───────────────────────────────────┐  │
│  │               EXTERNAL APIS                    │  │
│  │                                               │  │
│  │  ┌──────────┐  ┌──────────┐  ┌───────┐ │  │
│  │  │   Z.ai   │  │ Moonshot │  │ Mini  │ │  │
│  │  │  (GLM)   │  │  (Kimi) │  │  Max  │ │  │
│  │  │           │  │           │  │       │ │  │
│  │  │ • zai-    │  │ • OpenAI │  │ • Ant  │ │  │
│  │  │   sdk     │  │   SDK    │  │ hropic │ │  │
│  │  │ • 200K    │  │ • 256K   │  │ • Claude│ │  │
│  │  │   context│  │   context│  │ • API  │ │  │
│  │  │ • Non-    │  │ • Non-    │  │ • Non- │ │  │
│  │  │   China   │  │   China   │  │ China │ │  │
│  │  └─────┬──────┘  └─────┬────┘  └─┬───┘ │  │
│  └─────────┼──────────────────┼────────┼──────┘  │
│            │                  │        │         │
│            └──────────────────┴────────┘         │
└───────────────────────────────────────────────┘
```

---

## 🔧 Current Container Configuration

### Container Details
```
exai-mcp-server:
  - Purpose: Main MCP server with WebSocket daemon
  - Ports: 3010 (WebSocket), 3001 (monitoring), 3002 (health), 3003 (metrics)
  - Image: exai-mcp-server:latest (built from local Dockerfile)

exai-mcp-stdio:
  - Purpose: stdio MCP server for direct tool execution
  - Port: 8079 (internal)
  - Shares same image as exai-mcp-server

exai-redis:
  - Purpose: Session storage, caching, queue management
  - Port: 6379 (Redis protocol)
  - Image: redis:7-alpine

exai-redis-commander:
  - Purpose: Web-based Redis management UI
  - Port: 8081 (HTTP web interface)
  - Image: rediscommander/redis-commander:latest
```

### Port Mapping Strategy
```
Host:Container Mappings:
- 3010:8079  → WebSocket daemon (MCP protocol)
- 3001:8080  → Monitoring dashboard
- 3002:8082  → Health check endpoint  
- 3003:8000  → Prometheus metrics
- 6379:6379   → Redis session storage
- 8081:8081   → Redis Commander UI
```

---

## 🔌 Data Flow

### MCP Tool Execution Flow
```
Client Request
    ↓
MCP stdio/WebSocket
    ↓
exai-mcp-stdio (Port 8079)
    ↓
Tool Registry & Validation
    ↓
Provider Selection (GLM/Kimi/MiniMax)
    ↓
External API Call (zai-sdk/OpenAI SDK/Anthropic)
    ↓
Redis Session Management
    ↓
Response to Client
```

### Port Communication
```
Client → Port 3010 → exai-mcp-server (WebSocket)
Client → Port 8079 → exai-mcp-stdio (stdio)
Monitoring → Port 3001 → Dashboard
Health Check → Port 3002 → Status
Metrics → Port 3003 → Prometheus
Redis UI → Port 8081 → Web Interface
```

---

## 📊 Provider Integration

### GLM (Z.ai) - Primary Provider
- **SDK**: zai-sdk==0.0.4
- **Base URL**: https://api.z.ai/api/paas/v4 (Non-China)
- **Model**: glm-4.6 (200K context)
- **Features**: Chat, files, images, web search, tools

### Kimi (Moonshot AI) - Secondary Provider  
- **SDK**: OpenAI-compatible SDK
- **Base URL**: https://api.moonshot.ai/v1 (Non-China)
- **Model**: kimi-k2-thinking-turbo (256K context)
- **Features**: Chat, images, thinking mode

### MiniMax - Tertiary Provider
- **SDK**: Anthropic SDK
- **Base URL**: https://api.minimax.ai (Non-China)  
- **Features**: Chat, reasoning, tool calling

---

## 🛡️ Security & Compliance

### Non-China Compliance ✅
- All API endpoints verified non-China based
- No dependencies on China-based services
- zai-sdk provides official non-China access to GLM models

### Authentication
- Environment-based API key management
- JWT token support for client sessions
- Redis-backed session management

### Network Security
- Container isolation
- Internal service communication
- External API encryption (HTTPS/TLS)

---

## 📈 Monitoring & Observability

### Health Monitoring
- **Port 3002**: HTTP health check endpoint
- **Port 3001**: Real-time monitoring dashboard
- Container health checks via Docker

### Metrics
- **Port 3003**: Prometheus metrics endpoint
- Request/response tracking
- Provider performance metrics
- Error rate monitoring

### Logging
- Structured logging with timestamps
- Provider-specific error categorization
- Performance timing tracking

---

## 🚀 Deployment

### Current Status
```bash
# All containers running and healthy
NAME                   STATUS       HEALTH
exai-mcp-server        Up 4min      healthy
exai-mcp-stdio         Up 4min      healthy  
exai-redis             Up 5min      healthy
exai-redis-commander   Up 4min      healthy
```

### Build Process
```bash
# Clean rebuild with latest changes
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

## 🔄 Recent Updates (2025-11-16)

### zai-sdk Migration
- ✅ Migrated from zhipuai to zai-sdk==0.0.4
- ✅ Removed all legacy zhipu dependencies
- ✅ Updated all environment variables and documentation

### Container Optimization
- ✅ Port strategy updated to avoid Orchestrator conflicts
- ✅ Non-China base URLs confirmed for all providers
- ✅ Build optimization with --no-cache rebuilds

### Documentation Alignment
- ✅ Architecture docs updated to reflect current system
- ✅ Provider API docs updated with accurate model specs
- ✅ Integration guides updated for container deployment

---

## 📚 References

- **Container Configuration**: `docker-compose.yml`
- **SDK Architecture**: `docs/architecture/SDK_ARCHITECTURE_FINAL.md`
- **Provider APIs**: `docs/api/provider-apis/`
- **Operations Guide**: `docs/operations/`

**Last Updated**: 2025-11-16 (Container architecture current)
