# ROOT CAUSE ANALYSIS - Workflow Tool Timeout Issue

**Date:** 2025-10-06  
**Status:** 🔴 CRITICAL - Workflow tools hanging at provider.generate_content()  
**Impact:** 7/13 core workflow tools timing out (54% failure rate)

---

## 🎯 The Real Problem

After extensive investigation, the issue is **NOT**:
- ❌ Missing test fixture files
- ❌ WebSocket connection problems
- ❌ Timeout configuration
- ❌ File reading logic

The issue **IS**:
- ✅ **Workflow tools hang when calling `provider.generate_content()` during expert analysis**

---

## 📊 Evidence from Daemon Logs

```
2025-10-06 20:05:48 INFO ws_daemon: Tool: analyze
2025-10-06 20:05:48 INFO ws_daemon: === PROCESSING ===
[DEBUG_EXPERT] About to call _call_expert_analysis for analyze
[DEBUG_EXPERT] use_assistant_model=True
[DEBUG_EXPERT] consolidated_findings.findings count=2
[PRINT_DEBUG] _call_expert_analysis() ENTERED for tool: analyze
[PRINT_DEBUG] About to call provider.generate_content() for analyze
[PRINT_DEBUG] Inside _invoke_provider, calling provider.generate_content()
```

**Then it hangs indefinitely** - no response, no error, no timeout.

---

## 🔍 What Works vs What Doesn't

### ✅ Working Tools (23/37 = 62%)
- **Simple tools:** chat, version, health, status, listmodels, etc.
- **Non-workflow tools:** challenge, consensus, docgen, planner, precommit, tracer
- **Provider tools:** All Kimi and GLM provider-specific tools
- **Advanced tools:** activity, health, selfcheck, toolcall_log_tail

### ❌ Failing Tools (7/13 workflow tools = 54%)
- analyze
- codereview
- debug
- refactor
- secaudit
- testgen
- thinkdeep

**Pattern:** ALL workflow tools that call expert analysis are timing out.

---

## 🧩 The Execution Flow

1. **Test script** calls MCP client
2. **MCP client** connects to WebSocket daemon ✅
3. **Daemon** receives tool call ✅
4. **Workflow tool** processes step 1 ✅
5. **Workflow tool** calls `_call_expert_analysis()` ✅
6. **Expert analysis** calls `provider.generate_content()` ✅
7. **Provider** makes API call to GLM/Kimi... **⏸️ HANGS HERE**

---

## 🔬 Technical Details

### Where It Hangs

**File:** `tools/workflow/base.py` or provider implementation  
**Function:** `provider.generate_content()`  
**Context:** Expert analysis validation step

### Why It Hangs

The provider's `generate_content()` call is making an HTTP request to the AI API (GLM or Kimi) and:
1. The request is sent
2. No response is received
3. No timeout is triggered
4. The call blocks indefinitely

### Timeout Hierarchy (Current)

```
Workflow Tool: 300s (from .env WORKFLOW_TOOL_TIMEOUT_SECS)
Daemon: 450s (1.5x workflow)
Shim: 600s (2x workflow)
Test: 400s (TEST_TIMEOUT_SECS)
```

**Problem:** The provider HTTP client doesn't respect these timeouts!

---

## 🎯 Root Cause

The **provider HTTP client** (httpx or requests) is not configured with proper timeouts.

When the workflow tool calls:
```python
response = await provider.generate_content(prompt, model, ...)
```

The underlying HTTP client makes a request to the AI API without a timeout, so it waits indefinitely for a response.

---

## 🔧 Solution

### Fix #1: Add HTTP Client Timeouts to Providers

**Location:** `src/providers/glm_provider.py` and `src/providers/kimi_provider.py`

**Current (problematic):**
```python
response = httpx.post(url, json=payload)  # No timeout!
```

**Should be:**
```python
timeout = httpx.Timeout(
    connect=10.0,  # 10s to establish connection
    read=300.0,    # 300s to read response (matches WORKFLOW_TOOL_TIMEOUT_SECS)
    write=10.0,    # 10s to send request
    pool=10.0      # 10s to get connection from pool
)
response = httpx.post(url, json=payload, timeout=timeout)
```

### Fix #2: Use Timeout from Environment

```python
import os
from config import TimeoutConfig

# Get workflow timeout from config
workflow_timeout = TimeoutConfig.WORKFLOW_TOOL_TIMEOUT_SECS

# Create HTTP timeout with buffer
http_timeout = httpx.Timeout(
    connect=10.0,
    read=float(workflow_timeout) - 10.0,  # Leave 10s buffer
    write=10.0,
    pool=10.0
)
```

### Fix #3: Add Async Timeout Wrapper

```python
import asyncio

async def generate_content_with_timeout(self, prompt, model, **kwargs):
    """Wrapper that enforces timeout on provider calls."""
    timeout = TimeoutConfig.WORKFLOW_TOOL_TIMEOUT_SECS
    
    try:
        return await asyncio.wait_for(
            self._generate_content_impl(prompt, model, **kwargs),
            timeout=timeout
        )
    except asyncio.TimeoutError:
        raise TimeoutError(f"Provider call timed out after {timeout}s")
```

---

## 📝 Action Plan

### Priority 1: Fix Provider Timeouts (CRITICAL)

1. **Update GLM Provider**
   - Add timeout to all HTTP requests
   - Use `TimeoutConfig.WORKFLOW_TOOL_TIMEOUT_SECS`
   - Test with analyze tool

2. **Update Kimi Provider**
   - Add timeout to all HTTP requests
   - Use `TimeoutConfig.WORKFLOW_TOOL_TIMEOUT_SECS`
   - Test with analyze tool

3. **Verify Fix**
   - Run `test_analyze.py` - should complete (pass or fail, not timeout)
   - Run `test_codereview.py` - should complete
   - Run full test suite - expect 0 timeouts

### Priority 2: Add Monitoring

1. **Log HTTP Request Timing**
   ```python
   logger.debug(f"[PROVIDER] Sending request to {url} with {timeout}s timeout")
   start = time.time()
   response = await client.post(url, json=payload, timeout=timeout)
   duration = time.time() - start
   logger.debug(f"[PROVIDER] Response received in {duration:.2f}s")
   ```

2. **Add Timeout Warnings**
   ```python
   if duration > timeout * 0.8:
       logger.warning(f"[PROVIDER] Request took {duration:.2f}s (80% of {timeout}s timeout)")
   ```

### Priority 3: Update Documentation

1. Update `docs/system-reference/` with timeout configuration
2. Document provider timeout requirements
3. Add troubleshooting guide for timeouts

---

## 🧪 Verification Steps

After implementing fixes:

1. **Test Single Workflow Tool:**
   ```bash
   python tool_validation_suite/tests/core_tools/test_analyze.py
   # Expected: Completes in <300s (pass or fail, not timeout)
   ```

2. **Test All Workflow Tools:**
   ```bash
   # Run just workflow tools
   python tool_validation_suite/tests/core_tools/test_analyze.py
   python tool_validation_suite/tests/core_tools/test_codereview.py
   python tool_validation_suite/tests/core_tools/test_debug.py
   # Expected: All complete, 0 timeouts
   ```

3. **Test Full Suite:**
   ```bash
   python tool_validation_suite/scripts/run_all_tests_simple.py
   # Expected: Pass rate >85%, 0 timeouts
   ```

---

## 📈 Expected Improvements

**Before Fix:**
- Pass Rate: 62.2% (23/37)
- Timeouts: 7/37 (18.9%)
- Workflow Tools: 46% pass rate (6/13)

**After Fix:**
- Pass Rate: >85% (>31/37)
- Timeouts: 0/37 (0%)
- Workflow Tools: >85% pass rate (>11/13)

---

## 🎓 Lessons Learned

1. **Always set HTTP timeouts** - Never make HTTP requests without explicit timeouts
2. **Respect timeout hierarchy** - Each layer should have appropriate timeouts
3. **Log timing information** - Makes debugging much easier
4. **Test with real APIs** - Mock tests don't catch timeout issues
5. **Monitor long-running operations** - Workflow tools need special attention

---

**Status:** Ready for implementation  
**Estimated Time:** 1-2 hours  
**Priority:** CRITICAL  
**Blocking:** Full test suite validation

