# WORKFLOWTOOLS TESTING PLAN - 2025-10-12
**Date:** 2025-10-12 12:25 PM AEDT  
**Status:** Ready to Execute  
**Priority:** HIGH - Validates critical bug fix

---

## 🎯 OBJECTIVE

Test the file inclusion bug fix in 4 WorkflowTools to validate:
1. Tools respect `EXPERT_ANALYSIS_INCLUDE_FILES=false` from `.env`
2. No file bloat occurs during expert analysis
3. Daemon remains stable during testing
4. Tools function correctly without file inclusion

---

## 🔧 BUG FIX SUMMARY

**Problem:** 4 WorkflowTools hardcoded file inclusion, ignoring `.env` configuration  
**Files Fixed:**
- `tools/workflows/analyze.py`
- `tools/workflows/codereview.py`
- `tools/workflows/refactor.py`
- `tools/workflows/secaudit.py`

**Fix:** Removed `_prepare_files_for_expert()` method overrides  
**Result:** Tools now inherit correct behavior from `ExpertAnalysisMixin` base class

---

## 📋 TEST PLAN

### Test 1: Analyze Tool
**Tool:** `analyze_EXAI-WS`  
**Test Case:** Simple code analysis without file inclusion  
**Expected:** Tool completes successfully, no file bloat, daemon stable

**MCP Call:**
```json
{
  "tool": "analyze_EXAI-WS",
  "arguments": {
    "step": "Test analyze tool after file inclusion fix",
    "step_number": 1,
    "total_steps": 1,
    "next_step_required": false,
    "findings": "Testing file inclusion fix",
    "model": "glm-4.5-flash",
    "confidence": "high"
  }
}
```

### Test 2: Codereview Tool
**Tool:** `codereview_EXAI-WS`  
**Test Case:** Simple code review without file inclusion  
**Expected:** Tool completes successfully, no file bloat, daemon stable

**MCP Call:**
```json
{
  "tool": "codereview_EXAI-WS",
  "arguments": {
    "step": "Test codereview tool after file inclusion fix",
    "step_number": 1,
    "total_steps": 1,
    "next_step_required": false,
    "findings": "Testing file inclusion fix",
    "model": "glm-4.5-flash",
    "confidence": "high"
  }
}
```

### Test 3: Refactor Tool
**Tool:** `refactor_EXAI-WS`  
**Test Case:** Simple refactoring analysis without file inclusion  
**Expected:** Tool completes successfully, no file bloat, daemon stable

**MCP Call:**
```json
{
  "tool": "refactor_EXAI-WS",
  "arguments": {
    "step": "Test refactor tool after file inclusion fix",
    "step_number": 1,
    "total_steps": 1,
    "next_step_required": false,
    "findings": "Testing file inclusion fix",
    "model": "glm-4.5-flash",
    "confidence": "incomplete"
  }
}
```

### Test 4: Secaudit Tool
**Tool:** `secaudit_EXAI-WS`  
**Test Case:** Simple security audit without file inclusion  
**Expected:** Tool completes successfully, no file bloat, daemon stable

**MCP Call:**
```json
{
  "tool": "secaudit_EXAI-WS",
  "arguments": {
    "step": "Test secaudit tool after file inclusion fix",
    "step_number": 1,
    "total_steps": 1,
    "next_step_required": false,
    "findings": "Testing file inclusion fix",
    "model": "glm-4.5-flash",
    "confidence": "high"
  }
}
```

---

## ✅ SUCCESS CRITERIA

### For Each Tool:
1. ✅ Tool executes without errors
2. ✅ No file bloat in request (check logs for file count)
3. ✅ Daemon remains stable (no crashes)
4. ✅ Response is coherent and useful
5. ✅ Execution time is reasonable (<30 seconds)

### Overall:
1. ✅ All 4 tools pass individual tests
2. ✅ No daemon crashes during testing
3. ✅ File inclusion is properly disabled
4. ✅ Tools function correctly without files

---

## 📊 MONITORING

### What to Watch:
1. **Daemon Logs** (`logs/ws_daemon.log`) - Check for errors/crashes
2. **Tool Call Logs** (`logs/toolcalls.jsonl`) - Verify no file bloat
3. **Server Logs** (`logs/server.log`) - Monitor for issues
4. **Memory Usage** - Ensure no memory spikes

### Red Flags:
- ⚠️ Daemon crashes during tool execution
- ⚠️ Large file lists in request payloads
- ⚠️ Timeout errors
- ⚠️ Memory spikes

---

## 🔄 EXECUTION STEPS

1. **Pre-Test Verification**
   - ✅ Confirm `.env` has `EXPERT_ANALYSIS_INCLUDE_FILES=false`
   - ✅ Verify server is running cleanly
   - ✅ Check no lingering processes

2. **Server Restart**
   - ✅ Clean restart to load bug fixes
   - ✅ Verify 29 tools loaded
   - ✅ Confirm providers configured

3. **Execute Tests**
   - Run Test 1 (analyze)
   - Monitor daemon stability
   - Run Test 2 (codereview)
   - Monitor daemon stability
   - Run Test 3 (refactor)
   - Monitor daemon stability
   - Run Test 4 (secaudit)
   - Monitor daemon stability

4. **Post-Test Analysis**
   - Review all logs
   - Verify no file bloat
   - Confirm daemon stability
   - Document results

---

## 📝 RESULTS TEMPLATE

### Test Results: [Tool Name]
**Date:** 2025-10-12  
**Time:** [HH:MM AEDT]  
**Status:** ✅ PASS / ❌ FAIL

**Execution:**
- Duration: [X seconds]
- Errors: [None / Description]
- Daemon Status: [Stable / Crashed]

**File Inclusion:**
- Files Embedded: [0 expected]
- Bloat Detected: [Yes / No]

**Response Quality:**
- Coherent: [Yes / No]
- Useful: [Yes / No]

**Notes:**
[Any observations]

---

## 🎓 LESSONS LEARNED

**To be filled after testing:**
- What worked well?
- What issues were discovered?
- What needs further investigation?
- What improvements can be made?

---

**Next Steps After Testing:**
1. Document all results
2. Update task manager
3. If all tests pass: Mark Task 2.G.4 complete
4. If issues found: Create new bug reports
5. Proceed with Phase 3 planning

---

**Created:** 2025-10-12 12:25 PM AEDT  
**Status:** Ready for execution

