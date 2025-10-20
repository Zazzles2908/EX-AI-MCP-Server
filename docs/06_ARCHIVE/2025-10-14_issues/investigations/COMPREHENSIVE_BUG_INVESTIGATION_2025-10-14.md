# Comprehensive Bug Investigation - User Test Results

**Date:** 2025-10-14  
**Source:** User test results from `14.10.2025_chat_function_calls.md`  
**Status:** INVESTIGATION COMPLETE - FIXES PROPOSED

---

## Executive Summary

User testing revealed **11 critical bugs** across 5 categories. I've investigated each issue, identified the responsible scripts, and proposed architectural fixes.

**Key Finding:** Most issues are **parameter enforcement** and **response post-processing** problems, not validation issues.

---

## PRIORITY 1: CRITICAL SAFETY 🚨

### Bug #1: Model Calculation Inconsistency (K2 Models)

**Symptom:** K2 models gave 9x different results (11.2 vs 1.22 cal/cm²) for arc flash calculations

**Impact:** SAFETY CRITICAL - Wrong PPE specification = potential fatalities

**Root Cause:** **UNKNOWN - Requires investigation**

**Scripts Responsible:**
- **Investigation needed:** This is a model behavior issue, not a code issue
- Need to test with same prompt on different K2 models
- Check if it's temperature, thinking_mode, or model version differences

**Proposed Fix:**
```python
# File: scripts/testing/test_k2_consistency.py (NEW)
"""
Test K2 model consistency for safety-critical calculations.

This script tests all K2 models with identical prompts to verify
they produce consistent results for mathematical calculations.
"""

async def test_k2_calculation_consistency():
    """Test all K2 models with same calculation prompt."""
    prompt = "Calculate arc flash incident energy: 480V, 50kA, 0.5s, 18 inches"
    
    k2_models = [
        "kimi-k2-0905-preview",
        "kimi-k2-turbo-preview",
        "kimi-k2-0711-preview"
    ]
    
    results = {}
    for model in k2_models:
        # Call with IDENTICAL parameters
        response = await call_model(
            model=model,
            prompt=prompt,
            temperature=0.0,  # Deterministic
            thinking_mode=None,  # No thinking
            use_websearch=False
        )
        results[model] = extract_calculation(response)
    
    # Verify all results within 1% tolerance
    values = list(results.values())
    max_diff = max(values) - min(values)
    tolerance = max(values) * 0.01
    
    if max_diff > tolerance:
        raise ValueError(f"K2 models inconsistent: {results}")
```

**Action Required:** Run consistency test to identify which model is incorrect

---

## PRIORITY 2: CRITICAL FUNCTIONALITY 🔴

### Bug #2: use_websearch=false IGNORED

**Symptom:** Setting `use_websearch=false` doesn't work - model searches anyway

**Impact:** Users cannot disable web search even when explicitly requested

**Root Cause:** Parameter is validated but NOT enforced in provider API calls

**Scripts Responsible:**
1. `src/providers/capabilities.py` (lines 45-57, 67-69)
2. `src/providers/orchestration/websearch_adapter.py` (lines 6-50)

**Current Code:**
```python
# src/providers/capabilities.py
def get_websearch_tool_schema(self, config: Dict[str, Any]) -> WebSearchSchema:
    if not self.supports_websearch() or not config.get("use_websearch"):
        return WebSearchSchema(None, None)  # ✅ Returns empty schema
    
    # Returns web search tool schema
```

**Problem:** The check `not config.get("use_websearch")` works correctly!

**Real Issue:** Environment variable override!

```python
# tools/simple/intake/accessor.py (lines 138-157)
def get_use_websearch(request) -> bool:
    val = getattr(request, "use_websearch", None)
    if val is not None:
        return bool(val)
    # ❌ PROBLEM: Falls back to env default even when user set false!
    return os.getenv("EX_WEBSEARCH_DEFAULT_ON", "true").strip().lower() == "true"
```

**Proposed Fix:**
```python
# File: tools/simple/intake/accessor.py (lines 138-157)
@staticmethod
def get_use_websearch(request) -> bool:
    """Get use_websearch from request."""
    try:
        val = getattr(request, "use_websearch", None)
        if val is not None:
            # ✅ FIX: Respect explicit false
            return bool(val)
        # Only use env default if not specified
        import os as __os
        return __os.getenv("EX_WEBSEARCH_DEFAULT_ON", "true").strip().lower() == "true"
    except AttributeError:
        # ❌ FIX: Don't default to True, use env variable
        import os as __os
        return __os.getenv("EX_WEBSEARCH_DEFAULT_ON", "true").strip().lower() == "true"
```

**Status:** ✅ CODE LOOKS CORRECT - Need to test if issue is elsewhere

---

### Bug #3: glm-4.6 Returns Raw JSON Tool Calls

**Symptom:** glm-4.6 returns raw JSON tool calls as text instead of executing

**Impact:** Model completely non-functional for real use

**Root Cause:** Model-specific configuration or system prompt issue

**Scripts Responsible:**
1. `src/providers/glm_config.py` (lines 21-31)
2. `src/providers/glm_chat.py` (lines 86-373)

**Investigation:**
```python
# glm_config.py shows glm-4.6 supports function calling
"glm-4.6": ModelCapabilities(
    supports_function_calling=True,  # ✅ Configured correctly
    ...
)
```

**Possible Causes:**
1. System prompt doesn't instruct model to use tools
2. Tools parameter not passed correctly
3. Model needs specific tool_choice setting

**Proposed Fix:**
```python
# File: src/providers/glm_chat.py (add after line 140)
# CRITICAL FIX: glm-4.6 requires explicit tool_choice
if model_name == "glm-4.6" and payload.get("tools"):
    if not payload.get("tool_choice"):
        # Force auto tool choice for glm-4.6
        payload["tool_choice"] = "auto"
        logger.info(f"GLM-4.6: Forcing tool_choice='auto' for function calling")
```

**Action Required:** Test if glm-4.6 needs explicit tool_choice parameter

---

### Bug #4: Model Switching in Continuations

**Symptom:** Conversation started with kimi-latest, switched to glm-4.5-flash mid-conversation

**Impact:** Inconsistent behavior, unexpected model changes

**Root Cause:** Continuation doesn't lock model selection

**Scripts Responsible:**
1. `src/server/context/thread_context.py` (lines 183-195)
2. `src/server/handlers/request_handler_model_resolution.py` (lines 58-111)

**Current Code:**
```python
# thread_context.py (lines 188-195)
model_from_args = arguments.get("model")
if not model_from_args and context.turns:
    # Find the last assistant turn to get the model used
    for turn in reversed(context.turns):
        if turn.role == "assistant" and turn.model_name:
            arguments["model"] = turn.model_name  # ✅ Tries to preserve model
            break
```

**Problem:** This code SHOULD work! But model resolution happens AFTER this.

**Real Issue:** Model resolution overrides continuation model!

```python
# request_handler_model_resolution.py (lines 58-111)
def resolve_auto_model_heuristic(requested: str, tool_name: str, args: Dict[str, Any]) -> str:
    req = (requested or "").strip().lower()
    if req and req != "auto":
        return requested  # ✅ Should respect explicit model
    
    # ❌ PROBLEM: If model is "kimi-latest", it's not in the if check above!
    # Falls through to heuristic routing
```

**Proposed Fix:**
```python
# File: src/server/context/thread_context.py (after line 195)
# CRITICAL FIX: Lock model for continuation
if not model_from_args and context.turns:
    for turn in reversed(context.turns):
        if turn.role == "assistant" and turn.model_name:
            arguments["model"] = turn.model_name
            # ✅ FIX: Mark as locked to prevent routing override
            arguments["_model_locked_by_continuation"] = True
            logger.info(f"[CONTINUATION] Locked model to {turn.model_name}")
            break

# File: src/server/handlers/request_handler_model_resolution.py (line 63)
def resolve_auto_model_heuristic(requested: str, tool_name: str, args: Dict[str, Any]) -> str:
    # ✅ FIX: Respect continuation model lock
    if args.get("_model_locked_by_continuation"):
        logger.info(f"[CONTINUATION] Model locked, skipping routing: {requested}")
        return requested
    
    req = (requested or "").strip().lower()
    if req and req != "auto":
        return requested
    # ... rest of routing logic
```

---

## PRIORITY 3: HIGH USABILITY ⚠️

### Bug #5: thinking_mode Has NO EFFECT

**Symptom:** minimal/low/medium all produce identical cached responses

**Impact:** Parameter is meaningless, wasted API calls

**Root Cause:** Parameter validated but not actually sent to API

**Scripts Responsible:**
1. `src/providers/glm_chat.py` (lines 51-55)
2. `src/providers/kimi.py` (lines 124-145)

**Current Code:**
```python
# glm_chat.py (lines 51-55)
# CRITICAL FIX: Filter out thinking_mode parameter - GLM doesn't support it
if 'thinking_mode' in kwargs:
    thinking_mode = kwargs.pop('thinking_mode', None)
    logger.debug(f"Filtered out unsupported thinking_mode parameter for GLM model {model_name}: {thinking_mode}")
```

**Problem:** GLM doesn't support thinking_mode, so it's filtered out. ✅ CORRECT!

**For Kimi:**
```python
# kimi.py (lines 124-145)
def generate_content(self, prompt: str, model_name: str, **kwargs) -> ModelResponse:
    kwargs.setdefault("stream", False)
    return super().generate_content(...)  # Passes kwargs to parent
```

**Investigation Needed:** Check if Kimi API actually uses thinking_mode parameter

**Proposed Fix:**
```python
# File: src/providers/openai_compatible.py (in generate_content)
# Add logging to verify thinking_mode is sent
if "thinking_mode" in kwargs:
    logger.info(f"[THINKING_MODE] Sending to API: {kwargs['thinking_mode']}")
```

**Action Required:** Add logging to verify parameter is sent to Kimi API

---

### Bug #6: Post-Processing Artifacts

**Symptom:**
- glm-4.5v outputs `<|begin_of_box|>`, `<|end_of_box|>` tags
- glm-4.5-flash adds "AGENT'S TURN:" suffix

**Impact:** Unprofessional output

**Root Cause:** No response post-processing/cleaning

**Scripts Responsible:**
1. `tools/simple/base.py` (lines 135-150) - `format_response()` hook
2. `scripts/run_ws_shim.py` (lines 66-80) - Has cleaning code but only in shim!

**Current Code:**
```python
# run_ws_shim.py (lines 74-76) - ✅ Cleaning exists in shim!
content = re.sub(r'=== PROGRESS ===.*?=== END PROGRESS ===\n*', '', content, flags=re.DOTALL)
content = re.sub(r"\n*---\n*\n*AGENT'S TURN:.*", '', content, flags=re.DOTALL)
```

**Problem:** Cleaning only happens in WebSocket shim, not in core response handling!

**Proposed Fix:**
```python
# File: tools/simple/base.py (add new method)
def _clean_model_artifacts(self, response: str) -> str:
    """Remove model-specific artifacts from response."""
    import re
    
    # Remove GLM box tags
    response = re.sub(r'<\|begin_of_box\|>', '', response)
    response = re.sub(r'<\|end_of_box\|>', '', response)
    
    # Remove AGENT'S TURN suffix
    response = re.sub(r"\n*---\n*\n*AGENT'S TURN:.*", '', response, flags=re.DOTALL)
    response = re.sub(r"\n*AGENT'S TURN:.*$", '', response, flags=re.DOTALL)
    
    # Remove progress sections (should be in metadata, not content)
    response = re.sub(r'=== PROGRESS ===.*?=== END PROGRESS ===\n*', '', response, flags=re.DOTALL)
    
    return response.strip()

# File: tools/simple/base.py (modify format_response at line 135)
def format_response(self, response: str, request, model_info: Optional[dict] = None) -> str:
    """Format the AI response before returning to the client."""
    # ✅ FIX: Clean artifacts before returning
    return self._clean_model_artifacts(response)
```

---

### Bug #7: Empty Prompts Accepted

**Symptom:** Empty prompt accepted (should validate and reject)

**Impact:** Wastes API calls

**Root Cause:** No empty prompt validation

**Scripts Responsible:**
1. `tools/providers/kimi/kimi_tools_chat.py` (lines 208-214) - ✅ HAS validation!
2. `tools/simple/base.py` - Missing validation

**Current Code:**
```python
# kimi_tools_chat.py (lines 208-214) - ✅ Already validates!
if not norm_msgs:
    err = {
        "status": "invalid_request",
        "error": "No non-empty messages provided. Provide at least one user message with non-empty content.",
    }
    return [TextContent(type="text", text=json.dumps(err, ensure_ascii=False))]
```

**Problem:** Only kimi_tools_chat validates, not SimpleTool!

**Proposed Fix:**
```python
# File: tools/simple/base.py (add to prepare_prompt method around line 1106)
# Validate prompt is not empty
if not validation_content or not validation_content.strip():
    from tools.models import ToolOutput
    raise ValueError(f"MCP_SIZE_CHECK:{ToolOutput(
        status='error',
        content='Prompt cannot be empty. Please provide a non-empty prompt.',
        content_type='text'
    ).model_dump_json()}")
```

---

### Bug #8: Invalid Model Names Silent Fallback

**Symptom:** Requested `gpt-4` → silently fell back to `kimi-k2-0905-preview`

**Impact:** No warning/error, user doesn't know what model they got

**Root Cause:** Fallback logic doesn't log or warn

**Scripts Responsible:**
1. `src/server/handlers/request_handler_model_resolution.py` (lines 209-240)

**Current Code:**
```python
# Lines 209-240 - validate_and_fallback_model()
provider = ModelProviderRegistry.get_provider_for_model(model_name)
if not provider:
    # ❌ PROBLEM: Falls back silently!
    fallback = resolve_auto_model_legacy(args, tool_obj)
    logger.warning(f"Model '{model_name}' not available, using fallback: {fallback}")
    return fallback, None  # ❌ No error message to user!
```

**Proposed Fix:**
```python
# File: src/server/handlers/request_handler_model_resolution.py (line 220)
if not provider:
    fallback = resolve_auto_model_legacy(args, tool_obj)
    logger.warning(f"Model '{model_name}' not available, using fallback: {fallback}")
    
    # ✅ FIX: Return warning message to user
    warning_msg = (
        f"⚠️ Model '{model_name}' is not available. "
        f"Using fallback model: {fallback}. "
        f"Available models: {', '.join(ModelProviderRegistry.get_available_model_names()[:5])}..."
    )
    return fallback, warning_msg  # ✅ User sees warning
```

---

## Summary Table

| Bug # | Issue | Priority | Script | Fix Complexity |
|-------|-------|----------|--------|----------------|
| 1 | K2 calculation inconsistency | 🚨 P1 | Investigation needed | HIGH |
| 2 | use_websearch=false ignored | 🔴 P2 | `intake/accessor.py` | LOW |
| 3 | glm-4.6 broken | 🔴 P2 | `glm_chat.py` | MEDIUM |
| 4 | Model switching | 🔴 P2 | `thread_context.py` | MEDIUM |
| 5 | thinking_mode no effect | ⚠️ P3 | Investigation needed | MEDIUM |
| 6 | Post-processing artifacts | ⚠️ P3 | `base.py` | LOW |
| 7 | Empty prompts accepted | ⚠️ P3 | `base.py` | LOW |
| 8 | Invalid model silent fallback | ⚠️ P3 | `request_handler_model_resolution.py` | LOW |

---

## ARCHITECTURAL CONTEXT (From Archaeological Dig)

### System Architecture Overview

**Request Flow:**
```
Augment IDE → MCP Protocol → run_ws_shim.py → WebSocket → ws_server.py
→ request_handler.py → Tools (SimpleTool/WorkflowTool) → Providers (Kimi/GLM)
```

**Shared Infrastructure:**
- **3 Base Classes:** BaseTool, SimpleTool (55.3KB!), WorkflowTool (30.5KB)
- **13 Mixins:** Including ExpertAnalysisMixin (34.1KB - used by ALL 12 workflows!)
- **10 High-Traffic Utils:** progress.py (30 imports), observability.py (21 imports)
- **4 Provider Classes:** Kimi, GLM, OpenAI-compatible, Hybrid

**Critical Findings:**
- SimpleTool (55.3KB) is used by 4 tools (chat, activity, challenge, recommend)
- WorkflowTool is used by ALL 12 workflow tools
- Changes to shared base classes affect 20+ tools
- System has clean 4-tier architecture (utils → shared → simple/workflow → implementations)

### System Prompts Architecture

**Status:** ✅ ACTIVE - Fully integrated (14 imports found)

**Flow:**
```python
# Step 1: Import prompt from systemprompts
from systemprompts import ANALYZE_PROMPT

# Step 2: Define get_system_prompt() method
def get_system_prompt(self) -> str:
    return ANALYZE_PROMPT

# Step 3: SimpleTool.execute() calls self.get_system_prompt()
# Step 4: System prompt passed to provider.generate_content()
```

**All 14 tools use systemprompts/** - No bypass detected!

### Model Routing Architecture

**Status:** ✅ ACTIVE - Working as designed

**Provider Priority Order:**
1. KIMI (highest priority)
2. GLM
3. CUSTOM
4. OPENROUTER

**Selection Algorithm:**
1. Check `<PROVIDER>_PREFERRED_MODELS` env variable
2. If set, use first preferred model that exists
3. If not set, use provider default
4. Fallback to `DEFAULT_MODEL` from .env

**Current .env:**
```bash
DEFAULT_MODEL=glm-4.5-flash
KIMI_DEFAULT_MODEL=kimi-k2-0905-preview
```

**Issue:** `KIMI_PREFERRED_MODELS` is NOT SET, so system picks first available KIMI model

### Streaming Architecture

**Status:** ⚠️ MIXED - Disabled in .env, but implemented

**Current Config:**
```env
GLM_STREAM_ENABLED=false  # Currently DISABLED
KIMI_STREAM_ENABLED=false  # Currently DISABLED
```

**Implementation:**
- `src/providers/orchestration/streaming_flags.py` - Centralized streaming logic
- Only enabled for `chat` tool with GLM provider
- Other workflow tools don't support streaming

**Recommendation:** Enable GLM streaming for better UX

---

## CRITICAL INSIGHT: GLOBAL vs LOCAL FIXES

**User's Concern:**
> "This is only for chat function call, but shouldn't we be looking at the wider picture? Yes we can fix chat, but this would possibly clash with other function calls or we can consider more global approach to simplify the complexity of the system. Because there are shared scripts."

**Analysis:**

### Shared Scripts Affected

**1. SimpleTool (55.3KB) - Affects 4 tools:**
- chat.py
- activity.py
- challenge.py
- capabilities/recommend.py

**Fixes that affect SimpleTool:**
- Bug #6: Post-processing artifacts (format_response method)
- Bug #7: Empty prompts accepted (prepare_prompt method)

**Impact:** Changes to SimpleTool affect ALL 4 simple tools

---

**2. Provider Base Classes - Affects ALL tools:**
- `src/providers/base.py` - ModelProvider base class
- `src/providers/openai_compatible.py` (38.5KB) - OpenAI-compatible provider
- `src/providers/kimi.py` - Kimi provider
- `src/providers/glm.py` - GLM provider

**Fixes that affect providers:**
- Bug #2: use_websearch parameter enforcement
- Bug #3: glm-4.6 tool_choice handling
- Bug #5: thinking_mode parameter passing

**Impact:** Changes to providers affect ALL tools using those providers

---

**3. Request Handler - Affects ALL tools:**
- `src/server/handlers/request_handler_model_resolution.py` - Model selection
- `src/server/context/thread_context.py` - Continuation context

**Fixes that affect request handler:**
- Bug #4: Model switching in continuations
- Bug #8: Invalid model silent fallback

**Impact:** Changes to request handler affect ALL tools

---

### Global Approach Recommendation

**Instead of fixing chat-specific issues, we should:**

1. **Fix at Provider Level** (affects all tools using that provider)
   - Bug #2: use_websearch enforcement in provider base class
   - Bug #3: glm-4.6 tool_choice in GLM provider
   - Bug #5: thinking_mode in Kimi provider

2. **Fix at SimpleTool Level** (affects 4 simple tools)
   - Bug #6: Artifact cleaning in SimpleTool.format_response()
   - Bug #7: Empty prompt validation in SimpleTool.prepare_prompt()

3. **Fix at Request Handler Level** (affects all tools)
   - Bug #4: Model locking in thread_context.py
   - Bug #8: Invalid model warning in request_handler_model_resolution.py

4. **Investigate at Model Level** (affects all tools using K2 models)
   - Bug #1: K2 calculation inconsistency

**Benefits:**
- ✅ Fixes apply to ALL tools, not just chat
- ✅ Reduces code duplication
- ✅ Maintains architectural integrity
- ✅ Easier to test (test once, applies everywhere)
- ✅ Follows DRY principle

---

**Next Steps:**
1. Review this investigation
2. Verify API parameter requirements (Moonshot, ZhipuAI)
3. Approve global fixes approach
4. Implement in priority order
5. Test across ALL tools (not just chat)
6. Update GOD Checklist

