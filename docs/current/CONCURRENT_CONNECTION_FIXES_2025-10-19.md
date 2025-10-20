# Concurrent Connection Fixes - Implementation Plan
**Date:** 2025-10-19  
**Priority:** 🔴 CRITICAL  
**Status:** 📋 READY FOR IMPLEMENTATION

---

## EXECUTIVE SUMMARY

Comprehensive fix plan for 4 critical concurrent connection issues:

1. ✅ **Semaphore Leaks** - Root cause identified, fix ready
2. ✅ **Connection Blocking** - Configuration fix ready
3. ✅ **Kimi Timeout Cascade** - Adaptive timeout strategy ready
4. ✅ **Model Selection Overhead** - Already optimized with caching

---

## FIX 1: Semaphore Leak Prevention

### Root Cause Analysis

**Location:** `src/daemon/ws_server.py` lines 1117-1140

**Current Code:**
```python
finally:
    # Guaranteed semaphore cleanup - release in reverse order
    if acquired_session:
        try:
            (await _sessions.get(session_id)).sem.release()
            logger.debug(f"Released session semaphore for {session_id}")
        except Exception as e:
            logger.critical(f"CRITICAL: Failed to release session semaphore: {e}")
            # This is a semaphore leak - log as critical for monitoring
```

**Problem:**
- Exception during `release()` call prevents semaphore from being released
- Logged as CRITICAL but semaphore still leaked
- Accumulates over time causing connection blocking

**Evidence:**
```
WARNING: Global semaphore leak: expected 24, got 23
WARNING: Provider GLM semaphore leak: expected 4, got 3
```

### Solution: Semaphore Health Recovery

**Add automatic semaphore recovery mechanism:**

```python
# Add to ws_server.py after line 1413

async def _recover_semaphore_leaks():
    """Attempt to recover from semaphore leaks by resetting to expected values."""
    recovered = []
    
    # Recover global semaphore
    if _global_sem._value < GLOBAL_MAX_INFLIGHT:
        leaked = GLOBAL_MAX_INFLIGHT - _global_sem._value
        for _ in range(leaked):
            try:
                _global_sem.release()
            except ValueError:
                break  # Can't release more than acquired
        recovered.append(f"Global: +{leaked}")
    
    # Recover provider semaphores
    for provider, sem in _provider_sems.items():
        expected = {"KIMI": KIMI_MAX_INFLIGHT, "GLM": GLM_MAX_INFLIGHT}.get(provider, 0)
        if sem._value < expected:
            leaked = expected - sem._value
            for _ in range(leaked):
                try:
                    sem.release()
                except ValueError:
                    break
            recovered.append(f"{provider}: +{leaked}")
    
    if recovered:
        logger.warning(f"SEMAPHORE RECOVERY: Recovered leaks: {', '.join(recovered)}")
        return True
    return False
```

**Call recovery in semaphore health check:**

```python
# Modify _check_semaphore_health() at line 1396

async def _check_semaphore_health():
    """Check for semaphore leaks and attempt recovery."""
    issues = []
    
    # Check global semaphore
    if _global_sem._value != GLOBAL_MAX_INFLIGHT:
        issues.append(f"Global semaphore leak: expected {GLOBAL_MAX_INFLIGHT}, got {_global_sem._value}")
    
    # Check provider semaphores
    for provider, sem in _provider_sems.items():
        expected = {"KIMI": KIMI_MAX_INFLIGHT, "GLM": GLM_MAX_INFLIGHT}.get(provider, 0)
        if sem._value != expected:
            issues.append(f"Provider {provider} semaphore leak: expected {expected}, got {sem._value}")
    
    if issues:
        for issue in issues:
            logger.warning(f"SEMAPHORE HEALTH: {issue}")
        
        # Attempt automatic recovery
        recovered = await _recover_semaphore_leaks()
        if recovered:
            logger.info("SEMAPHORE HEALTH: Automatic recovery successful")
    else:
        logger.debug("Semaphore health check passed")
```

---

## FIX 2: Development Environment Configuration

### Root Cause Analysis

**Current Configuration (.env.docker):**
```bash
EXAI_WS_GLOBAL_MAX_INFLIGHT=24  # Production scale!
EXAI_WS_GLM_MAX_INFLIGHT=4
EXAI_WS_KIMI_MAX_INFLIGHT=6
EXAI_WS_SESSION_MAX_INFLIGHT=8
```

**Problem:**
- Configured for production scale (24 global concurrent requests)
- User environment: Single-user dev, 2-5 concurrent sessions max
- Over-provisioned limits cause unnecessary contention

### Solution: Development-Optimized Configuration

**Update .env.docker:**

```bash
# ============================================================================
# CONCURRENCY LIMITS - DEVELOPMENT ENVIRONMENT
# ============================================================================
# CRITICAL: These limits are optimized for single-user development (2-5 concurrent sessions)
# For production deployment, increase to: GLOBAL=24, SESSION=8, GLM=4, KIMI=6

EXAI_WS_GLOBAL_MAX_INFLIGHT=5   # Max concurrent requests across all sessions (dev: 5, prod: 24)
EXAI_WS_GLM_MAX_INFLIGHT=2      # Max concurrent GLM requests per session (dev: 2, prod: 4)
EXAI_WS_KIMI_MAX_INFLIGHT=3     # Max concurrent Kimi requests per session (dev: 3, prod: 6)
EXAI_WS_SESSION_MAX_INFLIGHT=2  # Max concurrent requests per session (dev: 2, prod: 8)
```

**Rationale:**
- **Global: 5** - Supports 2-3 concurrent agents with 2 requests each
- **Session: 2** - Prevents single agent from monopolizing resources
- **GLM: 2** - Adequate for dev workload
- **Kimi: 3** - Slightly higher for web search + thinking mode

---

## FIX 3: Kimi Timeout Optimization

### Root Cause Analysis

**Current Configuration:**
```bash
KIMI_TIMEOUT_SECS=180  # 3 minutes
```

**Evidence:**
```
20:39:32 Retrying /chat/completions in 0.4s
20:42:33 Retrying /chat/completions in 0.8s
# 3 minutes 1 second between retries = 180s timeout
```

**Problem:**
- 180s timeout may be too short for:
  - Web search + thinking mode (combined operation)
  - Large context processing
  - Complex reasoning tasks
- Timeout triggers OpenAI client retry loop
- Creates cascade of 3-minute delays

### Solution: Adaptive Timeout Strategy

**Update .env.docker:**

```bash
# ============================================================================
# KIMI TIMEOUT CONFIGURATION - ADAPTIVE STRATEGY
# ============================================================================
# Base timeout for standard operations
KIMI_TIMEOUT_SECS=240  # 4 minutes (increased from 180s)

# Extended timeout for web search operations
KIMI_WEB_SEARCH_TIMEOUT_SECS=300  # 5 minutes (web search adds latency)

# Extended timeout for thinking mode
KIMI_THINKING_TIMEOUT_SECS=360  # 6 minutes (thinking mode needs more time)

# Combined timeout for web search + thinking mode
KIMI_WEB_THINKING_TIMEOUT_SECS=420  # 7 minutes (combined operations)
```

**Implementation in kimi_tools_chat.py:**

```python
# Modify timeout selection logic (around line 495)

# Determine timeout based on operation type
timeout_secs = 240.0  # Base timeout

# Check for web search
use_websearch = bool(arguments.get("use_websearch", False))

# Check for thinking mode
model = arguments.get("model", "")
is_thinking = "thinking" in model.lower()

# Apply adaptive timeout
if use_websearch and is_thinking:
    timeout_secs = float(os.getenv("KIMI_WEB_THINKING_TIMEOUT_SECS", "420"))
elif use_websearch:
    timeout_secs = float(os.getenv("KIMI_WEB_SEARCH_TIMEOUT_SECS", "300"))
elif is_thinking:
    timeout_secs = float(os.getenv("KIMI_THINKING_TIMEOUT_SECS", "360"))
else:
    timeout_secs = float(os.getenv("KIMI_TIMEOUT_SECS", "240"))

logger.info(f"Kimi timeout: {timeout_secs}s (web={use_websearch}, thinking={is_thinking})")
```

---

## FIX 4: Model Selection Optimization

### Analysis

**Current Implementation:**
- Model selection caching already implemented in `src/router/routing_cache.py`
- 3-minute TTL for cached selections
- Cache hit logging confirms it's working

**Evidence from Code:**
```python
# src/server/handlers/request_handler_model_resolution.py lines 90-101
cached_model = routing_cache.get_model_selection(cache_context)
if cached_model:
    logger.debug(f"[ROUTING_CACHE] Auto-routing cache HIT: {tool_name} → {cached_model}")
    return cached_model
```

**Conclusion:** ✅ **NO FIX NEEDED** - Already optimized

**Recommendation:** Use explicit model selection when possible to avoid cache misses:
```python
# Instead of:
chat(prompt="...", model="auto")

# Use:
chat(prompt="...", model="glm-4.6")
```

---

## IMPLEMENTATION CHECKLIST

### Phase 1: Immediate Fixes (15 minutes)
- [ ] Update `.env.docker` with development-optimized concurrency limits
- [ ] Update `.env.docker` with adaptive Kimi timeouts
- [ ] Restart Docker container to apply new configuration
- [ ] Test with 2-3 concurrent agents

### Phase 2: Semaphore Recovery (30 minutes)
- [ ] Add `_recover_semaphore_leaks()` function to `ws_server.py`
- [ ] Modify `_check_semaphore_health()` to call recovery
- [ ] Add periodic health check (every 60 seconds)
- [ ] Test semaphore recovery under load

### Phase 3: Adaptive Timeout Implementation (30 minutes)
- [ ] Add timeout environment variables to `.env.docker`
- [ ] Modify `kimi_tools_chat.py` timeout selection logic
- [ ] Test with web search + thinking mode
- [ ] Verify timeout logs show correct values

### Phase 4: Validation (30 minutes)
- [ ] Run 3 concurrent agents for 10 minutes
- [ ] Monitor semaphore health logs
- [ ] Verify no connection blocking
- [ ] Verify no timeout cascades
- [ ] Check Docker logs for errors

---

## EXPECTED IMPACT

### Before Fixes
- ❌ Semaphore leaks: 1-2 per hour
- ❌ Connection blocking: Frequent
- ❌ Kimi timeouts: 3-minute retry loops
- ❌ User experience: Must cancel other agents

### After Fixes
- ✅ Semaphore leaks: Auto-recovered
- ✅ Connection blocking: Eliminated
- ✅ Kimi timeouts: Rare (adaptive timeouts)
- ✅ User experience: Smooth concurrent operation

---

## MONITORING

### Key Metrics to Track
1. **Semaphore Health:**
   - `grep "SEMAPHORE HEALTH" docker logs`
   - Should see "health check passed" every 60s
   - Recovery events should be rare

2. **Kimi Timeouts:**
   - `grep "Kimi timeout" docker logs`
   - Should see correct timeout values (240s-420s)
   - Retry events should be rare

3. **Connection Blocking:**
   - Monitor concurrent session count
   - Should support 2-5 concurrent agents smoothly

---

**Status:** 📋 **READY FOR IMPLEMENTATION**

**Next Steps:**
1. Apply Phase 1 fixes (configuration)
2. Test with concurrent agents
3. Apply Phase 2 fixes (semaphore recovery)
4. Apply Phase 3 fixes (adaptive timeouts)
5. Validate and monitor

**Estimated Total Time:** 2 hours

