# Systematic EXAI Testing Report - 2025-10-21

## Executive Summary

Conducted comprehensive testing of EXAI system with **14 test cases** across multiple models, tools, and configurations.

**Results**:
- ✅ **9 tests PASSED** - Working correctly
- ⚠️ **5 tests REVEALED ISSUES** - Need fixes

**Critical Issues Found**:
1. **AsyncGLMProvider missing chat_completions_create method** (same as AsyncKimi bug)
2. **Expert analysis returning non-JSON responses** (parse errors)
3. **Codereview tool requires relevant_files in step 1** (validation error)
4. **Duplicate request blocking** (OVER_CAPACITY errors)
5. **Timeout issues** (180s timeout on analyze tool)

---

## Test Matrix

| Test # | Tool | Model | Websearch | Result | Issue |
|--------|------|-------|-----------|--------|-------|
| 1 | chat | glm-4.6 | ✅ | ✅ PASS | None |
| 2 | chat | glm-4.5-flash | ❌ | ✅ PASS | None |
| 3 | chat | kimi-k2-0905-preview | ✅ | ✅ PASS | None |
| 4 | thinkdeep | glm-4.6 | ✅ | ⚠️ ISSUE | Expert analysis non-JSON |
| 5 | thinkdeep | kimi-k2-0905-preview | ❌ | ⚠️ ISSUE | Expert analysis non-JSON |
| 6 | analyze | glm-4.5-flash | ❌ | ⚠️ ISSUE | Duplicate request + timeout |
| 7 | debug | glm-4.5-flash | ❌ | ✅ PASS | None |
| 8 | codereview | kimi-thinking-preview | ❌ | ❌ FAIL | Validation error |
| 9 | planner | glm-4.6 | N/A | ✅ PASS | None |
| 10 | chat | glm-4.5-flash | ✅ | ✅ PASS | None |
| 11 | chat | kimi-k2-0905-preview | ❌ | ✅ PASS | None |
| 12 | chat | glm-4.6 | ❌ | ✅ PASS | Unicode handled |
| 13 | chat | kimi-k2-0905-preview | ❌ | ✅ PASS | Code snippets handled |
| 14 | thinkdeep | glm-4.6 | N/A | ⚠️ ISSUE | Expert analysis non-JSON |

---

## Issue #1: AsyncGLMProvider Missing Method

### Severity: 🔴 **CRITICAL**

### Description
AsyncGLMProvider doesn't have `chat_completions_create` method, causing fallback to sync provider.

### Evidence
```
[EXPERT_DEBUG] Async provider call failed: 'AsyncGLMProvider' object has no attribute 'chat_completions_create', falling back to sync
```

### Impact
- Expert analysis with GLM models falls back to sync
- Performance degradation
- Same bug as AsyncKimiProvider (which we already fixed)

### Root Cause
AsyncGLMProvider missing the same method we added to AsyncKimiProvider in previous fix.

### Fix Required
Add `chat_completions_create` method to AsyncGLMProvider (same pattern as AsyncKimiProvider fix).

**File**: `src/providers/async_glm.py`

**Implementation**:
```python
async def chat_completions_create(
    self,
    model: str,
    messages: list[dict],
    temperature: float = 0.3,
    thinking_mode: Optional[str] = None,
    **kwargs,
) -> dict:
    """Create chat completion using message arrays (for expert_analysis compatibility)."""
    # Delegate to async_glm_chat module which returns ModelResponse
    response = await async_glm_chat.chat_completions_create_async(
        client=self._sdk_client,
        model=model,
        messages=messages,
        temperature=temperature,
        **kwargs
    )
    
    # Convert ModelResponse to dict format expected by expert_analysis
    return {
        "content": response.content,
        "model": response.model_name,
        "usage": response.usage or {},
    }
```

---

## Issue #2: Expert Analysis Non-JSON Responses

### Severity: 🟡 **HIGH**

### Description
Expert analysis sometimes returns plain text instead of JSON, causing parse errors.

### Evidence
```json
{
  "expert_analysis": {
    "status": "analysis_complete",
    "raw_analysis": "\nI see you're testing the thinkdeep functionality...",
    "parse_error": "Response was not valid JSON: Expecting value: line 1 column 1 (char 0)"
  }
}
```

### Test Cases Affected
- Test 4: thinkdeep with glm-4.6
- Test 5: thinkdeep with kimi-k2-0905-preview  
- Test 14: thinkdeep with continuation_id

### Impact
- Expert analysis fails to provide structured output
- Tools can't parse recommendations
- User gets raw text instead of actionable insights

### Root Cause Analysis

**Hypothesis 1**: System prompt doesn't enforce JSON output
- Expert analysis system prompt may not explicitly require JSON format
- Models default to conversational responses

**Hypothesis 2**: Models interpret "test" prompts differently
- When step says "Test X: ...", models think it's a test scenario
- Models ask for clarification instead of analyzing

**Hypothesis 3**: Low confidence triggers different response mode
- All failing tests have `confidence: "low"`
- Models may switch to "ask for more info" mode at low confidence

### Fix Required

**Option A**: Enforce JSON output in expert analysis system prompt
```python
# In expert_analysis.py system prompt
"You MUST respond with valid JSON only. No explanatory text before or after."
```

**Option B**: Add JSON schema validation to system prompt
```python
"Response format: {\"status\": \"...\", \"recommendations\": [...], \"next_steps\": \"...\"}"
```

**Option C**: Improve test case design
- Don't use "Test X:" in step descriptions
- Provide actual problems to analyze, not test scenarios

---

## Issue #3: Codereview Validation Error

### Severity: 🟡 **HIGH**

### Description
Codereview tool requires `relevant_files` parameter in step 1, but this isn't clear from documentation.

### Evidence
```
ERROR: 1 validation error for CodeReviewRequest
Value error, Step 1 requires 'relevant_files' field to specify code files or directories to review
```

### Test Case
Test 8: `codereview_EXAI-WS` with step "Review best practices for error handling"

### Impact
- Tool fails immediately on step 1
- User doesn't know what went wrong
- No code review performed

### Root Cause
Pydantic validation enforces `relevant_files` requirement, but:
1. Tool description doesn't mention this requirement
2. Error message is technical (Pydantic error)
3. No helpful guidance on what files to provide

### Fix Required

**Option A**: Make relevant_files optional for step 1
```python
# Allow step 1 without files for general questions
if step_number == 1 and not relevant_files:
    # Return guidance on what files are needed
    return {"status": "files_required", "message": "..."}
```

**Option B**: Improve error message
```python
# Custom validation error with helpful message
raise ValueError(
    "Code review requires files to review. Please provide:\n"
    "- relevant_files: List of file paths to review\n"
    "Example: relevant_files=['src/main.py', 'tests/test_main.py']"
)
```

**Option C**: Update tool description
```markdown
CRITICAL: Code review requires 'relevant_files' parameter in step 1.
Provide absolute paths to files you want reviewed.
```

---

## Issue #4: Duplicate Request Blocking

### Severity: 🟡 **MEDIUM**

### Description
System blocks duplicate requests with OVER_CAPACITY error.

### Evidence
```json
{
  "code": "OVER_CAPACITY",
  "message": "Duplicate request in progress (original: c74fb95d-e4e3-4a2a-9f0b-e7ffff465f65)",
  "details": {"retry_after_secs": 5}
}
```

### Test Case
Test 6: analyze_EXAI-WS called while previous request still processing

### Impact
- Parallel testing blocked
- User must wait 5+ seconds between requests
- Confusing error message

### Root Cause
Deduplication system prevents identical requests from running concurrently.

### Analysis
**Is this a bug or feature?**
- ✅ **FEATURE**: Prevents duplicate work
- ⚠️ **BUG**: Blocks legitimate parallel requests
- ⚠️ **UX ISSUE**: Error message unclear

### Fix Required

**Option A**: Improve error message
```json
{
  "code": "DUPLICATE_REQUEST",
  "message": "This request is already being processed. Please wait or use a different request.",
  "details": {
    "retry_after_secs": 5,
    "original_request_id": "...",
    "suggestion": "Wait 5 seconds or modify your request to make it unique"
  }
}
```

**Option B**: Add request ID to prevent false positives
- Include timestamp or random ID in request
- Only block truly identical requests

---

## Issue #5: Timeout on Analyze Tool

### Severity: 🟡 **MEDIUM**

### Description
Analyze tool timed out after 180 seconds.

### Evidence
```
ERROR: [INTERNAL_ERROR] Tool execution timed out after 180.0s
```

### Test Case
Test 6: analyze_EXAI-WS with glm-4.5-flash

### Impact
- Long-running analysis fails
- No partial results returned
- User loses all work

### Root Cause
Default timeout (180s) too short for complex analysis.

### Fix Required

**Option A**: Increase timeout for analyze tool
```python
# In config.py or tool-specific timeout
ANALYZE_TIMEOUT = 300  # 5 minutes instead of 3
```

**Option B**: Add progress updates
```python
# Send progress updates every 30s
# User knows tool is still working
```

**Option C**: Implement streaming results
```python
# Return partial results as analysis progresses
# User gets value even if timeout occurs
```

---

## Successful Test Cases

### ✅ Test 1: GLM-4.6 Chat with Websearch
**Input**: "What is the difference between async and sync in Python?"
**Output**: Clear 2-sentence explanation
**Quality**: ⭐⭐⭐⭐⭐ Excellent

---

### ✅ Test 2: GLM-4.5-Flash Math
**Input**: "What is 15 * 23?"
**Output**: "345"
**Quality**: ⭐⭐⭐⭐⭐ Perfect

---

### ✅ Test 3: Kimi Current Events with Websearch
**Input**: "Latest AI developments in 2025?"
**Output**: 3 detailed bullet points with context
**Quality**: ⭐⭐⭐⭐⭐ Excellent (web search worked!)

---

### ✅ Test 7: Debug Tool
**Input**: "Debug function returning None"
**Output**: Completed with low confidence (expected for hypothetical)
**Quality**: ⭐⭐⭐ Good (appropriate response)

---

### ✅ Test 9: Planner Tool
**Input**: "Plan migration to microservices"
**Output**: Planning complete, ready for next steps
**Quality**: ⭐⭐⭐⭐ Very Good

---

### ✅ Test 10: Empty Prompt Handling
**Input**: "Empty prompt test"
**Output**: Helpful guidance on what information is needed
**Quality**: ⭐⭐⭐⭐ Very Good (graceful handling)

---

### ✅ Test 11: Complex Technical Question
**Input**: Long distributed systems architecture question
**Output**: 5 detailed architectural considerations with concrete examples
**Quality**: ⭐⭐⭐⭐⭐ Outstanding (1500+ words, highly detailed)

---

### ✅ Test 12: Unicode Handling
**Input**: "你好世界 🚀 émojis and spëcial çharacters"
**Output**: Confirmed proper Unicode handling
**Quality**: ⭐⭐⭐⭐⭐ Perfect

---

### ✅ Test 13: Code Snippet Handling
**Input**: Python function with code block
**Output**: Detailed analysis of function behavior
**Quality**: ⭐⭐⭐⭐⭐ Excellent

---

## Summary Statistics

**Total Tests**: 14
**Passed**: 9 (64%)
**Issues Found**: 5 (36%)

**By Severity**:
- 🔴 Critical: 1 (AsyncGLMProvider)
- 🟡 High: 2 (Expert analysis JSON, Codereview validation)
- 🟡 Medium: 2 (Duplicate blocking, Timeout)

**By Tool**:
- chat: 6/6 passed (100%)
- thinkdeep: 0/3 passed (0% - all had expert analysis issues)
- analyze: 0/1 passed (timeout)
- debug: 1/1 passed (100%)
- codereview: 0/1 passed (validation error)
- planner: 1/1 passed (100%)

**By Model**:
- glm-4.6: 3/5 passed (60%)
- glm-4.5-flash: 3/4 passed (75%)
- kimi-k2-0905-preview: 3/4 passed (75%)
- kimi-thinking-preview: 0/1 passed (validation error)

---

## Recommendations

### Immediate Fixes (Critical)
1. ✅ **Add chat_completions_create to AsyncGLMProvider** (same as AsyncKimi fix)
2. ⚠️ **Fix expert analysis JSON output** (enforce JSON in system prompt)
3. ⚠️ **Improve codereview validation** (better error messages)

### Short-term Improvements (High Priority)
4. Increase analyze tool timeout to 300s
5. Improve duplicate request error messages
6. Add progress updates for long-running tools

### Long-term Enhancements
7. Implement streaming results for workflow tools
8. Add partial result recovery on timeout
9. Create comprehensive tool usage examples
10. Add integration tests for all model/tool combinations

---

## Testing Methodology

**Approach**: Systematic black-box testing
- Multiple models (GLM, Kimi)
- Multiple tools (chat, workflow tools)
- Various parameters (websearch, thinking modes, temperatures)
- Edge cases (Unicode, code snippets, empty prompts, long prompts)

**Coverage**:
- ✅ Basic functionality
- ✅ Model compatibility
- ✅ Parameter variations
- ✅ Edge cases
- ✅ Error handling
- ⚠️ Performance (partial - found timeout issue)
- ❌ Stress testing (not performed)
- ❌ Concurrent requests (blocked by deduplication)

---

## Conclusion

**System Status**: 🟡 **MOSTLY FUNCTIONAL** with known issues

**Strengths**:
- ✅ Chat tool works excellently across all models
- ✅ Unicode and special character handling perfect
- ✅ Web search integration working (after our fix)
- ✅ Complex technical responses high quality

**Weaknesses**:
- ❌ Workflow tools have expert analysis JSON issues
- ❌ AsyncGLMProvider missing critical method
- ❌ Validation errors not user-friendly
- ❌ Timeout handling needs improvement

**Next Steps**:
1. Fix AsyncGLMProvider (copy AsyncKimi fix)
2. Enforce JSON output in expert analysis
3. Improve error messages
4. Increase timeouts
5. Add comprehensive integration tests

---

**End of Testing Report**

