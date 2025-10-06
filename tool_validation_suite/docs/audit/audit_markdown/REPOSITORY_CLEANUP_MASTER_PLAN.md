# REPOSITORY CLEANUP MASTER PLAN
## Professional GitHub Repository Management

**Date:** 2025-10-07  
**Repository:** Zazzles2908/EX-AI-MCP-Server  
**Objective:** Clean, professional repository ready for production

---

## EXECUTIVE SUMMARY

This document consolidates all cleanup activities into a single execution plan.

### Scope
1. ✅ **Branch Cleanup:** Delete 23 stale branches
2. ✅ **Script Cleanup:** Delete 23 redundant scripts
3. ✅ **Merge Strategy:** Merge critical fixes to main
4. ✅ **Documentation:** Update all references

### Expected Outcomes
- **Branches:** 27 → 2 (93% reduction)
- **Scripts:** 48 → 25 (48% reduction)
- **Main Branch:** Updated with critical fixes
- **Repository:** Professional, maintainable, production-ready

---

## PHASE 1: CAPTURE CURRENT STATE

### Step 1.1: Create Snapshot Branch

```bash
# Create snapshot of current state before cleanup
git checkout -b snapshot/pre-cleanup-2025-10-07
git push origin snapshot/pre-cleanup-2025-10-07
```

**Purpose:** Safety net - can restore if needed

---

### Step 1.2: Verify Current Branch Status

```bash
# Verify we're on the right branch
git branch --show-current
# Should show: fix/test-suite-and-production-issues

# Verify no uncommitted changes
git status
# Should show: nothing to commit, working tree clean
```

**Status:** ✅ VERIFIED - No uncommitted changes

---

## PHASE 2: MERGE CRITICAL FIXES TO MAIN

### Step 2.1: Merge fix/test-suite-and-production-issues

```bash
# Fetch latest from remote
git fetch origin

# Checkout main
git checkout main

# Merge fix branch
git merge fix/test-suite-and-production-issues --no-ff -m "Merge critical timeout and production fixes

- HTTP timeout fix (60s → 300s) - ROOT CAUSE FIX
- Debug logging cleanup (removed all print() statements)
- Supabase integration activated
- Tool validation suite complete (37 tests)
- Comprehensive audit documentation

Fixes #[issue-number] (if applicable)
"

# Push to remote
git push origin main
```

**Expected Result:** Main branch updated with 30 commits, 964 files changed

---

### Step 2.2: Merge docs/wave1-complete-audit

```bash
# Merge documentation branch
git merge docs/wave1-complete-audit --no-ff -m "Merge Wave 1 comprehensive audit documentation

- Complete EXAI audit with thinkdeep + codereview
- Documentation baseline established
- Audit findings documented
"

# Push to remote
git push origin main
```

**Expected Result:** Main branch has complete audit documentation

---

### Step 2.3: Tag New Baseline

```bash
# Create tag for new baseline
git tag -a v2.0.0-production-ready -m "Production-ready baseline with critical fixes

- HTTP timeout fix (60s → 300s)
- Debug logging cleanup
- Supabase integration
- Tool validation suite (37 tests)
- Comprehensive audit documentation
"

# Push tag
git push origin v2.0.0-production-ready
```

**Purpose:** Mark this as a significant milestone

---

## PHASE 3: DELETE REDUNDANT SCRIPTS

### Step 3.1: Delete GLM Web Search Test Scripts (6)

```bash
git rm scripts/test_glm_websearch.py
git rm scripts/test_glm_websearch_detailed.py
git rm scripts/test_glm_all_configs.py
git rm scripts/debug_glm_websearch_response.py
git rm scripts/test_web_search_fix.py
git rm scripts/test_websearch_fix_final.py
```

---

### Step 3.2: Delete Kimi/Native Web Search Tests (3)

```bash
git rm scripts/test_native_websearch.py
git rm scripts/test_kimi_builtin_flow.py
git rm scripts/test_websearch_rag_failure.py
```

---

### Step 3.3: Delete Debug/Diagnostic Scripts (4)

```bash
git rm scripts/debug_kimi_tool_calls.py
git rm scripts/debug_model_response.py
git rm scripts/tmp_registry_probe.py
git rm scripts/diagnostics/exai_diagnose.py  # Duplicate
```

---

### Step 3.4: Delete Wave/Epic Test Scripts (2)

```bash
git rm scripts/test_wave3_complete.py
git rm scripts/test_agentic_transition.py
```

---

### Step 3.5: Delete Documentation/Cleanup Scripts (3)

```bash
git rm scripts/validate_docs.py
git rm scripts/docs_cleanup/verify_kimi_cleanup.py
git rm scripts/delete_all_kimi_files.py
```

---

### Step 3.6: Delete Validation/Probe Scripts (2)

```bash
git rm scripts/validate_exai_ws_kimi_tools.py
git rm scripts/probe_kimi_tooluse.py
```

---

### Step 3.7: Delete Diagnostic Kimi Scripts (3)

```bash
git rm scripts/diagnostics/kimi/capture_headers_run.py
git rm scripts/diagnostics/kimi/normalize_tester.py
git rm scripts/check_no_legacy_imports.py
```

---

### Step 3.8: Commit Script Cleanup

```bash
git commit -m "chore: Remove 23 redundant test and diagnostic scripts

Removed scripts superseded by tool_validation_suite:
- 6 GLM web search test scripts
- 3 Kimi/native web search tests
- 4 debug/diagnostic scripts
- 2 wave/epic test scripts
- 3 documentation/cleanup scripts
- 2 validation/probe scripts
- 3 diagnostic Kimi scripts

All functionality now in tool_validation_suite/ with proper structure.

See: tool_validation_suite/docs/audit/REDUNDANT_SCRIPTS_ANALYSIS.md
"

git push origin main
```

---

## PHASE 4: DELETE STALE BRANCHES

### Step 4.1: Delete Local Feature Branches (8)

```bash
git branch -D feature/cleanup-and-reorganization
git branch -D feature/exai-mcp-roadmap-implementation
git branch -D feature/phase-a-context-registry-fixes
git branch -D feature/p0-fallback-orchestrator-20250921
git branch -D feat/phaseA-providers-shim
git branch -D feat/phaseB-import-blocker-and-docs-cleanup
git branch -D feat/phaseB-router-unification
git branch -D feat/phaseD-pr1-modelrouter-observability
```

---

### Step 4.2: Delete Local Chore Branches (7)

```bash
git branch -D chore/docs-sweep-and-layering
git branch -D chore/manager-ui-reorg-docs
git branch -D chore/massive-cleanup-20250928
git branch -D chore/mcp-chat-qa-and-textcontent-hardening
git branch -D chore/mcp-glm-websearch-toolcall-loop
git branch -D chore/registry-switch-and-docfix
git branch -D chore/tests-routing-continuation
```

---

### Step 4.3: Delete Local Snapshot Branches (2)

```bash
git branch -D snapshot/all-local-changes-20250927
git branch -D stage1-cleanup-complete
```

---

### Step 4.4: Delete Local Integration Branches (3)

```bash
git branch -D integration/pr3-pr4-combined-20250926
git branch -D pr-1-review
git branch -D glm-flash-intelligent-router
```

---

### Step 4.5: Delete Local Experimental Branches (3)

```bash
git branch -D feat/phaseF-shim-removal
git branch -D feat/docs-restore-phaseD-from-stash
git branch -D ci/setup-ci
```

---

### Step 4.6: Delete Merged Branches (2)

```bash
# These were just merged to main
git branch -D fix/test-suite-and-production-issues
git branch -D docs/wave1-complete-audit
```

---

### Step 4.7: Delete Remote Branches Using gh-mcp

```bash
# Use gh-mcp to delete remote branches
# This will be done via gh_branch_delete_gh-mcp tool
```

**Note:** Will use gh-mcp tools to delete remote branches safely

---

## PHASE 5: REVIEW REMAINING BRANCH

### Step 5.1: Review feat/auggie-mcp-optimization

```bash
# Checkout and review
git checkout feat/auggie-mcp-optimization

# Compare with main
git diff main..feat/auggie-mcp-optimization

# Decision: Merge or Delete?
```

**Options:**
1. **Merge** if Auggie optimizations still relevant
2. **Delete** if superseded by main branch changes

---

## PHASE 6: UPDATE DOCUMENTATION

### Step 6.1: Update README

Update main README.md to reflect:
- New baseline version (v2.0.0)
- Tool validation suite
- Simplified branch structure
- Updated testing instructions

---

### Step 6.2: Update CONTRIBUTING.md

Update contribution guidelines:
- Branch naming conventions
- Where to add tests (validation suite)
- Script organization rules
- Cleanup process

---

### Step 6.3: Create CHANGELOG

Create CHANGELOG.md with:
- v2.0.0 release notes
- Critical fixes
- Breaking changes (if any)
- Migration guide

---

## PHASE 7: VALIDATION

### Step 7.1: Verify Repository State

```bash
# List all branches
git branch -a

# Should show:
# * main
# (optional) feat/auggie-mcp-optimization
# remotes/origin/main
# remotes/origin/snapshot/pre-cleanup-2025-10-07
```

---

### Step 7.2: Verify Scripts

```bash
# Count scripts
ls scripts/*.py | wc -l
# Should show: ~13 scripts

ls scripts/diagnostics/*.py | wc -l
# Should show: ~4 scripts

ls scripts/ws/*.py | wc -l
# Should show: ~4 scripts
```

---

### Step 7.3: Run Test Suite

```bash
# Restart daemon
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\ws_start.ps1 -Restart

# Run validation suite
python tool_validation_suite/scripts/run_all_tests_simple.py
```

**Expected:** >90% pass rate, 0% timeouts

---

## ROLLBACK PLAN

If anything goes wrong:

```bash
# Restore from snapshot
git checkout snapshot/pre-cleanup-2025-10-07

# Or restore from tag
git checkout v2.0.0-production-ready

# Or restore specific branch
git checkout origin/fix/test-suite-and-production-issues
```

---

## SUCCESS CRITERIA

- ✅ Main branch has critical fixes
- ✅ Only 2-3 active branches remain
- ✅ Only 25 scripts remain (all fit-for-purpose)
- ✅ All tests pass (>90% pass rate)
- ✅ Documentation updated
- ✅ Repository looks professional

---

## EXECUTION TIMELINE

**Total Time:** ~2 hours

1. **Phase 1:** 15 minutes - Snapshot and verification
2. **Phase 2:** 30 minutes - Merge to main
3. **Phase 3:** 20 minutes - Delete scripts
4. **Phase 4:** 20 minutes - Delete branches
5. **Phase 5:** 10 minutes - Review remaining branch
6. **Phase 6:** 20 minutes - Update documentation
7. **Phase 7:** 15 minutes - Validation

---

**Status:** Ready for execution  
**Next Action:** Begin Phase 1 - Create snapshot  
**Expected Outcome:** Professional, production-ready repository

