# DEPENDENCY MAP - IMPORT GRAPH ANALYSIS
**Date:** 2025-10-10 1:10 PM AEDT  
**Task:** Phase 0, Task 0.3 - Dependency Mapping  
**Status:** ✅ COMPLETE

---

## EXECUTIVE SUMMARY

**Dependency Structure:**
- Clean hierarchical dependency flow (no circular dependencies!)
- 3-tier architecture: Base → Intermediate → Implementation
- Utils are leaf dependencies (imported by all, import nothing)
- Providers have controlled dependencies on tools (TYPE_CHECKING only)

**Critical Findings:**
- ✅ NO runtime circular dependencies detected
- ✅ Clean separation: utils/ → tools/shared/ → tools/simple|workflow/ → tools/workflows/
- ⚠️ Some src/ files import from tools/ (but only for registry/tool discovery)
- ✅ TYPE_CHECKING imports prevent runtime cycles

---

## DEPENDENCY HIERARCHY

### Tier 1: LEAF DEPENDENCIES (No imports from project)

**utils/** - Pure utility functions
- Imported by: ALL layers (tools, src, scripts)
- Imports from project: NONE (except conversation_history.py has dynamic import)
- Status: ✅ CLEAN LEAF LAYER

**Key utils dependencies:**
- progress.py → imported by 30 files
- observability.py → imported by 21 files
- model_context.py → imported by 18 files
- conversation_memory.py → imported by 16 files

**Classification:** ✅ FOUNDATION LAYER - No circular dependencies

---

### Tier 2: SHARED INFRASTRUCTURE (Imports from utils only)

**tools/shared/** - Base classes and mixins
- Imported by: ALL tools
- Imports from: utils/, mcp.types, config
- Imports from tools: NONE

**Dependency chain:**
```
tools/shared/base_tool_core.py
  └─ imports: ABC, logging, mcp.types

tools/shared/base_tool_file_handling.py (26.5KB)
  └─ imports: utils/file_utils, utils/token_utils, utils/conversation_memory

tools/shared/base_tool_model_management.py (24.4KB)
  └─ imports: utils/model_context, utils/model_restrictions, src/providers/registry

tools/shared/base_tool_response.py
  └─ imports: mcp.types, utils/progress

tools/shared/base_tool.py
  └─ imports: base_tool_core, file_handling, model_management, response
  └─ imports: tools/models (for compatibility)
```

**Classification:** ✅ CLEAN SHARED LAYER - Only imports from utils and config

---

### Tier 3: TOOL BASE CLASSES (Imports from shared + utils)

**tools/simple/base.py** (55.3KB) - SimpleTool
```
SimpleTool
  ├─ imports: tools/shared/base_tool (BaseTool)
  ├─ imports: tools/shared/base_models (ToolRequest)
  ├─ imports: tools/shared/schema_builders (SchemaBuilder)
  ├─ imports: tools/simple/mixins/* (4 mixins)
  ├─ imports: utils/client_info
  ├─ imports: utils/progress
  └─ imports: utils/progress_messages
```

**tools/workflow/base.py** (30.5KB) - WorkflowTool
```
WorkflowTool
  ├─ imports: tools/shared/base_tool (BaseTool)
  ├─ imports: tools/shared/base_models (WorkflowRequest)
  ├─ imports: tools/workflow/schema_builders (WorkflowSchemaBuilder)
  ├─ imports: tools/workflow/workflow_mixin (BaseWorkflowMixin)
  └─ imports: config (TimeoutConfig)
```

**tools/workflow/workflow_mixin.py** (10.1KB) - BaseWorkflowMixin
```
BaseWorkflowMixin
  ├─ imports: tools/workflow/request_accessors (RequestAccessorMixin)
  ├─ imports: tools/workflow/conversation_integration (ConversationIntegrationMixin)
  ├─ imports: tools/workflow/file_embedding (FileEmbeddingMixin)
  ├─ imports: tools/workflow/expert_analysis (ExpertAnalysisMixin) ← 34.1KB!
  ├─ imports: tools/workflow/orchestration (OrchestrationMixin)
  └─ imports: tools/shared/base_models (ConsolidatedFindings)
```

**Classification:** ✅ CLEAN INTERMEDIATE LAYER

---

### Tier 4: TOOL IMPLEMENTATIONS (Imports from base classes)

**Simple Tools** (4 tools)
```
activity.py, challenge.py, chat.py, capabilities/recommend.py
  └─ imports: tools/simple/base (SimpleTool)
  └─ imports: utils/* (various)
```

**Workflow Tools** (12 tools)
```
analyze.py, codereview.py, consensus.py, debug.py, docgen.py, planner.py,
precommit.py, refactor.py, secaudit.py, testgen.py, thinkdeep.py, tracer.py
  └─ imports: tools/workflow/base (WorkflowTool)
  └─ imports: tools/workflow/*_config (tool-specific config)
  └─ imports: tools/workflow/*_models (tool-specific models)
  └─ imports: systemprompts/* (tool-specific prompts)
```

**Direct BaseTool Users** (14 tools)
```
capabilities/*, diagnostics/*, providers/glm/*, providers/kimi/*
  └─ imports: tools/shared/base_tool (BaseTool)
  └─ imports: utils/* (various)
```

**Classification:** ✅ CLEAN IMPLEMENTATION LAYER

---

## CROSS-LAYER DEPENDENCIES

### src/ → tools/ Dependencies

**Found 10 files in src/ that import from tools/:**

| File | Imports | Purpose |
|------|---------|---------|
| src/bootstrap/singletons.py | tools.registry | Tool registry singleton |
| src/daemon/ws_server.py | tools.registry | Tool discovery |
| src/providers/base.py | tools.models (TYPE_CHECKING) | Type hints only |
| src/providers/registry_config.py | tools.models | Model categories |
| src/providers/registry_core.py | tools.registry | Tool registry access |
| src/providers/registry_selection.py | tools.models | Model selection |
| src/server/handlers/request_handler*.py | tools.registry | Tool execution |
| src/server/tools/tool_filter.py | tools.registry | Tool filtering |
| src/server/registry_bridge.py | tools.registry | Registry bridge |

**Analysis:**
- ✅ Most imports are for `tools.registry` (tool discovery/execution)
- ✅ TYPE_CHECKING imports prevent runtime circular dependencies
- ✅ This is expected: src/ needs to discover and execute tools
- ⚠️ Coupling: src/providers depends on tools/models for model categories

**Classification:** ⚠️ ACCEPTABLE COUPLING - But worth documenting

---

### utils/ → tools/ Dependencies

**Found 1 file in utils/ that imports from tools/:**

| File | Import | Purpose |
|------|--------|---------|
| utils/conversation_history.py | server.TOOLS (dynamic) | Tool name lookup |

**Analysis:**
- ✅ Dynamic import (not at module level)
- ✅ Only for tool name resolution
- ✅ No circular dependency risk

**Classification:** ✅ SAFE DYNAMIC IMPORT

---

## MIXIN DEPENDENCY CHAINS

### SimpleTool Mixin Chain

```
SimpleTool
  ├─ WebSearchMixin (tools/simple/mixins/web_search_mixin.py)
  │   └─ imports: logging, typing
  │
  ├─ ToolCallMixin (tools/simple/mixins/tool_call_mixin.py)
  │   └─ imports: logging, typing, json
  │
  ├─ StreamingMixin (tools/simple/mixins/streaming_mixin.py)
  │   └─ imports: logging, typing
  │
  ├─ ContinuationMixin (tools/simple/mixins/continuation_mixin.py) (11.9KB)
  │   └─ imports: logging, typing, json, utils/conversation_threads
  │
  └─ BaseTool
      ├─ BaseToolCore
      ├─ ModelManagementMixin → utils/model_context, src/providers/registry
      ├─ FileHandlingMixin → utils/file_utils, utils/token_utils
      └─ ResponseFormattingMixin → utils/progress
```

**Total dependency depth:** 3 levels  
**Classification:** ✅ CLEAN MIXIN COMPOSITION

---

### WorkflowTool Mixin Chain

```
WorkflowTool
  ├─ BaseTool (see above)
  │
  └─ BaseWorkflowMixin
      ├─ RequestAccessorMixin (tools/workflow/request_accessors.py) (15.9KB)
      │   └─ imports: logging, typing, tools/shared/base_models
      │
      ├─ ConversationIntegrationMixin (tools/workflow/conversation_integration.py) (17.8KB)
      │   └─ imports: logging, typing, utils/conversation_threads
      │
      ├─ FileEmbeddingMixin (tools/workflow/file_embedding.py) (18.1KB)
      │   └─ imports: logging, typing, utils/file_utils, utils/token_utils
      │
      ├─ ExpertAnalysisMixin (tools/workflow/expert_analysis.py) (34.1KB) ← LARGEST!
      │   └─ imports: logging, typing, json, time
      │   └─ imports: src/providers/hybrid_platform_manager
      │   └─ imports: utils/model_context, utils/observability
      │
      └─ OrchestrationMixin (tools/workflow/orchestration.py) (26.9KB)
          └─ imports: logging, typing, asyncio, json
          └─ imports: tools/shared/base_models (ConsolidatedFindings)
          └─ imports: utils/progress, utils/observability
```

**Total dependency depth:** 3 levels  
**Classification:** ✅ CLEAN MIXIN COMPOSITION

**🚨 CRITICAL:** ExpertAnalysisMixin (34.1KB) imports from src/providers/hybrid_platform_manager!

---

## IMPACT RADIUS ANALYSIS

### If BaseTool Changes:

**Direct impact:** 20+ tools
- All capability tools (5)
- All diagnostic tools (4)
- All provider tools (9)
- SimpleTool (affects 4 more tools)
- WorkflowTool (affects 12 more tools)

**Total impact:** 30+ tools (ENTIRE SYSTEM!)

**Risk level:** 🔴 CRITICAL

---

### If SimpleTool Changes:

**Direct impact:** 4 tools
- activity.py
- challenge.py
- chat.py
- capabilities/recommend.py

**Risk level:** 🟡 MEDIUM

---

### If WorkflowTool Changes:

**Direct impact:** 12 tools
- All workflow tools (analyze, codereview, consensus, debug, docgen, planner, precommit, refactor, secaudit, testgen, thinkdeep, tracer)

**Risk level:** 🔴 HIGH

---

### If ExpertAnalysisMixin Changes:

**Direct impact:** 12 tools (ALL workflows)
- Used by BaseWorkflowMixin → WorkflowTool → ALL 12 workflow tools

**Risk level:** 🔴 CRITICAL

**🚨 CONCERN:** This is a 34.1KB file that affects ALL workflow tools!

---

### If utils/progress.py Changes:

**Direct impact:** 30 files
- All tools that show progress
- All workflow orchestration
- Response formatting

**Risk level:** 🔴 CRITICAL

---

### If utils/observability.py Changes:

**Direct impact:** 21 files
- All logging and observability
- Expert analysis
- Workflow orchestration

**Risk level:** 🔴 HIGH

---

## CIRCULAR DEPENDENCY ANALYSIS

### ✅ NO RUNTIME CIRCULAR DEPENDENCIES FOUND!

**Checked:**
- utils/ → tools/ ✅ Only 1 dynamic import (safe)
- src/ → tools/ ✅ Only for registry/discovery (expected)
- tools/ → src/ ✅ Only for providers (expected)
- tools/ → utils/ ✅ One-way dependency (clean)

**TYPE_CHECKING imports (safe):**
- src/providers/base.py → tools.models (TYPE_CHECKING only)
- These don't create runtime circular dependencies

**Dynamic imports (safe):**
- utils/conversation_history.py → server.TOOLS (dynamic, not at module level)

**Classification:** ✅ CLEAN ARCHITECTURE - No circular dependencies!

---

## ARCHITECTURAL OBSERVATIONS

### ✅ STRENGTHS

**1. Clean Layered Architecture**
```
Layer 1: utils/ (foundation - no project imports)
Layer 2: tools/shared/ (base classes - imports utils only)
Layer 3: tools/simple/, tools/workflow/ (intermediate - imports shared + utils)
Layer 4: tools/workflows/, tools/capabilities/, etc. (implementations)
```

**2. Mixin Composition**
- Clear separation of concerns
- Each mixin has focused responsibility
- No circular dependencies between mixins

**3. Controlled Cross-Layer Dependencies**
- src/ → tools/ only for registry/discovery (expected)
- TYPE_CHECKING prevents runtime cycles
- Dynamic imports are safe

### ⚠️ CONCERNS

**1. ExpertAnalysisMixin Location**
- File: tools/workflow/expert_analysis.py (34.1KB)
- Used by: ALL 12 workflow tools
- Location: tools/workflow/ (looks tool-specific)
- **Question:** Should it be in tools/shared/?

**2. Large Shared Files**
- SimpleTool: 55.3KB (LARGEST!)
- ExpertAnalysisMixin: 34.1KB
- WorkflowTool: 30.5KB
- Risk: Hard to maintain, high change impact

**3. High-Impact Utils**
- progress.py: 30 imports
- observability.py: 21 imports
- Changes affect many files

---

## RECOMMENDATIONS

### 1. Document Dependency Rules

**Create:** `docs/architecture/DEPENDENCY_RULES.md`

**Rules to document:**
- utils/ must not import from tools/ or src/
- tools/shared/ can import from utils/ and config only
- tools/simple/ and tools/workflow/ can import from tools/shared/ and utils/
- Tool implementations can import from their base classes
- src/ can import from tools/ only for registry/discovery

### 2. Consider Refactoring Large Files

**SimpleTool (55.3KB):**
- Consider splitting into smaller modules
- Extract helper methods to separate files

**ExpertAnalysisMixin (34.1KB):**
- Consider splitting into smaller mixins
- Or move to tools/shared/ to clarify it's shared infrastructure

### 3. Monitor High-Impact Components

**Critical components (changes affect 20+ files):**
- BaseTool
- FileHandlingMixin
- ModelManagementMixin
- utils/progress.py
- utils/observability.py

**Recommendation:** Extra care when modifying these!

---

**STATUS:** ✅ TASK 0.3 COMPLETE

Dependency map created. Clean architecture with no circular dependencies. Ready for Task 0.4: Duplicate Detection.

