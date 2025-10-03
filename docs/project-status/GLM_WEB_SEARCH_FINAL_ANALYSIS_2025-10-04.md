# GLM Web Search Final Analysis & Resolution
**Date:** 2025-10-04  
**Status:** CRITICAL FIX IMPLEMENTED - TESTING REQUIRED  
**Priority:** HIGH

---

## 🎯 EXECUTIVE SUMMARY

**ROOT CAUSE IDENTIFIED:** The ZhipuAI SDK was not receiving the `base_url` parameter, causing it to use the hardcoded default endpoint `https://open.bigmodel.cn` instead of the configured z.ai proxy `https://api.z.ai/api/paas/v4/`.

**FIX IMPLEMENTED:** Modified `src/providers/glm.py` line 36 to pass `base_url` to the SDK constructor.

**CURRENT STATUS:** Fix deployed, server restarted, awaiting comprehensive testing.

---

## 📊 INVESTIGATION TIMELINE

### Phase 1: Initial Diagnosis (INCORRECT)
- **Finding:** GLM web search appeared to work inconsistently
- **Test Results:** 
  - Bitcoin price (glm-4.6): ✅ SUCCESS
  - Tokyo weather (glm-4.5-flash): ❌ FAILED (returned tool call as text)
  - SpaceX news (glm-4.6): ❌ FAILED (acknowledgment only)
- **Initial Hypothesis:** `tool_choice="auto"` allows GLM to decide whether to execute
- **Action Taken:** Changed `tool_choice` to `"required"` in `src/providers/capabilities.py`
- **Result:** **MADE IT WORSE** - GLM returned different text format

### Phase 2: User Challenge & Deep Investigation
- **User Observation:** "You're seeing `bigmodel.cn` in logs, not `z.ai`"
- **Critical Finding:** Log analysis revealed:
  ```
  Line 202: httpcore.connection - DEBUG - connect_tcp.started host='open.bigmodel.cn'
  Line 212: httpx - INFO - HTTP Request: POST https://open.bigmodel.cn/api/paas/v4/chat/completions
  ```
- **Expected:** Should be using `https://api.z.ai/api/paas/v4/` from `.env`
- **Root Cause:** SDK initialization missing `base_url` parameter

### Phase 3: Fix Implementation
- **File:** `src/providers/glm.py`
- **Line:** 36
- **Change:**
  ```python
  # BEFORE (BROKEN):
  self._sdk_client = ZhipuAI(api_key=self.api_key)
  
  # AFTER (FIXED):
  self._sdk_client = ZhipuAI(api_key=self.api_key, base_url=self.base_url)
  ```
- **Reverted:** `tool_choice="required"` back to `"auto"` in `src/providers/capabilities.py`

---

## 🔍 TECHNICAL DETAILS

### The Problem

**Configuration:**
```env
GLM_API_URL=https://api.z.ai/api/paas/v4/
```

**Code Flow:**
1. `GLMModelProvider.__init__()` sets `self.base_url = "https://api.z.ai/api/paas/v4/"`
2. SDK initialization: `ZhipuAI(api_key=self.api_key)` ❌ **Missing base_url!**
3. SDK uses hardcoded default: `https://open.bigmodel.cn`
4. HTTP client (fallback) correctly uses `self.base_url` ✅

**Result:** SDK path uses wrong endpoint, HTTP fallback uses correct endpoint.

### Why This Caused Inconsistent Behavior

1. **SDK Path (Primary):** Hits `bigmodel.cn` → unpredictable web search behavior
2. **HTTP Fallback:** Hits `z.ai` → correct behavior (but rarely used)
3. **Model Differences:** glm-4.6 vs glm-4.5-flash may have different web search support
4. **Endpoint Differences:** `bigmodel.cn` vs `z.ai` may have different API implementations

### GLM Web Search Response Formats Observed

**Format A (Proper - Working):**
```json
{
  "message": {
    "tool_calls": [
      {
        "function": {
          "name": "web_search",
          "arguments": "{\"results\": [...]}"
        }
      }
    ]
  }
}
```

**Format B (Text - Broken):**
```
<tool_call>web_search
<think>query
<arg_value>current Bitcoin price USD
</tool_call>
```

**Format C (JSON Text - Broken):**
```
<tool_code>
{"name": "web_search", "parameters": {"query": "Ethereum price USD current live"}}
</tool_code>
```

**Format D (Acknowledgment Only - Broken):**
```
I'll search for the current temperature in London to provide you with real-time weather data.
```

---

## ✅ FIX VALIDATION

### Files Modified

1. **`src/providers/glm.py`** (Line 36)
   - Added `base_url=self.base_url` to SDK initialization
   - Ensures SDK uses configured endpoint instead of hardcoded default

2. **`src/providers/capabilities.py`** (Lines 79-81)
   - Reverted `tool_choice="required"` back to `"auto"`
   - Original setting was correct

3. **`src/providers/glm_chat.py`** (Lines 180-212)
   - Added debug logging to track response formats
   - Added warning when tool call returned as text
   - Prepared for future text format handler implementation

### Server Status
- ✅ Server restarted successfully
- ✅ WebSocket daemon listening on `ws://127.0.0.1:8765`
- ⏳ Awaiting comprehensive testing

---

## 🧪 TESTING REQUIRED

### Test Plan

**Test 1: Verify Correct Endpoint Usage**
```bash
# Check logs for api.z.ai instead of bigmodel.cn
tail -f logs/mcp_server.log.1 | grep -E "api\.z\.ai|bigmodel\.cn"
```

**Test 2: GLM-4.6 Web Search**
```python
chat_EXAI-WS(
    prompt="What is the current price of Bitcoin in USD? Use web search.",
    model="glm-4.6",
    use_websearch=true
)
```
**Expected:** Proper tool_calls array with search results

**Test 3: GLM-4.5-Flash Web Search**
```python
chat_EXAI-WS(
    prompt="What is the weather in Tokyo? Use web search.",
    model="glm-4.5-flash",
    use_websearch=true
)
```
**Expected:** Proper tool_calls array with search results

**Test 4: Multiple Consecutive Searches**
- Run 5-10 web search requests
- Verify consistency rate
- Check for any text format responses

**Test 5: Debug Log Verification**
```bash
# Check for debug messages
grep "GLM response format" logs/mcp_server.log.1
grep "GLM web_search executed successfully" logs/mcp_server.log.1
grep "GLM returned tool call as TEXT" logs/mcp_server.log.1
```

---

## 📋 NEXT STEPS

### Immediate (HIGH PRIORITY)
1. ✅ **DONE:** Implement base_url fix
2. ✅ **DONE:** Add debug logging
3. ⏳ **TODO:** Run comprehensive test suite
4. ⏳ **TODO:** Verify logs show `api.z.ai` instead of `bigmodel.cn`
5. ⏳ **TODO:** Document test results

### Short-Term (MEDIUM PRIORITY)
1. **If Fix Works:**
   - Update `WEB_SEARCH_TEST_RESULTS_2025-10-03.md` with success
   - Update `ARCHITECTURE_AUDIT_CRITICAL.md` to mark as RESOLVED
   - Update `FIXES_CHECKLIST.md` to mark as ✅ FIXED
   - Remove GLM web search from issues list

2. **If Fix Fails:**
   - Implement text format handler for Formats B, C, D
   - Consider restricting web_search to glm-4.6 only
   - Evaluate disabling GLM web search entirely

### Long-Term (LOW PRIORITY)
1. Add integration tests for web search
2. Monitor web search reliability metrics
3. Consider implementing retry logic for failed searches
4. Evaluate provider-native vs fallback search quality

---

## 🚨 KNOWN ISSUES

### Issue 1: Text Format Responses
**Status:** MONITORING  
**Description:** GLM sometimes returns tool calls as text instead of executing them  
**Formats:** B, C, D (see above)  
**Mitigation:** Debug logging added to track occurrences  
**Next Step:** Implement text format handler if issue persists after endpoint fix

### Issue 2: Model-Specific Behavior
**Status:** INVESTIGATING  
**Description:** glm-4.5-flash may not support web_search execution  
**Evidence:** All glm-4.5-flash tests failed, glm-4.6 had mixed results  
**Next Step:** Test both models after endpoint fix

### Issue 3: Auto-Routing to Kimi
**Status:** CONFIRMED WORKING  
**Description:** System auto-routes some web search requests to Kimi  
**Impact:** Positive - Kimi web search works perfectly  
**Action:** Document as intended behavior

---

## 📝 LESSONS LEARNED

1. **Always Check Logs First:** User's observation about `bigmodel.cn` in logs was the key to solving this
2. **SDK Initialization Matters:** Missing parameters in SDK constructors can cause subtle bugs
3. **Don't Jump to Conclusions:** Initial hypothesis about `tool_choice` was wrong
4. **Test Thoroughly:** One successful test doesn't mean the system works consistently
5. **Debug Logging is Essential:** Added logging will help diagnose future issues

---

## 🔗 RELATED DOCUMENTS

- `docs/project-status/GLM_WEB_SEARCH_ANOMALY_INVESTIGATION.md` - Initial investigation
- `docs/project-status/WEB_SEARCH_TEST_RESULTS_2025-10-03.md` - Test results
- `docs/project-status/ARCHITECTURE_AUDIT_CRITICAL.md` - Critical issues tracker
- `docs/project-status/FIXES_CHECKLIST.md` - Fix tracking

---

## ✍️ AUTHOR NOTES

This was a perfect example of why systematic investigation and log analysis are critical. The user's challenge to "read logs and backtrace" led directly to finding the root cause. The fix is simple (one parameter), but the impact is significant - it affects all GLM web search functionality.

**Confidence Level:** HIGH that this fixes the endpoint issue  
**Confidence Level:** MEDIUM that this fixes all web search issues  
**Recommendation:** Comprehensive testing required before marking as fully resolved

