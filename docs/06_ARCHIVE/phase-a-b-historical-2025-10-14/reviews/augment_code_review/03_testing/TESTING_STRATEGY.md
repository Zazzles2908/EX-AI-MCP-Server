# TESTING STRATEGY - Comprehensive Validation Approach

**Date:** 2025-10-04  
**Purpose:** Define testing approach for all fixes  
**Coverage:** Unit, Integration, E2E, Performance

---

## 🎯 Testing Philosophy

1. **Test Before Fix:** Verify issue exists
2. **Test During Fix:** Validate each step
3. **Test After Fix:** Confirm issue resolved
4. **Regression Test:** Ensure nothing broke
5. **Performance Test:** Verify acceptable performance

---

## 📋 Test Categories

### 1. Unit Tests
**Purpose:** Test individual components in isolation  
**When:** During implementation of each fix  
**Tools:** pytest, unittest

### 2. Integration Tests
**Purpose:** Test components working together  
**When:** After completing each phase  
**Tools:** pytest, asyncio

### 3. End-to-End Tests
**Purpose:** Test complete user workflows  
**When:** After completing all fixes  
**Tools:** Manual testing, automated scripts

### 4. Performance Tests
**Purpose:** Verify acceptable performance  
**When:** After completing all fixes  
**Tools:** time, profiling, benchmarks

### 5. Regression Tests
**Purpose:** Ensure fixes don't break existing functionality  
**When:** After each fix  
**Tools:** Existing test suite

---

## 🧪 WEEK 1: P0 Critical Fixes Testing

### Fix #1: Timeout Hierarchy - Testing

**Unit Tests:**
```python
# Test 1: Timeout hierarchy validation
def test_timeout_hierarchy_validation():
    from config import TimeoutConfig
    
    # Should validate successfully
    assert TimeoutConfig.validate_hierarchy() == True
    
    # Check values
    assert TimeoutConfig.WORKFLOW_TOOL_TIMEOUT_SECS == 120
    assert TimeoutConfig.get_daemon_timeout() == 180
    assert TimeoutConfig.get_shim_timeout() == 240
    assert TimeoutConfig.get_client_timeout() == 300
    
    # Check hierarchy
    assert TimeoutConfig.WORKFLOW_TOOL_TIMEOUT_SECS < TimeoutConfig.get_daemon_timeout()
    assert TimeoutConfig.get_daemon_timeout() < TimeoutConfig.get_shim_timeout()
    assert TimeoutConfig.get_shim_timeout() < TimeoutConfig.get_client_timeout()

# Test 2: Workflow tool timeout
async def test_workflow_tool_timeout():
    from tools.workflows.thinkdeep import ThinkDeepTool
    import asyncio
    
    tool = ThinkDeepTool()
    
    # Create request that will timeout
    request = {"prompt": "test", "steps": 10}
    
    start = time.time()
    try:
        # Should timeout at 120s
        result = await asyncio.wait_for(
            tool.execute(request),
            timeout=125  # Slightly longer than tool timeout
        )
        assert False, "Should have timed out"
    except asyncio.TimeoutError:
        duration = time.time() - start
        # Should timeout around 120s, not 600s
        assert 115 <= duration <= 125

# Test 3: Expert validation timeout
async def test_expert_validation_timeout():
    from tools.workflow.expert_analysis import ExpertAnalysis
    
    expert = ExpertAnalysis()
    timeout = expert.get_expert_timeout_secs()
    
    # Should be 90s from TimeoutConfig
    assert timeout == 90.0
```

**Integration Tests:**
```bash
# Test 1: Verify daemon timeout
# Start daemon and verify it uses 180s timeout
python3 -c "
from src.daemon.ws_server import CALL_TIMEOUT
assert CALL_TIMEOUT == 180, f'Expected 180, got {CALL_TIMEOUT}'
print('✅ Daemon timeout correct: 180s')
"

# Test 2: Verify shim timeout
# Start shim and verify it uses 240s timeout
python3 -c "
from scripts.run_ws_shim import RPC_TIMEOUT
assert RPC_TIMEOUT == 240, f'Expected 240, got {RPC_TIMEOUT}'
print('✅ Shim timeout correct: 240s')
"

# Test 3: Test workflow tool with real timeout
# Should timeout at 120s, not 600s
time python3 -c "
import asyncio
from tools.workflows.thinkdeep import ThinkDeepTool

async def test():
    tool = ThinkDeepTool()
    # Simulate long operation
    await asyncio.sleep(200)

asyncio.run(test())
"
# Expected: Timeout after ~120 seconds
```

**Acceptance Criteria:**
- [ ] TimeoutConfig validates hierarchy on import
- [ ] Daemon timeout = 180s
- [ ] Shim timeout = 240s
- [ ] Workflow tools timeout at 120s
- [ ] Expert validation timeouts at 90s
- [ ] All three MCP configs updated
- [ ] No regression in simple tools

---

### Fix #2: Progress Heartbeat - Testing

**Unit Tests:**
```python
# Test 1: Heartbeat timing
async def test_heartbeat_timing():
    from utils.progress import ProgressHeartbeat
    
    messages = []
    
    async def callback(data):
        messages.append(data)
    
    async with ProgressHeartbeat(interval_secs=2.0, callback=callback) as hb:
        for i in range(10):
            await hb.send_heartbeat(f"Step {i}")
            await asyncio.sleep(1)
    
    # Should have ~5 messages (10 seconds / 2 second interval)
    assert 4 <= len(messages) <= 6
    print(f"✅ Heartbeat timing correct: {len(messages)} messages in 10s")

# Test 2: Progress calculation
async def test_progress_calculation():
    from utils.progress import ProgressHeartbeat
    
    messages = []
    
    async def callback(data):
        messages.append(data)
    
    async with ProgressHeartbeat(interval_secs=1.0, callback=callback) as hb:
        hb.set_total_steps(5)
        
        for i in range(1, 6):
            hb.set_current_step(i)
            await hb.force_heartbeat(f"Step {i}")
            await asyncio.sleep(1)
    
    # Check last message has progress info
    last_msg = messages[-1]
    assert last_msg["step"] == 5
    assert last_msg["total_steps"] == 5
    assert last_msg["elapsed_secs"] >= 5
    assert last_msg["estimated_remaining_secs"] is not None

# Test 3: Heartbeat in workflow tool
async def test_workflow_tool_heartbeat():
    from tools.workflow.base import WorkflowTool
    
    # Mock workflow tool
    class TestWorkflowTool(WorkflowTool):
        async def _execute_step(self, step_num, request):
            await asyncio.sleep(2)
            return {"step": step_num}
    
    tool = TestWorkflowTool()
    
    # Execute and verify heartbeats sent
    # (Implementation depends on how heartbeat is integrated)
```

**Integration Tests:**
```bash
# Test 1: Workflow tool sends progress
# Run thinkdeep tool and verify progress messages
# Should see progress every 6 seconds

# Test 2: Expert validation sends progress
# Run debug tool and verify expert validation progress
# Should see progress every 8 seconds

# Test 3: Provider calls send progress
# Run chat tool with long prompt
# Should see streaming progress every 5 seconds
```

**Acceptance Criteria:**
- [ ] ProgressHeartbeat sends updates at configured interval
- [ ] Workflow tools send progress every 6 seconds
- [ ] Expert validation sends progress every 8 seconds
- [ ] Provider calls send progress every 5 seconds
- [ ] Progress includes elapsed time and estimated remaining
- [ ] WebSocket server routes progress to clients
- [ ] No performance degradation

---

### Fix #3: Unified Logging - Testing

**Unit Tests:**
```python
# Test 1: UnifiedLogger basic functionality
def test_unified_logger_basic():
    from utils.logging_unified import UnifiedLogger
    import tempfile
    import json
    
    # Create temp log file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.jsonl') as f:
        log_file = f.name
    
    logger = UnifiedLogger(log_file=log_file)
    
    # Log tool start
    logger.log_tool_start("test_tool", "req-123", {"param": "value"})
    
    # Log tool complete
    logger.log_tool_complete("test_tool", "req-123", 1.5, "result preview")
    
    # Flush buffer
    logger.flush()
    
    # Read log file
    with open(log_file, 'r') as f:
        lines = f.readlines()
    
    assert len(lines) == 2
    
    # Check first entry
    entry1 = json.loads(lines[0])
    assert entry1["event"] == "tool_start"
    assert entry1["tool"] == "test_tool"
    assert entry1["request_id"] == "req-123"
    
    # Check second entry
    entry2 = json.loads(lines[1])
    assert entry2["event"] == "tool_complete"
    assert entry2["duration_s"] == 1.5

# Test 2: Simple tool logging
async def test_simple_tool_logging():
    from tools.simple.chat import ChatTool
    
    tool = ChatTool()
    
    # Execute tool
    result = await tool.execute({"prompt": "test"})
    
    # Verify log entry created
    # (Check .logs/toolcalls.jsonl)

# Test 3: Workflow tool logging
async def test_workflow_tool_logging():
    from tools.workflows.thinkdeep import ThinkDeepTool
    
    tool = ThinkDeepTool()
    
    # Execute tool
    result = await tool.execute({"prompt": "test", "steps": 2})
    
    # Verify log entries for all steps
    # (Check .logs/toolcalls.jsonl)
```

**Integration Tests:**
```bash
# Test 1: Simple tool logging
# Run chat tool and verify log entry
tail -f .logs/toolcalls.jsonl | jq 'select(.tool == "chat")'

# Test 2: Workflow tool logging
# Run thinkdeep tool and verify all steps logged
tail -f .logs/toolcalls.jsonl | jq 'select(.tool == "thinkdeep")'

# Test 3: Expert validation logging
# Run debug tool and verify expert validation logged
tail -f .logs/toolcalls.jsonl | jq 'select(.event == "expert_validation_start")'
```

**Acceptance Criteria:**
- [ ] UnifiedLogger created with structured logging
- [ ] Simple tools use unified logger
- [ ] Workflow tools use unified logger
- [ ] Expert validation logged correctly
- [ ] All executions appear in .logs/toolcalls.jsonl
- [ ] Request IDs tracked throughout
- [ ] Errors logged with full traceback

---

## 🧪 WEEK 2: P1 High Priority Fixes Testing

### Fix #4: Expert Validation - Testing

**Unit Tests:**
```python
# Test 1: Call deduplication
async def test_expert_validation_deduplication():
    from tools.workflow.expert_analysis import ExpertAnalysis
    
    expert = ExpertAnalysis()
    
    # Call validation twice with same content
    result1 = await expert.validate_with_expert("req-123", "test content", {})
    result2 = await expert.validate_with_expert("req-123", "test content", {})
    
    # Second call should use cache
    assert result1 == result2
    # Verify only one actual API call made (check logs)

# Test 2: Circuit breaker
async def test_expert_validation_circuit_breaker():
    from tools.workflow.expert_analysis import ExpertAnalysis
    
    expert = ExpertAnalysis()
    
    # Simulate 5 failures
    for i in range(5):
        try:
            await expert.validate_with_expert(f"req-{i}", "fail", {})
        except:
            pass
    
    # Circuit should be open
    # Next call should fail fast
    start = time.time()
    try:
        await expert.validate_with_expert("req-6", "test", {})
        assert False, "Should have failed fast"
    except CircuitBreakerOpen:
        duration = time.time() - start
        assert duration < 1.0  # Should fail immediately
```

**Integration Tests:**
```bash
# Test 1: Expert validation enabled
# Verify DEFAULT_USE_ASSISTANT_MODEL=true in .env

# Test 2: Expert validation works
# Run debug tool with 2 steps
# Verify expert_analysis is not null
# Verify duration is 90-120 seconds (not 300+)

# Test 3: Expert validation called once per step
# Run debug tool with 2 steps
# Check logs for expert validation calls
# Should see exactly 2 calls (one per step)
```

**Acceptance Criteria:**
- [ ] Expert analysis called exactly once per step
- [ ] Call deduplication implemented
- [ ] Circuit breaker prevents runaway calls
- [ ] Expert validation re-enabled
- [ ] Duration is 90-120 seconds (not 300+)
- [ ] Expert_analysis contains real content

---

## 🧪 WEEK 3: P2 Enhancements Testing

### Fix #6: Web Search Verification - Testing

**Unit Tests:**
```python
# Test 1: GLM web search
async def test_glm_web_search():
    from tools.simple.chat import ChatTool
    
    tool = ChatTool()
    
    # Execute with web search
    result = await tool.execute({
        "prompt": "Latest AI news?",
        "use_websearch": True
    })
    
    # Verify web search was used
    # (Check logs for web search activation)

# Test 2: Kimi web search
async def test_kimi_web_search():
    from tools.simple.chat import ChatTool
    
    tool = ChatTool()
    
    # Execute with Kimi and web search
    result = await tool.execute({
        "prompt": "Latest AI news?",
        "model": "kimi-k2-0905-preview",
        "use_websearch": True
    })
    
    # Verify web search was used
    # (Check logs for web search activation)
```

**Integration Tests:**
```bash
# Test 1: GLM web search end-to-end
chat_exai(prompt="Latest AI news?", use_websearch=true)
# Verify web search logged
tail -f .logs/toolcalls.jsonl | grep web_search

# Test 2: Kimi web search end-to-end
chat_exai(prompt="Latest AI news?", model="kimi-k2-0905-preview", use_websearch=true)
# Verify web search logged
tail -f .logs/toolcalls.jsonl | grep web_search
```

**Acceptance Criteria:**
- [ ] Web search activation logged
- [ ] Tests verify GLM web search works
- [ ] Tests verify Kimi web search works
- [ ] Web search flow documented
- [ ] Metrics track web search usage

---

## 📊 Performance Testing

### Baseline Performance Targets

**Simple Tools:**
- listmodels: < 5s
- chat (no web search): < 30s
- chat (with web search): < 45s

**Workflow Tools:**
- debug (2 steps): 60-120s
- thinkdeep (3 steps): 90-180s
- analyze (4 steps): 120-240s
- codereview (5 steps): 150-300s

**Infrastructure:**
- Daemon startup: < 5s
- Shim connection: < 2s
- WebSocket latency: < 100ms

### Performance Test Suite

```bash
# Test 1: Simple tool performance
time listmodels_exai()
# Expected: < 5s

# Test 2: Chat tool performance
time chat_exai(prompt="Hello")
# Expected: < 30s

# Test 3: Workflow tool performance
time debug_exai(prompt="test", steps=2)
# Expected: 60-120s

# Test 4: Progress heartbeat overhead
# Run workflow tool and measure heartbeat overhead
# Expected: < 1% performance impact
```

---

## 🎯 Final Validation Checklist

**Before Declaring Production-Ready:**

- [ ] All P0 fixes tested and passing
- [ ] All P1 fixes tested and passing
- [ ] All P2 fixes tested and passing
- [ ] No regressions in existing functionality
- [ ] Performance targets met
- [ ] All three clients tested (VSCode, Auggie, Claude)
- [ ] Documentation updated
- [ ] Troubleshooting guide created
- [ ] All tests automated where possible
- [ ] Manual test results documented

**Success Criteria:**
- ✅ All workflow tools complete in expected time
- ✅ Progress updates visible every 5-8 seconds
- ✅ All tool executions logged correctly
- ✅ Expert validation working correctly
- ✅ Web search verified working
- ✅ No hanging or timeout issues
- ✅ Graceful error handling
- ✅ Production-ready system

