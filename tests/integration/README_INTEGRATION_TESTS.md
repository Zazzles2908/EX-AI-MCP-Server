# Integration Tests - Real WebSocket Protocol Testing

**Created:** 2025-10-26
**Purpose:** Test WebSocket protocol + component integration
**Expected Performance:** 50K-200K messages/second
**Status:** 🔄 IN PROGRESS

---

## 🎯 **WHAT INTEGRATION TESTS VALIDATE**

**Integration tests bridge the gap between unit tests and end-to-end tests:**

```
Unit Tests (3.1M msg/s)
    ↓
Integration Tests (50K-200K msg/s) ← YOU ARE HERE
    ↓
End-to-End Tests (10K-50K msg/s)
```

**What We Test:**
- ✅ Real WebSocket connections (not direct method calls)
- ✅ WebSocket protocol overhead (handshake, framing, ping/pong)
- ✅ Message serialization/deserialization (JSON encoding/decoding)
- ✅ Component integration with real network events
- ✅ Metrics collection accuracy with real WebSocket traffic
- ✅ Circuit breaker behavior with real connection failures

**What We DON'T Test:**
- ❌ Full MCP server stack (use e2e tests for this)
- ❌ Tool execution and provider SDK calls
- ❌ External API integration
- ❌ Production-scale concurrent load (use e2e tests for this)

---

## 📊 **TEST INFRASTRUCTURE**

**Reusing Existing Infrastructure:**
- `scripts/phase2_comparison/websocket_test_client.py` (300 lines)
- WebSocket server at `ws://localhost:8079`
- Custom MCP protocol (not standard JSON-RPC)

**Test Pattern:**
```python
# Integration Test Pattern
async with websockets.connect("ws://localhost:8079") as websocket:
    # Send hello message for authentication
    hello_msg = {"op": "hello", "session_id": session_id, "token": token}
    await websocket.send(json.dumps(hello_msg))
    
    # Send tool call request
    request = {"op": "call_tool", "request_id": "...", "name": "...", "arguments": {...}}
    await websocket.send(json.dumps(request))
    
    # Receive response
    response = await websocket.recv()
    result = json.loads(response)
```

---

## 🧪 **TEST SCENARIOS**

### **1. Real WebSocket Connections**
**File:** `test_websocket_real_connections.py`

**Tests:**
- Connection establishment with authentication
- Message sending through WebSocket protocol
- Message receiving and parsing
- Connection teardown and cleanup
- Reconnection after disconnect

**Success Criteria:**
- ✅ All connections establish successfully
- ✅ Messages sent/received without corruption
- ✅ Proper cleanup on disconnect
- ✅ Performance within 50K-200K msg/s range

### **2. Metrics Integration**
**File:** `test_metrics_integration.py`

**Tests:**
- Metrics collection with real WebSocket events
- Connection tracking accuracy
- Message tracking accuracy
- Latency measurement accuracy
- Deduplication tracking

**Success Criteria:**
- ✅ Metrics accuracy within ±5% of expected
- ✅ No missing events
- ✅ Proper timestamp recording
- ✅ Correct client isolation

### **3. Circuit Breaker Integration**
**File:** `test_circuit_breaker_integration.py`

**Tests:**
- Circuit breaker triggering with real connection failures
- State transitions (CLOSED → OPEN → HALF_OPEN → CLOSED)
- Failure threshold behavior
- Success threshold recovery
- Timeout-based transitions

**Success Criteria:**
- ✅ Circuit opens after failure threshold
- ✅ Half-open state after timeout
- ✅ Closes after success threshold
- ✅ Proper request blocking in OPEN state

---

## 🚀 **RUNNING INTEGRATION TESTS**

### **Prerequisites**
1. WebSocket server running at `ws://localhost:8079`
2. Valid authentication token in `.env` file
3. Python dependencies installed (`websockets`, `pytest`)

### **Run All Integration Tests**
```bash
cd tests/integration
python -m pytest -v
```

### **Run Specific Test**
```bash
python test_websocket_real_connections.py
```

---

## 📈 **EXPECTED PERFORMANCE**

**Performance Targets:**
- **Message throughput:** 50K-200K messages/second
- **Connection latency:** <10ms for establishment
- **Message latency:** <5ms for send/receive
- **Overhead vs Unit Tests:** 15-60x slower (due to WebSocket protocol)

**Performance Factors:**
- WebSocket handshake overhead
- JSON serialization/deserialization
- Network stack overhead (even on localhost)
- Frame encoding/decoding
- Ping/pong keepalive

---

## 🔄 **DEVELOPMENT STATUS**

**Phase 2: Real Integration Tests (6-8 hours)**

**Tasks:**
- [ ] Create `test_websocket_real_connections.py`
- [ ] Create `test_metrics_integration.py`
- [ ] Create `test_circuit_breaker_integration.py`
- [ ] Establish baseline performance metrics
- [ ] Document findings and performance characteristics

**Timeline:** IN PROGRESS

---

**Last Updated:** 2025-10-26 16:55 AEDT
**Status:** 🔄 IN PROGRESS - Infrastructure ready, tests pending

