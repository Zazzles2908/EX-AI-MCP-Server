# CRITICAL FIXES: Storage Factory Infinite Loop & Expert Analysis Override
**Date:** 2025-10-17 04:40 AEDT  
**Status:** ✅ **FIXED - AWAITING CONTAINER REBUILD**  
**Severity:** 🔥 **CRITICAL (P0)**

---

## 🚨 Executive Summary

Fixed TWO critical bugs that were causing:
1. **Storage factory infinite loop** - 60+ storage instances created per request
2. **Expert analysis always triggering** - Pydantic model default overriding env var

Both issues caused session drops, broken tool outputs, and massive performance degradation.

---

## 🔥 Issue #1: Storage Factory Infinite Loop

### **Symptoms**
- Docker logs showing 60+ storage factory initializations in 6 seconds
- Each initialization querying Supabase for same continuation_id
- Tool outputs breaking/truncating
- Massive performance degradation

### **Evidence from Docker Logs**
```
2025-10-17 02:54:57 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-17 02:54:57 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-17 02:54:58 INFO httpx: HTTP Request: GET .../conversations?...continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093
... (repeats 60+ times in 6 seconds)
```

### **Root Cause**
**Files calling `get_conversation_storage()` directly instead of using cached instance:**

1. **`tools/simple/mixins/continuation_mixin.py`** (3 locations):
   - Line 61: `storage = get_conversation_storage()`
   - Line 146: `storage = get_conversation_storage()`
   - Line 287: `storage = get_conversation_storage()`

2. **`tools/workflow/conversation_integration.py`** (1 location):
   - Line 54: `storage = get_conversation_storage()`

**Why This Broke:**
- `get_conversation_storage()` has singleton pattern in `storage_factory.py`
- BUT each call checks singleton INSIDE the function
- When called 60+ times rapidly, singleton isn't initialized yet
- Each call creates NEW `DualStorageConversation` instance
- Each instance queries Supabase independently

**Correct Pattern:**
```python
# ❌ WRONG - Creates new instance every time
from utils.conversation.storage_factory import get_conversation_storage
storage = get_conversation_storage()

# ✅ CORRECT - Uses cached singleton
from utils.conversation.threads import _get_storage_backend
storage = _get_storage_backend()
```

### **Fix Applied**

**File: `tools/simple/mixins/continuation_mixin.py`**
```python
# OLD (3 locations):
from utils.conversation.storage_factory import get_conversation_storage
storage = get_conversation_storage()

# NEW (3 locations):
from utils.conversation.threads import _get_storage_backend
storage = _get_storage_backend()
if not storage:
    logger.warning(f"{self.get_name()}: Storage backend not available")
    return  # or appropriate fallback
```

**File: `tools/workflow/conversation_integration.py`**
```python
# OLD:
from utils.conversation.storage_factory import get_conversation_storage
storage = get_conversation_storage()

# NEW:
from utils.conversation.threads import _get_storage_backend
storage = _get_storage_backend()
if not storage:
    logger.warning(f"{self.get_name()}: Storage backend not available for turn storage")
    return
```

---

## 🔥 Issue #2: Expert Analysis Always Triggering

### **Symptoms**
- Expert analysis triggering despite `DEFAULT_USE_ASSISTANT_MODEL=false`
- Session drops after 8 seconds during expert analysis
- Logs showing expert analysis starting even when disabled

### **Evidence from Docker Logs**
```
2025-10-17 04:38:52 WARNING tools.workflow.expert_analysis: 🔥 [EXPERT_ANALYSIS_START] Tool: debug
2025-10-17 04:38:52 WARNING tools.workflow.expert_analysis: 🔥 [EXPERT_ANALYSIS_START] Model: glm-4.6
2025-10-17 04:39:00 INFO mcp_activity: TOOL_CANCELLED: debug
```

### **Root Cause**
**File: `tools/shared/base_models.py` Line 170**

```python
# ❌ WRONG - Hardcoded default=True overrides env var
use_assistant_model: Optional[bool] = Field(True, description=...)
```

**Why This Broke:**
- Pydantic model defaults to `True` when field not provided
- This overrides `DEFAULT_USE_ASSISTANT_MODEL=false` env var
- Workflow tools always get `use_assistant_model=True`
- Expert analysis always triggers

**Correct Pattern:**
```python
# ✅ CORRECT - Default to None so env var is respected
use_assistant_model: Optional[bool] = Field(None, description=...)
```

### **Fix Applied**

**File: `tools/shared/base_models.py`**
```python
# OLD (Line 170):
use_assistant_model: Optional[bool] = Field(True, description=WORKFLOW_FIELD_DESCRIPTIONS["use_assistant_model"])

# NEW (Line 171):
# CRITICAL FIX: Default to None so env var DEFAULT_USE_ASSISTANT_MODEL is respected
use_assistant_model: Optional[bool] = Field(None, description=WORKFLOW_FIELD_DESCRIPTIONS["use_assistant_model"])
```

**How It Works Now:**
1. If user passes `use_assistant_model=true/false` → use that value
2. If user doesn't pass parameter (None) → check env var `DEFAULT_USE_ASSISTANT_MODEL`
3. If env var is `false` → skip expert analysis
4. If env var is `true` or not set → run expert analysis

---

## 📊 Files Modified

### **Storage Factory Loop Fix:**
1. ✅ `tools/simple/mixins/continuation_mixin.py` (3 locations)
2. ✅ `tools/workflow/conversation_integration.py` (1 location)

### **Expert Analysis Override Fix:**
3. ✅ `tools/shared/base_models.py` (1 location)

**Total:** 3 files, 5 locations fixed

---

## 🧪 Testing Required

### **After Container Rebuild:**

1. **Verify Storage Factory Fix:**
   ```bash
   # Check Docker logs - should see ONLY ONE storage factory init:
   docker logs exai-mcp-server 2>&1 | grep "STORAGE_FACTORY"
   
   # Expected: 1-2 lines total (startup init)
   # NOT: 60+ lines per request
   ```

2. **Verify Expert Analysis Fix:**
   ```bash
   # Check Docker logs - should see NO expert analysis:
   docker logs exai-mcp-server 2>&1 | grep "EXPERT_ANALYSIS_START"
   
   # Expected: 0 lines (expert analysis disabled)
   # NOT: Expert analysis starting
   ```

3. **Verify Tool Outputs:**
   - Test `debug_EXAI-WS` tool
   - Test `chat_EXAI-WS` tool
   - Verify outputs are complete (not truncated)
   - Verify no session drops

---

## 🎯 Expected Behavior After Fix

### **Storage Factory:**
- ✅ ONE storage factory initialization at daemon startup
- ✅ Cached instance reused for all requests
- ✅ NO repeated Supabase queries for same continuation_id
- ✅ Fast response times (<100ms for storage operations)

### **Expert Analysis:**
- ✅ Disabled by default (env var `DEFAULT_USE_ASSISTANT_MODEL=false`)
- ✅ Can be enabled per-call with `use_assistant_model=true`
- ✅ No session drops from timeout
- ✅ Workflow tools complete within 10 seconds

---

## 📋 Related Issues

- **Issue #10** (Supabase): Codereview Tool Session Drops After 8 Seconds
- **Issue #9** (Supabase): Misleading files Parameter - Embeds Text Instead of Upload

---

## 🚀 Next Steps

1. **IMMEDIATE:** Rebuild Docker container
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\ws_start.ps1 -Restart
   ```

2. **VERIFY:** Check Docker logs for both fixes

3. **TEST:** Run workflow tools and verify outputs

4. **UPDATE:** Supabase issue tracking with fix completion

---

## 📝 Lessons Learned

1. **Singleton Pattern Pitfalls:**
   - Singleton in module-level variable can be bypassed by direct function calls
   - Always use cached wrapper functions for singleton access
   - Document the correct usage pattern clearly

2. **Pydantic Default Values:**
   - Field defaults override environment variables
   - Use `None` as default when env var should control behavior
   - Test with and without explicit parameter values

3. **Performance Debugging:**
   - Docker logs are invaluable for identifying loops/spam
   - Count pattern repetitions to identify infinite loops
   - Trace call stacks to find root cause

---

**Fix Completion Time:** 2025-10-17 04:40 AEDT  
**Container Rebuild Required:** YES  
**User Approval Required:** NO (Critical P0 fixes)

