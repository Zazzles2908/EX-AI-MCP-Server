# MASTER CHECKLIST - EX-AI-MCP-SERVER
**Created:** 2025-10-14 (14th October 2025)  
**Purpose:** Ultimate consolidated checklist merging GOD Checklist + 8 Critical Bugs  
**Status:** ACTIVE - Phase A (Stabilize)

---

## 📊 EXECUTIVE SUMMARY

**Current State:**
- **Original GOD Checklist:** Phase 2 Cleanup 75% Complete (4 issues remaining)
- **New Critical Bugs:** 8 bugs discovered during real-world testing (0 fixed)
- **Total Outstanding Issues:** 12 issues (4 from GOD + 8 new bugs)

**System Status:**
- ✅ Architecture: Well-documented, clean 4-tier design
- ✅ Core Functionality: 29 tools, 2 providers, 22 models
- ⚠️ Stability: Auth token warnings, parameter enforcement failures
- ❌ Testing: Real-world testing revealed critical bugs

**Critical Blockers:**
1. **SAFETY CRITICAL:** K2 models giving 9x different calculations (11.2 vs 1.22 cal/cm²)
2. **Parameter Enforcement:** use_websearch=false being ignored
3. **Model Behavior:** glm-4.6 returning raw JSON instead of executing tools
4. **Thinking Mode:** Not working (was using wrong API format)

---

## 🎯 CONSOLIDATED PHASES

### Phase Structure (Merged)

```
PHASE A: STABILIZE (CRITICAL - 3-5 days)
├─ A.1: Fix 8 Critical Bugs (NEW - from real-world testing)
│   ├─ Bug #1: K2 Consistency (SAFETY CRITICAL)
│   ├─ Bug #2: use_websearch=false enforcement
│   ├─ Bug #3: glm-4.6 tool_choice
│   ├─ Bug #4: Model locking in continuations
│   ├─ Bug #5: Thinking mode (FIXED - was using wrong API format)
│   ├─ Bug #6: Artifact cleaning
│   ├─ Bug #7: Empty prompt validation
│   └─ Bug #8: Invalid model warnings
├─ A.2: Fix 4 Remaining GOD Issues
│   ├─ Issue #4: Auth token errors
│   ├─ Issue #7: WorkflowTools testing gaps
│   ├─ Issue #9: Expert analysis timeout
│   └─ Issue #10: next_call_builder bug
└─ A.3: System Stability Verification

PHASE B: CLEANUP (HIGH PRIORITY - 3-5 days)
├─ B.1: Complete Phase 2 Cleanup tasks
├─ B.2: WorkflowTools comprehensive testing
└─ B.3: Integration testing

PHASE C: OPTIMIZE (MEDIUM PRIORITY - 1-2 weeks)
├─ C.1: Performance improvements
├─ C.2: Documentation consolidation
└─ C.3: Testing coverage expansion

PHASE D: REFACTOR (LOW PRIORITY - 2-4 weeks)
├─ D.1: SimpleTool modularization (if needed)
├─ D.2: WorkflowTool improvements
└─ D.3: Code organization
```

---

## ⚡ PHASE A: STABILIZE (CRITICAL)

### Entry Criteria
- [x] Real-world testing revealed 8 critical bugs
- [x] GOD Checklist has 4 remaining issues
- [x] System functional but unstable

### Exit Criteria
- [ ] All 8 critical bugs fixed and tested
- [ ] All 4 GOD issues resolved
- [ ] System runs stable for 24 hours
- [ ] All core tools tested and working

---

## 🔴 TASK A.1: FIX 8 CRITICAL BUGS

**Status:** [→] IN PROGRESS (Phase 1 Complete: Bugs #1, #5)  
**Priority:** 🔴 CRITICAL - Blocking production use  
**Estimated Time:** 3-5 days

### Implementation Phases

**Phase 1: Critical Fixes (Safety + Thinking Mode)** ✅ COMPLETE
- [x] Bug #1: K2 Investigation Script Created
- [x] Bug #5: Thinking Mode Fixed (GLM + Kimi)

**Phase 2: Parameter Enforcement** [ ] NOT STARTED
- [ ] Bug #2: use_websearch=false enforcement
- [ ] Bug #4: Model locking in continuations

**Phase 3: Response Quality** [ ] NOT STARTED
- [ ] Bug #3: glm-4.6 tool_choice
- [ ] Bug #6: Artifact cleaning
- [ ] Bug #7: Empty prompt validation
- [ ] Bug #8: Invalid model warnings

**Phase 4: Testing & Documentation** [ ] NOT STARTED
- [ ] Test all fixes across multiple tools
- [ ] Update documentation
- [ ] Create evidence files

---

### Bug #1: K2 Consistency (SAFETY CRITICAL)

**Status:** [x] Investigation Script Created | [ ] Root Cause Found | [ ] Fixed

**Problem:**
- K2 models giving 9x different results for arc flash calculations
- User reported: 11.2 cal/cm² vs 1.22 cal/cm² for identical inputs
- SAFETY CRITICAL: Incorrect calculations could lead to injury/death

**Investigation:**
- [x] Created `scripts/testing/test_k2_consistency.py`
- [ ] Run script to identify which model is incorrect
- [ ] Report findings to Moonshot AI
- [ ] Document workaround or fix

**Files:**
- `scripts/testing/test_k2_consistency.py` (195 lines)

---

### Bug #5: Thinking Mode (FIXED)

**Status:** [x] FIXED | [ ] Tested

**Problem:**
- thinking_mode parameter had no effect
- Was using wrong API format for both providers

**Root Cause:**
- **GLM:** Was filtering out thinking_mode instead of converting to `thinking: {"type": "enabled"}`
- **Kimi:** Was passing thinking_mode as parameter instead of using `kimi-thinking-preview` model
- **CRITICAL MISUNDERSTANDING:** thinking_mode categories (minimal/low/medium/high/max) are for EXPERT_ANALYSIS, NOT GLM API!

**Fix:**
- **GLM:** Convert thinking_mode → `thinking: {"type": "enabled"}` (src/providers/glm_chat.py)
- **Kimi:** Extract reasoning_content from kimi-thinking-preview streaming (streaming/streaming_adapter.py)

**API Documentation:**
- GLM: https://docs.z.ai/api-reference/llm/chat-completion
- Kimi: https://platform.moonshot.ai/docs/guide/use-kimi-thinking-preview-model

**Files Modified:**
- `src/providers/glm_chat.py` (lines 51-64)
- `streaming/streaming_adapter.py` (NEW FILE - 98 lines)
- `streaming/__init__.py` (NEW FILE - 5 lines)

**Testing Required:**
- [ ] Test GLM with thinking_mode parameter
- [ ] Test Kimi with kimi-thinking-preview model
- [ ] Verify reasoning extraction works
- [ ] Test across multiple tools

---

### Bug #2: use_websearch=false Enforcement

**Status:** [ ] NOT STARTED

**Problem:**
- use_websearch=false parameter being ignored
- Models still performing web searches when explicitly disabled

**Investigation Needed:**
- [ ] Check parameter flow: Tool → Router → Provider
- [ ] Verify GLM web_search object construction
- [ ] Verify Kimi builtin_function construction
- [ ] Check if parameter is being overridden somewhere

**Hypothesis:**
- Parameter validation exists but enforcement may be missing
- May need to explicitly set web_search.enable=false for GLM
- May need to remove $web_search from Kimi tools array

---

### Bug #3: glm-4.6 tool_choice

**Status:** [ ] NOT STARTED

**Problem:**
- glm-4.6 returns raw JSON instead of executing tool calls
- Other GLM models work correctly

**Proposed Fix:**
```python
# File: src/providers/glm_chat.py (add after line 140)
if model_name == "glm-4.6" and payload.get("tools"):
    if not payload.get("tool_choice"):
        payload["tool_choice"] = "auto"
        logger.info(f"GLM-4.6: Forcing tool_choice='auto' for function calling")
```

---

### Bug #4: Model Locking in Continuations

**Status:** [ ] NOT STARTED

**Problem:**
- Model switches mid-conversation in continuation threads
- Should lock to initial model for consistency

**Investigation Needed:**
- [ ] Check thread storage for model_name
- [ ] Verify model selection in continuation flow
- [ ] Check if router is being called for continuations

---

### Bug #6: Artifact Cleaning

**Status:** [ ] NOT STARTED

**Problem:**
- Response contains artifacts like `<think>` tags or `<|begin_of_box|>` markers
- Should be cleaned before returning to user

**Proposed Fix:**
- Add artifact cleaning to SimpleTool response processing
- Strip known artifact patterns from GLM responses

---

### Bug #7: Empty Prompt Validation

**Status:** [ ] NOT STARTED

**Problem:**
- Empty prompts being accepted and sent to API
- Wastes API calls and confuses models

**Proposed Fix:**
- Add validation in SimpleTool.prepare_prompt()
- Raise ValueError if prompt is empty or whitespace-only

---

### Bug #8: Invalid Model Warnings

**Status:** [ ] NOT STARTED

**Problem:**
- Invalid model names silently fall back to defaults
- No warning to user about model not existing

**Proposed Fix:**
- Add model validation in RouterService
- Log warning when falling back to default model
- Include available models in warning message

---

## 🔴 TASK A.2: FIX 4 REMAINING GOD ISSUES

**Status:** [ ] NOT STARTED  
**Priority:** 🔴 CRITICAL  
**Estimated Time:** 2-3 days

### Issue #4: Auth Token Errors
- [ ] Investigate auth validation logic
- [ ] Fix token passing in shim
- [ ] Test with multiple clients
- [ ] Document fix

### Issue #7: WorkflowTools Testing Gaps
- [ ] Create comprehensive test suite
- [ ] Test all 12 workflow tools
- [ ] Document test results

### Issue #9: Expert Analysis Timeout
- [ ] Investigate timeout configuration
- [ ] Fix timeout hierarchy
- [ ] Test with long-running analysis

### Issue #10: next_call_builder Bug
- [ ] Investigate bug in next_call_builder
- [ ] Fix and test
- [ ] Document fix

---

## 📚 DOCUMENTATION REORGANIZATION

**Current State:** Documentation scattered across multiple directories

**Proposed Structure:**
```
docs/
├── 01_ARCHITECTURE/          # System design, architecture diagrams
├── 02_API_REFERENCE/          # Provider APIs, tool schemas
├── 03_IMPLEMENTATION/         # Code implementation details
├── 04_TESTING/                # Test plans, results, evidence
├── 05_ISSUES/                 # Bug reports, investigations
├── 06_PROGRESS/               # Session summaries, checklists
└── 07_ARCHIVE/                # Old/deprecated docs
```

**Action Items:**
- [ ] Create new directory structure
- [ ] Move existing docs to appropriate categories
- [ ] Update README with navigation guide
- [ ] Remove duplicate/obsolete docs

---

## 🎯 NEXT IMMEDIATE STEPS

1. **Run K2 Investigation** (15 minutes)
   ```bash
   python scripts/testing/test_k2_consistency.py
   ```

2. **Test Thinking Mode** (30 minutes)
   - Test GLM with thinking_mode parameter
   - Test Kimi with kimi-thinking-preview model

3. **Restart Server** (5 minutes)
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\ws_start.ps1 -Restart
   ```

4. **Continue with Phase 2** (2-3 days)
   - Fix Bug #2: use_websearch=false
   - Fix Bug #4: Model locking
   - Fix Bug #3: glm-4.6 tool_choice
   - Fix Bugs #6, #7, #8

5. **Documentation Cleanup** (1 day)
   - Reorganize docs by category
   - Consolidate investigation files
   - Update master checklist

---

**Last Updated:** 2025-10-14 (14th October 2025)  
**Next Review:** After Phase 1 testing complete

