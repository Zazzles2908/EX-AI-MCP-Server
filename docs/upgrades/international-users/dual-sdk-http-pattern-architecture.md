# Dual SDK/HTTP Pattern Architecture

**Document Type:** Architectural Decision Record (ADR)  
**Status:** Active  
**Created:** 2025-10-02  
**Last Updated:** 2025-10-02  
**Related Tasks:** Wave 1 Task 1.0.1

---

## Context and Problem Statement

The EX-AI-MCP-Server needs to interact with the GLM (ZhipuAI) API for chat completions, streaming, and tool calling. Two approaches are available:

1. **Official SDK:** Use the `zhipuai` Python SDK (zai-sdk)
2. **Direct HTTP:** Use HTTP client to call API endpoints directly

**Question:** Should we use SDK-only, HTTP-only, or both?

---

## Decision

**We implement a DUAL SDK/HTTP FALLBACK PATTERN** where:
- SDK is the **primary path** (preferred when available)
- HTTP is the **fallback path** (used when SDK unavailable or fails)
- Both paths support the same features (streaming, tool calling, etc.)
- Automatic fallback ensures resilience

---

## Architecture Overview

### High-Level Flow

```
User Request
     ↓
generate_content()
     ↓
  use_sdk?
   /    \
 YES    NO
  ↓      ↓
SDK    HTTP
Path   Path
  ↓      ↓
  Response
```

### Implementation Location

**File:** `src/providers/glm_chat.py`  
**Key Lines:**
- Lines 52-61: Tool calling support (SDK and HTTP)
- Line 107: Environment-gated streaming check
- Line 116: SDK path - `sdk_client.chat.completions.create()`
- Line 180: HTTP fallback path

---

## Detailed Architecture

### 1. SDK Path (Primary)

**When Used:**
- `use_sdk=True` AND `sdk_client` is available
- SDK successfully imported and initialized

**Implementation (Lines 114-178):**

```python
if use_sdk and sdk_client:
    # Use official SDK
    resp = sdk_client.chat.completions.create(
        model=model_name,
        messages=payload["messages"],
        temperature=payload.get("temperature"),
        max_tokens=payload.get("max_tokens"),
        stream=stream,
        tools=payload.get("tools"),
        tool_choice=payload.get("tool_choice"),
    )
```

**Features:**
- ✅ OpenAI-compatible API
- ✅ Streaming support (SSE)
- ✅ Tool calling
- ✅ Automatic response parsing
- ✅ Type safety (Pydantic models)

**Advantages:**
1. **Official Support:** Maintained by ZhipuAI
2. **Type Safety:** Pydantic models for requests/responses
3. **Automatic Updates:** SDK updates include new features
4. **Error Handling:** Built-in error handling and retries
5. **Documentation:** Official SDK documentation available

**Disadvantages:**
1. **Dependency:** Requires `zhipuai` package installed
2. **Version Lock:** Tied to SDK version
3. **Abstraction:** Less control over HTTP details

---

### 2. HTTP Path (Fallback)

**When Used:**
- `use_sdk=False` OR `sdk_client` is None
- SDK import failed or not available
- Fallback when SDK path fails

**Implementation (Lines 180-268):**

```python
else:
    # HTTP fallback
    if stream:
        # SSE streaming
        for data in http_client.stream_sse("/chat/completions", payload, event_field="data"):
            # Process SSE events
            ...
    else:
        # Non-streaming HTTP
        raw = http_client.post("/chat/completions", payload)
        ...
```

**Features:**
- ✅ Direct HTTP POST to `/chat/completions`
- ✅ SSE streaming support
- ✅ Tool calling support
- ✅ Manual response parsing
- ✅ Full control over requests

**Advantages:**
1. **No SDK Dependency:** Works without `zhipuai` package
2. **Full Control:** Direct access to HTTP layer
3. **Debugging:** Easier to inspect raw requests/responses
4. **Flexibility:** Can customize headers, timeouts, etc.
5. **Resilience:** Works even if SDK has bugs

**Disadvantages:**
1. **Manual Parsing:** Must parse responses manually
2. **Maintenance:** Must update for API changes
3. **No Type Safety:** No Pydantic models
4. **Error Handling:** Must implement manually

---

## Streaming Support

### Environment-Gated Streaming (Line 107)

```python
# Env gate: allow streaming only when GLM_STREAM_ENABLED=true
try:
    _stream_env = os.getenv("GLM_STREAM_ENABLED", "false").strip().lower() in ("1", "true", "yes")
except Exception:
    _stream_env = False
if stream and not _stream_env:
    logger.info("GLM streaming disabled via GLM_STREAM_ENABLED; falling back to non-streaming")
    stream = False
```

**Purpose:** Allow disabling streaming via environment variable for debugging or compatibility

**Configuration:**
```bash
# Enable streaming (default: false)
GLM_STREAM_ENABLED=true
```

### SDK Streaming (Lines 126-172)

**Mechanism:** Iterate over SDK response object
```python
for event in resp:
    choice = getattr(event, "choices", [None])[0]
    if choice is not None:
        delta = getattr(choice, "delta", None)
        if delta and getattr(delta, "content", None):
            content_parts.append(delta.content)
```

**Aggregation:** Collect chunks into `content_parts`, join at end

### HTTP Streaming (Lines 181-240)

**Mechanism:** SSE (Server-Sent Events) via `http_client.stream_sse()`
```python
for data in http_client.stream_sse("/chat/completions", payload, event_field="data"):
    line = (data or "").strip()
    if line == "[DONE]":
        break
    evt = json.loads(line)
    # Extract content from event
```

**Format:** `text/event-stream` with JSON events

---

## Tool Calling Support (Lines 52-61)

### Payload Construction

```python
# Pass through GLM tool capabilities when requested (e.g., native web_search)
try:
    tools = kwargs.get("tools")
    if tools:
        payload["tools"] = tools
    tool_choice = kwargs.get("tool_choice")
    if tool_choice:
        payload["tool_choice"] = tool_choice
except Exception:
    # be permissive
    pass
```

**Features:**
- ✅ OpenAI-compatible tool format
- ✅ Native web_search support
- ✅ Function calling
- ✅ Tool choice control

**Both Paths Support:**
- SDK path: `tools` and `tool_choice` parameters passed to SDK
- HTTP path: `tools` and `tool_choice` included in JSON payload

---

## Sequence Diagrams

### SDK Path (Non-Streaming)

```
User → generate_content()
         ↓
      use_sdk=True?
         ↓ YES
      sdk_client.chat.completions.create()
         ↓
      ZhipuAI API
         ↓
      Response (Pydantic model)
         ↓
      Extract content from response.choices[0].message.content
         ↓
      ModelResponse
         ↓
      User
```

### SDK Path (Streaming)

```
User → generate_content()
         ↓
      use_sdk=True? + stream=True
         ↓ YES
      sdk_client.chat.completions.create(stream=True)
         ↓
      ZhipuAI API (SSE stream)
         ↓
      for event in resp:
         ↓
      Aggregate chunks: content_parts.append(delta.content)
         ↓
      Join chunks: "".join(content_parts)
         ↓
      ModelResponse (metadata.streamed=True)
         ↓
      User
```

### HTTP Path (Non-Streaming)

```
User → generate_content()
         ↓
      use_sdk=False?
         ↓ YES
      http_client.post("/chat/completions", payload)
         ↓
      ZhipuAI API
         ↓
      Response (JSON)
         ↓
      Parse JSON: raw.get("choices")[0].get("message").get("content")
         ↓
      ModelResponse
         ↓
      User
```

### HTTP Path (Streaming)

```
User → generate_content()
         ↓
      use_sdk=False? + stream=True
         ↓ YES
      http_client.stream_sse("/chat/completions", payload)
         ↓
      ZhipuAI API (SSE stream)
         ↓
      for data in stream:
         ↓
      Parse SSE events: json.loads(line)
         ↓
      Aggregate chunks: content_parts.append(content)
         ↓
      Join chunks: "".join(content_parts)
         ↓
      ModelResponse (metadata.streamed=True)
         ↓
      User
```

---

## Implications for zai-sdk v0.0.4 Upgrade

### SDK Path Changes

**Expected Changes:**
- ✅ API signature unchanged (`chat.completions.create()`)
- ✅ Streaming format unchanged (SSE)
- ✅ Tool calling format unchanged (OpenAI-compatible)
- ✅ Response structure unchanged

**Impact:** **MINIMAL** - SDK path should work unchanged

### HTTP Path Changes

**Expected Changes:**
- ✅ Endpoint unchanged (`/chat/completions`)
- ✅ Request payload format unchanged
- ✅ Response format unchanged
- ✅ SSE streaming format unchanged

**Impact:** **NONE** - HTTP path should work unchanged

### New Features (Additive)

**Video Generation (CogVideoX-2):**
- New endpoint: `/paas/v4/videos/generations`
- Does NOT affect existing chat completions
- Can be added as separate function

**Assistant API:**
- New endpoint: `/paas/v4/assistant/conversation`
- Does NOT affect existing chat completions
- Can be added as separate function

**Character RP (CharGLM-3):**
- New model: `charglm-3`
- New meta parameters (user_info, bot_info, etc.)
- Does NOT affect existing models

**Impact:** **NONE** - New features are additive, don't affect dual pattern

---

## Upgrade Strategy

### Phase 1: Verify Compatibility (Wave 3, Epic 3.1)

1. **Test SDK Path:**
   ```bash
   pip install zai-sdk>=0.0.4
   # Test chat completions
   # Test streaming
   # Test tool calling
   ```

2. **Test HTTP Path:**
   ```bash
   # Test without SDK (use_sdk=False)
   # Verify HTTP fallback works
   # Test streaming via SSE
   ```

3. **Verify Dual Pattern:**
   ```bash
   # Test automatic fallback
   # Verify both paths produce same results
   ```

### Phase 2: Update Dependencies (Wave 3, Epic 3.2)

```python
# requirements.txt
zai-sdk>=0.0.4  # Updated from >=0.0.3.3
```

### Phase 3: Code Updates (Wave 3, Epic 3.3)

**Expected:** NONE (backward compatible)

**If needed:**
- Update response parsing if format changes
- Update streaming chunk aggregation if format changes
- Update tool calling if format changes

---

## Benefits of Dual Pattern

### 1. Resilience

**Scenario:** SDK has a bug or is unavailable
- **Without Dual Pattern:** Service down
- **With Dual Pattern:** Automatic fallback to HTTP

### 2. Flexibility

**Scenario:** Need to debug API calls
- **Without Dual Pattern:** Must modify SDK code
- **With Dual Pattern:** Switch to HTTP path, inspect raw requests

### 3. Gradual Migration

**Scenario:** Upgrading to new SDK version
- **Without Dual Pattern:** Must upgrade all at once
- **With Dual Pattern:** Test SDK path, fallback to HTTP if issues

### 4. Development Speed

**Scenario:** New API feature not yet in SDK
- **Without Dual Pattern:** Wait for SDK update
- **With Dual Pattern:** Use HTTP path immediately

---

## Trade-offs

### Complexity

**Cost:** More code to maintain (two paths)  
**Benefit:** Resilience and flexibility

**Mitigation:** Shared payload construction, similar response handling

### Testing

**Cost:** Must test both paths  
**Benefit:** Confidence in fallback mechanism

**Mitigation:** Automated tests for both paths

### Maintenance

**Cost:** Must update both paths for API changes  
**Benefit:** HTTP path catches SDK bugs

**Mitigation:** API changes are rare, both paths use same payload format

---

## Conclusion

The **Dual SDK/HTTP Fallback Pattern** provides:
- ✅ **Resilience:** Automatic fallback if SDK fails
- ✅ **Flexibility:** Can use HTTP for debugging
- ✅ **Compatibility:** Works with or without SDK
- ✅ **Future-Proof:** Easy to add new features

**For zai-sdk v0.0.4 upgrade:**
- ✅ **No breaking changes expected** in either path
- ✅ **Backward compatible** with v0.0.3.3
- ✅ **Seamless upgrade** (simple `pip install --upgrade`)
- ✅ **New features** can be added without affecting dual pattern

**Recommendation:** **MAINTAIN** dual pattern in v0.0.4 upgrade for continued resilience and flexibility.

---

**Document Status:** ✅ COMPLETE (Task 1.0.1)  
**Next Steps:** Task 1.0.2 (Map GLM-4.5 → GLM-4.6 API Changes)

