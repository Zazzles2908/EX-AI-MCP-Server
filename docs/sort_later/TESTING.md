# EX-AI MCP Server - Testing Strategy
**Last Updated:** 2025-10-21  
**Test Pass Rate:** 100% (9/9 tests passing)  
**Approach:** Hybrid (HTTP from host, WebSocket from container)

---

## 📊 Testing Overview

**Total Tests:** 9  
**Last Run:** 2025-10-21  
**Pass Rate:** 100%  
**Test Duration:** ~10 seconds

**Test Categories:**
- Monitoring UI functionality (4 tests)
- Error handling migration (2 tests)
- Input validation (2 tests)
- Size limits (1 test)

---

## 🎯 Testing Approach

### Hybrid Testing Strategy

Due to Docker/Windows/WSL2 WebSocket-specific networking issues, we use a **hybrid approach**:

✅ **HTTP Tests (from host):**
- Monitoring UI accessibility
- Health check endpoints
- Semaphore status endpoints
- All HTTP endpoints work perfectly from host

✅ **WebSocket Tests (from inside container):**
- MCP protocol handshake
- Tool call execution
- Error handling
- Input validation
- Size limit enforcement

### Why Hybrid?

**What Works:**
- HTTP endpoints accessible from host (localhost:8080, 8082)
- WebSocket connections work from inside container (localhost:8079)
- TCP port 8079 is accessible (Test-NetConnection confirms)

**What Doesn't Work:**
- WebSocket connections from host to container timeout during handshake
- Not a port mapping issue (TCP works)
- Not a server issue (works from inside container)
- Docker/Windows/WSL2 WebSocket-specific networking limitation

**EXAI Analysis:**
- Model: GLM-4.6 (High Thinking Mode)
- Verdict: Docker/Windows/WSL2 WebSocket-specific networking issue
- Recommendation: Use hybrid approach, document limitation

---

## 🧪 Test Suite Details

### Test 1: Monitoring UI Functionality (4 tests)

**Test 1.1: Health Endpoint Returns Healthy Status**
- **Type:** HTTP GET
- **Endpoint:** `http://localhost:8082/health`
- **Expected:** `{"status": "healthy"}`
- **Status:** ✅ PASS

**Test 1.2: Semaphore Endpoint Returns Expected Data**
- **Type:** HTTP GET
- **Endpoint:** `http://localhost:8082/health/semaphores`
- **Expected:** JSON with global/provider semaphore data
- **Status:** ✅ PASS

**Test 1.3: Global Semaphore Counts Match Expected**
- **Type:** HTTP GET + Validation
- **Endpoint:** `http://localhost:8082/health/semaphores`
- **Expected:** `available + in_use = total`
- **Status:** ✅ PASS

**Test 1.4: Monitoring UI is Accessible**
- **Type:** HTTP GET
- **Endpoint:** `http://localhost:8080/semaphore_monitor.html`
- **Expected:** HTML page with monitoring UI
- **Status:** ✅ PASS

---

### Test 2: Error Handling Migration (2 tests)

**Test 2.1: Tool Not Found Error Uses Standardized Format**
- **Type:** WebSocket (from container)
- **Tool:** `nonexistent_tool_EXAI-WS`
- **Expected:** `{"error": {"code": "TOOL_NOT_FOUND", "message": "..."}}`
- **Status:** ✅ PASS

**Test 2.2: Invalid Request Error Uses Standardized Format**
- **Type:** WebSocket (from container)
- **Request:** Missing required 'name' field
- **Expected:** `{"error": {"code": "INVALID_REQUEST", "message": "..."}}`
- **Status:** ✅ PASS

---

### Test 3: Input Validation (2 tests)

**Test 3.1: Invalid Temperature Triggers Validation Error**
- **Type:** WebSocket (from container)
- **Tool:** `chat_EXAI-WS`
- **Input:** `temperature=1.5` (exceeds max 1.0)
- **Expected:** `{"error": {"code": "VALIDATION_ERROR", "message": "..."}}`
- **Status:** ✅ PASS

**Test 3.2: Empty Prompt Triggers Validation Error**
- **Type:** WebSocket (from container)
- **Tool:** `chat_EXAI-WS`
- **Input:** `prompt=""` (empty string)
- **Expected:** `{"error": {"code": "VALIDATION_ERROR", "message": "..."}}`
- **Status:** ✅ PASS

---

### Test 4: Size Limits (1 test)

**Test 4.1: Oversized Request Triggers Size Limit Error**
- **Type:** WebSocket (from container)
- **Tool:** `chat_EXAI-WS`
- **Input:** 11MB prompt (exceeds 10MB limit)
- **Expected:** `{"error": {"code": "OVER_CAPACITY", "message": "..."}}`
- **Status:** ✅ PASS

---

## 🛠️ Testing Tools and Infrastructure

### Test Framework
- **Language:** Python 3.11
- **Libraries:** 
  - `websockets` - WebSocket client
  - `requests` - HTTP client
  - `json` - JSON parsing
  - `asyncio` - Async operations

### Test Environment
- **Host OS:** Windows
- **Container:** Docker (exai-mcp-daemon)
- **WebSocket Server:** ws://localhost:8079
- **HTTP Servers:** 
  - Monitoring: http://localhost:8080
  - Health: http://localhost:8082

### Test Execution
**From Host:**
```powershell
# HTTP tests only
python tests/week2/http_tests.py
```

**From Container:**
```bash
# WebSocket tests
docker exec exai-mcp-daemon python /app/test_suite.py
```

**Comprehensive Suite:**
```bash
# Copy test suite to container
docker cp tests/week2/comprehensive_test_suite.py exai-mcp-daemon:/app/test_suite.py

# Run all tests
docker exec exai-mcp-daemon python /app/test_suite.py
```

---

## 📈 Test Results History

### 2025-10-21 (Latest)
- **Total Tests:** 9
- **Passed:** 9 (100%)
- **Failed:** 0
- **Duration:** ~10 seconds
- **Notes:** All Week 2 fixes validated, monitoring UI CORS fixed

### 2025-10-21 (Earlier)
- **Total Tests:** 9
- **Passed:** 8 (88.9%)
- **Failed:** 1 (invalid request error)
- **Notes:** Fixed missing 'name' field validation

### 2025-10-20
- **Total Tests:** 4
- **Passed:** 4 (100%)
- **Failed:** 0
- **Notes:** Initial HTTP tests for monitoring UI

---

## ✅ Testing Best Practices

### Guidelines for New Tests

1. **Test Naming Convention:**
   - Use descriptive names: `test_<feature>_<scenario>`
   - Example: `test_error_handling_tool_not_found`

2. **Test Structure:**
   - Arrange: Set up test data and environment
   - Act: Execute the test action
   - Assert: Verify expected outcomes
   - Cleanup: Clean up resources

3. **Error Handling:**
   - Always test both success and failure paths
   - Verify error codes and messages
   - Check error response format

4. **Async Testing:**
   - Use `asyncio.run()` for async tests
   - Properly await all async operations
   - Handle timeouts gracefully

### Review Process

1. **Pre-commit:**
   - Run all tests locally
   - Ensure 100% pass rate
   - Check for new warnings/errors

2. **Code Review:**
   - Review test coverage
   - Verify test quality
   - Check for edge cases

3. **Post-merge:**
   - Run full test suite
   - Monitor Docker logs
   - Verify system health

### Regression Testing

1. **After Each Fix:**
   - Run comprehensive test suite
   - Verify no existing functionality broke
   - Update tests if needed

2. **Before Deployment:**
   - Run full test suite
   - Execute stress tests
   - Validate monitoring

3. **After Deployment:**
   - Monitor system health
   - Check error rates
   - Verify performance

---

## 🎯 Future Testing Plans

### Stress Testing (Planned)
- **Tool:** `scripts/stress_test_exai.py`
- **Duration:** 60+ minutes
- **Concurrent Requests:** 10+
- **Metrics:**
  - Response times
  - Success rates
  - Throughput
  - Memory usage
  - Semaphore utilization

### Load Testing (Planned)
- **Scenarios:**
  - Normal load (baseline)
  - Peak load (2x baseline)
  - Stress load (5x baseline)
  - Spike load (sudden 10x)

### Long-term Stability (Planned)
- **Duration:** 24+ hours
- **Monitoring:**
  - Memory leaks
  - Semaphore leaks
  - Error rates
  - Performance degradation

### Integration Testing (Planned)
- **Supabase Integration:**
  - File upload/download
  - Conversation persistence
  - Monitoring data storage

- **Provider Integration:**
  - Kimi API calls
  - GLM API calls
  - Error handling
  - Rate limiting

---

## 📚 References

- **Test Suite:** `tests/week2/comprehensive_test_suite.py`
- **Stress Test:** `scripts/stress_test_exai.py`
- **Testing Approach:** `fix_implementation/TESTING_APPROACH_HYBRID_2025-10-21.md`
- **Project Status:** `STATUS.md`
- **Roadmap:** `ROADMAP.md`

