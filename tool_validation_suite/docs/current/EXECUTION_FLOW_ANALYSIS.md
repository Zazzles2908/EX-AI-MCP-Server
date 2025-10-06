# EXECUTION FLOW ANALYSIS - Analyze Tool Bottleneck Investigation

**Date:** 2025-10-06  
**Status:** 🔍 INVESTIGATION COMPLETE  
**Finding:** HTTP client timeout mismatch causing indefinite hangs

---

## 📊 Complete Execution Flow

### 1. Test Script → MCP Client
```
test_analyze.py
  ↓
MCPClient.call_tool()
  ↓
WebSocket connection to ws://127.0.0.1:8765 ✅ WORKS
  ↓
Send tool call request ✅ WORKS
```

### 2. Daemon → Tool Execution
```
ws_daemon.py receives request ✅ WORKS
  ↓
tools/workflows/analyze.py
  ↓
WorkflowTool.execute(arguments) ✅ WORKS
  ↓
asyncio.wait_for(execute_workflow(arguments), timeout=300s) ✅ TIMEOUT SET
```

### 3. Workflow Orchestration
```
execute_workflow(arguments)
  ↓
Process step 1 ✅ WORKS
  ↓
Check if next_step_required=False ✅ WORKS
  ↓
handle_work_completion() ✅ WORKS
  ↓
should_call_expert_analysis() → True ✅ WORKS
  ↓
_call_expert_analysis(arguments, request) ⚠️ ENTERS HERE
```

### 4. Expert Analysis Call (THE BOTTLENECK)
```
tools/workflow/expert_analysis.py:_call_expert_analysis()
  ↓
Prepare expert context ✅ WORKS
  ↓
Prepare files for expert analysis ✅ WORKS
  ↓
Get provider (GLM or Kimi) ✅ WORKS
  ↓
Build prompt ✅ WORKS
  ↓
loop.run_in_executor(None, _invoke_provider) ⚠️ THREAD POOL
  ↓
provider.generate_content(...) 🔴 HANGS HERE
```

### 5. Provider Call Chain
```
GLMModelProvider.generate_content()
  ↓
glm_chat.generate_content(sdk_client, http_client, ...)
  ↓
IF use_sdk=True:
    sdk_client.chat.completions.create(...) 🔴 NO TIMEOUT
ELSE:
    http_client.post(...) ⚠️ HAS TIMEOUT (60s default)
```

---

## 🎯 The Bottleneck Identified

### Location
**File:** `src/providers/glm.py` line 36  
**Code:**
```python
self._sdk_client = ZhipuAI(api_key=self.api_key, base_url=self.base_url)
```

**Problem:** The ZhipuAI SDK client is created **without timeout configuration**.

### Evidence from Logs
```
2025-10-06 20:05:48 INFO ws_daemon: Tool: analyze
[DEBUG_EXPERT] About to call _call_expert_analysis for analyze
[PRINT_DEBUG] _call_expert_analysis() ENTERED for tool: analyze
[PRINT_DEBUG] About to call provider.generate_content() for analyze
[PRINT_DEBUG] Inside _invoke_provider, calling provider.generate_content()
```

**Then silence** - no response, no error, no timeout.

---

## 🔬 Timeout Configuration Analysis

### Current Timeout Hierarchy

| Layer | Timeout | Source | Status |
|-------|---------|--------|--------|
| **Workflow Tool** | 300s | `.env` WORKFLOW_TOOL_TIMEOUT_SECS | ✅ SET |
| **Daemon** | 450s | 1.5x workflow | ✅ AUTO-CALCULATED |
| **Shim** | 600s | 2x workflow | ✅ AUTO-CALCULATED |
| **Test** | 400s | `.env` TEST_TIMEOUT_SECS | ✅ SET |
| **HTTP Client** | 60s | `utils/http_client.py` default | ✅ SET |
| **SDK Client** | ??? | ZhipuAI SDK | ❌ **NOT SET** |

### The Problem

1. **HTTP fallback path** (use_sdk=False):
   ```python
   # utils/http_client.py line 38
   self._client = httpx.Client(timeout=self._timeout, follow_redirects=True)
   # ✅ Has 60s timeout (or EX_HTTP_TIMEOUT_SECONDS env var)
   ```

2. **SDK path** (use_sdk=True):
   ```python
   # src/providers/glm.py line 36
   self._sdk_client = ZhipuAI(api_key=self.api_key, base_url=self.base_url)
   # ❌ NO TIMEOUT PARAMETER!
   ```

---

## 🔍 Why It Hangs

### Execution Path
1. Test calls analyze tool with `model='glm-4.5-flash'`
2. Workflow tool processes step 1
3. Expert analysis is triggered
4. GLM provider is selected
5. **SDK path is used** (use_sdk=True)
6. SDK makes HTTP request to `https://api.z.ai/api/paas/v4/chat/completions`
7. **Request hangs** - no response from API
8. **No timeout** - SDK waits indefinitely
9. Thread pool executor blocks
10. Workflow tool timeout (300s) eventually fires
11. Test subprocess timeout (400s) kills the process

### Why HTTP Fallback Works
The HTTP client has a 60s timeout, so if the SDK fails to initialize, the fallback path would timeout properly.

---

## 🔧 The Fix

### Option 1: Configure SDK Timeout (RECOMMENDED)

**File:** `src/providers/glm.py`

**Current:**
```python
self._sdk_client = ZhipuAI(api_key=self.api_key, base_url=self.base_url)
```

**Fixed:**
```python
# Get timeout from config
from config import TimeoutConfig
timeout_secs = TimeoutConfig.WORKFLOW_TOOL_TIMEOUT_SECS

# Configure SDK with timeout
import httpx
timeout_config = httpx.Timeout(
    connect=10.0,
    read=float(timeout_secs),
    write=10.0,
    pool=10.0
)

self._sdk_client = ZhipuAI(
    api_key=self.api_key,
    base_url=self.base_url,
    timeout=timeout_config  # ← ADD THIS
)
```

### Option 2: Force HTTP Fallback

**File:** `src/providers/glm.py`

**Current:**
```python
try:
    from zhipuai import ZhipuAI
    self._use_sdk = True
    self._sdk_client = ZhipuAI(api_key=self.api_key, base_url=self.base_url)
except Exception as e:
    logger.warning("zhipuai SDK unavailable; falling back to HTTP client: %s", e)
    self._use_sdk = False
```

**Fixed:**
```python
# Force HTTP client for better timeout control
self._use_sdk = False
logger.info("Using HTTP client for GLM (better timeout control)")
```

### Option 3: Add Timeout Wrapper

**File:** `tools/workflow/expert_analysis.py`

**Current:**
```python
task = loop.run_in_executor(None, _invoke_provider)
```

**Fixed:**
```python
# Add explicit timeout to executor
timeout_secs = TimeoutConfig.WORKFLOW_TOOL_TIMEOUT_SECS - 10  # Leave 10s buffer
task = loop.run_in_executor(None, _invoke_provider)
try:
    result = await asyncio.wait_for(task, timeout=timeout_secs)
except asyncio.TimeoutError:
    logger.error(f"Provider call timed out after {timeout_secs}s")
    raise TimeoutError(f"Expert analysis provider call exceeded {timeout_secs}s")
```

---

## 📊 Interconnected Scripts

### Analyze Tool Dependencies

```
test_analyze.py
  ↓
tool_validation_suite/utils/mcp_client.py (WebSocket client)
  ↓
src/daemon/ws_server.py (WebSocket daemon)
  ↓
tools/workflows/analyze.py (Analyze tool)
  ↓
tools/workflow/base.py (WorkflowTool base class)
  ↓
tools/workflow/orchestration.py (execute_workflow)
  ↓
tools/workflow/conversation_integration.py (handle_work_completion)
  ↓
tools/workflow/expert_analysis.py (_call_expert_analysis)
  ↓
src/providers/glm.py (GLMModelProvider)
  ↓
src/providers/glm_chat.py (generate_content)
  ↓
zhipuai.ZhipuAI SDK (BOTTLENECK - NO TIMEOUT)
  ↓
https://api.z.ai/api/paas/v4/chat/completions (API endpoint)
```

### Critical Files

1. **src/providers/glm.py** - GLM provider initialization (BOTTLENECK)
2. **src/providers/kimi.py** - Kimi provider (likely same issue)
3. **tools/workflow/expert_analysis.py** - Expert analysis orchestration
4. **utils/http_client.py** - HTTP client with timeout (fallback path)
5. **config.py** - Timeout configuration (TimeoutConfig class)

---

## 🎯 Recommended Action

### Immediate Fix (5 minutes)
Force HTTP fallback in GLM provider to use the timeout-configured HTTP client:

```python
# src/providers/glm.py line 31-38
self._use_sdk = False  # Force HTTP client
logger.info("Using HTTP client for GLM provider (better timeout control)")
```

### Proper Fix (30 minutes)
Configure SDK timeout properly:

1. Check ZhipuAI SDK documentation for timeout parameter
2. Add timeout configuration to SDK initialization
3. Test with analyze tool
4. Apply same fix to Kimi provider

### Verification
```bash
# Should complete in <60s (not 300s timeout)
python tool_validation_suite/tests/core_tools/test_analyze.py
```

---

## 📝 Next Steps

1. ✅ Identify bottleneck - **COMPLETE**
2. ⏳ Implement immediate fix - **READY**
3. ⏳ Test fix with analyze tool
4. ⏳ Apply fix to all workflow tools
5. ⏳ Run full test suite
6. ⏳ Document timeout best practices

---

**Status:** Investigation complete, ready for fix implementation  
**Priority:** CRITICAL  
**Estimated Fix Time:** 5-30 minutes depending on approach

