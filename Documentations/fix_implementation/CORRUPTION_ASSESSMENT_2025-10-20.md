# System Corruption Assessment - EXAI MCP Server

**Date:** 2025-10-20  
**Branch:** fix/corruption-assessment-2025-10-20  
**Status:** CRITICAL - Multiple Overlapping Systems Detected

---

## 🚨 EXECUTIVE SUMMARY

**CORRECT ARCHITECTURE (How It Should Work):**

```
User → MCP Protocol → EXAI Server → Model Selection (GLM/Kimi)
                                   ↓
                          Native SDK (Z.ai/Moonshot)
                                   ↓
                          Tool Execution & Response
                                   ↓
                          Back to User via MCP
                                   ↓
                    Supabase (async storage/audit trail)
                          ↓ (if SDK fails)
                    Fallback/Recovery Point
```

**ACTUAL PROBLEM:**

**The system has THREE competing conversation management implementations running simultaneously:**

1. **Legacy Text Embedding** (`utils/conversation/history.py`) - OLD, SHOULD BE DELETED
2. **Supabase Message Arrays** (`utils/conversation/supabase_memory.py`) - CORRECT, BUT MIXED WITH LEGACY
3. **In-Memory History Store** (`src/conversation/memory_policy.py`) - LEGACY, SHOULD BE DELETED

**Result:** Legacy code bloat causes:
- Duplicate Supabase queries (3-5x per request) - treating Supabase as primary instead of audit trail
- Contradictory conversation formats (text vs arrays) - SDKs need arrays, legacy uses text
- Workflow tools stuck in infinite loops - circuit breaker broken
- EXAI tools non-functional - confusion from overlapping systems

---

## 📊 CORRUPTION ANALYSIS

### Issue #1: Triple Conversation Loading

**Evidence from Docker Logs:**
```
Line 206: GET conversations?continuation_id=eq.5dff8e35... (FIRST LOAD)
Line 208: GET messages?conversation_id=eq.576ca1c1... (FIRST MESSAGES)
Line 216: [MESSAGE_ARRAY] Building message array (SECOND LOAD)
Line 231: GET conversations?continuation_id=eq.5dff8e35... (THIRD LOAD!)
Line 233: GET messages?conversation_id=eq.576ca1c1... (FOURTH MESSAGES!)
```

**Why This Happens:**

1. **First Load** (`request_handler_context.py` line 102):
   ```python
   context = get_thread(continuation_id)  # ← Loads from Supabase
   ```

2. **Second Load** (`thread_context.py` line 263):
   ```python
   messages_array = storage.get_messages_array(continuation_id)  # ← Loads AGAIN
   ```

3. **Third Load** (inside tool execution):
   ```python
   history_string, _ = build_conversation_history(continuation_id)  # ← Loads AGAIN
   ```

**Impact:** 150-250ms wasted per request on redundant database queries

---

### Issue #2: Competing Conversation Formats

**Three Different Formats Simultaneously:**

**Format 1: Text Embedding** (`utils/conversation/history.py`)
```python
def build_conversation_history(context, model_context):
    history = "=== CONVERSATION HISTORY ===\n"
    for turn in context.turns:
        history += f"Turn {turn.turn_number}: {turn.role} said: {turn.content}\n"
    return history  # ← Returns TEXT STRING
```

**Format 2: Message Arrays** (`utils/conversation/supabase_memory.py`)
```python
def get_messages_array(self, continuation_id):
    messages = []
    for msg in thread['messages']:
        messages.append({
            "role": msg['role'],
            "content": msg['content']
        })
    return messages  # ← Returns ARRAY
```

**Format 3: Legacy Memory Policy** (`src/conversation/memory_policy.py`)
```python
def assemble_context_block(continuation_id, max_turns=6):
    # BUG FIX #12: Now uses Supabase-based storage
    history_string, _ = build_conversation_history(continuation_id)
    return history_string  # ← Returns TEXT STRING (calls Format 1!)
```

**The Conflict:**
- SDK providers expect **message arrays** (Format 2)
- Legacy tools use **text strings** (Format 1)
- Memory policy calls **both** (Format 3 → Format 1)
- Result: SDKs receive wrong format, features break

---

### Issue #3: Workflow Tools Infinite Loop

**Root Cause:** Circuit breaker detects stagnation but doesn't abort

**File:** `tools/workflow/orchestration.py` lines 617-629

**Current Code:**
```python
if stagnant_confidence in ['exploring', 'low', 'medium']:
    logger.warning(
        f"Confidence stagnant at '{stagnant_confidence}' for 3 steps. "
        f"Aborting auto-execution to prevent infinite loop."
    )
    return False  # ← Says "abort" but...
```

**The Problem:**
```python
# Line 479: _should_continue_execution returns False
if self._should_continue_execution(next_request):
    # This block is SKIPPED when False is returned
    return await self._auto_execute_next_step(...)
else:
    # Line 488: But this CONTINUES anyway!
    next_request.next_step_required = False
    return await self.handle_work_completion(...)  # ← Still calls expert analysis!
```

**Result:** Tool says "stopping" but continues to expert analysis, which can take 30-60s and often fails

---

### Issue #4: Supabase Treated as Primary Instead of Audit Trail

**ARCHITECTURAL MISUNDERSTANDING:**

**How It Should Work:**
```
User Request → SDK (primary) → Response to User
                              ↓ (async, non-blocking)
                         Supabase (audit trail)
```

**How It Actually Works:**
```
User Request → Load from Supabase (BLOCKING!)
            → SDK with Supabase data
            → Response to User
            → Write to Supabase (BLOCKING!)
```

**The Issue:**
- Supabase queries are **synchronous and blocking** (150-250ms per request)
- System treats Supabase as **primary data source** instead of **audit trail**
- Should be: SDK → User (fast), then Supabase async (background)
- Actually is: Supabase → SDK → User → Supabase (slow)

**Configuration Says:**
```env
USE_ASYNC_SUPABASE=true  # .env.docker line 424
```

**But Implementation:**
```python
# utils/conversation/supabase_memory.py line 589
def _write_message_background(...):
    """Background thread for writing to Supabase (fire-and-forget pattern)."""
    # This runs in ThreadPoolExecutor, NOT async!
    memory._write_message_background(...)  # ← SYNCHRONOUS call in thread
```

**Additional Problems:**
- Claims to be "async" but uses ThreadPoolExecutor (not true async)
- ThreadPoolExecutor can exhaust resources (max workers)
- Not true async - just "background sync"
- Still blocks if thread pool is full
- **Reads from Supabase are ALWAYS synchronous** (not even background threads!)

---

### Issue #5: Message Array Implementation Incomplete

**What's Implemented:**
- ✅ `get_messages_array()` in `supabase_memory.py`
- ✅ `_messages` parameter in SDK providers
- ✅ Message array building in `thread_context.py`

**What's Missing:**
- ❌ Legacy `build_conversation_history()` still called everywhere
- ❌ `memory_policy.py` still uses text format
- ❌ Tools still expect text format in some places
- ❌ No migration path - both systems run simultaneously

**Evidence:**
```python
# src/conversation/memory_policy.py line 20
from utils.conversation.storage_factory import build_conversation_history
# ← Still imports OLD text-based function!
```

---

## 🔍 FILE-BY-FILE CORRUPTION MAP

### Conversation Management (CRITICAL)

| File | Status | Issue |
|------|--------|-------|
| `utils/conversation/supabase_memory.py` | 🟡 PARTIAL | Has both `build_conversation_history()` AND `get_messages_array()` |
| `utils/conversation/history.py` | 🔴 LEGACY | Text-based history builder, should be deprecated |
| `utils/conversation/storage_factory.py` | 🟡 WRAPPER | Wraps both old and new, causing confusion |
| `src/conversation/memory_policy.py` | 🔴 LEGACY | Still calls old text-based builder |
| `src/server/context/thread_context.py` | 🟢 NEW | Uses message arrays correctly |

### Workflow Tools (BROKEN)

| File | Status | Issue |
|------|--------|-------|
| `tools/workflow/orchestration.py` | 🔴 BROKEN | Circuit breaker doesn't abort, infinite loops |
| `tools/workflows/debug.py` | 🔴 BROKEN | Inherits orchestration bug |
| `tools/workflows/analyze.py` | 🔴 BROKEN | Inherits orchestration bug |
| `tools/workflows/codereview.py` | 🔴 BROKEN | Inherits orchestration bug |
| `tools/workflows/thinkdeep.py` | 🔴 BROKEN | Inherits orchestration bug + auto-mode issues |

### SDK Providers (CONFUSED)

| File | Status | Issue |
|------|--------|-------|
| `src/providers/glm_chat.py` | 🟡 PARTIAL | Checks for `_messages` but also accepts text |
| `src/providers/kimi_chat.py` | 🟡 PARTIAL | Same dual-mode confusion |
| `src/providers/openai_compatible.py` | 🟡 PARTIAL | Wrapper around both modes |

---

## 💥 WHY EXAI IS NOT FUNCTIONAL

**The Perfect Storm:**

1. **Request arrives** with `continuation_id`
2. **Triple load** from Supabase (150-250ms wasted)
3. **Format confusion** - some code gets arrays, some gets text
4. **Workflow tools** try to auto-execute
5. **Circuit breaker** detects stagnation but doesn't abort
6. **Expert analysis** called anyway (30-60s)
7. **WebSocket timeout** or user cancels
8. **Result:** `TOOL_CANCELLED` in logs

**From Docker Logs:**
```
Line 185: TOOL_CANCELLED: chat req_id=03de832c...
Line 288: Success: True  # ← Contradictory!
```

The tool "succeeds" internally but gets cancelled by client timeout.

---

## 📋 CORRUPTION SEVERITY LEVELS

### 🔴 CRITICAL (Fix Immediately)
1. Workflow tool infinite loops
2. Triple Supabase loading
3. Competing conversation formats

### 🟡 HIGH (Fix Soon)
4. Async Supabase not truly async
5. Message array migration incomplete

### 🟢 MEDIUM (Technical Debt)
6. Legacy code not removed
7. Documentation contradictions

---

## 🎯 ROOT CAUSES

### 1. Incomplete Migration
- Started migrating to message arrays (SDK-native format)
- Never finished removing old text-based system
- Both systems run simultaneously, causing format conflicts

### 2. No Deprecation Strategy
- Old functions still exist and get called
- No warnings or errors when using legacy code
- Developers don't know which to use
- **CRITICAL:** Legacy code should have been deleted, not left alongside new code

### 3. Architectural Misunderstanding
- **Supabase should be audit trail/fallback** (async, non-blocking)
- **Actually implemented as primary data source** (sync, blocking)
- This causes 150-250ms latency per request
- Should be: SDK → User (fast), Supabase in background
- Actually is: Supabase → SDK → User → Supabase (slow)

### 4. Over-Engineering from Incomplete Cleanup
- Three layers of conversation management (should be ONE)
- Multiple caching systems (should be ONE request-scoped cache)
- Redundant storage backends (should be SDK primary, Supabase audit)
- **Root cause:** Never deleted old code when adding new features

### 5. Bug Fixes That Made It Worse
- "BUG FIX #11" added async queue (good idea, wrong implementation)
- "BUG FIX #12" changed memory_policy to use Supabase (made it primary instead of audit)
- Each fix added complexity without removing old code
- **Pattern:** Band-aid fixes instead of surgical removal of legacy code

---

## 📝 NEXT STEPS

See `FIX_IMPLEMENTATION_PLAN_2025-10-20.md` for detailed remediation strategy.

**Priority Order:**
1. Fix workflow tool circuit breaker (1 hour)
2. Remove duplicate Supabase queries (2 hours)
3. Complete message array migration (4 hours)
4. Remove legacy conversation code (2 hours)
5. Implement true async Supabase (3 hours)

**Total Estimated Time:** 12 hours of focused work

---

**Assessment Complete:** 2025-10-20 19:05 AEDT

