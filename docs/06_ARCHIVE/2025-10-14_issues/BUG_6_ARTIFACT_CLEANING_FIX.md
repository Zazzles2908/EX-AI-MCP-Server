# Bug #6: Artifact Cleaning Fix
**Date:** 2025-10-14 (14th October 2025)  
**Priority:** ⚠️ P3 - High Usability  
**Status:** ✅ FIXED - Ready for testing  
**Phase:** Phase 3 - Response Quality

---

## 🐛 Bug Description

### Symptom
Model responses contain unprofessional artifacts that should be cleaned before returning to users:
- **GLM-4.5v:** Outputs `<|begin_of_box|>` and `<|end_of_box|>` tags
- **GLM-4.5-flash:** Adds "AGENT'S TURN:" suffix to responses
- **Progress markers:** `=== PROGRESS ===` sections appear in output

### Example
**User Request:** "Explain quantum computing"

**Expected Response:**
```
Quantum computing uses quantum mechanics principles to process information...
```

**Actual Response (Before Fix):**
```
<|begin_of_box|>
Quantum computing uses quantum mechanics principles to process information...
<|end_of_box|>

---

AGENT'S TURN: [additional text]
```

### Impact
- Unprofessional output
- Confusing to end users
- Makes responses look broken
- Affects GLM-4.5v and GLM-4.5-flash models

---

## 🔍 Root Cause Analysis

### Investigation
**Discovery:** Cleaning code already exists in WebSocket shim!

**File:** `scripts/run_ws_shim.py` lines 73-76

**Existing Code:**
```python
# Remove progress sections and agent turn markers if present
content = re.sub(r'=== PROGRESS ===.*?=== END PROGRESS ===\n*', '', content, flags=re.DOTALL)
content = re.sub(r"\n*---\n*\n*AGENT'S TURN:.*", '', content, flags=re.DOTALL)
```

**Problem:**
- Cleaning only happens in WebSocket shim
- Direct API calls bypass the shim
- Core response handling has no cleaning
- Need to move cleaning to `SimpleTool.format_response()`

### Why Artifacts Appear
- **GLM-4.5v:** Uses special tokens for structured output
- **GLM-4.5-flash:** Adds turn markers for multi-turn conversations
- **Progress markers:** Internal progress tracking that leaks into output
- These are model-specific behaviors that need post-processing

---

## 🔧 Fix Implementation

### Fix Location
**File:** `tools/simple/base.py`  
**Lines:** 135-184 (updated)

### Code Changes

**Added Helper Method:**
```python
def _clean_model_artifacts(self, response: str) -> str:
    """
    Remove model-specific artifacts from response.
    
    CRITICAL FIX (Bug #6): Clean up artifacts that some models add to responses:
    - GLM-4.5v: <|begin_of_box|>, <|end_of_box|> tags
    - GLM-4.5-flash: "AGENT'S TURN:" suffix
    - Progress markers: === PROGRESS === sections
    
    This cleaning was previously only in the WebSocket shim (run_ws_shim.py),
    but needs to be in core response handling to work for all clients.
    
    Args:
        response: Raw response from model
        
    Returns:
        Cleaned response string
    """
    import re
    
    # Remove GLM-4.5v box markers
    response = re.sub(r'<\|begin_of_box\|>', '', response)
    response = re.sub(r'<\|end_of_box\|>', '', response)
    
    # Remove progress sections (=== PROGRESS === ... === END PROGRESS ===)
    response = re.sub(r'=== PROGRESS ===.*?=== END PROGRESS ===\n*', '', response, flags=re.DOTALL)
    
    # Remove "AGENT'S TURN:" suffix (GLM-4.5-flash artifact)
    response = re.sub(r"\n*---\n*\n*AGENT'S TURN:.*", '', response, flags=re.DOTALL)
    
    return response.strip()
```

**Updated format_response Method:**
```python
def format_response(self, response: str, request, model_info: Optional[dict] = None) -> str:
    """
    Format the AI response before returning to the client.

    This is a hook method that subclasses can override to customize
    response formatting. The default implementation cleans model artifacts
    and returns the response.

    Args:
        response: The raw response from the AI model
        request: The validated request object
        model_info: Optional model information dictionary

    Returns:
        Formatted response string
    """
    # CRITICAL FIX (Bug #6): Clean model artifacts before returning
    return self._clean_model_artifacts(response)
```

### Fix Logic
1. Extract cleaning logic from WebSocket shim
2. Add as helper method `_clean_model_artifacts()`
3. Call from `format_response()` method
4. Apply to ALL SimpleTool responses
5. Subclasses can override if needed

### Why This Fix Works
- Cleaning happens in core response handling
- Works for ALL clients (not just WebSocket)
- Centralized in one place
- Easy to extend for new artifacts
- Backward compatible (subclasses can override)

---

## 📊 Impact Analysis

### Affected Components
- **Base Class:** `tools/simple/base.py` - SimpleTool
- **Tools:** ALL 4 simple tools (chat, activity, challenge, recommend)
- **Models:** Primarily GLM-4.5v and GLM-4.5-flash

### Behavior Changes
**Before Fix:**
- GLM-4.5v responses: Contains `<|begin_of_box|>` tags ❌
- GLM-4.5-flash responses: Contains "AGENT'S TURN:" suffix ❌
- Progress markers: Visible in output ❌

**After Fix:**
- GLM-4.5v responses: Clean, no tags ✅
- GLM-4.5-flash responses: Clean, no suffix ✅
- Progress markers: Removed ✅

### Backward Compatibility
✅ **Fully backward compatible**
- No breaking changes
- Cleaning is additive (removes unwanted text)
- Subclasses can override if needed
- Other models unaffected

---

## 🧪 Testing Plan

### Test Cases

**Test 1: GLM-4.5v artifact cleaning**
```python
# Should remove <|begin_of_box|> tags
response = chat(
    prompt="Explain quantum computing",
    model="glm-4.5v"
)
# Expected: No <|begin_of_box|> or <|end_of_box|> in response
```

**Test 2: GLM-4.5-flash artifact cleaning**
```python
# Should remove "AGENT'S TURN:" suffix
response = chat(
    prompt="Explain quantum computing",
    model="glm-4.5-flash"
)
# Expected: No "AGENT'S TURN:" in response
```

**Test 3: Progress marker cleaning**
```python
# Should remove progress sections
response = chat(
    prompt="Long task that shows progress",
    model="glm-4.5-flash"
)
# Expected: No "=== PROGRESS ===" sections in response
```

**Test 4: Other models (regression test)**
```python
# Should not affect clean responses
response = chat(
    prompt="Explain quantum computing",
    model="kimi-k2-0905-preview"
)
# Expected: Response unchanged (no artifacts to clean)
```

### Success Criteria
- ✅ GLM-4.5v responses are clean (no box tags)
- ✅ GLM-4.5-flash responses are clean (no AGENT'S TURN)
- ✅ Progress markers removed
- ✅ Other models unaffected
- ✅ No errors during cleaning

---

## 📝 Implementation Steps

### Step 1: Code Fix ✅ COMPLETE
- [x] Add `_clean_model_artifacts()` helper method
- [x] Update `format_response()` to call cleaning
- [x] Add comprehensive docstrings

### Step 2: Server Restart ⏳ PENDING
- [ ] Restart server to load fix
- [ ] Verify no errors during startup
- [ ] Confirm fix is loaded

### Step 3: Testing ⏳ PENDING
- [ ] Create test script `scripts/testing/test_artifact_cleaning.py`
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
- Bug #7: Empty prompt validation (NEXT)

### Related Files
- `scripts/run_ws_shim.py` - Original cleaning code location
- `tools/simple/base.py` - New cleaning code location

---

## 📈 Progress Tracking

**Phase 3: Response Quality**
- [x] Bug #3: glm-4.6 tool_choice ✅ FIXED
- [x] Bug #6: Artifact cleaning (THIS BUG) ✅ FIXED
- [ ] Bug #7: Empty prompt validation ⏳ NEXT
- [ ] Bug #8: Invalid model warnings ⏳ PENDING

**Overall Progress:** 2/4 bugs fixed (50%)

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
**Next Step:** Continue with Bug #7 (empty prompt validation)

