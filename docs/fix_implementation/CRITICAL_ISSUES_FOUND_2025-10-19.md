# Critical Issues Found - 2025-10-19

## Executive Summary

**CRITICAL ISSUES DISCOVERED:**
1. ✅ **FIXED:** Context window explosion (139K tokens) - user prompts with embedded history saved AS-IS
2. 🔴 **NEW CRITICAL:** Path handling bug causing Docker container crashes
3. 🔴 **NEW CRITICAL:** Workflow tool infinite loop when file reading fails
4. ⚠️ **WARNING:** Container restart detected (crashed at 22:23:36, restarted at 22:24:00)

---

## Issue #1: Context Window Explosion (FIXED)

**Status:** ✅ RESOLVED  
**Severity:** CRITICAL (P0)  
**Impact:** 97% token reduction, 98% cost savings

See: `CONTEXT_WINDOW_EXPLOSION_FIX_2025-10-19.md`

---

## Issue #2: Path Handling Bug (NEW - CRITICAL)

**Status:** 🔴 ACTIVE  
**Severity:** CRITICAL (P0)  
**Impact:** Docker container crashes, workflow tools fail

### Problem Description

When workflow tools (debug, codereview, analyze, etc.) receive Windows file paths from Augment Code, they fail to read files inside the Docker container because:

1. **Windows path received:** `c:\Project\EX-AI-MCP-Server\src\daemon\ws_server.py`
2. **Docker tries to read:** `/app/c:\Project\EX-AI-MCP-Server\src\daemon\ws_server.py` ❌
3. **Result:** File not found error

### Evidence from Docker Logs

```
2025-10-19 22:23:33 WARNING tools.workflow.orchestration: codereview: Failed to read /app/c:\Project\EX-AI-MCP-Server\src\daemon\ws_server.py: Failed to read file: [Errno 2] No such file or directory: '/app/c:\\Project\\EX-AI-MCP-Server\\src\\daemon\\ws_server.py'
```

### Root Cause

**File:** `tools/workflow/orchestration.py`

The workflow orchestration code receives absolute Windows paths but doesn't convert them to Docker-relative paths before attempting to read files.

**Expected behavior:**
- Windows path: `c:\Project\EX-AI-MCP-Server\src\daemon\ws_server.py`
- Should convert to: `/app/src/daemon/ws_server.py`

**Current behavior:**
- Tries to read: `/app/c:\Project\EX-AI-MCP-Server\src\daemon\ws_server.py`
- Fails with "No such file or directory"

### Impact

1. **All workflow tools fail** when given Windows paths:
   - debug_EXAI-WS
   - codereview_EXAI-WS
   - analyze_EXAI-WS
   - refactor_EXAI-WS
   - secaudit_EXAI-WS
   - testgen_EXAI-WS
   - precommit_EXAI-WS
   - docgen_EXAI-WS
   - tracer_EXAI-WS

2. **Triggers infinite loop** (see Issue #3)
3. **Container crashes** after ~30 seconds

### Solution Required

Add path normalization in `tools/workflow/orchestration.py`:

```python
def _normalize_path_for_docker(self, path: str) -> str:
    """
    Convert Windows absolute paths to Docker container paths.
    
    Examples:
        c:\Project\EX-AI-MCP-Server\src\file.py -> /app/src/file.py
        /app/src/file.py -> /app/src/file.py (already normalized)
    """
    import os
    import re
    
    # If path starts with Windows drive letter (e.g., c:\, C:\)
    if re.match(r'^[a-zA-Z]:\\', path):
        # Extract the part after EX-AI-MCP-Server
        match = re.search(r'EX-AI-MCP-Server[\\\/](.+)$', path)
        if match:
            relative_path = match.group(1).replace('\\', '/')
            return f'/app/{relative_path}'
    
    # If path already starts with /app/, return as-is
    if path.startswith('/app/'):
        return path
    
    # Otherwise, assume it's a relative path
    return f'/app/{path}'
```

**Apply to all file reading operations in workflow tools.**

---

## Issue #3: Workflow Tool Infinite Loop (NEW - CRITICAL)

**Status:** 🔴 ACTIVE  
**Severity:** CRITICAL (P0)  
**Impact:** Container crashes, resource exhaustion

### Problem Description

When workflow tools fail to read files (due to Issue #2), they enter an infinite loop:

1. Step 1: Try to read file → FAIL
2. Step 2: Try again → FAIL
3. Step 3: Try again → FAIL
4. ...continues until step 25...
5. Container crashes

### Evidence from Docker Logs

```
2025-10-19 22:23:33 INFO tools.workflow.orchestration: codereview: Continuing auto-execution (step 2)
2025-10-19 22:23:33 WARNING tools.workflow.orchestration: codereview: Failed to read /app/src/daemon/ws_server.py: object of type 'NoneType' has no len()
2025-10-19 22:23:33 INFO tools.workflow.orchestration: codereview: Confidence stagnant at 'exploring' for 3 steps, may need different approach
2025-10-19 22:23:33 INFO tools.workflow.orchestration: codereview: Continuing auto-execution (step 3)
...
[Repeats 25 times]
...
2025-10-19 22:23:36 INFO tools.workflow.orchestration: codereview: Continuing auto-execution (step 25)
[Container crashes]
```

### Root Cause

**File:** `tools/workflow/orchestration.py`

The auto-execution logic doesn't have a **failure detection mechanism**:

1. When file reading fails, it logs a warning but continues
2. Confidence stays at 'exploring' (never increases)
3. The "stagnant confidence" warning is logged but ignored
4. Loop continues until safety limit (50 steps) or crash

**Missing logic:**
- No detection of repeated failures
- No circuit breaker for file read errors
- No early termination when same error occurs multiple times

### Impact

1. **Resource exhaustion:** CPU spins in tight loop
2. **Memory growth:** Each failed step allocates memory
3. **Container crash:** After ~30 seconds, container becomes unresponsive
4. **Data loss:** Any in-progress work is lost

### Solution Required

Add failure detection and circuit breaker in `tools/workflow/orchestration.py`:

```python
class WorkflowOrchestration:
    def __init__(self):
        self._consecutive_failures = 0
        self._max_consecutive_failures = 3
        self._last_error = None
    
    def _handle_file_read_failure(self, error: str) -> bool:
        """
        Track consecutive failures and trigger circuit breaker.
        
        Returns:
            True if should continue, False if should abort
        """
        # Check if same error as last time
        if error == self._last_error:
            self._consecutive_failures += 1
        else:
            self._consecutive_failures = 1
            self._last_error = error
        
        # Circuit breaker: abort after 3 consecutive identical failures
        if self._consecutive_failures >= self._max_consecutive_failures:
            logger.error(
                f"{self.get_name()}: Circuit breaker triggered - "
                f"{self._consecutive_failures} consecutive failures with same error: {error}"
            )
            return False  # Abort
        
        return True  # Continue
```

**Apply to all workflow tools.**

---

## Issue #4: Container Restart (WARNING)

**Status:** ⚠️ OBSERVED  
**Severity:** HIGH (P1)  
**Impact:** Service interruption, connection loss

### Timeline

```
22:23:31 - Container starts
22:23:33 - codereview tool called with Windows path
22:23:33 - File read fails (Issue #2)
22:23:33 - Infinite loop begins (Issue #3)
22:23:36 - Last log entry before crash
22:24:00 - Container restarts (29 seconds later)
22:24:02 - Container fully operational again
```

### Evidence

```
2025-10-19 22:23:36 INFO tools.workflow.orchestration: codereview: Continuing auto-execution (step 25)
[29 second gap]
2025-10-19 22:24:00 INFO root: [ASYNC_LOGGING] Async-safe logging configured successfully
```

### Root Cause

Likely caused by:
1. **Issue #3:** Infinite loop exhausting resources
2. **Docker health check failure:** Container became unresponsive
3. **Docker restart policy:** Container automatically restarted

### Impact

1. **Active connections lost:** Any in-progress tool calls terminated
2. **Session state lost:** Redis cache cleared on restart
3. **User experience:** "no close frame received or sent" errors
4. **Data integrity:** Potential for incomplete Supabase writes

### Solution Required

1. **Fix Issues #2 and #3** (primary cause)
2. **Add health check monitoring** to detect infinite loops
3. **Add graceful shutdown** to preserve state before restart
4. **Add circuit breaker** to prevent resource exhaustion

---

## Immediate Action Items

### Priority 1 (CRITICAL - Do Now)

1. ✅ **Fix context window explosion** - COMPLETED
2. 🔴 **Fix path handling bug** - Add path normalization to workflow tools
3. 🔴 **Fix infinite loop** - Add failure detection and circuit breaker
4. 🔴 **Test with Windows paths** - Verify workflow tools work correctly

### Priority 2 (HIGH - Do Soon)

1. ⚠️ **Add health monitoring** - Detect infinite loops and resource exhaustion
2. ⚠️ **Add graceful shutdown** - Preserve state before container restart
3. ⚠️ **Add error recovery** - Resume interrupted tool calls after restart
4. ⚠️ **Add path validation** - Reject invalid paths early

### Priority 3 (MEDIUM - Do Later)

1. 📝 **Add integration tests** - Test workflow tools with Windows paths
2. 📝 **Add monitoring alerts** - Alert on container restarts
3. 📝 **Add performance metrics** - Track file read failures
4. 📝 **Add documentation** - Document path handling requirements

---

## Testing Recommendations

### Test Case 1: Windows Path Handling

```python
# Test that Windows paths are correctly normalized
def test_windows_path_normalization():
    tool = CodeReviewTool()
    
    # Windows absolute path
    windows_path = r"c:\Project\EX-AI-MCP-Server\src\daemon\ws_server.py"
    
    # Should normalize to Docker path
    result = tool.execute(
        step="Review this file",
        step_number=1,
        total_steps=1,
        next_step_required=False,
        findings="Test",
        relevant_files=[windows_path]
    )
    
    # Should succeed (not crash)
    assert result is not None
    assert "Failed to read" not in result
```

### Test Case 2: Failure Detection

```python
# Test that repeated failures trigger circuit breaker
def test_failure_circuit_breaker():
    tool = CodeReviewTool()
    
    # Invalid path that will fail
    invalid_path = "/nonexistent/file.py"
    
    # Should abort after 3 failures (not loop forever)
    result = tool.execute(
        step="Review this file",
        step_number=1,
        total_steps=1,
        next_step_required=True,
        findings="Test",
        relevant_files=[invalid_path]
    )
    
    # Should contain circuit breaker message
    assert "Circuit breaker triggered" in result
```

### Test Case 3: Container Stability

```bash
# Test that container doesn't crash under load
docker logs exai-mcp-daemon --tail 100 --follow &

# Send 10 concurrent requests with Windows paths
for i in {1..10}; do
    # Call workflow tool with Windows path
    curl -X POST http://localhost:8079 -d '{
        "op": "call_tool",
        "tool": "codereview",
        "arguments": {
            "relevant_files": ["c:\\Project\\EX-AI-MCP-Server\\src\\daemon\\ws_server.py"]
        }
    }' &
done

wait

# Verify container is still running
docker ps | grep exai-mcp-daemon
```

---

## Supabase Status

**Status:** ✅ HEALTHY

Recent conversations (last hour):
- 5 conversations with 1 message each
- Total content length: 83-995 characters
- No signs of data corruption
- No exponential growth detected

**Verification Query:**
```sql
SELECT 
  c.continuation_id,
  COUNT(m.id) as message_count,
  SUM(LENGTH(m.content)) as total_content_length
FROM conversations c
LEFT JOIN messages m ON c.id = m.conversation_id
WHERE c.updated_at > NOW() - INTERVAL '1 hour'
GROUP BY c.id, c.continuation_id
ORDER BY MAX(m.created_at) DESC;
```

---

## Conclusion

**Critical Issues Found:** 4  
**Fixed:** 1 (Context window explosion)  
**Active:** 3 (Path handling, infinite loop, container restart)  

**Next Steps:**
1. Fix path normalization in workflow tools
2. Add failure detection and circuit breaker
3. Test with Windows paths
4. Monitor container stability

**Estimated Time to Fix:** 2-3 hours  
**Risk Level:** HIGH (container crashes affect all users)  
**Priority:** CRITICAL (P0)

---

**Date:** 2025-10-19  
**Author:** Augment Agent  
**Status:** INVESTIGATION COMPLETE - FIXES REQUIRED

