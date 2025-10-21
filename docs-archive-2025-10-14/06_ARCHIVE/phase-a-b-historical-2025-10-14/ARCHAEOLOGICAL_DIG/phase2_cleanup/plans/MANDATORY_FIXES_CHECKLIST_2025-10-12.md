# MANDATORY FIXES CHECKLIST - EXAI WORKFLOWTOOLS
**Date:** 2025-10-12 10:25 AM AEDT (12th October 2025, Saturday)
**Type:** Actionable Checklist - Required Before EXAI Usage
**Priority:** 🔴 CRITICAL - BLOCKING EXAI DEVELOPMENT
**Status:** ⏳ NOT STARTED

---

## 🎯 PURPOSE

This checklist contains **MANDATORY fixes** that MUST be completed before EXAI tools can be reliably used for WorkflowTool development and testing.

**Why These Fixes Are Mandatory:**
1. **EXAI tools lack model capability awareness** - Agent cannot make informed decisions
2. **Daemon crashes prevent EXAI usage** - System is unstable
3. **Core functionality disabled** - 4 tools have file inclusion disabled
4. **State leakage risks** - Tools may behave unpredictably
5. **Security vulnerabilities** - Validation logic is misplaced

---

## 🔴 BLOCKING FIXES (MUST COMPLETE FIRST)

### ✅ Fix 1: EXAI Model Capability Documentation
**Status:** [ ] NOT STARTED  
**Priority:** 🔴 BLOCKING  
**Estimated Effort:** 2-4 hours  
**Assigned To:** _____________  
**Due Date:** _____________

#### Tasks:
- [ ] **Task 1.1:** Create model capability matrix
  - [ ] Document file upload support per model
  - [ ] Document web search support per model
  - [ ] Document thinking mode support per model
  - [ ] Document max context window per model
  - [ ] Document cost per 1M tokens per model
  
- [ ] **Task 1.2:** Add capability validation to EXAI tools
  - [ ] Create `ModelCapabilityValidator` class
  - [ ] Add validation before file upload operations
  - [ ] Add validation before web search operations
  - [ ] Add validation before thinking mode operations
  
- [ ] **Task 1.3:** Add warnings and guidance
  - [ ] Warn when using model for unsupported operation
  - [ ] Suggest alternative models when operation unsupported
  - [ ] Display cost implications before expensive operations
  
- [ ] **Task 1.4:** Update documentation
  - [ ] Add model capability matrix to `.env.example`
  - [ ] Update EXAI tool descriptions with capability info
  - [ ] Create model selection guide

#### Acceptance Criteria:
- [ ] Agent receives clear warnings for unsupported operations
- [ ] Model capability matrix accessible to all EXAI tools
- [ ] Cost implications visible before expensive operations
- [ ] Documentation updated with capability information

#### Files to Modify:
- `.env` - Add model capability configuration
- `.env.example` - Add model capability documentation
- `tools/workflow/model_capabilities.py` - NEW FILE
- `tools/simple/chat.py` - Add capability validation
- `docs/EXAI_MODEL_CAPABILITIES.md` - NEW FILE

---

### ✅ Fix 2: Daemon Stability Investigation
**Status:** [ ] NOT STARTED  
**Priority:** 🔴 BLOCKING  
**Estimated Effort:** 4-8 hours  
**Assigned To:** _____________  
**Due Date:** _____________

#### Tasks:
- [ ] **Task 2.1:** Investigate crash patterns
  - [ ] Review `logs/ws_daemon.log` for crash patterns
  - [ ] Identify memory limits causing crashes
  - [ ] Identify resource exhaustion patterns
  - [ ] Document crash triggers
  
- [ ] **Task 2.2:** Implement error handling
  - [ ] Add try-catch blocks around critical sections
  - [ ] Implement graceful degradation
  - [ ] Add error logging with context
  - [ ] Prevent cascading failures
  
- [ ] **Task 2.3:** Add health checks
  - [ ] Implement health check endpoint
  - [ ] Add memory usage monitoring
  - [ ] Add connection pool monitoring
  - [ ] Add request queue monitoring
  
- [ ] **Task 2.4:** Implement auto-recovery
  - [ ] Add automatic restart on crash
  - [ ] Implement circuit breaker pattern
  - [ ] Add exponential backoff for retries
  - [ ] Preserve state across restarts

#### Acceptance Criteria:
- [ ] Daemon runs stably for 4+ hour EXAI sessions
- [ ] Crashes logged with actionable error messages
- [ ] Auto-recovery mechanisms prevent downtime
- [ ] Health checks detect issues before crashes

#### Files to Modify:
- `ws_daemon.py` - Add error handling and health checks
- `src/daemon/session_manager.py` - Add auto-recovery
- `scripts/ws_start.ps1` - Add health check integration
- `docs/DAEMON_STABILITY_GUIDE.md` - NEW FILE

---

### ✅ Fix 3: File Inclusion Strategy
**Status:** [ ] NOT STARTED  
**Priority:** 🔴 BLOCKING  
**Estimated Effort:** 6-8 hours  
**Assigned To:** _____________  
**Due Date:** _____________

#### Tasks:
- [ ] **Task 3.1:** Implement environment variables
  - [ ] Add `EXPERT_ANALYSIS_MAX_FILES=10` to `.env`
  - [ ] Add `EXPERT_ANALYSIS_MAX_CONTENT_KB=100` to `.env`
  - [ ] Add `EXPERT_ANALYSIS_FILE_SELECTION=relevance` to `.env`
  - [ ] Document variables in `.env.example`
  
- [ ] **Task 3.2:** Implement smart file selection
  - [ ] Create `FileSelector` class
  - [ ] Implement relevance-based ranking algorithm
  - [ ] Add file size validation
  - [ ] Add content truncation with context preservation
  
- [ ] **Task 3.3:** Update WorkflowTool base class
  - [ ] Add `_select_files_for_expert_analysis()` method
  - [ ] Add `_validate_file_limits()` method
  - [ ] Add `_truncate_file_content()` method
  - [ ] Update `should_include_files_in_expert_prompt()` logic
  
- [ ] **Task 3.4:** Re-enable file inclusion in 4 tools
  - [ ] Uncomment Analyze (lines 323-327)
  - [ ] Uncomment CodeReview (lines 307-311)
  - [ ] Uncomment Refactor (lines 313-317)
  - [ ] Uncomment SecAudit (lines 456-460)
  - [ ] Update to use new base class methods
  
- [ ] **Task 3.5:** Test with realistic scenarios
  - [ ] Test with 100+ files
  - [ ] Test with large files (>1MB)
  - [ ] Test with mixed file sizes
  - [ ] Verify no daemon crashes

#### Acceptance Criteria:
- [ ] File inclusion works without daemon crashes
- [ ] Limits configurable via environment variables
- [ ] Smart selection prioritizes most relevant files
- [ ] All 4 tools have file inclusion re-enabled
- [ ] Content stays under 100KB limit

#### Files to Modify:
- `.env` - Add file inclusion limits
- `.env.example` - Document file inclusion limits
- `tools/workflow/base.py` - Add file selection methods
- `tools/workflow/file_selector.py` - NEW FILE
- `tools/workflows/analyze.py` - Re-enable file inclusion
- `tools/workflows/codereview.py` - Re-enable file inclusion
- `tools/workflows/refactor.py` - Re-enable file inclusion
- `tools/workflows/secaudit.py` - Re-enable file inclusion

---

## 🟡 HIGH PRIORITY FIXES (COMPLETE AFTER BLOCKING)

### ✅ Fix 4: State Management Reset Mechanism
**Status:** [ ] NOT STARTED  
**Priority:** 🟡 HIGH  
**Estimated Effort:** 2-3 hours  
**Assigned To:** _____________  
**Due Date:** _____________

#### Tasks:
- [ ] Add `reset()` method to WorkflowTool base class
- [ ] Implement state reset in ThinkDeep
- [ ] Implement state reset in CodeReview
- [ ] Implement state reset in Consensus
- [ ] Implement state reset in Analyze
- [ ] Call `reset()` at start of each workflow
- [ ] Add unit tests for state reset

#### Files to Modify:
- `tools/workflow/base.py`
- `tools/workflows/thinkdeep.py`
- `tools/workflows/codereview.py`
- `tools/workflows/consensus.py`
- `tools/workflows/analyze.py`
- `tests/test_workflow_state_reset.py` - NEW FILE

---

### ✅ Fix 5: Exception Handling Standardization
**Status:** [ ] NOT STARTED  
**Priority:** 🟡 HIGH  
**Estimated Effort:** 3-4 hours  
**Assigned To:** _____________  
**Due Date:** _____________

#### Tasks:
- [ ] Create standard exception handling patterns
- [ ] Replace silent exception swallowing
- [ ] Add specific exception types
- [ ] Implement proper error propagation
- [ ] Add error context to all exceptions
- [ ] Update all tools to use standard patterns

#### Files to Modify:
- `tools/workflow/exceptions.py` - NEW FILE
- `tools/workflows/consensus.py` - Fix lines 430-434
- `tools/workflows/debug.py` - Fix exception handling
- `tools/workflows/analyze.py` - Fix exception handling
- All other workflow tools

---

### ✅ Fix 6: Security Validation Extraction
**Status:** [ ] NOT STARTED  
**Priority:** 🟡 HIGH  
**Estimated Effort:** 4-6 hours  
**Assigned To:** _____________  
**Due Date:** _____________

#### Tasks:
- [ ] Create `SecurityValidator` class
- [ ] Extract security validation from Debug (line 245)
- [ ] Extract security validation from Analyze (lines 280-315)
- [ ] Extract security validation from CodeReview
- [ ] Implement as middleware/decorator pattern
- [ ] Add comprehensive security tests
- [ ] Document security validation rules

#### Files to Modify:
- `tools/workflow/validators/security.py` - NEW FILE
- `tools/workflows/debug.py`
- `tools/workflows/analyze.py`
- `tools/workflows/codereview.py`
- `tests/test_security_validation.py` - NEW FILE

---

## 📊 PROGRESS TRACKING

### Overall Progress
- **Blocking Fixes:** 0/3 complete (0%)
- **High Priority Fixes:** 0/3 complete (0%)
- **Total Mandatory Fixes:** 0/6 complete (0%)

### Blocking Fixes Status
- [ ] Fix 1: EXAI Model Capability Documentation (0%)
- [ ] Fix 2: Daemon Stability Investigation (0%)
- [ ] Fix 3: File Inclusion Strategy (0%)

### High Priority Fixes Status
- [ ] Fix 4: State Management Reset Mechanism (0%)
- [ ] Fix 5: Exception Handling Standardization (0%)
- [ ] Fix 6: Security Validation Extraction (0%)

---

## 🎯 COMPLETION CRITERIA

**EXAI Usage Unblocked When:**
- ✅ All 3 BLOCKING fixes complete
- ✅ Daemon runs stably for 4+ hours
- ✅ File inclusion works without crashes
- ✅ Model capabilities documented and validated

**Production Ready When:**
- ✅ All 6 MANDATORY fixes complete
- ✅ State management prevents leakage
- ✅ Exception handling is standardized
- ✅ Security validation is extracted

---

## 📝 NOTES

**Important Reminders:**
1. **DO NOT** proceed with EXAI-based development until BLOCKING fixes are complete
2. **DO NOT** skip fixes - they are mandatory for system stability
3. **DO** test each fix thoroughly before marking complete
4. **DO** update this checklist as work progresses
5. **DO** commit after each fix is complete

**Dependencies:**
- Fix 1 has no dependencies (can start immediately)
- Fix 2 has no dependencies (can start immediately)
- Fix 3 depends on Fix 2 (daemon must be stable)
- Fix 4-6 can proceed in parallel after Fix 3

---

**STATUS:** ⏳ AWAITING START - 0/6 MANDATORY FIXES COMPLETE
**BLOCKER:** EXAI usage blocked until all BLOCKING fixes (1-3) are complete
**NEXT ACTION:** Assign owners and due dates, then begin Fix 1

