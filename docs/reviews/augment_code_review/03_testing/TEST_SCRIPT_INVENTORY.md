# TEST SCRIPT INVENTORY - Complete Test Suite

**Date:** 2025-10-04  
**Purpose:** Comprehensive inventory of all test scripts to create, modify, and execute  
**Coverage:** Baseline, Week 1-3, Regression, Performance, Integration

---

## 📋 SCRIPTS TO CREATE

### Baseline Tests (Run Before Implementation)

#### 1. `tests/baseline/test_timeout_baseline.py`
**Purpose:** Verify current timeout values are incorrect  
**Expected:** FAIL (confirms problem exists)  
**Lines:** ~50  
**Dependencies:** None

```python
# Test current timeout configuration
# Verify daemon timeout = 600s (too long)
# Verify no TimeoutConfig class exists
```

---

#### 2. `tests/baseline/test_workflow_timeout_baseline.sh`
**Purpose:** Verify workflow tools hang for 600s  
**Expected:** FAIL (timeout from shell, not from tool)  
**Lines:** ~30  
**Dependencies:** timeout command

```bash
# Test workflow tool timeout behavior
# Should hang for 600s (killed by timeout command at 130s)
```

---

#### 3. `tests/baseline/test_logging_baseline.sh`
**Purpose:** Verify workflow tools don't log  
**Expected:** FAIL (no logs for workflow tools)  
**Lines:** ~40  
**Dependencies:** jq

```bash
# Test simple tool logging (should work)
# Test workflow tool logging (should NOT work)
```

---

#### 4. `tests/baseline/test_progress_baseline.py`
**Purpose:** Verify ProgressHeartbeat doesn't exist  
**Expected:** FAIL (ImportError)  
**Lines:** ~20  
**Dependencies:** None

```python
# Try to import ProgressHeartbeat
# Should fail with ImportError
```

---

#### 5. `tests/baseline/test_expert_validation_baseline.sh`
**Purpose:** Verify expert validation is disabled  
**Expected:** PASS (confirms it's disabled)  
**Lines:** ~25  
**Dependencies:** python-dotenv

```bash
# Check DEFAULT_USE_ASSISTANT_MODEL=false
```

---

### Week 1 Tests (Timeout Hierarchy - Day 1-2)

#### 6. `tests/week1/test_timeout_config.py`
**Purpose:** Validate TimeoutConfig class implementation  
**Expected:** PASS after Day 1 complete  
**Lines:** ~100  
**Dependencies:** pytest, config.py

```python
# 7 test functions:
# - test_timeout_config_exists()
# - test_timeout_hierarchy_validation()
# - test_timeout_values()
# - test_daemon_timeout_calculation()
# - test_shim_timeout_calculation()
# - test_client_timeout_calculation()
# - test_timeout_hierarchy_order()
```

---

#### 7. `tests/week1/test_daemon_timeout.py`
**Purpose:** Verify daemon uses TimeoutConfig  
**Expected:** PASS after Day 1.2 complete  
**Lines:** ~30  
**Dependencies:** pytest, src/daemon/ws_server.py

```python
# Test CALL_TIMEOUT = 180s
# Test daemon imports TimeoutConfig
```

---

#### 8. `tests/week1/test_shim_timeout.py`
**Purpose:** Verify shim uses TimeoutConfig  
**Expected:** PASS after Day 1.3 complete  
**Lines:** ~30  
**Dependencies:** pytest, scripts/run_ws_shim.py

```python
# Test RPC_TIMEOUT = 240s
# Test shim imports TimeoutConfig
```

---

#### 9. `tests/week1/test_workflow_timeout_behavior.py`
**Purpose:** Verify workflow tools timeout at 120s  
**Expected:** PASS after Day 1.4 complete  
**Lines:** ~50  
**Dependencies:** pytest, pytest-asyncio, tools/workflow/base.py

```python
# Test workflow tool times out at 120s (not 600s)
# Test timeout error message is correct
```

---

#### 10. `tests/week1/test_mcp_configs.sh`
**Purpose:** Verify all 3 MCP configs updated  
**Expected:** PASS after Day 1.6 complete  
**Lines:** ~60  
**Dependencies:** grep, bash

```bash
# Check Daemon/mcp-config.auggie.json
# Check Daemon/mcp-config.augmentcode.json
# Check Daemon/mcp-config.claude.json
# Verify all have SIMPLE_TOOL_TIMEOUT_SECS=60
# Verify all have WORKFLOW_TOOL_TIMEOUT_SECS=120
```

---

### Week 1 Tests (Progress Heartbeat - Day 3-4)

#### 11. `tests/week1/test_progress_heartbeat.py`
**Purpose:** Validate ProgressHeartbeat implementation  
**Expected:** PASS after Day 3-4 complete  
**Lines:** ~120  
**Dependencies:** pytest, pytest-asyncio, utils/progress.py

```python
# 5 test functions:
# - test_progress_heartbeat_exists()
# - test_progress_tracker_exists()
# - test_get_progress_tracker()
# - test_heartbeat_timing()
# - test_progress_calculation()
```

---

#### 12. `tests/week1/test_progress_integration.py`
**Purpose:** Verify progress heartbeat integrated in tools  
**Expected:** PASS after Day 3-4 complete  
**Lines:** ~80  
**Dependencies:** pytest, pytest-asyncio, tools/workflow/base.py

```python
# Test workflow tools send progress updates
# Test expert analysis sends progress updates
# Test provider calls send progress updates
```

---

### Week 1 Tests (Unified Logging - Day 5)

#### 13. `tests/week1/test_unified_logging.py`
**Purpose:** Validate UnifiedLogger implementation  
**Expected:** PASS after Day 5 complete  
**Lines:** ~150  
**Dependencies:** pytest, utils/logging_unified.py

```python
# 8 test functions:
# - test_unified_logger_exists()
# - test_log_tool_start()
# - test_log_tool_progress()
# - test_log_tool_complete()
# - test_log_tool_error()
# - test_log_expert_validation()
# - test_sanitize_params()
# - test_buffer_flush()
```

---

#### 14. `tests/week1/test_logging_integration.py`
**Purpose:** Verify all tools use unified logger  
**Expected:** PASS after Day 5 complete  
**Lines:** ~100  
**Dependencies:** pytest, pytest-asyncio, all tool files

```python
# Test simple tools log correctly
# Test workflow tools log correctly
# Test expert validation logs correctly
# Test all logs appear in .logs/toolcalls.jsonl
```

---

### Week 2 Tests (Expert Validation - Day 6-8)

#### 15. `tests/week2/test_expert_validation_deduplication.py`
**Purpose:** Verify expert validation called once per step  
**Expected:** PASS after Week 2 complete  
**Lines:** ~80  
**Dependencies:** pytest, pytest-asyncio, tools/workflow/expert_analysis.py

```python
# Test no duplicate calls
# Test caching works
# Test in-progress tracking works
```

---

#### 16. `tests/week2/test_expert_validation_enabled.py`
**Purpose:** Verify expert validation re-enabled  
**Expected:** PASS after Week 2 complete  
**Lines:** ~60  
**Dependencies:** pytest, python-dotenv

```python
# Test DEFAULT_USE_ASSISTANT_MODEL=true
# Test expert validation actually runs
# Test duration is 90-120s (not 300+)
```

---

### Regression Tests

#### 17. `tests/regression/test_simple_tools.sh`
**Purpose:** Ensure simple tools still work  
**Expected:** PASS always  
**Lines:** ~80  
**Dependencies:** timeout, python3

```bash
# Test listmodels (should complete in <10s)
# Test chat without web search (should complete in <35s)
# Test all simple tools still functional
```

---

#### 18. `tests/regression/test_api_integration.py`
**Purpose:** Ensure API integration still works  
**Expected:** PASS always  
**Lines:** ~100  
**Dependencies:** pytest, pytest-asyncio, requests

```python
# Test GLM API calls work
# Test Kimi API calls work
# Test streaming works
# Test error handling works
```

---

#### 19. `tests/regression/test_websocket_daemon.py`
**Purpose:** Ensure WebSocket daemon still works  
**Expected:** PASS always  
**Lines:** ~120  
**Dependencies:** pytest, pytest-asyncio, websockets

```python
# Test daemon starts correctly
# Test WebSocket connections work
# Test message routing works
# Test session management works
```

---

### Performance Tests

#### 20. `tests/performance/test_timeout_overhead.py`
**Purpose:** Verify TimeoutConfig has minimal overhead  
**Expected:** PASS (overhead < 0.1s for 1000 iterations)  
**Lines:** ~40  
**Dependencies:** pytest, pytest-asyncio

```python
# Test TimeoutConfig method call overhead
# Should complete 1000 iterations in < 0.1s
```

---

#### 21. `tests/performance/test_progress_overhead.py`
**Purpose:** Verify progress heartbeat has minimal overhead  
**Expected:** PASS (overhead < 5%)  
**Lines:** ~60  
**Dependencies:** pytest, pytest-asyncio

```python
# Test heartbeat overhead vs baseline
# Overhead should be < 5%
```

---

#### 22. `tests/performance/test_logging_overhead.py`
**Purpose:** Verify unified logging has minimal overhead  
**Expected:** PASS (overhead < 10%)  
**Lines:** ~60  
**Dependencies:** pytest, pytest-asyncio

```python
# Test logging overhead vs baseline
# Overhead should be < 10%
```

---

### Integration Tests (All 3 Clients)

#### 23. `tests/integration/test_vscode_augment.py`
**Purpose:** Test VSCode Augment extension integration  
**Expected:** PASS after all fixes  
**Lines:** ~100  
**Dependencies:** pytest, VSCode Augment extension

```python
# Test simple tools work in VSCode
# Test workflow tools work in VSCode
# Test timeouts work correctly
# Test progress updates visible
```

---

#### 24. `tests/integration/test_auggie_cli.py`
**Purpose:** Test Auggie CLI integration  
**Expected:** PASS after all fixes  
**Lines:** ~100  
**Dependencies:** pytest, Auggie CLI

```python
# Test simple tools work in Auggie
# Test workflow tools work in Auggie
# Test timeouts work correctly
# Test progress updates visible
```

---

#### 25. `tests/integration/test_claude_desktop.py`
**Purpose:** Test Claude Desktop integration  
**Expected:** PASS after all fixes  
**Lines:** ~100  
**Dependencies:** pytest, Claude Desktop

```python
# Test simple tools work in Claude
# Test workflow tools work in Claude
# Test timeouts work correctly
# Test progress updates visible
```

---

## 🔧 SCRIPTS TO MODIFY

### Existing Test Suite

#### 1. `tests/test_*.py` (if any exist)
**Modification:** Update to use TimeoutConfig instead of hardcoded timeouts  
**Estimated Changes:** 10-20 lines per file  
**Dependencies:** config.py

---

## ▶️ SCRIPTS TO EXECUTE

### Phase 1: Baseline (Before Implementation)

```bash
# Run all baseline tests
pytest tests/baseline/test_timeout_baseline.py -v
bash tests/baseline/test_workflow_timeout_baseline.sh
bash tests/baseline/test_logging_baseline.sh
pytest tests/baseline/test_progress_baseline.py -v
bash tests/baseline/test_expert_validation_baseline.sh

# Expected: Most tests FAIL (confirming problems exist)
```

---

### Phase 2: After Day 1-2 (Timeout Hierarchy)

```bash
# Run timeout hierarchy tests
pytest tests/week1/test_timeout_config.py -v
pytest tests/week1/test_daemon_timeout.py -v
pytest tests/week1/test_shim_timeout.py -v
pytest tests/week1/test_workflow_timeout_behavior.py -v
bash tests/week1/test_mcp_configs.sh

# Expected: All tests PASS
```

---

### Phase 3: After Day 3-4 (Progress Heartbeat)

```bash
# Run progress heartbeat tests
pytest tests/week1/test_progress_heartbeat.py -v
pytest tests/week1/test_progress_integration.py -v

# Expected: All tests PASS
```

---

### Phase 4: After Day 5 (Unified Logging)

```bash
# Run unified logging tests
pytest tests/week1/test_unified_logging.py -v
pytest tests/week1/test_logging_integration.py -v

# Expected: All tests PASS
```

---

### Phase 5: After Week 1 Complete

```bash
# Run all Week 1 tests
pytest tests/week1/ -v

# Run regression tests
bash tests/regression/test_simple_tools.sh
pytest tests/regression/test_api_integration.py -v
pytest tests/regression/test_websocket_daemon.py -v

# Run performance tests
pytest tests/performance/ -v

# Expected: All tests PASS
```

---

### Phase 6: After Week 2 Complete

```bash
# Run Week 2 tests
pytest tests/week2/ -v

# Run all regression tests again
pytest tests/regression/ -v

# Expected: All tests PASS
```

---

### Phase 7: Final Integration Testing

```bash
# Run integration tests for all 3 clients
pytest tests/integration/test_vscode_augment.py -v
pytest tests/integration/test_auggie_cli.py -v
pytest tests/integration/test_claude_desktop.py -v

# Expected: All tests PASS
```

---

## 📊 SUMMARY

**Total Scripts to CREATE:** 25
- Baseline: 5 scripts
- Week 1: 9 scripts
- Week 2: 2 scripts
- Regression: 3 scripts
- Performance: 3 scripts
- Integration: 3 scripts

**Total Scripts to MODIFY:** 1-5 (existing test suite, if any)

**Total Scripts to EXECUTE:** 7 phases
- Phase 1: Baseline (5 scripts)
- Phase 2: Day 1-2 (5 scripts)
- Phase 3: Day 3-4 (2 scripts)
- Phase 4: Day 5 (2 scripts)
- Phase 5: Week 1 Complete (all Week 1 + regression + performance)
- Phase 6: Week 2 Complete (Week 2 + regression)
- Phase 7: Final Integration (3 clients)

**Estimated Total Test Lines:** ~2,000 lines of test code

**Estimated Test Creation Time:** 2-3 days

**Estimated Test Execution Time:** 
- Baseline: 5 minutes
- Week 1: 15 minutes
- Week 2: 10 minutes
- Regression: 10 minutes
- Performance: 5 minutes
- Integration: 20 minutes
- **Total:** ~65 minutes per full test run

