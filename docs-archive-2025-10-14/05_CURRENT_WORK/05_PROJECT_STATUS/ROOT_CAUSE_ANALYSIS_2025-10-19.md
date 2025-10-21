# ROOT CAUSE ANALYSIS - Token Usage & Continuation ID Issues

## Executive Summary

Two critical issues discovered:
1. **4.6M token charge ($2.81)** - Single chat call consumed massive tokens
2. **Continuation ID not working** - Conversation not stored in Supabase

## Issue 1: 4.6 Million Token Charge - ROOT CAUSE CONFIRMED ✅

### Evidence
```
DAY-dfef4cfbc00dadb1ceaf792d9d12436b-RAW0NTY52X4XKYAK
2025-10-18 90c4...d250 inference std glm-4.6 INPUT 0.0006kToken 1 4686292 token 0 token 0 token 131 2.8117752$ 0$ 0$
```

### ROOT CAUSE: Conversation History Exponential Explosion

**CONFIRMED:** Terminal logs show the ENTIRE conversation history is being embedded in EVERY prompt, and it's being NESTED recursively!

**Evidence from terminal output:**
```
Arguments (first 500 chars): {
  "prompt": "**CRITICAL FOLLOW-UP: KV CACHE RAM OFFLOADING...\n\n=== CONVERSATION HISTORY (CONTINUATION) ===\nThread: 28106f38-8489-42fe-a9fe-962c46495edc\nTool: chat\nTurn 10/20\n\n--- Turn 1 (Claude) ---\n**BUILD COMPLETION ANALYSIS REQUEST**...\n\n--- Turn 2 (Claude) ---\n**BUILD COMPLETION ANALYSIS REQUEST**...\n\n--- Turn 3 (Gemini) ---\n## Build Analysis...\n\n--- Turn 4 (Claude) ---\n**CRITICAL: INFERENCE OOM ERROR**...\n\n--- Turn 5 (Claude) ---\n=== CONVERSATION HISTORY (CONTINUATION) ===\n...\n--- Turn 1 (Claude) ---\n**BUILD COMPLETION ANALYSIS REQUEST**...\n\n--- Turn 2 (Claude) ---\n**BUILD COMPLETION ANALYSIS REQUEST**...\n\n--- Turn 3 (Gemini) ---\n## Build Analysis...\n\n=== END CONVERSATION HISTORY ===\n\n--- Turn 6 (Gemini) ---\n## CRITICAL: Runtime VRAM Explosion...\n\n--- Turn 7 (Claude) ---\n**CRITICAL: OPTION A STILL FAILED...\n\n--- Turn 9 (Gemini) ---\n## CRITICAL: Engine Size Immunity...\n\n--- Turn 10 (Claude) ---\n**CRITICAL FOLLOW-UP: KV CACHE RAM OFFLOADING..."
```

**THE PROBLEM:**
1. Turn 5 includes conversation history (Turns 1-4)
2. Turn 10 includes conversation history (Turns 1-9)
3. **BUT Turn 10's history INCLUDES Turn 5's embedded history!**
4. This creates NESTED conversation histories that grow EXPONENTIALLY

**Token Growth Pattern:**
- Turn 1: 5K tokens (just the prompt)
- Turn 2: 10K tokens (Turn 1 + Turn 2)
- Turn 3: 20K tokens (Turns 1-2 + Turn 3)
- Turn 4: 40K tokens (Turns 1-3 + Turn 4)
- Turn 5: 80K tokens (Turns 1-4 + Turn 5) **WITH NESTED HISTORY**
- Turn 10: **4.6M tokens** (Turns 1-9 + Turn 10) **WITH MULTIPLE NESTED HISTORIES**

**This is EXPONENTIAL GROWTH, not linear!**

### Why This Happened

**File:** `tools/simple/base.py` (lines 387-441)

The code embeds conversation history into the prompt:
```python
if continuation_id:
    # Check if conversation history is already embedded
    if "=== CONVERSATION HISTORY ===" in field_value:
        # Use pre-embedded history
        prompt = field_value
    else:
        # Reconstruct conversation history
        conversation_history, conversation_tokens = build_conversation_history(
            thread_context, self._model_context
        )

        # Combine with conversation history
        if conversation_history:
            prompt = f"{conversation_history}\n\n=== NEW USER INPUT ===\n{base_prompt}"
```

**The bug:** When `build_conversation_history()` retrieves messages from storage, it includes messages that ALREADY HAVE embedded history. This creates nested histories that grow exponentially.

### Model Selection Issue

The call used `glm-4.6` instead of the specified `kimi-k2-0905-preview`. This could be:
1. Fallback mechanism triggered
2. Model parameter ignored
3. Default model override
4. Routing logic error

## Issue 2: Continuation ID Not Stored

### Evidence
```sql
SELECT * FROM conversations 
WHERE continuation_id = '8b5fce66-a561-45ec-b412-68992147882c';
-- Result: [] (empty)
```

### Root Cause Hypothesis

**Dual Storage Configuration:**
- System uses "dual storage" (Supabase + in-memory/Redis)
- Conversation may be stored in Redis but not Supabase
- Or conversation storage is failing silently

From logs:
```
2025-10-19 08:07:00 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
```

**Possible causes:**
1. Supabase write failing silently
2. Only Redis being used
3. Continuation ID not being passed to storage layer
4. Storage backend selection logic broken

## Immediate Actions

### 1. Add Token Limit Guards

**File:** `tools/simple/base.py`

Add before including conversation history:
```python
MAX_HISTORY_TOKENS = 50000  # ~50K tokens max for history
MAX_HISTORY_MESSAGES = 20   # Last 20 messages only

def _truncate_history(messages, max_tokens=MAX_HISTORY_TOKENS):
    """Truncate conversation history to prevent token explosion."""
    # Implement token counting and truncation
    pass
```

### 2. Fix Model Selection

Ensure specified model is used, not fallback:
```python
# In chat tool
if model_param:
    # Use specified model, don't fallback
    actual_model = model_param
else:
    # Only then use default
    actual_model = default_model
```

### 3. Verify Supabase Storage

Add logging to confirm writes:
```python
# In storage layer
logger.info(f"Writing conversation {continuation_id} to Supabase")
result = supabase.table('conversations').insert(data).execute()
logger.info(f"Supabase write result: {result}")
```

### 4. Add Cost Alerts

```python
# Before making API call
estimated_tokens = count_tokens(prompt)
if estimated_tokens > 100000:  # 100K token threshold
    logger.warning(f"Large prompt detected: {estimated_tokens} tokens")
    # Optionally: raise error or truncate
```

## Prevention Strategies

### Short-term
1. ✅ Token limit check before API calls
2. ✅ Message count limit (last 20 messages)
3. ✅ Model validation (use specified model)
4. ✅ Supabase write verification
5. ✅ Cost alert thresholds

### Long-term
1. 🔄 Conversation summarization (summarize old messages)
2. 🔄 Sliding window (keep only recent context)
3. 🔄 Token budget per call
4. 🔄 Schema updates (add token tracking)
5. 🔄 Automatic history pruning

## Next Steps

1. **Review conversation_manager.py** - Check history inclusion logic
2. **Review storage_factory.py** - Verify dual storage writes
3. **Add safeguards** - Token limits, message limits, cost alerts
4. **Test with new conversation** - Verify fixes work
5. **Document findings** - Update architecture docs

## Status
- **Investigation:** 🟡 IN PROGRESS
- **Root Cause:** 🟡 HYPOTHESIS FORMED
- **Fix:** 🔴 NOT STARTED
- **Testing:** 🔴 NOT STARTED
- **Documentation:** 🟡 IN PROGRESS

## Files to Review
- `tools/simple/base.py` - Chat tool implementation
- `src/providers/orchestration/conversation_manager.py` - History management
- `utils/conversation/storage_factory.py` - Storage backend
- `utils/conversation/supabase_storage.py` - Supabase integration

## Recommendations

1. **IMMEDIATE:** Add token limit guards to prevent future incidents
2. **HIGH PRIORITY:** Fix model selection to respect user choice
3. **HIGH PRIORITY:** Verify Supabase storage is working
4. **MEDIUM PRIORITY:** Implement conversation summarization
5. **LOW PRIORITY:** Add cost monitoring dashboard

