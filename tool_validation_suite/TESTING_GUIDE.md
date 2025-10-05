# Testing Guide - Tool Validation Suite

**Purpose:** Complete guide to running tests and interpreting results  
**Time Required:** 5 minutes to read, 30-60 minutes to run full suite  
**Difficulty:** Easy

---

## 🚀 QUICK START

### Run All Tests (Full Suite)

```bash
cd tool_validation_suite
python scripts/run_all_tests.py
```

**Duration:** 30-60 minutes  
**Cost:** ~$2-5 USD  
**Tests:** 360 test scenarios (30 tools × 12 variations)

### Run Core Tools Only

```bash
python scripts/run_core_tests.py
```

**Duration:** 15-20 minutes  
**Cost:** ~$1-2 USD  
**Tests:** 180 test scenarios (15 tools × 12 variations)

### Run Single Tool

```bash
python scripts/run_all_tests.py --tool chat
```

**Duration:** 1-2 minutes  
**Cost:** ~$0.10 USD  
**Tests:** 12 test scenarios (1 tool × 12 variations)

---

## 📋 TEST CATEGORIES

### 1. **Core Tools** (15 tools)

Essential user-facing tools:

```bash
# Run all core tools
python scripts/run_core_tests.py

# Run specific core tool
python scripts/run_all_tests.py --tool analyze
python scripts/run_all_tests.py --tool debug
python scripts/run_all_tests.py --tool codereview
```

**Tools:** chat, analyze, debug, codereview, refactor, secaudit, planner, tracer, testgen, consensus, thinkdeep, docgen, precommit, challenge, status

### 2. **Advanced Tools** (7 tools)

Diagnostic and utility tools:

```bash
# Run all advanced tools
python scripts/run_advanced_tests.py

# Run specific advanced tool
python scripts/run_all_tests.py --tool listmodels
python scripts/run_all_tests.py --tool health
```

**Tools:** listmodels, version, activity, health, provider_capabilities, toolcall_log_tail, selfcheck

### 3. **Provider Tools** (8 tools)

Provider-specific tools:

```bash
# Run all provider tools
python scripts/run_provider_tests.py

# Run Kimi tools only
python scripts/run_all_tests.py --provider kimi

# Run GLM tools only
python scripts/run_all_tests.py --provider glm
```

**Kimi Tools:** kimi_upload_and_extract, kimi_multi_file_chat, kimi_intent_analysis, kimi_capture_headers, kimi_chat_with_tools

**GLM Tools:** glm_upload_file, glm_web_search, glm_payload_preview

---

## 🎯 TEST VARIATIONS

Each tool is tested with 12 variations:

### 1. **Basic Functionality**
Tests the tool with simple, valid input.

```bash
python scripts/run_all_tests.py --tool chat --variation basic
```

### 2. **Edge Cases**
Tests with empty input, minimal input, maximum input.

```bash
python scripts/run_all_tests.py --tool chat --variation edge_cases
```

### 3. **Error Handling**
Tests with invalid input, missing required fields.

```bash
python scripts/run_all_tests.py --tool chat --variation error_handling
```

### 4. **File Handling**
Tests with files, without files, large files.

```bash
python scripts/run_all_tests.py --tool analyze --variation file_handling
```

### 5. **Model Selection**
Tests with different models (Kimi, GLM).

```bash
python scripts/run_all_tests.py --tool chat --variation model_selection
```

### 6. **Continuation**
Tests multi-turn conversations.

```bash
python scripts/run_all_tests.py --tool chat --variation continuation
```

### 7. **Timeout Handling**
Tests long-running operations.

```bash
python scripts/run_all_tests.py --tool thinkdeep --variation timeout
```

### 8. **Progress Reporting**
Tests progress heartbeat for long operations.

```bash
python scripts/run_all_tests.py --tool analyze --variation progress
```

### 9. **Web Search Integration**
Tests web search activation (Kimi/GLM).

```bash
python scripts/run_all_tests.py --tool chat --variation web_search
```

### 10. **File Upload**
Tests file upload to provider platforms.

```bash
python scripts/run_all_tests.py --tool kimi_upload_and_extract --variation file_upload
```

### 11. **Conversation ID Persistence**
Tests conversation ID tracking within platform.

```bash
python scripts/run_all_tests.py --tool chat --variation conversation_persistence
```

### 12. **Conversation ID Isolation**
Tests conversation ID isolation across platforms.

```bash
python scripts/run_all_tests.py --tool chat --variation conversation_isolation
```

---

## 🔧 ADVANCED OPTIONS

### Limit Number of Tests

```bash
# Run only first 5 tests
python scripts/run_all_tests.py --limit 5

# Run only first test of each tool
python scripts/run_all_tests.py --limit 1
```

### Skip Specific Variations

```bash
# Skip file upload tests
python scripts/run_all_tests.py --skip file_upload

# Skip multiple variations
python scripts/run_all_tests.py --skip file_upload,web_search
```

### Dry Run (No API Calls)

```bash
# See what would be tested without running
python scripts/run_all_tests.py --dry-run
```

### Verbose Output

```bash
# Show detailed output during testing
python scripts/run_all_tests.py --verbose
```

### Disable GLM Watcher

```bash
# Run without watcher observations
python scripts/run_all_tests.py --no-watcher
```

### Custom Timeout

```bash
# Set custom timeout (seconds)
python scripts/run_all_tests.py --timeout 600
```

---

## 📊 MONITORING PROGRESS

### Real-Time Progress

During test execution, you'll see:

```
[1/360] Testing chat - basic_functionality... ✅ PASS (2.3s, $0.02)
[2/360] Testing chat - edge_cases... ✅ PASS (1.8s, $0.01)
[3/360] Testing chat - error_handling... ✅ PASS (1.5s, $0.01)
...
[180/360] Testing analyze - basic_functionality... ✅ PASS (15.2s, $0.08)
...
[360/360] Testing glm_payload_preview - conversation_isolation... ✅ PASS (1.2s, $0.01)

========================================
SUMMARY
========================================
Total Tests: 360
Passed: 355 (98.6%)
Failed: 5 (1.4%)
Skipped: 0
Duration: 1834.5s (30.6 minutes)
Total Cost: $4.23 USD
========================================
```

### Check Progress in Another Terminal

```bash
# View latest results
cat results/latest/summary.json

# Tail test logs
tail -f results/latest/test_logs/core_tools/chat.log

# Check watcher observations
ls results/latest/watcher_observations/
```

---

## 🛑 STOPPING TESTS

### Graceful Stop

Press `Ctrl+C` once to stop gracefully:

```
^C
Stopping tests gracefully...
Saving results...
Generating reports...
Done. Results saved to results/latest/
```

### Force Stop

Press `Ctrl+C` twice to force stop:

```
^C^C
Force stopping...
Partial results saved to results/latest/
```

---

## 📈 VIEWING RESULTS

### Quick Summary

```bash
# View JSON summary
cat results/latest/summary.json

# View markdown report
cat results/reports/VALIDATION_REPORT.md
```

### Detailed Results

```bash
# View detailed results
cat results/latest/detailed_results.json

# View specific tool results
cat results/latest/detailed_results.json | jq '.tools.chat'
```

### Test Logs

```bash
# View all logs
ls results/latest/test_logs/

# View specific tool log
cat results/latest/test_logs/core_tools/chat.log

# Search for errors
grep ERROR results/latest/test_logs/**/*.log
```

### Watcher Observations

```bash
# View all observations
ls results/latest/watcher_observations/

# View specific observation
cat results/latest/watcher_observations/chat_basic_functionality.json

# View watcher summary
cat results/latest/watcher_observations/summary.json
```

### API Responses (Debugging)

```bash
# View API requests/responses
ls results/latest/api_responses/kimi/
ls results/latest/api_responses/glm/

# View specific API response
cat results/latest/api_responses/kimi/chat_basic_functionality_request.json
cat results/latest/api_responses/kimi/chat_basic_functionality_response.json
```

---

## 🔄 RE-RUNNING FAILED TESTS

### Automatic Retry

Failed tests are automatically retried (up to 3 times by default).

### Manual Re-Run

```bash
# Re-run only failed tests from last run
python scripts/run_all_tests.py --retry-failed

# Re-run specific failed test
python scripts/run_all_tests.py --tool chat --variation basic_functionality
```

---

## 📊 GENERATING REPORTS

### Auto-Generated Reports

Reports are automatically generated after test completion:

- `results/reports/VALIDATION_REPORT.md` - Main report
- `results/reports/TOOL_COVERAGE_MATRIX.md` - Coverage matrix
- `results/reports/FAILURE_ANALYSIS.md` - Failure analysis

### Manual Report Generation

```bash
# Generate all reports
python scripts/generate_report.py

# Generate specific report
python scripts/generate_report.py --type validation
python scripts/generate_report.py --type coverage
python scripts/generate_report.py --type failures
```

---

## ⚠️ TROUBLESHOOTING

### Problem: "API key not found"

**Solution:**
```bash
# Check .env.testing exists
ls .env.testing

# Verify API keys are set
grep KIMI_API_KEY .env.testing
grep GLM_API_KEY .env.testing
grep GLM_WATCHER_KEY .env.testing
```

### Problem: "Cost limit exceeded"

**Solution:**
```bash
# Increase cost limit in .env.testing
MAX_TOTAL_COST=20.00

# Or run fewer tests
python scripts/run_all_tests.py --limit 10
```

### Problem: "Timeout exceeded"

**Solution:**
```bash
# Increase timeout in .env.testing
TEST_TIMEOUT_SECS=600

# Or increase for specific run
python scripts/run_all_tests.py --timeout 600
```

### Problem: "Test failed"

**Solution:**
```bash
# Check test log
cat results/latest/test_logs/core_tools/[tool_name].log

# Check API response
cat results/latest/api_responses/kimi/[test_name]_response.json

# Check watcher observation
cat results/latest/watcher_observations/[test_name].json

# Re-run with verbose output
python scripts/run_all_tests.py --tool [tool_name] --verbose
```

---

## 🎯 BEST PRACTICES

### 1. **Start Small**

```bash
# Test one tool first
python scripts/run_all_tests.py --tool chat --limit 1

# Then expand
python scripts/run_all_tests.py --tool chat
python scripts/run_core_tests.py
python scripts/run_all_tests.py
```

### 2. **Monitor Costs**

```bash
# Check cost after each run
cat results/latest/summary.json | jq '.total_cost_usd'

# Set conservative limits
MAX_TOTAL_COST=5.00
```

### 3. **Review Watcher Observations**

```bash
# Always check watcher insights
cat results/latest/watcher_observations/summary.json
```

### 4. **Keep History**

```bash
# Results are automatically saved to history
ls results/history/

# Compare runs
diff results/history/2025-10-05_run1/summary.json results/latest/summary.json
```

---

## 📚 NEXT STEPS

After running tests:

1. ✅ Review **RESULTS_ANALYSIS.md** to interpret results
2. ✅ Check `results/reports/VALIDATION_REPORT.md`
3. ✅ Review watcher observations
4. ✅ Address any failures
5. ✅ Re-run failed tests

---

## ✅ TESTING CHECKLIST

Before running tests:

- [ ] Read this guide
- [ ] Verify setup (run `validate_setup.py`)
- [ ] Check API keys are configured
- [ ] Set cost limits appropriately
- [ ] Understand what will be tested
- [ ] Know how to stop tests if needed

**Ready to test!** 🚀

