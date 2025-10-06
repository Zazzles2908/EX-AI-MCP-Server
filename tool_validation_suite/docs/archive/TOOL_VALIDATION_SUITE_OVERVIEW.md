# 🧪 Tool Validation Suite

**Version:** 2.0  
**Status:** ✅ Ready for Test Implementation  
**Last Updated:** 2025-10-05

---

## 📋 OVERVIEW

The Tool Validation Suite is a comprehensive testing framework for validating **provider API integration** in the EX-AI MCP Server. It tests Kimi and GLM APIs directly, focusing on feature activation, cost tracking, performance monitoring, and independent validation.

### Purpose

This suite **complements** the existing MCP integration tests (`tests/` directory) by:
- Testing provider APIs directly (bypassing MCP layer)
- Validating feature activation (web search, file upload, thinking mode)
- Tracking costs and monitoring performance
- Providing independent validation via GLM Watcher
- Testing platform isolation (Kimi vs GLM conversation IDs)

### What This Suite Does NOT Test

❌ MCP protocol compliance (tested in `tests/`)  
❌ Server startup/shutdown (tested in `tests/`)  
❌ Tool registration (tested in `tests/`)  
❌ WebSocket daemon (tested in `tests/`)  
❌ Routing logic (tested in `tests/`)

**For MCP integration testing, see:** `tests/` directory and `run_tests.py`

---

## 🏗️ ARCHITECTURE

### Directory Structure

```
tool_validation_suite/
├── README.md                    # This file
├── NEXT_AGENT_HANDOFF.md       # Project context and handoff
├── TOOL_VALIDATION_SUITE_README.md  # Original README
│
├── docs/                        # Documentation
│   ├── current/                # Current, accurate documentation
│   │   ├── CORRECTED_AUDIT_FINDINGS.md      ⭐ Start here!
│   │   ├── AGENT_RESPONSE_SUMMARY.md        ⭐ Quick overview
│   │   ├── FINAL_RECOMMENDATION.md          ⭐ Implementation plan
│   │   ├── ARCHITECTURE.md                  📐 System design
│   │   ├── TESTING_GUIDE.md                 📖 How to run tests
│   │   ├── UTILITIES_COMPLETE.md            🔧 Utilities reference
│   │   └── SETUP_GUIDE.md                   ⚙️ Setup instructions
│   │
│   └── archive/                # Superseded documents
│       ├── HIGH_LEVEL_AUDIT_ANALYSIS.md     (incorrect - pre-discovery)
│       ├── TECHNICAL_AUDIT_FINDINGS.md      (incorrect - pre-discovery)
│       ├── AUDIT_SUMMARY_AND_RECOMMENDATIONS.md  (incorrect)
│       ├── AUDIT_VISUAL_SUMMARY.md          (incorrect)
│       ├── IMMEDIATE_ACTION_PLAN.md         (incorrect)
│       ├── AUDIT_REPORT.md                  (superseded)
│       ├── AUDIT_FIXES_COMPLETE.md          (superseded)
│       ├── PROGRESS_UPDATE.md               (superseded)
│       └── IMPLEMENTATION_STATUS.md         (superseded)
│
├── config/                      # Configuration files
│   ├── test_config.json        # Test configuration ✅ Fixed
│   └── pricing_and_models.json # Pricing and model info
│
├── scripts/                     # Test runners and utilities
│   ├── validate_setup.py       # Verify environment
│   ├── run_all_tests.py        # Run all 360 tests
│   ├── run_core_tests.py       # Run core tool tests
│   ├── run_provider_tests.py   # Run provider-specific tests
│   ├── generate_report.py      # Generate reports
│   └── cleanup_results.py      # Manage result history
│
├── utils/                       # Test utilities (11 modules)
│   ├── __init__.py
│   ├── api_client.py           # Unified Kimi/GLM API client
│   ├── conversation_tracker.py # Platform-isolated conversation management
│   ├── file_uploader.py        # File upload to both providers
│   ├── glm_watcher.py          # Independent validation observer
│   ├── performance_monitor.py  # CPU/memory/response time tracking
│   ├── prompt_counter.py       # Feature tracking and cost calculation
│   ├── response_validator.py   # Response quality validation
│   ├── result_collector.py     # Result aggregation
│   ├── test_runner.py          # Test orchestration
│   └── report_generator.py     # Comprehensive reports
│
├── tests/                       # Test scripts (36 to be created)
│   ├── core_tools/             # 15 core tool tests
│   ├── advanced_tools/         # 7 advanced tool tests
│   ├── provider_tools/         # 8 provider tool tests
│   └── integration/            # 6 integration tests
│
└── results/                     # Test results (auto-generated)
    └── latest/                 # Latest test run
        ├── reports/            # Test reports
        ├── test_logs/          # Individual test logs
        ├── watcher_observations/  # GLM Watcher observations
        └── cost_summary.json   # Cost tracking
```

---

## 🚀 QUICK START

### 1. Read Documentation (30 minutes)

**Start with these in order:**

1. **`docs/current/CORRECTED_AUDIT_FINDINGS.md`** (10 min)
   - Accurate audit findings
   - Discovery of existing MCP tests
   - Coverage analysis

2. **`docs/current/AGENT_RESPONSE_SUMMARY.md`** (5 min)
   - Quick overview
   - Answers to key questions
   - What's been done

3. **`docs/current/FINAL_RECOMMENDATION.md`** (10 min)
   - Implementation plan
   - Success criteria
   - Next steps

4. **`docs/current/TESTING_GUIDE.md`** (5 min)
   - How to run tests
   - How to interpret results

### 2. Verify Setup (5 minutes)

```bash
cd tool_validation_suite
python scripts/validate_setup.py
```

### 3. Create Test Scripts (4-6 hours)

See **Implementation Plan** below.

### 4. Run Tests (1-2 hours)

```bash
python scripts/run_all_tests.py
```

---

## 📊 CURRENT STATUS

### ✅ Complete (70%)

- [x] 11 utility modules
- [x] 6 helper scripts
- [x] Configuration files
- [x] Documentation
- [x] Directory structure
- [x] Model names fixed

### ⏳ In Progress (30%)

- [ ] 36 test scripts (0% complete)
  - [ ] 15 core tool tests
  - [ ] 7 advanced tool tests
  - [ ] 8 provider tool tests
  - [ ] 6 integration tests

---

## 🎯 IMPLEMENTATION PLAN

### Phase 1: Simple Tools (1-2 hours)

Create tests for simple tools to validate the approach:

1. **`tests/core_tools/test_chat.py`** (30 min)
2. **`tests/advanced_tools/test_status.py`** (15 min)
3. **`tests/advanced_tools/test_version.py`** (15 min)

**Run and validate:**
```bash
python scripts/run_all_tests.py --tool chat
python scripts/run_all_tests.py --tool status
```

### Phase 2: Core Tools (3-4 hours)

Create tests for remaining core tools:

4. **`tests/core_tools/test_analyze.py`** (45 min)
5. **`tests/core_tools/test_debug.py`** (45 min)
6. **`tests/core_tools/test_codereview.py`** (45 min)
7-16. Remaining core tools (30-45 min each)

### Phase 3: Provider Tools (2-3 hours)

Create tests for provider-specific tools:

17. **`tests/provider_tools/test_kimi_upload_and_extract.py`** (60 min)
18. **`tests/provider_tools/test_glm_web_search.py`** (60 min)
19-24. Remaining provider tools (45-60 min each)

### Phase 4: Integration Tests (1-2 hours)

Create integration tests:

25. **`tests/integration/test_conversation_id_kimi.py`** (45 min)
26. **`tests/integration/test_conversation_id_glm.py`** (45 min)
27-30. Remaining integration tests (30-45 min each)

### Phase 5: Advanced Tools (1-2 hours)

Create tests for advanced tools:

31-36. Advanced tools (15-30 min each)

**Total Time:** 8-13 hours

---

## 🔧 TEST SCRIPT TEMPLATE

Each test script should test **12 variations**:

1. basic_functionality
2. edge_cases
3. error_handling
4. file_handling
5. model_selection
6. continuation
7. timeout_handling
8. progress_reporting
9. web_search
10. file_upload
11. conversation_id_persistence
12. conversation_id_isolation

**See:** `docs/archive/IMMEDIATE_ACTION_PLAN.md` for detailed template

---

## 📈 SUCCESS CRITERIA

### Test Execution

✅ 90%+ pass rate  
✅ All 30 tools tested with 12 variations  
✅ Cost under $5 for full suite  
✅ GLM Watcher observations collected  
✅ Performance metrics within thresholds  
✅ Platform isolation verified  

### Coverage

✅ Provider API direct testing: 90%  
✅ Feature activation: 85%  
✅ Cost tracking: 100%  
✅ Performance monitoring: 100%  
✅ Platform isolation: 100%  

### Combined with MCP Tests

✅ 85%+ overall system coverage  
✅ Both daemon and MCP modes validated  
✅ No critical bugs detected  

---

## 💰 COST TRACKING

### Limits

- **Per-test limit:** $0.50
- **Total limit:** $10.00
- **Alert threshold:** $5.00

### Expected Costs

- **Full suite (360 tests):** $2-5 USD
- **Core tools only (180 tests):** $1-2 USD
- **Single tool (12 tests):** $0.05-0.10 USD

### Cost Monitoring

All costs are tracked in real-time by `PromptCounter` utility and reported in:
- `results/latest/cost_summary.json`
- `results/latest/reports/VALIDATION_REPORT.md`

---

## 🔍 INDEPENDENT VALIDATION

### GLM Watcher

Every test execution is observed by **GLM Watcher**, an independent validation system that:

- Uses separate GLM API key (FREE tier: glm-4.5-flash)
- Analyzes test inputs and outputs
- Provides quality scores (0-100)
- Suggests improvements
- Detects anomalies

**Observations saved to:** `results/latest/watcher_observations/`

---

## 📚 RELATED DOCUMENTATION

### In This Suite

- **`NEXT_AGENT_HANDOFF.md`** - Original project context
- **`docs/current/CORRECTED_AUDIT_FINDINGS.md`** - Audit results
- **`docs/current/ARCHITECTURE.md`** - System design
- **`docs/current/TESTING_GUIDE.md`** - How to run tests
- **`docs/current/UTILITIES_COMPLETE.md`** - Utilities reference

### In Project Root

- **`TESTING_STRATEGY.md`** - Dual testing approach
- **`tests/`** - MCP integration tests
- **`run_tests.py`** - MCP test runner
- **`pytest.ini`** - pytest configuration

---

## 🐛 TROUBLESHOOTING

### Setup Issues

```bash
# Verify environment
python scripts/validate_setup.py

# Check API keys
echo $MOONSHOT_API_KEY
echo $ZHIPUAI_API_KEY
```

### Test Failures

```bash
# Review test logs
cat results/latest/test_logs/<tool_name>_<variation>.log

# Check GLM Watcher observations
cat results/latest/watcher_observations/<tool_name>_<variation>.json

# Review cost summary
cat results/latest/cost_summary.json
```

### Cost Overruns

- Check `results/latest/cost_summary.json`
- Adjust limits in `config/test_config.json`
- Use `--tool` flag to test specific tools only

---

## 📞 SUPPORT

### Documentation

- Start with `docs/current/CORRECTED_AUDIT_FINDINGS.md`
- Read `docs/current/TESTING_GUIDE.md`
- Check `docs/current/UTILITIES_COMPLETE.md`

### Issues

- Review test logs in `results/latest/test_logs/`
- Check GLM Watcher observations
- Verify API keys and configuration

---

## ✅ NEXT STEPS

1. **Read documentation** (30 minutes)
   - CORRECTED_AUDIT_FINDINGS.md
   - AGENT_RESPONSE_SUMMARY.md
   - FINAL_RECOMMENDATION.md

2. **Verify setup** (5 minutes)
   ```bash
   python scripts/validate_setup.py
   ```

3. **Create test scripts** (8-13 hours)
   - Start with simple tools
   - Validate approach
   - Create remaining tests

4. **Run full suite** (1-2 hours)
   ```bash
   python scripts/run_all_tests.py
   ```

5. **Analyze results** (1 hour)
   - Review reports
   - Check GLM Watcher observations
   - Verify cost tracking

**Total Time:** 10-16 hours  
**Expected Cost:** $2-5 USD

---

**Tool Validation Suite** ✅  
**Ready for Implementation** 🚀  
**Last Updated:** 2025-10-05

