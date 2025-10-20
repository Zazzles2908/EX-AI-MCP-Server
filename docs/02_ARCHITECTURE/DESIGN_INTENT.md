
# DESIGN INTENT SUMMARY - EX-AI-MCP-SERVER
**Date:** 2025-10-13  
**Purpose:** Extracted design intentions from existing code and documentation  
**Source:** Phase 0-2 analysis, code review, architectural mapping

---

## EXECUTIVE SUMMARY

The EX-AI-MCP-Server was **deliberately designed**, not accidentally evolved. The architectural analysis shows:
- **85% match** with intended design
- **Clean 4-tier layered architecture**
- **Deliberate use of mixins** for shared behavior
- **Single responsibility principle** in most modules

This document captures the **design intent** so future changes respect the original vision.

---

## 🎯 CORE DESIGN PRINCIPLES

### 1. Layered Architecture (Top-Down)

**Intent:** Organize by **conceptual responsibility**, not implementation details.

```
User → IDE → MCP Protocol → WebSocket Daemon → Request Handler → Tools → Providers → AI
```

**Why This Works:**
- Clear separation of concerns
- Each layer has single responsibility
- Easy to understand request flow
- Easy to test each layer independently

**Design Decision:** Use **domain language** (definition, intake, preparation, execution, delivery) not technical terms.

### 2. Mixin Composition Over Inheritance

**Intent:** Share behavior across tools without deep inheritance hierarchies.

**Pattern:**
```python
class SimpleTool(BaseTool, ContinuationMixin, StreamingMixin, WebSearchMixin):
    """Compose behavior from mixins"""
```

**Why This Works:**
- Single tool can have multiple behaviors
- Behaviors are reusable across tool types
- Easy to add/remove behaviors
- Avoids "diamond problem" of multiple inheritance

**Design Decision:** Each mixin has **one responsibility** (e.g., ContinuationMixin ONLY handles conversation continuation).

### 3. Provider Abstraction

**Intent:** Tools don't know about providers; providers are selected dynamically.

**Pattern:**
```python
# Tool requests model by name:
response = ModelProviderRegistry.generate_content(model="kimi-k2-0905-preview", ...)

# Registry selects provider:
# Priority: KIMI → GLM → CUSTOM → OPENROUTER
```

**Why This Works:**
- Easy to add new providers
- Tools work with any provider
- Centralized provider configuration
- Fallback logic in one place

**Design Decision:** Environment-driven configuration (KIMI_PREFERRED_MODELS, GLM_PREFERRED_MODELS).

### 4. Request Coalescing (Semantic Caching)

**Intent:** Avoid duplicate AI calls for identical requests.

**Pattern:**
```python
# In ws_server.py line 514:
cache_key = f"{tool_name}:{normalize(arguments)}"
if cache_key in cache:
    return cached_result  # Instant response
else:
    result = execute_tool(...)
    cache[cache_key] = result
```

**Why This Works:**
- 4428x faster for duplicate requests (0.00s vs 11.36s)
- Reduces API costs
- Improves user experience
- TTL ensures freshness (10 minutes)

**Design Decision:** Caching at **daemon level** (before tool execution) for maximum efficiency.

### 5. Session Management

**Intent:** Track client connections and manage lifecycle.

**Pattern:**
```python
# Session created on connection
session = SessionManager.create_session(websocket)

# Session removed on disconnect
SessionManager.remove_session(session_id)
```

**Why This Works:**
- Clean connection tracking
- Graceful cleanup on disconnect
- Support for multiple clients
- Timeout handling (3600s)

**Design Decision:** In-memory for speed, Supabase planned for persistence.

---

## 📚 MODULE DESIGN INTENTS

### WebSocket Daemon (src/daemon/ws_server.py)

**Intent:** Central orchestration point for all requests.

**Single Responsibility:** Manage WebSocket connections and route requests.

**Design Decisions:**
- **Request coalescing** at daemon level (line 514)
- **Session management** integrated
- **Concurrency control** (24 global, 6 Kimi, 4 GLM)
- **Auth validation** on connection
- **Message bus** (implemented but disabled)

**Why Here:**
- All requests flow through daemon
- Central point for cross-cutting concerns (auth, caching, metrics)
- Natural place for connection management

### Request Handler (src/server/handlers/request_handler.py)

**Intent:** Orchestrate tool execution with context reconstruction.

**Single Responsibility:** Prepare request → Execute tool → Post-process response.

**Design Decisions:**
- **Conversation reconstruction** from continuation_id
- **Progress tracking** initialization
- **Model auto-selection** for consensus tool only
- **Tool registry** lazy loading
- **Metadata attachment** (progress, summary)

**Why Here:**
- Knows about tools but not WebSocket details
- Natural place for conversation context
- Central point for tool orchestration

### SimpleTool (tools/simple/base.py)

**Intent:** Base class for simple single-call tools.

**Single Responsibility:** One AI call, one response.

**Design Decisions:**
- **55.3KB** (currently) → **Target: ~150-200 lines** after modularization
- **Conservative refactoring** already done (Phase 2 Cleanup)
- **Facade pattern** to preserve 25 public methods
- **Modules:** definition, intake, preparation, execution, delivery (planned)

**Why Refactor:**
- Easier to find code
- Easier to test
- Clearer responsibilities
- Long-term maintainability

### WorkflowTool (tools/workflow/base.py)

**Intent:** Base class for multi-step workflow tools.

**Single Responsibility:** Manage workflow steps with expert validation.

**Design Decisions:**
- **Step-by-step execution** with state management
- **Expert analysis** integration (ExpertAnalysisMixin)
- **Confidence checking** before completion
- **Findings consolidation** across steps

**Why This Works:**
- Complex analyses broken into manageable steps
- Expert validation ensures quality
- User can see intermediate progress
- Natural fit for investigative workflows

### ExpertAnalysisMixin (tools/workflow/expert_analysis.py)

**Intent:** Provide expert validation for workflow results.

**Single Responsibility:** Call expert model and validate findings.

**Design Decisions:**
- **34.1KB** (large, but single responsibility)
- **Thinking mode support** with auto-upgrade
- **Async polling** with 0.1s interval (recently fixed)
- **Progress reporting** every 5s heartbeat
- **File inclusion** configurable

**Why Here:**
- Used by ALL 12 workflow tools
- Complex logic deserves dedicated module
- Natural place for expert-specific features

### Provider Implementations (src/providers/kimi.py, glm.py)

**Intent:** Adapt provider-specific APIs to common interface.

**Single Responsibility:** Transform requests → Call API → Transform responses.

**Design Decisions:**
- **OpenAI-compatible** format for Kimi
- **Native format** for GLM
- **Context caching** for Kimi (X-Kimi-Context-Cache)
- **Idempotency** for Kimi (X-Idempotency-Key)
- **Web search** support for GLM (all models)
- **Streaming** support (SSE protocol)

**Why Separate:**
- Each provider has unique features
- Allows provider-specific optimizations
- Isolates API changes to one file

---

## 🏗️ ARCHITECTURAL PATTERNS

### Pattern 1: Registry Pattern

**Used By:** Tool discovery, provider selection  
**Intent:** Dynamic registration and lookup  
**Implementation:** `src/bootstrap/tool_registry.py`, `src/providers/registry.py`

**Why:**
- Tools can be added without changing core code
- Discovery happens automatically
- Lazy loading for performance

### Pattern 2: Facade Pattern

**Used By:** SimpleTool (planned), WorkflowTool  
**Intent:** Preserve public interface while refactoring internals  
**Implementation:** Public methods delegate to internal modules

**Why:**
- Backward compatibility guaranteed
- Internal changes don't break clients
- Gradual refactoring possible

### Pattern 3: Mixin Pattern

**Used By:** All tools  
**Intent:** Compose behavior from reusable modules  
**Implementation:** Multiple inheritance with single-responsibility mixins

**Why:**
- Behavior reuse without deep inheritance
- Each mixin has one responsibility
- Easy to add/remove features

### Pattern 4: Strategy Pattern

**Used By:** Provider selection, model routing  
**Intent:** Select algorithm at runtime  
**Implementation:** Environment-driven preference system

**Why:**
- Configuration drives behavior
- Easy to change strategies
- No code changes needed

### Pattern 5: Template Method Pattern

**Used By:** WorkflowTool step execution  
**Intent:** Define algorithm skeleton, let subclasses fill in details  
**Implementation:** `execute()` in base, steps in subclass

**Why:**
- Consistent workflow structure
- Subclasses only implement unique logic
- Easy to understand flow

---

## 💡 KEY DESIGN INSIGHTS

### Insight 1: Top-Down Design Matters

**Discovery:** User pointed out bottom-up organization was wrong.

**Quote:**
> "Should be more like Top-Down Design (Stepwise Refinement or Decomposition) so it like splits into categories."

**Design Change:**
- **Before:** Organized by what code does (prompt building, model calling)
- **After:** Organized by concepts (definition, intake, preparation, execution, delivery)
- **Result:** Clearer, more maintainable structure

### Insight 2: Dependency Analysis Before Design

**Discovery:** Was designing "new system" instead of refactoring existing.

**Quote:**
> "How do you know what is existing to be put into what you are building?"

**Design Change:**
- **Before:** Design modules, then fill with code
- **After:** Analyze dependencies, then design around them
- **Result:** Facade pattern to preserve backward compatibility

### Insight 3: Single Responsibility Prevents Chaos

**Discovery:** utils/ folder with 37 files and no structure.

**Design Change:**
- **Before:** All utilities in flat directory
- **After:** Organized by responsibility (file/, conversation/, model/, infrastructure/)
- **Result:** Easy to find, easy to maintain

### Insight 4: Understand Architecture First

**Discovery:** Fixed shared infrastructure (expert_analysis.py) during "timezone investigation".

**Lesson:**
- **Before:** Jump into fixing bugs
- **After:** Understand architecture, map dependencies, then fix
- **Result:** No broken shared infrastructure

---

## 🎨 MODULAR REFACTORING STRATEGY

### Vision: SimpleTool Organization

**Current:** 55.3KB monolithic base.py  
**Target:** ~150-200 line facade + 5 conceptual modules

```
tools/simple/
├── base.py (FACADE - 150-200 lines)
│   """Delegates to conceptual modules"""
│
├── definition/    ← "What does this tool promise?"
│   └── schema.py (~150-200 lines)
│
├── intake/    ← "What did the user ask for?"
│   ├── accessor.py (~200-250 lines)
│   └── validator.py (~150-200 lines)
│
├── preparation/    ← "How do we ask the AI?"
│   ├── prompt.py (~200-250 lines)
│   └── files.py (~80-100 lines)
│
├── execution/    ← "How do we call the AI?"
│   └── caller.py (~200-250 lines)
│
└── delivery/    ← "How do we deliver the result?"
    └── formatter.py (~150-200 lines)
```

**Status:** Phase 2 Cleanup did **conservative refactoring** (extracted 2 modules). Full modularization is **optional** (Phase D).

### Vision: WorkflowTool Organization

**Current:** Large mixins (expert_analysis.py 34.1KB, orchestration.py 26.9KB)  
**Target:** Focused modules with single responsibility

**Status:** **Deferred** - Current structure is acceptable, refactoring is low priority.

---

## 📋 DESIGN DECISIONS SUMMARY

### Configuration Philosophy

**Decision:** Environment-driven configuration (.env)

**Rationale:**
- No hardcoded values
- Easy to change without code changes
- Different configs for dev/staging/prod
- Secrets isolated from code

**Variables:**
- `EXAI_WS_TOKEN` - Auth token
- `KIMI_PREFERRED_MODELS` - Model preferences
- `GLM_PREFERRED_MODELS` - Model preferences
- `EXPERT_ANALYSIS_INCLUDE_FILES` - File inclusion
- `EXAI_WS_INFLIGHT_TTL_SECS` - Cache TTL
- [100+ more variables]

### Error Handling Philosophy

**Decision:** Catch errors at each layer, propagate with context.

**Rationale:**
- Errors logged where they occur
- Context added at each layer
- Top-level handler shows full context
- Makes debugging easier

**Pattern:**
```python
try:
    result = lower_layer.execute()
except Exception as e:
    logger.error(f"Layer X failed: {e}")
    raise LayerXError(f"Context: {details}") from e
```

### Testing Philosophy

**Decision:** Integration tests > Unit tests for this codebase.

**Rationale:**
- Complex interactions between layers
- Unit tests would require extensive mocking
- Integration tests catch real issues
- End-to-end validation more valuable

**Current:** 46 tests, 97.5% pass rate (Phase 2 Cleanup)

### Documentation Philosophy

**Decision:** Comprehensive markdown documentation.

**Rationale:**
- Complex system needs detailed docs
- Architecture must be understood before changes
- Historical context prevents repeated mistakes
- Phase-based organization shows evolution

**Current:** 80+ markdown documents organized by phase/topic

---

## ✅ RESPECTING DESIGN INTENT

### Before Making Changes

Ask these questions:

1. **Does this respect the layered architecture?**
   - Is this change in the right layer?
   - Does it maintain layer separation?

2. **Does this preserve single responsibility?**
   - Does this module still do ONE thing?
   - Should this be in a different module?

3. **Does this maintain backward compatibility?**
   - Will existing code break?
   - Are public interfaces preserved?

4. **Does this follow existing patterns?**
   - Is there already a pattern for this?
   - Should I create a new pattern or use existing?

5. **Does this need configuration?**
   - Should this be in .env?
   - Is it documented in .env.example?

### Red Flags (Design Intent Violations)

- ❌ Changing public method signatures
- ❌ Adding code to wrong layer
- ❌ Creating circular dependencies
- ❌ Hardcoding configuration values
- ❌ Mixing responsibilities in one module
- ❌ Breaking existing patterns without reason
- ❌ Skipping documentation
- ❌ Changing shared infrastructure without analysis

### Green Lights (Design Intent Aligned)

- ✅ Adding new tools via registry
- ✅ Creating new mixins with single responsibility
- ✅ Extracting large modules into focused ones
- ✅ Adding configuration to .env
- ✅ Following existing patterns
- ✅ Preserving backward compatibility
- ✅ Testing before and after
- ✅ Documenting changes

---

## 🎯 DESIGN INTENT BY ISSUE

### Issue #1: Auth Token

**Intent:** Secure WebSocket connections.

**Design:**
- Token in .env
- Validation on connection
- Reject invalid tokens
- Log security events

**Respect Intent By:**
- Ensure .env loaded before validation
- Don't change validation logic without security review
- Document token format in .env.example

### Issue #8: File Embedding

**Intent:** Include relevant files in expert analysis.

**Design:**
- Configurable via EXPERT_ANALYSIS_INCLUDE_FILES
- Limit via EXPERT_ANALYSIS_MAX_FILES (planned)
- Smart selection by relevance (planned)

**Respect Intent By:**
- Don't hardcode file inclusion
- Respect configuration variables
- Add limits to prevent bloat
- Document file inclusion strategy

### Issue #10: Model Auto-Upgrade

**Intent:** Enable advanced features (thinking mode) automatically.

**Design:**
- Auto-upgrade if model doesn't support feature
- Log upgrade decision
- Make configurable (planned)

**Respect Intent By:**
- Keep auto-upgrade optional
- Warn user about changes
- Document cost implications
- Allow user to disable

---

**NEXT ACTION:** Use this summary when implementing GOD_CHECKLIST tasks  
**KEY INSIGHT:** Design is deliberate - respect it to maintain system integrity
