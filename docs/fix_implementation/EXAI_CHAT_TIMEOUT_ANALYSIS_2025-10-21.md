# EXAI Chat Timeout Analysis
**Date:** 2025-10-21  
**Issue:** chat_EXAI-WS calls timing out when using web search  
**Root Cause:** GLM API read timeout insufficient for web search operations

---

## Problem Summary

When calling `chat_EXAI-WS` with `use_websearch=true`, the request times out with:

```
ERROR src.providers.glm_chat: GLM generate_content failed: GLM SDK streaming failed: The read operation timed out
```

This happens because:
1. Web search operations take longer (search + process + generate)
2. Current `GLM_TIMEOUT_SECS=120` (2 minutes) is insufficient
3. The timeout is a **socket read timeout**, not the streaming timeout

---

## Current Configuration

### `.env.docker` Settings

```bash
# Line 278: GLM provider timeout
GLM_TIMEOUT_SECS=120  # 2 minutes - TOO SHORT for web search

# Line 404: GLM streaming timeout
GLM_STREAM_TIMEOUT=300  # 5 minutes - This is fine

# Line 386: Web search specific timeout
GLM_WEBSEARCH_TIMEOUT_SECS=30  # 30 seconds - This is for the search API call itself
```

### How Timeouts Work

1. **`GLM_TIMEOUT_SECS`** (120s) - Socket-level timeout for the entire HTTP request
   - Used by ZhipuAI SDK client initialization
   - Controls how long to wait for ANY response from the API
   - **This is what's timing out**

2. **`GLM_STREAM_TIMEOUT`** (300s) - Application-level streaming timeout
   - Used by `glm_chat.py` to prevent infinite streaming
   - Only applies AFTER the connection is established
   - Not the issue here

3. **`GLM_WEBSEARCH_TIMEOUT_SECS`** (30s) - Web search API timeout
   - Only for the web search API call itself
   - Not relevant to chat completions

---

## Root Cause

The ZhipuAI SDK client is initialized with:

```python
# src/providers/glm.py line 38-41
self._sdk_client = ZhipuAI(
    api_key=self.api_key,
    base_url=self.base_url,
    timeout=TimeoutConfig.GLM_TIMEOUT_SECS,  # 120 seconds
    max_retries=3,
)
```

When `use_websearch=true`, the GLM API:
1. Receives the request
2. Executes web search (10-30 seconds)
3. Processes search results (10-20 seconds)
4. Generates response with thinking mode (30-60 seconds)
5. **Total: 50-110 seconds** (can exceed 120s with retries)

The socket read timeout of 120 seconds is hit before the API finishes processing.

---

## Solution Options

### Option 1: Increase GLM_TIMEOUT_SECS (Recommended)

**Change `.env.docker` line 278:**
```bash
# OLD:
GLM_TIMEOUT_SECS=120  # 2 minutes

# NEW:
GLM_TIMEOUT_SECS=300  # 5 minutes (matches GLM_STREAM_TIMEOUT)
```

**Pros:**
- Simple, one-line change
- Matches existing `GLM_STREAM_TIMEOUT` value
- Allows web search + thinking mode to complete

**Cons:**
- Longer timeout means slower failure detection
- May mask other issues

### Option 2: Adaptive Timeout Based on Web Search (Better)

**Add new env var in `.env.docker`:**
```bash
# Line 282 (after GLM_TIMEOUT_SECS):
GLM_WEB_SEARCH_TIMEOUT_SECS=300  # 5 minutes for web search operations
```

**Update `src/providers/glm_chat.py` to use adaptive timeout:**
```python
# Detect if web search is enabled
has_web_search = any(
    tool.get('type') == 'web_search' 
    for tool in kwargs.get('tools', [])
)

# Use longer timeout for web search
if has_web_search:
    timeout = int(os.getenv("GLM_WEB_SEARCH_TIMEOUT_SECS", "300"))
else:
    timeout = TimeoutConfig.GLM_TIMEOUT_SECS
```

**Pros:**
- Only uses longer timeout when needed
- Faster failure detection for non-web-search calls
- More precise timeout management

**Cons:**
- Requires code changes
- More complex

### Option 3: Disable Web Search by Default (Quick Fix)

**Change `.env.docker` line 11:**
```bash
# OLD:
GLM_ENABLE_WEB_BROWSING=true

# NEW:
GLM_ENABLE_WEB_BROWSING=false
```

**Pros:**
- Immediate fix, no timeout issues
- Can still enable web search per-call with `use_websearch=true`

**Cons:**
- Loses web search capability by default
- Not a real solution, just avoids the problem

---

## Recommended Approach

**Immediate Fix (Option 1):**
1. Change `GLM_TIMEOUT_SECS=120` to `GLM_TIMEOUT_SECS=300` in `.env.docker`
2. Restart Docker container
3. Test chat_EXAI-WS with web search

**Long-term Fix (Option 2):**
1. Implement adaptive timeout based on web search detection
2. Add `GLM_WEB_SEARCH_TIMEOUT_SECS` env var
3. Update documentation

---

## Testing Plan

After implementing the fix:

1. **Test web search with thinking mode:**
   ```python
   chat_EXAI-WS(
       prompt="What are the latest developments in TensorRT-LLM?",
       model="glm-4.6",
       use_websearch=True,
       thinking_mode="high"
   )
   ```

2. **Test without web search:**
   ```python
   chat_EXAI-WS(
       prompt="Explain async/await in Python",
       model="glm-4.6",
       use_websearch=False
   )
   ```

3. **Monitor Docker logs:**
   ```bash
   docker logs exai-mcp-daemon --tail 100 -f
   ```

4. **Verify no timeout errors:**
   - Should see successful completion
   - No "read operation timed out" errors
   - Response includes web search results

---

## Related Issues

1. **EXAI Tools Assessment** - This timeout issue prevented comprehensive testing of EXAI tools with web search enabled
2. **Expert Analysis** - Similar timeout issues may affect workflow tools with `use_assistant_model=true`
3. **Thinking Mode** - High thinking modes may also need longer timeouts

---

## Next Steps

1. ✅ Implement immediate fix (increase GLM_TIMEOUT_SECS to 300)
2. ⏳ Test with web search enabled
3. ⏳ Implement adaptive timeout (long-term fix)
4. ⏳ Update EXAI tools assessment with web search results
5. ⏳ Document timeout configuration in user guide

---

## Files to Modify

### Immediate Fix:
- `.env.docker` (line 278)

### Long-term Fix:
- `.env.docker` (add GLM_WEB_SEARCH_TIMEOUT_SECS)
- `src/providers/glm_chat.py` (adaptive timeout logic)
- `config.py` (add GLM_WEB_SEARCH_TIMEOUT_SECS to TimeoutConfig)
- `docs/04_GUIDES/guides/TIMEOUT_CONFIGURATION_GUIDE.md` (document new setting)

