# ARCHAEOLOGICAL DIG - PHASE 3 MASTER CHECKLIST
**Branch:** archaeological-dig/phase3-refactor-and-simplify
**Started:** TBD (After Phase 2 Cleanup complete)
**Purpose:** Refactor & Simplify - Reduce complexity and improve maintainability
**Parent:** MASTER_CHECKLIST_PHASE2_CLEANUP.md (All tasks must be COMPLETE)

**NOTE:** SimpleTool refactoring was completed in Phase 2 Cleanup (Task 2.B). Phase 3 focuses on broader codebase simplification and maintainability improvements.

---

## 🎯 PHASE 3 GOAL

Refactor and simplify the codebase to:
1. Consolidate duplicate code
2. Simplify complex modules
3. Improve code organization
4. Reduce technical debt
5. Enhance maintainability
6. Prepare for production deployment

**Based on:** Phase 0, 1, 2 findings and Phase 2 Cleanup optimizations

---

## ✅ PREREQUISITES (MUST BE COMPLETE)

**Phase 0: Architectural Mapping** ✅ COMPLETE
- [x] Complete system inventory (433 Python files)
- [x] Shared infrastructure identification
- [x] Dependency mapping
- [x] Architecture pattern recognition
- [x] Modular refactoring strategy created

**Phase 1: Discovery & Classification** ✅ COMPLETE
- [x] All components classified (ACTIVE/ORPHANED/PLANNED)
- [x] Orphaned directories deleted (4 directories)
- [x] Planned infrastructure archived (3 systems)
- [x] Utils folder reorganized (37 files → 6 folders)
- [x] All changes committed and pushed

**Phase 2: Map Connections** ✅ COMPLETE
- [x] All 10 connection mapping tasks complete
- [x] Critical paths identified
- [x] Integration patterns documented
- [x] GLM-4.6 validation performed

**Phase 2 Cleanup: Execute Phase 2 Findings** ✅ COMPLETE
- [x] SimpleTool refactoring complete (Facade pattern)
- [x] Performance optimizations complete (caching, parallel uploads, metrics)
- [x] Testing enhancements complete (46 tests)
- [x] Documentation improvements complete
- [x] Critical bugs fixed
- [x] All changes committed

---

## 📋 PHASE 3 EXECUTION TASKS

**NOTE:** Phase 3 tasks are placeholders. The actual tasks will be defined based on findings from Phase 2 Cleanup and user priorities.

### Task 3.1: Code Consolidation (TBD)

**Goal:** Identify and consolidate duplicate code

**Status:** ⏳ NOT STARTED
**Prerequisites:** ✅ Phase 2 Cleanup complete

---

### Task 3.2: Simplify Complex Modules (TBD)

**Goal:** Break down overly complex modules

**Status:** ⏳ NOT STARTED
**Prerequisites:** ✅ Phase 2 Cleanup complete

---

### Task 3.3: Improve Code Organization (TBD)

**Goal:** Reorganize code for better structure

**Status:** ⏳ NOT STARTED
**Prerequisites:** ✅ Phase 2 Cleanup complete

---

### Task 3.4: Reduce Technical Debt (TBD)

**Goal:** Address technical debt backlog

**Status:** ⏳ NOT STARTED
**Prerequisites:** ✅ Phase 2 Cleanup complete

---

### Task 3.5: Enhance Maintainability (TBD)

**Goal:** Make codebase easier to maintain

**Status:** ⏳ NOT STARTED
**Prerequisites:** ✅ Phase 2 Cleanup complete

---

## 📊 PROGRESS TRACKER

**Total Tasks:** 5 (placeholder)
**Completed:** 0/5 (0%)
**In Progress:** 0/5
**Not Started:** 5/5

**Estimated Duration:** TBD (to be determined based on user priorities)

---

## 🎯 SUCCESS CRITERIA

- [ ] All duplicate code consolidated
- [ ] Complex modules simplified
- [ ] Code well-organized
- [ ] Technical debt reduced
- [ ] Maintainability enhanced
- [ ] All tests passing
- [ ] Documentation complete

---

## 📝 NOTES

**Phase 3 is ready to begin when:**
1. User reviews Phase 2 Cleanup completion summary
2. User defines specific Phase 3 priorities
3. User approves Phase 3 scope and timeline

**Current Status:**
- ✅ Phase 2 Cleanup complete
- ✅ Phase 3 checklist created
- ⏳ Awaiting user input for Phase 3 priorities

---

**STATUS:** ⏳ READY TO BEGIN (awaiting user priorities)
**Prerequisites:** ✅ ALL COMPLETE
**Next:** User defines Phase 3 scope and priorities

- [ ] Extract schema generation methods:
  - [ ] get_input_schema()
  - [ ] get_tool_fields() (abstract)
  - [ ] get_required_fields() (abstract)
  - [ ] get_annotations()
  - [ ] get_model_field_schema()
- [ ] Update SimpleTool base.py to delegate to definition module
- [ ] Run integration tests (must pass)
- [ ] Commit changes

**Deliverable:**
- [ ] tools/simple/definition/schema.py (~150-200 lines)
- [ ] SimpleTool base.py delegates to definition module
- [ ] All integration tests passing
- [ ] Changes committed

**Time Estimate:** 2-3 days

---

### Task 3.3: Extract Intake Module (3-4 days)

**Goal:** Extract request accessor and validation logic into intake/ module

**Tasks:**
- [ ] Create tools/simple/intake/ directory
- [ ] Create tools/simple/intake/__init__.py
- [ ] Create tools/simple/intake/accessor.py
- [ ] Extract 13 request accessor methods
- [ ] Create tools/simple/intake/validator.py
- [ ] Extract validation logic (temperature, files, etc.)
- [ ] Update SimpleTool base.py to delegate to intake module
- [ ] Run integration tests (must pass)
- [ ] Commit changes

**Deliverable:**
- [ ] tools/simple/intake/accessor.py (~200-250 lines)
- [ ] tools/simple/intake/validator.py (~150-200 lines)
- [ ] SimpleTool base.py delegates to intake module
- [ ] All integration tests passing
- [ ] Changes committed

**Time Estimate:** 3-4 days

---

### Task 3.4: Extract Preparation Module (3-4 days)

**Goal:** Extract prompt building logic into preparation/ module

**Tasks:**
- [ ] Create tools/simple/preparation/ directory
- [ ] Create tools/simple/preparation/__init__.py
- [ ] Create tools/simple/preparation/prompt.py
- [ ] Extract prompt building methods:
  - [ ] build_standard_prompt()
  - [ ] prepare_chat_style_prompt()
- [ ] Create tools/simple/preparation/files.py
- [ ] Extract prompt file handling:
  - [ ] handle_prompt_file_with_fallback()
- [ ] Update SimpleTool base.py to delegate to preparation module
- [ ] Run integration tests (must pass)
- [ ] Commit changes

**Deliverable:**
- [ ] tools/simple/preparation/prompt.py (~200-250 lines)
- [ ] tools/simple/preparation/files.py (~80-100 lines)
- [ ] SimpleTool base.py delegates to preparation module
- [ ] All integration tests passing
- [ ] Changes committed

**Time Estimate:** 3-4 days

---

### Task 3.5: Extract Execution Module (2-3 days)

**Goal:** Extract model calling logic into execution/ module

**Tasks:**
- [ ] Create tools/simple/execution/ directory
- [ ] Create tools/simple/execution/__init__.py
- [ ] Create tools/simple/execution/caller.py
- [ ] Extract execution logic:
  - [ ] execute() method
  - [ ] Model invocation logic
  - [ ] Error handling
- [ ] Update SimpleTool base.py to delegate to execution module
- [ ] Run integration tests (must pass)
- [ ] Commit changes

**Deliverable:**
- [ ] tools/simple/execution/caller.py (~200-250 lines)
- [ ] SimpleTool base.py delegates to execution module
- [ ] All integration tests passing
- [ ] Changes committed

**Time Estimate:** 2-3 days

---

### Task 3.6: Extract Response Module (2-3 days)

**Goal:** Extract response formatting logic into response/ module

**Tasks:**
- [ ] Create tools/simple/response/ directory
- [ ] Create tools/simple/response/__init__.py
- [ ] Create tools/simple/response/formatter.py
- [ ] Extract response formatting methods:
  - [ ] format_response()
  - [ ] get_actually_processed_files()
  - [ ] Response parsing logic
- [ ] Update SimpleTool base.py to delegate to response module
- [ ] Run integration tests (must pass)
- [ ] Commit changes

**Deliverable:**
- [ ] tools/simple/response/formatter.py (~150-200 lines)
- [ ] SimpleTool base.py delegates to response module
- [ ] All integration tests passing
- [ ] Changes committed

**Time Estimate:** 2-3 days

---

### Task 3.7: Finalize Facade Pattern (2-3 days)

**Goal:** Ensure SimpleTool base.py is clean facade maintaining all public methods

**Tasks:**
- [ ] Review SimpleTool base.py
- [ ] Verify all 25 public methods present with exact signatures
- [ ] Verify all methods delegate to appropriate modules
- [ ] Verify inheritance chain unchanged
- [ ] Verify class constants preserved (FILES_FIELD, IMAGES_FIELD)
- [ ] Target: base.py ~150-200 lines (down from 1,220)
- [ ] Add comprehensive docstrings
- [ ] Run integration tests (must pass)
- [ ] Commit changes

**Deliverable:**
- [ ] SimpleTool base.py is clean facade (~150-200 lines)
- [ ] All 25 public methods preserved
- [ ] 100% backward compatibility verified
- [ ] All integration tests passing
- [ ] Changes committed

**Time Estimate:** 2-3 days

---

### Task 3.8: Integration Testing & Validation (2-3 days)

**Goal:** Comprehensive testing to verify no breaking changes

**Tasks:**
- [ ] Run full integration test suite
- [ ] Test ChatTool thoroughly
  - [ ] All 25 public methods
  - [ ] Chat-specific features
  - [ ] Conversation continuation
  - [ ] File handling
  - [ ] Web search integration
- [ ] Test ChallengeTool thoroughly
  - [ ] All 25 public methods
  - [ ] Challenge-specific features
- [ ] Test ActivityTool thoroughly
  - [ ] All 25 public methods
  - [ ] Activity-specific features
- [ ] Performance testing
  - [ ] Compare before/after performance
  - [ ] Ensure no regressions
- [ ] Manual testing of all tools
- [ ] Document any issues found
- [ ] Fix any issues
- [ ] Re-run tests until all pass

**Deliverable:**
- [ ] All integration tests passing
- [ ] Performance metrics documented
- [ ] No breaking changes confirmed
- [ ] All 3 SimpleTool subclasses working correctly
- [ ] Test results documented

**Time Estimate:** 2-3 days

---

### Task 3.9: Documentation & Cleanup (2-3 days)

**Goal:** Update all documentation and clean up

**Tasks:**
- [ ] Create design intent documents for each module:
  - [ ] tools/simple/definition/DESIGN_INTENT.md
  - [ ] tools/simple/intake/DESIGN_INTENT.md
  - [ ] tools/simple/preparation/DESIGN_INTENT.md
  - [ ] tools/simple/execution/DESIGN_INTENT.md
  - [ ] tools/simple/response/DESIGN_INTENT.md
- [ ] Update SimpleTool base.py docstring
- [ ] Update architecture documentation
- [ ] Create visual diagrams (Mermaid)
  - [ ] New SimpleTool module structure
  - [ ] Facade pattern implementation
  - [ ] Module dependencies
- [ ] Update SIMPLETOOL_CONNECTION_MAP.md
- [ ] Clean up any temporary files
- [ ] Update README files
- [ ] Commit documentation

**Deliverable:**
- [ ] Design intent documents for all 5 modules
- [ ] Updated architecture documentation
- [ ] Visual diagrams created
- [ ] All documentation committed

**Time Estimate:** 2-3 days

---

### Task 3.10: Expert Validation & Summary (1-2 days)

**Goal:** Get expert validation and create comprehensive summary

**Tasks:**
- [ ] Use EXAI codereview tool to validate refactoring
- [ ] Use EXAI analyze tool for architectural assessment
- [ ] Address any issues found by expert analysis
- [ ] Create PHASE3_COMPREHENSIVE_SUMMARY.md
  - [ ] Document refactoring approach
  - [ ] Document module structure
  - [ ] Document lessons learned
  - [ ] Include metrics (before/after)
  - [ ] Include visual diagrams
- [ ] Get user approval
- [ ] Prepare for merge to main

**Deliverable:**
- [ ] Expert validation complete
- [ ] PHASE3_COMPREHENSIVE_SUMMARY.md created
- [ ] User approval obtained
- [ ] Ready for merge

**Time Estimate:** 1-2 days

---

## 📊 PROGRESS TRACKER

### Overall Progress
- Setup: 0/1 (0%) ⏳
- Refactoring: 0/9 (0%) ⏳
- **Total: 0/10 (0%)**

### Current Status
- ⏳ Task 3.0: Setup & Planning - NOT STARTED
- ⏳ Task 3.1: Pre-Refactoring Validation - NOT STARTED
- ⏳ Task 3.2: Extract Definition Module - NOT STARTED
- ⏳ Task 3.3: Extract Intake Module - NOT STARTED
- ⏳ Task 3.4: Extract Preparation Module - NOT STARTED
- ⏳ Task 3.5: Extract Execution Module - NOT STARTED
- ⏳ Task 3.6: Extract Response Module - NOT STARTED
- ⏳ Task 3.7: Finalize Facade Pattern - NOT STARTED
- ⏳ Task 3.8: Integration Testing - NOT STARTED
- ⏳ Task 3.9: Documentation & Cleanup - NOT STARTED
- ⏳ Task 3.10: Expert Validation - NOT STARTED

### Time Estimates
- Task 3.0: ~1 day
- Task 3.1: ~2-3 days
- Task 3.2: ~2-3 days
- Task 3.3: ~3-4 days
- Task 3.4: ~3-4 days
- Task 3.5: ~2-3 days
- Task 3.6: ~2-3 days
- Task 3.7: ~2-3 days
- Task 3.8: ~2-3 days
- Task 3.9: ~2-3 days
- Task 3.10: ~1-2 days
- **Total: ~23-32 days (4-6 weeks)**

---

## 🎯 SUCCESS CRITERIA

### Phase 3 Complete When:
- [ ] SimpleTool base.py reduced from 1,220 lines to ~150-200 lines
- [ ] 5 conceptual modules created (definition, intake, preparation, execution, response)
- [ ] All 25 public methods preserved with exact signatures
- [ ] All 3 SimpleTool subclasses working correctly
- [ ] 100% backward compatibility verified
- [ ] All integration tests passing
- [ ] No performance regressions
- [ ] Comprehensive documentation created
- [ ] Expert validation complete
- [ ] User approval obtained

### Ready for Merge When:
- [ ] All tasks complete
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Expert validation positive
- [ ] User approves changes
- [ ] No breaking changes confirmed

---

## 🎨 TARGET ARCHITECTURE

### Current State (Monolithic)
```
tools/simple/
├── base.py (55.3KB, 1,220 lines - DOES EVERYTHING!)
└── mixins/ (already modular)
```

### Target State (Modular - Top-Down Design)
```
tools/simple/
├── base.py (FACADE - ~150-200 lines)
│   class SimpleTool:
│       """Facade that delegates to conceptual modules"""
│       # All 25 public methods preserved
│       # Each method delegates to appropriate module
│
├── definition/          ← "What does this tool promise?"
│   ├── __init__.py
│   └── schema.py (~150-200 lines)
│       - get_input_schema()
│       - get_tool_fields()
│       - get_required_fields()
│       - get_annotations()
│
├── intake/              ← "What did the user ask for?"
│   ├── __init__.py
│   ├── accessor.py (~200-250 lines)
│   │   - 13 request accessor methods
│   └── validator.py (~150-200 lines)
│       - get_validated_temperature()
│       - Validation logic
│
├── preparation/         ← "How do we ask the AI?"
│   ├── __init__.py
│   ├── prompt.py (~200-250 lines)
│   │   - build_standard_prompt()
│   │   - prepare_chat_style_prompt()
│   └── files.py (~80-100 lines)
│       - handle_prompt_file_with_fallback()
│
├── execution/           ← "How do we call the AI?"
│   ├── __init__.py
│   └── caller.py (~200-250 lines)
│       - execute()
│       - Model invocation
│
├── response/            ← "How do we deliver the result?"
│   ├── __init__.py
│   └── formatter.py (~150-200 lines)
│       - format_response()
│       - get_actually_processed_files()
│
└── mixins/ (existing - keep as-is)
    ├── continuation_mixin.py
    ├── streaming_mixin.py
    ├── tool_call_mixin.py
    └── web_search_mixin.py
```

---

## 📝 NOTES

- Use Facade Pattern: base.py keeps all public methods, delegates to modules
- Incremental approach: Extract one module at a time
- Test after EACH module extraction
- Commit frequently (after each successful module extraction)
- 100% backward compatibility is NON-NEGOTIABLE
- All 25 public methods must maintain exact signatures
- Integration tests are CRITICAL - create before refactoring
- Follow Top-Down Design principles (conceptual categories)
- Each module has single responsibility
- Target: 150-250 lines per module

---

## 🚨 RISK MITIGATION

### Risk 1: Breaking Changes
**Mitigation:**
- Create comprehensive integration tests BEFORE refactoring
- Test after each module extraction
- Maintain exact method signatures
- Use facade pattern to preserve public interface

### Risk 2: Import Complexity
**Mitigation:**
- Use lazy imports in facade methods
- Clear module boundaries
- Document import patterns

### Risk 3: Performance Regression
**Mitigation:**
- Benchmark before refactoring
- Test performance after each module
- Optimize if needed

### Risk 4: Scope Creep
**Mitigation:**
- Stick to the plan
- No new features during refactoring
- Focus on structure, not functionality

---

**STATUS: READY TO BEGIN**

Next: Task 3.0 - Setup & Planning

