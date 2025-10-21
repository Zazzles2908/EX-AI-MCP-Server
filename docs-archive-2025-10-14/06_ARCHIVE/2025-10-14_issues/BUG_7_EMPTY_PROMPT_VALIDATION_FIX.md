# Bug #7: Empty Prompt Validation Fix
**Date:** 2025-10-14 (14th October 2025)  
**Priority:** ⚠️ P3 - High Usability  
**Status:** ✅ FIXED - Ready for testing  
**Phase:** Phase 3 - Response Quality

---

## 🐛 Bug Description

### Symptom
Empty prompts are accepted and sent to AI models, wasting API calls and returning meaningless responses.

### Example
**User Request:** (empty string or whitespace only)

**Expected Behavior:**
- System rejects empty prompt
- Returns error: "Prompt cannot be empty"
- No API call made

**Actual Behavior (Before Fix):**
- Empty prompt accepted ❌
- API call made to model ❌
- Model returns generic/confused response ❌
- API credits wasted ❌

### Impact
- Wastes API calls and credits
- Poor user experience
- Confusing error messages from models
- Affects ALL simple tools (chat, activity, challenge, recommend)

---

## 🔍 Root Cause Analysis

### Investigation
**Discovery:** Kimi-specific tool already has validation!

**File:** `tools/providers/kimi/kimi_tools_chat.py` lines 208-214

**Existing Code:**
```python
if not norm_msgs:
    err = {
        "status": "invalid_request",
        "error": "No non-empty messages provided. Provide at least one user message with non-empty content.",
    }
    return [TextContent(type="text", text=json.dumps(err, ensure_ascii=False))]
```

**Problem:**
- Validation only in Kimi-specific tool
- SimpleTool base class has NO validation
- Empty prompts pass through to models
- Need to add validation to `handle_prompt_file_with_fallback()`

### Why Empty Prompts Are Bad
- **API Cost:** Wastes credits on meaningless calls
- **User Experience:** Confusing responses
- **Model Behavior:** Models may return generic text or errors
- **Best Practice:** Validate input early, fail fast

---

## 🔧 Fix Implementation

### Fix Location
**File:** `tools/simple/base.py`  
**Lines:** 1111-1161 (updated)

### Code Changes

**Updated handle_prompt_file_with_fallback Method:**
```python
def handle_prompt_file_with_fallback(self, request) -> str:
    """
    Handle prompt.txt files with fallback to request field.

    This is a convenience method for tools that accept prompts either
    as a field or as a prompt.txt file. It handles the extraction
    and validation automatically.

    Args:
        request: The validated request object

    Returns:
        The effective prompt content

    Raises:
        ValueError: If prompt is empty or too large for MCP transport
    """
    # Check for prompt.txt in files
    files = self.get_request_files(request)
    if files:
        prompt_content, updated_files = self.handle_prompt_file(files)

        # Update request files list if needed
        if updated_files is not None:
            self.set_request_files(request, updated_files)
    else:
        prompt_content = None

    # Use prompt.txt content if available, otherwise use the prompt field
    user_content = prompt_content if prompt_content else self.get_request_prompt(request)

    # CRITICAL FIX (Bug #7): Validate prompt is not empty
    # Empty prompts waste API calls and should be rejected early
    if not user_content or not user_content.strip():
        from tools.models import ToolOutput
        error_output = ToolOutput(
            status="invalid_request",
            error="Prompt cannot be empty. Please provide a non-empty prompt.",
            data={}
        )
        raise ValueError(f"MCP_VALIDATION_ERROR:{error_output.model_dump_json()}")

    # Check user input size at MCP transport boundary (excluding conversation history)
    validation_content = self.get_prompt_content_for_size_validation(user_content)
    size_check = self.check_prompt_size(validation_content)
    if size_check:
        from tools.models import ToolOutput

        raise ValueError(f"MCP_SIZE_CHECK:{ToolOutput(**size_check).model_dump_json()}")

    return user_content
```

### Fix Logic
1. Get user content from prompt field or prompt.txt file
2. Check if content is empty or whitespace-only
3. If empty, raise ValueError with proper error message
4. If not empty, continue with size validation
5. Return validated content

### Why This Fix Works
- Validation happens early in request processing
- Prevents API calls for empty prompts
- Clear error message to user
- Consistent with Kimi tool validation
- Minimal code change, targeted fix

---

## 📊 Impact Analysis

### Affected Components
- **Base Class:** `tools/simple/base.py` - SimpleTool
- **Tools:** ALL 4 simple tools (chat, activity, challenge, recommend)
- **Method:** `handle_prompt_file_with_fallback()`

### Behavior Changes
**Before Fix:**
- Empty prompt → API call made → Wasted credits ❌
- Whitespace-only prompt → API call made → Wasted credits ❌

**After Fix:**
- Empty prompt → Validation error → No API call ✅
- Whitespace-only prompt → Validation error → No API call ✅
- Valid prompt → Works as before ✅

### Backward Compatibility
✅ **Fully backward compatible**
- No breaking changes for valid prompts
- Only rejects invalid (empty) prompts
- Error message is clear and actionable
- Follows existing error handling patterns

---

## 🧪 Testing Plan

### Test Cases

**Test 1: Empty string prompt**
```python
# Should reject with validation error
try:
    response = chat(prompt="")
    assert False, "Should have raised ValueError"
except ValueError as e:
    assert "Prompt cannot be empty" in str(e)
    assert "MCP_VALIDATION_ERROR" in str(e)
```

**Test 2: Whitespace-only prompt**
```python
# Should reject with validation error
try:
    response = chat(prompt="   \n\t  ")
    assert False, "Should have raised ValueError"
except ValueError as e:
    assert "Prompt cannot be empty" in str(e)
```

**Test 3: Valid prompt (regression test)**
```python
# Should work normally
response = chat(prompt="Explain quantum computing")
assert response.status == "success"
assert len(response.content) > 0
```

**Test 4: Prompt with leading/trailing whitespace**
```python
# Should work (whitespace is trimmed for validation)
response = chat(prompt="  Explain quantum computing  ")
assert response.status == "success"
```

### Success Criteria
- ✅ Empty prompts rejected with clear error
- ✅ Whitespace-only prompts rejected
- ✅ Valid prompts work normally
- ✅ No API calls made for invalid prompts
- ✅ Error message is user-friendly

---

## 📝 Implementation Steps

### Step 1: Code Fix ✅ COMPLETE
- [x] Add empty prompt validation
- [x] Add clear error message
- [x] Update docstring

### Step 2: Server Restart ⏳ PENDING
- [ ] Restart server to load fix
- [ ] Verify no errors during startup
- [ ] Confirm fix is loaded

### Step 3: Testing ⏳ PENDING
- [ ] Create test script `scripts/testing/test_empty_prompt_validation.py`
- [ ] Run all 4 test cases
- [ ] Verify success criteria met
- [ ] Document test results

### Step 4: Documentation ⏳ PENDING
- [ ] Update this file with test results
- [ ] Create evidence document
- [ ] Update PHASE_3_BUG_FIXES.md

---

## 🎯 Related Issues

### Similar Bugs
- Bug #3: glm-4.6 tool_choice (FIXED)
- Bug #6: Artifact cleaning (FIXED)
- Bug #8: Invalid model warnings (NEXT)

### Related Files
- `tools/providers/kimi/kimi_tools_chat.py` - Original validation example
- `tools/simple/base.py` - New validation location

---

## 📈 Progress Tracking

**Phase 3: Response Quality**
- [x] Bug #3: glm-4.6 tool_choice ✅ FIXED
- [x] Bug #6: Artifact cleaning ✅ FIXED
- [x] Bug #7: Empty prompt validation (THIS BUG) ✅ FIXED
- [ ] Bug #8: Invalid model warnings ⏳ NEXT

**Overall Progress:** 3/4 bugs fixed (75%)

---

## ✅ Completion Checklist

- [x] Root cause identified
- [x] Fix implemented
- [x] Code reviewed
- [ ] Server restarted
- [ ] Tests created
- [ ] Tests passed
- [ ] Documentation updated
- [ ] Evidence created

---

**Fix Implemented:** 2025-10-14 (14th October 2025)  
**Implemented By:** Augment Agent  
**Status:** ✅ FIXED - Ready for testing  
**Next Step:** Continue with Bug #8 (invalid model warnings)

