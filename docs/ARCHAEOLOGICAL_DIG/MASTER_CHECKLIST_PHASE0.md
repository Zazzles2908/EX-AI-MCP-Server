# ARCHAEOLOGICAL DIG - PHASE 0 MASTER CHECKLIST
**Branch:** archaeological-dig/phase1-discovery-and-cleanup  
**Started:** 2025-10-10 12:55 PM AEDT  
**Purpose:** Understand architecture BEFORE making any changes

---

## 🎯 PHASE 0 GOAL

**Map the entire architecture to understand:**
- What's SHARED vs SPECIFIC
- What's src/ vs tools/ vs utils/ separation
- What's duplicate vs unique
- What's the intended design vs historical accident
- **NEW: What's the SINGLE RESPONSIBILITY of each module?**
- **NEW: How to refactor for long-term stability?**

**WHY THIS IS CRITICAL:**
- Prevents fixing "shared" code without understanding impact
- Prevents tracking chaos (fixing same thing in multiple investigations)
- Ensures informed decisions about refactoring
- Maps dependencies before making changes
- **NEW: Enables principled refactoring based on Single Responsibility Principle**
- **NEW: Creates modular architecture for long-term maintainability**

---

## ✅ SETUP (COMPLETE)

- [x] Identified need for Phase 0 (user feedback)
- [x] Reverted premature fixes (expert_analysis.py, codereview.py)
- [x] Created Phase 0 checklist
- [x] Created shared infrastructure overlap analysis
- [x] Ready to begin systematic architecture mapping

---

## 📋 PHASE 0 INVESTIGATION TASKS

### Task 0.1: Layout Map - Complete System Inventory ✅ COMPLETE

**Goal:** Create complete inventory of ALL folders and files

- [x] Read existing SYSTEM_ARCHITECTURE.md
- [x] List ALL top-level directories (22 directories)
- [x] List ALL subdirectories (2 levels deep minimum)
- [x] Count files in each directory (1779 total, 433 Python)
- [x] Identify large files (>10KB) - 34 files found
- [x] Document folder purposes (from names/README files)
- [x] Create visual folder tree
- [x] Create layoutmap/COMPLETE_SYSTEM_INVENTORY.md
- [x] Mark task 0.1 complete

**Output:** ✅ Complete system inventory with folder counts and purposes

**Key Findings:**
- 22 top-level directories
- 433 Python files (excluding .venv)
- Largest file: tools/simple/base.py (55.3KB)
- utils/ has 37 files with ZERO folder structure (chaos!)
- Multiple duplicates detected (conf/ vs config/, conversation/ in 2 places, etc.)

---

### Task 0.2: Shared Infrastructure Identification ✅ COMPLETE

**Goal:** Identify ALL shared components (base classes, mixins, utilities)

**Shared Base Classes:**
- [x] Search for "class.*BaseTool" - find all base tool classes (3 found)
- [x] Search for "class.*Mixin" - find all mixins (13 found)
- [x] Search for "class.*Base" - find all base classes
- [x] List all files in tools/shared/ (9 files)
- [x] List all files in tools/workflow/ (9 files - base classes + mixins)
- [x] List all files in tools/simple/ (4 files + 5 mixins)
- [x] Classify each as: BASE_CLASS / MIXIN / IMPLEMENTATION

**Shared Utilities:**
- [x] List all files in utils/ (37 files)
- [x] List all files in src/utils/ (2 files)
- [x] List all files in src/server/utils/ (1 file)
- [x] Group by category (file_utils, conversation, token, etc.)
- [x] Identify top 10 most-imported utils (7-30 imports each)

**Shared Providers:**
- [x] List all files in src/providers/ (22 files)
- [x] List all files in src/server/providers/ (6 files)
- [x] List all files in tools/providers/ (9 files in glm/ and kimi/)
- [x] Understand separation: core vs server vs tool-specific

**Document findings:**
- [x] Create shared_infrastructure/SHARED_COMPONENTS_INVENTORY.md
- [x] Mark task 0.2 complete

**Output:** ✅ Complete inventory of shared components with classifications

**Key Findings:**
- 3 base classes: BaseTool (20+ tools), SimpleTool (4 tools), WorkflowTool (12 workflows)
- 13 mixins: 3 in tools/shared/, 5 in tools/simple/mixins/, 5 in tools/workflow/
- 10 highly-used utils: progress.py (30 imports), observability.py (21 imports), etc.
- 🚨 CRITICAL: expert_analysis.py (34.1KB) is shared mixin used by ALL workflows but in wrong location?

---

### Task 0.3: Dependency Mapping ✅ COMPLETE

**Goal:** Understand what depends on what (import graph)

**For Each Shared Component:**
- [x] Search for imports of tools/workflow/expert_analysis.py (via BaseWorkflowMixin)
- [x] Search for imports of tools/shared/base_tool.py (20+ tools)
- [x] Search for imports of tools/simple/base.py (4 tools)
- [x] Search for imports of tools/workflow/base.py (12 workflows)
- [x] Search for imports from utils/ (top 10 identified)
- [x] Search for imports from src/providers/ (mapped)
- [x] Create dependency graph (4-tier architecture)

**Document findings:**
- [x] Create shared_infrastructure/DEPENDENCY_MAP.md
- [x] List high-impact components (BaseTool: 30+ tools, progress.py: 30 files)
- [x] List low-impact components (SimpleTool: 4 tools)
- [x] Identify circular dependencies (NONE FOUND! ✅)
- [x] Mark task 0.3 complete

**Output:** ✅ Dependency map showing import relationships

**Key Findings:**
- ✅ NO circular dependencies!
- Clean 4-tier architecture: utils → tools/shared → tools/simple|workflow → implementations
- Impact radius: BaseTool (30+ tools), ExpertAnalysisMixin (12 workflows), progress.py (30 files)
- Cross-layer: src/ → tools/ (10 files, for registry/discovery - expected)

---

### Task 0.4: Duplicate Detection

**Goal:** Find duplicate functionality in multiple locations

**Known Duplicates to Investigate:**
- [ ] src/conf/ vs src/config/ - same purpose?
- [ ] src/conversation/ vs src/server/conversation/ - duplicate?
- [ ] src/providers/ vs src/server/providers/ - duplicate?
- [ ] utils/ vs src/utils/ vs src/server/utils/ - why three locations?
- [ ] tools/workflow/ vs tools/workflows/ - singular vs plural?
- [ ] streaming/ vs tools/streaming/ - duplicate?

**Search for Duplicates:**
- [ ] Search for duplicate file names across directories
- [ ] Search for similar functionality (file_utils_*.py - 7 files!)
- [ ] Search for similar class names
- [ ] Identify which is active vs orphaned

**Document findings:**
- [ ] Update src_structure/SRC_FOLDER_DUPLICATION_ANALYSIS.md
- [ ] Update tools/TOOLS_FOLDER_STRUCTURE_ANALYSIS.md
- [ ] Create shared_infrastructure/DUPLICATE_FUNCTIONALITY.md
- [ ] Mark task 0.4 complete

**Output:** List of all duplicates with recommendations

---

### Task 0.5: Architecture Pattern Recognition

**Goal:** Understand if there's an intended pattern or historical accident

**Investigate Patterns:**
- [ ] Read any existing architecture documentation
- [ ] Check for README files in key directories
- [ ] Look for comments explaining folder structure
- [ ] Check git history for major refactoring commits
- [ ] Identify if pattern is: layered / feature-based / hybrid / chaotic

**Hypotheses to Test:**
- [ ] Hypothesis A: Layered (src=core, tools=layer, utils=shared)
- [ ] Hypothesis B: Feature-based (src=system, tools=tools, utils=utilities)
- [ ] Hypothesis C: Historical accident (organic growth, no clear pattern)

**Document findings:**
- [ ] Create shared_infrastructure/ARCHITECTURE_PATTERN_ANALYSIS.md
- [ ] Document intended pattern (if found)
- [ ] Document actual pattern (what exists)
- [ ] Document gaps between intended and actual
- [ ] Mark task 0.5 complete

**Output:** Understanding of architecture pattern (or lack thereof)

---

### Task 0.6: Modular Refactoring Strategy (UPDATED FROM "Consolidation Strategy")

**Goal:** Create principled refactoring strategy based on Single Responsibility Principle

**USER'S VISION:**
- Each script should have ONE clear purpose
- Easy to find which script to modify
- Modular design: prompt builder → model caller → response formatter
- Long-term stability through proper separation of concerns
- Industry-standard clean architecture

**For Each Large File:**
- [ ] Document current responsibilities (what does it do?)
- [ ] Identify single responsibility (what SHOULD it do?)
- [ ] Identify misplaced responsibilities (what doesn't belong?)
- [ ] Propose module breakdown (how to split it?)
- [ ] Estimate impact and effort

**For Shared Infrastructure:**
- [ ] Recommend proper location for each component
- [ ] Propose modular folder structure
- [ ] Document design intent for each module
- [ ] Identify breaking changes
- [ ] Propose migration strategy

**For Utils Chaos:**
- [ ] Propose modular folder structure (file/, conversation/, model/, etc.)
- [ ] Group by single responsibility
- [ ] Document purpose of each module
- [ ] Plan import updates

**For Duplicates:**
- [ ] Determine which is active
- [ ] Determine which follows single responsibility better
- [ ] Recommend: KEEP / MERGE / DELETE / REFACTOR
- [ ] Estimate impact of consolidation

**Document findings:**
- [ ] Create MODULAR_REFACTORING_STRATEGY.md
- [ ] Document design intent for each module
- [ ] Break into phases (Phase 1: Refactoring, Phase 2: Testing, Phase 3: Documentation)
- [ ] Prioritize by impact and dependencies
- [ ] Create timeline estimate (7-12 weeks)
- [ ] Get user approval
- [ ] Mark task 0.6 complete

**Output:** Detailed modular refactoring strategy with design intent documentation

---

## 📊 PROGRESS TRACKER

### Overall Progress
- Setup: 5/5 (100%) ✅
- Investigations: 4/6 (67%) 🔄
- **Total: 9/11 (82%)**

### Time Estimates
- Task 0.1: Layout Map - ~30 minutes
- Task 0.2: Shared Infrastructure - ~45 minutes
- Task 0.3: Dependency Mapping - ~60 minutes
- Task 0.4: Duplicate Detection - ~45 minutes
- Task 0.5: Architecture Pattern - ~30 minutes
- Task 0.6: Consolidation Strategy - ~60 minutes
- **Total: ~4.5 hours**

---

## 🎯 SUCCESS CRITERIA

### Phase 0 Complete When:
- [ ] Complete system inventory created
- [ ] All shared components identified and classified
- [ ] Dependency map created
- [ ] All duplicates identified
- [ ] Architecture pattern understood
- [ ] **Modular refactoring strategy created (not just consolidation)**
- [ ] **Design intent documented for each module**
- [ ] **Single responsibility identified for each large file**
- [ ] **Timeline estimated (7-12 weeks for Phase 1)**
- [ ] User approval obtained
- [ ] Ready to begin Phase 1: Modular Refactoring with informed decisions

---

## 📝 INTEGRATION WITH PHASE 1

### Tasks Moving from Phase 1 to Phase 0:
- **Task 1.8: Tools Structure Investigation** → Part of Task 0.1, 0.2, 0.4
- **Task 1.9: Src Duplicates Investigation** → Part of Task 0.1, 0.4

### Tasks Remaining in Phase 1:
- Task 1.1: System Prompts ✅ (COMPLETE - no changes needed)
- Task 1.2: Timezone Utility (PAUSED - resume after Phase 0)
- Task 1.3: Model Routing
- Task 1.4: Utils Folder Audit (informed by Phase 0)
- Task 1.5: Monitoring Infrastructure
- Task 1.6: Security/RBAC
- Task 1.7: Streaming
- Task 1.10: Consolidation Strategy (informed by Phase 0)

---

## 🚨 CRITICAL LESSONS LEARNED

### What Went Wrong:
1. Started fixing bugs without understanding architecture
2. Fixed `expert_analysis.py` (shared infrastructure) during "timezone investigation"
3. Created tracking chaos - exactly what we're trying to prevent
4. Didn't understand src/ vs tools/ vs utils/ separation

### What We're Doing Right Now:
1. ✅ Pausing to understand architecture FIRST
2. ✅ Mapping shared vs specific FIRST
3. ✅ Creating proper categorization
4. ✅ Then making informed decisions

### User's Feedback Validated:
> "When I mention suggestions like this, then scripts start going in other places, which is difficult to track and not considered when other categories are tackled/assessed"

**User was 100% correct. Phase 0 prevents this.**

---

## 📚 DOCUMENTATION STRUCTURE

```
docs/ARCHAEOLOGICAL_DIG/
├── MASTER_CHECKLIST_PHASE0.md (this file)
├── MASTER_CHECKLIST_PHASE1.md (updated after Phase 0)
├── AUDIT_TRAIL_PHASE0.md (to be created)
├── README_ARCHAEOLOGICAL_DIG_STATUS.md (to be updated)
│
├── layoutmap/
│   └── SYSTEM_ARCHITECTURE.md (to be updated with complete inventory)
│
├── shared_infrastructure/
│   ├── SHARED_INFRASTRUCTURE_OVERLAP_ANALYSIS.md ✅
│   ├── SHARED_COMPONENTS_INVENTORY.md (Task 0.2)
│   ├── DEPENDENCY_MAP.md (Task 0.3)
│   ├── DUPLICATE_FUNCTIONALITY.md (Task 0.4)
│   ├── ARCHITECTURE_PATTERN_ANALYSIS.md (Task 0.5)
│   └── CONSOLIDATION_STRATEGY_PHASE0.md (Task 0.6)
│
├── src_structure/
│   └── SRC_FOLDER_DUPLICATION_ANALYSIS.md (to be updated)
│
└── tools/
    └── TOOLS_FOLDER_STRUCTURE_ANALYSIS.md (to be updated)
```

---

**STATUS: READY TO BEGIN TASK 0.1**

Next: Complete system inventory and layout mapping

