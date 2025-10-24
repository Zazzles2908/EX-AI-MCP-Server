# Architecture Decisions - 2025-10-24

**Merged from:** SDK_ARCHITECTURE_TRUTH, OpenAI_SDK_Retry_Investigation, OpenAI_SDK_Standardization_Validation, MCP_INTEGRATION_COMPLETE

---

## 🎯 **CRITICAL ARCHITECTURAL DECISIONS**

### **1. Custom WebSocket Protocol (NOT Standard MCP JSON-RPC)**

**Decision:** EXAI-MCP uses a custom WebSocket protocol, not the standard MCP JSON-RPC protocol.

**Protocol Specification:**
```json
// Request
{
  "op": "call_tool",
  "request_id": "unique-id",
  "name": "tool_name",
  "arguments": {...}
}

// Response
{
  "op": "call_tool_res",
  "request_id": "unique-id",
  "outputs": [...],
  "error": null
}

// Authentication
{
  "op": "hello",
  "session_id": "session-id",
  "token": "auth-token"
}
```

**Rationale:** Custom protocol designed for EXAI-specific requirements and optimizations.

---

### **2. SDK Architecture: OpenAI SDK for Kimi, Independent SDK for GLM**

**Decision:**
- **Kimi Provider:** Uses OpenAI SDK (Moonshot API is OpenAI-compatible)
- **GLM Provider:** Uses independent ZhipuAI SDK (not OpenAI-compatible)

**Key Findings:**
- Moonshot API is 100% OpenAI-compatible (uses `openai` Python package)
- ZhipuAI API has its own SDK and protocol
- Both SDKs have built-in retry mechanisms (no need for custom retry logic)

**Retry Mechanisms:**
- **OpenAI SDK:** Built-in exponential backoff with jitter (max 2 retries by default)
- **ZhipuAI SDK:** Built-in retry logic (configuration varies)

**Implication:** No need to implement custom retry logic at application level.

---

### **3. MCP WebSocket Integration**

**Implementation:** Created `scripts/baseline_collection/mcp_client.py` (300 lines)

**Features:**
- Custom WebSocket protocol implementation
- Authentication via hello message
- Tool invocation with timeout support (30s default)
- Metrics collection (latency, success/failure, timestamps)
- Context manager support (`async with`)
- Automatic reconnection with exponential backoff

**Connection Configuration:**
```python
self.ws = await websockets.connect(
    uri,
    max_size=20 * 1024 * 1024,  # 20MB
    ping_interval=20.0,          # Send ping every 20s
    ping_timeout=20.0            # Wait 20s for pong (increased from 10s)
)
```

**Reconnection Logic:**
- Max retries: 3 (configurable)
- Backoff factor: 2.0 (exponential)
- Automatic reconnection on connection loss

---

### **4. Supabase Integration Strategy**

**Decision:** Supabase is audit trail/fallback, NOT primary gateway

**Architecture:**
- **Primary Path:** Client → WebSocket → MCP Daemon → Provider SDK → AI Platform
- **Audit Path:** Async/perpendicular recording to Supabase (non-blocking)
- **Purpose:** Historical tracking, debugging, analytics (not real-time gateway)

**Rationale:**
- Avoids latency from synchronous Supabase operations
- Maintains fast response times
- Provides comprehensive audit trail without performance impact

---

### **5. Context Window Strategy**

**Decision:** Context windows vary by model selection (not fixed 128k)

**Model Context Windows:**
- **GLM Models:** Varies by model (check provider documentation)
- **Kimi Models:** Varies by model (kimi-k2-0905-preview has larger context)
- **Not Fixed:** System adapts to model-specific limits

**Implication:** Don't assume 128k context for all models.

---

## 🔧 **IMPLEMENTATION DETAILS**

### **MCP Client Class Structure**

```python
class MCPWebSocketClient:
    async def connect(max_retries=3, backoff_factor=2.0) -> bool
    async def disconnect()
    async def ensure_connected(max_retries=3) -> bool
    async def call_tool(tool_name, arguments, timeout=30.0, auto_reconnect=True)
    async def execute_tool_with_metrics(tool_name, arguments, timeout=30.0)
```

**Key Methods:**
- `connect()`: Establish connection with retry logic
- `ensure_connected()`: Verify connection, reconnect if needed
- `call_tool()`: Invoke tool with automatic reconnection
- `execute_tool_with_metrics()`: Invoke tool and collect performance metrics

---

### **Tool Invocation Flow**

1. **Client** sends `call_tool` request via WebSocket
2. **Daemon** receives request, validates authentication
3. **Daemon** routes to appropriate tool handler
4. **Tool** executes (may call provider SDK)
5. **Provider SDK** makes API call to AI platform (with built-in retry)
6. **Tool** returns result
7. **Daemon** sends `call_tool_res` response
8. **Client** receives response and extracts outputs

**Latency Layers:**
- WebSocket communication: ~10-50ms
- Tool execution: Varies by tool
- Provider API call: 100ms-30s (depends on model and complexity)
- Total: Typically 200ms-30s

---

### **SDK Standardization**

**Current State:**
- Kimi provider uses OpenAI SDK (`openai` package)
- GLM provider uses ZhipuAI SDK (`zhipuai` package)
- Both SDKs are used as default with HTTP as fallback

**Validation:**
- ✅ OpenAI SDK works correctly for Kimi
- ✅ ZhipuAI SDK works correctly for GLM
- ✅ No need for custom HTTP implementations
- ✅ Built-in retry mechanisms sufficient

---

## 📊 **PERFORMANCE CHARACTERISTICS**

### **WebSocket Connection**
- **Ping Interval:** 20 seconds
- **Ping Timeout:** 20 seconds (increased from 10s to prevent premature closure)
- **Max Message Size:** 20MB
- **Reconnection:** Automatic with exponential backoff

### **Tool Execution**
- **Default Timeout:** 30 seconds
- **Provider Timeouts:** GLM 30s, Kimi 25s
- **Retry Logic:** Handled by provider SDKs (not application layer)

---

## 🚨 **CRITICAL ISSUES DISCOVERED**

### **1. WebSocket Keepalive Ping Timeout**
- **Issue:** Connection closes with `1011 (internal error) keepalive ping timeout`
- **Fix:** Increased `ping_timeout` from 10s to 20s (matching `ping_interval`)
- **Status:** Fix implemented, testing pending

### **2. Semaphore Leak in Workflow Tools**
- **Issue:** `BoundedSemaphore released too many times` for `analyze` tool
- **Impact:** Critical resource management bug
- **Status:** Identified, not yet fixed (Phase 2)

---

## 💡 **KEY LEARNINGS**

1. **Custom Protocol:** EXAI-MCP uses custom WebSocket protocol, not standard MCP JSON-RPC
2. **SDK Choice:** Use provider-native SDKs (OpenAI for Kimi, ZhipuAI for GLM)
3. **Retry Logic:** Built into SDKs, no need for custom implementation
4. **Supabase Role:** Audit trail, not primary gateway (async/perpendicular)
5. **Context Windows:** Vary by model, not fixed at 128k
6. **Connection Management:** Automatic reconnection critical for reliability

---

## 🔗 **RELATED FILES**

- **MCP Client:** `scripts/baseline_collection/mcp_client.py`
- **WebSocket Server:** `src/daemon/ws_server.py`
- **Request Router:** `src/daemon/ws/request_router.py`
- **Kimi Provider:** `src/providers/kimi_chat.py`
- **GLM Provider:** `src/providers/glm_chat.py`

---

**Created:** 2025-10-24  
**Last Updated:** 2025-10-25  
**Status:** Architecture decisions finalized and implemented

