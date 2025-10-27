# API Credit Drain Analysis - CRITICAL FINDINGS
**Date:** 2025-10-27  
**Status:** 🚨 CRITICAL ISSUE IDENTIFIED  
**Impact:** HIGH - Excessive API calls consuming credits from both Kimi and GLM

---

## 🔍 EXECUTIVE SUMMARY

**ROOT CAUSE:** AI Auditor service is making **6,712 API calls** to GLM (glm-4.5-flash) for monitoring events.

**IMPACT:**
- **6,712 HTTP POST requests** to `https://api.z.ai/api/paas/v4/chat/completions`
- **6,696 batch analyses** logged in Docker logs
- API calls made **every 5 seconds OR when 10 events accumulate** (whichever comes first)
- Running continuously since container startup

---

## 📊 EVIDENCE

### 1. Docker Log Analysis
```powershell
# Total AI Auditor batch analyses
docker logs exai-mcp-daemon 2>&1 | Select-String -Pattern "AI_AUDITOR.*Analyzing batch" | Measure-Object
# Result: 6,696 matches

# Total HTTP POST requests to GLM API
docker logs exai-mcp-daemon 2>&1 | Select-String -Pattern "HTTP Request.*POST.*chat/completions" | Measure-Object
# Result: 6,712 matches
```

### 2. AI Auditor Configuration
**File:** `.env.docker`
```env
AUDITOR_ENABLED=true
AUDITOR_MODEL=glm-4.5-flash  # FREE model but still consumes API quota
AUDITOR_BATCH_SIZE=10        # Analyze every 10 events
AUDITOR_ANALYSIS_INTERVAL=5  # OR every 5 seconds
AUDITOR_WS_URL=ws://localhost:8080/ws
```

### 3. Recent Log Samples
```
2025-10-27 21:41:30 INFO utils.monitoring.ai_auditor: [AI_AUDITOR] Analyzing batch of 10 events
2025-10-27 21:41:35 INFO httpx: HTTP Request: POST https://api.z.ai/api/paas/v4/chat/completions "HTTP/1.1 200 OK"
2025-10-27 21:41:39 INFO utils.monitoring.ai_auditor: [AI_AUDITOR] Analyzing batch of 4 events
2025-10-27 21:41:44 INFO httpx: HTTP Request: POST https://api.z.ai/api/paas/v4/chat/completions "HTTP/1.1 200 OK"
2025-10-27 21:41:49 INFO utils.monitoring.ai_auditor: [AI_AUDITOR] Analyzing batch of 2 events
2025-10-27 21:41:54 INFO httpx: HTTP Request: POST https://api.z.ai/api/paas/v4/chat/completions "HTTP/1.1 200 OK"
```

**Pattern:** API call every 5-10 seconds continuously

---

## 🔧 ROOT CAUSE ANALYSIS

### AI Auditor Logic (`utils/monitoring/ai_auditor.py`)

```python
def _should_analyze(self) -> bool:
    """Determine if we should analyze now"""
    time_elapsed = time.time() - self.last_analysis_time
    
    return (
        len(self.event_buffer) >= self.batch_size or  # 10 events
        time_elapsed >= self.analysis_interval        # 5 seconds
    ) and not self.circuit_open
```

**Issue:** The AI Auditor analyzes events when **EITHER**:
1. 10 events accumulate in buffer, **OR**
2. 5 seconds have elapsed since last analysis

This means even with **low event volume**, it makes an API call **every 5 seconds**.

### Initialization (`scripts/ws/run_ws_daemon.py`)

```python
auditor = AIAuditor(
    model=auditor_model,           # glm-4.5-flash
    batch_size=auditor_batch_size, # 10
    analysis_interval=auditor_interval,  # 5 seconds
    ws_url=auditor_ws_url
)
```

---

## 💰 COST IMPACT ESTIMATION

### GLM-4.5-Flash Pricing (FREE Tier)
- **Model:** glm-4.5-flash (FREE but has quota limits)
- **API Calls:** 6,712 calls
- **Frequency:** ~12 calls/minute (every 5 seconds)
- **Daily Projection:** ~17,280 calls/day (if running 24/7)

### Kimi API Impact
**Need to verify:** Check if Kimi API is also being used for file operations or other tools.

---

## 🚨 ADDITIONAL CONCERNS

### 1. Parsing Failures
```
2025-10-27 21:41:35 ERROR utils.monitoring.ai_auditor: [AI_AUDITOR] All parsing strategies failed
2025-10-27 21:41:35 ERROR utils.monitoring.ai_auditor: [AI_AUDITOR] Raw Response (first 1000 chars): I notice that the actual events data to analyze is missing from your request...
```

**Issue:** AI Auditor is making API calls but **failing to parse responses**, wasting credits.

### 2. Empty Responses
```
2025-10-27 21:46:34 WARNING utils.monitoring.ai_auditor: [AI_AUDITOR] Empty response received
2025-10-27 21:46:34 WARNING utils.monitoring.ai_auditor: [AI_AUDITOR] Failed to parse response, returning empty list
```

**Issue:** Some API calls return empty responses, indicating wasted credits.

---

## 🎯 RECOMMENDED FIXES

### IMMEDIATE (Priority 1)
1. **Disable AI Auditor temporarily**
   ```env
   AUDITOR_ENABLED=false
   ```

2. **Increase analysis interval**
   ```env
   AUDITOR_ANALYSIS_INTERVAL=60  # Change from 5s to 60s
   AUDITOR_BATCH_SIZE=50         # Change from 10 to 50
   ```

### SHORT-TERM (Priority 2)
3. **Add event filtering** - Only analyze critical events (errors, warnings)
4. **Implement rate limiting** - Max X analyses per hour
5. **Fix parsing failures** - Ensure API calls are productive

### LONG-TERM (Priority 3)
6. **Use local AI model** - Replace API calls with local inference
7. **Implement smart batching** - Only analyze when meaningful events occur
8. **Add cost monitoring** - Track API usage and set alerts

---

## 📋 NEXT STEPS

1. ✅ **COMPLETE:** Identified root cause (AI Auditor)
2. ✅ **COMPLETE:** Quantified impact (6,712 API calls)
3. ⏳ **IN PROGRESS:** Check Supabase tables for additional patterns
4. ⏳ **PENDING:** Review Kimi file upload patterns
5. ⏳ **PENDING:** EXAI consultation for comprehensive fix strategy
6. ⏳ **PENDING:** Implement recommended fixes

---

## 🔗 RELATED FILES

- **Configuration:** `.env.docker` (lines 248-253)
- **AI Auditor:** `utils/monitoring/ai_auditor.py`
- **Daemon Startup:** `scripts/ws/run_ws_daemon.py` (lines 92-112)
- **Monitoring Dashboard:** `static/monitoring_dashboard.html`

---

## 📝 NOTES

- AI Auditor was implemented in **Phase 0.1 (2025-10-24)** for real-time system observation
- Uses **glm-4.5-flash** (FREE model) but still consumes API quota
- Designed to watch monitoring WebSocket and analyze system events
- **Current behavior:** Making API calls even when no meaningful events occur
- **Expected behavior:** Only analyze when critical events happen

---

**CRITICAL:** This issue is consuming API credits continuously. Immediate action required to disable or reconfigure AI Auditor.

