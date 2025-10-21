# SYSTEM ARCHITECTURE - COMPREHENSIVE LAYOUT MAP
**Date:** 2025-10-10 (10th October 2025, Thursday)
**Category:** Overall System Architecture
**Status:** 🔍 Comprehensive Investigation In Progress
**Last Updated:** 2025-10-10 11:56 AM AEDT

---

## PURPOSE

This document maps the **complete system architecture** based on comprehensive archaeological dig findings to understand:
1. How all components connect
2. What's active vs orphaned
3. Where duplications exist
4. Where disconnections exist
5. How to fix the system systematically

---

## 🚨 CRITICAL DISCOVERIES

### Major Architectural Issues Found

**1. DUPLICATE FOLDERS (Multiple Locations)**
- `conf/` vs `src/config/` - Configuration duplication
- `conversation/` vs `src/server/conversation/` - Conversation duplication
- `providers/` vs `src/server/providers/` - Provider duplication
- `utils/` vs `src/utils/` vs `src/server/utils/` - Triple utils duplication!
- `workflow/` vs `workflows/` - Confusing similar names
- `streaming/` vs `tools/streaming/` - Streaming duplication

**2. DISCONNECTED SYSTEMS**
- `systemprompts/` (15 files) - May not be connected to tools
- `src/utils/timezone.py` - May not be imported anywhere
- `src/utils/async_logging.py` - May not be used
- `monitoring/` (9 files) - Unknown if active
- `security/` (2 files) - Unknown if active
- `streaming/` (1 file) - Unknown if active

**3. CHAOTIC ORGANIZATION**
- `utils/` - 30+ scripts with NO folder structure
- `tools/` - 13 subfolders with unclear organization
- `src/providers/` - 20+ files in flat structure

---

## HIGH-LEVEL ARCHITECTURE

### Request Flow (Preliminary Understanding)

```
┌─────────────────────────────────────────────────────────────┐
│                     AUGMENT IDE (Client)                     │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ MCP Protocol (stdio)
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              scripts/run_ws_shim.py (MCP Entry)              │
│  - Converts MCP requests to WebSocket messages               │
│  - Handles list_tools and call_tool                          │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ WebSocket (port 8765)
                            ↓
┌─────────────────────────────────────────────────────────────┐
│           src/daemon/ws_server.py (WS Daemon)                │
│  - WebSocket server on port 8765                             │
│  - Session management                                        │
│  - Routes to request handler                                 │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────┐
│      src/server/handlers/request_handler.py (Router)         │
│  - Model selection (auto or explicit)                        │
│  - Tool execution orchestration                              │
│  - Provider selection                                        │
└───────────────────────────┬─────────────────────────────────┘
                            │
                ┌───────────┴───────────┐
                ↓                       ↓
┌───────────────────────┐   ┌───────────────────────┐
│   TOOLS (tools/)      │   │  PROVIDERS (src/     │
│  - 40+ tool files     │   │   providers/)         │
│  - 13 subfolders      │   │  - kimi.py            │
│  - Workflow tools     │   │  - glm_chat.py        │
│  - Simple tools       │   │  - registry.py        │
│  - Diagnostic tools   │   │  - 20+ files          │
└───────────────────────┘   └───────────────────────┘
                │                       │
                └───────────┬───────────┘
                            ↓
                ┌───────────────────────┐
                │  SYSTEM PROMPTS?      │
                │  (systemprompts/)     │
                │  - 15 specialized     │
                │  - May be bypassed    │
                └───────────────────────┘
```

---

## COMPLETE FOLDER INVENTORY

### Root Level Folders
```
EX-AI-MCP-Server/
├── .logs/                       # JSONL logs (current)
├── docs/                        # Documentation
├── logs/                        # Better-designed logs (disconnected?)
├── monitoring/                  # Monitoring infrastructure (9 files)
├── scripts/                     # Entry point scripts
├── security/                    # RBAC implementation (2 files)
├── src/                         # Source code (11 subfolders)
├── streaming/                   # Streaming adapter (1 file)
├── systemprompts/               # System prompts (15 files)
├── tools/                       # Tool implementations (40+ files)
└── utils/                       # Utilities (30+ files, chaotic)
```

### src/ Subfolders (WITH DUPLICATES!)
```
src/
├── bootstrap/                   # System initialization (3 files)
├── conf/                        # Config files (JSON) ⚠️ DUPLICATE
├── config/                      # Config module ⚠️ DUPLICATE
├── conversation/                # Conversation mgmt ⚠️ DUPLICATE
├── core/                        # Core functionality (2 files)
├── daemon/                      # WebSocket daemon (2 files)
├── embeddings/                  # Embeddings provider (1 file)
├── providers/                   # Providers (20+ files) ⚠️ DUPLICATE
├── router/                      # Request routing (4 files)
├── server/                      # Server components
│   ├── conversation/            # ⚠️ DUPLICATE of src/conversation/
│   ├── providers/               # ⚠️ DUPLICATE of src/providers/
│   └── utils/                   # ⚠️ DUPLICATE of src/utils/
└── utils/                       # Clean utilities (2 files) ⚠️ DUPLICATE
```

### tools/ Subfolders (CONFUSING NAMES!)
```
tools/
├── audits/                      # Audit tools (1 file)
├── capabilities/                # Capability tools (5 files)
├── cost/                        # Cost optimization (2 files)
├── diagnostics/                 # Diagnostic tools (8 files)
├── providers/                   # Provider tools ⚠️ DUPLICATE?
├── reasoning/                   # Reasoning tools (1 file)
├── shared/                      # Base classes (8 files)
├── simple/                      # Simple tool base (3 files)
├── streaming/                   # Streaming tools ⚠️ DUPLICATE?
├── workflow/                    # Workflow base ⚠️ CONFUSING NAME
├── workflows/                   # Workflow impls ⚠️ CONFUSING NAME
└── (root files)                 # Individual tools
```

---

## DETAILED COMPONENT ANALYSIS

### 1. MONITORING INFRASTRUCTURE (monitoring/)
**Files:** 9 Python files + 1 markdown
**Status:** ❓ Unknown if active
**Features:**
- autoscale.py - Auto-scaling logic
- health_monitor.py - Health monitoring
- telemetry.py - Telemetry collection
- slo.py - Service Level Objectives
- predictive.py - Predictive monitoring
- worker_pool.py - Worker pool management

**Investigation:** See `docs/ARCHAEOLOGICAL_DIG/monitoring/MONITORING_INFRASTRUCTURE_ANALYSIS.md`

### 2. SECURITY & RBAC (security/)
**Files:** 2 Python files
**Status:** ❓ Unknown if active
**Features:**
- rbac.py - Role-Based Access Control
- rbac_config.py - RBAC configuration

**Use Cases:**
- Multi-user access control
- Permission management
- API key management
- Cost control per user

**Investigation:** See `docs/ARCHAEOLOGICAL_DIG/security/SECURITY_RBAC_IMPLEMENTATION.md`

### 3. STREAMING (streaming/)
**Files:** 1 Python file
**Status:** ❓ Unknown if active
**Features:**
- streaming_adapter.py - Streaming response adapter

**Duplicate Alert:** Also `tools/streaming/` folder exists!

**Investigation:** See `docs/ARCHAEOLOGICAL_DIG/streaming/STREAMING_ADAPTER_ARCHITECTURE.md`

### 4. SYSTEM PROMPTS (systemprompts/)
**Files:** 15 specialized prompts
**Status:** ❓ May be bypassed by hardcoded prompts
**Design:** Modular, well-organized
**Prompts:**
- chat_prompt.py, debug_prompt.py, analyze_prompt.py
- codereview_prompt.py, consensus_prompt.py, docgen_prompt.py
- planner_prompt.py, precommit_prompt.py, refactor_prompt.py
- secaudit_prompt.py, testgen_prompt.py, thinkdeep_prompt.py
- tracer_prompt.py, base_prompt.py

**Investigation:** See `docs/ARCHAEOLOGICAL_DIG/prompts/SYSTEMPROMPTS_BYPASS_INVESTIGATION.md`

### 5. TOOLS (tools/)
**Files:** 40+ files across 13 subfolders
**Status:** ✅ Core active system
**Architecture:** Three-layer design (shared → simple/workflow → implementations)

**Critical Issues:**
- workflow/ vs workflows/ (confusing names)
- tools/streaming/ vs streaming/ (duplicate?)
- tools/providers/ vs src/providers/ (duplicate?)

**Investigation:** See `docs/ARCHAEOLOGICAL_DIG/tools/TOOLS_FOLDER_STRUCTURE_ANALYSIS.md`

### 6. SRC STRUCTURE (src/)
**Files:** 11 subfolders with MULTIPLE DUPLICATES
**Status:** ✅ Core active system with duplication issues

**Critical Duplicates:**
- conf/ vs config/
- conversation/ vs server/conversation/
- providers/ vs server/providers/
- utils/ vs server/utils/

**Investigation:** See `docs/ARCHAEOLOGICAL_DIG/src_structure/SRC_FOLDER_DUPLICATION_ANALYSIS.md`

### 7. UTILITIES (utils/)
**Files:** 30+ scripts with NO organization
**Status:** ❓ Unknown which are active
**Issues:**
- Flat structure (no folders)
- 7 file_utils_*.py scripts (likely duplicates)
- 4 conversation_*.py scripts (unclear purpose)

**Investigation:** See `docs/ARCHAEOLOGICAL_DIG/utilities/UTILS_FOLDER_CHAOS_AUDIT.md`

### 8. TIMEZONE (src/utils/timezone.py)
**Status:** ✅ Excellent implementation
**Issue:** 🚨 Hardcoded to Melbourne timezone
**Features:** Multiple format options, AEDT/AEST handling

**Investigation:** See `docs/ARCHAEOLOGICAL_DIG/timezone/TIMEZONE_DETECTION_STRATEGY.md`

### 9. MESSAGE BUS (src/core/message_bus_client.py)
**Status:** ✅ Well-designed (455 lines)
**Issue:** ✅ Type error FIXED!
**Features:**
- Large payload support (100MB)
- Compression (gzip/zstd)
- Circuit breaker
- Checksum verification

**Investigation:** See `docs/ARCHAEOLOGICAL_DIG/message_bus/SUPABASE_MESSAGE_BUS_DESIGN.md`

### 10. MODEL ROUTING (src/providers/registry*.py)
**Files:** 4-5 registry files
**Status:** ❓ Unknown if routing rules enforced
**Issue:** kimi-latest-128k selected incorrectly

**Investigation:** See `docs/ARCHAEOLOGICAL_DIG/routing/MODEL_ROUTING_REGISTRY_ANALYSIS.md`

---

## INVESTIGATION TASKS

### Phase 0: Architectural Mapping ✅ COMPLETE

**Completed Tasks:**
- [x] Task 0.1: Layout Map - Complete System Inventory
  - [x] 22 top-level directories mapped
  - [x] 433 Python files inventoried
  - [x] Large files identified (34 files >10KB)
  - [x] Folder purposes documented

- [x] Task 0.2: Shared Infrastructure Identification
  - [x] 3 base classes identified (BaseTool, SimpleTool, WorkflowTool)
  - [x] 13 mixins identified
  - [x] 37 utils files classified
  - [x] Provider separation understood

- [x] Task 0.3: Dependency Mapping
  - [x] 4-tier architecture documented
  - [x] Import chains traced
  - [x] No circular dependencies found
  - [x] Impact radius mapped

- [x] Task 0.4: Duplicate Detection
  - [x] All duplicates investigated
  - [x] No true duplicates found (different purposes or orphaned)
  - [x] Recommendations documented

- [x] Task 0.5: Architecture Pattern Recognition
  - [x] Layered + Mixin Composition pattern identified
  - [x] 85% match with design intent
  - [x] Gaps documented

- [x] Task 0.6: Modular Refactoring Strategy
  - [x] Top-Down Design (Option C) created
  - [x] 5-phase plan (7-12 weeks)
  - [x] User approval obtained

**Documentation Created:**
- ✅ layoutmap/COMPLETE_SYSTEM_INVENTORY.md
- ✅ layoutmap/SYSTEM_ARCHITECTURE.md
- ✅ shared_infrastructure/SHARED_COMPONENTS_INVENTORY.md
- ✅ shared_infrastructure/DEPENDENCY_MAP.md
- ✅ shared_infrastructure/DUPLICATE_FUNCTIONALITY.md
- ✅ shared_infrastructure/ARCHITECTURE_PATTERN_ANALYSIS.md
- ✅ MODULAR_REFACTORING_STRATEGY.md
- ✅ OPTION_D_PRINCIPLED_REFACTORING.md

---

### Phase 1: Discovery & Classification ✅ COMPLETE

**For Each Category:**
- [x] Search for imports in codebase
- [x] Check .env configuration
- [x] Read implementation files
- [x] Classify: ACTIVE / ORPHANED / PLANNED
- [x] Document findings
- [x] Execute cleanup strategy

**Categories Investigated:**
- [x] System Prompts (15 files) - ✅ ACTIVE - Fully integrated
- [x] Timezone (1 file) - ✅ ACTIVE - In use
- [x] Model Routing (4-5 files) - ✅ ACTIVE - Working as designed
- [x] Utilities (37 files) - ✅ ACTIVE - Reorganized into 6 folders
- [x] Monitoring (9 files) - ⚠️ PLANNED - Archived (0 imports)
- [x] Security/RBAC (2 files) - ⚠️ PLANNED - Archived (0 imports)
- [x] Streaming (2 locations) - ⚠️ MIXED - tools/streaming/ archived (empty)
- [x] Tools Structure (40+ files) - ✅ ACTIVE - Different purposes confirmed
- [x] Src Duplicates (multiple folders) - ⚠️ MIXED - Orphaned deleted, active kept
- [x] Message Bus - ✅ ACTIVE - Type error fixed, design documented

**Cleanup Actions Completed:**
- [x] Phase 1.A: Deleted 4 orphaned directories (src/conf/, src/config/, src/server/conversation/, tools/streaming/)
- [x] Phase 1.B: Archived 3 planned systems (monitoring/, security/, streaming/)
- [x] Phase 1.C: Reorganized utils/ into 6 folders (37 files)
- [x] Fixed circular imports (utils.model.context, utils.model.restrictions)
- [x] Archived instrumentation.py (0 imports, depends on archived monitoring/)
- [x] All changes committed and pushed

**Documentation Created:**
- ✅ prompts/SYSTEMPROMPTS_BYPASS_INVESTIGATION.md
- ✅ timezone/TIMEZONE_DETECTION_STRATEGY.md
- ✅ routing/MODEL_ROUTING_REGISTRY_ANALYSIS.md
- ✅ utilities/UTILS_FOLDER_CHAOS_AUDIT.md
- ✅ monitoring/MONITORING_INFRASTRUCTURE_ANALYSIS.md
- ✅ security/SECURITY_RBAC_IMPLEMENTATION.md
- ✅ streaming/STREAMING_ADAPTER_ARCHITECTURE.md
- ✅ tools/TOOLS_FOLDER_STRUCTURE_ANALYSIS.md
- ✅ src_structure/SRC_FOLDER_DUPLICATION_ANALYSIS.md
- ✅ CONSOLIDATION_STRATEGY.md
- ✅ MASTER_CHECKLIST_PHASE1.md
- ✅ MASTER_CHECKLIST_PHASE1_CLEANUP.md
- ✅ AUDIT_TRAIL_PHASE1.md

---

### Phase 2: Map Connections ⏳ NEXT

**Goal:** Map HOW active components connect and communicate

**Investigation Tasks:**
- [ ] Task 2.1: Entry Point Analysis (30 min)
  - [ ] Map scripts/run_ws_shim.py execution flow
  - [ ] Map src/daemon/ws_server.py execution flow
  - [ ] Map src/server/handlers/request_handler.py execution flow
  - [ ] Create ENTRY_POINTS_FLOW_MAP.md

- [ ] Task 2.2: Tool Execution Flow Tracing (45 min)
  - [ ] Trace tool registry and discovery
  - [ ] Trace SimpleTool execution path
  - [ ] Trace WorkflowTool execution path
  - [ ] Create TOOL_EXECUTION_FLOW.md

- [ ] Task 2.3: Provider Integration Mapping (30 min)
  - [ ] Trace provider registry and selection
  - [ ] Trace Kimi provider execution
  - [ ] Trace GLM provider execution
  - [ ] Create PROVIDER_INTEGRATION_MAP.md

- [ ] Task 2.4: Utils Dependency Tracing (60 min)
  - [ ] Map utils/file/ imports
  - [ ] Map utils/conversation/ imports
  - [ ] Map utils/model/ imports
  - [ ] Map high-traffic utils (progress.py, observability.py)
  - [ ] Create UTILS_DEPENDENCY_MAP.md

- [ ] Task 2.5: SimpleTool Connection Analysis (45 min)
  - [ ] Map upstream dependencies (tools using SimpleTool)
  - [ ] Map downstream dependencies (SimpleTool imports)
  - [ ] Identify critical public interface (CANNOT CHANGE)
  - [ ] Create SIMPLETOOL_CONNECTION_MAP.md

- [ ] Task 2.6: WorkflowTool Connection Analysis (45 min)
  - [ ] Map upstream dependencies (12 workflow tools)
  - [ ] Map downstream dependencies (mixins, utils)
  - [ ] Map ExpertAnalysisMixin integration
  - [ ] Create WORKFLOWTOOL_CONNECTION_MAP.md

- [ ] Task 2.7: Data Flow Mapping (60 min)
  - [ ] Trace complete request lifecycle
  - [ ] Map data transformation points
  - [ ] Identify validation points
  - [ ] Create DATA_FLOW_MAP.md

- [ ] Task 2.8: Critical Path Identification (30 min)
  - [ ] Identify top 5 critical execution paths
  - [ ] Identify bottlenecks
  - [ ] Create CRITICAL_PATHS.md

- [ ] Task 2.9: Integration Pattern Documentation (30 min)
  - [ ] Document mixin composition pattern
  - [ ] Document facade pattern usage
  - [ ] Document registry pattern usage
  - [ ] Create INTEGRATION_PATTERNS.md

- [ ] Task 2.10: Create Phase 2 Summary & Call Graph (60 min)
  - [ ] Synthesize all Phase 2 findings
  - [ ] Create visual call graph (Mermaid)
  - [ ] Document key insights for Phase 3
  - [ ] Create PHASE2_COMPREHENSIVE_SUMMARY.md

**Estimated Time:** ~7 hours

**Documentation to Create:**
- ⏳ ENTRY_POINTS_FLOW_MAP.md
- ⏳ TOOL_EXECUTION_FLOW.md
- ⏳ PROVIDER_INTEGRATION_MAP.md
- ⏳ UTILS_DEPENDENCY_MAP.md
- ⏳ SIMPLETOOL_CONNECTION_MAP.md
- ⏳ WORKFLOWTOOL_CONNECTION_MAP.md
- ⏳ DATA_FLOW_MAP.md
- ⏳ CRITICAL_PATHS.md
- ⏳ INTEGRATION_PATTERNS.md
- ⏳ PHASE2_COMPREHENSIVE_SUMMARY.md

**See:** `MASTER_CHECKLIST_PHASE2.md` for detailed task breakdown

---

### Phase 3: SimpleTool Refactoring (Top-Down Design) ⏳ FUTURE

**Goal:** Refactor SimpleTool using Top-Down Design (Option C - Hybrid)

**Approach:** Facade Pattern + Top-Down Design
- SimpleTool becomes thin orchestrator
- Delegates to conceptual modules
- Maintains 100% backward compatibility
- Organizes by domain language (definition, intake, preparation, execution, delivery)

**Refactoring Plan:**
- [ ] Phase 3.1: Document Design Intent (1-2 weeks)
  - [ ] Document SimpleTool's single responsibility
  - [ ] Identify misplaced responsibilities
  - [ ] Create design intent documents
  - [ ] Get user approval

- [ ] Phase 3.2: Create Foundation (1 week)
  - [ ] Create folder structure (5 folders)
  - [ ] Create __init__.py files
  - [ ] Set up backward compatibility

- [ ] Phase 3.3: Implement Top-Down Design (2-3 weeks)
  - [ ] Create definition/ module (schema, contract)
  - [ ] Create intake/ module (request processing)
  - [ ] Create preparation/ module (prompt building)
  - [ ] Create execution/ module (model calling)
  - [ ] Create delivery/ module (response formatting)

- [ ] Phase 3.4: Update Dependencies (1 week)
  - [ ] Update 4 simple tools
  - [ ] Update tests
  - [ ] Verify backward compatibility

- [ ] Phase 3.5: Testing & Validation (1 week)
  - [ ] Run all tests
  - [ ] Verify all 4 tools work
  - [ ] Performance testing
  - [ ] User acceptance testing

**Estimated Time:** 7-12 weeks

**See:** `phase1_refactoring/design_intent/SIMPLETOOL_DESIGN_INTENT_TOP_DOWN.md`

---

### Phase 4: WorkflowTool Refactoring ⏳ FUTURE

**Goal:** Refactor WorkflowTool and ExpertAnalysisMixin

**Approach:** Similar to SimpleTool refactoring
- Split ExpertAnalysisMixin (34.1KB) into focused modules
- Split OrchestrationMixin into focused modules
- Each module has ONE clear purpose

**Estimated Time:** 2-3 weeks

---

### Phase 5: Final Cleanup & Documentation ⏳ FUTURE

**Goal:** Final polish and comprehensive documentation

**Tasks:**
- [ ] Update all documentation
- [ ] Create architecture diagrams
- [ ] Write developer guide
- [ ] Create onboarding documentation

**Estimated Time:** 1-2 weeks

---

---

## CRITICAL QUESTIONS & HYPOTHESES

### 1. Why So Many Duplicate Folders?

**Duplicates Found:**
1. conf/ vs config/
2. conversation/ vs server/conversation/
3. providers/ vs server/providers/
4. utils/ vs server/utils/ vs utils/ (root)
5. workflow/ vs workflows/
6. streaming/ vs tools/streaming/

**Hypothesis:**
- System has grown organically
- Multiple refactoring attempts
- Incomplete migrations
- Unclear separation of concerns

**Evidence Needed:**
- Git history analysis
- Import chain analysis
- Active vs orphaned determination

### 2. What's the Intended Architecture?

**Option A: Layered Architecture**
```
src/
├── core/           # Core libraries
├── providers/      # Provider implementations
├── utils/          # Shared utilities
└── server/         # Server application layer
    ├── handlers/   # Request handlers
    ├── providers/  # Server-side provider handling
    └── utils/      # Server-specific utilities
```

**Option B: Feature-Based Architecture**
```
src/
├── conversation/   # All conversation code
├── providers/      # All provider code
├── routing/        # All routing code
└── server/         # Server entry point only
```

**Option C: Hybrid (Current State?)**
```
src/
├── (mix of both patterns)
└── (resulting in duplicates)
```

**Need to determine:**
- Which architecture is intended?
- Is current structure intentional?
- Should it be refactored?

### 3. Logging Architecture

**Two Log Folders:**
- `.logs/` - JSONL logs (current, active)
- `logs/` - Better-designed logs (disconnected?)

**User's Insight:**
> "Under logs it looks way more designed better, but it appears disconnected fundamentally"

**Questions:**
- What's in logs/ that's better?
- Why is it disconnected?
- Should .logs/ be migrated to logs/?
- Or should logs/ be removed?

**Related:**
- src/utils/async_logging.py (may not be used)
- monitoring/file_sink.py (metrics to files)
- monitoring/telemetry.py (telemetry collection)

### 4. Provider Registry System

**Multiple Registry Files:**
- src/providers/registry.py
- src/providers/registry_config.py
- src/providers/registry_core.py
- src/providers/registry_selection.py
- src/providers/provider_registration.py
- src/server/providers/provider_registration.py (duplicate?)

**Questions:**
- Are these all part of one system?
- Or multiple competing systems?
- Which is active?
- Why provider_registration.py in two places?

### 5. Tools Architecture

**Confusing Folder Names:**
- tools/workflow/ (base classes)
- tools/workflows/ (implementations)

**Questions:**
- Why similar names?
- Is this intentional?
- Should workflow/ be renamed to workflow_base/?
- Or moved into shared/?

### 6. Streaming Implementation

**Two Streaming Locations:**
- streaming/streaming_adapter.py (1 file)
- tools/streaming/ (unknown contents)

**Questions:**
- Are these related?
- Is one deprecated?
- Should they be consolidated?
- Which is active?

### 7. System Prompts Connection

**User's Concern:**
> "I believe our current system has hardcoded script that uses generic scripts prompts and has bypassed the system prompts."

**Questions:**
- Are systemprompts/ files imported by tools?
- Or are prompts hardcoded in tools?
- Where is the bypass happening?
- How should they be connected?

### 8. Timezone Hardcoding

**Issue:** Hardcoded to Melbourne timezone

**Questions:**
- How should user timezone be detected?
- Environment variable?
- OS detection?
- Client-side detection?
- Supabase user preferences?

### 9. Security & RBAC

**Minimal Implementation:**
- Only 2 files (rbac.py, rbac_config.py)

**Questions:**
- Is RBAC active?
- Is system single-user or multi-user?
- Is authentication implemented?
- Where are user credentials stored?

### 10. Monitoring Status

**Comprehensive System:**
- 9 monitoring files
- Advanced features (predictive, SLO, autoscale)

**Questions:**
- Is monitoring active?
- Are metrics being collected?
- Where are metrics stored?
- Is this planned for future?

---

## COMPREHENSIVE ARCHITECTURE ASSESSMENT

### Strengths ✅

**Well-Designed Systems Found:**
1. ✅ **Message Bus** - Robust Supabase integration (455 lines, type error fixed)
2. ✅ **System Prompts** - 15 specialized prompts with modular design
3. ✅ **Timezone Utility** - Comprehensive timezone handling
4. ✅ **Async Logging** - Async-safe logging infrastructure
5. ✅ **Tools Architecture** - Three-layer design (shared → simple/workflow → implementations)
6. ✅ **Workflow Pattern** - Each workflow has 3 files (main, config, models)
7. ✅ **Provider Registry** - Model selection logic (4-5 files)
8. ✅ **Monitoring System** - Comprehensive monitoring (9 files)
9. ✅ **Security/RBAC** - Role-based access control (2 files)
10. ✅ **Streaming Adapter** - Streaming response handling

### Issues Resolved ✅

**Phase 1 Cleanup Completed:**
1. ✅ **Orphaned Directories Deleted**
   - src/conf/ (1 file, 0 imports) - DELETED
   - src/config/ (only __pycache__) - DELETED
   - src/server/conversation/ (empty) - DELETED
   - tools/streaming/ (empty) - DELETED

2. ✅ **Planned Infrastructure Archived**
   - monitoring/ (9 files, 0 imports) - ARCHIVED
   - security/ (2 files, 0 imports) - ARCHIVED
   - streaming/ (1 file, 0 imports) - ARCHIVED
   - instrumentation.py (0 imports) - ARCHIVED

3. ✅ **Utils Reorganized**
   - 37 files reorganized into 6 folders
   - utils/file/ (9 files)
   - utils/conversation/ (4 files)
   - utils/model/ (4 files)
   - utils/config/ (3 files)
   - utils/progress_utils/ (1 file)
   - utils/infrastructure/ (7 files)
   - High-traffic files kept at root (progress.py, observability.py, etc.)

4. ✅ **Circular Imports Fixed**
   - utils.model.context - imports moved inside methods
   - utils.model.restrictions - used __future__ annotations

5. ✅ **All Systems Validated**
   - systemprompts/ - ✅ ACTIVE (14 imports, fully integrated)
   - timezone.py - ✅ ACTIVE (2 imports, in use)
   - model routing - ✅ ACTIVE (working as designed)
   - async_logging.py - ✅ ACTIVE (used by logging system)

### Remaining Work 🔄

**Phase 2: Map Connections** (⏳ NEXT - ~7 hours)
- Trace execution flow from entry points
- Map tool execution paths
- Document provider integration
- Map utils dependencies
- Analyze SimpleTool/WorkflowTool connections
- Create call graphs and flow diagrams

**Phase 3: SimpleTool Refactoring** (⏳ FUTURE - 7-12 weeks)
- Implement Top-Down Design (Option C)
- 7 files across 5 conceptual folders
- Facade Pattern for backward compatibility
- Complete testing and validation

**Phase 4: WorkflowTool Refactoring** (⏳ FUTURE - 2-3 weeks)
- Refactor ExpertAnalysisMixin (34.1KB)
- Split into focused modules
- Maintain backward compatibility

**Phase 5: Final Cleanup** (⏳ FUTURE - 1-2 weeks)
- Update documentation
- Create architecture diagrams
- Write developer guide

### Root Cause Analysis

**The system has grown organically with:**

1. **Feature Addition Without Cleanup**
   - New features added
   - Old code not removed
   - Result: Working + orphaned code mixed

2. **Multiple Refactoring Attempts**
   - Refactoring started
   - Not completed
   - Result: Duplicate folders

3. **Good Designs Not Integrated**
   - Excellent utilities created
   - Not connected to system
   - Result: Disconnected components

4. **Unclear Separation of Concerns**
   - Multiple attempts at organization
   - No clear architecture pattern
   - Result: Confusing structure

**Evidence:**
- Backup files (ws_server.py.backup)
- Duplicate folders with similar names
- Orphaned code (likely)
- Disconnected utilities

---

## INVESTIGATION STRATEGY

### Phase 1: Determine Active vs Orphaned (IN PROGRESS)

**Method:**
```bash
# For each component/folder
1. Search for imports: grep -r "from {component} import" .
2. Check .env configuration
3. Read implementation
4. Classify: ACTIVE / ORPHANED / DUPLICATE
5. Document in investigation markdown
```

**Status:**
- [x] Message Bus - ACTIVE (type error fixed)
- [ ] Monitoring - Unknown
- [ ] Security - Unknown
- [ ] Streaming - Unknown
- [ ] System Prompts - Unknown (likely bypassed)
- [ ] Timezone - Unknown (likely orphaned)
- [ ] Model Routing - Unknown (likely broken)
- [ ] Utilities - Unknown (30+ files)
- [ ] Tools - ACTIVE (but confusing structure)
- [ ] Src Duplicates - Unknown

### Phase 2: Map Active Code Paths

**Method:**
1. Start from entry point (scripts/run_ws_shim.py)
2. Trace every import
3. Build call graph
4. Mark files as ACTIVE
5. Identify critical paths

**Output:**
- Call graph diagram
- Active file list
- Critical path documentation

### Phase 3: Identify Duplicates

**Method:**
1. Group files by purpose
2. Compare functionality
3. Search for imports of each
4. Identify which is active
5. Mark others as DUPLICATE

**Duplicate Pairs to Investigate:**
- conf/ vs config/
- conversation/ vs server/conversation/
- providers/ vs server/providers/
- utils/ vs server/utils/ vs utils/ (root)
- workflow/ vs workflows/
- streaming/ vs tools/streaming/

### Phase 4: Consolidation Strategy

**For Each Duplicate:**
1. Determine which is active
2. Identify best implementation
3. Plan migration if needed
4. Recommend consolidation approach

**Options:**
- **MERGE:** Combine into single folder
- **RENAME:** Clarify separation (e.g., workflow_base/)
- **REMOVE:** Delete orphaned code
- **MIGRATE:** Move code to correct location

### Phase 5: Reorganization Plan

**Goals:**
1. Clear architecture pattern
2. No duplicates
3. Logical folder structure
4. Connected utilities
5. Removed orphaned code

**Approach:**
- Define target architecture
- Create migration plan
- Prioritize by impact
- Break into phases
- Test after each phase

---

## INVESTIGATION DOCUMENTS

### Created Investigation Files

**Core Categories:**
1. `prompts/SYSTEMPROMPTS_BYPASS_INVESTIGATION.md`
2. `timezone/TIMEZONE_DETECTION_STRATEGY.md`
3. `routing/MODEL_ROUTING_REGISTRY_ANALYSIS.md`
4. `utilities/UTILS_FOLDER_CHAOS_AUDIT.md`
5. `message_bus/SUPABASE_MESSAGE_BUS_DESIGN.md`

**New Categories:**
6. `monitoring/MONITORING_INFRASTRUCTURE_ANALYSIS.md`
7. `security/SECURITY_RBAC_IMPLEMENTATION.md`
8. `streaming/STREAMING_ADAPTER_ARCHITECTURE.md`
9. `tools/TOOLS_FOLDER_STRUCTURE_ANALYSIS.md`
10. `src_structure/SRC_FOLDER_DUPLICATION_ANALYSIS.md`

**Master Documents:**
11. `layoutmap/SYSTEM_ARCHITECTURE.md` (this file)
12. `00_CONTEXT_AND_SCOPE.md`
13. `README_ARCHAEOLOGICAL_DIG_STATUS.md`

---

## PROGRESS SUMMARY

### Phase 0: Architectural Mapping ✅ COMPLETE (2025-10-10)
1. ✅ Complete system inventory (433 Python files)
2. ✅ Shared infrastructure identification (3 base classes, 13 mixins)
3. ✅ Dependency mapping (4-tier architecture, no circular dependencies)
4. ✅ Duplicate detection (no true duplicates found)
5. ✅ Architecture pattern recognition (Layered + Mixin Composition)
6. ✅ Modular refactoring strategy (Top-Down Design approved)

### Phase 1: Discovery & Classification ✅ COMPLETE (2025-10-10)
1. ✅ All 9 categories investigated and classified
2. ✅ Orphaned directories deleted (4 directories)
3. ✅ Planned infrastructure archived (3 systems)
4. ✅ Utils folder reorganized (37 files → 6 folders)
5. ✅ Circular imports fixed (2 files)
6. ✅ All changes committed and pushed
7. ✅ Consolidation strategy executed

### Phase 2: Map Connections ⏳ NEXT (~7 hours)
1. ⏳ Entry point analysis
2. ⏳ Tool execution flow tracing
3. ⏳ Provider integration mapping
4. ⏳ Utils dependency tracing
5. ⏳ SimpleTool connection analysis (critical for refactoring)
6. ⏳ WorkflowTool connection analysis
7. ⏳ Data flow mapping
8. ⏳ Critical path identification
9. ⏳ Integration pattern documentation
10. ⏳ Comprehensive summary with call graphs

### Phase 3: SimpleTool Refactoring ⏳ FUTURE (7-12 weeks)
- Top-Down Design (Option C - Hybrid)
- 7 files across 5 conceptual folders
- Facade Pattern for backward compatibility
- Complete testing and validation

### Phase 4: WorkflowTool Refactoring ⏳ FUTURE (2-3 weeks)
- Refactor ExpertAnalysisMixin (34.1KB)
- Split into focused modules
- Maintain backward compatibility

### Phase 5: Final Cleanup ⏳ FUTURE (1-2 weeks)
- Update documentation
- Create architecture diagrams
- Write developer guide

---

## SUCCESS CRITERIA

### Phase 0 ✅ COMPLETE
- [x] All components mapped
- [x] Dependencies understood
- [x] Architecture pattern identified
- [x] Refactoring strategy approved

### Phase 1 ✅ COMPLETE
- [x] All components classified (ACTIVE/ORPHANED/PLANNED)
- [x] All orphaned code removed
- [x] All planned infrastructure archived
- [x] Utils folder reorganized
- [x] All changes committed and pushed
- [x] User approval obtained

### Phase 2 ⏳ NEXT
- [ ] All entry points mapped
- [ ] Tool execution flow documented
- [ ] Provider integration mapped
- [ ] Utils dependencies traced
- [ ] SimpleTool connections mapped (critical for refactoring)
- [ ] WorkflowTool connections mapped
- [ ] Data flow documented
- [ ] Critical paths identified
- [ ] Integration patterns documented
- [ ] Comprehensive summary created with visual diagrams
- [ ] User approval obtained

### Phase 3 ⏳ FUTURE
- [ ] SimpleTool refactored using Top-Down Design
- [ ] All 4 simple tools working
- [ ] Tests passing
- [ ] User approval obtained

---

**STATUS: PHASE 1 COMPLETE - READY FOR PHASE 2**

**This is the master architecture document that ties all investigations together.**

**All investigation documents are in:** `docs/ARCHAEOLOGICAL_DIG/`

**Next Action:** Begin Phase 2 - Map Connections (see `MASTER_CHECKLIST_PHASE2.md`)

**Last Updated:** 2025-10-10 (Phase 1 complete, Phase 2 checklist created)

