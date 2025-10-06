# Agentic Routing System - Issues & Fixes

**Date:** 2025-10-03  
**Status:** Issues identified, fixes needed

---

## System Design Intent

**Agentic Architecture:**
1. `DEFAULT_MODEL=auto` → Triggers intelligent routing
2. GLM-4.5-Flash acts as **AI Manager**
3. Manager analyzes prompt and selects appropriate model/provider
4. Routes to:
   - GLM-4.6 for complex reasoning
   - Kimi-K2 for long context
   - Kimi-Thinking for deep analysis
   - GLM-4.5-Flash for simple tasks

---

## Issues Found

### Issue 1: Missing Environment Variable

**Code expects:** `GLM_FLASH_MODEL`  
**Env has:** `GLM_FLASH_ROUTING_MODEL`

**Location:** `src/server/handlers/request_handler_model_resolution.py:75`
```python
if tool_name in simple_tools:
    return os.getenv("GLM_FLASH_MODEL", "glm-4.5-flash")  # ← WRONG VAR NAME!
```

**Impact:** Falls back to hardcoded "glm-4.5-flash" instead of using env variable

---

### Issue 2: DEFAULT_MODEL Set to Specific Model

**Current:** `DEFAULT_MODEL=glm-4.6`  
**Should be:** `DEFAULT_MODEL=auto`

**Impact:** Bypasses agentic routing entirely, always uses GLM-4.6

---

### Issue 3: Inconsistent Variable Names

**In .env:**
- `GLM_QUALITY_MODEL=glm-4.6`
- `GLM_SPEED_MODEL=glm-4.5-flash`
- `GLM_COMPLEX_MODEL=glm-4.6`
- `GLM_FLASH_ROUTING_MODEL=glm-4.5-flash`
- `KIMI_QUALITY_MODEL=kimi-thinking-preview`
- `KIMI_SPEED_MODEL=kimi-k2-0905-preview`
- `KIMI_FILE_MODEL=kimi-k2-0905-preview`

**In code:**
- `GLM_FLASH_MODEL` (not in .env!)
- `KIMI_THINKING_MODEL` (not in .env!)
- `KIMI_DEFAULT_MODEL` (not in .env!)
- `DEFAULT_AUTO_MODEL` (not in .env!)

**Impact:** Code falls back to hardcoded defaults, env variables ignored

---

## Variable Mapping Needed

### What Code Expects vs What .env Has

| Code Variable | .env Variable | Fallback | Purpose |
|--------------|---------------|----------|---------|
| `GLM_FLASH_MODEL` | `GLM_SPEED_MODEL` | glm-4.5-flash | Fast manager |
| `KIMI_THINKING_MODEL` | `KIMI_QUALITY_MODEL` | kimi-thinking-preview | Deep reasoning |
| `KIMI_DEFAULT_MODEL` | `KIMI_SPEED_MODEL` | kimi-k2-0711-preview | Default Kimi |
| `DEFAULT_AUTO_MODEL` | `GLM_SPEED_MODEL` | glm-4.5-flash | Auto fallback |

---

## Fixes Needed

### Fix 1: Update .env Variable Names

**Add missing variables:**
```env
# AI Manager (GLM Flash for routing)
GLM_FLASH_MODEL=glm-4.5-flash

# Deep reasoning (Kimi Thinking)
KIMI_THINKING_MODEL=kimi-thinking-preview

# Default Kimi model
KIMI_DEFAULT_MODEL=kimi-k2-0905-preview

# Auto mode fallback
DEFAULT_AUTO_MODEL=glm-4.5-flash
```

**OR update code to use existing variables:**
- `GLM_FLASH_MODEL` → `GLM_SPEED_MODEL`
- `KIMI_THINKING_MODEL` → `KIMI_QUALITY_MODEL`
- `KIMI_DEFAULT_MODEL` → `KIMI_SPEED_MODEL`

---

### Fix 2: Set DEFAULT_MODEL=auto

**Change:**
```env
# Before
DEFAULT_MODEL=glm-4.6

# After
DEFAULT_MODEL=auto
```

**Impact:** Enables agentic routing for all tools

---

### Fix 3: Verify Routing Logic

**Check these files:**
1. `src/server/handlers/request_handler_model_resolution.py`
   - Line 75: `GLM_FLASH_MODEL` usage
   - Line 84: `KIMI_THINKING_MODEL` usage
   - Line 70: `KIMI_DEFAULT_MODEL` usage
   - Line 107: `DEFAULT_AUTO_MODEL` usage

2. `src/router/service.py`
   - Verify `_fast_default` and `_long_default` initialization
   - Check if they use env variables correctly

3. `config.py`
   - Line 30: `DEFAULT_MODEL` usage

---

## Recommended Approach

**Option A: Standardize on Existing .env Variables** (RECOMMENDED)

Update code to use:
- `GLM_SPEED_MODEL` instead of `GLM_FLASH_MODEL`
- `KIMI_QUALITY_MODEL` instead of `KIMI_THINKING_MODEL`
- `KIMI_SPEED_MODEL` instead of `KIMI_DEFAULT_MODEL`
- `GLM_SPEED_MODEL` instead of `DEFAULT_AUTO_MODEL`

**Pros:**
- No .env changes needed
- Cleaner variable names
- Less duplication

**Cons:**
- Need to update code in multiple places

---

**Option B: Add Missing Variables to .env**

Add the missing variables that code expects.

**Pros:**
- Minimal code changes
- Backward compatible

**Cons:**
- Duplicate variables in .env
- More configuration to maintain

---

## Testing Plan

### Test 1: Verify Auto Routing

```python
# Should use glm-4.5-flash (AI manager)
result = chat(prompt="What is 2+2?", model="auto")
assert result.metadata["model_used"] == "glm-4.5-flash"
```

### Test 2: Verify Complex Routing

```python
# Should route to GLM-4.6 or Kimi-Thinking
result = thinkdeep(
    step="Analyze complex system architecture",
    model="auto"
)
assert result.metadata["model_used"] in ["glm-4.6", "kimi-thinking-preview"]
```

### Test 3: Verify DEFAULT_MODEL=auto

```python
# With DEFAULT_MODEL=auto, should use intelligent routing
# Simple chat → glm-4.5-flash
# Complex analysis → glm-4.6 or kimi-thinking
```

---

## Implementation Priority

1. **HIGH**: Fix variable name mismatches (Fix 1)
2. **HIGH**: Set DEFAULT_MODEL=auto (Fix 2)
3. **MEDIUM**: Verify routing logic (Fix 3)
4. **LOW**: Document variable mapping

---

## Next Steps

1. Decide on Option A vs Option B
2. Implement chosen approach
3. Test with simple and complex prompts
4. Verify AI manager is being used
5. Document final variable mapping

---

**Status:** Ready to implement  
**Estimated Time:** 30 minutes  
**Risk:** Low (env variable changes only)

