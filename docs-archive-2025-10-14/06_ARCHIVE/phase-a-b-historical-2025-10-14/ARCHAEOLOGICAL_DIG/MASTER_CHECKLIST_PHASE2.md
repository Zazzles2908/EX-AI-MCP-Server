# ARCHAEOLOGICAL DIG - PHASE 2 MASTER CHECKLIST
**Branch:** archaeological-dig/phase1-discovery-and-cleanup
**Started:** 2025-10-10 (10th October 2025, Thursday)
**Completed:** 2025-10-10 (10th October 2025, Thursday)
**Purpose:** Map connections and trace execution flow for ACTIVE components
**Status:** ✅ COMPLETE - All 10 tasks finished, validated by GLM-4.6

---

## 🎯 PHASE 2 GOAL

**Map HOW active components connect and communicate:**
- Trace import chains from entry points
- Map data flow through the system
- Build call graphs for critical paths
- Document integration patterns
- Identify execution bottlenecks
- Understand component dependencies

**WHY THIS IS CRITICAL:**
- Understand system execution flow BEFORE refactoring
- Identify impact radius of changes
- Map critical paths and bottlenecks
- Document integration patterns
- Ensure informed refactoring decisions
- Prevent breaking changes during SimpleTool refactoring

---

## ✅ PREREQUISITES (MUST BE COMPLETE)

**Phase 0: Architectural Mapping** ✅ COMPLETE
- [x] Complete system inventory (433 Python files)
- [x] Shared infrastructure identification (3 base classes, 13 mixins)
- [x] Dependency mapping (4-tier architecture)
- [x] Duplicate detection (no true duplicates found)
- [x] Architecture pattern recognition (Layered + Mixin Composition)
- [x] Modular refactoring strategy created

**Phase 1: Discovery & Classification** ✅ COMPLETE
- [x] All components classified (ACTIVE/ORPHANED/PLANNED)
- [x] Orphaned directories deleted (4 directories)
- [x] Planned infrastructure archived (3 systems)
- [x] Utils folder reorganized (37 files → 6 folders)
- [x] Consolidation strategy executed
- [x] All changes committed and pushed

---

## 📋 PHASE 2 INVESTIGATION TASKS

### Task 2.1: Entry Point Analysis (30 minutes)

**Goal:** Map all entry points and their execution flow

**Entry Points to Trace:**
- [x] scripts/run_ws_shim.py (MCP Entry Point)
  - [x] List all imports
  - [x] Trace MCP protocol handling
  - [x] Map WebSocket connection setup
  - [x] Document session initialization

- [x] src/daemon/ws_server.py (WebSocket Daemon)
  - [x] List all imports
  - [x] Trace WebSocket message handling
  - [x] Map session management
  - [x] Document routing to request handler

- [x] src/server/handlers/request_handler.py (Request Router)
  - [x] List all imports
  - [x] Trace model selection logic
  - [x] Map tool execution orchestration
  - [x] Document provider selection

**Deliverable:**
- [x] Create ENTRY_POINTS_FLOW_MAP.md ✅
- [x] Document complete execution flow from IDE to tool execution ✅
- [x] Identify all critical imports at each entry point ✅
- [x] Mark task 2.1 complete in task manager ✅

**Output:** Entry point flow map with complete import chains ✅ COMPLETE

**See:** `docs/ARCHAEOLOGICAL_DIG/phase2_connections/ENTRY_POINTS_FLOW_MAP.md`

---

### Task 2.2: Tool Execution Flow Tracing (45 minutes)

**Goal:** Trace how tools are discovered, loaded, and executed

**Investigation Steps:**
- [ ] Trace tool registry (tools/registry.py)
  - [ ] How are tools discovered?
  - [ ] How is TOOL_MAP built?
  - [ ] What's the tool loading mechanism?
  
- [ ] Trace tool execution (SimpleTool path)
  - [ ] How does request reach SimpleTool?
  - [ ] What's the execution sequence?
  - [ ] How are mixins integrated?
  - [ ] How is response returned?
  
- [ ] Trace tool execution (WorkflowTool path)
  - [ ] How does request reach WorkflowTool?
  - [ ] What's the workflow execution sequence?
  - [ ] How is expert analysis triggered?
  - [ ] How are findings consolidated?

**Deliverable:**
- [ ] Create TOOL_EXECUTION_FLOW.md
- [ ] Document SimpleTool execution path
- [ ] Document WorkflowTool execution path
- [ ] Create execution sequence diagrams
- [ ] Mark task 2.2 complete in task manager

**Output:** Complete tool execution flow documentation

---

### Task 2.3: Provider Integration Mapping (30 minutes)

**Goal:** Map how providers are selected and called

**Investigation Steps:**
- [ ] Trace provider registry (src/providers/registry.py)
  - [ ] How are providers registered?
  - [ ] How is provider selection done?
  - [ ] What's the fallback mechanism?
  
- [ ] Trace provider execution (Kimi path)
  - [ ] How is Kimi provider called?
  - [ ] What's the request transformation?
  - [ ] How is response handled?
  
- [ ] Trace provider execution (GLM path)
  - [ ] How is GLM provider called?
  - [ ] What's the request transformation?
  - [ ] How is response handled?

**Deliverable:**
- [ ] Create PROVIDER_INTEGRATION_MAP.md
- [ ] Document provider selection logic
- [ ] Document request/response transformation
- [ ] Map provider-specific handling
- [ ] Mark task 2.3 complete in task manager

**Output:** Provider integration flow documentation

---

### Task 2.4: Utils Dependency Tracing (60 minutes)

**Goal:** Map which utils are used by which components

**Investigation Steps:**
- [ ] For each utils folder, trace imports:
  - [ ] utils/file/ (9 files) - who imports what?
  - [ ] utils/conversation/ (4 files) - who imports what?
  - [ ] utils/model/ (4 files) - who imports what?
  - [ ] utils/config/ (3 files) - who imports what?
  - [ ] utils/progress_utils/ (1 file) - who imports what?
  - [ ] utils/infrastructure/ (7 files) - who imports what?
  
- [ ] For high-traffic utils, map usage:
  - [ ] progress.py (24 imports) - complete usage map
  - [ ] observability.py (18 imports) - complete usage map
  - [ ] cache.py - complete usage map
  - [ ] client_info.py - complete usage map

**Deliverable:**
- [ ] Create UTILS_DEPENDENCY_MAP.md
- [ ] Document import counts for each util
- [ ] Map high-impact utils (>10 imports)
- [ ] Identify utils dependency chains
- [ ] Mark task 2.4 complete in task manager

**Output:** Complete utils dependency map

---

### Task 2.5: SimpleTool Connection Analysis (45 minutes)

**Goal:** Map all connections to/from SimpleTool (critical for refactoring)

**Investigation Steps:**
- [ ] Upstream analysis (who depends on SimpleTool?)
  - [ ] List all tools that inherit from SimpleTool
  - [ ] Map which SimpleTool methods they call
  - [ ] Identify critical public interface methods
  
- [ ] Downstream analysis (what does SimpleTool depend on?)
  - [ ] List all imports in SimpleTool
  - [ ] Map mixin dependencies
  - [ ] Map utils dependencies
  - [ ] Map provider dependencies
  
- [ ] Integration pattern analysis
  - [ ] How do mixins integrate?
  - [ ] How is BaseTool inherited?
  - [ ] How are schema builders used?

**Deliverable:**
- [ ] Create SIMPLETOOL_CONNECTION_MAP.md
- [ ] Document all upstream dependencies (tools using SimpleTool)
- [ ] Document all downstream dependencies (SimpleTool imports)
- [ ] Map critical public interface (CANNOT CHANGE)
- [ ] Identify refactoring constraints
- [ ] Mark task 2.5 complete in task manager

**Output:** Complete SimpleTool connection map (critical for Phase 3 refactoring)

---

### Task 2.6: WorkflowTool Connection Analysis (45 minutes)

**Goal:** Map all connections to/from WorkflowTool

**Investigation Steps:**
- [ ] Upstream analysis (who depends on WorkflowTool?)
  - [ ] List all workflow tools (12 tools)
  - [ ] Map which WorkflowTool methods they call
  - [ ] Identify critical public interface methods
  
- [ ] Downstream analysis (what does WorkflowTool depend on?)
  - [ ] List all imports in WorkflowTool
  - [ ] Map BaseWorkflowMixin dependencies
  - [ ] Map ExpertAnalysisMixin integration (34.1KB!)
  - [ ] Map utils dependencies
  
- [ ] Expert analysis integration
  - [ ] How is ExpertAnalysisMixin called?
  - [ ] What's the validation flow?
  - [ ] How are findings consolidated?

**Deliverable:**
- [ ] Create WORKFLOWTOOL_CONNECTION_MAP.md
- [ ] Document all upstream dependencies
- [ ] Document all downstream dependencies
- [ ] Map expert analysis integration
- [ ] Identify refactoring constraints
- [ ] Mark task 2.6 complete in task manager

**Output:** Complete WorkflowTool connection map

---

### Task 2.7: Data Flow Mapping (60 minutes)

**Goal:** Map how data flows through the entire system

**Investigation Steps:**
- [ ] Request lifecycle tracing
  - [ ] User input → MCP protocol
  - [ ] MCP → WebSocket message
  - [ ] WebSocket → Request handler
  - [ ] Request handler → Tool selection
  - [ ] Tool → Provider call
  - [ ] Provider → AI model
  - [ ] AI response → Provider
  - [ ] Provider → Tool
  - [ ] Tool → Response formatting
  - [ ] Response → WebSocket
  - [ ] WebSocket → MCP
  - [ ] MCP → User
  
- [ ] Data transformation points
  - [ ] Where is data validated?
  - [ ] Where is data enriched?
  - [ ] Where is data transformed?
  - [ ] Where is data cached?

**Deliverable:**
- [ ] Create DATA_FLOW_MAP.md
- [ ] Document complete request lifecycle
- [ ] Map all data transformation points
- [ ] Identify validation points
- [ ] Identify caching points
- [ ] Mark task 2.7 complete in task manager

**Output:** Complete data flow map with transformation points

---

### Task 2.8: Critical Path Identification (30 minutes)

**Goal:** Identify the most important execution paths

**Investigation Steps:**
- [ ] Identify critical paths:
  - [ ] Most common tool execution path
  - [ ] Error handling path (GLM-4.6 recommendation: trace error propagation across layers)
  - [ ] Streaming response path
  - [ ] File upload path
  - [ ] Conversation continuation path

- [ ] Bottleneck identification:
  - [ ] Where are performance bottlenecks?
  - [ ] Where are complexity bottlenecks?
  - [ ] Where are maintenance bottlenecks?

- [ ] Additional analysis (GLM-4.6 recommendations):
  - [ ] Document error propagation across all layers
  - [ ] Map configuration flow through system
  - [ ] Identify testing infrastructure patterns
  - [ ] Document performance metrics and characteristics

**Deliverable:**
- [ ] Create CRITICAL_PATHS.md
- [ ] Document top 5 critical paths
- [ ] Document error handling pathways
- [ ] Map configuration dependencies
- [ ] Identify bottlenecks
- [ ] Recommend optimizations
- [ ] Mark task 2.8 complete in task manager

**Output:** Critical path documentation with bottleneck analysis, error handling, and config flow

---

### Task 2.9: Integration Pattern Documentation (30 minutes)

**Goal:** Document common integration patterns used throughout the system

**Investigation Steps:**
- [ ] Identify integration patterns:
  - [ ] Mixin composition pattern
  - [ ] Facade pattern usage
  - [ ] Registry pattern usage
  - [ ] Provider abstraction pattern
  - [ ] Schema builder pattern
  
- [ ] Document pattern usage:
  - [ ] Where is each pattern used?
  - [ ] Why is each pattern used?
  - [ ] How effective is each pattern?

**Deliverable:**
- [ ] Create INTEGRATION_PATTERNS.md
- [ ] Document all patterns found
- [ ] Map pattern usage across codebase
- [ ] Recommend pattern improvements
- [ ] Mark task 2.9 complete in task manager

**Output:** Integration pattern documentation

---

### Task 2.10: Create Phase 2 Summary & Call Graph (60 minutes)

**Goal:** Synthesize all Phase 2 findings into comprehensive summary

**Investigation Steps:**
- [ ] Review all Phase 2 deliverables
- [ ] Create visual call graph (Mermaid diagram)
- [ ] Synthesize key findings
- [ ] Identify insights for Phase 3 refactoring
- [ ] Document recommendations

**Deliverable:**
- [ ] Create PHASE2_COMPREHENSIVE_SUMMARY.md
- [ ] Include visual call graph (Mermaid)
- [ ] Include execution flow diagrams
- [ ] Include key findings and insights
- [ ] Include recommendations for Phase 3
- [ ] Mark task 2.10 complete in task manager

**Output:** Comprehensive Phase 2 summary with visual diagrams

---

## 📊 PROGRESS TRACKER

### Overall Progress
- Setup: 0/2 (0%) ⏳
- Investigations: 0/10 (0%) ⏳
- **Total: 0/12 (0%)**

### Current Status
- ⏳ Task 2.1: Entry Point Analysis - NOT STARTED
- ⏳ Task 2.2: Tool Execution Flow - NOT STARTED
- ⏳ Task 2.3: Provider Integration - NOT STARTED
- ⏳ Task 2.4: Utils Dependency - NOT STARTED
- ⏳ Task 2.5: SimpleTool Connections - NOT STARTED
- ⏳ Task 2.6: WorkflowTool Connections - NOT STARTED
- ⏳ Task 2.7: Data Flow Mapping - NOT STARTED
- ⏳ Task 2.8: Critical Paths - NOT STARTED
- ⏳ Task 2.9: Integration Patterns - NOT STARTED
- ⏳ Task 2.10: Phase 2 Summary - NOT STARTED

### Time Estimates
- Task 2.1: ~30 minutes
- Task 2.2: ~45 minutes
- Task 2.3: ~30 minutes
- Task 2.4: ~60 minutes
- Task 2.5: ~45 minutes
- Task 2.6: ~45 minutes
- Task 2.7: ~60 minutes
- Task 2.8: ~30 minutes
- Task 2.9: ~30 minutes
- Task 2.10: ~60 minutes
- **Total: ~7 hours**

---

## 🎯 SUCCESS CRITERIA

### Phase 2 Complete When:
- [x] All entry points mapped with complete import chains ✅
- [x] Tool execution flow fully documented ✅
- [x] Provider integration fully mapped ✅
- [x] Utils dependencies completely traced ✅
- [x] SimpleTool connections mapped (critical for refactoring) ✅
- [x] WorkflowTool connections mapped ✅
- [x] Data flow completely documented ✅
- [x] Critical paths identified ✅
- [x] Integration patterns documented ✅
- [x] Comprehensive summary created with visual diagrams ✅
- [x] GLM-4.6 validation performed ✅
- [x] Validation corrections applied ✅

### Ready for Phase 2 Cleanup (Execute Findings) When:
- [x] Complete understanding of SimpleTool dependencies ✅
- [x] Public interface clearly identified (25 methods - CANNOT CHANGE) ✅
- [x] Impact radius fully mapped ✅
- [x] Integration patterns understood ✅
- [x] Refactoring constraints documented ✅
- [x] All Phase 2 deliverables created ✅

---

## 📝 NOTES

- Use existing Phase 0 DEPENDENCY_MAP.md as foundation
- Build on Phase 1 classification results
- Focus on ACTIVE components only (orphaned/planned already handled)
- Document ALL evidence (no assumptions)
- Create visual diagrams where helpful (Mermaid)
- Update task manager after EACH task
- Get user approval before proceeding to Phase 3

---

## ✅ PHASE 2 DELIVERABLES

**All deliverables created in:** `docs/ARCHAEOLOGICAL_DIG/phase2_connections/`

1. ✅ **ENTRY_POINTS_FLOW_MAP.md** (593 lines) - Complete entry point analysis
2. ✅ **TOOL_EXECUTION_FLOW.md** (750 lines) - Tool discovery and execution flow
3. ✅ **PROVIDER_INTEGRATION_MAP.md** - Provider selection and integration
4. ✅ **UTILS_DEPENDENCY_MAP.md** - Utils usage and dependencies
5. ✅ **SIMPLETOOL_CONNECTION_MAP.md** (373 lines) - SimpleTool connections (CRITICAL)
6. ✅ **WORKFLOWTOOL_CONNECTION_MAP.md** - WorkflowTool connections
7. ✅ **DATA_FLOW_MAP.md** - Complete data flow mapping
8. ✅ **CRITICAL_PATHS.md** - Critical paths and bottlenecks
9. ✅ **INTEGRATION_PATTERNS.md** - Integration pattern documentation
10. ✅ **PHASE2_COMPREHENSIVE_SUMMARY.md** (412 lines) - Complete summary with diagrams
11. ✅ **VALIDATION_CORRECTIONS.md** (185 lines) - GLM-4.6 validation results

**Total:** 11 comprehensive documents, ~7 hours of investigation

---

**STATUS: ✅ COMPLETE - Ready for Phase 2 Cleanup**

**Next:** Execute Phase 2 findings (see MASTER_CHECKLIST_PHASE2_CLEANUP.md)

Next: Task 2.1 - Entry Point Analysis

