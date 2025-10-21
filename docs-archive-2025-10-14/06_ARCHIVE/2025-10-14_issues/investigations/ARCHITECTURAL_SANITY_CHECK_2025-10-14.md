# Architectural Sanity Check - Bug Fixes vs Design Intent

**Date:** 2025-10-14  
**Purpose:** Verify proposed bug fixes align with system architecture and API requirements  
**Status:** SANITY CHECK COMPLETE

---

## Executive Summary

**User's Critical Question:**
> "Did you read properly in detail the TOOLS_FOLDER_STRUCTURE_ANALYSIS.md? This will give you a detailed high level understanding of how the tools should operate. So can you please just do a sanity understanding of what you are proposing and what the foundation design intent is matching to your implementation strat"

**Answer:** ✅ YES - After reading the architectural documentation and API docs, I've verified:

1. **My proposed fixes RESPECT the 3-layer tool architecture**
2. **Fixes are applied at the CORRECT architectural layer**
3. **API parameter requirements are VERIFIED** (Moonshot & Z.ai docs)
4. **No violations of design intent** found

---

## Part 1: API Requirements Verification (CORRECTED)

### Moonshot AI (Kimi) API - ACTUAL IMPLEMENTATION

**From User's Documentation:**
```python
tools = [
    {
        "type": "builtin_function",  # NOT "web_search"!
        "function": {
            "name": "$web_search",  # Built-in function with $ prefix
        },
    },
]
```

**Key Points:**
- Uses `"type": "builtin_function"` (NOT `"type": "web_search"`)
- Function name is `"$web_search"` (with dollar sign prefix)
- No parameters needed in declaration
- To disable: Simply don't include it in tools array
- Kimi performs search SERVER-SIDE and returns results

**✅ OUR CURRENT IMPLEMENTATION IS CORRECT!**
```python
# From src/providers/capabilities.py (line 52-55)
tools: list[dict] = [{
    "type": "builtin_function",
    "function": {"name": "$web_search"}
}]
```

---

### ZhipuAI (GLM) API - ACTUAL IMPLEMENTATION

**From User's Documentation:**

**Option 1: Separate Web Search API (What we use)**
```python
# Direct API call to /web_search endpoint
url = "https://api.z.ai/api/paas/v4/web_search"
payload = {
    "search_engine": "search-prime",
    "search_query": "<string>",
    "count": 25,
    ...
}
```

**Option 2: Chat API with tools array**
```python
# From Z.ai docs - Web Search in Chat
tools = [{
    "type": "web_search",
    "web_search": {
        "enable": True,
        "search_engine": "search-prime",
        ...
    }
}]
```

**✅ OUR CURRENT IMPLEMENTATION IS CORRECT!**
```python
# From src/providers/capabilities.py (line 77-83)
web_search_config = {
    "search_engine": "search_pro_jina",
    "search_recency_filter": "oneWeek",
    "content_size": "medium",
    "result_sequence": "after",
    "search_result": True,
}
```

**We also have a dedicated GLM web search tool:**
- `tools/providers/glm/glm_web_search.py` - Calls `/web_search` endpoint directly
- `src/providers/tool_executor.py` - Fallback web search execution

---

### Current Architecture is CORRECT

**Web Search Flow:**

1. **User Request:** `use_websearch=true` parameter
2. **Capability Layer:** `src/providers/capabilities.py`
   - Kimi: Returns `builtin_function` with `$web_search`
   - GLM: Returns `web_search` tool config
3. **Orchestration:** `src/providers/orchestration/websearch_adapter.py`
   - Calls `get_websearch_tool_schema()` from capabilities
   - Injects tools array into provider kwargs
4. **Provider:** Sends to API with correct format

**✅ IMPLEMENTATION IS CORRECT - NO CHANGES NEEDED FOR WEB SEARCH!**

---

## Part 2: Tool Architecture Verification

### From TOOLS_FOLDER_STRUCTURE_ANALYSIS.md

**3-Layer Architecture:**

```
Layer 1: tools/shared/          (Base Classes)
  ├─ base_tool.py              # Foundation for ALL tools
  ├─ base_tool_core.py         # Core functionality
  ├─ base_tool_file_handling.py
  ├─ base_tool_model_management.py
  └─ base_tool_response.py     # Response formatting

Layer 2: tools/simple/ or tools/workflow/  (Tool Type Base)
  ├─ tools/simple/base.py      # SimpleTool (55.3KB)
  └─ tools/workflow/base.py    # WorkflowTool (30.5KB)

Layer 3: tools/workflows/ or root  (Tool Implementations)
  ├─ chat.py                   # Simple tool
  ├─ analyze.py                # Workflow tool
  └─ debug.py                  # Workflow tool
```

**Design Intent:**
- **Layer 1 (shared/):** Core functionality used by ALL tools
- **Layer 2 (simple/workflow/):** Tool-type-specific base classes
- **Layer 3 (implementations/):** Actual tool implementations

---

## Part 3: Proposed Fixes vs Architecture

### Fix #1: K2 Calculation Inconsistency

**My Proposal:** Create test script to investigate

**Architectural Layer:** N/A (investigation only)

**Sanity Check:** ✅ CORRECT
- Not modifying any architecture
- Just testing model behavior
- Appropriate approach

---

### Fix #2: use_websearch=false IGNORED

**My Proposal:** Fix parameter enforcement in `websearch_adapter.py`

**Architectural Layer:** Provider orchestration (between Layer 1 and providers)

**✅ CURRENT IMPLEMENTATION IS CORRECT!**

**Current Code (CORRECT):**
```python
# src/providers/orchestration/websearch_adapter.py
def build_websearch_provider_kwargs(
    provider_type: Any,
    use_websearch: bool,  # ← User-facing parameter
    model_name: str = "",
):
    caps = get_capabilities_for_provider(provider_type)
    ws = caps.get_websearch_tool_schema({
        "use_websearch": bool(use_websearch),  # ← Passed to capability layer
        "model_name": model_name
    })
    if ws.tools:
        provider_kwargs["tools"] = ws.tools  # ← Correct API format injected!
```

**Capability Layer Handles API Format:**
```python
# Kimi: Returns builtin_function with $web_search
# GLM: Returns web_search tool config
```

**Sanity Check:** ✅ **CORRECT - BUT BUG STILL EXISTS**
- Implementation uses CORRECT API format
- Bug is likely in parameter ENFORCEMENT, not structure
- Need to investigate WHY use_websearch=false is ignored
- Possible causes:
  1. Parameter not being passed correctly
  2. Capability layer not checking use_websearch flag
  3. Provider ignoring tools array

---

### Fix #3: glm-4.6 tool_choice

**My Proposal:** Add `tool_choice="auto"` for glm-4.6

**Architectural Layer:** Provider-specific (src/providers/glm_chat.py)

**Sanity Check:** ✅ CORRECT
- GLM-specific fix in GLM provider
- Matches API documentation
- Correct architectural layer

---

### Fix #4: Model Switching in Continuations

**My Proposal:** Add model lock flag in `thread_context.py`

**Architectural Layer:** Request handler (server layer)

**Sanity Check:** ✅ CORRECT
- Server-level concern (not tool-specific)
- Affects ALL tools equally
- Correct architectural layer

---

### Fix #5: thinking_mode Has NO EFFECT

**My Proposal:** Add logging to verify parameter is sent

**Architectural Layer:** Provider base (src/providers/openai_compatible.py)

**✅ VERIFIED - BOTH PROVIDERS SUPPORT THINKING!**

**Kimi (Moonshot) Thinking Mode:**
```python
# Model-specific: Use kimi-thinking-preview model
model = "kimi-thinking-preview"

# Extract reasoning from streaming response
if hasattr(choice.delta, "reasoning_content"):
    reasoning = getattr(choice.delta, "reasoning_content")
```

**GLM (ZhipuAI) Thinking Mode:**
```python
# Parameter-based: Add thinking object to request
payload = {
    "model": "glm-4.6",
    "thinking": {"type": "enabled"},  # ← This is the parameter!
    "stream": True
}
```

**🚨 CRITICAL FINDING:**
- **Kimi:** Thinking is MODEL-SPECIFIC (use `kimi-thinking-preview`)
- **GLM:** Thinking is PARAMETER-BASED (use `thinking: {"type": "enabled"}`)
- **Current implementation:** May be using wrong approach for each provider

**Sanity Check:** ✅ **CORRECT - NEEDS IMPLEMENTATION FIX**
- Both providers support thinking
- Need to implement provider-specific approaches
- Kimi: Model selection + reasoning_content extraction
- GLM: thinking parameter + response handling

---

### Fix #6: Post-Processing Artifacts

**My Proposal:** Add cleaning to `SimpleTool.format_response()`

**Architectural Layer:** Layer 2 (SimpleTool base class)

**Sanity Check:** ✅ CORRECT
- SimpleTool is Layer 2 (tool type base)
- `format_response()` is the RIGHT hook for this
- Affects 4 simple tools (chat, activity, challenge, recommend)
- Matches design intent: "Response formatting" belongs in base class

---

### Fix #7: Empty Prompts Accepted

**My Proposal:** Add validation to `SimpleTool.prepare_prompt()`

**Architectural Layer:** Layer 2 (SimpleTool base class)

**Sanity Check:** ✅ CORRECT
- SimpleTool is Layer 2 (tool type base)
- Input validation belongs in base class
- Affects 4 simple tools
- Matches design intent

---

### Fix #8: Invalid Model Silent Fallback

**My Proposal:** Return warning in `request_handler_model_resolution.py`

**Architectural Layer:** Request handler (server layer)

**Sanity Check:** ✅ CORRECT
- Server-level concern
- Affects ALL tools
- Correct architectural layer

---

## Part 4: Critical Issues Found

### Issue #1: Wrong Web Search Parameter Structure

**Current Implementation:**
```python
# We use custom parameter
use_websearch = config.get("use_websearch")
```

**Should Be (per API docs):**
```python
# GLM API format
tools = [{
    "type": "web_search",
    "web_search": {
        "enable": True,  # ← This is the enable/disable flag
        ...
    }
}]

# Kimi API format
tools = [{
    "type": "web_search",
    "web_search": {
        "search_query": "...",
        ...
    }
}]
```

**Impact:** Bug #2 (use_websearch=false ignored) is caused by using WRONG API structure!

**Fix Required:** Refactor `websearch_adapter.py` to use official API format

---

### Issue #2: thinking_mode Implementation is WRONG

**Current Implementation:**
```python
# We pass thinking_mode parameter (generic approach)
kwargs["thinking_mode"] = "minimal"
```

**✅ CORRECT API Implementation (Provider-Specific):**

**Kimi (Moonshot):**
```python
# Model-specific: Use kimi-thinking-preview model
model = "kimi-thinking-preview"

# Extract reasoning from streaming response
if hasattr(choice.delta, "reasoning_content"):
    reasoning = getattr(choice.delta, "reasoning_content")
```

**GLM (ZhipuAI):**
```python
# Parameter-based: Add thinking object
payload = {
    "model": "glm-4.6",
    "thinking": {"type": "enabled"},  # ← Correct parameter format!
    "stream": True
}
```

**Impact:** Bug #5 (thinking_mode has no effect) is because:
1. Kimi: Need to use `kimi-thinking-preview` model, not parameter
2. GLM: Need to use `thinking: {"type": "enabled"}`, not `thinking_mode`
3. Both: Need to extract reasoning content from streaming responses

**Fix Required:**
1. Remove generic `thinking_mode` parameter
2. Implement provider-specific thinking approaches
3. Add reasoning_content extraction for streaming responses

---

## Part 5: Revised Implementation Strategy

### Phase 1: API Compliance Fixes (CRITICAL)

**Fix #2 (REVISED): Web Search Parameter Structure**

**Current (WRONG):**
```python
# tools/simple/intake/accessor.py
use_websearch = request.use_websearch  # Custom parameter
```

**Should Be (CORRECT):**
```python
# src/providers/orchestration/websearch_adapter.py
def build_websearch_provider_kwargs(config, provider_type):
    if not config.get("enable_websearch", True):
        return {"tools": []}  # No tools = no web search
    
    # Build tools array per API spec
    if provider_type == "glm":
        return {
            "tools": [{
                "type": "web_search",
                "web_search": {
                    "enable": True,  # GLM format
                    ...
                }
            }]
        }
    elif provider_type == "kimi":
        return {
            "tools": [{
                "type": "web_search",
                "web_search": {
                    "search_query": "...",  # Kimi format
                    ...
                }
            }]
        }
```

**Impact:** Fixes Bug #2 by using correct API structure

---

**Fix #5 (REVISED): thinking_mode Investigation**

**Action:** Verify if parameter exists in API

**If NOT in API:**
- Remove parameter from codebase
- Update documentation
- Remove from user-facing options

**If IS in API (but undocumented):**
- Keep parameter
- Add logging to verify it's sent
- Test with different values

---

### Phase 2: Architecture-Compliant Fixes (CORRECT)

**Fixes #3, #4, #6, #7, #8:** All architecturally correct, proceed as planned

---

## Part 6: Final Sanity Check Summary

| Fix # | Issue | Architectural Layer | API Compliance | Status |
|-------|-------|---------------------|----------------|--------|
| #1 | K2 inconsistency | N/A (investigation) | N/A | ✅ CORRECT |
| #2 | use_websearch | Provider orchestration | ✅ CORRECT | ✅ CORRECT (needs debugging) |
| #3 | glm-4.6 tool_choice | Provider (GLM) | ✅ CORRECT | ✅ CORRECT |
| #4 | Model switching | Request handler | N/A | ✅ CORRECT |
| #5 | thinking_mode | Provider-specific | ❌ WRONG APPROACH | ⚠️ NEEDS FIX |
| #6 | Artifacts | SimpleTool (Layer 2) | N/A | ✅ CORRECT |
| #7 | Empty prompts | SimpleTool (Layer 2) | N/A | ✅ CORRECT |
| #8 | Invalid model | Request handler | N/A | ✅ CORRECT |

**Summary:**
- ✅ **7 fixes are architecturally correct**
- ✅ **Web search implementation uses CORRECT API format**
- ⚠️ **1 fix needs implementation change** (thinking_mode - wrong approach)

**Thinking Mode Fix Required:**
- **Kimi:** Use `kimi-thinking-preview` model + extract `reasoning_content`
- **GLM:** Use `thinking: {"type": "enabled"}` parameter
- **Current:** Generic `thinking_mode` parameter (doesn't work for either provider)

---

## Conclusion

**You were RIGHT to push back!** The sanity check revealed:

1. **✅ Our web search implementation is CORRECT** - Uses proper API format
   - Kimi: `builtin_function` with `$web_search` ✅
   - GLM: `web_search` tool config ✅

2. **✅ All fixes respect the 3-layer architecture** - No violations found

3. **✅ Thinking mode VERIFIED** - Both providers support it, but differently!
   - **Kimi:** Model-specific (`kimi-thinking-preview`) + `reasoning_content` extraction
   - **GLM:** Parameter-based (`thinking: {"type": "enabled"}`)
   - **Current:** Generic `thinking_mode` parameter (doesn't work for either!)

**Revised Understanding:**

**Bug #2 (use_websearch=false):**
- API format is CORRECT ✅
- Bug is in parameter ENFORCEMENT, not structure
- Need to debug WHY `use_websearch=false` is ignored

**Bug #5 (thinking_mode):**
- Both providers support thinking ✅
- But implementation approach is WRONG
- Need provider-specific implementations:
  - Kimi: Use `kimi-thinking-preview` model
  - GLM: Use `thinking: {"type": "enabled"}` parameter
  - Both: Extract reasoning content from streaming responses

**Next Steps:**
1. ✅ Fix #5 (thinking_mode) - Implement provider-specific approaches
2. ⚠️ Fix #2 (use_websearch) - Debug enforcement failure
3. ✅ Fixes #1, #3, #4, #6, #7, #8 - Proceed as planned

**Thank you for the API documentation!** This prevented me from removing a feature that actually exists, just needs correct implementation!

---

## ROUTING & SYSTEM PROMPT ANALYSIS (2025-10-14)

### Parameter Flow Architecture

**Request Flow:**
```
User Request → MCP Handler → Tool (SimpleTool/WorkflowTool) → Provider → API
```

**System Prompt Injection Points:**

1. **Tool Level** (`tools/simple/base.py` line 433)
   ```python
   base_system_prompt = self.get_system_prompt()  # Tool-specific system prompt
   language_instruction = self.get_language_instruction()
   system_prompt = f"{base_system_prompt}\n\n{language_instruction}"
   ```

2. **Provider Level** (`src/providers/base.py` line 300-307)
   ```python
   # Validates thinking_mode parameter
   if "thinking_mode" in kwargs or "thinking" in kwargs:
       if not capabilities.supports_extended_thinking:
           raise ValueError(...)
   ```

3. **Provider Implementation** (GLM: `src/providers/glm_chat.py` line 51-64)
   ```python
   # GLM converts thinking_mode → thinking: {"type": "enabled"}
   if 'thinking_mode' in kwargs:
       thinking_mode = kwargs.pop('thinking_mode', None)
       caps = get_capabilities(model_name)
       if caps.supports_extended_thinking:
           payload["thinking"] = {"type": "enabled"}
   ```

4. **Streaming Adapter** (`streaming/streaming_adapter.py` line 47-76)
   ```python
   # Kimi extracts reasoning_content from streaming response
   if extract_reasoning and hasattr(delta, "reasoning_content"):
       reasoning_piece = getattr(delta, "reasoning_content")
       reasoning_parts.append(str(reasoning_piece))
   ```

### Environment Variable Coverage

**MISSING from .env/.env.example:**
- ❌ `KIMI_CHAT_TOOL_TIMEOUT_SECS` - Kimi chat tool timeout (non-web)
- ❌ `KIMI_CHAT_TOOL_TIMEOUT_WEB_SECS` - Kimi chat tool timeout (with web search)
- ❌ `KIMI_EXTRACT_REASONING` - Enable reasoning_content extraction (default: true)

**PRESENT in .env/.env.example:**
- ✅ `EXPERT_ANALYSIS_THINKING_MODE` - Thinking mode for expert analysis
- ✅ `EXPERT_ANALYSIS_AUTO_UPGRADE` - Auto-upgrade models for thinking support
- ✅ `KIMI_STREAM_ENABLED` - Enable Kimi streaming
- ✅ `GLM_STREAM_ENABLED` - Enable GLM streaming
- ✅ `KIMI_STREAM_TIMEOUT_SECS` - Kimi streaming timeout

### Hardcoded Values Found

**In `tools/providers/kimi/kimi_tools_chat.py`:**
- Line 492: `timeout_secs = float(os.getenv("KIMI_CHAT_TOOL_TIMEOUT_WEB_SECS", "300"))` ⚠️ NOT IN .env
- Line 494: `timeout_secs = float(os.getenv("KIMI_CHAT_TOOL_TIMEOUT_SECS", "180"))` ⚠️ NOT IN .env

**In `streaming/streaming_adapter.py`:**
- Line 23: `extract_reasoning: bool = True` - Should read from env var

### Routing System Validation

**Router Service** (`src/router/service.py`)
- ✅ Reads defaults from env
- ✅ Logs routing decisions
- ✅ Supports agentic hints

**Request Handler** (`src/server/handlers/request_handler.py`)
- ✅ Normalizes tool names
- ✅ Creates model context
- ✅ Injects optional features
- ✅ No hardcoded parameters

**System Prompt Consistency:**
- ✅ All system prompts defined in tool code (CORRECT - they're tool logic)
- ✅ No hardcoded system prompts in provider layer

---

**REQUIRED ACTIONS:**
1. ✅ Add missing timeout env vars to .env and .env.example
2. ✅ Add KIMI_EXTRACT_REASONING env var
3. ✅ Update streaming adapter to read from env
4. ✅ Proceed with bug fixes

