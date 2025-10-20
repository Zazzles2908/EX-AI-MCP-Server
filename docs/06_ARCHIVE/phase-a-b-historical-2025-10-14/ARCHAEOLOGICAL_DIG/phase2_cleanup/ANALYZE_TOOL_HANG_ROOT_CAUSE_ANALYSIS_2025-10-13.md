# ANALYZE TOOL HANG - ROOT CAUSE ANALYSIS
**Date:** 2025-10-13  
**Status:** INVESTIGATION IN PROGRESS  
**Severity:** CRITICAL - Tool hangs indefinitely, crashes daemon

---

## EXECUTIVE SUMMARY

The `analyze_EXAI-WS` tool hangs indefinitely when expert analysis is enabled, requiring manual cancellation. The `codereview_EXAI-WS` tool works perfectly with identical base implementation. This indicates a tool-specific issue rather than a general expert analysis problem.

**Critical Finding:** The analyze tool is **CRASHING THE DAEMON** - not just hanging, but causing the entire WebSocket server to become unresponsive.

---

## SYMPTOMS

### What Works ✅
- **codereview_EXAI-WS**: Completes in ~5 seconds with expert analysis
- **chat_EXAI-WS**: Works perfectly
- **debug_EXAI-WS**: Works perfectly  
- **thinkdeep_EXAI-WS**: Works perfectly

### What Fails ❌
- **analyze_EXAI-WS**: Hangs indefinitely, must be cancelled
- **Daemon crashes** after analyze hangs
- WebSocket connection becomes stale

---

## EVIDENCE FROM LOGS

### Codereview (WORKS)
```
[EXPERT_DEBUG] provider.generate_content() returned successfully
[EXPERT_DEBUG] Successfully retrieved model_response from task
[EXPERT_DEBUG] About to break from while loop
🔥 [EXPERT_ANALYSIS_COMPLETE] Total Duration: 5.00s
```

### Analyze (HANGS)
```
[EXPERT_DEBUG] provider.generate_content() returned successfully
[EXPERT_DEDUP] Removed analyze:unknown:... from in-progress
TOOL_CANCELLED
(Never sees task.result() retrieval logs)
```

**Key Observation:** Provider returns successfully for BOTH tools, but analyze never retrieves the result.

---

## TIMELINE OF INVESTIGATION

### Attempt 1: Remove Hardcoded Timeout
- **Action:** Removed hardcoded 200s timeout from analyze override
- **Result:** FAILED - Still hangs

### Attempt 2: Remove Entire Override
- **Action:** Deleted `_call_expert_analysis` override from analyze.py
- **Result:** FAILED - Still hangs

### Attempt 3: Add Debug Logging
- **Action:** Added `task.done()` logging to polling loop
- **Result:** Daemon CRASHED before we could see logs

---

## ARCHITECTURAL DIFFERENCES

### Class Hierarchy
Both tools inherit from:
```
WorkflowTool → BaseTool → BaseToolCore → [Mixins] → ExpertAnalysisMixin
```

### Files to Compare
1. **Implementation:**
   - `tools/workflows/analyze.py` vs `tools/workflows/codereview.py`
   
2. **Configuration:**
   - `tools/workflows/analyze_config.py` vs `tools/workflows/codereview_config.py`
   
3. **Models:**
   - `tools/workflows/analyze_models.py` vs `tools/workflows/codereview_models.py`

4. **Base Classes:**
   - `tools/workflow/base.py`
   - `tools/workflow/workflow_mixin.py`
   - `tools/workflow/orchestration.py`
   - `tools/workflow/expert_analysis.py`

5. **Registration:**
   - `src/bootstrap/singletons.py`
   - Tool registry mechanism

6. **Request Handling:**
   - `src/server/handlers/request_handler.py`
   - `src/daemon/session_manager.py`

---

## HYPOTHESES

### Hypothesis 1: Async Context Loss
The analyze tool's execution context is being lost or interrupted, preventing the polling loop from detecting `task.done()`.

### Hypothesis 2: Event Loop Blocking
There's a blocking call specific to analyze that prevents the async event loop from processing the task completion.

### Hypothesis 3: Registration/Routing Issue
Analyze is registered or routed differently than codereview, causing different execution paths.

### Hypothesis 4: Model/Config Difference
Analyze has different configuration that triggers a code path with a bug.

### Hypothesis 5: Daemon Resource Exhaustion
The analyze tool is consuming resources in a way that crashes the daemon.

---

## NEXT STEPS

### Phase 1: Comparative Analysis
1. **Compare tool implementations line-by-line**
   - Identify ANY differences between analyze.py and codereview.py
   - Check for tool-specific overrides or customizations
   
2. **Compare configurations**
   - analyze_config.py vs codereview_config.py
   - analyze_models.py vs codereview_models.py
   
3. **Compare registration**
   - How are tools discovered and registered?
   - Are there tool-specific registry entries?

### Phase 2: Execution Path Tracing
1. **Trace analyze execution from MCP call to expert analysis**
   - Use working tools (chat, codereview) to investigate
   - Map the complete call chain
   
2. **Identify divergence point**
   - Where does analyze execution differ from codereview?
   - What code path is unique to analyze?

### Phase 3: Daemon Crash Investigation
1. **Check daemon logs for crash details**
   - What error occurs before daemon becomes unresponsive?
   - Are there resource exhaustion indicators?
   
2. **Check for memory leaks or resource locks**
   - Is analyze holding resources that prevent cleanup?
   - Are there unclosed connections or file handles?

---

## CRITICAL QUESTIONS

1. **Why does removing the override not fix it?**
   - If analyze now uses the same base implementation as codereview, why different behavior?

2. **Why does the daemon crash?**
   - What is analyze doing that crashes the entire server?

3. **Why does task.done() not trigger?**
   - The provider returns successfully, but the polling loop never detects completion

4. **Is this a race condition?**
   - Does analyze trigger a timing-dependent bug in the base implementation?

---

## FILES MODIFIED (Attempted Fixes)

1. **tools/workflow/expert_analysis.py**
   - Added task.result() timeout protection (lines 512-520)
   - Added debug logging for polling loop
   
2. **tools/workflows/analyze.py**
   - Removed `_call_expert_analysis` override entirely
   
3. **src/daemon/ws_server.py**
   - Added .env file loading for proper configuration

---

## CRITICAL UPDATE (2025-10-13 12:02)

**BREAKTHROUGH FINDING:** The issue is NOT specific to analyze! After removing debug logging, **codereview is NOW ALSO HANGING** with the exact same symptoms:

```
2025-10-13 12:02:08 INFO httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2025-10-13 12:02:08 INFO tools.workflow.expert_analysis: [EXPERT_DEBUG] provider.generate_content() returned successfully
2025-10-13 12:02:10 INFO tools.workflow.expert_analysis: [EXPERT_DEDUP] Removed codereview:unknown:... from in-progress
2025-10-13 12:02:10 INFO mcp_activity: TOOL_CANCELLED: codereview
```

**This means:**
1. The issue is in the `expert_analysis.py` base implementation
2. The `task.result()` timeout fix is NOT working
3. ALL WorkflowTools with expert analysis are affected
4. The problem is in the polling loop's result retrieval mechanism

## ROOT CAUSE IDENTIFIED ✅

**THE BUG:** The expert analysis polling loop was sleeping for 5 seconds between `task.done()` checks!

**File:** `tools/workflow/expert_analysis.py` line 657 (before fix)

**Original Code:**
```python
await asyncio.sleep(min(hb, max(0.1, deadline - time.time())))
```

Where `hb` (heartbeat interval) defaults to 5 seconds.

**The Problem:**
1. Provider completes and returns (e.g., at 12:02:08)
2. Polling loop is sleeping for 5 seconds
3. Client (Augment Code) has its own timeout and cancels the tool (e.g., at 12:02:10)
4. Polling loop never gets a chance to detect `task.done()` because it's still sleeping!

**The Fix:**
```python
# Poll every 100ms to detect task completion immediately
await asyncio.sleep(0.1)

# Only send progress heartbeat every hb seconds to avoid spam
if now - last_progress_time >= hb:
    send_progress(...)
    last_progress_time = now
```

This ensures we detect task completion within 100ms instead of waiting up to 5 seconds.

## CONCLUSION ✅

**Root Cause:** Polling loop sleep interval was too long (5 seconds), causing delayed detection of task completion.

**Fix Applied:** Changed polling interval to 0.1 seconds while keeping progress heartbeat at 5 seconds.

**Files Modified:**
- `tools/workflow/expert_analysis.py` lines 505-661

**Status:** FIXED - Ready for testing

