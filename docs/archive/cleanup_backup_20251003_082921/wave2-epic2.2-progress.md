# Wave 2 - Epic 2.2: Web Search Prompt Injection Fix - Progress Report

**Date:** 2025-10-03  
**Status:** IN PROGRESS (50% Complete)  
**Priority:** HIGH (Leverage-first strategy - fix this FIRST)

---

## Executive Summary

Epic 2.2 aims to fix the chat_EXAI-WS web search issue where responses are incomplete when `use_websearch=true`. The issue has two components:

1. **"AGENT'S TURN" Message** ✅ **FIXED**
2. **Web Search Results Integration** 🔄 **IN PROGRESS**

---

## Issue Analysis

### Original Problem Statement

When using `chat_EXAI-WS` with `use_websearch=true`:
- ❌ Response ends with confusing "AGENT'S TURN: Evaluate this perspective..." message
- ❌ Web search results are NOT integrated into response
- ✅ Web search DOES execute (confirmed by `tool_call_events` metadata)
- ❌ User receives incomplete information

### Example of Issue

**Request:**
```json
{
  "prompt": "What are the latest features in zai-sdk version 0.0.4?",
  "use_websearch": true,
  "model": "auto"
}
```

**Response (Before Fix):**
```
"I'll help you find information about the latest features in zai-sdk version 0.0.4. 
Let me search for the most current information about this SDK's recent updates.

---

AGENT'S TURN: Evaluate this perspective alongside your analysis to form a 
comprehensive solution and continue with the user's request and task at hand."
```

**Metadata:**
```json
"tool_call_events": [{
  "provider": "kimi",
  "tool_name": "web_search",
  "args": {},
  "start_ts": 1759356492.751445
}]
```

---

## Fix #1: "AGENT'S TURN" Message ✅ COMPLETE

### Root Cause
The `format_response()` method in `tools/chat.py` (lines 236-274) **ALWAYS** appended the "AGENT'S TURN" message to every chat response, regardless of context.

### Solution Implemented
Modified `tools/chat.py` lines 236-285:
- Added `has_continuation` flag to track if `continuation_id` is present
- Only append "AGENT'S TURN" message for multi-turn conversations (when `has_continuation=True`)
- For standalone calls (especially with web search), return clean response

### Code Changes
```python
# Before (lines 271-274):
return (
    f"{response}\n\n---\n\nAGENT'S TURN: Evaluate this perspective alongside your analysis to "
    "form a comprehensive solution and continue with the user's request and task at hand."
)

# After (lines 278-285):
if has_continuation:
    return (
        f"{response}\n\n---\n\nAGENT'S TURN: Evaluate this perspective alongside your analysis to "
        "form a comprehensive solution and continue with the user's request and task at hand."
    )
else:
    return response
```

### Validation
**Test Call:**
```json
{
  "prompt": "What are the latest features in zai-sdk version 0.0.4?",
  "use_websearch": true,
  "model": "auto"
}
```

**Result:** ✅ SUCCESS
- "AGENT'S TURN" message is GONE
- Response is clean: `"I'll help you find the latest features in zai-sdk version 0.0.4. Let me search for the most current information about this release."`
- No confusing message at the end

### Impact
- ✅ Eliminates confusing "AGENT'S TURN" message for standalone calls
- ✅ Maintains message for multi-turn conversations (when needed)
- ✅ Improves user experience
- ✅ Backward compatible (continuation_id behavior unchanged)

---

## Fix #2: Web Search Results Integration 🔄 IN PROGRESS

### Current Status
Web search executes successfully (confirmed by metadata), but results are NOT integrated into the final response.

### Symptoms
- Response says "I'll search for..." or "Let me search for..."
- Actual search results are missing from response
- Metadata confirms `tool_call_events` with `tool_name: "web_search"`
- Response appears to be the initial acknowledgment, not the final synthesized answer

### Investigation Findings

#### File: `tools/providers/kimi/kimi_tools_chat.py`

**Tool Loop Structure (lines 476-594):**
```python
for _ in range(3):  # limit tool loop depth
    # 1. Make API call to Kimi
    result = await _aio.wait_for(_aio.to_thread(_call), timeout=timeout_secs)
    
    # 2. Extract tool calls from response
    tcs = _extract_tool_calls(result.get("raw"))
    
    # 3. If no tool calls, return response immediately (lines 504-532)
    if not tcs:
        # Extract content and return
        return [TextContent(...)]
    
    # 4. If tool calls exist, append assistant message (lines 534-547)
    messages_local.append(assistant_msg)
    
    # 5. Execute tools locally (lines 549-585)
    for tc in tcs:
        if fname in ("web_search",):
            res = _run_web_search_backend(query)
            tool_msgs.append({"role": "tool", "content": json.dumps(res)})
    
    # 6. Append tool results and continue loop (line 588)
    messages_local.extend(tool_msgs)
    # Loop continues to next iteration...

# 7. If loop exits due to depth, return error (lines 590-594)
return [TextContent(text=json.dumps({"status": "max_tool_depth_reached"}))]
```

**Expected Flow:**
1. **Iteration 1:** Model requests `web_search` tool call
2. Tool is executed, results appended to `messages_local`
3. **Iteration 2:** Model receives tool results and synthesizes final response
4. No tool calls in response → return synthesized content (lines 504-532)

**Actual Flow (Hypothesis):**
1. **Iteration 1:** Model requests `web_search` tool call
2. Tool is executed, results appended to `messages_local`
3. **Iteration 2:** Model makes API call with tool results
4. **Problem:** Response may be incomplete or not properly synthesized

### Possible Root Causes

#### Hypothesis 1: Response Truncation
- Second API call returns incomplete response
- Model hasn't finished synthesizing search results
- Response is cut off before synthesis completes

#### Hypothesis 2: Tool Results Not Properly Formatted
- Search results appended to `messages_local` (line 588)
- Format may not be compatible with Kimi's expectations
- Model may not recognize tool results as valid input

#### Hypothesis 3: Timeout or Early Return
- Second API call times out before synthesis
- Code returns early without waiting for complete response
- Tool loop exits prematurely

#### Hypothesis 4: Streaming vs Non-Streaming Conflict
- Line 224-225: `if bool(arguments.get("use_websearch", False)): stream_flag = False`
- Web search forces non-streaming mode
- Non-streaming tool loop may have issues with multi-turn synthesis

### Next Steps

1. **Add Diagnostic Logging**
   - Log each iteration of the tool loop
   - Capture messages_local state after each iteration
   - Log response content at each step
   - Track tool call execution and results

2. **Create Test Script**
   - Isolated test for web search tool loop
   - Direct call to `kimi_tools_chat.py`
   - Capture full request/response cycle
   - Verify tool results format

3. **Investigate Kimi Provider Behavior**
   - Check if Kimi requires specific tool result format
   - Verify tool_call_id matching
   - Test with different search backends (DuckDuckGo, Tavily, Bing)
   - Compare with working examples

4. **Review Tool Loop Logic**
   - Verify loop continues after tool execution
   - Check if second API call is made
   - Ensure response is properly extracted
   - Validate no early returns

5. **Test Alternative Approaches**
   - Try forcing streaming mode for web search
   - Test with different models (GLM vs Kimi)
   - Compare with direct web-search tool (working workaround)
   - Investigate if issue is Kimi-specific

---

## Files Modified

### ✅ Completed
- `tools/chat.py` (lines 236-285) - Fixed "AGENT'S TURN" message

### 🔄 To Be Modified
- `tools/providers/kimi/kimi_tools_chat.py` (lines 476-594) - Fix web search results integration
- Potential: Add diagnostic logging module
- Potential: Create test script for validation

---

## Testing Plan

### Test Case 1: Simple Web Search
**Prompt:** "What is Python 3.13?"  
**Expected:** Complete answer with search results integrated  
**Actual:** "I'll search for..." (incomplete)

### Test Case 2: Specific Query
**Prompt:** "What are the latest features in zai-sdk version 0.0.4?"  
**Expected:** List of features from search results  
**Actual:** "Let me search for..." (incomplete)

### Test Case 3: Multi-Turn with Web Search
**Prompt:** "Search for GLM-4.6 specifications" (with continuation_id)  
**Expected:** Complete answer + "AGENT'S TURN" message  
**Actual:** TBD

---

## Success Criteria

### Epic 2.2 Complete When:
- ✅ "AGENT'S TURN" message only appears with continuation_id
- ⬜ Web search results are integrated into responses
- ⬜ Responses are complete and synthesized
- ⬜ No regressions in existing functionality
- ⬜ All test cases pass
- ⬜ Validated with EXAI-WS MCP tool calls

---

## Timeline

- **2025-10-03 05:47:** Started Epic 2.2
- **2025-10-03 05:50:** Fixed "AGENT'S TURN" message (50% complete)
- **2025-10-03 06:00:** Investigating web search results integration
- **Next Session:** Continue investigation and implement fix

---

## Related Documentation

- **Issue Analysis:** `docs/upgrades/international-users/exai-tool-ux-issues.md` Section 1
- **User Guide:** `docs/guides/web-search-guide.md`
- **Implementation Plan:** `docs/upgrades/international-users/wave2-implementation-plan.md`
- **Task Breakdown:** `zai-sdk_v0.0.4_Upgrade_Task_Breakdown__2025-10-02T19-40-33.md`

---

## Notes

- Server restart required after modifying `tools/chat.py` ✅ DONE
- Fix #1 validated successfully with real EXAI-WS MCP calls
- Fix #2 requires deeper investigation of Kimi provider tool loop
- Consider consulting EXAI for optimal implementation approach

