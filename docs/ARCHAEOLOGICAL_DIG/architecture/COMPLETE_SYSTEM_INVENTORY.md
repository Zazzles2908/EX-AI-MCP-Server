# COMPLETE SYSTEM INVENTORY - LAYOUT MAP
**Date:** 2025-10-10 12:58 PM AEDT  
**Task:** Phase 0, Task 0.1 - Layout Map  
**Status:** ✅ COMPLETE

---

## EXECUTIVE SUMMARY

**Total Directories:** 22 top-level directories  
**Total Python Files:** 433 Python files (excluding .venv)  
**Largest Files:** 34 files > 10KB (tools/workflow/expert_analysis.py = 34.1KB)  
**Documentation:** 240 files in docs/  
**Tests:** 39 test files  
**Scripts:** 47 Python scripts

---

## TOP-LEVEL DIRECTORY INVENTORY

| Directory | Total Files | Python Files | Purpose |
|-----------|-------------|--------------|---------|
| .augment | 2 | 0 | Augment IDE configuration |
| .claude | 1 | 0 | Claude configuration |
| .github | 10 | 0 | GitHub workflows/actions |
| .logs | 6 | 0 | Legacy log files |
| Daemon | 4 | 0 | Daemon configuration (legacy?) |
| docs | 240 | 23 | Documentation (LARGE!) |
| logs | 74 | 0 | Active log files |
| monitoring | 9 | 8 | Monitoring infrastructure |
| nl | 0 | 0 | Empty directory |
| scripts | 64 | 47 | Utility scripts |
| security | 2 | 2 | Security/RBAC |
| src | 75 | 73 | Core source code |
| streaming | 1 | 1 | Streaming adapter |
| supabase | 1 | 0 | Supabase configuration |
| systemprompts | 15 | 15 | System prompts (ACTIVE) |
| test_files | 5 | 0 | Test data files |
| tests | 39 | 38 | Test suite |
| tool_validation_suite | 1103 | 68 | Tool validation (HUGE!) |
| tools | 91 | 91 | Tool implementations |
| utils | 37 | 37 | Utility functions |
| **TOTAL** | **1779** | **433** | |

---

## DETAILED STRUCTURE: src/ (Core Source Code)

**Total:** 75 files, 73 Python files

```
src/
├── __init__.py
├── bootstrap/              (4 py files) - System initialization
│   ├── env_loader.py
│   ├── logging_setup.py
│   └── singletons.py
│
├── conf/                   (0 py files) - JSON configuration files
│   └── custom_models.json
│
├── config/                 (0 py files) - Configuration module (DUPLICATE?)
│
├── conversation/           (4 py files) - Conversation management
│   ├── cache_store.py
│   ├── history_store.py
│   └── memory_policy.py
│
├── core/                   (2 py files) - Core infrastructure
│   ├── config.py
│   ├── message_bus_client.py (15.1KB)
│   └── validation/         (1 py files)
│
├── daemon/                 (2 py files) - WebSocket daemon
│   ├── session_manager.py
│   └── ws_server.py (54.4KB - LARGE!)
│
├── embeddings/             (1 py files) - Embedding providers
│   └── provider.py
│
├── providers/              (22 py files) - AI provider implementations
│   ├── base.py (20KB)
│   ├── capabilities.py
│   ├── glm.py
│   ├── glm_chat.py (16.7KB)
│   ├── glm_config.py
│   ├── glm_files.py
│   ├── hybrid_platform_manager.py
│   ├── kimi.py
│   ├── kimi_cache.py
│   ├── kimi_chat.py (10.9KB)
│   ├── kimi_config.py (10.3KB)
│   ├── kimi_files.py
│   ├── metadata.py
│   ├── openai_compatible.py (38.5KB - LARGE!)
│   ├── registry.py
│   ├── registry_config.py (10.7KB)
│   ├── registry_core.py (20.2KB)
│   ├── registry_selection.py (19.1KB)
│   ├── text_format_handler.py
│   ├── tool_executor.py
│   ├── zhipu_optional.py
│   ├── handlers/           (0 py files)
│   ├── mixins/             (2 py files)
│   ├── moonshot/           (1 py files)
│   └── orchestration/      (2 py files)
│
├── router/                 (4 py files) - Request routing
│   ├── classifier.py
│   ├── service.py (17.5KB)
│   ├── synthesis.py
│   └── unified_router.py
│
├── server/                 (4 py files) - MCP server
│   ├── fallback_orchestrator.py
│   ├── registry_bridge.py
│   ├── utils.py
│   ├── context/            (2 py files)
│   │   └── thread_context.py (15.8KB)
│   ├── conversation/       (0 py files) - DUPLICATE?
│   ├── handlers/           (10 py files)
│   │   ├── request_handler_execution.py (11.9KB)
│   │   ├── request_handler_model_resolution.py (10.3KB)
│   │   ├── request_handler_post_processing.py (14KB)
│   │   └── [7 more files]
│   ├── providers/          (6 py files) - DUPLICATE?
│   ├── tools/              (2 py files)
│   └── utils/              (1 py files) - DUPLICATE?
│
└── utils/                  (2 py files) - Utilities
    ├── async_logging.py
    └── timezone.py
```

### src/ Key Observations:

**✅ ACTIVE:**
- bootstrap/ - System initialization
- daemon/ - WebSocket server (ws_server.py = 54.4KB!)
- providers/ - 22 provider files (core AI provider logic)
- router/ - Request routing
- server/ - MCP server implementation

**⚠️ DUPLICATES DETECTED:**
- `src/conf/` vs `src/config/` - Both exist, unclear separation
- `src/conversation/` vs `src/server/conversation/` - Duplicate?
- `src/providers/` vs `src/server/providers/` - Duplicate?
- `src/utils/` (2 files) vs root `utils/` (37 files) - Why separate?

**🔍 NEEDS INVESTIGATION:**
- Why is `src/server/conversation/` empty?
- What's the separation between `src/providers/` and `src/server/providers/`?
- Why only 2 files in `src/utils/` when root `utils/` has 37?

---

## DETAILED STRUCTURE: tools/ (Tool Implementations)

**Total:** 91 files, 91 Python files

```
tools/
├── __init__.py
├── activity.py (10.8KB)
├── challenge.py (10.4KB)
├── chat.py (13.8KB)
├── models.py (17.4KB)
├── registry.py
├── selfcheck.py
├── version.py
│
├── audits/                 (1 py files)
│   └── schema_audit.py
│
├── capabilities/           (5 py files)
│   ├── listmodels.py (15.1KB)
│   ├── models.py (17.4KB)
│   ├── provider_capabilities.py
│   ├── recommend.py
│   └── version.py
│
├── cost/                   (2 py files)
│   ├── cost_optimizer.py
│   └── model_selector.py
│
├── diagnostics/            (8 py files)
│   ├── batch_markdown_reviews.py
│   ├── diagnose_ws_stack.py
│   ├── health.py
│   ├── ping_activity.py
│   ├── provider_diagnostics.py
│   ├── status.py
│   ├── toolcall_log_tail.py
│   └── ws_daemon_smoke.py
│
├── providers/              (0 py files) - Provider-specific tools
│   ├── glm/                (4 py files)
│   │   ├── glm_agents.py
│   │   ├── glm_files.py
│   │   ├── glm_payload_preview.py
│   │   └── glm_web_search.py
│   └── kimi/               (5 py files)
│       ├── kimi_capture_headers.py
│       ├── kimi_chat_with_tools.py
│       ├── kimi_intent_analysis.py
│       ├── kimi_multi_file_chat.py
│       ├── kimi_tools_chat.py (31.2KB - LARGE!)
│       └── kimi_upload.py (17.4KB)
│
├── reasoning/              (1 py files)
│   └── mode_selector.py
│
├── shared/                 (9 py files) - SHARED BASE CLASSES
│   ├── base_models.py (10.5KB)
│   ├── base_tool.py
│   ├── base_tool_core.py
│   ├── base_tool_file_handling.py (26.5KB - LARGE!)
│   ├── base_tool_model_management.py (24.4KB)
│   ├── base_tool_response.py
│   ├── error_envelope.py
│   └── schema_builders.py
│
├── simple/                 (4 py files) - SimpleTool architecture
│   ├── base.py (55.3KB - LARGEST FILE!)
│   ├── simple_tool_execution.py (10.4KB)
│   ├── simple_tool_helpers.py (10.5KB)
│   └── mixins/             (5 py files)
│       ├── continuation_mixin.py (11.9KB)
│       ├── file_mixin.py
│       ├── image_mixin.py
│       ├── model_mixin.py
│       └── websearch_mixin.py
│
├── streaming/              (0 py files) - Streaming support (DUPLICATE?)
│
├── workflow/               (9 py files) - WORKFLOW BASE CLASSES + MIXINS
│   ├── base.py (30.5KB - LARGE!)
│   ├── conversation_integration.py (17.8KB)
│   ├── expert_analysis.py (34.1KB - VERY LARGE! SHARED MIXIN!)
│   ├── file_embedding.py (18.1KB)
│   ├── orchestration.py (26.9KB)
│   ├── request_accessors.py (15.9KB)
│   ├── schema_builders.py
│   └── workflow_mixin.py (10.1KB)
│
└── workflows/              (30 py files) - WORKFLOW IMPLEMENTATIONS
    ├── analyze.py (27.7KB)
    ├── analyze_config.py
    ├── analyze_models.py
    ├── codereview.py (28.5KB)
    ├── codereview_config.py
    ├── codereview_models.py
    ├── consensus.py (29.1KB)
    ├── consensus_config.py
    ├── consensus_schema.py
    ├── consensus_validation.py
    ├── debug.py (34.5KB - LARGE!)
    ├── docgen.py (35.8KB - LARGE!)
    ├── planner.py (28.2KB)
    ├── precommit.py (27.6KB)
    ├── precommit_config.py
    ├── precommit_models.py
    ├── refactor.py (29.1KB)
    ├── refactor_config.py
    ├── refactor_models.py
    ├── secaudit.py (31.7KB)
    ├── secaudit_config.py
    ├── secaudit_models.py
    ├── testgen.py (30.6KB)
    ├── thinkdeep.py (27.1KB)
    ├── thinkdeep_config.py
    ├── thinkdeep_models.py
    ├── thinkdeep_ui.py
    ├── tracer.py (31.8KB)
    ├── tracer_config.py
    └── tracer_models.py
```

### tools/ Key Observations:

**✅ SHARED INFRASTRUCTURE (affects ALL tools):**
- `tools/shared/` - Base classes for all tools (9 files)
- `tools/simple/base.py` (55.3KB!) - SimpleTool base class
- `tools/workflow/base.py` (30.5KB) - WorkflowTool base class
- `tools/workflow/expert_analysis.py` (34.1KB!) - **CRITICAL: Used by ALL workflow tools**

**⚠️ CONFUSION:**
- `tools/workflow/` (singular) - Base classes + mixins (9 files)
- `tools/workflows/` (plural) - Implementations (30 files)
- Why singular vs plural? Unclear separation

**⚠️ DUPLICATES:**
- `tools/providers/` vs `src/providers/` - Different purposes?
- `tools/streaming/` (empty) vs root `streaming/` - Duplicate?

**📊 SIZE ANALYSIS:**
- Largest file: `tools/simple/base.py` (55.3KB)
- Second largest: `tools/workflows/docgen.py` (35.8KB)
- Third largest: `tools/workflow/expert_analysis.py` (34.1KB) - **SHARED MIXIN!**

---

## DETAILED STRUCTURE: utils/ (Utilities - ROOT LEVEL)

**Total:** 37 files, 37 Python files, **ZERO FOLDERS!**

### File Groups:

| Prefix | Count | Files |
|--------|-------|-------|
| file_utils_* | 9 | expansion, helpers, json, reading, security, tokens, + base |
| conversation_* | 4 | history, memory, models, threads |
| model_* | 2 | context, restrictions |
| config_* | 2 | bootstrap, helpers |
| token_* | 2 | estimator, utils |
| progress* | 2 | progress.py, progress_messages.py |
| [single files] | 16 | cache, client_info, costs, docs_validator, error_handling, file_cache, file_types, health, http_client, instrumentation, logging_unified, lru_cache_ttl, metrics, observability, security_config, storage_backend, tool_events |

### utils/ Key Observations:

**🚨 CHAOS:**
- 37 Python files with **ZERO folder structure**
- 9 `file_utils_*.py` files - should be in `file_utils/` folder
- 4 `conversation_*.py` files - should be in `conversation/` folder
- No organization, difficult to navigate

**⚠️ DUPLICATES:**
- `utils/conversation_*.py` (4 files) vs `src/conversation/` (4 files) - Same functionality?
- `utils/` (37 files) vs `src/utils/` (2 files) - Why separate?

**📊 LARGEST FILES:**
- `conversation_history.py` (24.2KB)
- `conversation_threads.py` (16KB)
- `error_handling.py` (13KB)
- `file_utils_reading.py` (12.8KB)

---

## LARGE FILES ANALYSIS (>10KB)

**Top 20 Largest Files (excluding docs/archive):**

| Size (KB) | Path | Category |
|-----------|------|----------|
| 55.3 | tools/simple/base.py | SHARED BASE CLASS |
| 54.4 | src/daemon/ws_server.py | SYSTEM CORE |
| 38.5 | src/providers/openai_compatible.py | PROVIDER |
| 35.8 | tools/workflows/docgen.py | WORKFLOW TOOL |
| 34.5 | tools/workflows/debug.py | WORKFLOW TOOL |
| 34.1 | tools/workflow/expert_analysis.py | **SHARED MIXIN** |
| 31.8 | tools/workflows/tracer.py | WORKFLOW TOOL |
| 31.7 | tools/workflows/secaudit.py | WORKFLOW TOOL |
| 31.2 | tools/providers/kimi/kimi_tools_chat.py | PROVIDER TOOL |
| 30.6 | tools/workflows/testgen.py | WORKFLOW TOOL |
| 30.5 | tools/workflow/base.py | SHARED BASE CLASS |
| 29.1 | tools/workflows/consensus.py | WORKFLOW TOOL |
| 29.1 | tools/workflows/refactor.py | WORKFLOW TOOL |
| 28.5 | tools/workflows/codereview.py | WORKFLOW TOOL |
| 28.2 | tools/workflows/planner.py | WORKFLOW TOOL |
| 27.7 | tools/workflows/analyze.py | WORKFLOW TOOL |
| 27.6 | tools/workflows/precommit.py | WORKFLOW TOOL |
| 27.1 | tools/workflows/thinkdeep.py | WORKFLOW TOOL |
| 26.9 | tools/workflow/orchestration.py | SHARED INFRASTRUCTURE |
| 26.5 | tools/shared/base_tool_file_handling.py | SHARED BASE CLASS |

### Large Files Observations:

**🔍 SHARED INFRASTRUCTURE (Large files affecting multiple systems):**
1. `tools/simple/base.py` (55.3KB) - SimpleTool base class
2. `tools/workflow/expert_analysis.py` (34.1KB) - **Used by ALL workflow tools**
3. `tools/workflow/base.py` (30.5KB) - WorkflowTool base class
4. `tools/workflow/orchestration.py` (26.9KB) - Workflow orchestration
5. `tools/shared/base_tool_file_handling.py` (26.5KB) - File handling mixin

**⚠️ RISK:** Changes to these files affect MANY tools!

---

## README FILES INVENTORY

| Path | Purpose |
|------|---------|
| README.md | Main project README |
| docs/README.md | Documentation index (legacy?) |
| docs/architecture/README.md | Architecture documentation |
| docs/architecture/core-systems/backbone-xray/README.md | Backbone analysis |
| docs/handoff-next-agent/README.md | Agent handoff guide |
| docs/ARCHAEOLOGICAL_DIG/README_ARCHAEOLOGICAL_DIG_STATUS.md | This investigation |
| tests/unit/README.md | Unit tests guide |
| tool_validation_suite/README_CURRENT.md | Tool validation guide |

---

## NEXT STEPS FOR TASK 0.2

**Now that we have complete inventory, we can:**
1. Identify ALL shared components (base classes, mixins)
2. Map dependencies (what imports what)
3. Detect duplicates (same functionality in multiple places)
4. Understand architecture pattern

**Key Questions to Answer:**
- Why `src/conf/` AND `src/config/`?
- Why `src/conversation/` AND `src/server/conversation/`?
- Why `src/providers/` AND `src/server/providers/`?
- Why `tools/workflow/` AND `tools/workflows/`?
- Why `utils/` (37 files) AND `src/utils/` (2 files)?
- Why is `tools/workflow/expert_analysis.py` (34KB shared mixin) in workflow/ folder?

---

**STATUS:** ✅ TASK 0.1 COMPLETE

Complete system inventory created. Ready for Task 0.2: Shared Infrastructure Identification.

