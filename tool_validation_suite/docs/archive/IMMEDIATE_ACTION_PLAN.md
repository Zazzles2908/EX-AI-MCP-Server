# ⚡ IMMEDIATE ACTION PLAN

**For Next Agent: Start Here**

---

## 🎯 YOUR MISSION

Create 36 test scripts to validate the EX-AI MCP Server's 30 tools with real API calls.

**Status:** ✅ Audit Complete - Ready to Proceed  
**Confidence:** 85% - This will genuinely validate the system and detect bugs  
**Time Required:** 6-9 hours (minimum) or 9-15 hours (recommended with MCP tests)

---

## ⚡ STEP 1: FIX CRITICAL ISSUE (5 minutes)

### Fix test_config.json Model Names

**File:** `tool_validation_suite/config/test_config.json`

**Change lines 65-75 from:**
```json
"models": {
  "kimi": [
    "moonshot-v1-8k",
    "moonshot-v1-32k",
    "moonshot-v1-128k"
  ],
  "glm": [
    "glm-4-flash",
    "glm-4-plus",
    "glm-4-air"
  ]
}
```

**To:**
```json
"models": {
  "kimi": [
    "kimi-k2-0905-preview",
    "kimi-k2-0711-preview",
    "kimi-k2-turbo-preview"
  ],
  "glm": [
    "glm-4.5-flash",
    "glm-4.6",
    "glm-4.5"
  ]
}
```

**Why:** Old model names will cause "model not found" errors.

---

## ⚡ STEP 2: VERIFY SETUP (2 minutes)

```bash
cd tool_validation_suite
python scripts/validate_setup.py
```

**Expected Output:**
```
✅ Environment variables loaded
✅ API keys present
✅ Directories created
✅ Configuration valid
✅ Ready to run tests
```

**If any ❌ appears:** Fix the issue before proceeding.

---

## ⚡ STEP 3: CREATE TEST SCRIPTS (4-6 hours)

### Order of Creation

**Start Simple → Build Complexity**

#### Round 1: Simple Tools (1 hour)
1. `tests/core_tools/test_chat.py`
2. `tests/core_tools/test_status.py`
3. `tests/advanced_tools/test_version.py`
4. `tests/advanced_tools/test_health.py`

**Why start here:** These are the simplest tools with minimal parameters.

#### Round 2: Core Analysis Tools (2-3 hours)
5. `tests/core_tools/test_analyze.py`
6. `tests/core_tools/test_debug.py`
7. `tests/core_tools/test_codereview.py`
8. `tests/core_tools/test_refactor.py`
9. `tests/core_tools/test_secaudit.py`
10. `tests/core_tools/test_planner.py`
11. `tests/core_tools/test_tracer.py`
12. `tests/core_tools/test_testgen.py`
13. `tests/core_tools/test_consensus.py`
14. `tests/core_tools/test_thinkdeep.py`
15. `tests/core_tools/test_docgen.py`
16. `tests/core_tools/test_precommit.py`
17. `tests/core_tools/test_challenge.py`

#### Round 3: Advanced Tools (1 hour)
18. `tests/advanced_tools/test_listmodels.py`
19. `tests/advanced_tools/test_activity.py`
20. `tests/advanced_tools/test_provider_capabilities.py`
21. `tests/advanced_tools/test_toolcall_log_tail.py`
22. `tests/advanced_tools/test_selfcheck.py`

#### Round 4: Provider Tools (1 hour)
23. `tests/provider_tools/test_kimi_upload_and_extract.py`
24. `tests/provider_tools/test_kimi_multi_file_chat.py`
25. `tests/provider_tools/test_kimi_intent_analysis.py`
26. `tests/provider_tools/test_kimi_capture_headers.py`
27. `tests/provider_tools/test_kimi_chat_with_tools.py`
28. `tests/provider_tools/test_glm_upload_file.py`
29. `tests/provider_tools/test_glm_web_search.py`
30. `tests/provider_tools/test_glm_payload_preview.py`

#### Round 5: Integration Tests (30 minutes)
31. `tests/integration/test_conversation_id_kimi.py`
32. `tests/integration/test_conversation_id_glm.py`
33. `tests/integration/test_conversation_id_isolation.py`
34. `tests/integration/test_file_upload_kimi.py`
35. `tests/integration/test_file_upload_glm.py`
36. `tests/integration/test_web_search_integration.py`

---

## 📝 TEST SCRIPT TEMPLATE

**Use this template for each test script:**

```python
"""
Test [TOOL_NAME] - All 12 variations

This script tests the [TOOL_NAME] tool with:
- Real API calls to Kimi and GLM
- GLM Watcher observations
- All 12 test variations

Created: 2025-10-05
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from utils import TestRunner

# ============================================================================
# TEST FUNCTIONS (12 variations)
# ============================================================================

def test_[tool_name]_basic(api_client, **kwargs):
    """Test basic [TOOL_NAME] functionality."""
    return api_client.call_kimi(
        model="kimi-k2-0905-preview",
        messages=[{"role": "user", "content": "Simple test prompt"}],
        tool_name="[tool_name]",
        variation="basic_functionality"
    )

def test_[tool_name]_edge_cases(api_client, **kwargs):
    """Test [TOOL_NAME] edge cases."""
    # Test with minimal input
    return api_client.call_kimi(
        model="kimi-k2-0905-preview",
        messages=[{"role": "user", "content": ""}],  # Empty prompt
        tool_name="[tool_name]",
        variation="edge_cases"
    )

def test_[tool_name]_error_handling(api_client, **kwargs):
    """Test [TOOL_NAME] error handling."""
    # Test with invalid input
    return api_client.call_kimi(
        model="invalid-model",  # Invalid model
        messages=[{"role": "user", "content": "test"}],
        tool_name="[tool_name]",
        variation="error_handling"
    )

def test_[tool_name]_file_handling(api_client, file_uploader, **kwargs):
    """Test [TOOL_NAME] file handling."""
    # Upload a test file first
    file_id = file_uploader.upload_to_kimi("path/to/test/file.txt")
    
    return api_client.call_kimi(
        model="kimi-k2-0905-preview",
        messages=[
            {"role": "user", "content": f"Analyze this file: {file_id}"}
        ],
        tool_name="[tool_name]",
        variation="file_handling"
    )

def test_[tool_name]_model_selection(api_client, **kwargs):
    """Test [TOOL_NAME] with different models."""
    # Test with GLM instead of Kimi
    return api_client.call_glm(
        model="glm-4.5-flash",
        messages=[{"role": "user", "content": "Test with GLM"}],
        tool_name="[tool_name]",
        variation="model_selection"
    )

def test_[tool_name]_continuation(api_client, conversation_tracker, **kwargs):
    """Test [TOOL_NAME] multi-turn conversation."""
    # Create conversation
    conv_id = conversation_tracker.create_conversation("kimi")
    
    # First turn
    response1 = api_client.call_kimi(
        model="kimi-k2-0905-preview",
        messages=[{"role": "user", "content": "First message"}],
        tool_name="[tool_name]",
        variation="continuation"
    )
    
    # Add to conversation
    conversation_tracker.add_message(conv_id, "user", "First message")
    conversation_tracker.add_message(conv_id, "assistant", response1.get("content", ""))
    
    # Second turn
    messages = conversation_tracker.get_conversation(conv_id)["messages"]
    messages.append({"role": "user", "content": "Follow-up message"})
    
    return api_client.call_kimi(
        model="kimi-k2-0905-preview",
        messages=messages,
        tool_name="[tool_name]",
        variation="continuation"
    )

def test_[tool_name]_timeout(api_client, **kwargs):
    """Test [TOOL_NAME] timeout handling."""
    # Test with very long prompt that might timeout
    long_prompt = "Analyze this: " + "x" * 10000
    
    return api_client.call_kimi(
        model="kimi-k2-0905-preview",
        messages=[{"role": "user", "content": long_prompt}],
        tool_name="[tool_name]",
        variation="timeout_handling"
    )

def test_[tool_name]_progress(api_client, **kwargs):
    """Test [TOOL_NAME] progress reporting."""
    # For tools that support progress heartbeat
    return api_client.call_kimi(
        model="kimi-k2-0905-preview",
        messages=[{"role": "user", "content": "Long analysis task"}],
        tool_name="[tool_name]",
        variation="progress_reporting",
        stream=True  # Enable streaming for progress
    )

def test_[tool_name]_web_search(api_client, **kwargs):
    """Test [TOOL_NAME] with web search."""
    return api_client.call_kimi(
        model="kimi-k2-0905-preview",
        messages=[{"role": "user", "content": "Search for latest info"}],
        tool_name="[tool_name]",
        variation="web_search",
        enable_search=True  # Enable web search
    )

def test_[tool_name]_file_upload(api_client, file_uploader, **kwargs):
    """Test [TOOL_NAME] file upload."""
    # Upload file and use in prompt
    file_id = file_uploader.upload_to_kimi("path/to/test/file.txt")
    
    return api_client.call_kimi(
        model="kimi-k2-0905-preview",
        messages=[{"role": "user", "content": f"Process file {file_id}"}],
        tool_name="[tool_name]",
        variation="file_upload"
    )

def test_[tool_name]_conversation_persistence(api_client, conversation_tracker, **kwargs):
    """Test [TOOL_NAME] conversation ID persistence."""
    # Create and reuse conversation
    conv_id = conversation_tracker.create_conversation("kimi")
    
    # Verify conversation persists
    assert conversation_tracker.get_conversation(conv_id) is not None
    
    return api_client.call_kimi(
        model="kimi-k2-0905-preview",
        messages=[{"role": "user", "content": "Test persistence"}],
        tool_name="[tool_name]",
        variation="conversation_id_persistence"
    )

def test_[tool_name]_conversation_isolation(api_client, conversation_tracker, **kwargs):
    """Test [TOOL_NAME] conversation ID isolation."""
    # Create Kimi conversation
    kimi_conv_id = conversation_tracker.create_conversation("kimi")
    
    # Try to use with GLM (should fail or be rejected)
    is_valid = conversation_tracker.is_valid_for_provider(kimi_conv_id, "glm")
    
    assert not is_valid, "Kimi conversation ID should not be valid for GLM"
    
    return {"status": "passed", "isolation_verified": True}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    runner = TestRunner()
    
    # Run all 12 variations
    test_functions = [
        (test_[tool_name]_basic, "basic_functionality"),
        (test_[tool_name]_edge_cases, "edge_cases"),
        (test_[tool_name]_error_handling, "error_handling"),
        (test_[tool_name]_file_handling, "file_handling"),
        (test_[tool_name]_model_selection, "model_selection"),
        (test_[tool_name]_continuation, "continuation"),
        (test_[tool_name]_timeout, "timeout_handling"),
        (test_[tool_name]_progress, "progress_reporting"),
        (test_[tool_name]_web_search, "web_search"),
        (test_[tool_name]_file_upload, "file_upload"),
        (test_[tool_name]_conversation_persistence, "conversation_id_persistence"),
        (test_[tool_name]_conversation_isolation, "conversation_id_isolation"),
    ]
    
    for test_func, variation in test_functions:
        runner.run_test(
            tool_name="[tool_name]",
            variation=variation,
            test_func=test_func,
            tool_type="simple"  # or "workflow" or "provider"
        )
    
    # Print results
    runner.print_results()
```

---

## ⚡ STEP 4: RUN TESTS (1-2 hours)

```bash
# Run all tests
python scripts/run_all_tests.py

# Or run specific categories
python scripts/run_core_tests.py
python scripts/run_provider_tests.py --provider kimi
```

**Monitor:**
- Cost tracking (should stay under $5)
- GLM Watcher observations
- Test pass/fail rates
- Performance metrics

---

## ⚡ STEP 5: ANALYZE RESULTS (1 hour)

```bash
# Generate reports
python scripts/generate_report.py
```

**Review:**
- `results/latest/reports/VALIDATION_REPORT.md`
- `results/latest/reports/COVERAGE_MATRIX.md`
- `results/latest/reports/FAILURE_ANALYSIS.md`
- `results/latest/watcher_observations/`

---

## 📊 SUCCESS CRITERIA

**Tests are successful when:**
- ✅ 90%+ pass rate (some failures expected for edge cases)
- ✅ All 30 tools tested
- ✅ All 12 variations tested per tool
- ✅ GLM Watcher observations collected
- ✅ Cost under $5
- ✅ No critical bugs detected

---

## 🚨 TROUBLESHOOTING

### Issue: "Model not found"
**Solution:** You forgot to fix test_config.json (Step 1)

### Issue: "API key invalid"
**Solution:** Check .env.testing has correct API keys

### Issue: "File not found"
**Solution:** Create test fixtures in `fixtures/` directory

### Issue: "Cost limit exceeded"
**Solution:** Increase limit in test_config.json or reduce test count

---

## 📚 REFERENCE DOCUMENTS

**Read these in order:**
1. `AUDIT_VISUAL_SUMMARY.md` - Quick overview
2. `NEXT_AGENT_HANDOFF.md` - Complete context
3. `AUDIT_SUMMARY_AND_RECOMMENDATIONS.md` - Detailed recommendations

**For deep dives:**
- `HIGH_LEVEL_AUDIT_ANALYSIS.md` - Overall assessment
- `TECHNICAL_AUDIT_FINDINGS.md` - Technical details
- `ARCHITECTURE.md` - System design
- `TESTING_GUIDE.md` - How to run tests

---

## ✅ FINAL CHECKLIST

```
Before Starting:
☐ Read this document completely
☐ Fix test_config.json model names
☐ Verify environment setup
☐ Review test template

During Test Creation:
☐ Start with simple tools
☐ Test each script individually
☐ Monitor costs
☐ Save progress frequently

After Test Creation:
☐ Run full test suite
☐ Review GLM Watcher observations
☐ Generate reports
☐ Analyze failures
☐ Document findings

Optional Enhancement:
☐ Add MCP integration tests
☐ Add schema validation tests
☐ Re-run complete suite
```

---

**Ready to Start?** ✅  
**Confidence:** 85%  
**Expected Time:** 6-9 hours  
**Expected Cost:** $2-5

**GO!** 🚀

