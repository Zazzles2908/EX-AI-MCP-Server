# IMPLEMENTATION PLAN - Phase-by-Phase Guide

**Date:** 2025-10-04  
**Total Duration:** 3 weeks (19-26 days)  
**Approach:** Incremental, testable, documented

---

## 🎯 Implementation Philosophy

1. **Safety First:** Never break working functionality
2. **Incremental:** One fix at a time with validation
3. **Testable:** Every fix must have acceptance criteria
4. **Documented:** Update docs as we go, not at the end
5. **Autonomous:** Work through all tasks systematically
6. **Environment Hygiene:** ⚠️ **ALWAYS update BOTH .env and .env.example files** - Never update just .env.example alone

---

## 📅 WEEK 1: P0 Critical Fixes (Days 1-5)

**Goal:** Make workflow tools functional again

### Day 1-2: Fix #1 - Timeout Hierarchy Coordination

**Objective:** Implement coordinated timeout hierarchy to prevent hanging

**Tasks:**
1. [ ] Create `config.py` TimeoutConfig class
   - Define tool timeouts (60s simple, 120s workflow, 90s expert)
   - Auto-calculate infrastructure timeouts (daemon 180s, shim 240s, client 300s)
   - Add hierarchy validation on import
   
2. [ ] Update `src/daemon/ws_server.py`
   - Change CALL_TIMEOUT to use TimeoutConfig.get_daemon_timeout()
   - Import TimeoutConfig
   
3. [ ] Update `scripts/run_ws_shim.py`
   - Change RPC_TIMEOUT to use TimeoutConfig.get_shim_timeout()
   - Import TimeoutConfig
   
4. [ ] Update `tools/workflow/base.py`
   - Add timeout parameter to execute method
   - Implement asyncio.wait_for with timeout
   - Add graceful timeout handling with partial results
   
5. [ ] Update `tools/workflows/thinkdeep.py`
   - Change get_expert_timeout_secs to use TimeoutConfig
   - Remove hardcoded timeout values
   
6. [ ] Update all MCP configs
   - `Daemon/mcp-config.auggie.json`
   - `Daemon/mcp-config.augmentcode.json`
   - `Daemon/mcp-config.claude.json`
   - Replace 600s+ timeouts with coordinated values
   
7. [ ] Update `.env.example`
   - Add timeout configuration section
   - Document timeout hierarchy
   - Explain auto-calculation

**Testing:**
```bash
# Validate timeout hierarchy
python3 -c "from config import TimeoutConfig; TimeoutConfig.validate_hierarchy()"

# Test workflow tool timeout
# Should timeout at 120s, not 600s
```

**Acceptance Criteria:**
- [ ] TimeoutConfig validates hierarchy on import
- [ ] All timeouts coordinated (tool < daemon < shim < client)
- [ ] Workflow tools timeout at 120s
- [ ] Expert validation timeouts at 90s
- [ ] All three MCP configs updated

**Estimated Time:** 2 days

---

### Day 3-4: Fix #2 - Progress Heartbeat Implementation

**Objective:** Provide continuous feedback during long operations

**Tasks:**
1. [ ] Create `utils/progress.py`
   - ProgressHeartbeat class (6s interval)
   - ProgressTracker class (global tracker)
   - Async context manager support
   - Callback support for WebSocket routing
   
2. [ ] Update `tools/workflow/base.py`
   - Integrate ProgressHeartbeat in execute method
   - Set total steps and current step
   - Send heartbeat before/after each step
   - Include elapsed time and estimated remaining
   
3. [ ] Update `tools/workflow/expert_analysis.py`
   - Add heartbeat during expert validation
   - Show which expert is being consulted
   - Show progress through validation steps
   
4. [ ] Update `src/providers/openai_compatible.py`
   - Add heartbeat during long API calls
   - Show streaming progress
   - Show retry attempts
   
5. [ ] Update `src/daemon/ws_server.py`
   - Add send_progress_update method
   - Route progress messages to clients
   - Handle WebSocket send failures gracefully
   
6. [ ] Update `scripts/run_ws_shim.py`
   - Add handle_progress_message method
   - Log progress messages
   - Optionally forward to MCP client

**Testing:**
```python
# Test heartbeat timing
import asyncio
from utils.progress import ProgressHeartbeat

async def test():
    messages = []
    async def callback(data):
        messages.append(data)
    
    async with ProgressHeartbeat(interval_secs=2.0, callback=callback) as hb:
        for i in range(10):
            await hb.send_heartbeat(f"Step {i}")
            await asyncio.sleep(1)
    
    # Should have ~5 messages (10 seconds / 2 second interval)
    assert 4 <= len(messages) <= 6

asyncio.run(test())
```

**Acceptance Criteria:**
- [ ] ProgressHeartbeat sends updates at configured interval
- [ ] Workflow tools send progress every 6 seconds
- [ ] Expert validation sends progress every 8 seconds
- [ ] Provider calls send progress every 5 seconds
- [ ] Progress includes elapsed time and estimated remaining
- [ ] WebSocket server routes progress to clients
- [ ] No performance degradation

**Estimated Time:** 2 days

---

### Day 5: Fix #3 - Logging Infrastructure Unification

**Objective:** Ensure all tools log execution correctly

**Tasks:**
1. [ ] Create `utils/logging_unified.py`
   - UnifiedLogger class with structured logging
   - Methods: log_tool_start, log_tool_progress, log_tool_complete, log_tool_error
   - Methods: log_expert_validation_start, log_expert_validation_complete
   - Buffered writes for performance
   - Automatic log rotation
   
2. [ ] Update `tools/simple/base.py`
   - Replace existing logging with unified logger
   - Add request_id tracking
   - Log start, progress, complete, error
   
3. [ ] Update `tools/workflow/base.py`
   - Add unified logger integration
   - Log all execution steps
   - Log expert validation
   - Log progress updates
   
4. [ ] Update `tools/workflow/expert_analysis.py`
   - Log expert validation start/complete
   - Log each expert consulted
   - Log validation results
   
5. [ ] Update `src/daemon/ws_server.py`
   - Add request ID generation
   - Track request IDs throughout execution

**Testing:**
```bash
# Test simple tool logging
# Run chat tool and verify log entry in .logs/toolcalls.jsonl

# Test workflow tool logging
# Run thinkdeep tool and verify all steps logged

# Verify log format
tail -f .logs/toolcalls.jsonl | jq .
```

**Acceptance Criteria:**
- [ ] UnifiedLogger created with structured logging
- [ ] Simple tools use unified logger
- [ ] Workflow tools use unified logger
- [ ] Expert validation logged correctly
- [ ] All executions appear in .logs/toolcalls.jsonl
- [ ] Request IDs tracked throughout
- [ ] Errors logged with full traceback

**Estimated Time:** 1 day

---

## 📅 WEEK 2: P1 High Priority Fixes (Days 6-10)

**Goal:** Restore full functionality and standardize configuration

### Day 6-8: Fix #4 - Expert Validation Duplicate Call Bug

**Objective:** Debug and fix duplicate call issue, re-enable expert validation

**Tasks:**
1. [ ] Add detailed logging to `tools/workflow/expert_analysis.py`
   - Track each call to expert validation
   - Log call stack to identify caller
   - Log request_id and content hash
   
2. [ ] Trace execution path
   - Identify where duplicate calls originate
   - Check for recursive calls
   - Check for event-driven triggers
   
3. [ ] Implement call deduplication
   - Add validation cache by request_id + content hash
   - Track in-progress validations
   - Prevent duplicate calls with lock mechanism
   
4. [ ] Add circuit breaker
   - Track validation failures
   - Open circuit after 5 failures
   - Auto-reset after 5 minutes
   
5. [ ] Re-enable expert validation
   - Change DEFAULT_USE_ASSISTANT_MODEL=true in .env
   - Test with debug tool (2-step workflow)
   - Verify expert_analysis contains real content
   - Verify duration is 90-120s (not 300+)

**Testing:**
```bash
# Test expert validation
# Run debug tool with 2 steps
# Verify expert validation called exactly once per step
# Verify duration is 90-120 seconds
# Verify expert_analysis is not null
```

**Acceptance Criteria:**
- [ ] Expert analysis called exactly once per step
- [ ] Call deduplication implemented
- [ ] Circuit breaker prevents runaway calls
- [ ] Expert validation re-enabled
- [ ] Duration is 90-120 seconds (not 300+)
- [ ] Expert_analysis contains real content

**Estimated Time:** 3 days

---

### Day 9-10: Fix #5 - Configuration Standardization

**Objective:** Standardize timeout configurations across all clients

**Tasks:**
1. [ ] Create base configuration template
   - Define standard timeout values
   - Define standard concurrency limits
   - Document configuration schema
   
2. [ ] Update `Daemon/mcp-config.auggie.json`
   - Use standard timeout values
   - Document Auggie-specific overrides
   - Add validation comments
   
3. [ ] Update `Daemon/mcp-config.augmentcode.json`
   - Use standard timeout values
   - Document VSCode-specific overrides
   - Add validation comments
   
4. [ ] Update `Daemon/mcp-config.claude.json`
   - Use standard timeout values
   - Document Claude-specific overrides
   - Add validation comments
   
5. [ ] Add configuration validation
   - Validate timeout hierarchy
   - Validate concurrency limits
   - Warn on invalid values
   
6. [ ] Test all three clients
   - VSCode Augment extension
   - Auggie CLI
   - Claude Desktop

**Testing:**
```bash
# Test each client with standardized config
# Verify consistent behavior across clients
# Verify timeout values are correct
```

**Acceptance Criteria:**
- [ ] Base configuration template created
- [ ] All three configs standardized
- [ ] Differences documented
- [ ] Configuration validation implemented
- [ ] All three clients tested

**Estimated Time:** 2 days

---

## 📅 WEEK 3: P2 Enhancements (Days 11-15)

**Goal:** Complete web search integration and polish system

### Day 11-12: Fix #6 - Web Search Verification

**Objective:** Verify web search works and add logging/tests

**Tasks:**
1. [ ] Add web search activation logging
   - Log when GLM web search is triggered
   - Log when Kimi web search is triggered
   - Log web search results
   
2. [ ] Create web search tests
   - Test GLM native web search
   - Test Kimi $web_search builtin
   - Test web search auto-injection
   - Test web search results parsing
   
3. [ ] Document web search flow
   - Update architecture docs
   - Document GLM web search integration
   - Document Kimi web search integration
   
4. [ ] Add web search metrics
   - Track web search usage
   - Track web search success rate
   - Track web search latency

**Testing:**
```bash
# Test GLM web search
chat_exai(prompt="Latest AI news?", use_websearch=true)

# Test Kimi web search
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

**Estimated Time:** 2 days

---

### Day 13-14: Fix #7 - Simplify Continuation System

**Objective:** Make continuation_id optional and simplify response format

**Tasks:**
1. [ ] Update `tools/simple/base.py`
   - Make continuation_id optional based on request parameter
   - Move metadata to separate response field
   - Simplify response format for single-turn operations
   
2. [ ] Update `tools/simple/mixins/continuation_mixin.py`
   - Only include continuation_offer when conversation mode active
   - Add request parameter to control continuation behavior
   
3. [ ] Update `scripts/run_ws_shim.py`
   - Clean response format
   - Remove unnecessary metadata from content
   
4. [ ] Test continuation system
   - Test single-turn operations (no continuation)
   - Test multi-turn conversations (with continuation)
   - Verify response format is clean

**Acceptance Criteria:**
- [ ] Continuation_id optional based on request
- [ ] Metadata in separate field
- [ ] Continuation offer only when needed
- [ ] Simplified response format

**Estimated Time:** 2 days

---

### Day 15: Documentation Update & Final Testing

**Objective:** Update all documentation and run final tests

**Tasks:**
1. [ ] Update architecture documentation
   - Document timeout hierarchy
   - Document progress heartbeat system
   - Document unified logging
   - Document web search integration
   
2. [ ] Update configuration documentation
   - Document timeout configuration
   - Document MCP configurations
   - Document environment variables
   
3. [ ] Create troubleshooting guide
   - Common issues and solutions
   - Debugging workflow tools
   - Timeout troubleshooting
   
4. [ ] Run comprehensive tests
   - Test all simple tools
   - Test all workflow tools
   - Test all three clients
   - Verify all fixes working

**Acceptance Criteria:**
- [ ] All documentation updated
- [ ] Troubleshooting guide created
- [ ] All tests passing
- [ ] System production-ready

**Estimated Time:** 1 day

---

## 📊 Progress Tracking

**Week 1 Progress:**
- [ ] Day 1-2: Timeout hierarchy ✅
- [ ] Day 3-4: Progress heartbeat ✅
- [ ] Day 5: Unified logging ✅

**Week 2 Progress:**
- [ ] Day 6-8: Expert validation fix ✅
- [ ] Day 9-10: Config standardization ✅

**Week 3 Progress:**
- [ ] Day 11-12: Web search verification ✅
- [ ] Day 13-14: Continuation simplification ✅
- [ ] Day 15: Documentation & testing ✅

**Overall Progress:** 0/15 days complete (0%)

---

## 📅 POST-IMPLEMENTATION: Cleanup & Optimization

**Goal:** Organizational improvements and technical debt cleanup

**When to Execute:** After Week 3 (all P0/P1/P2 fixes complete)

### Task: Script Consolidation (P3)

**Objective:** Consolidate scattered scripts into organized structure

**Priority:** P3 (Nice-to-have, organizational improvement)
**Risk:** 🔴 HIGH (breaks MCP client configurations)
**Effort:** 2-3 hours
**Status:** 🟡 DEFERRED

**Tasks:**
1. [ ] Create organized directory structure
   - `scripts/setup/` - Setup and installation scripts
   - `scripts/daemon/` - Daemon management scripts
   - `scripts/client/` - Client wrappers and shims
   - `scripts/testing/` - Test scripts

2. [ ] Move scripts to appropriate categories
   - Move `run-server.ps1/.sh` to `scripts/setup/`
   - Move `ws_start.ps1` to `scripts/daemon/start.ps1`
   - Move `ws_stop.ps1` to `scripts/daemon/stop.ps1`
   - Move `force_restart.ps1` to `scripts/daemon/restart.ps1`
   - Move `run_ws_daemon.py` to `scripts/daemon/run_daemon.py`
   - Move `ws_status.py` to `scripts/daemon/status.py`
   - Move `mcp_server_wrapper.py` to `scripts/client/mcp_wrapper.py`
   - Move `run_ws_shim.py` to `scripts/client/ws_shim.py`
   - Move `ws_chat_*.py` to `scripts/testing/`

3. [ ] Update all references
   - Update `Daemon/mcp-config.auggie.json` (script path)
   - Update `Daemon/mcp-config.augmentcode.json` (script path)
   - Update `Daemon/mcp-config.claude.json` (script path)
   - Update `scripts/client/ws_shim.py` (daemon path reference)
   - Update `scripts/daemon/start.ps1` (script paths)
   - Update `scripts/daemon/restart.ps1` (script paths)
   - Update documentation (SERVER_ARCHITECTURE_MAP.md, SCRIPT_INTERCONNECTIONS.md)

4. [ ] Create README.md for each category
   - `scripts/setup/README.md` - Setup guide
   - `scripts/daemon/README.md` - Daemon management guide
   - `scripts/client/README.md` - Client integration guide
   - `scripts/testing/README.md` - Testing guide

5. [ ] Test thoroughly
   - Test daemon management (start, stop, restart, status)
   - Test all 3 MCP client connections (Auggie, Augment Code, Claude)
   - Test WebSocket shim
   - Test testing scripts
   - Verify no broken references (grep confirms)

**Acceptance Criteria:**
- [ ] All scripts organized into clear categories
- [ ] All references updated (no broken paths)
- [ ] All 3 MCP clients can connect successfully
- [ ] Daemon management scripts work
- [ ] Documentation updated with new paths
- [ ] No broken references

**Testing:**
```powershell
# Test daemon management
.\scripts\daemon\start.ps1
python scripts\daemon\status.py
.\scripts\daemon\stop.ps1
.\scripts\daemon\restart.ps1

# Test MCP clients
# (Connect with Auggie, Augment Code, Claude)

# Test WebSocket shim
.\scripts\daemon\start.ps1 -Shim
python scripts\testing\ws_chat_once.py
```

**Estimated Time:** 2-3 hours

**⚠️ Risk:** HIGH - Breaks MCP client configurations if not done carefully

**📋 Detailed Plan:** See `SCRIPT_CONSOLIDATION_PLAN.md`

---

### Task: WebSocket Deprecation Fix (P3)

**Objective:** Fix deprecated websockets library import

**Priority:** P3 (Low urgency, but should fix soon)
**Risk:** 🟢 LOW
**Effort:** 5 minutes
**Status:** ✅ TO BE COMPLETED BEFORE DAY 3

**Tasks:**
1. [ ] Update `src/daemon/ws_server.py` (line 14)
   - Remove deprecated import: `from websockets.server import WebSocketServerProtocol`
   - Update type hints to use new API or generic types

2. [ ] Test WebSocket daemon
   - Start daemon: `.\scripts\ws_start.ps1`
   - Check status: `python scripts\ws\ws_status.py`
   - Test connection: `python scripts\ws\ws_chat_once.py`
   - Stop daemon: `.\scripts\ws_stop.ps1`

**Acceptance Criteria:**
- [ ] No deprecation warnings in test output
- [ ] WebSocket daemon starts successfully
- [ ] WebSocket connections work
- [ ] All tests pass

**Estimated Time:** 5 minutes

---

