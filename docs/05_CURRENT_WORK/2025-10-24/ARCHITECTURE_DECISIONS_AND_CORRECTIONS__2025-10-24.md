# Architecture Decisions & Critical Corrections - 2025-10-24

**Merged from:** ARCHITECTURE_DECISIONS__2025-10-24.md + SDK_ARCHITECTURE_TRUTH__CRITICAL_CORRECTION__2025-10-24.md

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

## 🚨 **CRITICAL CORRECTION: SDK CONVERSATION MANAGEMENT**

### ❌ THE WRONG ASSUMPTION

An AI agent made a **FUNDAMENTAL INCORRECT ASSUMPTION** about SDK conversation management:

**What Was Wrongly Believed:**
1. "The native SDKs have built-in conversation management"
2. "The SDKs store conversation state on their servers"
3. "You can pass a `conversation_id` instead of full messages array"
4. "Supabase/Redis are only needed as fallback storage"
5. "The `stream=True` parameter enables conversation state management"

**Why This Was Wrong:**
The AI agent confused **response streaming** (progressive token delivery) with **conversation state management** (storing conversation history).

---

### ✅ THE ACTUAL TRUTH

**CONFIRMED TRUTH:**
Both Z.ai (GLM) and Moonshot (Kimi) SDKs are **COMPLETELY STATELESS**.

**SDK Behavior:**
- **NO automatic conversation storage in standard API**
- **NO conversation_id or session_id parameter**
- **MUST send full `messages` array with EVERY request**
- **`stream=True` ONLY controls response delivery format**

**What `stream=True` Actually Does:**
- Enables Server-Sent Events (SSE) for progressive response delivery
- Returns an iterator that yields response chunks
- Does NOT store conversation state
- Does NOT enable conversation continuity
- Does NOT reduce token costs

---

### 🎯 CORRECT ARCHITECTURE UNDERSTANDING

**How Conversation Continuity ACTUALLY Works:**

**Step 1: Store Conversation in Supabase (PRIMARY STORAGE)**
```python
supabase.table('conversations').insert({
    'continuation_id': '123-456-789',
    'messages': [{'role': 'user', 'content': 'Hello'}]
})
```

**Step 2: Retrieve Conversation to Build Messages Array**
```python
conversation = supabase.table('conversations').select('*').eq('continuation_id', '123-456-789').single()
messages = conversation['messages']
messages.append({'role': 'user', 'content': 'How are you?'})
```

**Step 3: Send Full Messages Array to SDK**
```python
response = client.chat.completions.create(
    model="glm-4.6",
    messages=messages,  # ← Full conversation history required
    stream=True
)
```

**Step 4: Store Response Back to Supabase**
```python
messages.append({'role': 'assistant', 'content': response_content})
supabase.table('conversations').update({'messages': messages}).eq('continuation_id', '123-456-789')
```

**Why This Is The ONLY Approach:**
1. **SDKs are stateless** - they don't remember previous conversations
2. **No conversation_id parameter exists** - you can't reference past conversations
3. **Token costs are unavoidable** - you MUST send full history every time
4. **Supabase is PRIMARY storage** - not a fallback, but the core conversation mechanism

---

## 💰 TOKEN COST IMPLICATIONS

**Every request with conversation history:**
```python
messages = [
    {'role': 'system', 'content': '...'},      # ~50 tokens
    {'role': 'user', 'content': '...'},        # ~20 tokens
    {'role': 'assistant', 'content': '...'},   # ~100 tokens
    {'role': 'user', 'content': '...'},        # ~20 tokens
    {'role': 'assistant', 'content': '...'},   # ~150 tokens
    {'role': 'user', 'content': '...'},        # ~20 tokens (new message)
]
# Total: ~360 tokens sent EVERY request
```

**Cost Comparison:**
- **Token costs:** ~$0.002-0.01 per 1K tokens = ~$0.0007-0.0036 per request
- **Supabase query:** ~$0.0001 per request
- **Token costs are 7-36x MORE expensive than Supabase queries**

---

## 📋 CHECKLIST FOR FUTURE AI AGENTS

Before making assumptions about SDK behavior:

- [ ] Read the official SDK documentation
- [ ] Look at official code examples
- [ ] Verify what parameters the SDK actually accepts
- [ ] Test with actual SDK calls
- [ ] Don't confuse "streaming" with "conversation management"
- [ ] Don't assume SDKs have features they don't have
- [ ] Ask the user for clarification if uncertain

---

## 🎓 KEY LESSONS LEARNED

1. **Streaming ≠ Conversation Management**
   - Streaming is about response delivery format
   - Conversation management is about storing history
   - These are completely separate concerns

2. **Stateless SDKs Require External Storage**
   - Z.ai and Moonshot SDKs are stateless
   - You MUST manage conversation history yourself
   - Supabase/Redis/Database is the PRIMARY storage mechanism

3. **Token Costs Dominate**
   - Token costs are 7-36x more expensive than database queries
   - Optimizing database queries is good, but won't solve cost explosion
   - Smart context window management is the real cost optimization

4. **Verify Before Assuming**
   - Don't trust what "most modern SDKs" do
   - Read the actual documentation for the specific SDK
   - Test with real code examples

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
**Status:** Architecture decisions finalized and critical corrections documented

