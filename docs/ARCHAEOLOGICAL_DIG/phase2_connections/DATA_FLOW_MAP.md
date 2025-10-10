# DATA FLOW MAP
**Date:** 2025-10-10 (10th October 2025, Thursday)  
**Phase:** Phase 2 - Map Connections  
**Task:** 2.7 - Data Flow Mapping  
**Status:** ✅ COMPLETE

---

## 🎯 PURPOSE

Map how data flows through the entire EX-AI-MCP-Server system from user input to AI response.

**Complete Request Lifecycle:**
User → MCP Client → WebSocket Daemon → Request Handler → Tool → Provider → AI → Response

---

## 📊 COMPLETE DATA FLOW DIAGRAM

```
┌─────────────────────────────────────────────────────────────────────────┐
│ USER (Augment IDE)                                                      │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
                    MCP Protocol (stdio transport)
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│ ENTRY POINT 1: scripts/run_ws_shim.py                                  │
│ - Health check daemon                                                   │
│ - Connect to WebSocket (ws://127.0.0.1:8765)                           │
│ - Send hello handshake                                                  │
│ - Transform: MCP request → WebSocket message                           │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
                    WebSocket Protocol (JSON messages)
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│ ENTRY POINT 2: src/daemon/ws_server.py                                 │
│ - Session management (session_id, token)                               │
│ - Concurrency control (global: 24, Kimi: 6, GLM: 4)                   │
│ - Result caching (by request_id + semantic key, 10min TTL)            │
│ - Transform: WebSocket message → Tool call                             │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
                    Tool Call (name + arguments dict)
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│ ENTRY POINT 3: src/server/handlers/request_handler.py                  │
│ Step 1: Initialize request (progress capture, request_id)              │
│ Step 2: Normalize tool name                                            │
│ Step 3: Get tool from registry (lazy load)                             │
│ Step 4: Reconstruct context (conversation continuation)                │
│ Step 5: Auto-select models (consensus tool only)                       │
│ Step 6: Execute tool                                                   │
│ Step 7: Normalize result                                               │
│ Step 8: Post-processing (attach progress, summary)                     │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
                    Tool Execution (arguments dict)
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│ TOOL LAYER: SimpleTool or WorkflowTool                                 │
│                                                                         │
│ SimpleTool Flow:                                                        │
│ 1. Validate request (Pydantic)                                         │
│ 2. Resolve model context                                               │
│ 3. Process files (expand paths, read content)                          │
│ 4. Build prompt (system + user + files + web search)                   │
│ 5. Call AI provider                                                    │
│ 6. Format response                                                     │
│ 7. Return TextContent                                                  │
│                                                                         │
│ WorkflowTool Flow:                                                      │
│ 1. Validate request (Pydantic)                                         │
│ 2. Process step data (consolidate findings)                            │
│ 3. Check completion (confidence + criteria)                            │
│ 4. If complete: Call expert analysis                                   │
│ 5. If not complete: Return guidance for next step                      │
│ 6. Return TextContent with structured response                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
                    Provider Call (model_name + prompt + params)
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│ PROVIDER LAYER: ModelProviderRegistry                                  │
│ 1. Get provider for model (priority: KIMI → GLM → CUSTOM → OPENROUTER)│
│ 2. Check health (circuit breaker if enabled)                           │
│ 3. Call provider.generate_content()                                    │
│ 4. Record telemetry (tokens, latency, success/failure)                 │
│ 5. Return ModelResponse                                                │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
                    HTTP Request (provider-specific format)
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│ AI PROVIDER API                                                         │
│                                                                         │
│ Kimi (api.moonshot.ai/v1):                                            │
│ - OpenAI-compatible format                                             │
│ - Context caching (X-Kimi-Context-Cache header)                        │
│ - Idempotency (X-Idempotency-Key header)                              │
│                                                                         │
│ GLM (api.z.ai/api/paas/v4):                                           │
│ - Native GLM format                                                     │
│ - Dual SDK/HTTP fallback                                               │
│ - Web search support                                                    │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
                    HTTP Response (JSON)
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│ RESPONSE TRANSFORMATION                                                 │
│ 1. Extract response text from provider format                          │
│ 2. Extract usage (input_tokens, output_tokens)                         │
│ 3. Extract cache token (Kimi only)                                     │
│ 4. Transform to ModelResponse                                          │
│ 5. Record observability (token usage, cache hits)                      │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
                    ModelResponse (text + usage + metadata)
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│ TOOL RESPONSE FORMATTING                                                │
│ 1. Format response text (tool-specific)                                │
│ 2. Add conversation history (if applicable)                            │
│ 3. Add metadata (model, tokens, timing)                                │
│ 4. Wrap in TextContent                                                 │
│ 5. Return list[TextContent]                                            │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
                    list[TextContent]
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│ POST-PROCESSING (request_handler.py)                                   │
│ 1. Normalize result (ensure list[TextContent])                         │
│ 2. Attach progress log                                                 │
│ 3. Attach activity summary                                             │
│ 4. Return to daemon                                                    │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
                    WebSocket Response (JSON)
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│ DAEMON RESPONSE (ws_server.py)                                         │
│ 1. Cache result (by request_id + semantic key)                         │
│ 2. Send response to WebSocket client                                   │
│ 3. Update metrics (latency, success/failure)                           │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
                    WebSocket Message
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│ SHIM RESPONSE (run_ws_shim.py)                                         │
│ 1. Receive WebSocket response                                          │
│ 2. Transform: WebSocket message → MCP response                         │
│ 3. Return to MCP client                                                │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
                    MCP Protocol (stdio transport)
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│ USER (Augment IDE)                                                      │
│ - Display response in chat                                             │
│ - Show progress messages                                               │
│ - Show activity summary                                                │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 DATA TRANSFORMATION POINTS

### 1. MCP Request → WebSocket Message (run_ws_shim.py)

**Input:**
```python
# MCP CallToolRequest
{
    "method": "tools/call",
    "params": {
        "name": "chat",
        "arguments": {
            "prompt": "Hello",
            "model": "auto"
        }
    }
}
```

**Output:**
```python
# WebSocket message
{
    "type": "call_tool",
    "session_id": "abc123",
    "request_id": "req_456",
    "name": "chat",
    "arguments": {
        "prompt": "Hello",
        "model": "auto"
    }
}
```

---

### 2. Tool Arguments → Pydantic Request (Tool Layer)

**Input:**
```python
# Raw arguments dict
{
    "prompt": "Hello",
    "files": ["/path/to/file.py"],
    "model": "auto",
    "temperature": 0.5
}
```

**Output:**
```python
# Validated Pydantic model
ChatRequest(
    prompt="Hello",
    files=["/path/to/file.py"],
    model="auto",
    temperature=0.5,
    continuation_id=None,
    use_websearch=True,
    stream=False
)
```

---

### 3. Prompt Building → AI Request (Tool → Provider)

**Input:**
```python
# Tool prompt components
system_prompt = "You are a helpful assistant..."
user_content = "Hello"
files = ["/path/to/file.py"]
```

**Output:**
```python
# Provider request
{
    "model": "kimi-k2-0905-preview",
    "messages": [
        {"role": "system", "content": "You are a helpful assistant..."},
        {"role": "user", "content": "# CONTEXT FILES\n\n<file.py content>\n\nHello"}
    ],
    "temperature": 0.5,
    "stream": False
}
```

---

### 4. Provider Response → ModelResponse (Provider Layer)

**Input (Kimi):**
```json
{
    "id": "chatcmpl-123",
    "model": "kimi-k2-0905-preview",
    "choices": [{
        "message": {"role": "assistant", "content": "Hi there!"},
        "finish_reason": "stop"
    }],
    "usage": {
        "prompt_tokens": 100,
        "completion_tokens": 5,
        "total_tokens": 105
    }
}
```

**Output:**
```python
ModelResponse(
    text="Hi there!",
    model_name="kimi-k2-0905-preview",
    finish_reason="stop",
    usage={
        "input_tokens": 100,
        "output_tokens": 5,
        "total_tokens": 105
    }
)
```

---

### 5. ModelResponse → TextContent (Tool Layer)

**Input:**
```python
ModelResponse(text="Hi there!", ...)
```

**Output:**
```python
[TextContent(type="text", text="Hi there!")]
```

---

### 6. TextContent → WebSocket Response (Daemon)

**Input:**
```python
[TextContent(type="text", text="Hi there!")]
```

**Output:**
```json
{
    "type": "tool_result",
    "request_id": "req_456",
    "content": [
        {"type": "text", "text": "Hi there!"}
    ],
    "isError": false
}
```

---

## 📝 VALIDATION POINTS

### 1. Request Validation (request_handler.py)
- **What:** Validate tool name exists in registry
- **When:** Step 2 (Normalize tool name)
- **Error:** Return error if tool not found

### 2. Pydantic Validation (Tool Layer)
- **What:** Validate request arguments against Pydantic model
- **When:** Tool.execute() start
- **Error:** Return validation error with field details

### 3. File Path Validation (Tool Layer)
- **What:** Validate file paths exist and are accessible
- **When:** File processing
- **Error:** Return error with invalid paths

### 4. Token Limit Validation (Tool Layer)
- **What:** Check prompt doesn't exceed model token limit
- **When:** Prompt building
- **Error:** Return error or truncate files

### 5. Model Availability Validation (Provider Layer)
- **What:** Check model is supported by provider
- **When:** Provider selection
- **Error:** Fallback to next provider or return error

---

## 💾 CACHING POINTS

### 1. Result Cache (Daemon - by request_id)
- **Key:** request_id
- **TTL:** 10 minutes
- **Purpose:** Prevent duplicate execution for same request
- **Location:** ws_server.py

### 2. Semantic Cache (Daemon - by call_key)
- **Key:** tool_name + arguments hash
- **TTL:** 10 minutes
- **Purpose:** Reuse results for identical calls
- **Location:** ws_server.py

### 3. Kimi Context Cache (Provider)
- **Key:** session_id + tool_name + prefix_hash
- **TTL:** LRU cache
- **Purpose:** Reduce costs with context caching
- **Location:** kimi_cache.py

### 4. File Content Cache (Utils)
- **Key:** file_path + sha256
- **TTL:** Session-based
- **Purpose:** Avoid re-reading same files
- **Location:** utils/file/cache.py

---

## 📊 OBSERVABILITY POINTS

### 1. Progress Tracking (utils/progress.py)
- **What:** Progress messages during execution
- **When:** Throughout tool execution
- **Output:** logs/mcp_activity.log

### 2. Token Usage (utils/observability.py)
- **What:** Token usage per provider/model
- **When:** After AI response
- **Output:** .logs/metrics.jsonl

### 3. File Upload Tracking (utils/observability.py)
- **What:** File upload count delta
- **When:** After file upload
- **Output:** .logs/metrics.jsonl

### 4. Error Tracking (utils/observability.py)
- **What:** Provider errors
- **When:** On error
- **Output:** .logs/metrics.jsonl

### 5. Route Plan Logging (utils/observability.py)
- **What:** Model selection decisions
- **When:** After model selection
- **Output:** logs/routeplan/<YYYY-MM-DD>.jsonl

---

## ✅ TASK 2.7 COMPLETE

**Deliverable:** DATA_FLOW_MAP.md ✅

**Key Findings:**
- Complete request lifecycle mapped (User → AI → User)
- 6 data transformation points identified
- 5 validation points documented
- 4 caching layers mapped
- 5 observability points tracked

**Next Task:** Task 2.8 - Critical Path Identification

**Time Taken:** ~60 minutes (as estimated)

---

**Status:** ✅ COMPLETE - Complete data flow mapped with all transformation and validation points

