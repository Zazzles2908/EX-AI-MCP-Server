# EXAI Unpredictability Root Cause Analysis
**Date:** 2025-10-21  
**Investigator:** Claude (Augment Agent) + EXAI Consultation  
**Status:** 🔍 ACTIVE - Implementation in Progress

---

## Executive Summary

**User Problem:** "Sometimes when you use EXAI you get flop response and sometimes you get really good answers. I can't have this unpredictability for production."

**Root Cause Analysis:** EXAI identified 6 categories of unpredictability sources, ranked by likelihood and impact.

**Top Priority Issues:**
1. **Model Selection Inconsistency** (HIGH likelihood, HIGH impact)
2. **Timeout/Error Recovery Issues** (HIGH likelihood, HIGH impact)
3. **Prompt Building Variability** (MEDIUM likelihood, HIGH impact)

---

## Detailed Analysis (from EXAI Consultation)

### 1. Model Selection Issues (CRITICAL)

#### Recent Model Change Impact
- **Change:** glm-4.6 → glm-4.5-flash, thinking mode high → medium
- **Reason:** Prevent Augment Code timeout (10-30s limit)
- **Side Effect:** Likely reduced response quality
- **Location:** `tools/workflow/expert_analysis.py` lines 595-596

#### Auto-Upgrade Inconsistency
- **Behavior:** System automatically upgrades models when thinking mode is requested but not supported
- **Control:** `EXPERT_ANALYSIS_AUTO_UPGRADE` environment variable
- **Problem:** Users unaware their model was changed mid-call
- **Location:** `tools/workflow/expert_analysis.py` lines 735-755

**Unpredictability Sources:**
1. Model used might change between calls based on thinking mode requirements
2. Different thinking-capable models have different quality levels
3. Silent model upgrades/downgrades without user awareness

**Recommended Fixes:**
1. ✅ Make model selection explicit - don't auto-upgrade silently
2. ✅ Document model quality differences clearly
3. ✅ Add model logging - log exactly which model was used for each request

---

### 2. Timeout/Error Recovery Issues (CRITICAL)

#### Timeout Handling Inconsistencies
- **Different timeout values:** Different tools may override `get_expert_timeout_secs()` with different values
- **Async vs sync paths:** Two different code paths for async and sync providers
- **Incomplete error handling:** Some exceptions might not be properly caught
- **Location:** `tools/workflow/expert_analysis.py` lines 860-960

#### Duplicate Call Prevention Race Conditions
- **Complex lock handling:** Nested acquisition attempts
- **Multiple strategies:** "SIMPLIFIED DUPLICATE PREVENTION" section overrides previous logic
- **Non-atomic cache operations:** Potential race conditions
- **Location:** `tools/workflow/expert_analysis.py` lines 635-695

**Unpredictability Sources:**
1. Timeout behavior varies by tool and provider type
2. Race conditions in duplicate call prevention
3. Undefined return states on certain exceptions

**Recommended Fixes:**
1. ✅ Standardize timeout handling across all provider types
2. ✅ Simplify duplicate prevention - use single, clear caching strategy
3. ✅ Add comprehensive error logging for all exceptions

---

### 3. Prompt Building Issues (HIGH IMPACT)

#### Variable-Length Prompts
**Factors affecting prompt size:**
1. Number of relevant files being analyzed
2. Whether file contents are embedded (`EXPERT_ANALYSIS_INCLUDE_FILES`)
3. Size of consolidated findings across workflow steps

#### Prompt Truncation Risks
- **No explicit handling:** Prompts might be silently truncated when hitting token limits
- **Missing context:** Truncated prompts lead to incomplete information
- **Poor responses:** Model can't provide good analysis without full context

**Unpredictability Sources:**
1. Silently truncated prompts
2. Missing context leading to poor responses
3. Incomplete information being sent to the model

**Recommended Fixes:**
1. ✅ Add prompt size monitoring - log sizes and warn when approaching limits
2. ✅ Implement explicit truncation - smart truncation preserving important info
3. ✅ Add prompt validation - check completeness before sending

---

### 4. Provider-Level Issues (MEDIUM IMPACT)

#### Websearch Adapter Inconsistencies
- **Complex fallback logic:** Different behavior when websearch isn't supported
- **Provider-specific behavior:** Different providers handle websearch differently
- **Silent failures:** Websearch requested but not supported
- **Location:** `tools/workflow/expert_analysis.py` lines 845-860

#### No Quota/Rate Limit Handling
**Missing:**
1. API quota exhaustion handling
2. Rate limiting from providers
3. Network connectivity issue handling

**Recommended Fixes:**
1. ✅ Add provider health checks - periodic health monitoring
2. ✅ Implement retry logic - exponential backoff for transient failures
3. ✅ Add quota monitoring - track usage and warn when approaching limits

---

### 5. Configuration Issues (MEDIUM IMPACT)

#### Environment Variable Dependencies
**Variables affecting behavior:**
1. `EXPERT_ANALYSIS_ENABLED`
2. `EXPERT_ANALYSIS_INCLUDE_FILES`
3. `EXPERT_ANALYSIS_THINKING_MODE`
4. `EXPERT_ANALYSIS_AUTO_UPGRADE`
5. `USE_MESSAGE_ARRAYS`
6. `USE_ASYNC_PROVIDERS`

#### Temperature Validation
- **Silent adjustments:** System silently adjusts temperatures out of bounds
- **Model-specific constraints:** Different models have different temperature limits
- **User unawareness:** Users don't know their temperature was adjusted
- **Location:** `tools/workflow/expert_analysis.py` lines 830-835

**Recommended Fixes:**
1. ✅ Document all configuration options comprehensively
2. ✅ Add configuration validation at startup
3. ✅ Log configuration changes when values are adjusted

---

### 6. Caching/Deduplication Issues (LOW LIKELIHOOD)

#### Cache Key Determinism
**Cache key generation uses:**
1. Tool name
2. Request ID
3. Hash of consolidated findings

**Potential issues:**
1. Hash changes due to ordering differences
2. Hash function produces different results across Python versions
3. Request ID not consistent across related requests
- **Location:** `tools/workflow/expert_analysis.py` lines 640-645

#### No Cache Invalidation Strategy
**Problems:**
1. Stale results being returned
2. Memory leaks from unbounded cache growth
3. Inconsistent behavior when underlying data changes

**Recommended Fixes:**
1. ✅ Implement cache key normalization - ensure consistency
2. ✅ Add cache TTL - time-based expiration
3. ✅ Add cache size limits - prevent unbounded growth

---

## Implementation Plan

### Phase 1: Immediate (Critical) - TODAY
1. ✅ Integrate SemaphoreTracker into request_router.py
2. ✅ Integrate PerformanceProfiler into expert_analysis.py
3. ⏳ Add explicit model logging
4. ⏳ Standardize timeout handling
5. ⏳ Simplify duplicate call prevention

### Phase 2: Short Term (High) - THIS WEEK
1. Add prompt size monitoring
2. Implement smart prompt truncation
3. Add prompt validation
4. Document all configuration options
5. Add configuration validation at startup

### Phase 3: Medium Term (Medium) - NEXT WEEK
1. Add provider health checks
2. Implement retry logic with exponential backoff
3. Add quota monitoring
4. Implement cache TTL
5. Add cache size limits

### Phase 4: Long Term (Low) - FUTURE
1. Enhanced monitoring dashboard
2. Automated baseline establishment
3. Alerting mechanisms for unusual patterns
4. Integration with CI/CD for documentation validation

---

## Diagnostic Tools Implemented

### 1. SemaphoreTracker
**File:** `src/daemon/middleware/semaphore_tracker.py`

**Features:**
- Full lifecycle tracking with stack traces
- Thread ID tracking
- Leak detection with configurable threshold (default 60s)
- Periodic diagnostic reporting
- Global tracker instance for easy integration

**Usage:**
```python
tracker = get_global_tracker()
sem_id = await tracker.track_acquire("global_sem")
# ... use semaphore ...
await tracker.track_release(sem_id, "global_sem")
```

### 2. PerformanceProfiler
**File:** `src/utils/performance_profiler.py`

**Features:**
- Named checkpoint system
- Automatic duration calculation between phases
- Metadata attachment (e.g., prompt size, response size)
- Context manager and decorator support
- Diagnostic reporting

**Usage:**
```python
profiler = PerformanceProfiler("expert_analysis")
profiler.checkpoint("start")
profiler.checkpoint("prompt_built", metadata={"size": len(prompt)})
profiler.checkpoint("api_complete")
profiler.log_report()
```

---

## Next Steps

1. **Complete diagnostic integration** - Add tracking to all semaphore acquisition points
2. **Run baseline collection** - Collect 1-2 days of operational data
3. **Analyze patterns** - Identify actual sources of unpredictability from real data
4. **Implement fixes** - Address issues in priority order based on evidence
5. **Verify improvements** - Measure consistency improvement with diagnostic tools

---

## Success Criteria

**Unpredictability is SOLVED when:**
1. ✅ Model selection is explicit and logged
2. ✅ Timeout handling is consistent across all tools
3. ✅ Prompt truncation is explicit and smart
4. ✅ Error recovery is predictable and logged
5. ✅ Configuration is validated and documented
6. ✅ Cache behavior is deterministic
7. ✅ Response quality variance is < 10% (measured over 100 calls)

---

## Status: IN PROGRESS

**Current Task:** Integrating SemaphoreTracker and PerformanceProfiler into production code.

**Next:** Add explicit model logging and standardize timeout handling.

