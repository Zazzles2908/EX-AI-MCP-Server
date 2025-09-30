# Refactoring Action Plan – EX-AI MCP Server
**Date**: 2025-09-29  
**Based on**: Architectural Review (architectural_review_2025-09-29.md)  
**Objective**: Reduce all scripts to ≤500 lines while maintaining full functionality

---

## Overview

This plan addresses **26 scripts exceeding the 500-line limit** through systematic refactoring. The approach prioritizes:
1. **AI Context Window Compatibility**: Enable AI-assisted development on all files
2. **Architectural Alignment**: Match documented design in `docs/System_layout/`
3. **Maintainability**: Improve separation of concerns and reduce coupling
4. **Zero Downtime**: Maintain full MCP/GLM/streaming functionality throughout

---

## Phase 1: Critical Infrastructure (Top 6 Files)

### Target: Reduce 8,773 lines → 3,000 lines (65% reduction)

#### 1.1 Workflow Mixin (1,937 → 500 lines)

**Current**: Single monolithic file with all workflow functionality  
**Target**: 4 focused modules

**File Split Plan**:
```
tools/workflow/
  ├── orchestration.py          (~500 lines)
  │   ├── BaseWorkflowMixin (abstract base)
  │   ├── Step execution engine
  │   ├── Pause/resume logic
  │   └── Progress tracking
  │
  ├── file_embedding.py         (~500 lines)
  │   ├── Context-aware file selection
  │   ├── Token budget allocation
  │   ├── Deduplication (newest-first)
  │   └── File content preparation
  │
  ├── expert_analysis.py        (~500 lines)
  │   ├── External model integration
  │   ├── Analysis request formatting
  │   ├── Response consolidation
  │   └── Findings aggregation
  │
  └── conversation_integration.py (~437 lines)
      ├── Thread reconstruction
      ├── Turn management
      ├── Continuation offers
      └── Cross-tool context transfer
```

**Migration Strategy**:
1. Create new modules with extracted functionality
2. Update `workflow_mixin.py` to import and delegate
3. Update all workflow tools to import from new modules
4. Deprecate old monolithic file
5. **Server restart required after step 3**

**Acceptance Criteria**:
- All workflow tools (analyze, debug, codereview, etc.) function identically
- Test suite passes (pytest tests/phase*)
- No circular import errors

---

#### 1.2 Base Tool (1,673 → 500 lines)

**Current**: Single base class with all tool infrastructure  
**Target**: 4 specialized modules

**File Split Plan**:
```
tools/shared/
  ├── tool_interface.py         (~500 lines)
  │   ├── BaseTool (abstract interface)
  │   ├── Request validation
  │   ├── Error handling
  │   ├── Response formatting
  │   └── get_input_schema()
  │
  ├── model_integration.py      (~500 lines)
  │   ├── get_model_provider()
  │   ├── _resolve_model_context()
  │   ├── Provider selection logic
  │   ├── Temperature/token handling
  │   └── OpenRouter registry cache
  │
  ├── file_processing.py        (~400 lines)
  │   ├── read_file_content()
  │   ├── read_files() with deduplication
  │   ├── _prepare_file_content_for_prompt()
  │   ├── Token limit checking
  │   └── File size validation
  │
  └── conversation_support.py   (~273 lines)
      ├── reconstruct_thread_context()
      ├── get_conversation_file_list()
      ├── Continuation ID handling
      └── Thread creation/retrieval
```

**Migration Strategy**:
1. Extract interfaces to `tool_interface.py` (abstract methods only)
2. Move model logic to `model_integration.py`
3. Move file logic to `file_processing.py`
4. Move conversation logic to `conversation_support.py`
5. Update `base_tool.py` to compose from new modules (mixin pattern)
6. Update all tool classes to import from correct modules
7. **Server restart required after step 6**

**Acceptance Criteria**:
- All tools (chat, thinkdeep, analyze, etc.) function identically
- MCP list_tools returns same schema
- File processing maintains deduplication behavior

---

#### 1.3 Request Handler (1,344 → 500 lines)

**Current**: Single handler with routing, model resolution, conversation, and dispatch  
**Target**: 3 focused handlers

**File Split Plan**:
```
src/server/handlers/
  ├── tool_dispatcher.py        (~500 lines)
  │   ├── handle_call_tool() (main entry)
  │   ├── Tool lookup and validation
  │   ├── Error normalization
  │   ├── Progress capture
  │   └── Response formatting
  │
  ├── model_resolver.py         (~500 lines)
  │   ├── _resolve_model_context()
  │   ├── parse_model_option()
  │   ├── RoutePlan construction
  │   ├── Provider capability matching
  │   └── Fallback logic
  │
  └── conversation_manager.py   (~344 lines)
      ├── reconstruct_thread_context()
      ├── Continuation ID processing
      ├── Thread creation/retrieval
      ├── File deduplication
      └── get_follow_up_instructions()
```

**Migration Strategy**:
1. Extract model resolution to `model_resolver.py`
2. Extract conversation logic to `conversation_manager.py`
3. Refactor `request_handler.py` → `tool_dispatcher.py` (imports from above)
4. Update imports in `mcp_handlers.py` and `ws_server.py`
5. **Server restart required after step 4**

**Acceptance Criteria**:
- MCP tool calls work identically
- WebSocket daemon tool calls work identically
- Routing decisions unchanged (verify with logs)
- Continuation IDs work across tool boundaries

---

#### 1.4 Simple Base (1,183 → 500 lines)

**File Split Plan**:
```
tools/simple/
  ├── simple_tool_base.py       (~500 lines)
  │   ├── SimpleBaseTool (core interface)
  │   ├── Single-turn execution
  │   └── Basic validation
  │
  └── simple_tool_helpers.py    (~683 lines)
      ├── Utility functions
      ├── Common formatters
      └── Shared validators
```

**Migration Strategy**:
1. Extract helpers to separate module
2. Update simple tool imports
3. **Server restart required**

---

#### 1.5 Conversation Memory (1,109 → 500 lines)

**File Split Plan**:
```
utils/
  ├── conversation_storage.py   (~500 lines)
  │   ├── Thread storage (in-memory)
  │   ├── Turn persistence
  │   └── File reference tracking
  │
  └── conversation_api.py       (~609 lines)
      ├── create_thread()
      ├── add_turn()
      ├── get_thread()
      ├── reconstruct_thread_context()
      └── get_conversation_file_list()
```

**Migration Strategy**:
1. Split storage from API
2. Update all imports (request_handler, base_tool, workflow_mixin)
3. **Server restart required**

---

#### 1.6 Provider Registry (1,037 → 500 lines)

**File Split Plan**:
```
src/providers/
  ├── provider_registry.py      (~500 lines)
  │   ├── ModelProviderRegistry (core)
  │   ├── register_provider()
  │   ├── get_provider()
  │   ├── get_provider_for_model()
  │   └── Model resolution
  │
  └── provider_health.py        (~537 lines)
      ├── HealthWrappedProvider
      ├── CircuitBreaker integration
      ├── Health checks
      └── Retry logic
```

**Migration Strategy**:
1. Extract health wrapper to separate module
2. Update provider_config.py imports
3. **Server restart required**

---

## Phase 2: Workflow Tools (8 files, 700-914 lines each)

### Target: Reduce 6,527 lines → 4,000 lines (39% reduction)

**Affected Files**:
- `tools/workflows/consensus.py` (914 lines)
- `tools/workflows/secaudit.py` (824 lines)
- `tools/workflows/thinkdeep.py` (818 lines)
- `tools/workflows/tracer.py` (810 lines)
- `tools/workflows/analyze.py` (795 lines)
- `tools/workflows/precommit.py` (743 lines)
- `tools/workflows/codereview.py` (736 lines)
- `tools/workflows/refactor.py` (736 lines)

**Common Pattern** (each tool):
```
tools/workflows/<tool_name>/
  ├── <tool_name>_tool.py       (~500 lines: main tool class)
  └── <tool_name>_prompts.py    (~200-400 lines: system prompts, templates)
```

**Migration Strategy** (per tool):
1. Extract system prompts to separate file
2. Extract large helper methods to module-level functions
3. Leverage refactored workflow_mixin (from Phase 1)
4. **Server restart required after each tool**

**Priority Order**:
1. `consensus.py` (914 lines, most complex)
2. `thinkdeep.py` (818 lines, high usage)
3. `analyze.py` (795 lines, entry point for many workflows)
4. Others in descending size order

---

## Phase 3: Provider & Utility Files (6 files)

### Target: Reduce 4,841 lines → 3,000 lines (38% reduction)

**Files**:
- `src/providers/openai_compatible.py` (991 lines)
- `src/daemon/ws_server.py` (887 lines)
- `utils/file_utils.py` (864 lines)
- `src/providers/base.py` (557 lines)
- `src/providers/kimi.py` (550 lines)

**Approach**:
- Extract common patterns to shared modules
- Split large providers into base + extensions
- Modularize WS daemon handlers

---

## Phase 4: Remaining Violations (6 files)

### Target: Reduce 3,859 lines → 3,000 lines (22% reduction)

**Files**:
- `scripts/diagnostics/ws_probe.py` (758 lines)
- `tools/workflows/debug.py` (693 lines)
- `tools/workflows/docgen.py` (655 lines)
- `tools/workflows/testgen.py` (613 lines)
- `server.py` (602 lines)
- `tools/providers/kimi/kimi_tools_chat.py` (594 lines)

**Approach**:
- Extract diagnostic utilities to shared modules
- Apply workflow tool pattern from Phase 2
- Consider splitting server.py into server + initialization

---

## Implementation Constraints

### Must Maintain Throughout
1. ✅ Full MCP protocol compliance
2. ✅ WebSocket daemon functionality
3. ✅ GLM and Kimi provider integration
4. ✅ Streaming (GLM SSE, Kimi when enabled)
5. ✅ Intelligent routing (GLM-4.5-flash manager)
6. ✅ Conversation threading and continuation
7. ✅ File upload and processing
8. ✅ All existing tool functionality

### Server Restart Protocol
**After each phase**:
```powershell
# Stop existing daemon
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\ws_stop.ps1

# Restart with new code
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\ws_start.ps1 -Restart
```

**Validation after restart**:
1. Check logs: `logs/ws_daemon.health.json`
2. Verify MCP tools: Use EXAI-WS MCP to call `listmodels`
3. Test routing: Call `chat` with GLM and Kimi models
4. Test workflow: Call `analyze` with continuation

---

## Testing Strategy

### Per-Phase Validation
1. **Unit Tests**: Run existing test suite
   ```powershell
   python -m pytest tests/phase* -v
   ```

2. **Integration Smoke Tests**:
   ```powershell
   python scripts/validate_exai_ws_kimi_tools.py --fast
   ```

3. **Manual Verification**:
   - MCP list_tools (count should match pre-refactor)
   - Chat with GLM (verify streaming)
   - Chat with Kimi (verify file upload)
   - Analyze → Codereview continuation (verify threading)

### Regression Prevention
- Capture baseline outputs before Phase 1
- Compare outputs after each phase
- Log all routing decisions for comparison

---

## Risk Mitigation

### High-Risk Changes
1. **Workflow Mixin Split**: Affects all workflow tools
   - Mitigation: Implement backward-compatible wrapper initially
   - Rollback: Keep old file until all tools migrated

2. **Request Handler Split**: Core MCP boundary
   - Mitigation: Extensive logging during migration
   - Rollback: Git branch per phase

3. **Provider Registry Split**: Affects all provider calls
   - Mitigation: Feature flag for health wrapper
   - Rollback: Keep monolithic version as fallback

### Low-Risk Changes
- Individual workflow tool splits (isolated)
- Utility module extractions (pure functions)
- Documentation updates

---

## Success Metrics

### Quantitative
- ✅ 0 files >500 lines (currently 26)
- ✅ Average file size <350 lines
- ✅ All tests passing
- ✅ No performance regression (measure with telemetry)

### Qualitative
- ✅ Improved AI-assisted development experience
- ✅ Easier onboarding for new contributors
- ✅ Clearer separation of concerns
- ✅ Better alignment with documented architecture

---

## Timeline Estimate

**Phase 1** (Critical Infrastructure): 3-4 sessions  
**Phase 2** (Workflow Tools): 2-3 sessions  
**Phase 3** (Providers & Utils): 2 sessions  
**Phase 4** (Remaining): 1-2 sessions  

**Total**: 8-11 sessions (assuming 2-3 hours per session)

---

## Next Immediate Steps

1. **Review this plan** with user for approval
2. **Create git branch**: `refactor/500-line-limit`
3. **Start Phase 1.1**: Workflow Mixin split
4. **Document baseline**: Capture current test outputs
5. **Implement first split**: Create `tools/workflow/orchestration.py`

---

**End of Action Plan**

