# Complete System Architecture - EX-AI MCP Server
**Created:** 2025-10-21  
**Purpose:** Deep dive into how everything connects - from Docker to APIs

---

## 🎯 System Purpose

**EX-AI MCP Server** is a production-ready WebSocket-based MCP (Model Context Protocol) server that provides:

1. **13 Workflow Tools** for systematic AI-assisted development:
   - `debug_EXAI-WS` - Root cause analysis with expert validation
   - `analyze_EXAI-WS` - Code architecture assessment
   - `codereview_EXAI-WS` - Comprehensive code review
   - `refactor_EXAI-WS` - Refactoring opportunity identification
   - `secaudit_EXAI-WS` - Security vulnerability assessment
   - `precommit_EXAI-WS` - Pre-commit validation
   - `testgen_EXAI-WS` - Test generation
   - `planner_EXAI-WS` - Sequential planning
   - `consensus_EXAI-WS` - Multi-model consensus
   - `thinkdeep_EXAI-WS` - Deep reasoning
   - `tracer_EXAI-WS` - Code execution tracing
   - `docgen_EXAI-WS` - Documentation generation
   - `chat_EXAI-WS` - General chat

2. **Dual AI Provider Integration**:
   - GLM (ZhipuAI) via z.ai proxy - 3x faster than China endpoint
   - Kimi (Moonshot) via OpenAI-compatible API

3. **Persistent Storage** via Supabase for conversations, files, audit trail

4. **Docker-based Deployment** with hot-reload for development

---

## 🏗️ Complete System Flow

### **Layer 1: Entry Points**

```
Windows Host (User)
    ↓
Augment Code (MCP Client)
    ↓ stdio
scripts/run_ws_shim.py (MCP Shim)
    ↓ WebSocket (ws://localhost:8079)
Docker Container (WSL/Linux)
    ↓
scripts/ws/run_ws_daemon.py (Daemon Launcher)
```

**Key Files:**
- `scripts/run_ws_shim.py` - Bridges MCP stdio ↔ WebSocket
- `scripts/ws/run_ws_daemon.py` - Launches daemon + monitoring + health + metrics

---

### **Layer 2: Docker Container**

**Dockerfile:**
```dockerfile
FROM python:3.13-slim
WORKDIR /app
ENV PYTHONPATH=/app
COPY src/ tools/ utils/ systemprompts/ streaming/ scripts/ws/ static/ ./
COPY .env.docker .env
EXPOSE 8079 8080 8082 8000
CMD ["python", "-u", "scripts/ws/run_ws_daemon.py"]
```

**docker-compose.yml:**
```yaml
services:
  exai-daemon:
    ports:
      - "8079:8079"  # WebSocket Daemon (MCP protocol)
      - "8080:8080"  # Monitoring Dashboard
      - "8082:8082"  # Health Check Endpoint
      - "8000:8000"  # Prometheus Metrics
    volumes:
      - ./src:/app/src          # Hot reload
      - ./tools:/app/tools      # Hot reload
      - ./utils:/app/utils      # Hot reload
      - ./scripts:/app/scripts  # Hot reload
      - ./logs:/app/logs        # Persistent logs
    depends_on:
      - redis
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
```

**Environment:** `.env.docker` (508 lines of configuration)

---

### **Layer 3: Daemon Startup**

**scripts/ws/run_ws_daemon.py:**
```python
async def main_with_monitoring():
    # 1. Setup correlation ID logging
    setup_correlation_logging()
    
    # 2. Setup monitoring broadcast hook
    setup_monitoring_broadcast()
    
    # 3. Start servers concurrently
    servers = [
        main_async(),                    # WebSocket daemon (port 8079)
        start_monitoring_server(),       # Monitoring (port 8080)
        start_health_server(),           # Health check (port 8082)
        start_periodic_updates()         # Metrics (port 8000)
    ]
    
    await asyncio.gather(*servers)
```

**src/daemon/ws_server.py:**
```python
async def main_async():
    # 1. Create PID file (single-instance guard)
    # 2. Initialize managers
    connection_manager = ConnectionManager()
    rate_limiter = RateLimiter()
    session_manager = SessionManager()
    auth_token_manager = AuthTokenManager()
    request_router = RequestRouter()
    
    # 3. Pre-warm external connections
    await warmup_all()  # Supabase + Redis
    
    # 4. Start WebSocket server
    async with websockets.serve(...):
        # 5. Start background tasks
        health_writer_task = start_health_writer()
        semaphore_health_task = start_semaphore_health()
        session_cleanup_task = start_session_cleanup()
        
        await stop_event.wait()
```

---

### **Layer 4: WebSocket Connection**

**Connection Flow:**
```
Client connects → ws://localhost:8079
    ↓
_connection_wrapper(ws)
    ↓
serve_connection(ws, ...)
    ↓
1. Handshake: {"op": "hello", "session_id": "...", "token": "..."}
2. Ack: {"ok": true}
3. Tool calls: {"op": "call_tool", "name": "...", "arguments": {...}}
4. Responses: {"op": "call_tool_res", "outputs": [...]}
```

**Key Components:**
- `src/websocket/connection_manager.py` - Connection lifecycle
- `src/websocket/heartbeat.py` - Heartbeat monitoring
- `src/daemon/ws/request_router.py` - Message routing

---

### **Layer 5: Tool Registration**

**server.py:**
```python
# 1. Bootstrap: Load environment
load_env()

# 2. Build tools (idempotent)
TOOLS = ensure_tools_built()

# 3. Register provider-specific tools
ensure_provider_tools_registered(TOOLS)

# 4. Filter disabled tools
TOOLS = filter_disabled_tools(TOOLS)
TOOLS = filter_by_provider_capabilities(TOOLS)
```

**Tool Discovery:**
```
tools/
├── registry.py              # Tool discovery and registration
├── workflow/
│   ├── debug.py            # debug_EXAI-WS
│   ├── analyze.py          # analyze_EXAI-WS
│   ├── codereview.py       # codereview_EXAI-WS
│   ├── refactor.py         # refactor_EXAI-WS
│   ├── secaudit.py         # secaudit_EXAI-WS
│   ├── precommit.py        # precommit_EXAI-WS
│   ├── testgen.py          # testgen_EXAI-WS
│   ├── planner.py          # planner_EXAI-WS
│   ├── consensus.py        # consensus_EXAI-WS
│   ├── thinkdeep.py        # thinkdeep_EXAI-WS
│   ├── tracer.py           # tracer_EXAI-WS
│   ├── docgen.py           # docgen_EXAI-WS
│   └── expert_analysis.py  # Expert validation (shared)
├── simple/
│   ├── chat.py             # chat_EXAI-WS
│   ├── challenge.py        # challenge_EXAI-WS
│   └── activity.py         # activity_EXAI-WS
└── provider/
    ├── kimi_*.py           # Kimi-specific tools
    └── glm_*.py            # GLM-specific tools
```

---

### **Layer 6: Request Routing**

**src/daemon/ws/request_router.py:**
```python
async def handle_message(msg):
    # 1. Parse message
    op = msg.get("op")
    
    # 2. Route based on operation
    if op == "list_tools":
        return await handle_list_tools()
    elif op == "call_tool":
        return await handle_call_tool(msg)
    
async def handle_call_tool(msg):
    # 1. Acquire semaphores (global + provider-specific)
    async with global_sem, provider_sem:
        # 2. Get tool instance
        tool = TOOLS.get(name)
        
        # 3. Call tool
        result = await tool.call(arguments, request)
        
        # 4. Return result
        return {"op": "call_tool_res", "outputs": result}
```

**Semaphore Management:**
```
Global Semaphore (5 concurrent)
    ↓
Provider Semaphore (GLM: 2, Kimi: 3)
    ↓
Per-Session Semaphore (2 per conversation)
```

---

### **Layer 7: Tool Execution**

**Workflow Tool Pattern:**
```python
class DebugTool(WorkflowTool):
    async def call(self, arguments, request):
        # Step 1: YOU investigate using view/codebase-retrieval
        # Step 2: Call this tool with YOUR findings
        # Step 3: Tool auto-executes internally (NO AI calls)
        # Step 4: Tool calls expert analysis at END (ONE AI call)
        # Step 5: Return comprehensive analysis
        
        # Multi-step workflow
        for step in range(1, total_steps + 1):
            # Collect findings from user
            findings = arguments.get("findings")
            
            # Build context
            context = self.build_context(findings)
            
            # If final step, call expert analysis
            if step == total_steps:
                result = await self.call_expert_analysis(context)
                return result
```

**Expert Analysis (Shared):**
```python
# tools/workflow/expert_analysis.py
async def _call_expert_analysis(arguments, request):
    # 1. Resolve model context
    model_name, model_context = self._resolve_model_context()
    
    # 2. Build prompt
    prompt = self.build_expert_prompt(context)
    
    # 3. Call provider
    if use_async_providers:
        result = await async_provider.generate_content(...)
    else:
        result = await run_in_executor(provider.generate_content, ...)
    
    # 4. Parse and return
    return self.parse_expert_response(result)
```

---

### **Layer 8: Provider Integration**

**src/providers/:**
```
providers/
├── base.py                 # ProviderType enum, base classes
├── glm_provider.py         # GLM sync provider
├── kimi_provider.py        # Kimi sync provider
├── async_glm_provider.py   # GLM async provider
├── async_kimi_provider.py  # Kimi async provider
└── orchestration/
    ├── websearch_adapter.py    # Web search validation
    └── model_router.py         # Intelligent model routing
```

**Provider Selection:**
```python
# 1. Model name determines provider
if model_name.startswith("glm-"):
    provider = GLMProvider()
elif model_name.startswith("kimi-") or model_name.startswith("moonshot-"):
    provider = KimiProvider()

# 2. Provider calls external API
if provider_type == ProviderType.GLM:
    # GLM via z.ai proxy (3x faster)
    response = await glm_client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=temperature,
        thinking={"type": "enabled"} if thinking_mode else None
    )
elif provider_type == ProviderType.KIMI:
    # Kimi via OpenAI-compatible API
    response = await kimi_client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=temperature
    )
```

---

### **Layer 9: External APIs**

**GLM (ZhipuAI):**
- **Endpoint:** `https://api.z.ai/api/paas/v4`
- **SDK:** `zai-sdk` (custom SDK for z.ai proxy)
- **Models:** glm-4.6, glm-4.5-flash, glm-4.5, glm-4.5-air
- **Features:** Thinking mode, web search, embeddings

**Kimi (Moonshot):**
- **Endpoint:** `https://api.moonshot.ai/v1`
- **SDK:** OpenAI SDK (compatible)
- **Models:** kimi-k2-0905-preview, kimi-thinking-preview, moonshot-v1-*
- **Features:** Context caching, file uploads, thinking mode

---

### **Layer 10: Persistent Storage**

**Supabase:**
```
Tables:
├── conversations          # Multi-turn conversation threads
├── conversation_messages  # Individual messages
├── file_uploads           # File metadata
├── issues                 # Bug tracking
└── audit_logs             # System audit trail
```

**Redis:**
```
Keys:
├── conversation:{id}      # Conversation state
├── session:{id}           # Session state
└── cache:{key}            # Response cache
```

---

## 🔧 Critical Integration Points

### **1. Bootstrap Module** (`src/bootstrap/`)
- `env_loader.py` - Environment variable loading
- `logging_setup.py` - Logging configuration
- `singletons.py` - Provider and tool initialization

### **2. Configuration** (`config.py`)
- `TimeoutConfig` - Coordinated timeout hierarchy
- Environment variable validation
- Provider configuration

### **3. Middleware** (`src/middleware/`)
- `correlation.py` - Request correlation IDs
- `rate_limiter.py` - Rate limiting
- `circuit_breaker.py` - Circuit breaker pattern

### **4. Monitoring** (`src/monitoring/`)
- `metrics.py` - Prometheus metrics
- `health_endpoint.py` - Health check endpoint
- `monitoring_endpoint.py` - Real-time dashboard

---

## 📊 Data Flow Example

**User Request: "Debug this function"**

```
1. Augment Code → run_ws_shim.py (stdio)
2. run_ws_shim.py → Docker:8079 (WebSocket)
3. ws_server.py → request_router.py
4. request_router.py → debug_EXAI-WS tool
5. debug_EXAI-WS → expert_analysis.py
6. expert_analysis.py → GLMProvider
7. GLMProvider → api.z.ai/api/paas/v4
8. api.z.ai → GLM-4.6 model
9. GLM-4.6 → Response
10. Response → expert_analysis.py (parse)
11. expert_analysis.py → debug_EXAI-WS (format)
12. debug_EXAI-WS → request_router.py
13. request_router.py → ws_server.py
14. ws_server.py → run_ws_shim.py (WebSocket)
15. run_ws_shim.py → Augment Code (stdio)
16. Augment Code → User (UI)
```

**Parallel Operations:**
- Supabase: Store conversation (async, non-blocking)
- Redis: Cache response (async, non-blocking)
- Metrics: Update counters (async, non-blocking)
- Logs: Write to file (async, non-blocking)

---

## 🚨 Known Issues & Gaps

### **EXAI Unpredictability (6 Root Causes)**
1. ✅ Model Selection Logging - FIXED (2025-10-21)
2. ⏳ Timeout Standardization - IN PROGRESS
3. ✅ Prompt Size Monitoring - FIXED (2025-10-21)
4. ⏳ Duplicate Call Prevention - IN PROGRESS
5. ⏳ Provider Health Checks - NOT STARTED
6. ⏳ Cache Management - NOT STARTED

### **Forgotten/Blocked Scripts**
- 41 test scripts archived (2025-10-21)
- 30 core scripts remaining (need audit)
- Unknown: Which scripts are actually used in production?

### **Documentation Drift**
- Roadmaps created from outdated analysis
- Fixes implemented but not documented
- Need observation-driven development

---

## 🎯 Next Steps

1. **Complete EXAI Fixes** (4 of 6 remaining)
2. **Audit Core Scripts** (30 scripts)
3. **Verify Docker Dependencies** (requirements.txt)
4. **Create Production Deployment Guide**
5. **Implement Diagnostic Data Collection**

---

**Status:** Architecture mapped, issues identified, fixes in progress

