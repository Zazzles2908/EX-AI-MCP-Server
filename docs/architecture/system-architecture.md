# System Architecture Overview

> **Version:** 1.0.0
> **Last Updated:** 2025-11-10
> **Status:** ✅ **Complete**

---

## 🎯 Executive Summary

The EX-AI MCP Server is a production-ready, intelligent routing system that provides AI-powered tools through the Model Context Protocol (MCP). It features a modular architecture with GLM-4.6 and Kimi K2 model integration, Supabase for persistent storage, and WebSocket for real-time communication.

### Key Architecture Highlights:
- **Modular Design**: Thin orchestrator pattern with 13 specialized modules
- **86% Code Reduction**: From 1,398 lines to lean, maintainable code
- **Intelligent Routing**: AI-powered provider selection (GLM ↔ Kimi)
- **Security-First**: JWT authentication, RLS policies, environment-based secrets
- **Production-Ready**: Health monitoring, circuit breakers, graceful degradation

---

## 🏗️ High-Level Architecture

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
                           │ MCP Protocol
                           │ (WebSocket/stdio)
┌──────────────────────────▼────────────────────────────────────────┐
│                    EX-AI MCP SERVER                              │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              WEBSOCKET DAEMON (Port 3000)                 │  │
│  │                                                          │  │
│  │  • Request routing and load balancing                    │  │
│  │  • Session management                                    │  │
│  │  • Health monitoring                                     │  │
│  │  • Circuit breakers                                      │  │
│  └──────────────┬───────────────────────────────────────────┘  │
│                 │                                                  │
│  ┌──────────────▼───────────────────────────────────────────┐  │
│  │                  MCP TOOLS LAYER                          │  │
│  │                                                          │  │
│  │  29 MCP Tools:                                           │  │
│  │  • Chat & Listmodels (Simple)                            │  │
│  │  • Analyze, Codereview, Debug (Workflow)                 │  │
│  │  • Provider-specific tools                               │  │
│  │  • Orchestrated execution                                │  │
│  └──────────────┬───────────────────────────────────────────┘  │
│                 │                                                  │
│  ┌──────────────▼───────────────────────────────────────────┐  │
│  │              INTELLIGENT ROUTER                          │  │
│  │                                                          │  │
│  │  GLM-4.6 AI Manager:                                    │  │
│  │  • Task classification                                   │  │
│  │  • Provider selection                                    │  │
│  │  • Cost optimization                                     │  │
│  │  • Fallback management                                   │  │
│  └──────────────┬───────────────────────────────────────────┘  │
│                 │                                                  │
│  ┌──────────────▼───────────────────────────────────────────┐  │
│  │              PROVIDER ABSTRACTION LAYER                   │  │
│  │                                                          │  │
│  │  ┌──────────┐          ┌──────────┐                      │  │
│  │  │   GLM    │          │   Kimi   │                      │  │
│  │  │ Provider │          │ Provider │                      │  │
│  │  │          │          │          │                      │  │
│  │  │ • Web    │          │ • File   │                      │  │
│  │  │   Search │          │   Upload │                      │  │
│  │  │ • Chat   │          │ • Analyze│                      │  │
│  │  │ • Code   │          │ • Think  │                      │  │
│  │  └────┬─────┘          └────┬─────┘                      │  │
│  │       │                      │                            │  │
│  └───────┼──────────────────────┼────────────────────────────┘  │
│          │                      │                                │
│          └──────────┬───────────┘                                │
│                     │                                              │
└─────────────────────▼──────────────────────────────────────────────┘
                      │
                      │ REST API
                      │
┌─────────────────────▼──────────────────────────────────────────────┐
│                     DATA LAYER                                     │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │               SUPABASE DATABASE                            │  │
│  │                                                          │  │
│  │  18 Tables:                                              │  │
│  │  • conversations, messages                               │  │
│  │  • provider_file_uploads, file_id_mappings               │  │
│  │  • audit_logs, file_operations, file_metadata           │  │
│  │  • user_quotas, monitoring.metrics_raw                  │  │
│  │                                                          │  │
│  │  78 Indexes + 20 RLS Policies                           │  │
│  └──────────────┬───────────────────────────────────────────┘  │
│                 │                                                  │
│  ┌──────────────▼───────────────────────────────────────────┐  │
│  │               SUPABASE STORAGE                            │  │
│  │                                                          │  │
│  │  3 Buckets:                                              │  │
│  │  • user-files (user uploads)                            │  │
│  │  • results (generated results)                          │  │
│  │  • generated-files (AI outputs)                         │  │
│  └──────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Request Flow

### 1. Client Request
```
Client → .mcp.json → WebSocket Connection (port 3000)
```

### 2. Tool Orchestration
```
WebSocket Daemon → Tool Registry → Request Handler → Router
```

### 3. Provider Routing
```
Router → GLM-4.6 AI Manager → Task Classification → Provider Selection
                                     ↓
                    ┌────────────────┴───────────────┐
                    │                               │
            ┌───────▼───────┐             ┌────────▼────────┐
            │  GLM Provider │             │ Kimi Provider  │
            │               │             │                │
            │ • Web Search  │             │ • File Upload  │
            │ • Chat        │             │ • Analysis     │
            │ • Code        │             │ • Think        │
            └───────┬───────┘             └────────┬───────┘
                    │                               │
                    └───────────────┬───────────────┘
                                    │
                                    ▼
                            Provider Response
```

### 4. Data Persistence
```
Response → Database Insert (if needed) → Storage (if file) → Client
```

---

## 🧩 Core Components

### 1. WebSocket Daemon
**File:** `src/daemon/ws/daemon.py`
- **Purpose**: Main entry point, handles all MCP communications
- **Port**: 3000 (maps to container 8079)
- **Features**:
  - Session management
  - Health monitoring (writes to `logs/ws_daemon.health.json`)
  - Circuit breaker pattern
  - Rate limiting
  - Load balancing

### 2. Request Handler (Refactored)
**File:** `src/server/handlers/request_handler.py`
- **Before**: 1,345 lines (monolithic)
- **After**: 160 lines (thin orchestrator)
- **Modules**:
  - `request_handler_init.py` - Initialization & tool registry
  - `request_handler_routing.py` - Tool routing & aliasing
  - `request_handler_model_resolution.py` - Auto routing & model validation
  - `request_handler_context.py` - Context reconstruction
  - `request_handler_monitoring.py` - Execution monitoring
  - `request_handler_execution.py` - Tool execution
  - `request_handler_post_processing.py` - Post-processing

### 3. Provider Configuration (Refactored)
**File:** `src/server/providers/provider_config.py`
- **Before**: 290 lines (mixed concerns)
- **After**: 77 lines (thin orchestrator)
- **Modules**:
  - `provider_detection.py` - Provider detection & validation
  - `provider_registration.py` - Provider registration
  - `provider_diagnostics.py` - Logging & diagnostics
  - `provider_restrictions.py` - Model restrictions

### 4. Intelligent Router
**File:** `src/providers/capability_router.py`
- **Purpose**: AI-powered provider selection
- **Model**: GLM-4.6 (default)
- **Logic**:
  - Task classification
  - Provider capability matching
  - Cost optimization
  - Fallback chain management

### 5. Database Layer
**File:** `src/storage/hybrid_supabase_manager.py`
- **Purpose**: Unified database and storage access
- **Features**:
  - Connection pooling
  - Transaction management
  - RLS policy enforcement
  - File upload/download
  - Metrics collection

---

## 🔌 Provider Integration

### GLM Provider (ZhipuAI)
**Files:**
- `src/providers/glm_provider.py`
- `src/providers/async_glm.py`
- `src/providers/glm_config.py`

**Capabilities:**
- Web search (native)
- Text generation
- Code analysis
- Reasoning
- Streaming support

**Models:**
- `glm-4.5-flash` (default, fast)
- `glm-4.6` (quality, thinking mode)
- `glm-4.5-air` (balanced)
- `glm-4.5v` (vision)

**Configuration:**
```env
GLM_API_KEY=your_api_key_here
GLM_BASE_URL=https://api.z.ai/api/paas/v4
GLM_DEFAULT_MODEL=glm-4.5-flash
```

### Kimi Provider (Moonshot AI)
**Files:**
- `src/providers/kimi_chat.py`
- `src/providers/async_kimi_chat.py`
- `src/providers/kimi_config.py`

**Capabilities:**
- File processing (20MB)
- Multi-format support
- Document analysis
- Thinking mode
- Context caching

**Models:**
- `kimi-k2-0905-preview` (default, balanced)
- `kimi-k2-turbo-preview` (fast)
- `kimi-thinking-preview` (extended reasoning)
- `kimi-k2-0711-preview` (quality)

**Configuration:**
```env
KIMI_API_KEY=your_api_key_here
KIMI_BASE_URL=https://api.moonshot.ai/v1
KIMI_DEFAULT_MODEL=kimi-k2-0905-preview
```

---

## 💾 Database Architecture

### Schema Overview (18 Tables)
```
conversations          → Conversation threads
messages              → Message history
conversation_files    → File associations
provider_file_uploads → Upload tracking (by provider)
file_id_mappings      → Cross-provider file mapping
audit_logs           → Security audit trail
file_operations      → File operation log
file_metadata        → File metadata
user_quotas         → Storage quotas (10GB/user)
monitoring.metrics_raw → System metrics
```

### Indexes (78 Total)
- Conversation queries: `conversation_id`, `role_created_at`
- File operations: `user_id`, `file_id`, `timestamp`
- Provider uploads: `provider`, `timestamp`, `file_hash`
- Audit logs: `action`, `timestamp`, `user_id`

### RLS Policies (20 Total)
- **User Isolation**: Users can only access their own data
- **Service Role**: Full access for server operations
- **Anonymous**: No access to any data

### Storage Buckets (3)
- `user-files`: User uploaded files
- `results`: Generated results
- `generated-files`: AI-generated outputs

---

## 🔐 Security Architecture

### Authentication Flow
```
Client Request → JWT Validation → RLS Check → Operation Allowed
                            ↓
                    Supabase Service Role
                    (Server-side operations)
```

### Security Measures
1. **Environment Variables**: All secrets in `.env`, never in code
2. **JWT Authentication**: HS256 algorithm with 64-char secret
3. **RLS Policies**: Database-level access control
4. **Input Validation**: All inputs sanitized
5. **Rate Limiting**: Per-user, per-IP, global limits
6. **Circuit Breakers**: Automatic failover on failures
7. **Audit Logging**: All security events logged

### Configuration Files
- **`.mcp.json`**: MCP server configuration (no hardcoded secrets)
- **`.env`**: Environment variables (supabase keys, API keys)
- **`src/config/settings.py`**: Centralized configuration

---

## 📊 Monitoring & Observability

### Health Monitoring
- **Health File**: `logs/ws_daemon.health.json`
- **Metrics**: Provider success rates, response times
- **Diagnostics**: Structured logging with timestamps
- **Alerts**: Circuit breaker activation, provider failures

### Performance Metrics
- Request latency
- Provider response times
- Success/failure rates
- Active sessions
- Global capacity
- Token usage

### Logging
- **Location**: `.logs/` directory (JSONL format)
- **Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Structured**: Machine-readable JSON
- **Context**: Request ID, session ID, user ID

---

## 🚀 Deployment Architecture

### Docker Composition
```yaml
exai-mcp-daemon:      # Main MCP server
exai-redis:           # Session storage
exai-redis-commander: # Redis GUI
```

### Port Mappings
- **3000** → **8079**: WebSocket daemon
- **3001** → **8080**: Health check endpoint
- **3002** → **8082**: Metrics endpoint
- **3003** → **8000**: Additional services

### Environment Configuration
```env
# Required
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=
SUPABASE_ACCESS_TOKEN=
SUPABASE_JWT_SECRET=
GLM_API_KEY=
KIMI_API_KEY=

# Optional (with defaults)
EXAI_WS_HOST=127.0.0.1
EXAI_WS_PORT=3000
LOG_LEVEL=INFO
ROUTER_ENABLED=true
```

---

## 🔄 Configuration Management

### Centralized Configuration
**File:** `src/config/settings.py`
- Single source of truth
- Environment variable loading
- Validation and defaults
- No hardcoded values

### Configuration Hierarchy
1. Environment variables (highest priority)
2. `.env` file
3. `settings.py` defaults (lowest priority)

### Configuration Sections
- WebSocket daemon settings
- Provider configurations
- Timeout hierarchies
- Security settings
- Monitoring settings
- Performance tuning

---

## 🧪 Testing Architecture

### Test Structure
```
tests/
├── test_mcp_tools.py       # Tool functionality
├── test_providers.py       # Provider integration
├── test_database.py        # Database operations
├── test_websocket.py       # WebSocket daemon
├── test_security.py        # Authentication & RLS
└── test_integration.py     # End-to-end workflows
```

### Testing Strategy
- **Unit Tests**: Individual components
- **Integration Tests**: Provider interactions
- **End-to-End Tests**: Full request flow
- **Performance Tests**: Load and stress testing
- **Security Tests**: Authentication and authorization

---

## 📈 Performance Characteristics

### Response Times (Expected)
- **Simple tools** (chat, listmodels): 2-5 seconds
- **Workflow tools** (analyze, codereview): 30-60 seconds
- **File operations** (upload, analysis): 5-30 seconds
- **Web search** (GLM): 5-15 seconds

### Throughput
- **Global concurrent requests**: 24
- **Per-session requests**: 8
- **Per-provider requests**: GLM (4), Kimi (6)
- **Rate limiting**: 50 req/sec (global), 20 req/sec (per-user)

### Database Performance (With Indexes)
- **get_conversation_by_continuation_id**: 1.0s → 0.1s (90% improvement)
- **Message queries**: 50% faster
- **File queries**: 40% faster
- **Overall operations**: 60-90% improvement

---

## 🔧 Extensibility

### Adding New Providers
1. Extend `BaseProvider` class
2. Implement required methods
3. Register in `ProviderRegistry`
4. Update routing logic
5. Add configuration defaults

### Adding New Tools
1. Create tool class in `tools/`
2. Register in `tools/registry.py`
3. Add to `.mcp.json` if needed
4. Update documentation
5. Add tests

### Customizing Routing
1. Modify `capability_router.py`
2. Update task classification logic
3. Adjust provider selection rules
4. Test with various workloads
5. Monitor performance metrics

---

## 🚨 Failure Modes & Recovery

### Provider Failure
1. Circuit breaker opens
2. Automatic fallback to secondary provider
3. Retry with exponential backoff
4. Graceful degradation
5. Health check and recovery

### Database Failure
1. Circuit breaker opens
2. Fallback to in-memory storage
3. Queue operations for later
4. Retry when connection restored
5. Audit log all failures

### WebSocket Failure
1. Health check detects failure
2. Automatic restart
3. Session recovery
4. Client reconnection
5. State validation

---

## 📚 Related Documentation

- **Component Integration**: [02_component_integration.md](02_component_integration.md)
- **Data Flow Diagrams**: [03_data_flow_diagrams.md](03_data_flow_diagrams.md)
- **Mermaid Diagrams**: [04_mermaid_diagrams.md](04_mermaid_diagrams.md)
- **Database Integration**: [../02-database-integration/](../02-database-integration/)
- **Security & Authentication**: [../03-security-authentication/](../03-security-authentication/)
- **MCP Tools Reference**: [../04-api-tools-reference/01_mcp_tools_reference.md](../04-api-tools-reference/01_mcp_tools_reference.md)

---

## 🔗 Key Files

| Component | File Path | Purpose |
|-----------|-----------|---------|
| WebSocket Daemon | `src/daemon/ws/daemon.py` | Main server |
| Request Handler | `src/server/handlers/request_handler.py` | Request orchestration |
| Provider Config | `src/server/providers/provider_config.py` | Provider management |
| Capability Router | `src/providers/capability_router.py` | AI routing |
| Database Manager | `src/storage/hybrid_supabase_manager.py` | Data layer |
| Tool Registry | `tools/registry.py` | Tool registration |
| Settings | `src/config/settings.py` | Configuration |
| Environment | `.env` | Secrets & config |
| MCP Config | `.mcp.json` | MCP server setup |

---

**Document Version:** 1.0.0
**Created:** 2025-11-10
**Author:** EX-AI MCP Server Architecture Team
**Status:** ✅ **Complete - Core Architecture Documented**
