# System Prompt Audit - Wave 2 Epic 2.2

**Date:** 2025-10-03  
**Status:** COMPLETE  
**Priority:** CRITICAL (Affects all tool outputs)

---

## Executive Summary

Comprehensive audit of system prompts and hardcoded references to "Claude" throughout the EX-AI-MCP-Server codebase. Found **2 critical issues** in production code that need immediate fixing.

---

## Findings

### ✅ GOOD: System Prompts Are Properly Modularized

**Location:** `systemprompts/` directory

All EXAI tools correctly load system prompts from the `systemprompts/` module:
- ✅ `chat_prompt.py` - Uses base_prompt components
- ✅ `analyze_prompt.py` - Uses base_prompt components
- ✅ `codereview_prompt.py` - Uses base_prompt components
- ✅ `debug_prompt.py` - Uses base_prompt components
- ✅ `thinkdeep_prompt.py` - Uses base_prompt components
- ✅ `consensus_prompt.py` - Uses base_prompt components
- ✅ `planner_prompt.py` - Uses base_prompt components
- ✅ `refactor_prompt.py` - Uses base_prompt components
- ✅ `secaudit_prompt.py` - Uses base_prompt components
- ✅ `testgen_prompt.py` - Uses base_prompt components
- ✅ `docgen_prompt.py` - Uses base_prompt components
- ✅ `precommit_prompt.py` - Uses base_prompt components
- ✅ `tracer_prompt.py` - Uses base_prompt components

**Verification:**
```python
# All tools import from systemprompts module
from systemprompts import CHAT_PROMPT, ANALYZE_PROMPT, etc.

# Base prompt provides shared components
from .base_prompt import (
    ANTI_OVERENGINEERING,
    FILE_PATH_GUIDANCE,
    SERVER_CONTEXT,
    RESPONSE_QUALITY,
    ESCALATION_PATTERN
)
```

**No hardcoded prompts found in tool implementations** ✅

---

## ❌ CRITICAL ISSUES: "Claude" References in Production Code

### Issue #1: Hardcoded "Claude" in Continuation Offer Messages

**File:** `tools/simple/base.py`  
**Lines:** 814, 849, 853

**Problem:**
Continuation offer messages hardcode "Claude" as the client name, which is incorrect for EX-AI-MCP-Server using GLM/Kimi providers.

**Code:**
```python
# Line 814 (existing conversation)
"note": f"Claude can continue this conversation for {remaining_turns} more exchanges."

# Lines 849-853 (new conversation)
note_client = friendly or "Claude"
return {
    "continuation_id": new_thread_id,
    "remaining_turns": MAX_CONVERSATION_TURNS - 1,
    "note": f"{note_client} can continue this conversation for {MAX_CONVERSATION_TURNS - 1} more exchanges.",
}
```

**Impact:**
- MEDIUM severity
- Affects all tools that offer conversation continuation
- Confusing for users (mentions "Claude" when using GLM/Kimi)
- Appears in every continuation_offer response

**Fix Required:**
Replace "Claude" with provider-agnostic language like "You" or "The AI assistant"

---

### Issue #2: Legacy "CLAUDE_*" Environment Variables

**Files:**
- `src/server/handlers/mcp_handlers.py` (lines 48-49)
- `src/server/handlers/request_handler_execution.py` (lines 125)
- `src/server/handlers/request_handler_BACKUP.py` (lines 412-413, 916, 920, 1054)

**Problem:**
Code uses legacy `CLAUDE_TOOL_ALLOWLIST`, `CLAUDE_TOOL_DENYLIST`, `CLAUDE_DEFAULTS_USE_WEBSEARCH`, `CLAUDE_DEFAULT_THINKING_MODE`, `CLAUDE_MAX_WORKFLOW_STEPS` environment variables with fallback to generic `CLIENT_*` variables.

**Code Example:**
```python
# mcp_handlers.py lines 48-49
raw_allow = os.getenv("CLIENT_TOOL_ALLOWLIST", os.getenv("CLAUDE_TOOL_ALLOWLIST", ""))
raw_deny  = os.getenv("CLIENT_TOOL_DENYLIST",  os.getenv("CLAUDE_TOOL_DENYLIST",  ""))
```

**Impact:**
- LOW severity (backward compatibility maintained)
- Confusing variable names for GLM/Kimi-only deployment
- Documentation may reference outdated variable names

**Fix Required:**
- Keep fallback for backward compatibility
- Update documentation to use `CLIENT_*` variables
- Add deprecation notice for `CLAUDE_*` variables

---

## ℹ️ INFORMATIONAL: Documentation References

**Files:**
- `docs/system-reference/04-features-and-capabilities.md` (lines 679-689, 704)
- `src/server/context/thread_context.py` (lines 92, 116)
- `src/server/handlers/mcp_handlers.py` (lines 85, 129)

**Context:**
These are legitimate references to Claude Code/Desktop as a compatible MCP client or in example usage flows.

**Examples:**
```markdown
# Compatible Tools section
**Claude Code Integration:**
ANTHROPIC_API_KEY=your_zai_key
ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic
```

```python
# Example Usage Flow comment
# 1. Claude: "Continue analyzing the security issues" + continuation_id
```

**No Action Required:** These are documentation/comments about Claude as a client, not hardcoded assumptions.

---

## 🔍 Additional Findings

### .venv Library References
Found multiple "Claude" references in `.venv/Lib/site-packages/mcp/` - these are from the MCP SDK library and should NOT be modified.

### Archive/Superseded Files
Found references in `docs/archive/superseded/architecture/ws_daemon/examples/claude.mcp.json` - this is an archived example file, no action needed.

---

## Recommended Fixes

### Fix #1: Update Continuation Offer Messages (HIGH PRIORITY)

**File:** `tools/simple/base.py`

**Change 1 (Line 814):**
```python
# Before:
"note": f"Claude can continue this conversation for {remaining_turns} more exchanges."

# After:
"note": f"You can continue this conversation for {remaining_turns} more exchanges."
```

**Change 2 (Lines 849-853):**
```python
# Before:
note_client = friendly or "Claude"
return {
    "continuation_id": new_thread_id,
    "remaining_turns": MAX_CONVERSATION_TURNS - 1,
    "note": f"{note_client} can continue this conversation for {MAX_CONVERSATION_TURNS - 1} more exchanges.",
}

# After:
note_client = friendly or "You"
return {
    "continuation_id": new_thread_id,
    "remaining_turns": MAX_CONVERSATION_TURNS - 1,
    "note": f"{note_client} can continue this conversation for {MAX_CONVERSATION_TURNS - 1} more exchanges.",
}
```

**Rationale:**
- "You" is provider-agnostic and addresses the user directly
- Maintains friendly tone without assuming specific client
- Works for all MCP clients (Claude Code, Augment, Cline, etc.)

---

### Fix #2: Document CLIENT_* Variables (MEDIUM PRIORITY)

**Files to Update:**
- `.env.example`
- `docs/system-reference/` (configuration guides)
- `README.md` (if applicable)

**Add Documentation:**
```bash
# Client-specific configuration (generic, works with all MCP clients)
CLIENT_TOOL_ALLOWLIST=chat,analyze,debug
CLIENT_TOOL_DENYLIST=
CLIENT_DEFAULTS_USE_WEBSEARCH=false
CLIENT_DEFAULT_THINKING_MODE=medium
CLIENT_MAX_WORKFLOW_STEPS=0

# Legacy variables (deprecated, use CLIENT_* instead)
# CLAUDE_TOOL_ALLOWLIST=
# CLAUDE_TOOL_DENYLIST=
```

---

## Validation Plan

### Test Case 1: Continuation Offer Message
**Before Fix:**
```json
{
  "continuation_offer": {
    "continuation_id": "abc123",
    "remaining_turns": 19,
    "note": "Claude can continue this conversation for 19 more exchanges."
  }
}
```

**After Fix:**
```json
{
  "continuation_offer": {
    "continuation_id": "abc123",
    "remaining_turns": 19,
    "note": "You can continue this conversation for 19 more exchanges."
  }
}
```

### Test Case 2: With Friendly Client Name
**Before Fix:**
```json
{
  "note": "Augment Code can continue this conversation for 19 more exchanges."
}
```

**After Fix:**
```json
{
  "note": "Augment Code can continue this conversation for 19 more exchanges."
}
```
(No change - friendly name is preserved)

---

## Implementation Checklist

- [x] Fix continuation offer messages in `tools/simple/base.py` (lines 814, 849)
- [x] Restart EXAI-WS MCP server
- [x] Validate with chat_EXAI-WS tool call
- [x] Verify continuation_offer.note field shows "You" instead of "Claude"
- [x] Update .env.example with CLIENT_* variable documentation
- [x] Add deprecation notice for CLAUDE_* variables
- [x] Update task manager with completion status

---

## Validation Results

### Test Execution
**Date:** 2025-10-03 05:59:18
**Tool:** chat_EXAI-WS
**Model:** glm-4.5-flash
**Status:** ✅ PASS

### Actual Response
```json
{
  "continuation_offer": {
    "continuation_id": "6e832316-afda-432a-a7ac-2a8ee8722a8d",
    "note": "You can continue this conversation for 19 more exchanges.",
    "remaining_turns": 19
  }
}
```

### Verification
✅ **CONFIRMED:** Continuation offer message now shows "You" instead of "Claude"
✅ **CONFIRMED:** Server restarted successfully
✅ **CONFIRMED:** .env.example updated with CLIENT_* variable documentation
✅ **CONFIRMED:** Deprecation notice added for CLAUDE_* variables

---

## Files Modified

1. **tools/simple/base.py** (2 changes)
   - Line 814: Changed "Claude can continue" → "You can continue"
   - Line 849: Changed `note_client = friendly or "Claude"` → `note_client = friendly or "You"`

2. **.env.example** (1 addition)
   - Added CLIENT_* variable documentation section
   - Added deprecation notice for CLAUDE_* variables
   - Lines 84-106 (new section)

---

## Impact Assessment

**Backward Compatibility:** ✅ MAINTAINED
- Friendly client names (e.g., "Augment Code") still work correctly
- Legacy CLAUDE_* environment variables still supported via fallback
- No breaking changes to API or tool behavior

**User Experience:** ✅ IMPROVED
- Provider-agnostic language ("You" instead of "Claude")
- Clearer documentation for CLIENT_* variables
- Reduced confusion for GLM/Kimi-only deployments

**Code Quality:** ✅ IMPROVED
- Removed hardcoded client assumptions
- Better separation of concerns
- Clearer variable naming conventions

---

## Summary

**Total Issues Found:** 2 critical, 0 informational  
**Files Requiring Changes:** 1 (tools/simple/base.py)  
**Documentation Updates:** 1 (.env.example)  
**Estimated Time:** 15 minutes  
**Risk Level:** LOW (simple string replacement)

**Next Steps:**
1. Implement Fix #1 (continuation offer messages)
2. Restart server and validate
3. Document CLIENT_* variables
4. Mark audit as COMPLETE

