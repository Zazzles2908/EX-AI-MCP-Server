# Monitoring and Metrics Guide
**Last Updated:** 2025-10-11 (Phase 2 Cleanup, Task 2.E)

---

## 📊 Overview

EX-AI-MCP-Server provides comprehensive performance monitoring through:
- **Performance Metrics** - Real-time tool, cache, and system metrics
- **Prometheus Integration** - Enterprise monitoring support
- **JSON Metrics Endpoint** - Simple HTTP access to metrics
- **Logging** - Detailed execution logs

---

## 🎯 Quick Start

### 1. Enable Metrics Collection

Add to `.env`:
```bash
PERFORMANCE_METRICS_ENABLED=true
METRICS_JSON_ENDPOINT_ENABLED=true
METRICS_JSON_PORT=9109
```

### 2. Start Metrics Server

```bash
python scripts/metrics_server.py
```

### 3. Access Metrics

**JSON Endpoint:**
```bash
curl http://localhost:9109/metrics
```

**Health Check:**
```bash
curl http://localhost:9109/health
```

---

## 📈 Metrics Available

### Tool Metrics

**Per-Tool Tracking:**
- Total calls, successful calls, failed calls
- Success rate percentage
- Average latency, p50, p95, p99 latency
- Min/max latency
- Error types and frequencies

**Example:**
```json
{
  "tool_metrics": {
    "chat": {
      "tool_name": "chat",
      "total_calls": 150,
      "successful_calls": 145,
      "failed_calls": 5,
      "success_rate": 96.67,
      "avg_latency_ms": 2340.50,
      "p50_latency_ms": 2100.00,
      "p95_latency_ms": 4500.00,
      "p99_latency_ms": 6200.00,
      "min_latency_ms": 850.00,
      "max_latency_ms": 8500.00,
      "error_types": {
        "TimeoutError": 3,
        "ValueError": 2
      }
    }
  }
}
```

---

### Cache Metrics

**Per-Cache Tracking:**
- Hits, misses, total requests
- Hit rate percentage
- Evictions, size rejections

**Example:**
```json
{
  "cache_metrics": {
    "semantic_cache": {
      "cache_name": "semantic_cache",
      "hits": 450,
      "misses": 550,
      "total_requests": 1000,
      "hit_rate": 45.00,
      "evictions": 12,
      "size_rejections": 3
    },
    "file_cache": {
      "cache_name": "file_cache",
      "hits": 85,
      "misses": 15,
      "total_requests": 100,
      "hit_rate": 85.00,
      "evictions": 0,
      "size_rejections": 0
    }
  }
}
```

---

### System Metrics

**System-Wide Tracking:**
- Active sessions
- Concurrent requests
- Total requests
- Uptime (seconds and hours)

**Example:**
```json
{
  "system_metrics": {
    "active_sessions": 3,
    "concurrent_requests": 1,
    "total_requests": 1250,
    "start_time": 1728640000.0,
    "uptime_seconds": 8000.00,
    "uptime_hours": 2.22
  }
}
```

---

## 🔍 Using Metrics for Debugging

### Identify Slow Tools

**Problem:** Which tools are slowest?

**Solution:** Check p95/p99 latency:
```bash
curl http://localhost:9109/metrics | jq '.tool_metrics | to_entries | sort_by(.value.p95_latency_ms) | reverse | .[0:5]'
```

**Interpretation:**
- p50 (median) - Typical performance
- p95 - 95% of requests faster than this
- p99 - 99% of requests faster than this

**Action:**
- If p95 > 5000ms: Tool is slow, investigate
- If p99 >> p95: Occasional spikes, check for timeouts

---

### Identify Failing Tools

**Problem:** Which tools are failing most?

**Solution:** Check success rates:
```bash
curl http://localhost:9109/metrics | jq '.tool_metrics | to_entries | sort_by(.value.success_rate) | .[0:5]'
```

**Interpretation:**
- Success rate < 90%: Investigate error types
- Check error_types for common failures

**Action:**
- TimeoutError: Increase timeout or optimize tool
- ValueError: Check input validation
- Other errors: Check logs for details

---

### Optimize Cache Performance

**Problem:** Is caching effective?

**Solution:** Check cache hit rates:
```bash
curl http://localhost:9109/metrics | jq '.cache_metrics'
```

**Interpretation:**
- Hit rate > 50%: Caching is effective
- Hit rate < 30%: Consider increasing cache size or TTL
- High evictions: Cache too small, increase max_size
- High size_rejections: Responses too large, increase max_response_size

**Action:**
- Low hit rate: Increase SEMANTIC_CACHE_TTL_SECS
- High evictions: Increase SEMANTIC_CACHE_MAX_SIZE
- Size rejections: Increase SEMANTIC_CACHE_MAX_RESPONSE_SIZE

---

### Monitor System Health

**Problem:** Is the system healthy?

**Solution:** Check system metrics:
```bash
curl http://localhost:9109/metrics | jq '.system_metrics'
```

**Interpretation:**
- High concurrent_requests: System under load
- Growing active_sessions: Sessions not being cleaned up
- Uptime: How long server has been running

**Action:**
- High load: Scale horizontally or optimize tools
- Session leaks: Check session cleanup logic
- Long uptime: Consider periodic restarts

---

## 📊 Prometheus Integration

### Enable Prometheus

Add to `.env`:
```bash
PROMETHEUS_ENABLED=true
PROMETHEUS_PORT=9108
```

### Access Prometheus Metrics

```bash
curl http://localhost:9108/metrics
```

### Grafana Dashboard

**Coming in Phase 3:**
- Pre-built Grafana dashboard
- Real-time visualization
- Alerting rules
- Historical trend analysis

---

## 🔧 Configuration

### Environment Variables

```bash
# Performance Metrics
PERFORMANCE_METRICS_ENABLED=true          # Enable metrics collection
METRICS_WINDOW_SIZE=1000                  # Sliding window for percentiles
METRICS_JSON_ENDPOINT_ENABLED=true        # Enable JSON endpoint
METRICS_JSON_PORT=9109                    # JSON endpoint port

# Prometheus (Optional)
PROMETHEUS_ENABLED=false                  # Enable Prometheus metrics
PROMETHEUS_PORT=9108                      # Prometheus endpoint port
```

### Tuning Recommendations

**For Development:**
```bash
PERFORMANCE_METRICS_ENABLED=true
METRICS_WINDOW_SIZE=100                   # Smaller window for faster percentiles
METRICS_JSON_ENDPOINT_ENABLED=true
```

**For Production:**
```bash
PERFORMANCE_METRICS_ENABLED=true
METRICS_WINDOW_SIZE=1000                  # Larger window for accurate percentiles
METRICS_JSON_ENDPOINT_ENABLED=true
PROMETHEUS_ENABLED=true                   # Enable for enterprise monitoring
```

**For Performance Testing:**
```bash
PERFORMANCE_METRICS_ENABLED=false         # Disable to measure raw performance
```

---

## 📝 Logging

### Log Locations

- **WebSocket Daemon:** `logs/ws_daemon.log`
- **WebSocket Shim:** `logs/ws_shim.log`
- **Activity Log:** `logs/mcp_activity.log`

### Log Levels

```bash
# In .env
LOG_LEVEL=INFO                            # DEBUG, INFO, WARNING, ERROR
```

### Useful Log Patterns

**Tool Execution:**
```
=== TOOL CALL COMPLETE ===
Tool: chat
Duration: 2.34s
Provider: kimi
Success: True
=== END ===
```

**Cache Hits:**
```
Cache HIT for model=glm-4.5-flash (key=abc12345...)
```

**Cache Misses:**
```
Cache MISS for model=glm-4.5-flash (key=def67890...)
```

---

## 🎯 Best Practices

### 1. Monitor Regularly

- Check metrics daily during development
- Set up alerts for production
- Review trends weekly

### 2. Baseline Performance

- Record baseline metrics after deployment
- Compare current metrics to baseline
- Investigate significant deviations

### 3. Optimize Based on Data

- Don't guess - use metrics to identify bottlenecks
- Focus on p95/p99 latency, not just averages
- Optimize high-frequency tools first

### 4. Cache Tuning

- Start with conservative TTL (1 hour)
- Increase if hit rate is low
- Monitor evictions and size rejections

### 5. Error Tracking

- Monitor error types and frequencies
- Investigate new error types immediately
- Track error rate trends over time

---

## 🚀 Advanced Usage

### Custom Metrics Dashboard

Create a simple dashboard using the JSON endpoint:

```python
import requests
import time

while True:
    metrics = requests.get("http://localhost:9109/metrics").json()
    
    print(f"\n=== EX-AI-MCP-Server Metrics ===")
    print(f"Uptime: {metrics['system_metrics']['uptime_hours']:.2f} hours")
    print(f"Total Requests: {metrics['system_metrics']['total_requests']}")
    print(f"Active Sessions: {metrics['system_metrics']['active_sessions']}")
    
    # Top 5 slowest tools
    tools = sorted(
        metrics['tool_metrics'].items(),
        key=lambda x: x[1]['p95_latency_ms'],
        reverse=True
    )[:5]
    
    print("\nTop 5 Slowest Tools (p95):")
    for name, data in tools:
        print(f"  {name}: {data['p95_latency_ms']:.0f}ms")
    
    time.sleep(10)
```

---

**Status:** ✅ MONITORING GUIDE COMPLETE  
**Next:** Continue with documentation improvements


