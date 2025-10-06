# External AI Feedback Analysis & Action Plan

**Date:** 2025-10-04  
**Source:** Claude Sonnet 4.5 (External AI) testing EXAI MCP tools  
**Status:** 🔴 CRITICAL ISSUES IDENTIFIED  
**Priority:** P0 - UX and Infrastructure Problems

---

## 🎯 EXECUTIVE SUMMARY

An external AI (Claude Sonnet 4.5) tested the EXAI MCP tools and identified critical UX and infrastructure issues that significantly impact usability, especially for ADHD-C users who require continuous feedback and fast iteration cycles.

**Critical Issues Identified:**
1. 🔴 **Daemon Connectivity Failure** - 30-second timeout with no recovery guidance
2. 🟡 **Tool Discoverability** - Tool names don't signal functionality
3. 🟡 **Progress Blackout** - No feedback during 7+ second operations
4. 🟡 **JSON Parse Error** - Expert analysis returning non-JSON responses

**What's Working:**
- ✅ Visual structure (color-coded status indicators)
- ✅ Continuation ID pattern
- ✅ Dual output (JSON + markdown)
- ✅ Metadata summaries

---

## 🔴 CRITICAL ISSUE 1: Daemon Connectivity Failure

### The Problem

**Error Message:**
```
Tool: exai-mcp:chat
Error: "Failed to connect to WS daemon at ws://127.0.0.1:8765 within 30.0s"
Impact: 30-second wait → no recovery guidance → dead end
```

**User Experience:**
- User waits 30 seconds for timeout
- No indication of what went wrong
- No guidance on how to fix it
- No fallback options provided
- Dead end - user must figure out solution themselves

**ADHD-C Impact:**
- 30-second wait = assumed permanent failure
- No retry attempted
- User disengages and moves on

### Root Cause

**File:** `scripts/run_ws_shim.py` (lines 82-131)

```python
async def _ensure_ws():
    uri = f"ws://{EXAI_WS_HOST}:{EXAI_WS_PORT}"
    deadline = asyncio.get_running_loop().time() + EXAI_WS_CONNECT_TIMEOUT  # 30 seconds
    # ... connection attempts ...
    raise RuntimeError(f"Failed to connect to WS daemon at {uri} within {EXAI_WS_CONNECT_TIMEOUT}s: {last_err}")
```

**Issues:**
1. No health check before attempting connection
2. No clear error message explaining what to do
3. No fallback mode for offline operation
4. No daemon start command in error message

### Recommended Fix

**Priority:** P0 - IMMEDIATE

**Implementation:**
```python
async def _ensure_ws_with_guidance():
    """Connect to WS daemon with helpful error messages and recovery guidance."""
    # 1. Check if daemon is running via health file
    health_file = Path("logs/ws_daemon.health.json")
    if not health_file.exists() or not _is_health_fresh(health_file):
        raise RuntimeError(
            "WebSocket daemon is not running.\n"
            "To start the daemon, run:\n"
            "  python scripts/ws/run_ws_daemon.py\n"
            "Or use the convenience script:\n"
            "  ./scripts/ws_start.ps1 (Windows)\n"
            "  ./scripts/ws_start.sh (Linux/Mac)\n"
            "\n"
            "To check daemon status:\n"
            "  python scripts/ws/ws_status.py"
        )
    
    # 2. Attempt connection with shorter timeout and better error messages
    try:
        return await _connect_with_retry(timeout=10)  # Shorter timeout
    except Exception as e:
        raise RuntimeError(
            f"Failed to connect to WebSocket daemon: {e}\n"
            "\n"
            "Troubleshooting steps:\n"
            "1. Check if daemon is running: python scripts/ws/ws_status.py\n"
            "2. Restart daemon: ./scripts/force_restart.ps1\n"
            "3. Check logs: tail -f logs/ws_daemon.log\n"
            "4. Verify port 8765 is not in use: netstat -an | grep 8765"
        )
```

**Files to Modify:**
- `scripts/run_ws_shim.py` - Add health check and better error messages
- `tools/simple/base.py` - Add fallback mode for offline operation

**Expected Impact:**
- Faster failure detection (10s instead of 30s)
- Clear recovery guidance
- Reduced user frustration
- Better ADHD-C user experience

---

## 🟡 ISSUE 2: Tool Discoverability

### The Problem

**Example:**
```
Tool: listmodels
Issue: Name doesn't signal what it does without docs
Cognitive load: "Do I want models? Or capabilities? Or status?"
```

**User Experience:**
- Tool names are not self-explanatory
- Users must read documentation to understand what each tool does
- Increases cognitive load for ADHD-C users

### Recommended Fix

**Priority:** P1 - HIGH

**Option 1: Add Tool Descriptions to Response Headers**
```python
# In listmodels_exai response
{
    "tool": "listmodels",
    "description": "💡 TIP: Use this to see which AI models you can call",
    "models": [...]
}
```

**Option 2: Rename Tools with Verb-First Naming**
```
listmodels → show_available_models
chat → ask_ai
thinkdeep → analyze_deeply
debug → investigate_issue
```

**Option 3: Add Inline Hints in Tool Registry**
```python
# In server.py tool registration
tools = {
    "listmodels": {
        "description": "List all available AI models and providers",
        "hint": "Use this to see which models you can call",
        "example": "listmodels()"
    }
}
```

**Recommendation:** Implement Option 1 (add descriptions to response headers) as it's the least disruptive and provides immediate value.

---

## 🟡 ISSUE 3: Progress Blackout

### The Problem

**Example:**
```
Tool: thinkdeep
Duration: 7.0s with no intermediate signals
User experience: "Is it working? Did it hang? Should I retry?"
```

**ADHD-C Impact:**
- ADHD brain assumes failure after 5s silence
- User anxiety increases
- May cancel operation prematurely

### Current Implementation

**File:** `tools/workflow/expert_analysis.py` (lines 361-367)

```python
# Emit heartbeat at configured cadence
try:
    send_progress(f"{self.get_name()}: Waiting on expert analysis (provider={provider.get_provider_type().value})...")
except Exception:
    pass
# Sleep only up to remaining time to avoid overshooting deadline
await asyncio.sleep(min(hb, max(0.1, deadline - time.time())))
```

**Issue:** Progress messages are sent, but may not be frequent enough or visible enough.

### Recommended Fix

**Priority:** P1 - HIGH

**Implementation:**
```python
# For tools >3s execution, emit progress every 2s
async def execute_with_progress(operation, estimated_duration):
    start_time = time.time()
    progress_interval = 2.0  # seconds
    
    async def progress_emitter():
        while not operation.done():
            elapsed = time.time() - start_time
            remaining = max(0, estimated_duration - elapsed)
            progress_pct = min(100, int((elapsed / estimated_duration) * 100))
            
            yield {
                "status": "in_progress",
                "progress": f"{progress_pct}%",
                "elapsed": f"{elapsed:.1f}s",
                "estimated_remaining": f"{remaining:.1f}s",
                "message": "Analyzing..."
            }
            await asyncio.sleep(progress_interval)
    
    # Run operation with progress emitter
    return await asyncio.gather(operation, progress_emitter())
```

**Expected Impact:**
- User sees progress every 2 seconds
- Reduces anxiety about operation status
- Better ADHD-C user experience

---

## 🟡 ISSUE 4: JSON Parse Error

### The Problem

**Warning Message:**
```
WARNING:tools.workflow.expert_analysis:[EXPERT_ANALYSIS_DEBUG] JSON parse error, returning raw analysis
```

**Root Cause:**
- Expert analysis model is returning non-JSON responses
- Response is being returned as raw text instead of structured data
- This breaks downstream processing that expects JSON

### Current Implementation

**File:** `tools/workflow/expert_analysis.py` (lines 370-397)

```python
if model_response.content:
    try:
        analysis_result = json.loads(model_response.content.strip())
        return analysis_result
    except json.JSONDecodeError:
        logger.warning(f"[EXPERT_ANALYSIS_DEBUG] JSON parse error, returning raw analysis")
        return {
            "status": "analysis_complete",
            "raw_analysis": model_response.content,
            "parse_error": "Response was not valid JSON",
        }
```

### Enhanced Logging (IMPLEMENTED)

**File:** `tools/workflow/expert_analysis.py` (lines 370-397)

```python
if model_response.content:
    try:
        # Log the raw response for debugging
        response_preview = model_response.content[:500] if len(model_response.content) > 500 else model_response.content
        logger.debug(f"[EXPERT_ANALYSIS_DEBUG] Raw response preview (first 500 chars): {response_preview}")
        
        analysis_result = json.loads(model_response.content.strip())
        logger.info(f"[EXPERT_ANALYSIS_DEBUG] Successfully parsed JSON response")
        return analysis_result
    except json.JSONDecodeError as json_err:
        # Enhanced logging for JSON parse errors
        logger.error(
            f"[EXPERT_ANALYSIS_DEBUG] JSON parse error: {json_err}\n"
            f"Response length: {len(model_response.content)} chars\n"
            f"Response preview (first 1000 chars): {model_response.content[:1000]}\n"
            f"Response preview (last 500 chars): {model_response.content[-500:]}"
        )
        return {
            "status": "analysis_complete",
            "raw_analysis": model_response.content,
            "parse_error": f"Response was not valid JSON: {str(json_err)}",
        }
```

**Status:** ✅ IMPLEMENTED - Enhanced logging now captures full error details

---

## ✅ WHAT'S WORKING WELL

### 1. Visual Structure (WIN)
```
✅ Color-coded status indicators
✅ Clear section headers
✅ Metadata summary footer
```
**Impact:** Instant pattern recognition without reading every word

### 2. Continuation ID Pattern (WIN)
```json
"continuation_id": "f57b63f1-a664-4d71-956f-e99290c9336d"
```
**Why it works:**
- Explicit state management
- No hidden session dependencies
- Can resume from exact point

### 3. Dual Output (WIN)
```
- Structured JSON for programmatic use
- Human-readable markdown for debugging
```
**Impact:** Can switch between "what did it return" and "what does it mean"

---

## 📊 PRIORITY MATRIX

| Issue | Severity | Impact | Effort | Priority |
|-------|----------|--------|--------|----------|
| Daemon Connectivity Failure | HIGH | HIGH | MEDIUM | P0 |
| JSON Parse Error Logging | MEDIUM | HIGH | LOW | P0 (DONE) |
| Progress Blackout | MEDIUM | MEDIUM | MEDIUM | P1 |
| Tool Discoverability | MEDIUM | LOW | LOW | P1 |

---

## 🚀 IMPLEMENTATION PLAN

### Sprint 1 (Immediate - This Week)
1. ✅ **Enhanced JSON Parse Error Logging** - COMPLETE
2. [ ] **Daemon Health Check** - Add pre-connection health check
3. [ ] **Better Error Messages** - Add recovery guidance to all daemon errors
4. [ ] **Tool Descriptions** - Add descriptions to response headers

### Sprint 2 (Next Week)
1. [ ] **Progress Streaming** - Implement 2-second progress updates
2. [ ] **Fallback Mode** - Add offline mode for non-daemon tools
3. [ ] **Daemon Auto-Start** - Attempt to start daemon automatically on first connection

### Sprint 3 (Future)
1. [ ] **Tool Renaming** - Consider verb-first naming convention
2. [ ] **Estimated Time Remaining** - Add ETA to progress messages
3. [ ] **Health Check Endpoint** - Add HTTP health check endpoint

---

## 📝 FILES TO MODIFY

### High Priority
1. `scripts/run_ws_shim.py` - Daemon connection and error handling
2. `tools/workflow/expert_analysis.py` - ✅ Enhanced logging (DONE)
3. `tools/simple/base.py` - Add fallback mode
4. `server.py` - Add tool descriptions to registry

### Medium Priority
5. `src/daemon/ws_server.py` - Add HTTP health check endpoint
6. `tools/workflow/base.py` - Add progress streaming
7. `docs/` - Update documentation with troubleshooting guides

---

**Created:** 2025-10-04  
**Status:** IN PROGRESS  
**Priority:** P0 - CRITICAL

**Next Steps:** Implement daemon health check and better error messages in Sprint 1.

