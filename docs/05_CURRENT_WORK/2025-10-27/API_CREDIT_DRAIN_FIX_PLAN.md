# API Credit Drain - Comprehensive Fix Plan
**Date:** 2025-10-27  
**Status:** ✅ ROOT CAUSE IDENTIFIED - READY FOR IMPLEMENTATION  
**EXAI Validation:** CONFIRMED - Analysis is 100% correct  
**Continuation ID:** `a864f2ff-462f-42f4-bef7-d40e4bddb314`

---

## 🎯 EXECUTIVE SUMMARY

**ROOT CAUSE CONFIRMED:** AI Auditor making **6,712 API calls** to GLM due to aggressive 5-second analysis interval.

**EXAI VALIDATION:** ✅ Analysis is completely correct. Additional issues identified beyond original findings.

**IMMEDIATE ACTION REQUIRED:** Disable AI Auditor or increase intervals dramatically.

---

## 🚨 CRITICAL FINDINGS

### Primary Issue: AI Auditor Configuration
```env
AUDITOR_ENABLED=true
AUDITOR_ANALYSIS_INTERVAL=5   # ← PROBLEM: API call every 5 seconds!
AUDITOR_BATCH_SIZE=10         # ← PROBLEM: Too small, triggers frequently
```

**Impact:**
- 6,712 API calls to GLM (glm-4.5-flash)
- ~12 calls/minute (every 5 seconds)
- Projected: ~17,280 calls/day if running 24/7
- Many parsing failures = wasted credits

### Additional Issues (EXAI Identified)
1. **No Event Filtering** - Every event buffered (including routine health checks)
2. **Verbose Prompts** - Using more tokens than necessary
3. **Empty Batch Analyses** - Analyzing batches with only 2-4 events
4. **Resource Leaks** - Unbounded observation cache, new Supabase connections per observation
5. **Ineffective Circuit Breaker** - 60s reset provides only brief relief

---

## 🔧 IMMEDIATE FIXES (Priority 1 - DO NOW)

### Option A: Disable AI Auditor (RECOMMENDED)
```env
# .env.docker
AUDITOR_ENABLED=false
```

**Restart container:**
```powershell
docker-compose restart
```

### Option B: Dramatically Increase Intervals
```env
# .env.docker
AUDITOR_ENABLED=true
AUDITOR_ANALYSIS_INTERVAL=300  # 5 minutes (was 5 seconds)
AUDITOR_BATCH_SIZE=50          # Larger batches (was 10)
AUDITOR_MODEL=glm-4.5-flash    # Keep free model
```

**Impact:** Reduces API calls from ~12/min to ~0.2/min (60x reduction)

---

## 📋 SHORT-TERM FIXES (Priority 2 - TODAY)

### 1. Add Event Severity Filtering
**File:** `utils/monitoring/ai_auditor.py`

```python
def _process_event(self, event: Dict):
    """Process incoming event with severity filtering"""
    # CRITICAL FIX: Only buffer events with severity >= WARNING
    if event.get('severity', 'info') not in ['warning', 'error', 'critical']:
        return  # Skip routine events
    
    self.event_buffer.append(event)
    self.stats["events_processed"] += 1
```

### 2. Implement Minimum Batch Size
**File:** `utils/monitoring/ai_auditor.py`

```python
def _should_analyze(self) -> bool:
    """Determine if we should analyze now"""
    time_elapsed = time.time() - self.last_analysis_time
    
    # CRITICAL FIX: Require minimum 20 events AND time interval
    return (
        len(self.event_buffer) >= max(self.batch_size, 20) and  # Min 20 events
        time_elapsed >= self.analysis_interval
    ) and not self.circuit_open
```

### 3. Add Hourly Rate Limiting
**File:** `utils/monitoring/ai_auditor.py`

```python
def __init__(self, ...):
    # ... existing code ...
    
    # CRITICAL FIX: Add rate limiting
    self.hourly_calls = 0
    self.max_hourly_calls = 60  # Max 1 per minute
    self.hour_start = time.time()

def _analyze_batch(self):
    """Analyze batch with rate limiting"""
    # Reset hourly counter if hour elapsed
    if time.time() - self.hour_start > 3600:
        self.hourly_calls = 0
        self.hour_start = time.time()
    
    # Check rate limit
    if self.hourly_calls >= self.max_hourly_calls:
        logger.warning("[AI_AUDITOR] Hourly rate limit reached, skipping analysis")
        return
    
    # ... existing analysis code ...
    self.hourly_calls += 1
```

---

## 🏗️ LONG-TERM IMPROVEMENTS (Priority 3 - THIS WEEK)

### 1. Smart Event Selection
```python
def _should_buffer_event(self, event: Dict) -> bool:
    """Intelligent event filtering"""
    # Always buffer errors and critical events
    if event.get('severity') in ['error', 'critical']:
        return True
    
    # Sample routine events (10% sampling)
    if event.get('type') == 'health_check':
        return random.random() < 0.1
    
    # Buffer performance anomalies
    if event.get('response_time_ms', 0) > 1000:
        return True
    
    return False
```

### 2. Adaptive Analysis Intervals
```python
def _get_next_interval(self) -> int:
    """Dynamic interval based on system activity"""
    if self.recent_errors > 5:
        return 60  # Analyze frequently during issues
    elif self.recent_errors > 0:
        return 300  # Moderate frequency
    else:
        return 900  # 15 minutes during normal operation
```

### 3. Cost Monitoring Dashboard
```python
class CostTracker:
    def __init__(self, daily_limit: float = 10.0):
        self.daily_limit = daily_limit
        self.daily_usage = 0.0
        self.call_count = 0
        
    def track_call(self, model: str, tokens: int):
        cost = self.get_cost(model, tokens)
        self.daily_usage += cost
        self.call_count += 1
        
        if self.daily_usage > self.daily_limit * 0.8:
            logger.warning(f"API cost at 80% of daily limit: ${self.daily_usage}")
```

---

## 🔮 FUTURE ENHANCEMENTS (Priority 4 - NEXT SPRINT)

### 1. Local AI Model Integration
Replace API calls with local inference:
- **Ollama** for local LLM hosting
- **Llama.cpp** for lightweight models
- **Cached responses** for common patterns

### 2. Provider-Level Rate Limiting
Add rate limiting at the provider level to prevent any tool from excessive API usage.

### 3. Comprehensive Cost Tracking
Implement real-time cost tracking across all providers (GLM, Kimi) with alerts and dashboards.

---

## 📊 IMPLEMENTATION CHECKLIST

### Immediate (Do Now)
- [ ] Disable AI Auditor in `.env.docker` (`AUDITOR_ENABLED=false`)
- [ ] Restart Docker container
- [ ] Verify API calls stop (check Docker logs)
- [ ] Document current API usage baseline

### Today
- [ ] Add event severity filtering to `ai_auditor.py`
- [ ] Implement minimum batch size requirement
- [ ] Add hourly rate limiting
- [ ] Test with `AUDITOR_ENABLED=true` and new settings
- [ ] Monitor API call reduction

### This Week
- [ ] Implement smart event selection
- [ ] Add adaptive analysis intervals
- [ ] Create cost monitoring dashboard
- [ ] Add Supabase table for cost tracking
- [ ] Set up alerts for excessive usage

### Next Sprint
- [ ] Evaluate local AI model options (Ollama, Llama.cpp)
- [ ] Implement provider-level rate limiting
- [ ] Add comprehensive cost tracking
- [ ] Create monitoring dashboard for API usage

---

## 🎯 SUCCESS METRICS

### Immediate Goals
- **API Calls:** Reduce from 6,712 to 0 (disable) or <100/day (reconfigure)
- **Cost:** Eliminate unnecessary API credit consumption
- **Monitoring:** Maintain system observability with reduced overhead

### Long-term Goals
- **Efficiency:** <10 API calls/day for monitoring
- **Cost:** <$1/day for all monitoring services
- **Quality:** Maintain or improve observation quality with fewer calls

---

## 🔗 RELATED DOCUMENTATION

- **Root Cause Analysis:** `API_CREDIT_DRAIN_ANALYSIS.md`
- **EXAI Continuation:** `a864f2ff-462f-42f4-bef7-d40e4bddb314` (19 exchanges remaining)
- **Configuration:** `.env.docker` (lines 248-253)
- **AI Auditor Code:** `utils/monitoring/ai_auditor.py`
- **Daemon Startup:** `scripts/ws/run_ws_daemon.py`

---

## 📝 NOTES

**EXAI Recommendations:**
- ✅ Analysis is completely correct
- ✅ Additional issues identified (event filtering, resource leaks)
- ✅ Parsing failures suggest model might not be appropriate for structured JSON
- ✅ Consider switching to model optimized for JSON output

**Next Steps:**
1. Implement immediate fix (disable or reconfigure)
2. Monitor API usage reduction
3. Implement short-term fixes (filtering, rate limiting)
4. Plan long-term improvements (local AI, cost tracking)

---

**CRITICAL:** Immediate action required to stop API credit drain. Recommend disabling AI Auditor until proper fixes are implemented.

