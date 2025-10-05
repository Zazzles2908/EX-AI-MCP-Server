# 🧪 EX-AI MCP Server - Comprehensive Testing Strategy

**Date:** 2025-10-05  
**Version:** 2.0  
**Status:** Active

---

## 📋 OVERVIEW

The EX-AI MCP Server uses a **dual testing strategy** to ensure comprehensive validation of both the MCP protocol layer and the underlying provider APIs.

### Two Testing Systems

1. **MCP Integration Tests** (`tests/` directory)
   - Tests the complete MCP stack (protocol → server → tools → providers)
   - Uses pytest framework
   - 40+ existing test files

2. **Provider API Tests** (`tool_validation_suite/` directory)
   - Tests provider APIs directly (bypasses MCP layer)
   - Uses custom test runner with GLM Watcher
   - 70% complete (utilities done, test scripts needed)

---

## 🎯 WHEN TO USE EACH SYSTEM

### Use `tests/` (MCP Integration) When:

✅ Testing MCP protocol compliance  
✅ Testing server startup/shutdown  
✅ Testing tool registration and discovery  
✅ Testing WebSocket daemon + shim  
✅ Testing configuration loading  
✅ Testing routing logic  
✅ Testing end-to-end workflows through MCP  
✅ Testing both stdio and WebSocket modes  
✅ Testing concurrent client connections  

**Example:** "Does the chat tool work when called through MCP?"

### Use `tool_validation_suite/` (Provider API) When:

✅ Testing direct provider API integration  
✅ Testing feature activation (web search, file upload, thinking mode)  
✅ Testing conversation management and platform isolation  
✅ Testing cost tracking and limits  
✅ Benchmarking performance  
✅ Validating provider-specific behavior  
✅ Getting independent validation via GLM Watcher  

**Example:** "Does Kimi web search activate correctly with the right parameters?"

---

## 🏗️ ARCHITECTURE COMPARISON

### MCP Integration Tests (tests/)

```
┌─────────────────────────────────────────────────────────────┐
│                    FULL STACK TESTING                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Test Script (pytest)                                        │
│      ↓                                                        │
│  MCP Client (stdio or WebSocket)                             │
│      ↓                                                        │
│  server.py / ws_server.py                                    │
│      ↓                                                        │
│  MCP Handlers (handle_call_tool, etc.)                       │
│      ↓                                                        │
│  Tool Registry & Tool Execution                              │
│      ↓                                                        │
│  Provider APIs (Kimi/GLM)                                    │
│      ↓                                                        │
│  Response Validation                                         │
│                                                               │
│  ✅ Tests: Protocol, Server, Tools, Providers                │
│  ✅ Modes: stdio and WebSocket                               │
│  ✅ Framework: pytest                                        │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Provider API Tests (tool_validation_suite/)

```
┌─────────────────────────────────────────────────────────────┐
│                  PROVIDER API TESTING                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Test Script (custom)                                        │
│      ↓                                                        │
│  APIClient (utils/api_client.py)                             │
│      ↓                                                        │
│  Provider APIs (Kimi/GLM) - DIRECT                           │
│      ↓                                                        │
│  Response Validation                                         │
│      ↓                                                        │
│  GLM Watcher (Independent Validation)                        │
│      ↓                                                        │
│  Cost Tracking & Performance Monitoring                      │
│                                                               │
│  ✅ Tests: Provider APIs, Features, Cost, Performance        │
│  ✅ Validation: Independent GLM Watcher                      │
│  ✅ Framework: Custom TestRunner                             │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 COVERAGE MATRIX

### What Each System Tests

| Component | MCP Tests (tests/) | Provider Tests (tool_val) |
|-----------|-------------------|---------------------------|
| **MCP Protocol** | ✅ 80% | ❌ 0% (bypassed) |
| **Server Handlers** | ✅ 75% | ❌ 0% (bypassed) |
| **Tool Registration** | ✅ 70% | ❌ 0% (bypassed) |
| **WebSocket Daemon** | ✅ 60% | ❌ 0% (bypassed) |
| **Routing Logic** | ✅ 80% | ❌ 0% (bypassed) |
| **Configuration** | ✅ 85% | ❌ 0% (bypassed) |
| **Provider APIs** | ✅ 70% (through MCP) | ⏳ 0% (direct) |
| **Feature Activation** | ⚠️ 40% | ⏳ 0% (comprehensive) |
| **Cost Tracking** | ❌ 0% | ✅ 100% |
| **Performance** | ⚠️ 30% | ✅ 100% |
| **Platform Isolation** | ❌ 0% | ✅ 100% |
| **Independent Validation** | ❌ 0% | ✅ 100% (GLM Watcher) |

**Combined Coverage:** ~85% (when both systems complete)

---

## 🚀 RUNNING TESTS

### Run MCP Integration Tests

```bash
# All MCP tests
python run_tests.py --category all

# Specific categories
python run_tests.py --category mcp_protocol
python run_tests.py --category routing
python run_tests.py --category providers
python run_tests.py --category e2e

# With pytest directly
pytest tests/ -v
pytest tests/phase8/ -v
pytest tests/week3/ -v

# Specific markers
pytest -m integration
pytest -m e2e
pytest -m performance
```

### Run Provider API Tests

```bash
# All provider tests
cd tool_validation_suite
python scripts/run_all_tests.py

# Specific categories
python scripts/run_core_tests.py
python scripts/run_provider_tests.py --provider kimi
python scripts/run_provider_tests.py --provider glm

# Specific tool
python scripts/run_all_tests.py --tool chat
python scripts/run_all_tests.py --tool analyze
```

### Run Both Systems

```bash
# Unified test runner (to be created)
python run_all_tests_unified.py

# Or run separately
python run_tests.py --category all
cd tool_validation_suite && python scripts/run_all_tests.py
```

---

## 📁 DIRECTORY STRUCTURE

```
EX-AI-MCP-Server/
├── tests/                          # MCP Integration Tests
│   ├── phase2/                     # Phase 2 tests
│   ├── phase3/                     # Phase 3 tests
│   ├── phase4/                     # Phase 4 tests
│   ├── phase5/                     # Phase 5 tests
│   ├── phase6/                     # Phase 6 tests
│   ├── phase7/                     # Phase 7 tests
│   ├── phase8/                     # Phase 8 tests
│   ├── week1/                      # Week 1 tests
│   ├── week2/                      # Week 2 tests
│   ├── week3/                      # Week 3 tests
│   └── docs/                       # Documentation tests
│
├── tool_validation_suite/          # Provider API Tests
│   ├── config/                     # Test configuration
│   ├── scripts/                    # Test runners
│   ├── utils/                      # Test utilities (11 modules)
│   ├── tests/                      # Test scripts (to be created)
│   │   ├── core_tools/            # 15 core tool tests
│   │   ├── advanced_tools/        # 7 advanced tool tests
│   │   ├── provider_tools/        # 8 provider tool tests
│   │   └── integration/           # 6 integration tests
│   └── results/                    # Test results and reports
│
├── pytest.ini                      # pytest configuration
├── run_tests.py                    # MCP test runner
└── TESTING_STRATEGY.md            # This file
```

---

## 🔧 TEST DEVELOPMENT GUIDELINES

### For MCP Integration Tests (tests/)

1. **Use pytest framework**
   ```python
   import pytest
   
   @pytest.mark.integration
   async def test_chat_through_mcp():
       from tools.chat import ChatTool
       tool = ChatTool()
       # Test through MCP protocol
   ```

2. **Test both execution modes**
   - stdio mode (direct server.py)
   - WebSocket mode (daemon + shim)

3. **Use appropriate markers**
   - `@pytest.mark.unit` - Unit tests
   - `@pytest.mark.integration` - Integration tests
   - `@pytest.mark.e2e` - End-to-end tests
   - `@pytest.mark.performance` - Performance tests

4. **Follow existing patterns**
   - Look at tests/phase8/ for examples
   - Use monkeypatch for environment variables
   - Mock external dependencies when appropriate

### For Provider API Tests (tool_validation_suite/)

1. **Use TestRunner framework**
   ```python
   from utils import TestRunner
   
   def test_chat_basic(api_client, **kwargs):
       return api_client.call_kimi(
           model="kimi-k2-0905-preview",
           messages=[{"role": "user", "content": "test"}],
           tool_name="chat",
           variation="basic_functionality"
       )
   ```

2. **Test all 12 variations**
   - basic_functionality
   - edge_cases
   - error_handling
   - file_handling
   - model_selection
   - continuation
   - timeout_handling
   - progress_reporting
   - web_search
   - file_upload
   - conversation_id_persistence
   - conversation_id_isolation

3. **Use real API calls**
   - No mocks (tests actual provider behavior)
   - Track costs with PromptCounter
   - Monitor performance with PerformanceMonitor

4. **Leverage GLM Watcher**
   - Independent validation of test results
   - Quality scores and suggestions
   - Anomaly detection

---

## 📈 SUCCESS CRITERIA

### MCP Integration Tests

✅ 90%+ pass rate  
✅ All tools discoverable via MCP  
✅ Both stdio and WebSocket modes work  
✅ No protocol violations  
✅ Configuration loads correctly  
✅ Routing logic works as expected  

### Provider API Tests

✅ 90%+ pass rate  
✅ All 30 tools tested with 12 variations  
✅ Cost under $5 for full suite  
✅ GLM Watcher observations collected  
✅ Performance metrics within thresholds  
✅ Platform isolation verified  

### Combined

✅ 85%+ overall system coverage  
✅ Both daemon and MCP modes validated  
✅ No critical bugs detected  
✅ All reports generated successfully  

---

## 🐛 DEBUGGING FAILED TESTS

### MCP Integration Test Failures

1. **Check server logs**
   ```bash
   tail -f logs/server.log
   tail -f logs/toolcalls.jsonl
   ```

2. **Verify configuration**
   ```bash
   python scripts/diagnose_mcp.py
   ```

3. **Test WebSocket daemon**
   ```bash
   python scripts/ws/ws_status.py
   python scripts/ws/ws_chat_once.py kimi-k2-0905-preview "test"
   ```

4. **Run specific test with verbose output**
   ```bash
   pytest tests/phase8/test_workflows_end_to_end.py -v --tb=long
   ```

### Provider API Test Failures

1. **Check API keys**
   ```bash
   cd tool_validation_suite
   python scripts/validate_setup.py
   ```

2. **Review test logs**
   ```bash
   cat tool_validation_suite/results/latest/test_logs/*.log
   ```

3. **Check GLM Watcher observations**
   ```bash
   cat tool_validation_suite/results/latest/watcher_observations/*.json
   ```

4. **Review cost tracking**
   ```bash
   cat tool_validation_suite/results/latest/cost_summary.json
   ```

---

## 📚 RELATED DOCUMENTATION

**MCP Integration Tests:**
- `tests/` directory - Existing test files
- `pytest.ini` - pytest configuration
- `run_tests.py` - Test runner

**Provider API Tests:**
- `tool_validation_suite/NEXT_AGENT_HANDOFF.md` - Complete context
- `tool_validation_suite/ARCHITECTURE.md` - System design
- `tool_validation_suite/TESTING_GUIDE.md` - How to run tests
- `tool_validation_suite/CORRECTED_AUDIT_FINDINGS.md` - Audit results

**General:**
- `TESTING_STRATEGY.md` - This file
- `docs/reviews/augment_code_review/03_testing/` - Testing documentation

---

## ✅ NEXT STEPS

1. **Complete tool_validation_suite test scripts** (4-6 hours)
2. **Integrate both testing systems** (1-2 hours)
3. **Run full test suite** (1-2 hours)
4. **Analyze results and fix issues** (2-3 hours)
5. **Document findings** (1 hour)

**Total Time:** 9-14 hours

---

**Testing Strategy Active** ✅  
**Last Updated:** 2025-10-05  
**Maintained By:** EX-AI MCP Server Team

