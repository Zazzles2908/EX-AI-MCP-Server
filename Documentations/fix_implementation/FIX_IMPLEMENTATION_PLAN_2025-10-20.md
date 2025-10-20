# Fix Implementation Plan - EXAI MCP Server

**Date:** 2025-10-20
**Branch:** fix/corruption-assessment-2025-10-20
**Status:** ✅ PHASE 1 & 3 COMPLETE - CONTINUING WITH PHASE 2

**Last Updated:** 2025-10-20 20:30 AEDT

---

## 🎯 OBJECTIVES

**PRIMARY GOAL: KILL LEGACY CODE - SURGICAL REMOVAL, NOT BAND-AIDS**

1. **Make EXAI functional** - Fix workflow tools and conversation management
2. **DELETE legacy code** - Remove old text-based system entirely (not deprecate, DELETE)
3. **Fix architecture** - Supabase as audit trail (async), not primary data source (sync)
4. **Eliminate redundancy** - Remove duplicate queries and competing systems
5. **Complete migration** - Finish message array implementation (SDK-native format)
6. **Improve performance** - Reduce latency by 60-70%
7. **Simplify architecture** - ONE conversation system (message arrays), not three

**PHILOSOPHY: If it's legacy, DELETE IT. Don't leave it "just in case."**

---

## 📊 PRIORITY MATRIX

| Priority | Issue | Impact | Effort | Order |
|----------|-------|--------|--------|-------|
| P0 | Workflow tool infinite loops | 🔴 CRITICAL | 1h | #1 |
| P0 | Triple Supabase loading | 🔴 CRITICAL | 2h | #2 |
| P1 | Complete message array migration | 🟡 HIGH | 4h | #3 |
| P1 | Remove legacy conversation code | 🟡 HIGH | 2h | #4 |
| P2 | Implement true async Supabase | 🟢 MEDIUM | 3h | #5 |

---

## 🔧 PHASE 1: EMERGENCY FIXES ✅ COMPLETE

### Fix #1: Workflow Tool Circuit Breaker ✅ COMPLETE

**Problem:** Circuit breaker logs warning but doesn't abort
**Status:** ✅ FIXED (Commit: 901dbb7)
**Result:** Circuit breaker now raises RuntimeError to force immediate abort

**File:** `tools/workflow/orchestration.py`

**Current Code (lines 617-629):**
```python
if stagnant_confidence in ['exploring', 'low', 'medium']:
    logger.warning(f"Confidence stagnant...")
    return False  # ← Returns False but...

# Line 479-489: Caller doesn't respect False!
if self._should_continue_execution(next_request):
    return await self._auto_execute_next_step(...)
else:
    # Still continues to expert analysis!
    return await self.handle_work_completion(...)
```

**Fix:**
```python
# Line 617-629: When stagnation detected, raise exception
if stagnant_confidence in ['exploring', 'low', 'medium']:
    logger.error(
        f"{self.get_name()}: Circuit breaker ABORT - Confidence stagnant at "
        f"'{stagnant_confidence}' for 3 steps. Stopping auto-execution."
    )
    # Raise exception to force abort
    raise RuntimeError(
        f"Auto-execution aborted: Confidence stagnant at '{stagnant_confidence}' for 3 steps. "
        f"Suggestions: (1) Provide more context/files, (2) Break task into smaller steps, "
        f"(3) Use chat_EXAI-WS for manual guidance."
    )

# Line 479-489: Catch exception and return error
try:
    if self._should_continue_execution(next_request):
        return await self._auto_execute_next_step(...)
    else:
        return await self.handle_work_completion(...)
except RuntimeError as e:
    # Circuit breaker aborted
    return {
        "status": "circuit_breaker_abort",
        "error": str(e),
        "step_number": next_step_number,
        "confidence": next_request.confidence
    }
```

**Testing:**
1. Call `debug_EXAI-WS` with vague prompt
2. Verify it aborts after 3 stagnant steps
3. Check logs show "Circuit breaker ABORT"
4. Confirm no expert analysis is called

---

### Fix #2: Eliminate Triple Supabase Loading ✅ COMPLETE

**Problem:** Same conversation loaded 3-5 times per request
**Status:** ✅ FIXED (Commits: 901dbb7, 74e2b10, f7ab3ef)
**Critical Fix:** Method was defined at module level instead of inside class (f7ab3ef)
**Result:** Request cache now properly clears after each request

**Root Cause:** Three different code paths all call `get_thread()`

**Solution:** Single load with request-scoped cache

**Step 1: Add Request-Scoped Cache**

**File:** `utils/conversation/supabase_memory.py`

**Add after line 75:**
```python
# Request-scoped cache (cleared after each request)
self._request_cache = {}
self._request_cache_enabled = True
```

**Step 2: Modify get_thread() to Use Request Cache**

**File:** `utils/conversation/supabase_memory.py` line 100

**Replace:**
```python
def get_thread(self, continuation_id: str) -> Optional[Dict[str, Any]]:
    # Check request cache first (NEW)
    if self._request_cache_enabled and continuation_id in self._request_cache:
        logger.debug(f"[REQUEST_CACHE HIT] {continuation_id}")
        return self._request_cache[continuation_id]
    
    # Existing code...
    thread = self._load_from_supabase(continuation_id)
    
    # Store in request cache (NEW)
    if self._request_cache_enabled and thread:
        self._request_cache[continuation_id] = thread
    
    return thread
```

**Step 3: Clear Request Cache After Each Request**

**File:** `src/server/handlers/request_handler.py` line 70

**Add at end of function:**
```python
finally:
    # Clear request-scoped cache
    try:
        from utils.conversation.storage_factory import get_conversation_storage
        storage = get_conversation_storage()
        if hasattr(storage, '_request_cache'):
            storage._request_cache.clear()
            logger.debug("[REQUEST_CACHE] Cleared after request")
    except Exception as e:
        logger.debug(f"Failed to clear request cache: {e}")
```

**Expected Result:**
- First `get_thread()` loads from Supabase
- Subsequent calls in same request use cache
- Reduce from 3-5 queries to 1 query per request
- Save 100-200ms per request

---

## 🔧 PHASE 2: COMPLETE MESSAGE ARRAY MIGRATION 🔄 IN PROGRESS

### Fix #3: Remove Text-Based Conversation Building 🔄 IN PROGRESS

**Problem:** Two competing formats (text vs arrays)
**Status:** 🔄 PARTIALLY COMPLETE - Need to verify all SDK providers use message arrays

**Step 1: Deprecate build_conversation_history()**

**File:** `utils/conversation/history.py`

**Add deprecation warning:**
```python
def build_conversation_history(...):
    """
    DEPRECATED: Use get_messages_array() instead.
    This function will be removed in next release.
    """
    import warnings
    warnings.warn(
        "build_conversation_history() is deprecated. Use get_messages_array() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    # Existing code...
```

**Step 2: Update memory_policy.py**

**File:** `src/conversation/memory_policy.py`

**Replace lines 7-31:**
```python
def assemble_context_block(continuation_id: str, max_turns: int = 6) -> str:
    """
    DEPRECATED: This function is deprecated.
    Tools should use message arrays directly via _messages parameter.
    """
    import warnings
    warnings.warn(
        "assemble_context_block() is deprecated. Use message arrays instead.",
        DeprecationWarning,
        stacklevel=2
    )
    
    # Return empty string - tools should use _messages parameter
    return ""
```

**Step 3: Update All Tool Calls**

**Files to update:**
- `tools/simple/base.py`
- `tools/simple/mixins/continuation_mixin.py`
- `tools/workflow/base.py`

**Change:**
```python
# OLD: Build text history
history = assemble_context_block(continuation_id)
prompt = f"{history}\n\n{user_prompt}"

# NEW: Use _messages parameter (already in arguments)
# No need to build text - SDK providers handle it
```

**Step 4: Remove Fallback to Text Format**

**File:** `src/providers/glm_chat.py` line 44

**Remove fallback:**
```python
# REMOVE THIS:
if "_messages" in kwargs and kwargs["_messages"]:
    messages = kwargs["_messages"]
else:
    # Fallback: Build messages from prompt
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

# REPLACE WITH:
if "_messages" not in kwargs or not kwargs["_messages"]:
    raise ValueError(
        "Message array required. Ensure continuation_id is provided or "
        "request_handler builds message array correctly."
    )
messages = kwargs["_messages"]
```

---

## 🔧 PHASE 3: KILL LEGACY CODE ✅ COMPLETE

**PHILOSOPHY: DELETE, DON'T DEPRECATE. SURGICAL REMOVAL.**
**Status:** ✅ COMPLETE (Commits: b1605d7, 78c99e3, b82c832)
**Result:** 925 lines of dead code removed, 3 competing systems eliminated

### Fix #4: Delete Unused Conversation Systems ✅ COMPLETE

**Step 1: DELETE Legacy History Store (COMPLETE REMOVAL)**

**Files to DELETE entirely:**
- `src/conversation/history_store.py` - DELETE FILE
- `src/conversation/memory_policy.py` - DELETE FILE
- `src/conversation/__init__.py` - DELETE FILE (if only contains legacy imports)
- `utils/conversation/history.py` - DELETE FILE

**Rationale:** These are 100% legacy. No modern code should use them.

**Step 2: DELETE Text-Based History Functions**

**File:** `utils/conversation/supabase_memory.py`

**DELETE these functions entirely:**
- `build_conversation_history()` (lines 443-554) - DELETE
- Any text-based formatting functions - DELETE

**KEEP only:**
- `get_messages_array()` - This is the ONLY conversation builder we need
- Supabase storage wrapper
- Async write queue

**Step 3: Simplify Storage Factory**

**File:** `utils/conversation/storage_factory.py`

**DELETE:**
- `build_conversation_history()` function (lines 286-320) - DELETE
- All text-based history methods - DELETE
- Any fallback to text format - DELETE

**KEEP:**
- `get_messages_array()` only
- Supabase storage wrapper
- Request-scoped caching (from Phase 1)

**Step 4: Verify No Callers Remain**

**Search entire codebase for:**
```bash
grep -r "build_conversation_history" src/ tools/ utils/
grep -r "assemble_context_block" src/ tools/ utils/
grep -r "history_store" src/ tools/ utils/
```

**If any callers found:** Update them to use `get_messages_array()` or delete them

**Expected result:** Zero matches (all legacy code removed)

---

## 🔧 PHASE 4: TRUE ASYNC SUPABASE (3 hours)

### Fix #5: Replace ThreadPoolExecutor with Async Queue

**Problem:** "Async" Supabase uses threads, not true async

**Step 1: Verify Async Queue Implementation**

**File:** `src/daemon/conversation_queue.py`

**Ensure it exists and works:**
```python
class ConversationQueue:
    def __init__(self, max_size=1000):
        self.queue = asyncio.Queue(maxsize=max_size)
        self.consumer_task = None
    
    async def put(self, item):
        await self.queue.put(item)
    
    async def consume(self):
        while True:
            item = await self.queue.get()
            await self._process_item(item)
```

**Step 2: Remove ThreadPoolExecutor**

**File:** `utils/conversation/supabase_memory.py`

**Remove lines 76-87:**
```python
# DELETE THIS:
if USE_ASYNC_SUPABASE:
    self._write_executor = None
    self._use_async_queue = True
else:
    self._write_executor = None
    self._use_async_queue = False
```

**Replace with:**
```python
# Always use async queue
self._use_async_queue = True
logger.info("[ASYNC_SUPABASE] Using async queue for all writes")
```

**Step 3: Make Supabase Client Truly Async**

**File:** `src/storage/supabase_client.py`

**Add async methods:**
```python
async def save_message_async(self, conversation_id, role, content, ...):
    """Truly async Supabase write using httpx async client"""
    # Use httpx.AsyncClient instead of sync client
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{self.url}/rest/v1/messages",
            json={...},
            headers={...}
        )
    return response.json()
```

---

## 📋 TESTING CHECKLIST

### Phase 1 Tests ✅ COMPLETE
- [x] Workflow tool aborts after 3 stagnant steps
- [x] No expert analysis called on abort
- [x] Error message is clear and actionable
- [x] Supabase queries reduced from 3-5 to 1 per request
- [x] Request cache cleared after each request

### Phase 2 Tests 🔄 IN PROGRESS
- [ ] All tools use message arrays (NEED TO VERIFY)
- [ ] No text-based history building (NEED TO VERIFY)
- [ ] SDK providers receive correct format (NEED TO VERIFY)
- [ ] Continuation works across multiple turns (NEED TO TEST)
- [ ] File context preserved in arrays (NEED TO TEST)

### Phase 3 Tests ✅ COMPLETE
- [x] Legacy files deleted
- [x] No import errors
- [x] All tests pass
- [x] Documentation updated

### Phase 4 Tests
- [ ] Async queue processes writes
- [ ] No ThreadPoolExecutor usage
- [ ] Supabase writes don't block responses
- [ ] Queue doesn't overflow under load

---

## 📊 EXPECTED IMPROVEMENTS

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Supabase queries per request | 3-5 | 1 | 70-80% reduction |
| Request latency | 300-500ms | 100-150ms | 60-70% faster |
| Workflow tool reliability | 20% | 95% | 4.75x better |
| Code complexity | 3 systems | 1 system | 66% simpler |
| Memory usage | High (threads) | Low (async) | 40% reduction |

---

## 🚀 EXECUTION TIMELINE

**Day 1 (4 hours):**
- Morning: Phase 1 (Emergency Fixes)
- Afternoon: Phase 2 Part 1 (Deprecation)

**Day 2 (4 hours):**
- Morning: Phase 2 Part 2 (Migration)
- Afternoon: Phase 3 (Cleanup)

**Day 3 (4 hours):**
- Morning: Phase 4 (True Async)
- Afternoon: Testing & Documentation

**Total:** 12 hours over 3 days

---

## ⚠️ RISKS & MITIGATION

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Breaking existing tools | Medium | High | Comprehensive testing before merge |
| Supabase connection issues | Low | Medium | Keep fallback to in-memory |
| Performance regression | Low | High | Benchmark before/after |
| User disruption | Medium | Low | Deploy during low-usage window |

---

**Plan Complete:** 2025-10-20 19:15 AEDT  
**Ready for Execution:** YES  
**Approval Required:** User confirmation before starting Phase 1

