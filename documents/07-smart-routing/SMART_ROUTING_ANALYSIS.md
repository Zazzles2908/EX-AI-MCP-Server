# EX-AI MCP Server Smart Routing Analysis

> **Intelligent Routing System Gap Analysis**
>
> **Version:** 1.0
> **Date:** 2025-11-10
> **Status:** ANALYSIS COMPLETE

---

## Executive Summary

### The Problem: A Sophisticated Router That Nobody Uses

The EX-AI MCP Server has a **critical architectural gap**: a fully-implemented, sophisticated `CapabilityRouter` exists in `src/providers/capability_router.py` (441 lines) but is **virtually unused** in the actual tool execution flow. Instead, tools use a simple, hardcoded 3-category fallback system from `src/providers/registry_selection.py` (525 lines).

**Key Findings:**
- ✅ **CapabilityRouter** exists with 7 execution paths, detailed capability matrices, and tool requirements for 12+ tools
- ❌ **Only 2 code locations** (lines 546-558, 646-658 in `tools/simple/base.py`) partially use it, and **only for web search routing**
- ❌ **All other tool execution** uses the simple category-based routing from `registry_selection.py`
- 🔍 **The "smart" router is not integrated** into the main execution flow

### The Impact

This disconnect means:
1. **No capability-based routing** - Tools don't check if providers support required features (vision, thinking mode, web search, etc.)
2. **Web search routing bug** - Tools can route to Kimi for web search, even though Kimi doesn't support it
3. **Suboptimal model selection** - No intelligent provider selection based on tool requirements
4. **Technical debt** - 441 lines of sophisticated routing code sits unused while the system uses primitive fallback chains

---

## Current Architecture: What Actually Gets Used

### Primary Routing: registry_selection.py

The current routing system uses a **simple 3-category model**:

```python
# From tools/models.py
class ToolModelCategory(Enum):
    FAST_RESPONSE = "fast_response"        # Speed & cost efficiency
    EXTENDED_REASONING = "extended_reasoning"  # Deep thinking
    BALANCED = "balanced"                  # Balanced capability
```

**Location:** `src/providers/registry_selection.py:42-127`

**How It Works:**
1. Tools define their category via `get_model_category()` method
2. Fallback chains are hardcoded in `_fallback_chain()` (lines 241-283):

```python
def _fallback_chain(category):
    if cat_name == "FAST_RESPONSE":
        order = ["glm-4.6", "glm-4.5-flash", "glm-4.5"]
    elif cat_name == "EXTENDED_REASONING":
        order = ["kimi-k2-0905-preview", "kimi-k2-0711-preview", "kimi-thinking-preview"]
    elif cat_name == "BALANCED":
        order = ["glm-4.5", "glm-4.5-air", "glm-4.6"]
```

**Tool Usage Pattern:**
- `tools/chat.py:140-144` - Returns `ToolModelCategory.FAST_RESPONSE`
- `tools/capabilities/listmodels.py:340-342` - Returns `ToolModelCategory.FAST_RESPONSE`
- All workflow tools use similar patterns

**The Problem:** This is a **static, hardcoded system** with no capability awareness.

---

## CapabilityRouter Design: The Unused Solution

### Sophisticated Architecture (441 lines)

**File:** `src/providers/capability_router.py`

**Key Components:**

#### 1. ExecutionPath Enum (7 routing strategies)

```python
class ExecutionPath(Enum):
    DIRECT = "direct_execution"              # Utility tools, no model needed
    STANDARD = "standard_execution"          # Basic model execution
    STREAMING = "streaming_execution"        # Streaming response
    THINKING = "thinking_mode"               # Deep reasoning mode
    VISION = "vision_enabled"                # Image processing
    FILE_UPLOAD = "file_upload_enabled"      # File handling
    TOOL_CALLING = "tool_calling_enabled"    # Function calling
```

**Location:** `src/providers/capability_router.py:19-28`

#### 2. CapabilityMatrix for Providers

```python
# Kimi (Moonshot) capabilities
KIMI_CAPABILITIES = {
    "streaming": True,
    "thinking_mode": True,
    "file_uploads": True,
    "vision": True,
    "tool_calling": True,
    "web_search": False,  # CRITICAL: Kimi does NOT support web_search
    "max_tokens": 128000,
    # ...
}

# GLM (ZhipuAI) capabilities
GLM_CAPABILITIES = {
    "streaming": True,
    "thinking_mode": True,
    "file_uploads": True,
    "vision": True,
    "tool_calling": True,
    "web_search": True,  # GLM DOES support web_search
    "max_tokens": 128000,
    # ...
}
```

**Location:** `src/providers/capability_router.py:30-112`

**Critical Bug Fix (lines 363-365):**
```python
if requirements.needs_web_search:
    logger.info("[SMART_ROUTING] Tool requires web_search, routing to GLM")
    return ProviderType.GLM
```

This correctly routes web search requests to GLM, avoiding the bug where Kimi receives web search requests.

#### 3. ToolRequirements for 12+ Tools

```python
TOOL_REQUIREMENTS = {
    # Complex workflow tools
    "debug": ToolRequirements(
        needs_reasoning=True,
        supports_streaming=True,
        min_tokens=8192
    ),
    "analyze": ToolRequirements(needs_reasoning=True),
    "codereview": ToolRequirements(needs_reasoning=True),
    "refactor": ToolRequirements(needs_reasoning=True),
    "secaudit": ToolRequirements(needs_reasoning=True),
    "precommit": ToolRequirements(needs_reasoning=True),
    "testgen": ToolRequirements(needs_reasoning=True),
    "thinkdeep": ToolRequirements(needs_reasoning=True, min_tokens=16384),
    "tracer": ToolRequirements(needs_reasoning=True),
    "planner": ToolRequirements(needs_reasoning=True),
    "docgen": ToolRequirements(needs_reasoning=False),
    "consensus": ToolRequirements(needs_reasoning=True),

    # Simple tools
    "chat": ToolRequirements(
        needs_file_upload=True,
        needs_web_search=True,  # BUG: This should trigger GLM routing
        min_tokens=4096
    ),

    # Utility tools
    "activity": ToolRequirements(requires_model=False),
    "health": ToolRequirements(requires_model=False),
    "listmodels": ToolRequirements(requires_model=False),
}
```

**Location:** `src/providers/capability_router.py:156-246`

#### 4. Smart Routing Methods

**get_optimal_provider()** - Lines 342-380:
```python
def get_optimal_provider(self, tool_name: str, required_features: Optional[List[str]] = None):
    requirements = TOOL_REQUIREMENTS.get(tool_name)
    if not requirements:
        return ProviderType.AUTO

    # BUG FIX (2025-11-09): Smart routing for web_search
    if requirements.needs_web_search:
        logger.info("[SMART_ROUTING] Tool requires web_search, routing to GLM")
        return ProviderType.GLM

    # Check which providers support all required features
    for provider in [ProviderType.KIMI, ProviderType.GLM]:
        capabilities = self.capability_matrix.get_capabilities(provider)
        if all(capabilities.get(feature, False) for feature in required_features):
            return provider

    return ProviderType.AUTO
```

**route_request()** - Lines 266-340:
Determines optimal execution path based on tool requirements, provider capabilities, and request parameters (streaming, thinking mode, images, files).

---

## Gap Analysis: Why They're Disconnected

### The Integration Gap

**Where the capability router SHOULD be called:**
1. Tool initialization → Get optimal provider for tool
2. Model resolution → Check provider capabilities
3. Request validation → Verify provider can handle features
4. Execution path selection → Choose routing strategy

**Where it ACTUALLY gets called:**

**Location 1:** `tools/simple/base.py:546-558` (First web search check)
```python
# BUG FIX (2025-11-09): Use smart routing when web search is needed
effective_provider_type = provider.get_provider_type()
if use_web:
    # Route to GLM for web_search - Kimi doesn't support it
    router = get_router()
    tool_name = getattr(self, 'tool_name', 'unknown')
    optimal_provider = router.get_optimal_provider(tool_name)
    if optimal_provider != ProviderType.AUTO:
        effective_provider_type = optimal_provider
        self.logger.info(f"[SMART_ROUTING] Tool '{tool_name}' requires web_search, routing to {optimal_provider.value}")
```

**Location 2:** `tools/simple/base.py:646-658` (Second web search check, duplicate code!)
```python
# BUG FIX (2025-11-09): Use smart routing when web search is needed
effective_provider_type = provider.get_provider_type()
if use_web:
    # Route to GLM for web_search - Kimi doesn't support it
    router = get_router()
    tool_name = getattr(self, 'tool_name', 'unknown')
    optimal_provider = router.get_optimal_provider(tool_name)
    if optimal_provider != ProviderType.AUTO:
        effective_provider_type = optimal_provider
        self.logger.info(f"[SMART_ROUTING] Tool '{tool_name}' requires web_search, routing to {optimal_provider.value}")
```

**The Problem:** The CapabilityRouter is only consulted for web search routing, and even then:
- The code is duplicated (lines 546-558 and 646-658)
- It's only checked when `use_web` is True
- It's not used for any other capability routing (vision, thinking mode, file uploads, etc.)

### What Actually Happens in Tool Execution

**Current Flow (simplified):**
```python
# tools/simple/base.py:369-396
def execute():
    # 1. Get model from request or use "auto"
    model_name = self.get_request_model_name(request) or DEFAULT_MODEL

    # 2. Create model context
    self._model_context = ModelContext(model_name)

    # 3. For auto mode, get fallback model from REGISTRY SELECTION
    if model_name == "auto":
        seed = registry_instance.get_preferred_fallback_model(
            self.get_model_category()  # ← Uses simple category
        )
        self._model_context = ModelContext(seed)

    # 4. Get provider from model context
    provider = self._model_context.provider

    # 5. Only check capabilities for WEB SEARCH (partial fix)
    if use_web:
        router = get_router()  # ← Only for web search!
        optimal_provider = router.get_optimal_provider(tool_name)

    # 6. Call provider WITHOUT capability checks
    result = provider.generate_content(...)
```

**Missing:** No capability checks for:
- Vision capabilities (image processing)
- Thinking mode support
- File upload support
- Tool calling support
- Token limit requirements

---

## Tool Analysis: All Tools and Their Categories

### Tools Using Simple Categories

**1. Chat Tool** (`tools/chat.py:140-144`)
```python
def get_model_category(self) -> "ToolModelCategory":
    """Chat prioritizes fast responses and cost efficiency"""
    return ToolModelCategory.FAST_RESPONSE
```
**Problem:** Category doesn't capture that chat needs web search support.

**2. ListModels Tool** (`tools/capabilities/listmodels.py:340-342`)
```python
def get_model_category(self) -> ToolModelCategory:
    return ToolModelCategory.FAST_RESPONSE  # Simple listing, no AI needed
```
**Note:** This tool doesn't even need a model (has `requires_model()` method).

**3. Workflow Tools** (all 12 tools in `tools/workflows/*.py`)

Each has:
```python
def get_model_category(self) -> "ToolModelCategory":
    return ToolModelCategory.EXTENDED_REASONING
```

**Examples:**
- `tools/workflows/debug.py:225` - Returns `EXTENDED_REASONING`
- `tools/workflows/analyze.py:93` - Returns `EXTENDED_REASONING`
- `tools/workflows/codereview.py:87` - Returns `EXTENDED_REASONING`
- `tools/workflows/refactor.py:93` - Returns `EXTENDED_REASONING`
- `tools/workflows/tracer.py:89` - Returns `EXTENDED_REASONING`
- `tools/workflows/thinkdeep.py:71` - Returns `EXTENDED_REASONING`
- `tools/workflows/testgen.py:198` - Returns `EXTENDED_REASONING`
- `tools/workflows/secaudit.py:108` - Returns `EXTENDED_REASONING`
- `tools/workflows/planner.py:154` - Returns `EXTENDED_REASONING`
- `tools/workflows/docgen.py:191` - Returns `EXTENDED_REASONING`
- `tools/workflows/consensus.py:185` - Returns `EXTENDED_REASONING`
- `tools/workflows/precommit.py:92` - Returns `EXTENDED_REASONING`

### The Tool Registry (`tools/registry.py`)

**33 tools total** organized by visibility:
- **ESSENTIAL (3):** status, chat, planner
- **CORE (8):** analyze, codereview, debug, refactor, testgen, thinkdeep, smart_file_query, smart_file_download
- **ADVANCED (7):** consensus, docgen, secaudit, tracer, precommit, kimi_chat_with_tools, glm_payload_preview
- **HIDDEN (16):** provider_capabilities, listmodels, activity, version, health, toolcall_log_tail, test_echo, kimi_capture_headers, kimi_intent_analysis, kimi_manage_files, glm_web_search, kimi_web_search

**Problem:** None of these tools leverage the CapabilityRouter for provider selection.

---

## Critical Issues

### Issue #1: Web Search Routing Bug

**Severity:** CRITICAL

**Location:** `tools/simple/base.py:369-396`

**Problem:** Tools can route web search requests to Kimi, even though:
- Kimi does NOT support web search (capability_router.py:45)
- GLM DOES support web search (capability_router.py:60)

**Evidence:**
```python
# tools/simple/base.py:391-396
if (model_name or "").strip().lower() == "auto":
    seed = registry_instance.get_preferred_fallback_model(self.get_model_category())
```

The `get_model_category()` method returns simple categories (FAST_RESPONSE, EXTENDED_REASONING, BALANCED) with NO awareness of web search requirements.

**Chat tool example:**
- `get_model_category()` returns `FAST_RESPONSE`
- This can route to Kimi (which doesn't support web search)
- Kimi receives web search request → Fails or produces wrong results

**Current Partial Fix:** Lines 546-558 and 646-658 check web search and route to GLM, but this is:
- Only checked when `use_web` is True
- Only used to set `effective_provider_type` (doesn't change the model context)
- Duplicated code in two places
- Not used for other capabilities

### Issue #2: Missing Capability Validation

**Severity:** HIGH

**Problem:** No validation that:
- Tools requesting images have providers with vision support
- Tools requesting thinking mode have providers that support it
- Tools requesting file uploads have providers with file upload support
- Tools requiring large context have providers with sufficient token limits

**Example - Vision Request:**
```python
# User sends image to chat tool
chat(prompt="Describe this image", images=["screenshot.png"])

# Current flow:
# 1. Gets model from category (FAST_RESPONSE)
# 2. May route to Kimi or GLM
# 3. NO CHECK: Does provider support vision?
# 4. If Kimi doesn't support vision → Error or wrong results
```

### Issue #3: Inefficient Model Selection

**Severity:** MEDIUM

**Problem:** The fallback chain system is static and doesn't consider:
- Request features (images, files, thinking mode)
- Provider capabilities (what each provider can actually do)
- Tool requirements (what the tool needs)

**Current (registry_selection.py:241-283):**
```python
def _fallback_chain(category):
    if cat_name == "FAST_RESPONSE":
        order = ["glm-4.6", "glm-4.5-flash", "glm-4.5"]
    elif cat_name == "EXTENDED_REASONING":
        order = ["kimi-k2-0905-preview", "kimi-k2-0711-preview", "kimi-thinking-preview"]
```

**Problem:** This is hardcoded and doesn't adapt to:
- Request having images (should check if provider supports vision)
- Request needing web search (should route to GLM)
- Provider not being available
- Model not supporting required features

### Issue #4: Duplicated Web Search Routing Code

**Severity:** LOW (but indicates architectural issues)

**Problem:** Lines 546-558 and 646-658 in `tools/simple/base.py` contain **nearly identical code** for web search routing:

```python
# First occurrence (lines 546-558)
if use_web:
    router = get_router()
    tool_name = getattr(self, 'tool_name', 'unknown')
    optimal_provider = router.get_optimal_provider(tool_name)
    if optimal_provider != ProviderType.AUTO:
        effective_provider_type = optimal_provider
        self.logger.info(f"[SMART_ROUTING] Tool '{tool_name}' requires web_search, routing to {optimal_provider.value}")

# Second occurrence (lines 646-658) - DUPLICATE!
if use_web:
    router = get_router()
    tool_name = getattr(self, 'tool_name', 'unknown')
    optimal_provider = router.get_optimal_provider(tool_name)
    if optimal_provider != ProviderType.AUTO:
        effective_provider_type = optimal_provider
        self.logger.info(f"[SMART_ROUTING] Tool '{tool_name}' requires web_search, routing to {optimal_provider.value}")
```

**Indicates:** The capability router logic was added in two different code paths without proper refactoring.

---

## Integration Opportunities

### Where to Connect CapabilityRouter

#### Opportunity 1: Tool Model Selection (High Priority)

**Current:** `tools/simple/base.py:391-396`
```python
if (model_name or "").strip().lower() == "auto":
    seed = registry_instance.get_preferred_fallback_model(self.get_model_category())
```

**Proposal:** Use capability router for auto mode:
```python
if (model_name or "").strip().lower() == "auto":
    router = get_router()
    tool_name = self.get_name()
    required_features = self._get_required_features_from_request(request)
    optimal_provider = router.get_optimal_provider(tool_name, required_features)

    if optimal_provider != ProviderType.AUTO:
        # Get model for specific provider
        seed = registry_instance.get_preferred_model_for_provider(optimal_provider)
    else:
        # Fall back to category-based selection
        seed = registry_instance.get_preferred_fallback_model(self.get_model_category())
```

#### Opportunity 2: Request Validation (High Priority)

**Location:** `tools/simple/base.py:359-367` (file path validation)

**Proposal:** Add capability validation:
```python
def execute():
    # Validate file paths
    path_error = self._validate_file_paths(request)
    if path_error:
        return error

    # NEW: Validate provider capabilities
    capability_error = self._validate_provider_capabilities(request)
    if capability_error:
        return capability_error
```

**Implementation:**
```python
def _validate_provider_capabilities(self, request):
    """Validate that provider supports required features"""
    from src.providers.capability_router import get_router

    tool_name = self.get_name()
    provider = self._model_context.provider
    router = get_router()

    validation = router.validate_request(
        tool_name=tool_name,
        provider=provider.get_provider_type(),
        has_images=bool(self.get_request_images(request)),
        has_files=bool(self.get_request_files(request)),
        thinking_mode=self.get_request_thinking_mode(request),
        use_websearch=self.get_request_use_websearch(request)
    )

    if not validation["valid"]:
        return f"Provider capability error: {validation['errors']}"

    if validation["warnings"]:
        # Log warnings but don't fail
        for warning in validation["warnings"]:
            self.logger.warning(warning)

    return None
```

#### Opportunity 3: Execution Path Routing (Medium Priority)

**Current:** `tools/simple/base.py:487-514` (building provider kwargs)

**Proposal:** Use ExecutionPath routing:
```python
def execute():
    # ... existing code ...

    # NEW: Determine execution path
    router = get_router()
    execution_path = router.route_request(
        tool_name=self.get_name(),
        provider=provider.get_provider_type(),
        streaming=provider_kwargs.get("stream", False),
        thinking_mode=thinking_mode,
        has_images=bool(images),
        has_files=bool(self.get_request_files(request))
    )

    # Adjust provider kwargs based on execution path
    if execution_path == ExecutionPath.VISION:
        provider_kwargs["vision_mode"] = True
    elif execution_path == ExecutionPath.THINKING:
        provider_kwargs["thinking_mode"] = thinking_mode
    elif execution_path == ExecutionPath.STREAMING:
        provider_kwargs["stream"] = True

    # ... rest of execution ...
```

#### Opportunity 4: Remove Duplicated Web Search Code (Low Priority)

**Current:** Lines 546-558 and 646-658 in `tools/simple/base.py`

**Proposal:** Create helper method:
```python
def _get_effective_provider_type(self, request, default_provider_type):
    """Get effective provider type considering capabilities"""
    use_web = self.get_request_use_websearch(request)
    if not use_web:
        return default_provider_type

    # Check if current provider supports web search
    router = get_router()
    tool_name = self.get_name()
    optimal_provider = router.get_optimal_provider(tool_name)

    if optimal_provider != ProviderType.AUTO and optimal_provider != default_provider_type:
        self.logger.info(f"[SMART_ROUTING] Tool '{tool_name}' requires web_search, routing to {optimal_provider.value}")
        return optimal_provider

    return default_provider_type
```

Then use this method in both places where web search routing is needed.

---

## Implementation Roadmap

### Phase 1: Critical Web Search Fix (1-2 days)

**Goal:** Fix the web search routing bug to prevent Kimi from receiving web search requests.

**Tasks:**

1. **Create smart provider selection helper** (`tools/simple/base.py`)
   - Add `_get_effective_provider_type()` method
   - Consolidate duplicated web search routing code
   - Call in both execution paths (lines ~530 and ~640)

2. **Test web search routing**
   - Ensure chat tool with `use_websearch=True` routes to GLM
   - Verify Kimi doesn't receive web search requests
   - Test with auto mode and explicit model selection

**Deliverable:** Web search bug fixed, no more Kimi web search failures.

### Phase 2: Auto Mode Integration (2-3 days)

**Goal:** Use CapabilityRouter for model selection in auto mode.

**Tasks:**

1. **Update auto mode logic** (`tools/simple/base.py:385-400`)
   - Get required features from request
   - Call `router.get_optimal_provider()` for auto mode
   - Fall back to category-based selection if no specific provider recommended

2. **Add feature detection helper**
   ```python
   def _get_required_features(self, request):
       """Determine required features from request"""
       features = []

       if self.get_request_images(request):
           features.append("vision")

       if self.get_request_use_websearch(request):
           features.append("web_search")

       thinking_mode = self.get_request_thinking_mode(request)
       if thinking_mode:
           features.append("thinking_mode")

       if self.get_request_files(request):
           features.append("file_uploads")

       return features
   ```

3. **Test auto mode routing**
   - Chat with images → Routes to provider with vision support
   - Chat with web search → Routes to GLM
   - Workflow tools → Routes based on requirements

**Deliverable:** Auto mode uses capability router for intelligent model selection.

### Phase 3: Request Validation (2-3 days)

**Goal:** Validate provider capabilities before making API calls.

**Tasks:**

1. **Add capability validation** (`tools/simple/base.py`)
   - Create `_validate_provider_capabilities()` method
   - Check vision, thinking mode, file upload, web search support
   - Check token limit requirements
   - Call after file path validation (line ~360)

2. **Handle validation failures**
   - Return clear error messages for unsupported features
   - Suggest alternative providers if available
   - Log validation warnings

3. **Test validation**
   - Send image to non-vision provider → Error message
   - Request thinking mode on unsupported model → Error or auto-switch
   - Request file upload on unsupported provider → Error message

**Deliverable:** No more "silent failures" when provider doesn't support requested features.

### Phase 4: Execution Path Optimization (3-4 days)

**Goal:** Use ExecutionPath routing for optimal execution strategies.

**Tasks:**

1. **Implement execution path selection**
   - Add `router.route_request()` call in execute flow
   - Adjust provider kwargs based on execution path
   - Optimize for streaming, thinking mode, vision, etc.

2. **Update provider methods**
   - Add execution path parameters to provider interface
   - Implement path-specific optimizations
   - Add path-based logging

3. **Test execution paths**
   - Verify vision path is used for image requests
   - Verify thinking path is used for complex reasoning
   - Verify streaming path is used for supported tools

**Deliverable:** Tools use optimal execution paths based on capabilities and requirements.

### Phase 5: Documentation & Cleanup (1-2 days)

**Goal:** Clean up and document the integrated routing system.

**Tasks:**

1. **Remove duplicated code**
   - Consolidate web search routing into helper method
   - Remove duplicate code paths
   - Simplify execute() method

2. **Update documentation**
   - Document new routing flow
   - Add examples of capability-aware routing
   - Update troubleshooting guide

3. **Add monitoring**
   - Log routing decisions
   - Track capability validation failures
   - Monitor execution path usage

**Deliverable:** Clean, documented, maintainable routing system.

---

## Technical Considerations

### Backward Compatibility

**Must maintain:**
- Existing `get_model_category()` API for tools
- Auto mode behavior (should improve, not break)
- Explicit model selection (should still work)
- All existing tool interfaces

**Can change:**
- Internal routing logic
- Provider selection algorithm
- Error messages for unsupported features

### Testing Strategy

1. **Unit Tests**
   - `test_capability_router.py` - Test router methods
   - `test_smart_routing.py` - Test integration with BaseTool
   - `test_provider_selection.py` - Test model selection logic

2. **Integration Tests**
   - Tool execution with different providers
   - Auto mode with various request types
   - Feature validation edge cases

3. **E2E Tests**
   - Full tool workflows with capability routing
   - Web search bug fix verification
   - Performance testing (ensure no regressions)

### Performance Impact

**Expected:** Minimal impact, potentially positive.

**Reasoning:**
- CapabilityRouter is lightweight (441 lines, simple operations)
- Caching already exists (routing_cache in registry_selection.py)
- May reduce API call failures (better provider selection)
- May reduce latency (smarter first-choice models)

**Monitoring:**
- Time to first response
- API call success rate
- Fallback chain usage
- Provider selection accuracy

---

## Conclusion

The EX-AI MCP Server has a sophisticated, well-designed `CapabilityRouter` that is largely unused. The current routing system relies on simple, hardcoded categories that don't consider provider capabilities or tool requirements. This creates a critical gap where:

1. **Web search requests can fail** (routed to Kimi which doesn't support it)
2. **Tools may request unsupported features** (no validation)
3. **Model selection is suboptimal** (no capability awareness)
4. **400+ lines of smart routing code sits idle**

**The Solution:** Integrate the CapabilityRouter into the main execution flow, starting with:
1. Fixing the web search bug (Phase 1)
2. Using it for auto mode model selection (Phase 2)
3. Adding request validation (Phase 3)
4. Optimizing execution paths (Phase 4)

**Expected Outcome:**
- ✅ No more web search failures
- ✅ Intelligent provider selection
- ✅ Better tool reliability
- ✅ Fully utilizing existing architecture
- ✅ Technical debt reduced

**Effort Estimate:** 8-14 days for full implementation (5 phases)

---

## References

**Key Files:**
- `src/providers/capability_router.py` - Unused sophisticated router (441 lines)
- `src/providers/registry_selection.py` - Currently used simple routing (525 lines)
- `tools/simple/base.py` - Tool base class, main execution flow
- `tools/registry.py` - Tool registry (33 tools)
- `tools/models.py` - Tool model categories (FAST_RESPONSE, EXTENDED_REASONING, BALANCED)

**Code Locations:**
- Web search routing: `tools/simple/base.py:546-558` and `tools/simple/base.py:646-658` (duplicated)
- Model selection: `tools/simple/base.py:391-396`
- Tool categories: Various `get_model_category()` methods in tools
- Capability definitions: `src/providers/capability_router.py:30-246`
- Fallback chains: `src/providers/registry_selection.py:241-283`

**Bug Fixes:**
- Web search routing: `src/providers/capability_router.py:363-365` (already implemented but unused)

---

**Document Version:** 1.0
**Last Updated:** 2025-11-10
**Next Review:** After Phase 1 implementation
