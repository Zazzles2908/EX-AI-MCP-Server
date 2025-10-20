# Phase 2: Parameter Enforcement Bug Fixes
**Date:** 2025-10-14 (14th October 2025)  
**Phase:** Phase 2 - Parameter Enforcement  
**Status:** IN PROGRESS (1/2 bugs fixed)

---

## 📊 Progress Summary

**Bugs in Phase 2:**
- [x] Bug #2: use_websearch=false enforcement ✅ FIXED
- [x] Bug #4: Model locking in continuations ✅ FIXED

**Overall Progress:** 100% (2/2 bugs fixed) ✅ COMPLETE

---

## ✅ Bug #2: use_websearch=false Enforcement - FIXED

### Problem
`use_websearch=false` parameter was being ignored - web search was performed even when explicitly disabled.

### Root Cause
**Location:** `tools/providers/kimi/kimi_tools_chat.py` lines 145-148

**Issue:** Environment variable override using `OR` logic
```python
# BEFORE (BROKEN):
use_websearch = bool(arguments.get("use_websearch", False)) or (
    os.getenv("KIMI_ENABLE_INTERNET_TOOL", "false").strip().lower() == "true" or
    os.getenv("KIMI_ENABLE_INTERNET_SEARCH", "false").strip().lower() == "true"
)
```

**Problem:** Even if `use_websearch=False`, environment variables would override it!

### Fix Applied
```python
# AFTER (FIXED):
use_websearch_arg = arguments.get("use_websearch")
if use_websearch_arg is not None:
    # User explicitly set use_websearch - respect their choice (even if False)
    use_websearch = bool(use_websearch_arg)
else:
    # No explicit choice - use environment variable defaults
    use_websearch = (
        os.getenv("KIMI_ENABLE_INTERNET_TOOL", "false").strip().lower() == "true" or
        os.getenv("KIMI_ENABLE_INTERNET_SEARCH", "false").strip().lower() == "true"
    )
```

### Verification
**GLM Provider:** ✅ Does NOT have this issue (uses centralized websearch_adapter)

**Files Modified:**
- `tools/providers/kimi/kimi_tools_chat.py` (lines 144-156)

**Files Created:**
- `docs/05_ISSUES/BUG_2_WEBSEARCH_ENFORCEMENT_FIX.md` - Complete analysis
- `scripts/testing/test_websearch_enforcement.py` - Test script (needs server running)

**Status:** ✅ FIXED - Ready for testing

---

## ✅ Bug #4: Model Locking in Continuations - FIXED

### Problem
Model switches mid-conversation during continuations, breaking conversation context.

### Root Cause
**Location:** Two-part issue:
1. `src/server/context/thread_context.py` - Sets model from previous turn ✅
2. `src/server/handlers/request_handler_model_resolution.py` - Routing overrides it ❌

**Issue:** No communication between thread context and routing logic

**Example Flow:**
1. User starts with `kimi-thinking-preview`
2. Continuation sets `model = "kimi-thinking-preview"` ✅
3. Routing sees tool="chat" and returns `"glm-4.5-flash"` ❌
4. Model switches mid-conversation! ❌

### Fix Applied
**Part 1:** Add model lock flag when continuation sets model
```python
# src/server/context/thread_context.py (lines 187-198)
if not model_from_args and context.turns:
    for turn in reversed(context.turns):
        if turn.role == "assistant" and turn.model_name:
            arguments["model"] = turn.model_name
            # CRITICAL FIX: Lock model to prevent routing override
            arguments["_model_locked_by_continuation"] = True
            logger.debug(f"Using model from previous turn: {turn.model_name} (locked)")
            break
```

**Part 2:** Respect lock flag in routing logic
```python
# src/server/handlers/request_handler_model_resolution.py (lines 44-71)
def _route_auto_model(tool_name: str, requested: str | None, args: Dict[str, Any]) -> str | None:
    # CRITICAL FIX: Respect model lock from continuation
    if args.get("_model_locked_by_continuation"):
        logger.debug(f"[MODEL_ROUTING] Model locked by continuation - skipping auto-routing")
        return requested  # Skip routing, use continuation model

    # ... rest of routing logic
```

### Verification
**Files Modified:**
- `src/server/context/thread_context.py` (lines 187-198)
- `src/server/handlers/request_handler_model_resolution.py` (lines 44-71)

**Files Created:**
- `docs/05_ISSUES/BUG_4_MODEL_LOCKING_FIX.md` - Complete analysis

**Status:** ✅ FIXED - Ready for testing

---

## 📁 Files Modified

### Code Changes
1. `tools/providers/kimi/kimi_tools_chat.py` (lines 144-156)
   - Fixed use_websearch enforcement logic
   - Respects explicit user choice before env defaults

### Documentation Created
1. `docs/05_ISSUES/BUG_2_WEBSEARCH_ENFORCEMENT_FIX.md`
   - Complete root cause analysis
   - Fix implementation details
   - Verification plan

2. `docs/06_PROGRESS/PHASE_2_BUG_FIXES_2025-10-14.md` (this file)
   - Phase 2 progress tracking
   - Bug fix summaries

### Test Scripts Created
1. `scripts/testing/test_websearch_enforcement.py`
   - Tests use_websearch=false enforcement
   - Tests use_websearch=true works
   - Needs server running to execute

---

## 🎯 Next Steps

### Immediate (Bug #4)
1. [ ] Investigate model locking in continuations
2. [ ] Identify where model selection happens
3. [ ] Check thread storage for model persistence
4. [ ] Create fix for model locking
5. [ ] Test fix across multiple tools

### After Phase 2
1. [ ] Move to Phase 3: Response Quality (Bugs #3, #6, #7, #8)
2. [ ] Test all fixes together
3. [ ] Create comprehensive evidence files
4. [ ] Update MASTER_CHECKLIST

---

## 📊 Overall Bug Fix Progress

**Phase 1: Critical Fixes** ✅ COMPLETE (2/2)
- [x] Bug #1: K2 Investigation Script
- [x] Bug #5: Thinking Mode

**Phase 2: Parameter Enforcement** ✅ COMPLETE (2/2)
- [x] Bug #2: use_websearch enforcement
- [x] Bug #4: Model locking

**Phase 3: Response Quality** ⏳ NOT STARTED (4/4)
- [ ] Bug #3: glm-4.6 tool_choice
- [ ] Bug #6: Artifact cleaning
- [ ] Bug #7: Empty prompt validation
- [ ] Bug #8: Invalid model warnings

**Phase 4: Testing & Documentation** ⏳ NOT STARTED
- [ ] Test all fixes
- [ ] Update documentation
- [ ] Create evidence files

**Total Progress:** 50% (4/8 bugs fixed)

---

## 🔍 Investigation Notes

### use_websearch Enforcement (Bug #2)

**Key Insight:** The issue was NOT in the centralized code (`src/providers/capabilities.py`, `src/providers/orchestration/websearch_adapter.py`) - those were correct!

**The bug was in Kimi-specific tool code** that bypassed the centralized logic with its own environment variable check.

**Lesson Learned:** Provider-specific tools should use centralized capabilities layer instead of implementing their own logic.

**Future Prevention:** 
- Code review for provider-specific overrides
- Prefer centralized capabilities layer
- Document when provider-specific logic is needed

---

## ✅ Verification Checklist

### Bug #2 (use_websearch)
- [x] Root cause identified
- [x] Fix implemented
- [x] GLM verified (no similar issue)
- [ ] Test script executed (needs server)
- [ ] Evidence file created
- [ ] Documentation updated

### Bug #4 (model locking)
- [ ] Root cause identified
- [ ] Fix implemented
- [ ] Test script created
- [ ] Test script executed
- [ ] Evidence file created
- [ ] Documentation updated

---

**Last Updated:** 2025-10-14 (14th October 2025)  
**Next Update:** After Bug #4 investigation complete  
**Status:** 🔄 IN PROGRESS - Moving to Bug #4

