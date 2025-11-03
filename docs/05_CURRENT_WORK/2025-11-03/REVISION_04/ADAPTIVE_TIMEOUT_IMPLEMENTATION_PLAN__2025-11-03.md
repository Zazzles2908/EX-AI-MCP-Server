# Adaptive Timeout Architecture - Implementation Plan

**Date:** 2025-11-03  
**Status:** Planning Phase  
**Continuation ID:** 49196783-dd79-4970-95e8-2634c0b09c41 (18 exchanges remaining)

---

## Executive Summary

Implementing **adaptive timeout architecture** to replace hardcoded timeout assumptions with **data-driven, model-aware, self-correcting timeouts**. This fixes the root cause of K2 response transmission failures where reasoning models (258s processing time) exceed the system's 45-90s timeout assumptions.

---

## Critical Context

### Provider Architecture
- **Kimi Models (K2, etc.)**: Use **OpenAI SDK** via `src/providers/openai_compatible.py`
- **GLM Models**: Use **Z.ai SDK** via `src/providers/glm.py` and `src/providers/glm_chat.py`
- Both providers need adaptive timeout support

### Current Problem
- **Timeout Hierarchy**: Tool (45s) → Shim (90s) → Daemon (450s)
- **K2 Reality**: 258 seconds (4.3 minutes) for complex reasoning
- **Result**: Shim times out before K2 completes, connection closes, response lost

### Root Cause
System designed under **tacit assumption**: "No tool will ever need more than 45-90 seconds"  
**K2 is not a tool** — it's a **reasoning engine** whose **unit of work is minutes**, not seconds.

---

## Implementation Timeline

### Day 0 (Today) - Foundation
**Goal:** Create adaptive timeout engine with feature flag

**Deliverables:**
1. `src/core/adaptive_timeout.py` - Core engine with unit tests
2. Integration point in `run_ws_shim.py` - Wrapped behind feature flag
3. Environment variable `ADAPTIVE_TIMEOUT_ENABLED` (default: false)

**Success Criteria:**
- [ ] Engine can calculate adaptive timeouts from historical data
- [ ] Falls back to static timeouts when no history available
- [ ] Feature flag allows safe rollout
- [ ] Unit tests cover edge cases (empty history, outliers, cold start)

---

### Day 1 - Data Collection & Observability + Estimate API Integration
**Goal:** Record actual model performance, expose metrics, and integrate predictive timeout calculation

**Deliverables:**
1. **Estimate API Integration (MUST-HAVE - K2 Priority 1)**
   - Integrate Moonshot `/estimate` endpoint for K2 requests
   - Calculate predicted duration: `estimated_tokens / tokens_per_second`
   - Apply adaptive timeout with estimate-based base
   - Add metrics: `estimated_tokens`, `actual_tokens`, `estimate_accuracy`
   - Track prediction accuracy: `(actual_duration / estimated_duration)` ratio

2. **Data Collection Infrastructure**
   - Post-call hook in `request_router.py` to record durations
   - Duration validation (0 < duration < 3600)
   - Provider-specific timeout defaults (Kimi: 300s/P95, GLM: 120s/P90)

3. **Observability**
   - `/metrics` endpoint exposing `kimi_adaptive_timeout_seconds` histogram
   - Prometheus integration for canary testing
   - Health check endpoint
   - Confidence scores in logs
   - Support for both OpenAI SDK (Kimi) and Z.ai SDK (GLM) providers

**Success Criteria:**
- [ ] Estimate API integrated for K2 requests (50-100ms overhead acceptable)
- [ ] Predicted duration calculated before each K2 request
- [ ] Estimate accuracy tracked and logged
- [ ] Fallback to static timeout if estimate API fails
- [ ] Every completed call records (model, prompt_tokens, completion_tokens, duration, estimated_tokens)
- [ ] Metrics endpoint shows adaptive vs actual vs estimated duration
- [ ] Can monitor prediction accuracy in real-time
- [ ] Both Kimi and GLM models tracked separately
- [ ] Health check endpoint returns system status

---

### Day 2-3 - File Handling & Request Type Differentiation
**Goal:** Separate file-based vs text-only request tracking for accurate timeout predictions

**Deliverables:**
1. **Request Type Classification (SHOULD-HAVE - K2 Priority 2)**
   - Implement `RequestType` enum: `FILE_BASED`, `FILE_REUSE`, `TEXT_ONLY`
   - Separate duration tracking for each request type
   - Add `file_size` and `file_reuse` metrics
   - Implement file-specific timeout calculations
   - Cache file upload IDs and correlate with durations

2. **File Upload Integration**
   - Track file upload time vs processing time separately
   - Detect cached file reuse patterns
   - Correlate file size with processing duration

**Success Criteria:**
- [ ] Request type correctly classified for all requests
- [ ] File-based requests tracked separately from text-only
- [ ] File upload timeouts don't contaminate text-only metrics
- [ ] File size correlation with duration measured
- [ ] Cached file reuse detected and tracked

---

### Day 3-4 - Persistence, Cold Start Resilience & Debugging Infrastructure
**Goal:** Survive restarts with yesterday's performance data + production debugging tools

**Deliverables:**
1. **Persistence Layer**
   - Supabase migration: `model_timeout_profile` table
   - Nightly cron job to aggregate and persist P95 + stddev
   - Boot-time seeding from Supabase
   - Fallback to static 300s if DB unavailable
   - Timeout source tracking in Supabase

2. **MoonPalace Integration (SHOULD-HAVE - K2 Priority 3)**
   - Add MoonPalace API calls when timeouts occur
   - Capture request/response details for analysis
   - Build debugging dashboard for timeout patterns
   - Async fire-and-forget pattern (no production impact)

3. **Debug Mode**
   - Detailed request logging for timeout analysis
   - Timeout analysis dashboard
   - Production debugging without performance impact

**Success Criteria:**
- [ ] Cold pods start with yesterday's timeout curve
- [ ] Graceful degradation if Supabase unavailable
- [ ] Nightly aggregation runs without blocking operations
- [ ] Historical data retained for analysis
- [ ] Cold start with partial DB data handled correctly
- [ ] MoonPalace integration captures timeout events
- [ ] Debug dashboard accessible for timeout analysis

---

### Day 5 - Canary Rollout & Validation
**Goal:** Safe production rollout with monitoring

**Deliverables:**
1. **Gradual Rollout**
   - Enable `ADAPTIVE_TIMEOUT_ENABLED=1` for 10% traffic (K2 recommendation: start at 10%)
   - Monitor prediction error: `kimi_adaptive_timeout_seconds` vs `kimi_actual_duration_seconds`
   - Monitor estimate accuracy: `estimated_duration` vs `actual_duration`
   - Rollout to 100% once prediction error < 15% for 2 business days

2. **Monitoring & Alerting**
   - Dashboard metrics for timeout source distribution
   - Sample count tracking per model
   - Prediction error bucketing
   - Alert on low confidence scenarios
   - Track timeout override usage

3. **Documentation**
   - Ops team documentation
   - Troubleshooting guide
   - Rollback procedures

**Success Criteria:**
- [ ] 10% canary shows < 15% prediction error
- [ ] Estimate API accuracy > 85%
- [ ] No increase in timeout-related errors
- [ ] K2 responses successfully reach clients
- [ ] Fast queries don't waste time with excessive timeouts
- [ ] Monitoring dashboard shows all metrics
- [ ] Ops team trained on new system

---

## Moonshot/Kimi Feature Integration Analysis

**Date:** 2025-11-03
**K2 Analysis:** Continuation ID 49196783-dd79-4970-95e8-2634c0b09c41 (14 exchanges remaining)

### MUST-HAVE: Estimate API Integration (Day 1)

**Why Critical:**
- ✅ Solves cold-start problem (no more guessing for new patterns)
- ✅ Dynamic adjustment (large documents get longer timeouts automatically)
- ✅ Resource optimization (small requests get tighter timeouts)

**Implementation Pattern:**
```python
# 1. Get token estimate BEFORE making request
estimate = await kimi_client.estimate(messages=messages, model=model)

# 2. Calculate predicted duration
predicted_tokens = estimate.total_tokens
tokens_per_second = get_historical_tps(model)
predicted_duration = predicted_tokens / tokens_per_second

# 3. Apply adaptive timeout with estimate
timeout = calculate_adaptive_timeout(
    base_timeout=predicted_duration * 1.2,  # 20% buffer
    recent_history=get_recent_durations(model),
    burst_protection=True
)
```

**Key Considerations:**
- **Overhead**: ~50-100ms latency per estimate call
- **Caching**: Consider caching estimates for similar message patterns
- **Fallback**: Always have fallback timeout if estimate API fails
- **Accuracy Monitoring**: Track estimate vs actual, adjust algorithm if consistently off

### SHOULD-HAVE: File Upload Persistence (Day 2-3)

**Request Type Classification:**
```python
class RequestType(Enum):
    FILE_BASED = "file_based"      # First upload + processing
    FILE_REUSE = "file_reuse"      # Cached file processing
    TEXT_ONLY = "text_only"        # No files involved
```

**Value**: Prevents file upload timeouts from contaminating text-only metrics.

**Implementation:**
- Track file upload time vs processing time separately
- Detect cached file reuse patterns
- Correlate file size with processing duration
- Separate duration tracking for each request type

### SHOULD-HAVE: MoonPalace Integration (Day 3-4)

**Purpose**: Production debugging (not core algorithm)

**Implementation:**
- Add MoonPalace API calls when timeouts occur
- Capture request/response details for analysis
- Build debugging dashboard for timeout patterns
- Use async fire-and-forget pattern (no production impact)

**Caution**: Don't let debugging tools impact production performance.

### NICE-TO-HAVE: Future Enhancements

**tool_choice Analysis:**
- Monitor as metric dimension
- Analyze after data collection
- Low priority unless specific patterns emerge

**Kimi CLI Insights:**
- Study patterns for potential optimizations
- CLI optimized for interactive use (short timeouts, retry-heavy)
- May not apply to server-to-server patterns

---

## Technical Specifications

### Adaptive Timeout Engine

**Core Algorithm:**
```python
class AdaptiveTimeoutEngine:
    def __init__(self):
        self.historical_durations = defaultdict(deque)  # model -> deque(maxlen=100)
        self.percentile_threshold = 95
    
    def get_adaptive_timeout(self, model: str, base_timeout: int) -> int:
        durations = self.historical_durations.get(model, [])
        if not durations:
            return base_timeout
        
        # Clipped P95 - discard top 1% outliers before percentile calc
        sorted_durations = sorted(durations)
        clip_index = int(len(sorted_durations) * 0.99)
        clipped = sorted_durations[:clip_index]
        
        p95 = np.percentile(clipped, self.percentile_threshold)
        buffer = max(30, p95 * 0.2)  # 20% buffer or 30s minimum
        adaptive = int(p95 + buffer)
        
        return max(base_timeout, adaptive)  # Never go below base
```

**Predictive Layer (Optional Enhancement):**
```python
def predict_timeout(self, model: str, prompt_tokens: int, max_tokens: int) -> int:
    expected_tokens = prompt_tokens + max_tokens
    tokens_per_sec_ewma = self._get_tokens_per_sec_ewma(model)
    predicted_duration = expected_tokens / tokens_per_sec_ewma
    return int(predicted_duration * 1.3 + 20)  # 30% buffer + 20s base
```

### Hierarchical Timeout Budget

**Three-Tier Architecture:**
1. **Edge (Cloudflare)**: 100s hard limit (immovable)
2. **Gateway (nginx)**: `adaptive_timeout + 5s`
   - Returns **202 Accepted** with `Location: /poll/{call-id}` when adaptive > 90s
3. **Worker (uvicorn + shim)**: Uses **adaptive** value

### Provider-Specific Integration

**Kimi Models (OpenAI SDK):**
- Integration point: `src/providers/kimi_chat.py`
- Timeout parameter: `timeout_seconds` in `chat_completions_create_with_session()`
- Session manager: `ConcurrentSessionManager` with adaptive timeout

**GLM Models (Z.ai SDK):**
- Integration point: `src/providers/glm_chat.py`
- Timeout parameter: `timeout` in GLM SDK calls
- Session manager: Similar pattern to Kimi

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| **Outlier poison** (one 20-min call blows P95) | Use **clipped P95** – discard top 1% samples before percentile calc |
| **Memory leak in circular buffer** | Pre-allocated `deque(maxlen=100)`; 100 × 4 floats ≈ 3KB per model |
| **Thundering herd on cold start** | Seed from Supabase at boot; fallback to static 300s if DB down |
| **SLA dashboards expect 60s ceiling** | Add `adaptive_timeout_value` label to Prometheus; dashboards can filter |
| **Provider-specific timeout formats** | Abstract timeout application in provider base classes |

---

## Files to Modify

### New Files
- `src/core/adaptive_timeout.py` - Core engine
- `src/core/timeout_storage.py` - Supabase persistence
- `tests/unit/test_adaptive_timeout.py` - Unit tests
- `migrations/YYYYMMDD_create_model_timeout_profile.sql` - Supabase schema

### Modified Files
- `scripts/runtime/run_ws_shim.py` - Integrate adaptive timeout
- `src/daemon/ws/request_router.py` - Record durations post-call
- `src/providers/kimi_chat.py` - Apply adaptive timeout (OpenAI SDK)
- `src/providers/glm_chat.py` - Apply adaptive timeout (Z.ai SDK)
- `config/timeouts.py` - Add adaptive timeout configuration
- `.env.docker` - Add `ADAPTIVE_TIMEOUT_ENABLED` flag

---

## Validation Checklist

### Day 0 Validation
- [ ] `AdaptiveTimeoutEngine` class created with all methods
- [ ] Unit tests pass (empty history, outliers, cold start, clipping)
- [ ] Integration in `run_ws_shim.py` behind feature flag
- [ ] `ADAPTIVE_TIMEOUT_ENABLED=false` by default
- [ ] K2 review confirms completeness

### Day 1 Validation
- [ ] **Estimate API Integration**
  - [ ] Estimate API called before K2 requests
  - [ ] Predicted duration calculated correctly
  - [ ] Estimate accuracy tracked and logged
  - [ ] Fallback to static timeout works when estimate fails
  - [ ] Overhead < 100ms per estimate call
- [ ] **Data Collection**
  - [ ] Post-call hook records durations for both Kimi and GLM
  - [ ] Duration validation (0 < duration < 3600) working
  - [ ] Provider-specific defaults applied correctly
- [ ] **Observability**
  - [ ] Metrics endpoint accessible at `/metrics`
  - [ ] Prometheus histogram shows adaptive vs actual vs estimated
  - [ ] Health check endpoint returns status
  - [ ] Confidence scores logged correctly
  - [ ] Can observe prediction accuracy in real-time
- [ ] K2 review confirms Day 1 complete

### Day 2-3 Validation
- [ ] **Request Type Classification**
  - [ ] RequestType enum implemented correctly
  - [ ] File-based requests classified correctly
  - [ ] File reuse detected and tracked
  - [ ] Text-only requests tracked separately
- [ ] **File Handling**
  - [ ] File upload time tracked separately
  - [ ] File size correlation measured
  - [ ] Cached file reuse patterns detected
  - [ ] File-specific timeout calculations working
- [ ] K2 review confirms Day 2-3 complete

### Day 3-4 Validation
- [ ] **Persistence Layer**
  - [ ] Supabase table `model_timeout_profile` created
  - [ ] Nightly cron job configured and tested
  - [ ] Cold start loads yesterday's data successfully
  - [ ] Fallback to 300s works when Supabase unavailable
  - [ ] Timeout source tracking in Supabase working
  - [ ] Cold start with partial DB data handled
- [ ] **MoonPalace Integration**
  - [ ] MoonPalace API calls on timeout events
  - [ ] Request/response details captured
  - [ ] Debugging dashboard accessible
  - [ ] Async fire-and-forget pattern working
  - [ ] No production performance impact
- [ ] **Debug Mode**
  - [ ] Detailed request logging working
  - [ ] Timeout analysis dashboard functional
- [ ] K2 review confirms Day 3-4 complete

### Day 5 Validation
- [ ] **Gradual Rollout**
  - [ ] 10% canary enabled successfully
  - [ ] Prediction error < 15% observed
  - [ ] Estimate API accuracy > 85%
  - [ ] No timeout-related error increase
  - [ ] K2 responses reach clients successfully
  - [ ] Fast queries don't waste time
- [ ] **Monitoring & Alerting**
  - [ ] Dashboard shows timeout source distribution
  - [ ] Sample count tracking per model working
  - [ ] Prediction error bucketing functional
  - [ ] Low confidence alerts configured
  - [ ] Timeout override usage tracked
- [ ] **Documentation**
  - [ ] Ops team documentation complete
  - [ ] Troubleshooting guide written
  - [ ] Rollback procedures documented
  - [ ] Ops team trained
- [ ] K2 review confirms production readiness

---

## Next Steps

1. **Submit this plan to K2 for validation**
2. **Address any gaps K2 identifies**
3. **Begin Day 0 implementation**
4. **Daily check-ins with K2 for validation**

---

## Questions for K2

1. Does this plan cover all requirements for the adaptive timeout architecture?
2. Are there any missing components or considerations?
3. Is the provider-specific integration (OpenAI SDK vs Z.ai SDK) properly addressed?
4. Are the success criteria sufficient for each day?
5. What additional validation steps should be included?
6. Should we implement the predictive layer immediately or defer to later?
7. Any concerns about the hierarchical timeout budget approach?

---

## K2 Validation Results (2025-11-03)

**Status:** ✅ **APPROVED WITH ENHANCEMENTS**

### ✅ What K2 Approved
- Clipped P95 algorithm (discard top 1% outliers)
- Feature flag strategy with `ADAPTIVE_TIMEOUT_ENABLED`
- Dual-channel seeding (runtime + persistent)
- Provider-specific integration points
- 5-day timeline is realistic and well-paced
- Canary rollout approach (5% → 100%)

### ⚠️ K2 Adjustments Required

#### 1. Memory Management Enhancement
```python
# Add explicit cleanup for model retirement
def retire_model(self, model: str):
    if model in self.historical_durations:
        del self.historical_durations[model]
```

#### 2. Hierarchical Timeout Budget Edge Case
```python
def get_edge_timeout(self, adaptive_timeout: int) -> int:
    if adaptive_timeout > 95:  # 5s buffer for network overhead
        return 95  # Return 202 Accepted with polling
    return adaptive_timeout
```

#### 3. Provider Integration Specificity
**Z.ai SDK (GLM) uses milliseconds:**
```python
# In glm_chat.py - Z.ai uses milliseconds for timeout
timeout_ms = int(adaptive_timeout * 1000)
response = await self.client.chat.completions.create(
    timeout=timeout_ms,  # Note: milliseconds, not seconds
    ...
)
```

### ❌ K2 Identified Missing Components

#### 1. Error Handling Strategy
```python
def get_adaptive_timeout_safe(self, model: str, base_timeout: int) -> int:
    try:
        return self.get_adaptive_timeout(model, base_timeout)
    except Exception as e:
        logger.error(f"Adaptive timeout calc failed for {model}: {e}")
        return base_timeout  # Graceful fallback
```

#### 2. Model Version Handling
```python
def normalize_model_name(self, model: str) -> str:
    # k2-2025-11-03 → k2 (strip date suffixes)
    # gpt-4-turbo-2025-04 → gpt-4-turbo
    return re.sub(r'-\d{4}-\d{2}-\d{2}$', '', model)
```

#### 3. Burst Protection
```python
def apply_burst_protection(self, new_timeout: int, old_timeout: int) -> int:
    max_change = 2.0  # Don't allow >2x increase in single update
    return min(new_timeout, int(old_timeout * max_change))
```

#### 4. Testing Strategy Gaps
- Cold start with partial DB data
- Provider timeout format validation
- Edge case: model with <5 historical samples
- Concurrent access to circular buffer

### 🚀 K2 Additional Recommendations

#### 1. Defer Predictive Layer
Implement basic clipped P95 first. Add predictive layer in Week 2 after stability proven.

#### 2. Emergency Timeout Override
```python
# In config or environment
EMERGENCY_TIMEOUT_OVERRIDE = {
    "k2": 300,  # seconds
    "gpt-4": 120
}
```

#### 3. Latency Attribution
```python
timeout_metadata = {
    "source": "adaptive",  # or "static", "emergency", "fallback"
    "confidence": 0.95,    # based on sample count
    "samples_used": 42
}
```

#### 4. Dashboard Integration
```python
# New metrics to expose
kimi_adaptive_timeout_source_total{source="adaptive|static|emergency"}
kimi_adaptive_timeout_samples_count{model="k2"}
kimi_adaptive_timeout_prediction_error_bucket
```

---

## Updated Implementation Requirements

### Day 0 - Enhanced Foundation
**Additional Requirements:**
- [ ] Error handling with graceful fallback
- [ ] Model version normalization
- [ ] Burst protection mechanism
- [ ] Emergency timeout override support
- [ ] Model retirement cleanup

### Day 1-2 - Enhanced Data Collection
**Additional Requirements:**
- [ ] Latency attribution metadata
- [ ] Provider timeout format validation (seconds vs milliseconds)
- [ ] Concurrent access protection for circular buffer
- [ ] Edge case handling for <5 samples

### Day 3-4 - Enhanced Persistence
**Additional Requirements:**
- [ ] Cold start with partial DB data handling
- [ ] Timeout source tracking in Supabase

### Day 5 - Enhanced Observability
**Additional Requirements:**
- [ ] Dashboard metrics for timeout source distribution
- [ ] Sample count tracking per model
- [ ] Prediction error bucketing

---

**Status:** ✅ **READY TO PROCEED WITH DAY 0 IMPLEMENTATION**

K2 confirms: "The plan is comprehensive and technically sound. The 5-day timeline is achievable, and the clipped P95 approach will immediately solve the K2 timeout issue while providing a foundation for future enhancements."

