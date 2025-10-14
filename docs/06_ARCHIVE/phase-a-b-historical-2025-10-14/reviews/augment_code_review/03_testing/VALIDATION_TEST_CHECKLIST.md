# VALIDATION TEST CHECKLIST - Comprehensive Testing Strategy

**Date:** 2025-10-04  
**Purpose:** Define all tests to run before, during, and after implementation  
**Coverage:** Pre-implementation baseline, post-implementation validation, regression, performance

---

## 🎯 Testing Philosophy

1. **Baseline First:** Test current state to confirm issues exist
2. **Test During:** Validate each fix immediately after implementation
3. **Regression Always:** Ensure no existing functionality breaks
4. **Performance Matters:** Verify acceptable performance at each step
5. **Document Everything:** Record all test results

---

## 📋 PRE-IMPLEMENTATION BASELINE TESTS

**Purpose:** Confirm issues exist before we fix them  
**When:** Before starting Week 1, Day 1  
**Expected:** Most tests should FAIL (confirming the problems)

### Baseline Test 1: Timeout Hierarchy Validation

**Test Script:**
```bash
# Test current timeout values
python3 -c "
import os
import sys
sys.path.insert(0, '.')

# Check current daemon timeout
from src.daemon.ws_server import CALL_TIMEOUT
print(f'Daemon timeout: {CALL_TIMEOUT}s')

# Check current shim timeout  
# Note: This will fail if TimeoutConfig doesn't exist yet
try:
    from config import TimeoutConfig
    print(f'Tool timeout: {TimeoutConfig.WORKFLOW_TOOL_TIMEOUT_SECS}s')
    print(f'Daemon timeout: {TimeoutConfig.get_daemon_timeout()}s')
    print(f'Shim timeout: {TimeoutConfig.get_shim_timeout()}s')
except ImportError:
    print('TimeoutConfig does not exist yet (expected)')
"
```

**Expected Baseline Result:**
- ❌ Daemon timeout = 600s (too long)
- ❌ TimeoutConfig does not exist
- ❌ No coordinated hierarchy

**File:** `tests/baseline/test_timeout_baseline.py` (CREATE)

---

### Baseline Test 2: Workflow Tool Timeout Behavior

**Test Script:**
```bash
# Test workflow tool timeout behavior
# This should hang for 600s (10 minutes)
time timeout 130s python3 -c "
import asyncio
import sys
sys.path.insert(0, '.')

async def test_workflow_timeout():
    # Simulate long-running workflow
    print('Starting workflow tool simulation...')
    await asyncio.sleep(200)  # Longer than desired timeout
    print('Workflow completed (should not reach here)')

asyncio.run(test_workflow_timeout())
"
```

**Expected Baseline Result:**
- ❌ Process runs for 130s (timeout command kills it)
- ❌ No timeout from workflow tool itself
- ❌ No progress updates during execution

**File:** `tests/baseline/test_workflow_timeout_baseline.sh` (CREATE)

---

### Baseline Test 3: Logging for Workflow Tools

**Test Script:**
```bash
# Clear logs
rm -f .logs/toolcalls.jsonl

# Run a simple tool (should log)
python3 -c "
import asyncio
import sys
sys.path.insert(0, '.')
from tools.simple.chat import ChatTool

async def test():
    tool = ChatTool()
    result = await tool.execute({'prompt': 'test'})
    
asyncio.run(test())
"

# Check if logs exist
echo "=== Simple Tool Logs ==="
cat .logs/toolcalls.jsonl | jq 'select(.tool == "chat")' 2>/dev/null || echo "No logs found"

# Clear logs
rm -f .logs/toolcalls.jsonl

# Run a workflow tool (should NOT log currently)
# Note: This may fail if workflow tools are broken
echo "=== Workflow Tool Logs ==="
# (Add workflow tool test here when we know which one works)
cat .logs/toolcalls.jsonl | jq 'select(.tool == "thinkdeep")' 2>/dev/null || echo "No logs found"
```

**Expected Baseline Result:**
- ✅ Simple tool logs appear
- ❌ Workflow tool logs do NOT appear
- ❌ No unified logging infrastructure

**File:** `tests/baseline/test_logging_baseline.sh` (CREATE)

---

### Baseline Test 4: Progress Heartbeat

**Test Script:**
```bash
# Test for progress heartbeat (should not exist)
python3 -c "
import sys
sys.path.insert(0, '.')

try:
    from utils.progress import ProgressHeartbeat
    print('ProgressHeartbeat exists (unexpected)')
except ImportError:
    print('ProgressHeartbeat does not exist (expected)')
"
```

**Expected Baseline Result:**
- ❌ ProgressHeartbeat does not exist
- ❌ No progress updates during long operations

**File:** `tests/baseline/test_progress_baseline.py` (CREATE)

---

### Baseline Test 5: Expert Validation Status

**Test Script:**
```bash
# Check if expert validation is enabled
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()

use_assistant = os.getenv('DEFAULT_USE_ASSISTANT_MODEL', 'false')
print(f'Expert validation enabled: {use_assistant}')

if use_assistant.lower() == 'false':
    print('✓ Expert validation is disabled (expected)')
else:
    print('✗ Expert validation is enabled (unexpected)')
"
```

**Expected Baseline Result:**
- ✅ Expert validation is disabled (DEFAULT_USE_ASSISTANT_MODEL=false)

**File:** `tests/baseline/test_expert_validation_baseline.sh` (CREATE)

---

## ✅ POST-IMPLEMENTATION VALIDATION TESTS

**Purpose:** Verify each fix works correctly  
**When:** After completing each fix  
**Expected:** All tests should PASS

### Week 1, Day 1-2: Timeout Hierarchy Tests

#### Test 1.1: TimeoutConfig Class Validation

**Test Script:**
```python
# File: tests/week1/test_timeout_config.py
import pytest
from config import TimeoutConfig

def test_timeout_config_exists():
    """Test that TimeoutConfig class exists."""
    assert TimeoutConfig is not None

def test_timeout_hierarchy_validation():
    """Test that timeout hierarchy validates correctly."""
    assert TimeoutConfig.validate_hierarchy() == True

def test_timeout_values():
    """Test that timeout values are correct."""
    assert TimeoutConfig.SIMPLE_TOOL_TIMEOUT_SECS == 60
    assert TimeoutConfig.WORKFLOW_TOOL_TIMEOUT_SECS == 120
    assert TimeoutConfig.EXPERT_ANALYSIS_TIMEOUT_SECS == 90
    
def test_daemon_timeout_calculation():
    """Test that daemon timeout is calculated correctly."""
    assert TimeoutConfig.get_daemon_timeout() == 180  # 1.5x 120
    
def test_shim_timeout_calculation():
    """Test that shim timeout is calculated correctly."""
    assert TimeoutConfig.get_shim_timeout() == 240  # 2x 120
    
def test_client_timeout_calculation():
    """Test that client timeout is calculated correctly."""
    assert TimeoutConfig.get_client_timeout() == 300  # 2.5x 120

def test_timeout_hierarchy_order():
    """Test that timeouts are in correct order."""
    tool = TimeoutConfig.WORKFLOW_TOOL_TIMEOUT_SECS
    daemon = TimeoutConfig.get_daemon_timeout()
    shim = TimeoutConfig.get_shim_timeout()
    client = TimeoutConfig.get_client_timeout()
    
    assert tool < daemon < shim < client
```

**Run Command:**
```bash
pytest tests/week1/test_timeout_config.py -v
```

**Expected Result:** All tests PASS

---

#### Test 1.2: Daemon Timeout Integration

**Test Script:**
```python
# File: tests/week1/test_daemon_timeout.py
import pytest
from src.daemon.ws_server import CALL_TIMEOUT
from config import TimeoutConfig

def test_daemon_uses_timeout_config():
    """Test that daemon uses TimeoutConfig."""
    expected = TimeoutConfig.get_daemon_timeout()
    assert CALL_TIMEOUT == expected
    assert CALL_TIMEOUT == 180
```

**Run Command:**
```bash
pytest tests/week1/test_daemon_timeout.py -v
```

**Expected Result:** All tests PASS

---

#### Test 1.3: Shim Timeout Integration

**Test Script:**
```python
# File: tests/week1/test_shim_timeout.py
import pytest
from scripts.run_ws_shim import RPC_TIMEOUT
from config import TimeoutConfig

def test_shim_uses_timeout_config():
    """Test that shim uses TimeoutConfig."""
    expected = TimeoutConfig.get_shim_timeout()
    assert RPC_TIMEOUT == expected
    assert RPC_TIMEOUT == 240
```

**Run Command:**
```bash
pytest tests/week1/test_shim_timeout.py -v
```

**Expected Result:** All tests PASS

---

#### Test 1.4: Workflow Tool Timeout Behavior

**Test Script:**
```python
# File: tests/week1/test_workflow_timeout_behavior.py
import pytest
import asyncio
import time
from tools.workflow.base import WorkflowTool
from config import TimeoutConfig

@pytest.mark.asyncio
async def test_workflow_tool_timeout():
    """Test that workflow tool times out at expected time."""
    
    class TestWorkflowTool(WorkflowTool):
        async def _execute_workflow(self, request):
            # Simulate long operation
            await asyncio.sleep(200)  # Longer than timeout
            
    tool = TestWorkflowTool()
    tool.timeout_secs = TimeoutConfig.WORKFLOW_TOOL_TIMEOUT_SECS
    
    start = time.time()
    
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(
            tool._execute_workflow({}),
            timeout=tool.timeout_secs
        )
    
    duration = time.time() - start
    
    # Should timeout around 120s, not 600s
    assert 115 <= duration <= 125, f"Timeout took {duration}s, expected ~120s"
```

**Run Command:**
```bash
pytest tests/week1/test_workflow_timeout_behavior.py -v
```

**Expected Result:** Test PASSES (timeout at 120s)

---

#### Test 1.5: MCP Configuration Updates

**Test Script:**
```bash
# File: tests/week1/test_mcp_configs.sh
#!/bin/bash

echo "=== Testing MCP Configuration Updates ==="

# Test Auggie config
echo "Checking Daemon/mcp-config.auggie.json..."
if grep -q '"SIMPLE_TOOL_TIMEOUT_SECS": "60"' Daemon/mcp-config.auggie.json; then
    echo "✓ Auggie config has SIMPLE_TOOL_TIMEOUT_SECS=60"
else
    echo "✗ Auggie config missing SIMPLE_TOOL_TIMEOUT_SECS"
    exit 1
fi

if grep -q '"WORKFLOW_TOOL_TIMEOUT_SECS": "120"' Daemon/mcp-config.auggie.json; then
    echo "✓ Auggie config has WORKFLOW_TOOL_TIMEOUT_SECS=120"
else
    echo "✗ Auggie config missing WORKFLOW_TOOL_TIMEOUT_SECS"
    exit 1
fi

# Test Augment config
echo "Checking Daemon/mcp-config.augmentcode.json..."
if grep -q '"SIMPLE_TOOL_TIMEOUT_SECS": "60"' Daemon/mcp-config.augmentcode.json; then
    echo "✓ Augment config has SIMPLE_TOOL_TIMEOUT_SECS=60"
else
    echo "✗ Augment config missing SIMPLE_TOOL_TIMEOUT_SECS"
    exit 1
fi

# Test Claude config
echo "Checking Daemon/mcp-config.claude.json..."
if grep -q '"SIMPLE_TOOL_TIMEOUT_SECS": "60"' Daemon/mcp-config.claude.json; then
    echo "✓ Claude config has SIMPLE_TOOL_TIMEOUT_SECS=60"
else
    echo "✗ Claude config missing SIMPLE_TOOL_TIMEOUT_SECS"
    exit 1
fi

echo "=== All MCP configs updated correctly ==="
```

**Run Command:**
```bash
bash tests/week1/test_mcp_configs.sh
```

**Expected Result:** All checks PASS

---

### Week 1, Day 3-4: Progress Heartbeat Tests

#### Test 2.1: ProgressHeartbeat Class Exists

**Test Script:**
```python
# File: tests/week1/test_progress_heartbeat.py
import pytest
import asyncio
import time
from utils.progress import ProgressHeartbeat, ProgressTracker, get_progress_tracker

def test_progress_heartbeat_exists():
    """Test that ProgressHeartbeat class exists."""
    assert ProgressHeartbeat is not None

def test_progress_tracker_exists():
    """Test that ProgressTracker class exists."""
    assert ProgressTracker is not None

def test_get_progress_tracker():
    """Test that get_progress_tracker returns instance."""
    tracker = get_progress_tracker()
    assert isinstance(tracker, ProgressTracker)

@pytest.mark.asyncio
async def test_heartbeat_timing():
    """Test that heartbeat sends at correct interval."""
    messages = []
    
    async def callback(data):
        messages.append(data)
    
    async with ProgressHeartbeat(interval_secs=2.0, callback=callback) as hb:
        for i in range(10):
            await hb.send_heartbeat(f"Step {i}")
            await asyncio.sleep(1)
    
    # Should have ~5 messages (10 seconds / 2 second interval)
    assert 4 <= len(messages) <= 6, f"Expected 4-6 messages, got {len(messages)}"

@pytest.mark.asyncio
async def test_progress_calculation():
    """Test that progress calculates estimated remaining time."""
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
```

**Run Command:**
```bash
pytest tests/week1/test_progress_heartbeat.py -v
```

**Expected Result:** All tests PASS

---

## 🔄 REGRESSION TESTS

**Purpose:** Ensure fixes don't break existing functionality  
**When:** After each major fix  
**Expected:** All tests should PASS

### Regression Test 1: Simple Tools Still Work

**Test Script:**
```bash
# File: tests/regression/test_simple_tools.sh
#!/bin/bash

echo "=== Testing Simple Tools (Regression) ==="

# Test listmodels
echo "Testing listmodels..."
timeout 10s python3 -c "
import asyncio
import sys
sys.path.insert(0, '.')

async def test():
    # Test listmodels tool
    print('Testing listmodels...')
    # Add actual test here
    
asyncio.run(test())
" && echo "✓ listmodels works" || echo "✗ listmodels failed"

# Test chat (without web search)
echo "Testing chat..."
timeout 35s python3 -c "
import asyncio
import sys
sys.path.insert(0, '.')

async def test():
    # Test chat tool
    print('Testing chat...')
    # Add actual test here
    
asyncio.run(test())
" && echo "✓ chat works" || echo "✗ chat failed"

echo "=== Simple Tools Regression Complete ==="
```

**Run Command:**
```bash
bash tests/regression/test_simple_tools.sh
```

**Expected Result:** All simple tools still work

---

## 📊 PERFORMANCE BENCHMARKS

**Purpose:** Verify acceptable performance  
**When:** After completing all Week 1 fixes  
**Expected:** Performance within acceptable thresholds

### Performance Test 1: Timeout Overhead

**Test Script:**
```python
# File: tests/performance/test_timeout_overhead.py
import pytest
import asyncio
import time
from config import TimeoutConfig

@pytest.mark.asyncio
async def test_timeout_config_overhead():
    """Test that TimeoutConfig has minimal overhead."""
    iterations = 1000
    
    start = time.time()
    for _ in range(iterations):
        _ = TimeoutConfig.get_daemon_timeout()
        _ = TimeoutConfig.get_shim_timeout()
        _ = TimeoutConfig.get_client_timeout()
    duration = time.time() - start
    
    # Should complete 1000 iterations in < 0.1s
    assert duration < 0.1, f"TimeoutConfig overhead too high: {duration}s for {iterations} iterations"
```

**Run Command:**
```bash
pytest tests/performance/test_timeout_overhead.py -v
```

**Expected Result:** Overhead < 0.1s for 1000 iterations

---

### Performance Test 2: Progress Heartbeat Overhead

**Test Script:**
```python
# File: tests/performance/test_progress_overhead.py
import pytest
import asyncio
import time
from utils.progress import ProgressHeartbeat

@pytest.mark.asyncio
async def test_heartbeat_overhead():
    """Test that heartbeat has minimal performance impact."""
    
    # Test without heartbeat
    start = time.time()
    for i in range(100):
        await asyncio.sleep(0.01)
    baseline = time.time() - start
    
    # Test with heartbeat
    start = time.time()
    async with ProgressHeartbeat(interval_secs=0.5) as hb:
        for i in range(100):
            await hb.send_heartbeat(f"Step {i}")
            await asyncio.sleep(0.01)
    with_heartbeat = time.time() - start
    
    overhead = with_heartbeat - baseline
    overhead_percent = (overhead / baseline) * 100
    
    # Overhead should be < 5%
    assert overhead_percent < 5, f"Heartbeat overhead too high: {overhead_percent:.1f}%"
```

**Run Command:**
```bash
pytest tests/performance/test_progress_overhead.py -v
```

**Expected Result:** Overhead < 5%

---

## 📝 TEST SCRIPT INVENTORY

### Scripts to CREATE:

**Baseline Tests:**
- [ ] `tests/baseline/test_timeout_baseline.py`
- [ ] `tests/baseline/test_workflow_timeout_baseline.sh`
- [ ] `tests/baseline/test_logging_baseline.sh`
- [ ] `tests/baseline/test_progress_baseline.py`
- [ ] `tests/baseline/test_expert_validation_baseline.sh`

**Week 1 Tests:**
- [ ] `tests/week1/test_timeout_config.py`
- [ ] `tests/week1/test_daemon_timeout.py`
- [ ] `tests/week1/test_shim_timeout.py`
- [ ] `tests/week1/test_workflow_timeout_behavior.py`
- [ ] `tests/week1/test_mcp_configs.sh`
- [ ] `tests/week1/test_progress_heartbeat.py`
- [ ] `tests/week1/test_unified_logging.py`

**Regression Tests:**
- [ ] `tests/regression/test_simple_tools.sh`
- [ ] `tests/regression/test_api_integration.py`
- [ ] `tests/regression/test_websocket_daemon.py`

**Performance Tests:**
- [ ] `tests/performance/test_timeout_overhead.py`
- [ ] `tests/performance/test_progress_overhead.py`
- [ ] `tests/performance/test_logging_overhead.py`

### Scripts to MODIFY:

- [ ] Existing test suite (if any) to use new TimeoutConfig

### Scripts to EXECUTE:

**Before Implementation:**
```bash
# Run baseline tests
pytest tests/baseline/ -v
bash tests/baseline/*.sh
```

**After Day 1-2 (Timeout Hierarchy):**
```bash
pytest tests/week1/test_timeout_config.py -v
pytest tests/week1/test_daemon_timeout.py -v
pytest tests/week1/test_shim_timeout.py -v
pytest tests/week1/test_workflow_timeout_behavior.py -v
bash tests/week1/test_mcp_configs.sh
```

**After Day 3-4 (Progress Heartbeat):**
```bash
pytest tests/week1/test_progress_heartbeat.py -v
```

**After Day 5 (Unified Logging):**
```bash
pytest tests/week1/test_unified_logging.py -v
```

**After Week 1 Complete:**
```bash
# Run all Week 1 tests
pytest tests/week1/ -v

# Run regression tests
bash tests/regression/test_simple_tools.sh
pytest tests/regression/ -v

# Run performance tests
pytest tests/performance/ -v
```

---

## ✅ ACCEPTANCE CRITERIA SUMMARY

**Week 1 Complete When:**
- [ ] All baseline tests show issues (confirming problems exist)
- [ ] All Week 1 tests PASS
- [ ] All regression tests PASS
- [ ] All performance tests PASS
- [ ] Workflow tools timeout at 120s (not 600s)
- [ ] Progress updates visible every 5-8 seconds
- [ ] All tool executions logged correctly
- [ ] No existing functionality broken
- [ ] Performance overhead < 5%

