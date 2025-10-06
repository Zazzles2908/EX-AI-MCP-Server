# Web Search Implementation Audit

**Date:** 2025-10-03  
**Status:** Issues identified, fixes needed

---

## Issues Found

### 1. ✅ Base URLs - FIXED (by user)

**GLM_API_URL:**
- ❌ Was: `https://open.bigmodel.cn/api/paas/v4` (China endpoint)
- ✅ Now: `https://api.z.ai/api/paas/v4/` (International endpoint)

**Endpoints:**
- Chat: `https://api.z.ai/api/paas/v4/chat/completions` ✅
- Web Search: `https://api.z.ai/api/paas/v4/web_search` ✅
- Files: `https://api.z.ai/api/paas/v4/files` ✅
- Async Result: `https://api.z.ai/api/v1/agents/async-result` (different base!)
- Conversation: `https://api.z.ai/api/v1/agents/conversation` (different base!)
- Videos: `https://api.z.ai/api/paas/v4/videos/generations` ✅

**KIMI_API_URL:**
- ✅ Correct: `https://api.moonshot.ai/v1`

---

### 2. ❌ Tool Call Loop - BROKEN

**Current Implementation:**
```python
# tools/simple/base.py, lines 661-745
if tool_calls_list:
    # Execute tools ONCE
    # Send results back
    # Get final response
    # DONE - NO LOOP!
```

**Problem:** Only executes tool calls **ONCE**. Doesn't loop until `finish_reason != "tool_calls"`.

**Kimi Documentation Says:**
```python
while finish_reason is None or finish_reason == "tool_calls":
    choice = chat(messages)
    finish_reason = choice.finish_reason
    if finish_reason == "tool_calls":
        messages.append(choice.message)  # Add assistant message
        for tool_call in choice.message.tool_calls:
            # Execute tool
            # Add tool result to messages
        # LOOP AGAIN!
```

**What We're Missing:**
1. No loop - only one iteration
2. Not checking `finish_reason == "tool_calls"`
3. Not continuing until model is satisfied

---

### 3. ❌ Search Implementation - MISSING

**Current Code:**
```python
if tc.get("type") == "builtin_function":
    # Just acknowledge with empty result
    tool_msg = {
        "role": "tool",
        "tool_call_id": str(tc.get("id", "tc-0")),
        "content": json.dumps({"status": "executed_server_side"})
    }
```

**Problem:** We're not implementing `search_impl(tool_call_arguments)`!

**Kimi Documentation Says:**
```python
if tool_call_name == "$web_search":
    tool_result = search_impl(tool_call_arguments)  # ← WE DON'T HAVE THIS!
else:
    tool_result = f"Error: unable to find tool by name '{tool_call_name}'"

messages.append({
    "role": "tool",
    "tool_call_id": tool_call.id,
    "name": tool_call_name,
    "content": json.dumps(tool_result),  # ← Actual search results!
})
```

**What We Need:**
- Implement `search_impl()` function
- Actually execute the search
- Return real search results
- Include them in tool message

---

### 4. ❌ Model Configuration - INCONSISTENT

**Current .env:**
```env
DEFAULT_MODEL=glm-4.6
GLM_QUALITY_MODEL=glm-4.6
GLM_SPEED_MODEL=glm-4.5-flash
KIMI_QUALITY_MODEL=kimi-thinking-preview
KIMI_SPEED_MODEL=kimi-k2-0905-preview
GLM_COMPLEX_MODEL=glm-4.6
```

**Questions:**
1. Which model is used for chat tool by default?
2. Which model is used when `model="auto"`?
3. Are these variables actually used in the code?

**Need to verify:**
- Where are these variables referenced?
- What's the actual model selection logic?
- Is there a mismatch between env vars and code?

---

## Root Cause Summary

**Why Web Search Fails:**

1. ✅ **Base URL** - Fixed (was pointing to China endpoint)
2. ❌ **Tool Call Loop** - Missing (only one iteration, no loop)
3. ❌ **Search Implementation** - Missing (`search_impl` not implemented)
4. ❌ **Result Injection** - Wrong (empty acknowledgment instead of real results)

**The Flow Should Be:**

```
1. User: "What is Kimi K2 pricing?"
2. Model: tool_calls=[{type: "builtin_function", name: "$web_search", args: {...}}]
3. We: Execute search_impl(args) → Get real search results
4. We: Send tool message with REAL results
5. Model: Checks finish_reason
6. IF finish_reason == "tool_calls": LOOP to step 2
7. ELSE: Return final response with search data
```

**What We're Doing:**

```
1. User: "What is Kimi K2 pricing?"
2. Model: tool_calls=[{type: "builtin_function", name: "$web_search"}]
3. We: Send {"status": "executed_server_side"} ← EMPTY!
4. Model: Returns response (no search data, hallucinates)
5. DONE - NO LOOP!
```

---

## Fix Plan

### Fix 1: Implement Tool Call Loop

**File:** `tools/simple/base.py`  
**Lines:** 661-745

**Change:**
```python
# Current: Single iteration
if tool_calls_list:
    # Execute once
    # Get response
    # Done

# New: Loop until finish_reason != "tool_calls"
max_iterations = 5  # Prevent infinite loops
iteration = 0

while iteration < max_iterations:
    iteration += 1
    
    # Check for tool calls
    tool_calls_list = extract_tool_calls(raw_response)
    
    if not tool_calls_list:
        break  # No more tool calls, we're done
    
    # Execute tools
    for tc in tool_calls_list:
        # Execute and add to messages
    
    # Call model again with tool results
    response = provider.chat_completions_create(...)
    
    # Check finish_reason
    finish_reason = response.get("choices", [{}])[0].get("finish_reason")
    if finish_reason != "tool_calls":
        break  # Model is satisfied
```

### Fix 2: Implement search_impl

**File:** `src/providers/tool_executor.py` or new file  
**Function:** `search_impl(arguments: dict) -> dict`

**Implementation:**
```python
def search_impl(arguments: dict) -> dict:
    """
    Execute web search using DuckDuckGo or configured backend.
    
    Args:
        arguments: Search arguments from tool_call
        
    Returns:
        Search results dict
    """
    query = arguments.get("query", "")
    if not query:
        return {"error": "No query provided"}
    
    # Use existing run_web_search_backend
    from src.providers.tool_executor import run_web_search_backend
    return run_web_search_backend(query)
```

### Fix 3: Use Real Search Results

**File:** `tools/simple/base.py`  
**Lines:** 684-695

**Change:**
```python
# Current
if tc.get("type") == "builtin_function":
    tool_msg = {
        "role": "tool",
        "tool_call_id": str(tc.get("id", "tc-0")),
        "content": json.dumps({"status": "executed_server_side"})
    }

# New
if tc.get("type") == "builtin_function":
    func_name = tc.get("function", {}).get("name", "unknown")
    
    if func_name == "$web_search":
        # Execute search
        args_raw = tc.get("function", {}).get("arguments", "{}")
        if isinstance(args_raw, str):
            args = json.loads(args_raw)
        else:
            args = args_raw
        
        # Get real search results
        search_results = search_impl(args)
        
        tool_msg = {
            "role": "tool",
            "tool_call_id": str(tc.get("id", "tc-0")),
            "name": func_name,
            "content": json.dumps(search_results, ensure_ascii=False)
        }
    else:
        # Unknown builtin function
        tool_msg = {
            "role": "tool",
            "tool_call_id": str(tc.get("id", "tc-0")),
            "content": json.dumps({"error": f"Unknown builtin: {func_name}"})
        }
```

### Fix 4: Verify Model Variables

**Files to check:**
- `src/providers/registry.py`
- `src/providers/registry_selection.py`
- `tools/simple/base.py`

**Questions to answer:**
1. Where is `DEFAULT_MODEL` used?
2. Where is `GLM_QUALITY_MODEL` used?
3. What happens when `model="auto"`?
4. Are all env variables actually referenced?

---

## Testing Plan

### Test 1: Kimi Pricing Query
```python
result = chat(
    prompt="What is the current pricing for Kimi K2?",
    model="kimi-k2-0905-preview",
    use_websearch=True
)

# Expected: $0.15/M input, $2.50/M output
# Should NOT be: $12/M
```

### Test 2: GLM Pricing Query
```python
result = chat(
    prompt="What is the current pricing for GLM-4.5?",
    model="glm-4.5",
    use_websearch=True
)

# Expected: Correct pricing from api.z.ai
# Should NOT be: ¥20/M (China pricing)
```

### Test 3: Tool Call Loop
```python
# Monitor logs for:
# - "Tool call iteration 1"
# - "Tool call iteration 2" (if needed)
# - "finish_reason: stop" (final)
```

---

## Priority

1. **HIGH**: Implement tool call loop (Fix 1)
2. **HIGH**: Implement search_impl (Fix 2)
3. **HIGH**: Use real search results (Fix 3)
4. **MEDIUM**: Verify model variables (Fix 4)

---

**Next Steps:**
1. Implement fixes 1-3
2. Test with pricing queries
3. Verify no regressions
4. Audit model variable usage

