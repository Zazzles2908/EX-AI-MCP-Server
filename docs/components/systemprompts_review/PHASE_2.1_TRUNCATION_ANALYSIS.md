# Phase 2.1: Truncated EXAI Responses - Root Cause Analysis

**Created:** 2025-10-21  
**Status:** Investigation Complete - Fix Required

---

## Root Cause Identified

### ❌ **Critical Issue: Missing max_tokens in Kimi API Calls**

**Evidence:**

1. **kimi_chat.py** (lines 152-160):
```python
api_params = {
    "model": model,
    "messages": messages,
    "tools": tools,
    "tool_choice": tool_choice,
    "temperature": temperature,
    "stream": False,
    "extra_headers": extra_headers,
}
# ❌ NO max_tokens parameter!
```

2. **async_kimi_chat.py** (lines 91-99):
```python
response = await client.chat.completions.create(
    model=model,
    messages=messages,
    tools=tools,
    tool_choice=tool_choice,
    temperature=temperature,
    stream=False,
    extra_headers=extra_headers,
)
# ❌ NO max_tokens parameter!
```

3. **GLM has it** (glm_chat.py lines 58-69):
```python
if max_output_tokens:
    payload["max_tokens"] = int(max_output_tokens)
elif ENFORCE_MAX_TOKENS and GLM_MAX_OUTPUT_TOKENS > 0:
    payload["max_tokens"] = int(GLM_MAX_OUTPUT_TOKENS)
```

---

## Impact Analysis

**Severity:** P0 - Critical

**Affected Components:**
- All Kimi API calls (sync and async)
- EXAI workflow tools using Kimi models
- Any long-form responses from Kimi

**Symptoms:**
- Responses truncated at model's default limit
- No control over response length
- Unpredictable truncation behavior
- finish_reason="length" not being prevented

---

## Existing Infrastructure (Good News)

✅ **Already Implemented:**
1. Configuration exists (config.py):
   - `KIMI_MAX_OUTPUT_TOKENS=16384`
   - `DEFAULT_MAX_OUTPUT_TOKENS=8192`
   - `ENFORCE_MAX_TOKENS` flag

2. finish_reason extraction (kimi_chat.py line 369-385):
   - Can detect truncation after the fact
   - Metadata includes finish_reason

3. Token utilities (utils/conversation/token_utils.py):
   - truncate_to_token_limit() function
   - TokenCounter for estimation

---

## Solution Design

### Fix 1: Add max_tokens to Kimi API Calls

**File:** `src/providers/kimi_chat.py`

```python
def chat_completions_create(
    client: Any,
    *,
    model: str,
    messages: list[dict[str, Any]],
    tools: Optional[list[Any]] = None,
    tool_choice: Optional[Any] = None,
    temperature: float = 0.6,
    max_output_tokens: Optional[int] = None,  # ADD THIS PARAMETER
    cache_id: Optional[str] = None,
    reset_cache_ttl: bool = False,
    **kwargs
) -> dict:
    # ... existing code ...
    
    # Build API call parameters
    api_params = {
        "model": model,
        "messages": messages,
        "tools": tools,
        "tool_choice": tool_choice,
        "temperature": temperature,
        "stream": False,
        "extra_headers": extra_headers,
    }
    
    # ADD max_tokens handling (same logic as GLM)
    from config import KIMI_MAX_OUTPUT_TOKENS, ENFORCE_MAX_TOKENS
    if max_output_tokens:
        api_params["max_tokens"] = int(max_output_tokens)
    elif ENFORCE_MAX_TOKENS and KIMI_MAX_OUTPUT_TOKENS > 0:
        api_params["max_tokens"] = int(KIMI_MAX_OUTPUT_TOKENS)
        logger.debug(f"Using default max_tokens={KIMI_MAX_OUTPUT_TOKENS} for Kimi")
```

**File:** `src/providers/async_kimi_chat.py`

```python
async def chat_completions_create_async(
    client: Any,
    *,
    model: str,
    messages: list[dict[str, Any]],
    tools: Optional[list[Any]] = None,
    tool_choice: Optional[Any] = None,
    temperature: float = 0.6,
    max_output_tokens: Optional[int] = None,  # ADD THIS PARAMETER
    cache_id: Optional[str] = None,
    **kwargs
) -> ModelResponse:
    # ... existing code ...
    
    # ADD max_tokens to API call
    from config import KIMI_MAX_OUTPUT_TOKENS, ENFORCE_MAX_TOKENS
    api_params = {
        "model": model,
        "messages": messages,
        "tools": tools,
        "tool_choice": tool_choice,
        "temperature": temperature,
        "stream": False,
        "extra_headers": extra_headers,
    }
    
    if max_output_tokens:
        api_params["max_tokens"] = int(max_output_tokens)
    elif ENFORCE_MAX_TOKENS and KIMI_MAX_OUTPUT_TOKENS > 0:
        api_params["max_tokens"] = int(KIMI_MAX_OUTPUT_TOKENS)
    
    response = await client.chat.completions.create(**api_params)
```

---

### Fix 2: Truncation Detection & Logging

**File:** `src/providers/kimi_chat.py` (after line 385)

```python
# Check for truncation
if finish_reason == "length":
    logger.warning(
        f"Kimi response truncated (finish_reason=length). "
        f"Model: {model}, Output tokens: {usage.get('output_tokens', 'unknown')}"
    )
    
    # Log to Supabase for monitoring
    try:
        from utils.supabase_logger import log_truncation_event
        log_truncation_event(
            provider="kimi",
            model=model,
            finish_reason=finish_reason,
            output_tokens=usage.get("output_tokens"),
            max_tokens=api_params.get("max_tokens")
        )
    except Exception as e:
        logger.debug(f"Failed to log truncation event: {e}")
```

---

### Fix 3: Automatic Retry with Continuation

**File:** `tools/workflow/expert_analysis.py` (or new truncation_handler.py)

```python
async def handle_truncated_response(
    provider,
    model: str,
    messages: list,
    truncated_response: str,
    max_retries: int = 2
) -> str:
    """
    Handle truncated responses by requesting continuation.
    
    Args:
        provider: Provider instance
        model: Model name
        messages: Original messages
        truncated_response: The truncated response
        max_retries: Maximum continuation attempts
    
    Returns:
        Complete response (original + continuations)
    """
    complete_response = truncated_response
    
    for attempt in range(max_retries):
        # Add continuation prompt
        continuation_messages = messages + [
            {"role": "assistant", "content": complete_response},
            {"role": "user", "content": "Please continue from where you left off."}
        ]
        
        # Request continuation
        continuation = await provider.chat_completions_create(
            model=model,
            messages=continuation_messages,
            max_output_tokens=16384  # Use max for continuation
        )
        
        # Check if still truncated
        if continuation.metadata.get("finish_reason") == "length":
            complete_response += continuation.content
            logger.info(f"Continuation {attempt + 1} also truncated, retrying...")
            continue
        else:
            # Complete!
            complete_response += continuation.content
            logger.info(f"Response completed after {attempt + 1} continuation(s)")
            break
    
    return complete_response
```

---

## Implementation Checklist

### Phase 2.1.1: Add max_tokens Parameter ✅ COMPLETE (2025-10-21)
- [x] Update `src/providers/kimi_chat.py`
  - [x] Add max_output_tokens parameter to function signature
  - [x] Add max_tokens logic (same as GLM)
  - [x] Update both API call sites (with_raw_response and fallback)
- [x] Update `src/providers/async_kimi_chat.py`
  - [x] Add max_output_tokens parameter
  - [x] Add max_tokens to API call
- [x] Update `src/providers/kimi.py`
  - [x] Pass max_output_tokens through to kimi_chat module (via **kwargs)
- [x] Update `src/providers/async_kimi.py`
  - [x] Pass max_output_tokens through to async_kimi_chat module

### Phase 2.1.1.1: Model-Aware Token Limits ✅ COMPLETE (2025-10-21)
- [x] Create `src/providers/model_config.py`
  - [x] Define MODEL_TOKEN_LIMITS for all models
  - [x] Implement get_model_token_limits() with fallback logic
  - [x] Implement validate_max_tokens() with validation
  - [x] Add helper functions (get_default_max_tokens, get_max_output_tokens)
- [x] Update `src/providers/kimi_chat.py`
  - [x] Replace hardcoded limits with model-aware validation
  - [x] Update both API call sites
- [x] Update `src/providers/async_kimi_chat.py`
  - [x] Replace hardcoded limits with model-aware validation
- [x] Update `src/providers/glm_chat.py`
  - [x] Replace hardcoded limits with model-aware validation
- [x] Testing
  - [x] Create test_model_config.py
  - [x] Verify all models have correct limits
  - [x] Verify validation logic works correctly
  - [x] Test edge cases (negative, too large, None)

### Phase 2.1.2: Truncation Detection
- [ ] Add truncation logging after finish_reason extraction
- [ ] Create `utils/supabase_logger.py` with log_truncation_event()
- [ ] Add Supabase table for truncation events
- [ ] Test truncation detection with intentionally low max_tokens

### Phase 2.1.3: Automatic Continuation
- [ ] Create `utils/truncation_handler.py`
- [ ] Implement handle_truncated_response()
- [ ] Integrate with expert_analysis.py
- [ ] Test continuation mechanism

### Phase 2.1.4: Testing
- [ ] Test with different models (GLM-4.6, Kimi-k2-0905)
- [ ] Test with different prompt sizes (1K, 5K, 10K, 20K tokens)
- [ ] Verify max_tokens is passed correctly
- [ ] Verify truncation detection works
- [ ] Verify continuation mechanism works
- [ ] Measure truncation rate before/after

---

## Success Criteria

✅ **Fix Verification:**
- max_tokens parameter passed to all Kimi API calls
- Truncation events logged to Supabase
- Automatic continuation working for truncated responses
- Truncation rate reduced by >90%

✅ **Testing:**
- All models tested with various prompt sizes
- No unexpected truncation
- Continuation mechanism tested and working

---

## Risk Assessment

**Low Risk:**
- Adding max_tokens parameter (standard OpenAI parameter)
- Truncation logging (non-blocking)

**Medium Risk:**
- Automatic continuation (could cause loops if not careful)
- Need to limit continuation attempts

**Mitigation:**
- Limit continuation to 2 attempts max
- Add timeout for continuation requests
- Log all continuation attempts

---

## Next Steps

1. Implement Fix 1 (max_tokens parameter) - **IMMEDIATE**
2. Test with EXAI to verify truncation reduced
3. Implement Fix 2 (truncation detection) - **SHORT TERM**
4. Implement Fix 3 (automatic continuation) - **MEDIUM TERM**
5. Monitor truncation rates in production

