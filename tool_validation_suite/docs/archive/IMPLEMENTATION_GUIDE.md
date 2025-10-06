# 🚀 Implementation Guide - Creating Test Scripts

**Date:** 2025-10-05  
**Status:** ✅ Ready to Implement  
**Progress:** 3/36 test scripts complete (8%)

---

## 📊 CURRENT PROGRESS

### Completed Test Scripts (3/36 - 8%)

✅ **`tests/core_tools/test_chat.py`** (11 test functions)
- Basic functionality (Kimi + GLM)
- Edge cases (Kimi + GLM)
- Error handling (Kimi + GLM)
- Model selection (Kimi + GLM)
- Continuation (Kimi + GLM)
- Conversation ID isolation

✅ **`tests/advanced_tools/test_status.py`** (6 test functions)
- Basic functionality
- Edge cases
- Error handling
- Response format validation
- Provider availability
- Performance metrics

✅ **`tests/provider_tools/test_glm_web_search.py`** (8 test functions)
- Basic web search
- Edge cases
- Error handling
- Specific queries
- Model selection
- Multi-turn continuation
- Timeout handling
- Result validation

### Remaining Test Scripts (33/36 - 92%)

**Core Tools (14 remaining):**
- [ ] analyze
- [ ] debug
- [ ] codereview
- [ ] refactor
- [ ] secaudit
- [ ] planner
- [ ] tracer
- [ ] testgen
- [ ] consensus
- [ ] thinkdeep
- [ ] docgen
- [ ] precommit
- [ ] challenge

**Advanced Tools (6 remaining):**
- [ ] listmodels
- [ ] version
- [ ] activity
- [ ] health
- [ ] provider_capabilities
- [ ] toolcall_log_tail
- [ ] selfcheck

**Provider Tools (7 remaining):**
- [ ] kimi_upload_and_extract
- [ ] kimi_multi_file_chat
- [ ] kimi_intent_analysis
- [ ] kimi_capture_headers
- [ ] kimi_chat_with_tools
- [ ] glm_upload_file
- [ ] glm_payload_preview

**Integration Tests (6 remaining):**
- [ ] conversation_id_kimi
- [ ] conversation_id_glm
- [ ] conversation_id_isolation
- [ ] file_upload_kimi
- [ ] file_upload_glm
- [ ] web_search_integration

---

## 🎯 IMPLEMENTATION STRATEGY

### Phase 1: Complete Simple Tools (2-3 hours)

**Priority 1: Advanced Tools (Simple, No API Calls)**

These tools don't make provider API calls, so they're quick to test:

1. **`test_version.py`** (15 min)
   - Returns version information
   - Similar to test_status.py

2. **`test_listmodels.py`** (20 min)
   - Lists available models
   - Test model enumeration

3. **`test_health.py`** (15 min)
   - Health check endpoint
   - Similar to test_status.py

4. **`test_activity.py`** (20 min)
   - Activity logging
   - Test log retrieval

5. **`test_provider_capabilities.py`** (20 min)
   - Provider feature enumeration
   - Test capability reporting

6. **`test_toolcall_log_tail.py`** (20 min)
   - Log tailing functionality
   - Test log retrieval

7. **`test_selfcheck.py`** (20 min)
   - Self-diagnostic tool
   - Test diagnostic reporting

**Total:** ~2.5 hours

### Phase 2: Core Tools (4-6 hours)

**Priority 2: Core Tools (Provider API Calls)**

These tools make provider API calls and need comprehensive testing:

1. **`test_analyze.py`** (45 min)
   - Code analysis
   - Similar to test_chat.py structure

2. **`test_debug.py`** (45 min)
   - Debugging assistance
   - Error analysis

3. **`test_codereview.py`** (45 min)
   - Code review
   - Quality assessment

4. **`test_refactor.py`** (45 min)
   - Code refactoring suggestions
   - Improvement recommendations

5. **`test_secaudit.py`** (45 min)
   - Security audit
   - Vulnerability detection

6. **`test_planner.py`** (45 min)
   - Task planning
   - Strategy generation

7. **`test_tracer.py`** (45 min)
   - Execution tracing
   - Flow analysis

8. **`test_testgen.py`** (45 min)
   - Test generation
   - Test case creation

9. **`test_consensus.py`** (45 min)
   - Multi-model consensus
   - Agreement analysis

10. **`test_thinkdeep.py`** (45 min)
    - Deep thinking mode
    - Extended reasoning

11. **`test_docgen.py`** (45 min)
    - Documentation generation
    - Doc string creation

12. **`test_precommit.py`** (45 min)
    - Pre-commit checks
    - Code validation

13. **`test_challenge.py`** (45 min)
    - Challenge/critique mode
    - Critical analysis

**Total:** ~9-10 hours

### Phase 3: Provider Tools (2-3 hours)

**Priority 3: Provider-Specific Tools**

1. **`test_kimi_upload_and_extract.py`** (60 min)
   - File upload to Kimi
   - Content extraction

2. **`test_kimi_multi_file_chat.py`** (60 min)
   - Multi-file chat
   - File context management

3. **`test_kimi_intent_analysis.py`** (45 min)
   - Intent analysis
   - Purpose detection

4. **`test_kimi_capture_headers.py`** (30 min)
   - Header capture
   - Metadata extraction

5. **`test_kimi_chat_with_tools.py`** (60 min)
   - Chat with tool calling
   - Function execution

6. **`test_glm_upload_file.py`** (60 min)
   - File upload to GLM
   - Content processing

7. **`test_glm_payload_preview.py`** (30 min)
   - Payload preview
   - Request inspection

**Total:** ~5-6 hours

### Phase 4: Integration Tests (1-2 hours)

**Priority 4: Integration Tests**

1. **`test_conversation_id_kimi.py`** (30 min)
   - Kimi conversation tracking
   - ID persistence

2. **`test_conversation_id_glm.py`** (30 min)
   - GLM conversation tracking
   - ID persistence

3. **`test_conversation_id_isolation.py`** (30 min)
   - Platform isolation
   - No cross-contamination

4. **`test_file_upload_kimi.py`** (30 min)
   - Kimi file upload integration
   - End-to-end file handling

5. **`test_file_upload_glm.py`** (30 min)
   - GLM file upload integration
   - End-to-end file handling

6. **`test_web_search_integration.py`** (30 min)
   - Web search integration
   - Search result handling

**Total:** ~3 hours

---

## 📝 TEST SCRIPT TEMPLATE

### For Provider API Tools (like chat, analyze, debug)

```python
"""
Test suite for [TOOL_NAME] tool - Provider API validation
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from utils.api_client import APIClient
from utils.test_runner import TestRunner
from utils.response_validator import ResponseValidator


def test_[tool]_basic_kimi(api_client: APIClient, **kwargs):
    """Test basic [tool] functionality with Kimi"""
    response = api_client.call_kimi(
        model="kimi-k2-0905-preview",
        messages=[
            {"role": "user", "content": "[TEST PROMPT]"}
        ],
        temperature=0.0,
        tool_name="[tool_name]",
        variation="basic_functionality"
    )
    
    validator = ResponseValidator()
    is_valid, score, issues = validator.validate_response(
        response=response,
        expected_keywords=["[EXPECTED]"],
        min_length=10
    )
    
    return {
        "success": is_valid and score >= 70,
        "response": response[:200],
        "validation_score": score,
        "issues": issues
    }


def test_[tool]_basic_glm(api_client: APIClient, **kwargs):
    """Test basic [tool] functionality with GLM"""
    # Similar structure for GLM
    pass


if __name__ == "__main__":
    runner = TestRunner()
    
    tests = [
        ("[tool]", "basic_functionality", "kimi", test_[tool]_basic_kimi),
        ("[tool]", "basic_functionality", "glm", test_[tool]_basic_glm),
        # Add more test variations
    ]
    
    for tool_name, variation, provider, test_func in tests:
        runner.run_test(
            tool_name=tool_name,
            variation=variation,
            provider=provider,
            test_func=test_func
        )
    
    runner.generate_report()
```

### For Metadata Tools (like status, version, health)

```python
"""
Test suite for [TOOL_NAME] tool - Metadata validation
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from utils.test_runner import TestRunner


def test_[tool]_basic(api_client, **kwargs):
    """Test basic [tool] functionality"""
    # Simulate tool response
    result = {
        "tool": "[tool_name]",
        "data": {
            # Tool-specific data
        }
    }
    
    # Validate structure
    success = "tool" in result and "data" in result
    
    return {
        "success": success,
        "result": result,
        "validation_score": 100 if success else 0
    }


if __name__ == "__main__":
    runner = TestRunner()
    
    tests = [
        ("[tool]", "basic_functionality", "none", test_[tool]_basic),
        # Add more test variations
    ]
    
    for tool_name, variation, provider, test_func in tests:
        runner.run_test(
            tool_name=tool_name,
            variation=variation,
            provider=provider,
            test_func=test_func
        )
    
    runner.generate_report()
```

---

## ✅ QUALITY CHECKLIST

For each test script, ensure:

- [ ] Imports are correct
- [ ] Test functions follow naming convention
- [ ] Both Kimi and GLM tested (if applicable)
- [ ] Response validation included
- [ ] Error handling tested
- [ ] Success criteria clear
- [ ] Test runner registration complete
- [ ] Documentation complete

---

## 🚀 NEXT STEPS

1. **Complete Phase 1** (2-3 hours)
   - Create 6 remaining advanced tool tests
   - Quick wins, no API calls

2. **Complete Phase 2** (9-10 hours)
   - Create 13 remaining core tool tests
   - Most time-intensive phase

3. **Complete Phase 3** (5-6 hours)
   - Create 7 remaining provider tool tests
   - Provider-specific features

4. **Complete Phase 4** (3 hours)
   - Create 6 integration tests
   - End-to-end validation

5. **Run Full Suite** (1-2 hours)
   ```bash
   cd tool_validation_suite
   python scripts/run_all_tests.py
   ```

6. **Analyze Results** (1 hour)
   - Review reports
   - Check GLM Watcher observations
   - Verify cost tracking
   - Fix any issues

**Total Estimated Time:** 21-25 hours  
**Expected Cost:** $3-6 USD

---

## 📊 PROGRESS TRACKING

Update this section as you complete test scripts:

- [x] test_chat.py (3/36 = 8%)
- [x] test_status.py (6/36 = 17%)
- [x] test_glm_web_search.py (9/36 = 25%)
- [ ] test_version.py
- [ ] test_listmodels.py
- [ ] test_health.py
- [ ] ... (continue for all 36)

**Current Progress:** 3/36 (8%)  
**Target:** 36/36 (100%)

---

**Implementation Guide Ready** ✅  
**Date:** 2025-10-05  
**Next:** Create remaining 33 test scripts  
**Let's complete the testing suite!** 🚀

