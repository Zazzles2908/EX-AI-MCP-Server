# 🧪 Tool Validation Suite - Complete System Testing Ground

**🎯 Independent Testing Environment for EX-AI MCP Server**
**📊 Real API Calls | 🔍 GLM Watcher Observer | 💰 Cost Tracking | 📈 Prompt Counter**

**Created:** 2025-10-05  
**Purpose:** Independent, comprehensive validation of all 30 EX-AI MCP Server tools  
**Status:** 🟢 READY FOR TESTING  
**Test Coverage:** 30 tools × 12 variations = 360 test scenarios

---

## 🎯 WHAT IS THIS?

This is a **completely independent testing ground** for validating all tools in the EX-AI MCP Server. It is designed to:

1. **Test every tool** with real-world scenarios
2. **Use real API calls** to Kimi and GLM providers
3. **Track conversation IDs** across platforms
4. **Validate file uploads** with provider-specific handling
5. **Monitor performance** and resource usage
6. **Generate comprehensive reports** with pass/fail analysis
7. **Include GLM-4.5-Flash as independent observer** for meta-validation

This suite is **disconnected from the main system** to avoid clutter and provide a clean testing environment.

---

## 📁 DIRECTORY STRUCTURE

```
tool_validation_suite/
├── README.md                    # ← YOU ARE HERE
├── SETUP_GUIDE.md              # How to set up and configure
├── TESTING_GUIDE.md            # How to run tests
├── ARCHITECTURE.md             # How the system works
├── RESULTS_ANALYSIS.md         # How to interpret results
├── API_INTEGRATION.md          # API key setup and usage
├── CONVERSATION_ID_GUIDE.md    # Conversation ID handling
│
├── tests/                      # All test scripts (30 tools)
│   ├── core_tools/            # 15 core tools
│   ├── advanced_tools/        # 7 advanced tools
│   ├── provider_tools/        # 8 provider-specific tools
│   └── integration/           # Cross-tool integration tests
│
├── results/                    # Test results storage
│   ├── latest/                # Latest test run
│   ├── history/               # Historical runs
│   └── reports/               # Generated reports
│
├── fixtures/                   # Test data and samples
│   ├── sample_files/          # Files for testing
│   ├── sample_prompts/        # Prompts for each tool
│   └── expected_responses/    # Expected response patterns
│
├── utils/                      # Testing utilities
│   ├── test_runner.py         # Main test runner
│   ├── result_collector.py    # Result aggregation
│   ├── api_client.py          # API client wrapper
│   ├── glm_watcher.py         # GLM-4.5-Flash observer (NEW!)
│   └── ...
│
├── scripts/                    # Helper scripts
│   ├── run_all_tests.py       # Run all tests
│   ├── generate_report.py     # Generate reports
│   └── validate_setup.py      # Validate setup
│
└── config/                     # Configuration files
    ├── test_config.json       # Test configuration
    ├── tool_variations.json   # Variations per tool
    └── success_criteria.json  # Success criteria
```

---

## 🚀 QUICK START

### 1. **Read the Documentation** (15 minutes)
- **SETUP_GUIDE.md** - Set up environment and API keys
- **TESTING_GUIDE.md** - Learn how to run tests
- **ARCHITECTURE.md** - Understand how it works

### 2. **Configure API Keys** (5 minutes)
```bash
# Copy example env file
cp .env.testing.example .env.testing

# Edit with your API keys
# KIMI_API_KEY=sk-ZpS6545OhteEeQuNSexAPhvW92WQqqYjkikNmxWExyeUsOjU
# GLM_API_KEY=90c4c8f531334693b2f684687fc7d250.ZhQ1I7U2mAgGZRUD
# GLM_WATCHER_KEY=1bd71ec183aa49f98d2d02d6cb6393e9.mx4rvtgunLxIipb4
```

### 3. **Validate Setup** (2 minutes)
```bash
python scripts/validate_setup.py
```

### 4. **Run Tests** (30-60 minutes)
```bash
# Run all tests
python scripts/run_all_tests.py

# Or run specific categories
python scripts/run_core_tests.py
python scripts/run_provider_tests.py
```

### 5. **Review Results** (10 minutes)
```bash
# Generate comprehensive report
python scripts/generate_report.py

# View results
cat results/latest/summary.json
cat results/reports/VALIDATION_REPORT.md
```

---

## 🎯 WHAT GETS TESTED?

### **30 Tools Tested:**

**Core Tools (15):**
1. chat - General chat
2. analyze - Code analysis
3. debug - Debugging
4. codereview - Code review
5. refactor - Refactoring
6. secaudit - Security audit
7. planner - Planning
8. tracer - Execution tracing
9. testgen - Test generation
10. consensus - Multi-perspective analysis
11. thinkdeep - Deep thinking
12. docgen - Documentation generation
13. precommit - Pre-commit validation
14. challenge - Challenge tool
15. status - Status check

**Advanced Tools (7):**
16. listmodels - List models
17. version - Version info
18. activity - Activity tracking
19. health - Health check
20. provider_capabilities - Provider capabilities
21. toolcall_log_tail - Log tail
22. selfcheck - Self-check

**Provider Tools (8):**
23. kimi_upload_and_extract - Kimi file upload
24. kimi_multi_file_chat - Kimi multi-file chat
25. kimi_intent_analysis - Kimi intent analysis
26. kimi_capture_headers - Kimi headers
27. kimi_chat_with_tools - Kimi chat with tools
28. glm_upload_file - GLM file upload
29. glm_web_search - GLM web search
30. glm_payload_preview - GLM payload preview

### **12 Variations Per Tool:**
1. Basic functionality
2. Edge cases
3. Error handling
4. File handling
5. Model selection
6. Continuation (multi-turn)
7. Timeout handling
8. Progress reporting
9. Web search integration
10. File upload (provider-specific)
11. Conversation ID persistence
12. Conversation ID isolation

**Total Test Scenarios:** 30 tools × 12 variations = **360 tests**

---

## 🔍 GLM WATCHER - INDEPENDENT OBSERVER

**NEW FEATURE:** Every test is observed by GLM-4.5-Flash, which provides:

- **Independent validation** of test results
- **Quality assessment** of tool responses
- **Anomaly detection** in behavior
- **Suggestions** for improvement
- **Meta-analysis** of testing process

The watcher uses a **separate API key** to ensure complete independence from the tools being tested.

**Watcher Output:** Stored in `results/latest/watcher_observations/`

---

## ✅ SUCCESS CRITERIA

Each test validates:

1. ✅ Execution without errors
2. ✅ Valid response structure
3. ✅ Response time within limits
4. ✅ Progress heartbeat (for long ops)
5. ✅ Correct logging
6. ✅ Graceful error handling
7. ✅ Real API integration
8. ✅ File upload success
9. ✅ Conversation ID tracking
10. ✅ Web search activation
11. ✅ Resource cleanup
12. ✅ Cost tracking

---

## 📊 RESULTS & REPORTS

After running tests, you'll get:

1. **summary.json** - Overall pass/fail statistics
2. **detailed_results.json** - Per-tool, per-variation results
3. **VALIDATION_REPORT.md** - Human-readable report
4. **TOOL_COVERAGE_MATRIX.md** - Coverage matrix
5. **FAILURE_ANALYSIS.md** - Analysis of failures
6. **watcher_observations/** - GLM watcher insights

---

## 🔑 API KEYS REQUIRED

This suite requires **3 API keys:**

1. **Kimi API Key** - For testing Kimi tools
2. **GLM API Key** - For testing GLM tools
3. **GLM Watcher Key** - For independent observation (separate account)

**Cost Estimate:** ~$2-5 USD for complete test run (360 tests)

---

## 📚 DOCUMENTATION

**Read these in order:**

1. **README.md** (this file) - Overview
2. **SETUP_GUIDE.md** - Setup instructions
3. **TESTING_GUIDE.md** - How to run tests
4. **ARCHITECTURE.md** - System design
5. **RESULTS_ANALYSIS.md** - Interpreting results
6. **API_INTEGRATION.md** - API details
7. **CONVERSATION_ID_GUIDE.md** - Conversation management

---

## 🎯 FOR NEXT AGENT

**If you're picking up this work:**

1. Read this README first
2. Check `results/latest/` for most recent test run
3. Review `results/reports/VALIDATION_REPORT.md` for status
4. Check task list for remaining work
5. Read ARCHITECTURE.md to understand the system

**Key Files:**
- `utils/test_runner.py` - Main test execution engine
- `utils/glm_watcher.py` - Independent observer
- `scripts/run_all_tests.py` - Entry point for testing
- `config/test_config.json` - Test configuration

---

## ⚠️ IMPORTANT NOTES

1. **Independent System** - This is completely separate from main codebase
2. **Real API Calls** - Tests use real API keys and cost money
3. **Long Running** - Full test suite takes 30-60 minutes
4. **Results Stored** - All results saved for historical analysis
5. **GLM Watcher** - Independent validation of every test

---

## 🚀 READY TO START?

1. ✅ Read SETUP_GUIDE.md
2. ✅ Configure .env.testing
3. ✅ Run validate_setup.py
4. ✅ Run run_all_tests.py
5. ✅ Review results

**Let's validate the entire system!** 🎉

