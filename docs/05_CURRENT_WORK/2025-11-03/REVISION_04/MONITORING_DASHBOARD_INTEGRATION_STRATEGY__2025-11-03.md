# Monitoring Dashboard Integration Strategy - Adaptive Timeout Day 1

**Date:** 2025-11-03  
**Status:** 📋 **PLANNING - DO NOT IMPLEMENT WITHOUT READING THIS FIRST**  
**Continuation ID:** 49196783-dd79-4970-95e8-2634c0b09c41 (14 exchanges remaining)  
**K2 Recommendation:** Hybrid Approach (Option C)

---

## ⚠️ CRITICAL WARNING

**The monitoring dashboard is FAR MORE COMPLEX than initially understood.**

This is NOT a simple HTML dashboard. It's a **sophisticated real-time monitoring system** with:
- Dual WebSocket/Supabase Realtime architecture
- Cross-session state synchronization
- Persistent metrics storage
- AI Auditor integration
- Feature flag system
- Cache metrics aggregation
- Edge Functions for data processing
- Materialized views for performance
- RPC functions for schema-qualified access

**DO NOT proceed with Day 1 implementation without understanding this architecture.**

---

## 🏗️ Existing Monitoring Infrastructure

### **1. Dual Architecture (WebSocket + Supabase Realtime)**

**Current State:** System uses BOTH architectures simultaneously

#### **Architecture A: Custom WebSocket System** (Primary - Port 8081)
```
monitoring_endpoint.py (1132 lines!)
    ↓ WebSocket Server (ws://localhost:8081/ws)
    ↓ Broadcasts every 5 seconds
    ↓
Dashboard Clients (monitoring_dashboard.html)
    ↓ JavaScript Modules:
    ├─ websocket-client.js - Connection management
    ├─ dashboard-core.js - State management
    ├─ chart-manager.js - Chart.js integration
    ├─ session-tracker.js - Session metrics
    ├─ auditor-panel.js - AI observations
    └─ testing-panel.js - Test execution
```

#### **Architecture B: Supabase Realtime System** (Partially Implemented)
```
PostgreSQL (monitoring schema)
    ↓ Supabase Realtime (postgres_changes)
    ↓ Realtime Adapter (realtime_adapter.py)
    ↓ Broadcast to subscribed clients
    ↓
Dashboard (supabase-realtime.js)
    ↓ Cross-session state (cross-session-state.js)
    └─ Persistent state sync
```

**Problem:** Both systems exist but integration is incomplete. Some components use WebSocket, others use Supabase Realtime.

---

### **2. Supabase Schema Architecture**

#### **Monitoring Schema** (`monitoring.*`)
```sql
-- Core tables
monitoring.monitoring_events       -- All monitoring events
monitoring.metrics_raw             -- Raw metrics data
monitoring.metrics_1min            -- 1-minute aggregates (materialized view)
monitoring.metrics_1hour           -- 1-hour aggregates (materialized view)

-- Cache metrics (public schema - legacy)
public.cache_metrics               -- Raw cache events (7-day retention)
public.cache_metrics_1min          -- 1-minute aggregates (30-day retention)
public.cache_metrics_1hour         -- 1-hour aggregates (1-year retention)
public.cache_baseline_metrics      -- Baseline for anomaly detection
public.cache_auditor_observations  -- AI Auditor alerts
```

#### **RPC Functions** (Schema-Qualified Access)
```sql
-- Public wrappers (for Supabase Python client)
public.insert_monitoring_event()
public.insert_monitoring_events_batch()
public.get_monitoring_events()

-- Core implementations (monitoring schema)
monitoring.insert_monitoring_event()
monitoring.aggregate_metrics()
monitoring.get_cache_metrics_summary()
```

#### **Realtime Publications**
```sql
ALTER PUBLICATION supabase_realtime ADD TABLE public.cache_metrics_1min;
ALTER PUBLICATION supabase_realtime ADD TABLE public.cache_auditor_observations;
```

---

### **3. Data Flow Patterns**

#### **Pattern A: WebSocket Broadcast** (Current Primary)
```
ConnectionMonitor.record_event()
    ↓ In-memory aggregation
    ↓ Redis persistence (dual-write)
    ↓
periodic_metrics_broadcast() (every 5s)
    ↓ WebSocket broadcast
    ↓
Dashboard clients receive updates
    ↓ Update charts, stats, health indicators
```

#### **Pattern B: Supabase Realtime** (Partially Implemented)
```
MetricsCollector.collect()
    ↓ Batch metrics
    ↓ HTTP POST to Edge Function
    ↓
Edge Function (cache-metrics-aggregator)
    ├─ Store raw metrics
    ├─ Aggregate into time windows
    ├─ Broadcast via Realtime
    └─ Trigger AI Auditor
    ↓
Dashboard subscribes to Realtime
    ↓ Receive postgres_changes events
    ↓ Update UI
```

#### **Pattern C: RPC Functions** (New - Phase 4)
```
UnifiedMetricsCollector
    ↓ Batch metrics
    ↓ Call aggregate_metrics() RPC
    ↓
PostgreSQL native aggregation
    ↓ Insert into metrics_raw
    ↓ Refresh materialized views
    ↓
Dashboard queries via RPC
    ↓ get_cache_metrics_summary()
    ↓ Render visualizations
```

---

### **4. JavaScript Module Architecture**

#### **Core Modules** (static/js/)
```javascript
// Connection Management
websocket-client.js          // Custom WebSocket with reconnection
supabase-client.js           // Supabase client wrapper
supabase-realtime.js         // Realtime subscription manager

// State Management
dashboard-core.js            // Central state + event emitter
cross-session-state.js       // Supabase-backed state sync
session-tracker.js           // Session metrics tracking

// Visualization
chart-manager.js             // Chart.js wrapper
realtime-adapter.js          // Realtime event routing

// Features
auditor-panel.js             // AI Auditor observations
testing-panel.js             // Test execution panel
cache-metrics-panel.js       // Cache metrics (REMOVED - redundant)
feature-flag-client.js       // Feature flag integration
```

#### **Module Dependencies**
```
monitoring_dashboard.html
    ├─ websocket-client.js (connects to monitoring_endpoint.py)
    ├─ dashboard-core.js (state management)
    │   └─ Emits events: 'event:added', 'stats:updated', 'health:updated'
    ├─ chart-manager.js (Chart.js wrapper)
    ├─ session-tracker.js (session metrics)
    ├─ auditor-panel.js (AI observations)
    └─ testing-panel.js (test execution)

// Supabase integration (partially implemented)
supabase-client.js
    └─ supabase-realtime.js
        └─ cross-session-state.js
```

---

### **5. Monitoring Endpoint Routes** (monitoring_endpoint.py)

```python
# WebSocket
GET  /ws                          # WebSocket connection

# Dashboard
GET  /monitoring_dashboard.html   # Serve dashboard
GET  /status                      # Health check

# Metrics (Phase 2.4.3)
GET  /metrics/validation          # Validation metrics
GET  /metrics/adapter             # Adapter metrics
POST /metrics/flush               # Flush metrics to Supabase

# Feature Flags
GET  /flags/status                # Feature flag status
GET  /health/flags                # Health check with flags

# Health
GET  /health                      # Monitoring health endpoint

# AI Auditor (Phase 0.1)
GET  /auditor/observations        # Get AI observations
POST /auditor/acknowledge         # Acknowledge observation
```

---

### **6. Persistence Layers**

#### **Layer 1: In-Memory** (ConnectionMonitor)
- Real-time event tracking
- Fast aggregation
- No persistence across restarts

#### **Layer 2: Redis** (Dual-Write Pattern)
- Persistent event storage
- Cross-session sharing
- Backup for Supabase failures

#### **Layer 3: Supabase** (Primary Persistence)
- Long-term storage
- Historical analysis
- AI Auditor data source
- Cross-session state sync

---

## 🎯 K2's Integration Strategy (Hybrid Approach)

### **Recommendation: Extend Existing Infrastructure**

**DO NOT create separate dashboard or duplicate infrastructure.**

### **Day 1 Implementation Plan**

#### **1. Estimate API** (`src/api/estimate.py`)
```python
# NEW FILE - Mount as sub-router
POST /api/v1/timeout/estimate

# Integration point:
# monitoring_endpoint.py line ~1210
from src.api.estimate import create_estimate_router
app.router.add_routes(create_estimate_router())
```

#### **2. Duration Recording** (Extend ConnectionMonitor)
```python
# MODIFY: utils/monitoring/connection_monitor.py
def record_duration(self, model: str, duration_ms: float, 
                   prompt_tokens: int = None, 
                   completion_tokens: int = None,
                   request_type: str = "text_only", 
                   metadata: Dict = None):
    """Record model duration for adaptive timeout calculation"""
    # Reuse existing record_event() infrastructure
    self.record_event(
        connection_type="adaptive_timeout",
        direction="duration_recorded",
        ...
    )
```

#### **3. Prometheus Metrics** (`src/monitoring/adaptive_timeout_metrics.py`)
```python
# NEW FILE - Integrate with websocket_metrics.py patterns
from prometheus_client import Histogram, Counter, Gauge

class AdaptiveTimeoutMetrics:
    adaptive_timeout_histogram = Histogram(
        'kimi_adaptive_timeout_seconds',
        'Adaptive timeout values',
        ['model', 'source']
    )
    estimate_accuracy = Histogram(
        'kimi_estimate_accuracy_ratio',
        'Actual vs estimated duration',
        ['model']
    )
```

#### **4. Dashboard Panel** (Extend monitoring_dashboard.html)
```html
<!-- ADD AFTER LINE ~200 -->
<div class="card adaptive-timeout-panel">
    <h2>⏱️ Adaptive Timeout Analytics</h2>
    <div id="adaptiveTimeoutStats"></div>
    <canvas id="timeoutAccuracyChart"></canvas>
</div>
```

```javascript
// ADD TO dashboard initialization
function handleAdaptiveTimeoutUpdate(data) {
    // Update stats
    updateAdaptiveTimeoutStats(data);
    // Update charts
    chartManager.updateTimeoutChart(data);
}
```

---

## 📋 Integration Checklist

### **Before Starting Day 1:**

- [ ] **Read this entire document**
- [ ] **Understand dual architecture** (WebSocket + Supabase Realtime)
- [ ] **Review ConnectionMonitor** implementation
- [ ] **Review monitoring_endpoint.py** routes
- [ ] **Review dashboard JavaScript modules**
- [ ] **Consult K2** with specific integration questions

### **Day 1 Implementation:**

- [ ] Create `src/api/estimate.py`
- [ ] Extend `ConnectionMonitor.record_duration()`
- [ ] Create `src/monitoring/adaptive_timeout_metrics.py`
- [ ] Add dashboard panel to `monitoring_dashboard.html`
- [ ] Add JavaScript handler for adaptive timeout events
- [ ] Integrate with existing WebSocket broadcast
- [ ] Test with existing monitoring infrastructure

---

## 🚨 Known Complexity Points

### **1. Dual Architecture Confusion**
- Some components use WebSocket
- Some components use Supabase Realtime
- Integration is incomplete
- **Solution:** Use WebSocket for Day 1, migrate to Realtime in Day 3-4

### **2. Schema Qualification Issues**
- Supabase Python client doesn't support `schema.table` syntax
- Must use RPC functions for monitoring schema
- **Solution:** Use existing RPC patterns from `20251101_add_monitoring_functions.sql`

### **3. Metrics Persistence**
- Three layers: In-memory, Redis, Supabase
- Dual-write pattern can fail
- **Solution:** Use existing `ConnectionMonitor` infrastructure

### **4. Dashboard State Management**
- Multiple state systems: dashboard-core.js, cross-session-state.js
- Event emitter pattern for updates
- **Solution:** Follow existing patterns in dashboard-core.js

---

## 📚 Critical Files to Review

**Backend:**
- `src/daemon/monitoring_endpoint.py` (1132 lines) - WebSocket server
- `utils/monitoring/connection_monitor.py` - Event tracking
- `src/monitoring/adapters/realtime_adapter.py` - Supabase Realtime

**Frontend:**
- `static/monitoring_dashboard.html` (918 lines) - Main dashboard
- `static/js/dashboard-core.js` - State management
- `static/js/websocket-client.js` - WebSocket connection
- `static/js/supabase-realtime.js` - Realtime integration

**Database:**
- `supabase/migrations/20251031_cache_metrics_monitoring.sql` - Cache metrics schema
- `supabase/migrations/20251101_unified_metrics_rpc_functions.sql` - RPC functions
- `supabase/migrations/20251101_add_monitoring_functions.sql` - Monitoring RPC

**Documentation:**
- `docs/05_CURRENT_WORK/2025-10-31/WEEK2_3_MONITORING_PHASE_IMPLEMENTATION__2025-10-31.md`
- `docs/05_CURRENT_WORK/2025-10-31_part2/COMPREHENSIVE_QA_AUDIT__EXAI_FINDINGS__2025-11-01.md`

---

## 🎯 K2's Specific Integration Decisions (2025-11-03)

### **Question 1: WebSocket vs Supabase Realtime Priority**
**✅ DECISION: Option A - Use existing WebSocket broadcast**

**Why:** WebSocket system is proven, working, handles real-time updates every 5 seconds. Supabase Realtime is incomplete.

**Implementation:** Extend `broadcast_monitoring_event()` in `monitoring_endpoint.py`

**Defer:** Complete Supabase Realtime migration to Day 3-4

---

### **Question 2: ConnectionMonitor Extension Strategy**
**✅ DECISION: Option B - Extend existing "kimi" and "glm" types with duration metadata**

**Why:** Adding 6th connection type would confuse dashboard panels expecting exactly 5 service cards.

**Implementation:**
```python
# In ConnectionMonitor.record_event(), detect adaptive timeout context
if metadata and metadata.get("adaptive_timeout"):
    event.metadata["adaptive_timeout_ms"] = duration_ms
    event.metadata["estimated_tokens"] = estimated_tokens
    event.metadata["actual_duration_ms"] = actual_duration_ms
```

**Defer:** Separate connection type only if panels become too cluttered

---

### **Question 3: Dashboard Panel Integration**
**✅ DECISION: Option D - Add new chart type to existing chart grid**

**Why:** Chart grid (4 charts) is designed to be extensible. Adding 5th chart fits existing layout.

**Implementation:**
```html
<!-- Add to chart-grid div -->
<div class="chart-card">
    <h3>⏱️ Timeout Accuracy</h3>
    <div class="chart-container">
        <canvas id="timeoutAccuracyChart"></canvas>
    </div>
</div>
```

**Defer:** Dedicated section only if chart approach proves insufficient

---

### **Question 4: Metrics Persistence Layer**
**✅ DECISION: Option B - In-memory + Redis (persistent, dual-write complexity)**

**Why:** Follows existing proven pattern in ConnectionMonitor with circuit breaker patterns.

**Implementation:** Extend existing Redis persistence to handle duration events

**Defer:** Supabase persistence until unified metrics collector in Phase 4

---

### **Question 5: Estimate API Integration**
**✅ DECISION: Option A - Mount in `monitoring_endpoint.py` (port 8081)**

**Why:** Monitoring server already has comprehensive API structure with `/api/*` endpoints.

**Implementation:**
```python
# Add to monitoring_endpoint.py around line 1210
app.router.add_post('/api/v1/timeout/estimate', handle_timeout_estimate)
```

**Defer:** Separate API server only if need to scale estimate requests independently

---

### **Question 6: Moonshot Estimate API Integration**
**✅ DECISION: Option C - Call estimate API only when confidence < 0.5**

**Why:** Balances accuracy vs performance by using expensive API only when adaptive algorithm lacks confidence.

**Implementation:**
```python
if confidence < 0.5:
    estimate = await call_moonshot_estimate(model, messages)
    timeout_duration = estimate_based_on_tokens(estimate)
else:
    timeout_duration = predict_from_historical_data(model, context)
```

**Defer:** Make configurable if different models need different confidence thresholds

---

### **Question 7: Implementation Priority**
**✅ DECISION: Option B - Implement Day 1 with minimal dashboard integration (WebSocket only)**

**Why:** Full integration would risk breaking existing monitoring system. WebSocket-only gives working adaptive timeouts with minimal risk.

**Day 1 Implementation Order:**
1. Create `/api/v1/timeout/estimate` endpoint in monitoring_endpoint.py
2. Extend ConnectionMonitor to record duration events via existing kimi/glm types
3. Add basic timeout accuracy chart to existing chart grid
4. Test with existing WebSocket infrastructure

**Defer to Day 2-3:**
- Complete dashboard panel with detailed analytics
- Supabase Realtime integration
- Advanced chart interactions
- Historical trend analysis

---

## 🚀 Day 1 Implementation Plan (K2 Approved)

### **Step 1: Estimate API Endpoint** (30 min)
```python
# File: src/daemon/monitoring_endpoint.py (add around line 1210)

async def handle_timeout_estimate(request: web.Request) -> web.Response:
    """
    Estimate timeout for a model request.

    POST /api/v1/timeout/estimate
    Body: {
        "model": "kimi-k2",
        "messages": [...],
        "request_type": "text"
    }
    Response: {
        "timeout": 180,
        "confidence": 0.85,
        "source": "adaptive"
    }
    """
    # Implementation here
    pass

# Mount route
app.router.add_post('/api/v1/timeout/estimate', handle_timeout_estimate)
```

### **Step 2: Duration Recording** (25 min)
```python
# File: utils/monitoring/connection_monitor.py

def record_duration(self, model: str, duration_ms: float,
                   prompt_tokens: int = None,
                   completion_tokens: int = None,
                   request_type: str = "text_only",
                   metadata: Dict = None):
    """Record model duration for adaptive timeout calculation"""
    # Detect provider
    provider = "kimi" if "kimi" in model.lower() or "k2" in model.lower() else "glm"

    # Reuse existing record_event with adaptive timeout metadata
    self.record_event(
        connection_type=provider,
        direction="duration_recorded",
        script_name="adaptive_timeout.py",
        function_name="record_duration",
        data_size_bytes=prompt_tokens + completion_tokens if prompt_tokens else 0,
        response_time_ms=duration_ms,
        metadata={
            "adaptive_timeout": True,
            "model": model,
            "request_type": request_type,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "adaptive_timeout_ms": duration_ms,
            **(metadata or {})
        }
    )
```

### **Step 3: Dashboard Chart** (20 min)
```html
<!-- File: static/monitoring_dashboard.html -->
<!-- Add to chart-grid div (after line ~382) -->

<div class="chart-card">
    <h3>⏱️ Adaptive Timeout Accuracy</h3>
    <div class="chart-container">
        <canvas id="timeoutAccuracyChart"></canvas>
    </div>
</div>
```

```javascript
// Add to chart initialization
function initializeCharts() {
    // ... existing charts ...

    // Timeout accuracy chart
    const timeoutAccuracyCtx = document.getElementById('timeoutAccuracyChart').getContext('2d');
    charts.timeoutAccuracy = new Chart(timeoutAccuracyCtx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Predicted vs Actual',
                data: [],
                backgroundColor: 'rgba(102, 126, 234, 0.5)'
            }]
        },
        options: {
            scales: {
                x: { title: { display: true, text: 'Predicted Timeout (s)' } },
                y: { title: { display: true, text: 'Actual Duration (s)' } }
            }
        }
    });
}
```

### **Step 4: Integration Testing** (15 min)
- Test estimate API endpoint
- Test duration recording
- Test dashboard chart updates
- Verify WebSocket broadcast

---

## ⚠️ Critical Implementation Notes (K2)

1. **Test in isolation first:** Create simple test script before full integration
2. **Use existing patterns:** Follow established patterns exactly
3. **Monitor the monitors:** Add logging to track adaptive timeout integration
4. **Feature flag consideration:** Add feature flag for adaptive timeouts

---

**✅ K2 APPROVED - READY FOR DAY 1 IMPLEMENTATION**

