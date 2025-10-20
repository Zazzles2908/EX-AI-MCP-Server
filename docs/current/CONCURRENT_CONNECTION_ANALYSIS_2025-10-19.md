# Concurrent Connection Analysis - Critical Issues
**Date:** 2025-10-19  
**Priority:** 🔴 CRITICAL - System Blocking  
**Status:** 🔍 INVESTIGATION IN PROGRESS

---

## EXECUTIVE SUMMARY

Multiple critical issues discovered affecting system robustness when handling concurrent connections:

1. **Connection Blocking** - Concurrent EXAI requests block each other
2. **Kimi Timeout Cascade** - 180s timeouts triggering retry loops
3. **Semaphore Leaks** - Global and provider-level semaphore leaks detected
4. **Model Selection Hangs** - "auto" model selection contributing to delays

---

## ISSUE 1: Concurrent Connection Blocking

### Evidence from User Report
> "if the other agent who is using exai has gotten stuck like that with the item i raised before, your request to exai becomes stuck as well until i cancel the other one"

### Evidence from Docker Logs
```
2025-10-19 20:10:04 INFO ws_daemon: === TOOL CALL RECEIVED ===
2025-10-19 20:10:04 INFO ws_daemon: Session: 9cb49ab6-cecc-44e3-adeb-a208d98bccec
2025-10-19 20:10:04 INFO ws_daemon: Tool: chat (original: chat)
2025-10-19 20:10:04 INFO ws_daemon: === PROCESSING ===
[NO COMPLETION LOG - Request hung]
```

**Timeline Analysis:**
- 20:10:04 - Session 9cb49ab6 starts processing (other agent)
- 20:24:15 - Session 32b380cd starts processing (this agent)
- 20:25:39 - Session 51dde9f1 starts processing (another agent)
- **All three sessions running concurrently**

### Semaphore Leak Evidence
```
2025-10-19 20:25:39 WARNING ws_daemon: SEMAPHORE HEALTH: Global semaphore leak: expected 24, got 23
2025-10-19 20:25:39 WARNING ws_daemon: SEMAPHORE HEALTH: Provider GLM semaphore leak: expected 4, got 3
```

**Analysis:**
- Global semaphore: 24 → 23 (1 leaked)
- GLM provider semaphore: 4 → 3 (1 leaked)
- Leaks occur during concurrent session processing
- Suggests semaphore not being released properly

### Configuration Analysis

From `.env.docker`:
```bash
# Concurrency limits
EXAI_WS_GLM_MAX_INFLIGHT=4  # Max concurrent GLM requests per session
EXAI_WS_GLOBAL_MAX_INFLIGHT=24  # Max concurrent requests across all sessions
EXAI_WS_KIMI_MAX_INFLIGHT=6  # Max concurrent Kimi requests per session
EXAI_WS_SESSION_MAX_INFLIGHT=8  # Max concurrent requests per session
```

**Problem:** These limits are configured for **production scale** (24 global), but user environment is:
- Single-user development
- 2-5 concurrent sessions maximum
- Should be configured for 5 users, not production

---

## ISSUE 2: Kimi Timeout Cascade

### Evidence from Logs
```
2025-10-19 20:39:32 INFO openai._base_client: Retrying request to /chat/completions in 0.413767 seconds
2025-10-19 20:42:33 INFO openai._base_client: Retrying request to /chat/completions in 0.835476 seconds
```

**Timeline Analysis:**
- 20:39:32 → 20:42:33 = **3 minutes 1 second**
- Matches KIMI_TIMEOUT_SECS=180 exactly
- OpenAI client retry delays: 0.4s, 0.8s (exponential backoff)

### Configuration Analysis

From `.env.docker`:
```bash
KIMI_TIMEOUT_SECS=180  # Kimi API request timeout (3min for thinking mode)
```

**Root Cause:**
1. Kimi API call times out after exactly 180 seconds
2. OpenAI client's built-in retry logic kicks in
3. Retry also times out after 180 seconds
4. Creates cascade of 3-minute delays

**Questions:**
- Is 180s timeout too short for some Kimi operations?
- Are specific API calls (web search, thinking mode) timing out?
- Is this a Kimi API performance issue or configuration issue?

---

## ISSUE 3: Model Selection Causing Hangs

### User Observation
> "you selected auto as the model selection, this might be the reason as well why the hang time is so long"

### Evidence from Logs
```
2025-10-19 20:10:04 INFO ws_daemon: [WS_PROGRESS_NOTIFIER] Called with message: chat: Model/context ready: glm-4.6
2025-10-19 20:13:55 INFO ws_daemon: [WS_PROGRESS_NOTIFIER] Called with message: chat: Model/context ready: glm-4.6
2025-10-19 20:24:27 INFO ws_daemon: [WS_PROGRESS_NOTIFIER] Called with message: chat: Model/context ready: glm-4.6
```

**Analysis:**
- All requests using GLM-4.6 (not Kimi)
- "auto" model selection may be adding overhead
- Model resolution happening for every request

**From AUTO_EXECUTION_ARCHITECTURE.md:**
- Performance optimizer includes "Model resolution caching"
- Should reduce redundant model selection operations
- May not be working correctly with "auto" selection

---

## ISSUE 4: Multi-Step Workflow Restrictions

### User Feedback
> "i dont want you to have restrictions where you have to do 5 steps, like i am pretty sure there was a strat in plan to remove all these restrictions and make yourself really agentic in nature"

### Evidence from AUTO_EXECUTION_ARCHITECTURE.md

**Current Implementation:**
```python
def _should_continue_execution(self, request, step_number):
    # Stop if next_step_required is False
    if not request.next_step_required:
        return False
    
    # Stop if confidence is high enough
    if request.confidence in ["certain", "very_high", "almost_certain"]:
        return False
    
    # Stop if step limit reached
    max_steps = self._calculate_dynamic_step_limit(request)
    if step_number >= max_steps:
        return False
    
    return True
```

**Dynamic Step Limits:**
- debug: 8 steps
- analyze: 10 steps
- secaudit: 15 steps

**Problem:** Still has artificial step limits that prevent true autonomous operation

---

## ARCHITECTURAL CONTEXT

### From ARCHITECTURAL_UPGRADE_REQUEST_2025-10-19.md

**Identified Limitations:**
1. **Multi-Session Parallelization** - Support concurrent connections without performance degradation
2. **Async Supabase Operations** - Non-blocking storage operations
3. **Documentation Organization** - Dedicated folder for context engineering docs
4. **Task Tracking in Supabase** - Persistent task management across sessions

**User's Observation:**
> "When two applications are both calling to EXAI at the same time, the runtime feels like it is extended. The API responses are pretty quick, but the information flowing internally feels slow."

**Proposed Solutions:**
- Option A: One daemon with session multiplexing (asyncio)
- Option B: Multiple daemon instances (one per session)
- Option C: Hybrid (one daemon, worker pool for heavy ops)

---

## ROOT CAUSE ANALYSIS

### Connection Blocking
**Hypothesis:** Semaphore contention at global or session level
- Global semaphore limit: 24 (too high for dev environment)
- Session semaphore limit: 8
- Semaphore leaks preventing proper release
- Concurrent sessions competing for same semaphore pool

### Kimi Timeouts
**Hypothesis:** Timeout too short for certain operations
- 180s timeout may be insufficient for:
  - Web search + thinking mode
  - Large context processing
  - Complex reasoning tasks
- Need to analyze which specific calls are timing out

### Model Selection Overhead
**Hypothesis:** "auto" selection adds latency
- Model resolution not properly cached
- Happening on every request
- Should use explicit model selection or fix caching

---

## IMPACT ASSESSMENT

### Current State
- **Concurrent connections:** Blocked/delayed
- **User experience:** Frustrating (must cancel other agents)
- **System reliability:** Degraded
- **Development velocity:** Slowed

### Risk Level
- 🔴 **CRITICAL** - Blocks multi-agent workflows
- 🔴 **CRITICAL** - Affects all concurrent operations
- 🟡 **HIGH** - Kimi timeouts cause 3-minute delays
- 🟡 **HIGH** - Artificial step limits prevent autonomous operation

---

## NEXT STEPS

### Immediate Actions (This Session)
1. ✅ Analyze Docker logs for patterns
2. ✅ Document concurrent connection issues
3. ⏳ Consult EXAI for root cause analysis
4. ⏳ Implement fixes based on EXAI recommendations

### Investigation Priorities
1. **Semaphore Management** - Fix leaks, adjust limits for dev environment
2. **Kimi Timeout Analysis** - Determine which calls are timing out and why
3. **Model Selection** - Fix caching or use explicit models
4. **Session Isolation** - Ensure sessions don't block each other

### Long-Term Solutions
1. Implement proper multi-session architecture (from ARCHITECTURAL_UPGRADE_REQUEST)
2. Remove artificial step limits from workflow tools
3. Add comprehensive monitoring for concurrent operations
4. Optimize for 2-5 concurrent sessions (not production scale)

---

**Status:** 🔍 **INVESTIGATION IN PROGRESS**

**Next Action:** Consult EXAI with working tools (chat_EXAI-WS) for comprehensive analysis and recommendations

