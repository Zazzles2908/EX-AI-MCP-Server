# DEPENDENCY MAP - EX-AI-MCP-SERVER
**Date:** 2025-10-13  
**Purpose:** Visual map of what depends on what for safe refactoring  
**Source:** Phase 0, 1, 2 architecture analysis

---

## EXECUTIVE SUMMARY

**Architecture:** Clean 4-tier layered architecture  
**Base Classes:** 3 (BaseTool, SimpleTool, WorkflowTool)  
**Mixins:** 13 shared behavior modules  
**Circular Dependencies:** NONE ✅  
**Critical Paths:** 5 identified

This dependency map shows what can be changed safely and what will have wide-reaching impact.

---

## 🎯 4-TIER ARCHITECTURE

```
┌────────────────────────────────────────────────────────────────┐
│ TIER 1: FOUNDATION (utils/)                                   │
│ - File utilities (9 modules)                                  │
│ - Conversation management (4 modules)                         │
│ - Model utilities (4 modules)                                 │
│ - Infrastructure (observability, progress, cache, metrics)    │
│                                                                │
│ IMPACT: Changes here affect ALL tools                         │
│ RISK: HIGH - Core functionality                               │
└────────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────────┐
│ TIER 2: SHARED INFRASTRUCTURE (tools/shared/)                 │
│ - BaseTool (base class for ALL tools)                        │
│ - Base mixins (3 mixins)                                      │
│ - File handling (26.5KB - used by 20+ tools)                 │
│ - Model management (24.4KB - used by 20+ tools)              │
│                                                                │
│ IMPACT: Changes here affect 20+ tools                         │
│ RISK: HIGH - Wide impact radius                               │
└────────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────────┐
│ TIER 3: TOOL FRAMEWORKS (tools/simple/, tools/workflow/)      │
│                                                                │
│ SimpleTool Framework:                                          │
│ - SimpleTool base class (55.3KB)                             │
│ - 5 mixins (continuation, streaming, tool_call, web_search)  │
│ - IMPACT: Changes affect 4 simple tools                       │
│ - RISK: MEDIUM - Bounded impact                               │
│                                                                │
│ WorkflowTool Framework:                                        │
│ - WorkflowTool base class (30.5KB)                           │
│ - ExpertAnalysisMixin (34.1KB - CRITICAL)                    │
│ - OrchestrationMixin (26.9KB)                                │
│ - 5 other mixins (file_embedding, conversation, etc.)        │
│ - IMPACT: Changes affect 12 workflow tools                    │
│ - RISK: HIGH - Complex interactions                           │
└────────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────────┐
│ TIER 4: TOOL IMPLEMENTATIONS                                  │
│                                                                │
│ SimpleTool Implementations (4):                                │
│ - chat, challenge, activity, [18 tools total]                │
│                                                                │
│ WorkflowTool Implementations (12):                             │
│ - analyze, codereview, debug, testgen, thinkdeep, refactor   │
│ - secaudit, precommit, docgen, tracer, consensus, planner    │
│                                                                │
│ IMPACT: Changes here are isolated                             │
│ RISK: LOW - Single tool affected                              │
└────────────────────────────────────────────────────────────────┘
```

---

## 📊 CRITICAL DEPENDENCIES

### High-Impact Components (Changes Affect 10+ Files)

| Component | Type | Imports | Used By | Impact Radius |
|-----------|------|---------|---------|--------------|
| **BaseTool** | Base Class | 30+ files | ALL tools (29) | 🔴 CRITICAL |
| **progress.py** | Utility | 30 files | Tools, daemon | 🔴 CRITICAL |
| **observability.py** | Utility | 21 files | Tools, daemon | 🔴 HIGH |
| **ExpertAnalysisMixin** | Mixin | 12 files | All workflows | 🔴 HIGH |
| **conversation_memory.py** | Utility | 15 files | Tools, daemon | 🟡 MEDIUM |
| **model_context.py** | Utility | 14 files | Tools, providers | 🟡 MEDIUM |

### Medium-Impact Components (Changes Affect 5-10 Files)

| Component | Used By | Impact |
|-----------|---------|--------|
| **SimpleTool** | 4 simple tools | 🟡 MEDIUM |
| **WorkflowTool** | 12 workflow tools | 🔴 HIGH (complex) |
| **cache.py** | Daemon, tools | 🟡 MEDIUM |
| **client_info.py** | Request handler | 🟡 MEDIUM |

### Low-Impact Components (Changes Affect 1-4 Files)

| Component | Used By | Impact |
|-----------|---------|--------|
| Tool implementations | Self only | 🟢 LOW |
| Specific mixins | 1-2 tools | 🟢 LOW |
| Config utilities | Config loading | 🟢 LOW |

---

## 🔄 DEPENDENCY FLOW DIAGRAM

### Complete Request Flow with Dependencies

```
┌─────────────┐
│ User (IDE)  │
└─────────────┘
       ↓ uses MCP protocol
┌─────────────────────────────────────────────────────────┐
│ MCP Shim (scripts/run_ws_shim.py)                      │
│ DEPENDS ON: websockets, json, os.getenv                │
└─────────────────────────────────────────────────────────┘
       ↓ WebSocket connection
┌─────────────────────────────────────────────────────────┐
│ WebSocket Daemon (src/daemon/ws_server.py)             │
│ DEPENDS ON:                                             │
│  - session_manager (session lifecycle)                 │
│  - request coalescing (semantic caching)               │
│  - utils/observability.py (logging)                    │
│  - utils/cache.py (caching)                            │
│  - .env configuration                                   │
└─────────────────────────────────────────────────────────┘
       ↓ Tool call
┌─────────────────────────────────────────────────────────┐
│ Request Handler (src/server/handlers/request_handler)  │
│ DEPENDS ON:                                             │
│  - tool_registry (tool discovery)                      │
│  - conversation_memory (context reconstruction)        │
│  - utils/progress.py (progress tracking)               │
│  - utils/model_context.py (model selection)            │
└─────────────────────────────────────────────────────────┘
       ↓ Execute tool
┌─────────────────────────────────────────────────────────┐
│ Tool Execution (SimpleTool OR WorkflowTool)             │
│                                                          │
│ SimpleTool DEPENDS ON:                                  │
│  ├─ BaseTool (tools/shared/base_tool.py)              │
│  ├─ File handling mixin (base_tool_file_handling.py)  │
│  ├─ Model management (base_tool_model_management.py)  │
│  ├─ Continuation mixin (continuation_mixin.py)        │
│  ├─ Web search mixin (web_search_mixin.py)            │
│  ├─ utils/file/* (file operations)                     │
│  └─ utils/conversation/* (conversation state)          │
│                                                          │
│ WorkflowTool DEPENDS ON:                                │
│  ├─ BaseTool (tools/shared/base_tool.py)              │
│  ├─ WorkflowMixin (base workflow functionality)       │
│  ├─ ExpertAnalysisMixin (expert validation) 🔴        │
│  ├─ OrchestrationMixin (step management)              │
│  ├─ FileEmbeddingMixin (embed project files)          │
│  ├─ ConversationIntegrationMixin (conversation)       │
│  └─ All utils dependencies                             │
└─────────────────────────────────────────────────────────┘
       ↓ Call provider
┌─────────────────────────────────────────────────────────┐
│ Provider Layer (src/providers/)                         │
│ DEPENDS ON:                                             │
│  - registry (provider selection)                       │
│  - kimi.py OR glm.py (provider implementation)         │
│  - utils/observability.py (telemetry)                  │
│  - circuit breaker (if enabled)                        │
└─────────────────────────────────────────────────────────┘
       ↓ HTTP request
┌─────────────────────────────────────────────────────────┐
│ AI Provider API (Kimi or GLM)                          │
└─────────────────────────────────────────────────────────┘
```

---

## 🔴 CRITICAL PATH: AUTH TOKEN VALIDATION

**User Issue:** "Invalid auth token" warnings

### Dependency Chain

```
User/IDE
    ↓
MCP Shim (run_ws_shim.py)
    ├─ Reads: .env (EXAI_WS_TOKEN)
    ├─ Creates: hello message with token
    └─ Sends: WebSocket message to daemon
        ↓
WebSocket Daemon (ws_server.py)
    ├─ Reads: .env (EXAI_WS_TOKEN) ← CRITICAL: Must load .env!
    ├─ Receives: hello message
    ├─ Validates: received token == expected token
    ├─ If valid: Creates session
    └─ If invalid: Logs warning, closes connection
```

### Files Involved (Priority Order)

1. **`.env`** - Token configuration
   - Variable: `EXAI_WS_TOKEN`
   - Current: `test-token-12345`
   - Impact: Must match between shim and daemon

2. **`scripts/run_ws_shim.py`** - Token sender
   - Reads token from .env
   - Includes in hello handshake
   - Impact: If token wrong here, auth fails

3. **`src/daemon/ws_server.py`** - Token validator
   - MUST load .env before validation
   - Compares received vs expected
   - Impact: If .env not loaded, validation always fails

4. **`src/bootstrap/logging_setup.py`** - Config loading
   - May contain .env loading
   - Impact: If .env loaded here, ws_server must import

### Dependencies That Could Break Auth

- **Environment loading order:** .env must load before auth validation
- **Token caching:** Old clients may cache wrong token
- **Race conditions:** Token validation before hello received
- **Configuration mismatch:** Different .env files in different directories

---

## 🔴 CRITICAL PATH: FILE EMBEDDING

**User Issue:** 48 files embedded for simple test

### Dependency Chain

```
User Request
    ↓
Tool Execution (analyze, codereview, etc.)
    ↓
ExpertAnalysisMixin._call_expert_analysis()
    ├─ Checks: EXPERT_ANALYSIS_INCLUDE_FILES env var
    ├─ If true: Calls file embedding
    └─ Passes files to expert analysis
        ↓
FileEmbeddingMixin.embed_files()
    ├─ Expands: File patterns (e.g., "docs/**/*.md")
    ├─ Reads: All matching files
    └─ Embeds: File contents in prompt
        ↓
BaseToolFileHandling._process_files()
    ├─ Reads: File contents
    ├─ Counts: Tokens
    └─ Logs: Files to be embedded
```

### Files Involved (Priority Order)

1. **`tools/workflow/expert_analysis.py`** - File inclusion decision
   - Reads: `EXPERT_ANALYSIS_INCLUDE_FILES`
   - Decides: Whether to include files
   - Impact: Controls if files are embedded

2. **`tools/workflow/file_embedding.py`** - File expansion
   - Expands: Glob patterns
   - Impact: How many files are included

3. **`tools/shared/base_tool_file_handling.py`** - File processing
   - Reads: File contents
   - Counts: Tokens
   - Impact: Actual embedding

4. **`.env`** - Configuration
   - Variables:
     - `EXPERT_ANALYSIS_INCLUDE_FILES` (currently: false)
     - `EXPERT_ANALYSIS_MAX_FILES` (missing!)
     - `EXPERT_ANALYSIS_MAX_CONTENT_KB` (missing!)

### Dependencies That Could Break File Handling

- **Missing limits:** No MAX_FILES or MAX_KB configured
- **Aggressive expansion:** Glob patterns too broad
- **No relevance filtering:** All matching files included
- **Ignored configuration:** Settings not respected

---

## 🔴 CRITICAL PATH: EXPERT ANALYSIS

**User Issue:** Progress shows 2%, completes in 5s

### Dependency Chain

```
WorkflowTool.execute()
    ↓
ExpertAnalysisMixin._call_expert_analysis()
    ├─ Creates: asyncio.create_task()
    ├─ Polls: task.done() in loop
    ├─ Reports: Progress every 5 seconds
    └─ Retrieves: task.result() when done
        ↓
Provider.generate_content()
    ├─ Calls: Kimi or GLM API
    ├─ Waits: For response
    └─ Returns: ModelResponse
```

### Files Involved (Priority Order)

1. **`tools/workflow/expert_analysis.py`** - Polling loop
   - Line ~657: Polling interval (was 5s, now 0.1s after recent fix)
   - Progress calculation
   - ETA calculation
   - Impact: Progress accuracy

2. **`src/providers/kimi.py` or `glm.py`** - API call
   - Actual API execution time
   - Impact: Real completion time

### Dependencies That Could Break Progress

- **Polling interval too long:** Can't detect completion fast enough
- **Progress calculation wrong:** Linear estimate vs event-driven
- **ETA based on default:** Doesn't account for actual model speed
- **No feedback from provider:** Can't update progress dynamically

---

## 🔴 CRITICAL PATH: MODEL SELECTION

**User Issue:** Model auto-upgraded without consent

### Dependency Chain

```
Tool Execution
    ↓
ExpertAnalysisMixin._call_expert_analysis()
    ├─ Checks: Does model support thinking mode?
    ├─ If no: Auto-upgrades to glm-4.6
    └─ Logs: "Auto-upgrading..."
        ↓
Provider Selection
    ├─ Uses: Upgraded model
    └─ Calls: API with different model than requested
```

### Files Involved (Priority Order)

1. **`tools/workflow/expert_analysis.py`** - Auto-upgrade logic
   - Model capability checking
   - Auto-upgrade decision
   - Impact: Which model is actually used

2. **`src/providers/registry_selection.py`** - Model routing
   - Model preference system
   - Fallback logic
   - Impact: Provider selection

3. **`.env`** - Configuration
   - Variables:
     - `KIMI_PREFERRED_MODELS`
     - `GLM_PREFERRED_MODELS`
     - `EXPERT_ANALYSIS_AUTO_UPGRADE` (missing!)

### Dependencies That Could Break Model Selection

- **No user control:** Auto-upgrade not configurable
- **Silent changes:** User not warned about upgrade
- **Cost implications:** Different models have different costs
- **Performance impact:** Different models have different speeds

---

## 📊 TASK DEPENDENCIES

### Phase A: Stabilize

```
Task A.1 (Auth Token)
    ↓ BLOCKS
Task A.2 (Fix Issues 7-10)
    ↓ BLOCKS
Task A.3 (Verify Stability)
    ↓ EXIT GATE
Phase B: Cleanup
```

### Phase B: Cleanup

```
Phase A Complete
    ↓ ENABLES
Task B.1 (WorkflowTools Testing)
    ↓ BLOCKS
Task B.2 (Integration Testing)
    ↓ BLOCKS
Task B.3 (Expert Validation)
    ↓ EXIT GATE
Phase C: Optimize
```

### Phase C: Optimize

```
Phase B Complete
    ↓ ENABLES
Task C.1 (Performance Benchmarking) ─┐
Task C.2 (Documentation)             ├─ PARALLEL
Task C.3 (Testing Coverage)          ┘
    ↓ EXIT GATE (User decides)
Phase D: Refactor (Optional)
```

---

## 🎯 SAFE CHANGE MATRIX

### Can Change Safely (Low Risk)

| Component | Why Safe | Testing Required |
|-----------|----------|------------------|
| Tool implementations | Isolated impact | Tool-specific tests |
| Configuration values | Externalized | Integration tests |
| Logging statements | Side-effect only | Visual verification |
| Documentation | No code impact | None |

### Change with Caution (Medium Risk)

| Component | Why Risky | Testing Required |
|-----------|-----------|------------------|
| SimpleTool base | Affects 4 tools | All 4 tools tested |
| Provider logic | Affects all API calls | All providers tested |
| File utilities | Used by many tools | File handling tests |
| Conversation utils | Used by daemon + tools | Conversation tests |

### High Risk Changes (Requires Thorough Testing)

| Component | Why Very Risky | Testing Required |
|-----------|----------------|------------------|
| **BaseTool** | Affects ALL 29 tools | Full test suite |
| **ExpertAnalysisMixin** | Affects 12 workflows | All workflow tests |
| **WebSocket daemon** | Affects all connections | Stress testing |
| **Auth validation** | Security critical | Security testing |
| **Request handler** | All requests flow through | Integration tests |

---

## 📝 REFACTORING SAFETY RULES

### Rule 1: Preserve Public Interfaces

**NEVER change:**
- Public method signatures
- Class inheritance chain
- Exported constants
- Configuration variable names

**CAN change:**
- Internal implementations
- Private methods
- Code organization
- Internal variable names

### Rule 2: Test Before and After

**MUST test:**
- All tools that use changed component
- All code paths through changed component
- Error handling in changed component
- Configuration loading for changed component

### Rule 3: Document Dependencies

**MUST document:**
- What depends on this component
- What this component depends on
- Why this component exists
- What happens if it breaks

### Rule 4: Incremental Changes

**MUST:**
- Change one component at a time
- Test after each change
- Commit after each success
- Keep rollback option available

---

## 🔗 CROSS-CUTTING CONCERNS

### Observability

**Used By:** Everything  
**Files:** `utils/observability.py`, `utils/metrics.py`, `utils/health.py`  
**Impact:** Logs, metrics, health checks  
**Risk:** Medium - Wide usage but side-effect only

### Configuration

**Used By:** All components  
**Files:** `.env`, `src/config/*`, `utils/config/*`  
**Impact:** Behavior of all components  
**Risk:** High - Misconfiguration can break system

### Error Handling

**Used By:** All layers  
**Pattern:** Try/catch at each layer  
**Impact:** Error propagation and logging  
**Risk:** Medium - Important for debugging

### Caching

**Used By:** Daemon, tools  
**Files:** `utils/cache.py`, daemon request coalescing  
**Impact:** Performance, response time  
**Risk:** Low - Can be disabled if problematic

---

## ✅ DEPENDENCY CHECKLIST

Before changing any component, check:

- [ ] What files import this component?
- [ ] What does this component import?
- [ ] What will break if this changes?
- [ ] What tests cover this component?
- [ ] What configuration affects this?
- [ ] What logs/metrics track this?
- [ ] What documentation describes this?
- [ ] Is there a rollback plan?

---

**NEXT ACTION:** Use this map when working on GOD_CHECKLIST tasks  
**KEY INSIGHT:** Most issues are in high-impact components - requires careful testing
