# Comprehensive Monitoring System Design
**Date**: 2025-10-24  
**Status**: Design Phase  
**Priority**: P0 - Critical for System Visibility

## Executive Summary

Design and implement a **full-stack observability system** that provides complete transparency into EXAI-WS MCP Server behavior, enabling rapid identification of bottlenecks, errors, and performance issues.

### Current Problems

1. **Error Tracking Failure**: Error field exists but never shows errors (even during major incidents)
2. **No Performance Visibility**: Can't identify where "3rd call slowdown" is happening
3. **Missing Request Flow**: No visibility into request path through system layers
4. **Dashboard Disconnected**: Monitoring dashboard exists but WebSocket connection fails (404 error)
5. **Incomplete Metrics**: Metadata fields in Supabase are null (model_used, provider_used, response_time_ms)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     COMPREHENSIVE MONITORING SYSTEM                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │ TIER 1: DATA COLLECTION (Instrumentation Layer)                    │    │
│  ├────────────────────────────────────────────────────────────────────┤    │
│  │                                                                     │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │    │
│  │  │ Request      │  │ Performance  │  │ Error        │            │    │
│  │  │ Interceptors │  │ Timers       │  │ Handlers     │            │    │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘            │    │
│  │         │                  │                  │                     │    │
│  │         └──────────────────┴──────────────────┘                     │    │
│  │                            │                                        │    │
│  │                    ┌───────▼────────┐                              │    │
│  │                    │ Event Collector │                              │    │
│  │                    └───────┬────────┘                              │    │
│  └────────────────────────────┼─────────────────────────────────────┘    │
│                                │                                           │
│  ┌────────────────────────────▼─────────────────────────────────────┐    │
│  │ TIER 2: DATA STORAGE (Multi-Backend Strategy)                     │    │
│  ├────────────────────────────────────────────────────────────────────┤    │
│  │                                                                     │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │    │
│  │  │ Redis        │  │ Supabase     │  │ In-Memory    │            │    │
│  │  │ (Real-time)  │  │ (Historical) │  │ (Hot Cache)  │            │    │
│  │  ├──────────────┤  ├──────────────┤  ├──────────────┤            │    │
│  │  │ • Events     │  │ • Metrics    │  │ • Active     │            │    │
│  │  │ • Metrics    │  │ • Errors     │  │   Sessions   │            │    │
│  │  │ • Traces     │  │ • Traces     │  │ • Current    │            │    │
│  │  │ TTL: 1 hour  │  │ Retention:   │  │   Requests   │            │    │
│  │  │              │  │ 30 days      │  │              │            │    │
│  │  └──────────────┘  └──────────────┘  └──────────────┘            │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ TIER 3: REAL-TIME PROCESSING (Stream Processing)                    │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │                                                                      │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │   │
│  │  │ Aggregator   │  │ Anomaly      │  │ Alert        │             │   │
│  │  │ (1s window)  │  │ Detector     │  │ Manager      │             │   │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘             │   │
│  │         │                  │                  │                      │   │
│  │         └──────────────────┴──────────────────┘                      │   │
│  │                            │                                         │   │
│  │                    ┌───────▼────────┐                               │   │
│  │                    │ WebSocket      │                               │   │
│  │                    │ Broadcaster    │                               │   │
│  │                    └───────┬────────┘                               │   │
│  └────────────────────────────┼────────────────────────────────────────┘   │
│                                │                                            │
│  ┌────────────────────────────▼────────────────────────────────────────┐   │
│  │ TIER 4: VISUALIZATION (Dashboard Layer)                             │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │                                                                      │   │
│  │  ┌──────────────────────────────────────────────────────────────┐  │   │
│  │  │ Real-Time Dashboard (http://localhost:8080)                   │  │   │
│  │  ├──────────────────────────────────────────────────────────────┤  │   │
│  │  │                                                               │  │   │
│  │  │  📊 System Overview  │  🔥 Live Requests  │  ⚠️ Errors       │  │   │
│  │  │  ─────────────────────────────────────────────────────────   │  │   │
│  │  │  • Health Status     │  • Request Flow    │  • Error Log     │  │   │
│  │  │  • Throughput        │  • Trace Timeline  │  • Stack Traces  │  │   │
│  │  │  • Response Times    │  • Layer Breakdown │  • Error Rates   │  │   │
│  │  │                                                               │  │   │
│  │  │  📈 Performance      │  🗄️ Resources      │  📜 History      │  │   │
│  │  │  ─────────────────────────────────────────────────────────   │  │   │
│  │  │  • Latency P50/P95   │  • Redis Memory    │  • Trends        │  │   │
│  │  │  • Bottleneck Map    │  • Supabase Pool   │  • Comparisons   │  │   │
│  │  │  • Provider Perf     │  • WebSocket Conn  │  • Anomalies     │  │   │
│  │  │                                                               │  │   │
│  │  └──────────────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Fix Critical Issues (Immediate - Day 1)

### 1.1 Fix Dashboard WebSocket Connection

**Problem**: Dashboard gets 404 on `/ws` endpoint  
**Root Cause**: Monitoring endpoint not properly initialized or wrong port

**Fix**:
```python
# src/daemon/ws_server.py
async def start_monitoring_server():
    """Start monitoring WebSocket server on port 8080"""
    from src.daemon.monitoring_endpoint import start_monitoring_endpoint
    await start_monitoring_endpoint(
        host=os.getenv("MONITORING_HOST", "0.0.0.0"),
        port=int(os.getenv("MONITORING_PORT", "8080"))
    )
```

**Verification**:
- Dashboard connects successfully
- Real-time events appear
- No 404 errors in console

### 1.2 Fix Error Tracking

**Problem**: Errors never appear in dashboard or database  
**Root Cause**: Errors logged but not captured in monitoring system

**Fix**:
```python
# utils/monitoring/connection_monitor.py
def record_event(self, connection_type, direction, script_name, function_name, 
                 data_size_bytes=0, response_time_ms=None, error=None, metadata=None):
    """Record monitoring event with proper error capture"""
    
    event = {
        "timestamp": log_timestamp(),
        "connection_type": connection_type,
        "direction": direction,
        "script_name": script_name,
        "function_name": function_name,
        "data_size_bytes": data_size_bytes,
        "response_time_ms": response_time_ms,
        "error": error,  # CRITICAL: Actually store the error
        "error_type": type(error).__name__ if error else None,
        "error_traceback": traceback.format_exc() if error else None,
        "metadata": metadata or {}
    }
    
    # Store in Redis
    self._store_in_redis(event)
    
    # Store in Supabase (async)
    if error:  # CRITICAL: Prioritize error storage
        self._store_error_in_supabase(event)
    
    # Broadcast to dashboard
    self._broadcast_event(event)
```

### 1.3 Fix Supabase Metadata Storage

**Problem**: `model_used`, `provider_used`, `response_time_ms` are null  
**Root Cause**: Metadata not being passed to Supabase storage

**Fix**:
```python
# src/storage/supabase_client.py
async def store_message(self, conversation_id, role, content, metadata=None):
    """Store message with complete metadata"""
    
    # CRITICAL: Ensure metadata is populated
    full_metadata = {
        "model_used": metadata.get("model_used") if metadata else None,
        "provider_used": metadata.get("provider_used") if metadata else None,
        "response_time_ms": metadata.get("response_time_ms") if metadata else None,
        "tool_name": metadata.get("tool_name") if metadata else None,
        "thinking_mode": metadata.get("thinking_mode") if metadata else None,
        "token_usage": metadata.get("token_usage") if metadata else None,
        "timestamp": log_timestamp()
    }
    
    # Store with metadata
    await self.supabase.table("messages").insert({
        "conversation_id": conversation_id,
        "role": role,
        "content": content,
        "metadata": full_metadata  # CRITICAL: Store complete metadata
    }).execute()
```

---

## Phase 2: Enhanced Metrics Collection (Day 2-3)

### 2.1 Request Tracing System

**Goal**: Track request flow through all system layers

**Implementation**:
```python
# utils/tracing/request_tracer.py
class RequestTracer:
    """Distributed tracing for request flow"""
    
    def __init__(self):
        self.active_traces = {}  # trace_id -> trace_data
    
    def start_trace(self, request_id, tool_name, parameters):
        """Start new trace"""
        trace = {
            "trace_id": request_id,
            "tool_name": tool_name,
            "parameters": parameters,
            "start_time": time.time(),
            "spans": [],  # List of spans (layers)
            "status": "active"
        }
        self.active_traces[request_id] = trace
        return trace
    
    def add_span(self, trace_id, layer_name, start_time, end_time, metadata=None):
        """Add span (layer timing) to trace"""
        span = {
            "layer": layer_name,
            "start_time": start_time,
            "end_time": end_time,
            "duration_ms": (end_time - start_time) * 1000,
            "metadata": metadata or {}
        }
        
        if trace_id in self.active_traces:
            self.active_traces[trace_id]["spans"].append(span)
    
    def complete_trace(self, trace_id, status="success", error=None):
        """Complete trace and store"""
        if trace_id not in self.active_traces:
            return
        
        trace = self.active_traces[trace_id]
        trace["end_time"] = time.time()
        trace["total_duration_ms"] = (trace["end_time"] - trace["start_time"]) * 1000
        trace["status"] = status
        trace["error"] = str(error) if error else None
        
        # Store in Redis and Supabase
        self._store_trace(trace)
        
        # Remove from active
        del self.active_traces[trace_id]
```

**Layers to Track**:
1. **Shim Layer** (run_ws_shim.py) - Windows host
2. **WebSocket Layer** (ws_server.py) - Docker daemon
3. **Tool Execution Layer** (tool handlers)
4. **Provider Selection Layer** (provider registry)
5. **AI API Layer** (GLM/Kimi SDK calls)
6. **Supabase Layer** (storage operations)

### 2.2 Performance Metrics

**Metrics to Track**:
```python
# utils/monitoring/metrics.py
class PerformanceMetrics:
    """Track performance metrics"""
    
    METRICS = {
        # Latency metrics (milliseconds)
        "latency_p50": [],  # 50th percentile
        "latency_p95": [],  # 95th percentile
        "latency_p99": [],  # 99th percentile
        
        # Throughput metrics
        "requests_per_second": 0,
        "bytes_per_second": 0,
        
        # Error metrics
        "error_rate": 0.0,  # Percentage
        "errors_per_minute": 0,
        
        # Resource metrics
        "redis_memory_mb": 0,
        "redis_key_count": 0,
        "supabase_pool_active": 0,
        "supabase_pool_idle": 0,
        "websocket_connections": 0,
        
        # Provider metrics
        "glm_avg_latency_ms": 0,
        "kimi_avg_latency_ms": 0,
        "glm_error_rate": 0.0,
        "kimi_error_rate": 0.0,
    }
```

---

## Phase 3: Advanced Visualization (Day 4-5)

### 3.1 Request Flow Visualization

**Component**: Live request flow diagram showing current requests

```html
<!-- static/components/request-flow.html -->
<div class="request-flow">
    <div class="flow-layer" id="shim-layer">
        <h3>Shim (Windows)</h3>
        <div class="active-requests"></div>
    </div>
    <div class="flow-arrow">→</div>
    <div class="flow-layer" id="daemon-layer">
        <h3>Daemon (Docker)</h3>
        <div class="active-requests"></div>
    </div>
    <div class="flow-arrow">→</div>
    <div class="flow-layer" id="provider-layer">
        <h3>Provider</h3>
        <div class="active-requests"></div>
    </div>
    <div class="flow-arrow">→</div>
    <div class="flow-layer" id="api-layer">
        <h3>AI API</h3>
        <div class="active-requests"></div>
    </div>
    <div class="flow-arrow">→</div>
    <div class="flow-layer" id="storage-layer">
        <h3>Supabase</h3>
        <div class="active-requests"></div>
    </div>
</div>
```

### 3.2 Bottleneck Heatmap

**Component**: Visual heatmap showing where time is spent

```javascript
// static/js/bottleneck-heatmap.js
class BottleneckHeatmap {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.layers = ['shim', 'daemon', 'tool', 'provider', 'api', 'storage'];
    }
    
    update(traceData) {
        // Calculate time spent in each layer
        const layerTimes = this.calculateLayerTimes(traceData);
        
        // Draw heatmap (red = slow, green = fast)
        this.drawHeatmap(layerTimes);
    }
    
    calculateLayerTimes(traceData) {
        // Aggregate time spent in each layer
        const times = {};
        for (const trace of traceData) {
            for (const span of trace.spans) {
                if (!times[span.layer]) times[span.layer] = [];
                times[span.layer].push(span.duration_ms);
            }
        }
        return times;
    }
}
```

---

## Implementation Priorities

### P0 - Critical (Day 1)
- [ ] Fix dashboard WebSocket connection
- [ ] Fix error tracking (errors must be captured)
- [ ] Fix Supabase metadata storage

### P1 - High (Day 2-3)
- [ ] Implement request tracing system
- [ ] Add performance metrics collection
- [ ] Create bottleneck detection

### P2 - Medium (Day 4-5)
- [ ] Build request flow visualization
- [ ] Add bottleneck heatmap
- [ ] Implement anomaly detection

### P3 - Nice to Have (Week 2)
- [ ] Historical trend analysis
- [ ] Automated alerting
- [ ] Playwright automated testing

---

## Success Criteria

✅ **Errors are visible** - Dashboard shows all errors with stack traces  
✅ **Performance is tracked** - Can identify "3rd call slowdown" root cause  
✅ **Request flow is visible** - Can see request path through all layers  
✅ **Bottlenecks are identified** - Heatmap shows where time is spent  
✅ **Real-time updates** - Dashboard updates without refresh  
✅ **Historical analysis** - Can query past performance data

---

## Next Steps

1. **Immediate**: Fix P0 issues (dashboard connection, error tracking, metadata)
2. **Short-term**: Implement request tracing and performance metrics
3. **Medium-term**: Build advanced visualizations
4. **Long-term**: Add automated testing with Playwright

**Ready to implement Phase 1?**

