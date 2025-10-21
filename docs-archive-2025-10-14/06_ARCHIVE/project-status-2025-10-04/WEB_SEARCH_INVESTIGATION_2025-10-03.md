# Web Search Investigation Report - 2025-10-03
## Native Provider Web Search Not Working - Root Cause Analysis

**Date:** 2025-10-03
**Status:** 🔍 INVESTIGATION IN PROGRESS
**Priority:** CRITICAL

---

## 🎯 Problem Statement

**Issue:** Both GLM and Kimi providers are NOT using their native web search capabilities. Instead, the system falls back to client-side DuckDuckGo search.

**Expected Behavior:**
- GLM: Should use native `web_search` tool (search executed by GLM API)
- Kimi: Should use `$web_search` builtin function (search executed by Kimi API)

**Actual Behavior:**
- GLM: Returns raw tool call text in content: `<tool_call>web_search...`
- Kimi: Unknown (needs testing)
- System falls back to DuckDuckGo client-side search

---

## 🔍 Investigation Findings

### 1. Configuration is Correct ✅

**Environment Variables:**
```bash
GLM_ENABLE_WEB_BROWSING=true
KIMI_ENABLE_INTERNET_SEARCH=true
```

**GLM Tool Schema** (`src/providers/capabilities.py` line 72-79):
```python
web_search_config = {
    "search_engine": "search_pro_jina",
    "search_recency_filter": "oneWeek",
    "content_size": "medium",
    "result_sequence": "after",
    "search_result": True,
}
tools = [{"type": "web_search", "web_search": web_search_config}]
```

**Kimi Tool Schema** (`src/providers/capabilities.py` line 52-55):
```python
tools = [{
    "type": "builtin_function",
    "function": {"name": "$web_search"}
}]
```

### 2. Tool Injection is Working ✅

**Code Path:**
1. `tools/simple/base.py` line 501-507: Calls `build_websearch_provider_kwargs()`
2. `src/providers/orchestration/websearch_adapter.py` line 25-30: Builds tool schema
3. `tools/simple/base.py` line 534, 575: Passes `**provider_kwargs` to `generate_content()`

**Verification:**
- `provider_kwargs` contains `{"tools": [...], "tool_choice": "auto"}`
- Tools are being passed to provider's `generate_content()` method

### 3. Provider Implementation is Correct ✅

**GLM** (`src/providers/glm_chat.py` line 51-58):
```python
tools = kwargs.get("tools")
if tools:
    payload["tools"] = tools
tool_choice = kwargs.get("tool_choice")
if tool_choice:
    payload["tool_choice"] = tool_choice
```

**Kimi** (`src/providers/kimi_chat.py` line 112-119):
```python
# Sanitize tools/tool_choice per Moonshot tool-use
if tools is not None and not tools:
    tools = None
if not tools:
    tool_choice = None
```

Both providers correctly pass tools to the API.

### 4. Response Handling is BROKEN ❌

**GLM Issue:**
- **Before Fix:** Only extracted `message.content`, ignored `message.tool_calls`
- **After Fix:** Added tool_calls extraction (lines 180-198, 272-285)
- **Current Problem:** GLM returns tool call as TEXT in content, not in tool_calls field

**Example Response:**
```json
{
  "content": "<tool_call>web_search\n<think>query\n<arg_value>current Bitcoin price USD today live\n</tool_call>"
}
```

**This means GLM is NOT executing the web search - it's just describing what it would do!**

**Kimi Issue:**
- Kimi already extracts `tool_calls` (line 217-236)
- Returns `tool_calls` in response dict (line 242)
- **Unknown:** Whether Kimi actually executes web search or returns text like GLM

---

## 🚨 Root Cause Analysis

### Hypothesis 1: GLM API Not Configured Correctly
**Likelihood:** HIGH

**Evidence:**
- GLM returns tool call as text instead of executing it
- This suggests GLM API is not recognizing the web_search tool
- Possible issues:
  1. Wrong tool schema format
  2. Missing API parameter
  3. Model doesn't support web_search
  4. API endpoint issue

**Next Steps:**
1. Check GLM official documentation for web_search tool format
2. Test with minimal example directly to GLM API
3. Verify model supports web_search (glm-4.5-flash, glm-4.6)
4. Check if web_search requires specific API endpoint

### Hypothesis 2: Tool Choice Configuration Issue
**Likelihood:** MEDIUM

**Evidence:**
- We set `tool_choice="auto"`
- GLM might require explicit tool_choice or different value
- Possible values: "auto", "required", "none", specific tool name

**Next Steps:**
1. Try `tool_choice="required"`
2. Try explicit tool name: `tool_choice={"type": "web_search"}`
3. Test without tool_choice parameter

### Hypothesis 3: Model Limitation
**Likelihood:** LOW

**Evidence:**
- glm-4.5-flash might not support web_search
- Only certain models might have web search capability

**Next Steps:**
1. Test with glm-4.6 instead of glm-4.5-flash
2. Check GLM documentation for model capabilities

---

## 🔧 Fixes Applied

### Fix #1: GLM Tool Calls Extraction ✅ PARTIAL

**File:** `src/providers/glm_chat.py`
**Lines:** 180-198 (SDK path), 272-285 (HTTP path)

**What Was Fixed:**
- Added extraction of `message.tool_calls` from response
- Parse web_search results from tool_calls
- Append results to content

**Status:** ✅ Code is correct, but GLM not returning tool_calls

**Impact:** Will work once GLM actually executes web search

---

## 📋 Next Steps

### Immediate (HIGH Priority)
1. ❌ **Test GLM web search with official example**
   - Use GLM SDK directly
   - Verify tool schema format
   - Check if web_search actually works

2. ❌ **Test Kimi web search**
   - Verify $web_search builtin function works
   - Check if Kimi returns tool_calls or text

3. ❌ **Review GLM/Kimi documentation**
   - Find official web search examples
   - Verify correct tool schema format
   - Check model compatibility

### Investigation (MEDIUM Priority)
4. ❌ **Add debug logging**
   - Log exact payload sent to GLM/Kimi
   - Log exact response received
   - Verify tools are in request

5. ❌ **Test different configurations**
   - Try tool_choice="required"
   - Try different models
   - Try different tool schemas

### Documentation (LOW Priority)
6. ❌ **Update documentation**
   - Document correct web search configuration
   - Add troubleshooting guide
   - Update architecture docs

---

## 📊 Testing Results

### Test #1: GLM Web Search with glm-4.5-flash
**Command:**
```python
chat_EXAI-WS(
    prompt="What is the current price of Bitcoin? Please search the web.",
    model="glm-4.5-flash",
    use_websearch=true
)
```

**Result:** ❌ FAIL
```
Content: "<tool_call>web_search\n<think>query\n<arg_value>current Bitcoin price USD today live\n</tool_call>"
```

**Analysis:**
- GLM returned tool call as text
- Web search NOT executed
- Fallback to DuckDuckGo would occur

### Test #2: Kimi Web Search
**Status:** ⏳ PENDING

### Test #3: GLM with Different Model
**Status:** ⏳ PENDING

---

## 🎯 Success Criteria

**Web search is working when:**
1. ✅ GLM executes web_search and returns actual search results
2. ✅ Kimi executes $web_search and returns actual search results
3. ✅ No fallback to DuckDuckGo occurs
4. ✅ Search results are properly formatted in response
5. ✅ Both SDK and HTTP paths work correctly

---

**Last Updated:** 2025-10-03 21:40
**Status:** 🔍 INVESTIGATION IN PROGRESS - Root cause identified, testing solutions

