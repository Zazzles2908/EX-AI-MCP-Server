# DISCREPANCIES TRACKER - ARCHAEOLOGICAL DIG REORGANIZATION
**Date Started:** 2025-10-12 11:05 AM AEDT
**Purpose:** Track all discrepancies, contradictions, and issues found during markdown reorganization
**Method:** Reading each file in full, fact-checking claims, validating completion status

---

## DISCREPANCY LOG

### Entry #1: Phase 2 Discovery Completion Claims
**File:** `MASTER_CHECKLIST_PHASE2.md`
**Claim:** "✅ COMPLETE - All 10 tasks finished, validated by GLM-4.6"
**Reality:** EXAI analysis suggests Tasks 2.2-2.10 may not have been executed
**Evidence:** 
- Task 2.1 has actual documentation (ENTRY_POINTS_FLOW_MAP.md)
- Tasks 2.2-2.10 marked complete but documentation unclear
**Severity:** 🔴 CRITICAL - Affects foundation for Phase 3
**Action Required:** Verify if discovery work was actually done

---

### Entry #2: File Inclusion Temporary Fix
**File:** Multiple WorkflowTool scripts
**Claim:** "Temporary fix for Phase 2 testing - file inclusion disabled"
**Reality:** File inclusion is ALREADY controlled by .env variable
**Evidence:**
- `.env` line 34: `EXPERT_ANALYSIS_INCLUDE_FILES=false`
- `.env` line 39: `EXPERT_ANALYSIS_MAX_FILE_SIZE_KB=10`
**Severity:** 🟡 MEDIUM - My mistake, needs correction
**Action Required:** Remove commented code from 4 tools, ensure .env variable is respected
**Files Affected:**
- `tools/workflows/analyze.py` (lines 323-327)
- `tools/workflows/codereview.py` (lines 307-311)
- `tools/workflows/refactor.py` (lines 313-317)
- `tools/workflows/secaudit.py` (lines 456-460)

---

### Entry #3: Model Capability Matrix Accuracy
**File:** `MANDATORY_FIXES_CHECKLIST_2025-10-12.md`
**Claim:** Model capability matrix showing file upload/web search support
**Reality:** Matrix may be inaccurate - needs verification
**Evidence:** User stated "the table compatibility matrix you generated appears not correct"
**Severity:** 🟡 MEDIUM - Affects EXAI usage decisions
**Action Required:** Verify actual model capabilities with documentation/testing

---

### Entry #4: Phase 0 Contradictory Status
**File:** `MASTER_CHECKLIST_PHASE0.md`
**Claim:** Line 249: "Total: 11/11 (100%) 🎉"
**Reality:** Multiple contradictions in same file:
- Line 235: "Get user approval - ⏳ PENDING"
- Line 364: "STATUS: READY TO BEGIN TASK 0.1"
- Line 274: Success criteria shows unchecked boxes
**Evidence:** File contains three different status claims
**Severity:** 🟡 MEDIUM - Confusing but work appears done
**Action Required:** Clarify actual status - appears 95% complete (awaiting user approval)

---

### Entry #5: Phase 1 Contradictory Status
**File:** `MASTER_CHECKLIST_PHASE1.md`
**Claim:** Line 299: "Total: 13/14 (93%)"
**Reality:** Line 350: "STATUS: READY TO BEGIN TASK 1.1"
**Evidence:** File shows completion but footer says ready to begin
**Severity:** 🟢 LOW - Work is actually done, just footer not updated
**Action Required:** None - consolidation clarifies actual status

---

### Entry #6: Phase 2 Cleanup Completion Claims vs Reality
**File:** `MASTER_CHECKLIST_PHASE2_CLEANUP.md`
**Claim:** "Phase 2 Cleanup: 8/8 tasks complete (100%)"
**Reality:** Only 6/8 tasks actually complete (75%)
**Evidence:**
- Task 2.G: Only 50% complete (WorkflowTools testing blocked by daemon crashes)
- Task 2.H: Not started (blocked by Task 2.G)
**Severity:** 🔴 CRITICAL - Premature completion claim
**Action Required:** Clarify actual completion status, fix blocking issues

---

### Entry #7: SimpleTool Refactoring Scope Mismatch
**File:** `MASTER_CHECKLIST_PHASE2_CLEANUP.md`
**Claim:** Task 2.B "✅ COMPLETE" with "SimpleTool refactored using Facade Pattern"
**Reality:** Only partial extraction - 2 modules extracted, core orchestration kept in SimpleTool
**Evidence:**
- Original goal: "150-200 line facade" and "5 modular files"
- Actual: Only extracted stateless utilities, kept orchestration in SimpleTool
- This is NOT a full Facade Pattern implementation
**Severity:** 🟡 MEDIUM - Partial implementation claimed as complete
**Action Required:** Clarify scope - was this intentional conservative approach?

---

### Entry #8: WorkflowTool Testing Presented as "In Progress" When Actually Blocked
**File:** `MASTER_CHECKLIST_PHASE2_CLEANUP.md`
**Claim:** Task 2.G.4 "⏳ IN PROGRESS" with "Code review 7/12 complete (58%)"
**Reality:** Task is BLOCKED by production-level daemon instability
**Evidence:**
- Daemon crashes when testing 3/12 WorkflowTools
- File inclusion issues causing 1,742 files to be embedded
- This is a production-blocking issue, not routine progress
**Severity:** 🔴 CRITICAL - Blocker not escalated properly
**Action Required:** Fix daemon stability before claiming progress

---

### Entry #9: Performance Optimization Claims vs Implementation
**File:** `MASTER_CHECKLIST_PHASE2_CLEANUP.md`
**Claim:** Task 2.C "✅ COMPLETE" with comprehensive performance optimizations
**Reality:** Key refactoring deferred, no benchmarks provided
**Evidence:**
- Parallel upload refactoring "deferred" (low priority maintainability)
- No evidence of actual performance benchmarks before/after
- 99.94% token reduction was a bug fix, not optimization
**Severity:** 🟡 MEDIUM - Incomplete optimization claimed as complete
**Action Required:** Clarify what "complete" means for performance work

---

### Entry #10: Documentation Validation Gap
**File:** `MASTER_CHECKLIST_PHASE2_CLEANUP.md`
**Claim:** All documentation complete and accurate
**Reality:** Multiple validation corrections needed AFTER claimed completion
**Evidence:**
- Provider comparison table had "3 major errors"
- Environment variable audit revealed features not "properly enabled"
- Validation corrections needed as separate task
**Severity:** 🟡 MEDIUM - Documentation quality issues
**Action Required:** Implement validation before completion claims

---

### Entry #11: CRITICAL PATTERN - Premature Completion Claims
**File:** Multiple Phase 2 documents
**Claim:** Tasks marked complete before validation
**Reality:** Systematic pattern of claiming completion before validation
**Evidence:**
1. Phase 2 Discovery claimed complete but needed validation corrections
2. SimpleTool Refactoring claimed complete but only partially implemented
3. Performance Optimizations claimed complete but deferred key work
4. WorkflowTool Testing claimed "in progress" while production-blocked
**Severity:** 🔴 CRITICAL - Systemic process issue
**Action Required:** Restructure validation process - require independent validation before completion

---

### Entry #12: [Template for new entries]
**File:**
**Claim:**
**Reality:**
**Evidence:**
**Severity:** 🔴 CRITICAL / 🟡 MEDIUM / 🟢 LOW
**Action Required:**

---

## SUMMARY STATISTICS

**Total Discrepancies Found:** 11
- 🔴 Critical: 4
- 🟡 Medium: 6
- 🟢 Low: 1

**Critical Pattern Identified:** Systematic premature completion claims across Phase 2

**Categories:**
- Completion Status Claims: 1
- Technical Implementation: 1
- Documentation Accuracy: 1

---

## NOTES

This document will be updated continuously during the reorganization process. Each markdown file will be read in full and fact-checked before being moved to its new location.

**Reorganization Progress:** 0% (just started)

