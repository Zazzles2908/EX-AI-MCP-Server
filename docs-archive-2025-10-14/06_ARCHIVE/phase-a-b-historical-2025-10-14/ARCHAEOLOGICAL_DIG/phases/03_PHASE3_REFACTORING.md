# PHASE 3: REFACTORING & SIMPLIFICATION
**Branch:** archaeological-dig/phase3-refactor-and-simplify  
**Started:** TBD (After Phase 2 Cleanup complete)  
**Status:** ⏳ NOT STARTED - Awaiting Phase 2 Cleanup completion

---

## 🎯 PHASE GOAL

**Refactor and simplify the codebase to:**
1. Consolidate duplicate code
2. Simplify complex modules
3. Improve code organization
4. Reduce technical debt
5. Enhance maintainability
6. Prepare for production deployment

**Based on:** Phase 0, 1, 2 findings and Phase 2 Cleanup optimizations

---

## ✅ PREREQUISITES (MUST BE COMPLETE)

**Phase 0: Architectural Mapping** ✅ COMPLETE (95%)
- [x] Complete system inventory (433 Python files)
- [x] Shared infrastructure identification
- [x] Dependency mapping
- [x] Architecture pattern recognition
- [x] Modular refactoring strategy created
- [ ] User approval for refactoring strategy ⏳ PENDING

**Phase 1: Discovery & Classification** ✅ COMPLETE (93%)
- [x] All components classified (ACTIVE/ORPHANED/PLANNED)
- [x] Orphaned directories identified
- [x] Planned infrastructure documented
- [x] Utils folder audit complete
- [ ] Consolidation strategy document ⏳ PENDING

**Phase 2: Map Connections** ✅ COMPLETE (100%)
- [x] All 10 connection mapping tasks complete
- [x] Critical paths identified
- [x] Integration patterns documented
- [x] GLM-4.6 validation performed

**Phase 2 Cleanup: Execute Phase 2 Findings** ⏳ 75% COMPLETE
- [x] SimpleTool refactoring complete (conservative approach)
- [x] Performance optimizations complete (caching, parallel uploads, metrics)
- [x] Testing enhancements complete (46 tests)
- [x] Documentation improvements complete
- [x] Critical bugs fixed (token bloat resolved)
- [ ] Comprehensive system testing ⏳ BLOCKED (daemon stability)
- [ ] Expert validation & summary ❌ BLOCKED

**⚠️ BLOCKER:** Phase 3 cannot begin until Phase 2 Cleanup is 100% complete

---

## 📋 PHASE 3 PLANNED TASKS

**NOTE:** Phase 3 tasks are placeholders. Actual tasks will be defined based on:
- Phase 2 Cleanup completion findings
- User priorities and timeline
- Production deployment requirements

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

### Task 3.4: Fix File Embedding Limits in WorkflowTools ⚠️ HIGH PRIORITY

**Goal:** Implement proper file count/size limits for expert analysis file embedding

**Background:**
During Phase 2 Cleanup testing (Task 2.G.4), discovered that 4 WorkflowTools (Analyze, CodeReview, Refactor, SecAudit) hardcode file inclusion and can embed entire projects (1,742 files, 147KB), causing daemon crashes.

**Temporary Fix Applied (WRONG APPROACH):**
- Commented out hardcoded file inclusion in 4 tools for Phase 2 testing
- This was MY MISTAKE - should use .env variable instead

**Proper Fix Required:**
- [ ] Remove temporary comments from 4 tools
- [ ] Ensure tools respect `EXPERT_ANALYSIS_INCLUDE_FILES` env variable
- [ ] Implement file count limit (env: `EXPERT_ANALYSIS_MAX_FILES`)
- [ ] Implement total content limit (env: `EXPERT_ANALYSIS_MAX_CONTENT_KB`)
- [ ] Add smart file selection (relevance-based)
- [ ] Add logging when limits are hit
- [ ] Test with realistic scenarios
- [ ] Document file inclusion requirements per tool

**Files to Fix:**
1. `tools/workflows/analyze.py:323-327`
2. `tools/workflows/codereview.py:307-311`
3. `tools/workflows/refactor.py:313-317`
4. `tools/workflows/secaudit.py:456-460`

**Status:** ⏳ NOT STARTED (deferred from Phase 2)
**Priority:** 🔴 HIGH (affects production use of 4 tools)
**Estimated Effort:** 2-4 hours

---

### Task 3.5: Reduce Technical Debt (TBD)
**Goal:** Address technical debt backlog
**Status:** ⏳ NOT STARTED
**Prerequisites:** ✅ Phase 2 Cleanup complete

---

### Task 3.6: Enhance Maintainability (TBD)
**Goal:** Make codebase easier to maintain
**Status:** ⏳ NOT STARTED
**Prerequisites:** ✅ Phase 2 Cleanup complete

---

## 🎯 RECOMMENDED NEXT STEPS

Based on Phase 2 Cleanup findings, here are recommended priorities:

### Priority 1: Fix File Embedding (Task 3.4) 🔴 HIGH
**Why:** Blocks production use of 4 WorkflowTools
**Estimated Time:** 2-4 hours
**Impact:** Unblocks WorkflowTools testing and production use

### Priority 2: Consolidate Provider Logic 🟡 MEDIUM
**Why:** Reduce duplicate code between Kimi and GLM providers
**Estimated Time:** 3-5 days
**Impact:** Improved maintainability, reduced code duplication

### Priority 3: Simplify WebSocket Server 🟡 MEDIUM
**Why:** Break down ws_server.py (1200 lines) into smaller modules
**Estimated Time:** 5-7 days
**Impact:** Better code organization, easier maintenance

### Priority 4: Improve Error Handling Consistency 🟢 LOW
**Why:** Standardize error handling across tools and providers
**Estimated Time:** 3-4 days
**Impact:** Better debugging, consistent user experience

### Priority 5: Optimize Performance Bottlenecks 🟢 LOW
**Why:** Address performance issues identified in Phase 2
**Estimated Time:** 4-6 days
**Impact:** Faster response times, better resource usage

---

## 📊 PROGRESS TRACKER

**Total Tasks:** 6 (5 placeholder + 1 defined)
**Completed:** 0/6 (0%)
**In Progress:** 0/6
**Not Started:** 6/6

**Estimated Duration:** TBD (to be determined based on user priorities)

---

## ✅ SUCCESS CRITERIA

**Phase 3 Complete When:**
- [ ] All duplicate code consolidated
- [ ] Complex modules simplified
- [ ] Code well-organized
- [ ] Technical debt reduced
- [ ] Maintainability enhanced
- [ ] File embedding limits implemented (Task 3.4)
- [ ] All tests passing
- [ ] Documentation complete
- [ ] User approval obtained

---

## 🚨 BLOCKERS

**Cannot Start Phase 3 Until:**
1. ❌ Phase 2 Cleanup Task 2.G complete (comprehensive testing)
2. ❌ Phase 2 Cleanup Task 2.H complete (expert validation)
3. ❌ Daemon stability issues resolved
4. ❌ File inclusion strategy corrected

**Current Blockers:**
- Daemon crashes during WorkflowTools testing
- File inclusion temporary fix needs to be reverted
- Model capability documentation missing
- WorkflowTools functional testing incomplete (0/12)

---

## 📝 NOTES

**Phase 3 is ready to begin when:**
1. Phase 2 Cleanup is 100% complete
2. User reviews Phase 2 Cleanup completion summary
3. User defines specific Phase 3 priorities
4. User approves Phase 3 scope and timeline

**Current Status:**
- ⏳ Phase 2 Cleanup 75% complete (blocked)
- ✅ Phase 3 checklist created
- ⏳ Awaiting Phase 2 Cleanup completion
- ⏳ Awaiting user input for Phase 3 priorities

---

## 📚 REFERENCE DOCUMENTATION

**Phase 2 Findings:**
- `phase2_cleanup/WORKFLOWTOOLS_POST_REVIEW_FINDINGS_2025-10-12.md`
- `phase2_cleanup/MANDATORY_FIXES_CHECKLIST_2025-10-12.md`
- `phase2_connections/CRITICAL_PATHS.md`
- `phase2_connections/INTEGRATION_PATTERNS.md`

**Architecture Documentation:**
- `shared_infrastructure/MODULAR_REFACTORING_STRATEGY.md`
- `shared_infrastructure/ARCHITECTURE_PATTERN_ANALYSIS.md`
- `shared_infrastructure/DEPENDENCY_MAP.md`

---

**PHASE 3 STATUS:** ⏳ NOT STARTED - Blocked by Phase 2 Cleanup completion
**Next:** Complete Phase 2 Cleanup, then define Phase 3 priorities with user

