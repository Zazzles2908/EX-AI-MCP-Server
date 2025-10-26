# End-to-End Tests - Full System Validation

**Created:** 2025-10-26
**Purpose:** Test complete system (WebSocket → MCP → Tools → Providers)
**Expected Performance:** 10K-50K messages/second
**Status:** ⏳ PENDING - Awaiting integration test completion

---

## 🎯 **WHAT E2E TESTS VALIDATE**

**End-to-end tests validate the COMPLETE system under realistic load:**

```
Unit Tests (3.1M msg/s)
    ↓
Integration Tests (50K-200K msg/s)
    ↓
End-to-End Tests (10K-50K msg/s) ← YOU ARE HERE
```

**What We Test:**
- ✅ Full WebSocket → MCP server → Tool execution → Provider SDK → Response flow
- ✅ Concurrent client load (10, 100, 1000+ clients)
- ✅ Sustained load over time (1 hour continuous operation)
- ✅ Resource usage under load (CPU, memory, file descriptors)
- ✅ System degradation under overload
- ✅ Recovery from failures
- ✅ Production-realistic scenarios

**This is the FINAL validation before production deployment.**

---

## 📊 **TEST INFRASTRUCTURE**

**Leveraging:**
- `tool_validation_suite/` - Full stack validation framework
- `scripts/phase2_comparison/websocket_test_client.py` - WebSocket client
- `static/monitoring_dashboard.html` - Real-time monitoring
- `src/daemon/monitoring_endpoint.py` - Metrics API

**Test Environment:**
- WebSocket server: `ws://localhost:8079`
- MCP server: Full stack with all tools enabled
- Monitoring: Real-time dashboard for visual validation

---

## 🧪 **TEST SCENARIOS**

### **1. Load Performance Testing**
**File:** `test_load_performance.py`

**Tests:**
- Single client baseline (latency, throughput)
- 10 concurrent clients
- 100 concurrent clients
- 1000 concurrent clients
- Performance degradation analysis

**Success Criteria:**
- ✅ Single client: <50ms latency, >1K msg/s
- ✅ 10 clients: <100ms latency, >10K msg/s
- ✅ 100 clients: <200ms latency, >20K msg/s
- ✅ 1000 clients: <500ms latency, >10K msg/s
- ✅ Linear or sub-linear degradation

### **2. Concurrent Connections**
**File:** `test_concurrent_connections.py`

**Tests:**
- Rapid connection establishment (100 clients in <1 second)
- Sustained concurrent connections (1000 clients for 10 minutes)
- Connection churn (clients connecting/disconnecting continuously)
- Resource usage monitoring (memory, CPU, file descriptors)

**Success Criteria:**
- ✅ System handles 1000+ concurrent connections
- ✅ No memory leaks over 1 hour
- ✅ CPU usage <80% under load
- ✅ Graceful degradation (no crashes)

### **3. End-to-End Latency**
**File:** `test_end_to_end_latency.py`

**Tests:**
- Request → Response latency distribution
- P50, P95, P99 latency percentiles
- Latency under various load levels
- Latency with different tool types

**Success Criteria:**
- ✅ P50 latency: <50ms
- ✅ P95 latency: <100ms
- ✅ P99 latency: <200ms
- ✅ No outliers >1 second

---

## 🚀 **RUNNING E2E TESTS**

### **Prerequisites**
1. WebSocket server running at `ws://localhost:8079`
2. MCP server fully operational with all tools enabled
3. Monitoring dashboard accessible
4. Sufficient system resources (8GB RAM, 4 CPU cores recommended)

### **Run All E2E Tests**
```bash
cd tests/e2e
python -m pytest -v --tb=short
```

### **Run Load Test**
```bash
python test_load_performance.py
```

### **Monitor During Testing**
- Open `http://localhost:8079/monitoring` in browser
- Watch real-time metrics during test execution
- Verify circuit breaker behavior
- Monitor resource usage

---

## 📈 **EXPECTED PERFORMANCE**

**Performance Targets:**
- **Message throughput:** 10K-50K messages/second (sustained)
- **Connection latency:** <50ms for establishment
- **Message latency:** <100ms for P95
- **Concurrent connections:** 1000+ clients
- **Uptime:** 1 hour continuous operation without crashes

**Performance Factors:**
- Full MCP server processing (request routing, tool execution)
- Provider SDK overhead (API calls to GLM/Kimi)
- Database operations (Supabase logging)
- Monitoring overhead (metrics collection, dashboard updates)
- System resource limits (memory, CPU, file descriptors)

**Overhead vs Integration Tests:** 5-20x slower (due to full system processing)

---

## 🔄 **DEVELOPMENT STATUS**

**Phase 3: End-to-End Load Tests (6-8 hours)**

**Tasks:**
- [ ] Create `test_load_performance.py`
- [ ] Create `test_concurrent_connections.py`
- [ ] Create `test_end_to_end_latency.py`
- [ ] Establish realistic performance baselines
- [ ] Document system limits and breaking points
- [ ] Create troubleshooting guide

**Timeline:** PENDING - Starts after integration tests complete

---

## ⚠️ **IMPORTANT NOTES**

**Resource Requirements:**
- E2E tests are resource-intensive
- May impact other running services
- Recommend running on dedicated test environment
- Monitor system resources during execution

**Test Duration:**
- Load tests: 10-30 minutes each
- Sustained load tests: 1 hour
- Full suite: 2-3 hours

**Cleanup:**
- Tests implement proper cleanup
- May need manual cleanup if tests fail
- Check for orphaned connections: `netstat -an | findstr 8079`

---

**Last Updated:** 2025-10-26 16:55 AEDT
**Status:** ⏳ PENDING - Awaiting integration test completion

