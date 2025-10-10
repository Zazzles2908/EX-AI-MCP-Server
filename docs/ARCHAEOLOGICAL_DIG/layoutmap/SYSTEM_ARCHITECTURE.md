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

### Phase 1: Determine Active vs Orphaned (IN PROGRESS)

**For Each Category:**
- [ ] Search for imports in codebase
- [ ] Check .env configuration
- [ ] Read implementation files
- [ ] Classify: ACTIVE / ORPHANED / DUPLICATE
- [ ] Document findings

**Categories:**
- [x] Message Bus (type error fixed, design documented)
- [ ] Monitoring (9 files)
- [ ] Security (2 files)
- [ ] Streaming (1 file + tools/streaming/)
- [ ] System Prompts (15 files)
- [ ] Timezone (1 file)
- [ ] Model Routing (4-5 files)
- [ ] Utilities (30+ files)
- [ ] Tools Structure (40+ files)
- [ ] Src Duplicates (multiple folders)

### Phase 2: Map Connections

**For Active Components:**
- [ ] Trace import chains
- [ ] Map data flow
- [ ] Identify entry points
- [ ] Document dependencies

### Phase 3: Identify Duplicates

**For Duplicate Folders:**
- [ ] Compare contents
- [ ] Determine which is active
- [ ] Identify best implementation
- [ ] Mark for consolidation

### Phase 4: Recommend Actions

**For Each Component:**
- **FIX:** Broken but needed
- **CONNECT:** Exists but not integrated
- **REMOVE:** Dead/orphaned code
- **CONSOLIDATE:** Merge duplicates
- **REORGANIZE:** Good code, wrong location

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

### Critical Issues 🚨

**1. MASSIVE DUPLICATION**
- conf/ vs config/
- conversation/ (2 locations)
- providers/ (2 locations)
- utils/ (3 locations!)
- workflow/ vs workflows/
- streaming/ (2 locations)

**2. DISCONNECTED SYSTEMS**
- systemprompts/ may be bypassed
- timezone.py may not be imported
- async_logging.py may not be used
- monitoring/ may not be active
- security/ may not be active
- streaming/ may not be active

**3. CHAOTIC ORGANIZATION**
- utils/ - 30+ scripts, no folders
- tools/ - 13 subfolders, confusing names
- src/providers/ - 20+ files, flat structure

**4. UNCLEAR ARCHITECTURE**
- Layered vs feature-based?
- src/ vs src/server/ separation unclear
- Multiple refactoring attempts visible
- Incomplete migrations

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

## NEXT STEPS

### Immediate (Today)
1. ✅ Create investigation structure (DONE)
2. ✅ Document all categories (DONE)
3. ✅ Fix message_bus type error (DONE)
4. ⏳ Begin import analysis for each category

### Phase 1: Import Analysis (Next)
1. Search for imports of each component
2. Check .env configuration
3. Classify: ACTIVE / ORPHANED / DUPLICATE
4. Update investigation markdowns

### Phase 2: Detailed Investigation
1. Read active components
2. Trace connections
3. Map data flow
4. Document findings

### Phase 3: Recommendations
1. Consolidation strategy
2. Reorganization plan
3. Connection strategy
4. Cleanup checklist

### Phase 4: Implementation
1. Break into phases
2. Prioritize by impact
3. Create detailed tasks
4. Get user approval
5. Execute systematically

---

## SUCCESS CRITERIA

### Investigation Complete When:
- [ ] All components classified (active/orphaned/duplicate)
- [ ] All duplicates identified
- [ ] All disconnections mapped
- [ ] All findings documented
- [ ] Recommendations created

### Ready for Implementation When:
- [ ] Clear consolidation strategy
- [ ] Phased reorganization plan
- [ ] Connection strategy defined
- [ ] Cleanup checklist created
- [ ] User approval obtained

---

**STATUS: COMPREHENSIVE INVESTIGATION IN PROGRESS**

**This is the master architecture document that ties all investigations together.**

**All investigation documents are in:** `docs/ARCHAEOLOGICAL_DIG/`

**Next Action:** Begin import analysis for each category to determine active vs orphaned status.

