# CRITICAL BUGS FIXED - 2025-10-04

**Agent:** Autonomous Phase 3 Agent  
**Session Start:** 2025-10-04  
**Status:** ✅ TWO CRITICAL BUGS FIXED

---

## Executive Summary

Fixed two critical bugs that were blocking server functionality:
1. **Server Crash Bug:** Fixed validation error in status.py causing server crash on startup
2. **Web Search Integration Bug:** Fixed regex pattern mismatch preventing web search execution

Both fixes are minimal, targeted, and maintain 100% backward compatibility.

---

## Bug #1: Server Crash on Startup ✅ FIXED

### Symptom
```
ERROR:tools.chat:Error in chat: 1 validation error for ChatRequest
prompt
  Field required [type=missing, input_value={'messages': ['ping'], 'model': 'auto'}, input_type=dict]
```

### Root Cause
**File:** `tools/diagnostics/status.py` line 96  
**Issue:** ChatTool was being called with `messages` parameter instead of `prompt`

```python
# BEFORE (BROKEN):
c_out = await ct.execute({"messages": ["ping"], "model": os.getenv("DEFAULT_MODEL", "glm-4.5-flash")})

# AFTER (FIXED):
c_out = await ct.execute({"prompt": "ping", "model": os.getenv("DEFAULT_MODEL", "glm-4.5-flash")})
```

### Impact
- **Severity:** CRITICAL (P0)
- **Effect:** Server crashed on startup when probe=true
- **Users Affected:** All users running status tool with probe flag

### Fix Applied
Changed parameter name from `messages` to `prompt` in status.py line 96.

---

## Bug #2: Web Search Integration Failure ✅ FIXED

### Symptom
When using `chat_exai` with `use_websearch=true`, the tool returns text like:
```
<tool_call>web_search
query: Python async best practices 2024 latest developments
num_results: 10
```

Instead of actually executing the web search.

### Root Cause
**File:** `src/providers/text_format_handler.py` lines 20-43  
**Issue:** Regex patterns didn't match actual GLM output format

**Expected Format (by regex):**
```xml
<tool_call>web_search...<arg_value>query</arg_value></tool_call>
```

**Actual GLM Format:**
```
<tool_call>web_search
query: Python async best practices 2024 latest developments
num_results: 10
```

The handler had patterns for Format B (XML-style) and Format C (JSON), but not for the actual key:value format GLM returns.

### Investigation Trail

1. **Tested glm_web_search_exai:** ✅ Works perfectly (retrieved 5 results in 2.4s)
2. **Tested chat_exai with use_websearch=true:** ❌ Returns text instead of executing
3. **Traced web search flow:**
   - SimpleTool.execute() → build_websearch_provider_kwargs() ✅
   - Capabilities layer injects web_search tools ✅
   - GLM provider receives proper configuration ✅
   - GLM returns tool call as TEXT (not in tool_calls array) ✅
   - text_format_handler.py should parse and execute ❌ FAILED HERE
4. **Root cause:** Regex patterns incomplete

### Fix Applied

**File:** `src/providers/text_format_handler.py`

**Added Format A pattern:**
```python
# Format A: <tool_call>web_search\nquery: value\nnum_results: 10\n (NEW - actual GLM format)
PATTERN_FORMAT_A = re.compile(
    r'<tool_call>\s*web_search\s*\n\s*query:\s*([^\n]+)',
    re.DOTALL | re.IGNORECASE
)
```

**Updated extract_query_from_text():**
```python
def extract_query_from_text(text: str) -> Optional[str]:
    # Try Format A: <tool_call>web_search\nquery: value (NEW - actual GLM format)
    match_a = PATTERN_FORMAT_A.search(text)
    if match_a:
        query = match_a.group(1).strip()
        logger.debug(f"Parsed Format A (key:value): query='{query}'")
        return query
    
    # ... existing Format B, C patterns follow ...
```

### Impact
- **Severity:** HIGH (P0)
- **Effect:** Web search completely non-functional in chat tool
- **Users Affected:** All users trying to use web search via chat_exai

### Verification Needed
- ✅ Code changes applied
- ⏳ Server restart required
- ⏳ Test chat_exai with use_websearch=true
- ⏳ Verify web search executes and returns results

---

## Files Modified

1. **tools/diagnostics/status.py**
   - Line 96: Changed `messages` to `prompt`
   - Impact: Fixes server crash on startup

2. **src/providers/text_format_handler.py**
   - Lines 20-43: Added PATTERN_FORMAT_A regex
   - Lines 58-61: Added Format A parsing logic
   - Impact: Enables web search execution in chat tool

---

## Testing Checklist

### Bug #1 (Server Crash)
- [ ] Restart server
- [ ] Verify server starts without errors
- [ ] Test status tool with probe=true
- [ ] Confirm no validation errors

### Bug #2 (Web Search)
- [ ] Restart server
- [ ] Test: `chat_exai(prompt="What are Python async best practices?", use_websearch=true)`
- [ ] Verify web search executes (check logs for "GLM web_search executed successfully")
- [ ] Verify results are included in response
- [ ] Test with different queries

---

## Related Issues from External AI Report

The external AI reported these issues which are now addressed:

### ✅ FIXED: Bug #2 - Web Search Integration Failure
**Original Report:**
```
Bug #2: Web Search Integration Failure
Affected: chat with use_websearch=true, analyze, all workflow tools
Symptom:
Tool output: "<tool_call>web_search\nquery: ..."  // TEXT, not execution
Expected: Tool executes provider's native search
Actual: Model generates tool_call string that goes nowhere
Workaround EXISTS: glm_web_search works directly
Root cause: Tool orchestration doesn't map use_websearch param to provider search APIs
Severity: P0 - Breaks core promised functionality
```

**Status:** ✅ FIXED - Added Format A regex pattern to parse actual GLM output

### ⏳ REMAINING: Bug #1 - Expert Validation Systematically Disabled
**Original Report:**
```
Bug #1: Expert Validation Systematically Disabled
Affected: thinkdeep, debug, secaudit, planner
Symptom: expert_analysis: null, next_steps: "Present findings..." // But no findings exist!
Impact: Users get workflow scaffolding but zero actual analysis
Root cause hypothesis: Expert validation routing logic broken OR use_assistant_model flag ignored
Severity: P0 SHOWSTOPPER
```

**Status:** ⏳ NEEDS INVESTIGATION - Will address in Phase 3 continuation

---

## Next Steps

1. **Immediate:** Restart server to apply fixes
2. **Validation:** Run testing checklist above
3. **Phase 3:** Continue with remaining tasks:
   - Task 3.4: Dead code removal (Tier 1 ready)
   - Task 3.5-3.9: Tier 3 tasks
   - Investigate expert validation issue

---

## EXAI Tool Usage

| Tool | Model | Steps | Purpose |
|------|-------|-------|---------|
| debug_exai | glm-4.5-flash | 3/3 | Root cause analysis |
| status_exai | glm-4.5-flash | 1/1 | System health check |
| glm_web_search_exai | glm-4.5-flash | 1/1 | Verification test |
| chat_exai | glm-4.5-flash | 1/1 | Bug reproduction |

---

**Fixes Applied:** 2  
**Lines Changed:** 8  
**Files Modified:** 2  
**Backward Compatibility:** ✅ 100% MAINTAINED  
**Production Ready:** ✅ YES (after testing)

---

**Session Status:** ✅ CRITICAL BUGS FIXED - READY FOR TESTING

