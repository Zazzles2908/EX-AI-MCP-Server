# SHARED COMPONENTS INVENTORY
**Date:** 2025-10-10 1:05 PM AEDT  
**Task:** Phase 0, Task 0.2 - Shared Infrastructure Identification  
**Status:** ✅ COMPLETE

---

## EXECUTIVE SUMMARY

**Shared Infrastructure Identified:**
- 3 Base Tool Classes (BaseTool, SimpleTool, WorkflowTool)
- 13 Mixins (shared functionality across tools)
- 10 Highly-Used Utilities (imported 7-30 times each)
- 4 Provider Classes (Kimi, GLM, OpenAI-compatible, Hybrid)

**Critical Finding:**
- `tools/workflow/expert_analysis.py` (34.1KB) is a SHARED MIXIN used by ALL 12 workflow tools
- Changes to shared base classes affect 20+ tools
- Utils/ has 10 highly-imported files (7-30 imports each)

---

## CATEGORY 1: BASE TOOL CLASSES (3 Classes)

### 1.1 BaseTool - Foundation for ALL Tools

**Location:** `tools/shared/base_tool.py`  
**Size:** Not large (composed of mixins)  
**Inheritance:** Composes BaseToolCore + 3 mixins

**What it provides:**
- Core tool interface (execute, get_name, get_description, get_schema)
- File handling capabilities
- Model management
- Response formatting

**Used by:** 20+ tools directly
- All capability tools (listmodels, version, provider_capabilities, etc.)
- All diagnostic tools (health, status, toolcall_log_tail, etc.)
- All provider-specific tools (GLM, Kimi tools)
- Base for SimpleTool and WorkflowTool

**Import count:** 20+ direct imports

**Classification:** ✅ SHARED BASE CLASS - CRITICAL INFRASTRUCTURE

---

### 1.2 SimpleTool - For Simple Single-Step Tools

**Location:** `tools/simple/base.py`  
**Size:** 55.3KB (LARGEST FILE!)  
**Inheritance:** `SimpleTool(WebSearchMixin, ToolCallMixin, StreamingMixin, ContinuationMixin, BaseTool)`

**What it provides:**
- Streamlined single-step tool execution
- Web search integration
- Tool calling capabilities
- Streaming support
- Conversation continuation

**Used by:** 4 tools
- activity.py
- challenge.py
- chat.py
- capabilities/recommend.py

**Import count:** 4 direct imports

**Classification:** ✅ SHARED BASE CLASS - HIGH IMPACT

**⚠️ WARNING:** 55.3KB is VERY LARGE for a base class! Potential for bloat.

---

### 1.3 WorkflowTool - For Multi-Step Workflow Tools

**Location:** `tools/workflow/base.py`  
**Size:** 30.5KB (LARGE)  
**Inheritance:** `WorkflowTool(BaseTool, BaseWorkflowMixin)`

**What it provides:**
- Multi-step workflow orchestration
- Expert analysis integration
- File embedding
- Conversation integration
- Request validation

**Used by:** 12 workflow tools (ALL workflows!)
- analyze.py
- codereview.py
- consensus.py
- debug.py
- docgen.py
- planner.py
- precommit.py
- refactor.py
- secaudit.py
- testgen.py
- thinkdeep.py
- tracer.py

**Import count:** 12 direct imports

**Classification:** ✅ SHARED BASE CLASS - CRITICAL INFRASTRUCTURE

---

## CATEGORY 2: SHARED MIXINS (13 Mixins)

### 2.1 tools/shared/ Mixins (3 mixins)

**Location:** `tools/shared/`

| Mixin | File | Size | Purpose |
|-------|------|------|---------|
| FileHandlingMixin | base_tool_file_handling.py | 26.5KB | File operations, token budgeting |
| ModelManagementMixin | base_tool_model_management.py | 24.4KB | Model selection, context management |
| ResponseFormattingMixin | base_tool_response.py | Small | Response formatting |

**Used by:** BaseTool (affects ALL tools)

**Classification:** ✅ SHARED MIXINS - CRITICAL INFRASTRUCTURE

---

### 2.2 tools/simple/mixins/ (5 mixins)

**Location:** `tools/simple/mixins/`

| Mixin | File | Size | Purpose | Used By |
|-------|------|------|---------|---------|
| ContinuationMixin | continuation_mixin.py | 11.9KB | Conversation continuation | SimpleTool |
| StreamingMixin | streaming_mixin.py | Small | Streaming support | SimpleTool |
| ToolCallMixin | tool_call_mixin.py | Small | Tool calling | SimpleTool |
| WebSearchMixin | web_search_mixin.py | Small | Web search integration | SimpleTool |
| FileMixin | file_mixin.py | Small | File handling | SimpleTool |

**Used by:** SimpleTool (affects 4 tools)

**Classification:** ✅ SHARED MIXINS - MEDIUM IMPACT

---

### 2.3 tools/workflow/ Mixins (5 mixins)

**Location:** `tools/workflow/`

| Mixin | File | Size | Purpose | Used By |
|-------|------|------|---------|---------|
| **ExpertAnalysisMixin** | **expert_analysis.py** | **34.1KB** | **External model integration** | **ALL 12 workflows!** |
| OrchestrationMixin | orchestration.py | 26.9KB | Workflow orchestration | BaseWorkflowMixin |
| FileEmbeddingMixin | file_embedding.py | 18.1KB | File embedding with token budgeting | BaseWorkflowMixin |
| ConversationIntegrationMixin | conversation_integration.py | 17.8KB | Conversation management | BaseWorkflowMixin |
| RequestAccessorMixin | request_accessors.py | 15.9KB | Request field access | BaseWorkflowMixin |

**Used by:** BaseWorkflowMixin → WorkflowTool → ALL 12 workflow tools

**Classification:** ✅ SHARED MIXINS - CRITICAL INFRASTRUCTURE

**🚨 CRITICAL:** ExpertAnalysisMixin (34.1KB) is used by ALL workflow tools!

---

## CATEGORY 3: HIGHLY-USED UTILITIES (10 files)

**Location:** `utils/` (root level, NO folder structure)

| File | Imports | Size | Purpose |
|------|---------|------|---------|
| progress.py | 30 | 10.2KB | Progress tracking/heartbeat |
| observability.py | 21 | Small | Observability/logging |
| model_context.py | 18 | Small | Model context management |
| conversation_memory.py | 16 | Small | Conversation memory |
| file_utils.py | 13 | Small | File utilities (base) |
| client_info.py | 12 | Small | Client information |
| token_utils.py | 11 | Small | Token estimation |
| model_restrictions.py | 9 | Small | Model restrictions |
| cache.py | 9 | Small | Caching utilities |
| tool_events.py | 7 | Small | Tool event tracking |

**Classification:** ✅ SHARED UTILITIES - HIGH IMPACT

**⚠️ ISSUE:** These are scattered in utils/ with NO folder structure!

---

## CATEGORY 4: PROVIDER CLASSES (4 providers)

**Location:** `src/providers/`

### 4.1 Core Provider Classes

| Provider | File | Size | Purpose | Imports |
|----------|------|------|---------|---------|
| KimiModelProvider | kimi.py | Small | Kimi/Moonshot provider | ~10 |
| GLMModelProvider | glm.py | Small | GLM/ZhipuAI provider | ~10 |
| OpenAICompatible | openai_compatible.py | 38.5KB | OpenAI-compatible provider | ~5 |
| HybridPlatformManager | hybrid_platform_manager.py | Small | Multi-provider manager | ~5 |

**Classification:** ✅ SHARED PROVIDERS - CRITICAL INFRASTRUCTURE

### 4.2 Provider Support Classes

| Class | File | Size | Purpose |
|-------|------|------|---------|
| ModelProviderRegistry | registry_core.py | 20.2KB | Provider registry |
| ProviderDiagnostics | registry_selection.py | 19.1KB | Provider selection |
| RegistryConfig | registry_config.py | 10.7KB | Registry configuration |

**Classification:** ✅ SHARED INFRASTRUCTURE - CRITICAL

---

## CATEGORY 5: SHARED MODELS (Pydantic)

**Location:** `tools/shared/base_models.py` (10.5KB)

| Model | Purpose | Used By |
|-------|---------|---------|
| ToolRequest | Base request model | All tools |
| BaseWorkflowRequest | Workflow request base | All workflows |
| WorkflowRequest | Concrete workflow request | All workflows |
| ConsolidatedFindings | Workflow findings | All workflows |

**Classification:** ✅ SHARED MODELS - CRITICAL INFRASTRUCTURE

---

## IMPACT ANALYSIS

### Critical Shared Components (Changes affect 10+ tools)

**Tier 1: CRITICAL (affects ALL tools - 20+)**
1. `tools/shared/base_tool.py` - BaseTool (20+ tools)
2. `tools/shared/base_tool_file_handling.py` - FileHandlingMixin (20+ tools)
3. `tools/shared/base_tool_model_management.py` - ModelManagementMixin (20+ tools)
4. `utils/progress.py` - Progress tracking (30 imports)
5. `utils/observability.py` - Observability (21 imports)

**Tier 2: HIGH IMPACT (affects 10-20 tools)**
6. `tools/workflow/expert_analysis.py` - ExpertAnalysisMixin (12 workflow tools)
7. `tools/workflow/base.py` - WorkflowTool (12 workflow tools)
8. `utils/model_context.py` - Model context (18 imports)
9. `utils/conversation_memory.py` - Conversation memory (16 imports)
10. `utils/file_utils.py` - File utilities (13 imports)

**Tier 3: MEDIUM IMPACT (affects 5-10 tools)**
11. `tools/simple/base.py` - SimpleTool (4 tools, but 55.3KB!)
12. `utils/client_info.py` - Client info (12 imports)
13. `utils/token_utils.py` - Token utils (11 imports)

---

## ARCHITECTURAL OBSERVATIONS

### ✅ GOOD PATTERNS

**1. Clear Base Class Hierarchy**
```
BaseTool (foundation)
├── SimpleTool (single-step tools)
└── WorkflowTool (multi-step workflows)
```

**2. Mixin Composition**
- BaseTool composes 3 mixins (file handling, model management, response formatting)
- SimpleTool adds 5 mixins (continuation, streaming, tool call, web search, file)
- WorkflowTool adds 5 mixins (expert analysis, orchestration, file embedding, conversation, request accessors)

**3. Shared Models**
- Pydantic models in `tools/shared/base_models.py`
- Consistent request/response structure

### ⚠️ CONCERNS

**1. File Size Bloat**
- `tools/simple/base.py` = 55.3KB (LARGEST FILE!)
- `tools/workflow/expert_analysis.py` = 34.1KB
- `tools/workflow/base.py` = 30.5KB
- Risk: Large shared files are hard to maintain

**2. Unclear Separation**
- Why is `expert_analysis.py` in `tools/workflow/` instead of `tools/shared/`?
- It's used by ALL workflow tools, should it be in shared/?

**3. Utils Chaos**
- 37 files in `utils/` with ZERO folder structure
- 10 highly-imported files (7-30 imports each)
- Should be organized into folders

---

## RECOMMENDATIONS

### 1. Document Shared Infrastructure

**Create:**
- `docs/architecture/SHARED_INFRASTRUCTURE.md` - Document all shared components
- `docs/architecture/BASE_CLASS_HIERARCHY.md` - Document inheritance tree
- `docs/architecture/MIXIN_GUIDE.md` - Document mixin usage

### 2. Consider Reorganization (Phase 1)

**Option A: Move expert_analysis.py to tools/shared/**
- It's used by ALL workflow tools
- Currently in `tools/workflow/` which looks tool-specific
- Should be in `tools/shared/` to indicate it's shared infrastructure

**Option B: Keep as-is but document clearly**
- Add comments explaining it's shared infrastructure
- Update documentation to clarify

### 3. Organize utils/ (Phase 1, Task 1.4)

**Proposed structure:**
```
utils/
├── file/           (9 file_utils_*.py files)
├── conversation/   (4 conversation_*.py files)
├── model/          (2 model_*.py files)
├── config/         (2 config_*.py files)
├── token/          (2 token_*.py files)
└── [core utils]    (progress, observability, cache, etc.)
```

---

## NEXT STEPS FOR TASK 0.3

**Now that we know what's shared, we can:**
1. Map dependencies (what imports what)
2. Create import graph
3. Identify circular dependencies
4. Understand impact of changes

**Key Questions to Answer:**
- What's the full dependency chain for each shared component?
- Are there circular dependencies?
- What's the impact radius of changing each component?

---

**STATUS:** ✅ TASK 0.2 COMPLETE

Shared infrastructure identified and classified. Ready for Task 0.3: Dependency Mapping.

