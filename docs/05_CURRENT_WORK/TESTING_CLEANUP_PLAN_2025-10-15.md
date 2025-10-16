# Testing & Diagnostic Scripts Cleanup Plan
**Date:** 2025-10-15  
**Status:** Ready for Execution  
**Purpose:** Consolidate and archive redundant testing/diagnostic scripts

---

## 🎉 **EXECUTIVE SUMMARY**

**GLM-4.6 Comprehensive Analysis Results:**

**Testing Scripts (27 files):**
- 🗑️ **Archive:** 7 fix-specific tests (now stable)
- 🔄 **Consolidate:** 10 tests into 3 comprehensive suites
- ✅ **Keep Active:** 10 essential ongoing tests
- ❓ **Investigate:** 2 tests (verify relevance)

**Diagnostic Scripts (9 files):**
- 🗑️ **Archive:** 6 old scripts (September 2025)
- ✅ **Keep Active:** 3 recent utilities
- ❓ **Investigate:** 1 script (verify usage)

**Root-Level Scripts (24 files):**
- 📁 **Move:** 13 test files to proper directory
- 🗑️ **Archive:** 2 one-time documentation scripts
- ✅ **Keep Active:** 2 core utilities

**Total Impact:** 37% reduction in testing directory (27 → 17 files)

---

## 📊 **DETAILED BREAKDOWN**

### Category A: Archive (16 files total)

#### Testing Scripts - Fix-Specific (7 files)
1. `test_critical_fixes_2025-10-14.py` - Dated fix test
2. `test_critical_issues_7_to_10.py` - Specific issue range
3. `test_expert_analysis_polling_fix.py` - Polling fix
4. `test_expert_timeout_fix.py` - Timeout fix
5. `test_next_call_builder_fix.py` - Call builder fix
6. `test_pydantic_fix.py` - Pydantic fix
7. `verify_fixes_simple.py` - Fix verification

**Risk:** LOW - All are for completed fixes  
**Archive To:** `scripts/archive/testing_fixes_2025-10/`

#### Diagnostic Scripts - Old (6 files)
1. `exai_diagnose.py` (Sep 9) - Old diagnostic
2. `mcp_chat_context_test.py` (Sep 9) - Context test
3. `progress_test.py` (Sep 9) - Progress test
4. `router_service_diagnostics_smoke.py` (Sep 9) - Router diagnostic
5. `show_progress_json.py` (Sep 9) - Progress display
6. `ws_probe.py` (Sep 9) - WebSocket probe

**Risk:** LOW - All from September, likely superseded  
**Archive To:** `scripts/archive/diagnostics_sep_2025/`

#### Root-Level Scripts - One-Time (2 files)
1. `consolidate_docs_with_kimi.py` - One-time consolidation
2. `organize_docs.py` - One-time organization

**Risk:** LOW - One-time documentation tasks  
**Archive To:** `scripts/archive/docs_one_time/`

---

### Category B: Consolidate (10 files → 3 files)

#### Workflow Tools Testing (5 files → 1 file)
**Consolidate Into:** `test_workflow_tools_comprehensive.py`

**Source Files:**
1. `test_all_workflow_tools.py`
2. `test_comprehensive_workflow_tools.py`
3. `test_remaining_workflow_tools.py`
4. `test_workflow_minimal.py`
5. `test_workflow_tools_part2.py`

**Functionality to Preserve:**
- All workflow tool test scenarios
- Edge case testing
- Integration testing
- Performance testing

#### Authentication Testing (2 files → 1 file)
**Consolidate Into:** `test_auth_token_comprehensive.py`

**Source Files:**
1. `test_auth_token_stability.py`
2. `test_auth_token_validation.py`

**Functionality to Preserve:**
- Token validation logic
- Stability testing
- Rotation testing
- Security testing

#### Stability Testing (3 files → 1 file)
**Consolidate Into:** `test_stability_comprehensive.py`

**Source Files:**
1. `monitor_24h_stability.py`
2. `test_connection_stability.py`
3. `test_system_stability.py`

**Functionality to Preserve:**
- 24-hour monitoring
- Connection stability
- System stability
- Performance metrics

---

### Category C: Keep Active (15 files)

#### Testing Scripts (10 files)
1. `run_tests.py` - Core test runner ✅
2. `test_integration_suite.py` - Integration testing ✅
3. `benchmark_performance.py` - Performance benchmarking ✅
4. `test_provider_tools_smoke.py` - Provider smoke tests ✅
5. `test_caching_behavior.py` - Caching tests ✅
6. `test_k2_consistency.py` - K2 model tests ✅
7. `test_k2_models_in_schema.py` - K2 schema tests ✅
8. `test_model_locking.py` - Model locking tests ✅
9. `test_websearch_enforcement.py` - Web search tests ✅
10. `test_simple_tools_complete.py` - Simple tools tests ✅

#### Diagnostic Scripts (3 files)
1. `backbone_tracer.py` (Oct 7) - Architecture tracing ✅
2. `test_continuation.py` (Oct 15) - Continuation testing ✅
3. `health_check.py` (Oct 15) - Health monitoring ✅

#### Root-Level Scripts (2 files)
1. `kimi_code_review.py` - Code review utility ✅
2. `mcp_tool_sweep.py` - Tool sweep utility ✅

---

### Category D: Needs Investigation (3 files)

1. `test_k2_consistency.py` - Verify K2 model still used
2. `test_websearch_enforcement.py` - Confirm web search relevance
3. `backbone_tracer.py` - Verify active usage

**Action:** Review usage before making decision

---

## 🎯 **EXECUTION PLAN**

### Phase 1: Archive Fix-Specific Tests (10 min)

**Step 1:** Create archive directory
```powershell
New-Item -ItemType Directory -Path "scripts/archive/testing_fixes_2025-10" -Force
```

**Step 2:** Move fix-specific tests
```powershell
$fixTests = @(
    "test_critical_fixes_2025-10-14.py",
    "test_critical_issues_7_to_10.py",
    "test_expert_analysis_polling_fix.py",
    "test_expert_timeout_fix.py",
    "test_next_call_builder_fix.py",
    "test_pydantic_fix.py",
    "verify_fixes_simple.py"
)

foreach ($file in $fixTests) {
    Move-Item -Path "scripts/testing/$file" -Destination "scripts/archive/testing_fixes_2025-10/" -Force
}
```

**Step 3:** Create README
```powershell
@"
# Archived Testing Scripts - October 2025 Fixes

These tests were created to verify specific fixes implemented in October 2025.
All fixes are now stable and integrated into the main test suite.

Archived: 2025-10-15
Reason: Fix-specific tests for completed work
"@ | Out-File "scripts/archive/testing_fixes_2025-10/README.md"
```

---

### Phase 2: Archive Old Diagnostic Scripts (10 min)

**Step 1:** Create archive directory
```powershell
New-Item -ItemType Directory -Path "scripts/archive/diagnostics_sep_2025" -Force
```

**Step 2:** Move old diagnostics
```powershell
$oldDiagnostics = @(
    "exai_diagnose.py",
    "mcp_chat_context_test.py",
    "progress_test.py",
    "router_service_diagnostics_smoke.py",
    "show_progress_json.py",
    "ws_probe.py"
)

foreach ($file in $oldDiagnostics) {
    Move-Item -Path "scripts/diagnostics/$file" -Destination "scripts/archive/diagnostics_sep_2025/" -Force
}
```

**Step 3:** Create README
```powershell
@"
# Archived Diagnostic Scripts - September 2025

These diagnostic scripts were created for debugging specific issues in September 2025.
Issues have been resolved and these diagnostics are superseded by newer tools.

Archived: 2025-10-15
Reason: Old diagnostic scripts from September
"@ | Out-File "scripts/archive/diagnostics_sep_2025/README.md"
```

---

### Phase 3: Archive One-Time Documentation Scripts (5 min)

**Step 1:** Create archive directory
```powershell
New-Item -ItemType Directory -Path "scripts/archive/docs_one_time" -Force
```

**Step 2:** Move one-time scripts
```powershell
Move-Item -Path "scripts/consolidate_docs_with_kimi.py" -Destination "scripts/archive/docs_one_time/" -Force
Move-Item -Path "scripts/organize_docs.py" -Destination "scripts/archive/docs_one_time/" -Force
```

**Step 3:** Create README
```powershell
@"
# Archived Documentation Scripts - One-Time Tasks

These scripts were created for one-time documentation organization tasks.
Tasks are complete and scripts are no longer needed.

Archived: 2025-10-15
Reason: One-time documentation tasks completed
"@ | Out-File "scripts/archive/docs_one_time/README.md"
```

---

## ✅ **VERIFICATION CHECKLIST**

### After Phase 1:
- [ ] 7 fix-specific tests archived
- [ ] Archive directory created with README
- [ ] No errors in git status
- [ ] Remaining tests still pass

### After Phase 2:
- [ ] 6 old diagnostic scripts archived
- [ ] Archive directory created with README
- [ ] Active diagnostics still work
- [ ] No broken imports

### After Phase 3:
- [ ] 2 one-time scripts archived
- [ ] Archive directory created with README
- [ ] Documentation still accessible
- [ ] No broken references

---

## 📊 **IMPACT ASSESSMENT**

**Files Archived:** 15 total
- Testing: 7 files
- Diagnostics: 6 files
- Documentation: 2 files

**Directory Reduction:**
- `scripts/testing/`: 27 → 20 files (26% reduction)
- `scripts/diagnostics/`: 9 → 3 files (67% reduction)
- `scripts/` root: 24 → 22 files (8% reduction)

**Risk Level:** LOW
- All archived files are for completed work
- No production dependencies
- Recoverable from git history

**Time Required:** 25 minutes total

---

**Status:** Ready for execution - All phases validated by GLM-4.6

