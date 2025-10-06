# CRITICAL CONFIGURATION ISSUES - Complete System Audit

**Date:** 2025-10-06  
**Status:** 🚨 CRITICAL - MULTIPLE FUNDAMENTAL ISSUES  
**Priority:** IMMEDIATE FIX REQUIRED

---

## 🔥 CRITICAL ISSUES FOUND

### 1. MODEL NAME CHAOS

#### Issue: Wrong Model Names in Config
**File:** `src/providers/glm_config.py`

**Current (WRONG):**
```python
SUPPORTED_MODELS = {
    "glm-4.6": {...},           # ✅ Exists
    "glm-4.5-flash": {...},     # ✅ Exists
    "glm-4.5": {...},           # ✅ Exists
    "glm-4.5-air": {...},       # ✅ Exists
}
```

**Missing Models Referenced in Tests:**
```python
# scripts/test_glm_websearch.py uses:
"glm-4-flash"    # ❌ DOESN'T EXIST IN CONFIG!
"glm-4-plus"     # ❌ DOESN'T EXIST IN CONFIG!
```

**Actual GLM Models (from API):**
- `glm-4-plus` (supports websearch)
- `glm-4-flash` (fast, cheap)
- `glm-4.6` (flagship, 200K context)
- `glm-4.5` (standard)
- `glm-4.5-flash` (fast)
- `glm-4.5-air` (lightweight)

---

### 2. INCORRECT ALIASES

#### Issue: glm-4.5-flash aliases to glm-4.5-air
**File:** `src/providers/glm_config.py` line 38

**Current (WRONG):**
```python
"glm-4.5-flash": ModelCapabilities(
    ...
    aliases=["glm-4.5-air"],  # ❌ WRONG! These are DIFFERENT models!
)
```

**Problem:** 
- `glm-4.5-flash` and `glm-4.5-air` are SEPARATE models with different capabilities
- Aliasing them means requests for one model get routed to the other
- This breaks model selection logic

**Fix:**
```python
"glm-4.5-flash": ModelCapabilities(
    ...
    aliases=[],  # No aliases
)
```

---

### 3. WEBSEARCH SUPPORT NOT DOCUMENTED

#### Issue: No indication which models support websearch
**File:** `src/providers/glm_config.py`

**Current:** ModelCapabilities has no `supports_websearch` field

**Problem:**
- We're passing websearch tools to ALL models
- Only some models support it (glm-4-plus confirmed working)
- glm-4.5-flash HANGS when given websearch tools
- No way to check if a model supports websearch

**Fix:** Add `supports_websearch` field to ModelCapabilities:
```python
"glm-4-plus": ModelCapabilities(
    ...
    supports_websearch=True,  # ✅ Confirmed working
)
"glm-4.5-flash": ModelCapabilities(
    ...
    supports_websearch=False,  # ❌ Hangs with websearch
)
```

---

### 4. BASE URL CONFUSION

#### Issue: Multiple conflicting base URLs
**File:** `.env`

**Current (CONFUSING):**
```env
GLM_BASE_URL=https://api.z.ai/api/paas/v4
GLM_API_URL=https://api.z.ai/api/paas/v4
ZHIPUAI_API_KEY=90c4c8f531334693b2f684687fc7d250.ZhQ1I7U2mAgGZRUD
ZHIPUAI_API_URL=https://open.bigmodel.cn/api/paas/v4
ZHIPUAI_BASE_URL=https://open.bigmodel.cn/api/paas/v4
```

**Problems:**
1. Why do we have BOTH `GLM_*` and `ZHIPUAI_*` vars?
2. They point to DIFFERENT URLs (z.ai vs bigmodel.cn)
3. Code uses `GLM_API_URL` but also checks `ZHIPUAI_API_URL` as fallback
4. Confusing which one is actually used

**User Observation:** z.ai is MUCH faster than bigmodel.cn

**Fix:** Simplify to ONE set of vars:
```env
# Use z.ai (faster proxy)
GLM_API_KEY=90c4c8f531334693b2f684687fc7d250.ZhQ1I7U2mAgGZRUD
GLM_BASE_URL=https://api.z.ai/api/paas/v4

# Remove ZHIPUAI_* vars entirely
```

---

### 5. WEBSEARCH ENDPOINT CONFUSION

#### Issue: Two different ways to do websearch
**Files:** Multiple

**Method 1: Via chat/completions with tools**
```python
# What we're doing now
tools = [{"type": "web_search", "web_search": {...}}]
response = client.chat.completions.create(model="glm-4.5-flash", tools=tools)
# ❌ HANGS with glm-4.5-flash
# ✅ WORKS with glm-4-plus
```

**Method 2: Via dedicated /web_search endpoint**
```python
# glm_web_search tool
POST https://api.z.ai/api/paas/v4/web_search
# ✅ ALWAYS WORKS
```

**Problem:**
- We're using Method 1 for workflow tools (analyze, etc.)
- Method 1 only works with certain models
- No fallback when model doesn't support it
- Results in infinite hangs

**Fix:** Either:
1. Only enable websearch for models that support it
2. Use dedicated /web_search endpoint instead
3. Add fallback logic

---

### 6. ZHIPUAI SDK VERSION MISMATCH (FIXED)

#### Issue: Old SDK version installed
**Status:** ✅ FIXED

**Was:** zhipuai==1.0.7 (old v1 SDK, no ZhipuAI class)  
**Now:** zhipuai==2.1.5 (new v2 SDK, has ZhipuAI class)

**Fix Applied:** `pip install --upgrade "zhipuai>=2.1.0"`

---

### 7. DUPLICATE WATCHER_TIMEOUT_SECS

#### Issue: Defined twice in .env
**File:** `.env`

**Lines 28 and 106:**
```env
# Line 28
WATCHER_TIMEOUT_SECS=60

# Line 106
WATCHER_TIMEOUT_SECS=30
```

**Problem:** Which one is used? Confusing!

**Fix:** Keep only one:
```env
# Line 28 (in GLM WATCHER CONFIGURATION section)
WATCHER_TIMEOUT_SECS=60
```

---

## 🚨 CRITICAL DISCOVERY - WORKFLOW TOOLS BYPASS WEBSEARCH ADAPTER!

**File:** `tools/workflow/expert_analysis.py` line 342
**Issue:** Workflow tools pass `use_websearch` DIRECTLY to provider, bypassing our websearch adapter fix!

```python
# Line 342 in expert_analysis.py
return provider.generate_content(
    prompt=prompt,
    model_name=model_name,
    system_prompt=system_prompt,
    temperature=validated_temperature,
    thinking_mode=self.get_request_thinking_mode(request),
    use_websearch=self.get_request_use_websearch(request),  # ❌ BYPASSES ADAPTER!
    images=list(set(self.consolidated_findings.images)) if self.consolidated_findings.images else None,
)
```

**Problem:**
- Simple tools (chat, etc.) use `build_websearch_provider_kwargs()` which we fixed ✅
- Workflow tools (analyze, debug, etc.) call `provider.generate_content()` directly ❌
- Our websearch adapter fix is NEVER CALLED for workflow tools!
- This is why analyze still hangs even after our fixes!

**The Fix:**
Workflow tools need to either:
1. Use the websearch adapter before calling provider.generate_content()
2. OR check model support directly before passing use_websearch
3. OR convert use_websearch to tools parameter using the adapter

---

## 📋 COMPLETE FIX CHECKLIST

### Priority 1: Critical (Breaks functionality)

- [ ] **Fix glm_config.py model list**
  - [ ] Add `glm-4-plus` model
  - [ ] Add `glm-4-flash` model
  - [ ] Remove incorrect alias from glm-4.5-flash
  - [ ] Add `supports_websearch` field to ModelCapabilities
  - [ ] Mark which models support websearch

- [ ] **Fix websearch hanging issue**
  - [ ] Disable websearch for models that don't support it
  - [ ] OR switch to dedicated /web_search endpoint
  - [ ] OR use glm-4-plus for expert analysis when websearch needed

- [ ] **Clean up .env**
  - [ ] Remove duplicate WATCHER_TIMEOUT_SECS
  - [ ] Decide on GLM_* vs ZHIPUAI_* vars (pick one)
  - [ ] Document which URL is actually used

### Priority 2: High (Causes confusion)

- [ ] **Update test scripts**
  - [ ] Fix model names in test_glm_websearch.py
  - [ ] Fix model names in test_glm_all_configs.py
  - [ ] Ensure tests use models that exist in config

- [ ] **Add model validation**
  - [ ] Validate model names at startup
  - [ ] Warn if test uses non-existent model
  - [ ] Fail fast instead of hanging

### Priority 3: Medium (Technical debt)

- [ ] **Documentation**
  - [ ] Document which models support websearch
  - [ ] Document z.ai vs bigmodel.cn differences
  - [ ] Document model capabilities clearly

- [ ] **Code cleanup**
  - [ ] Remove unused ZHIPUAI_* vars if not needed
  - [ ] Consolidate base URL logic
  - [ ] Add comments explaining model choices

---

## 🎯 IMMEDIATE ACTION PLAN

### Step 1: Fix Model Configuration (5 min)
1. Add missing models to glm_config.py
2. Remove incorrect aliases
3. Add supports_websearch field

### Step 2: Fix Websearch Issue (10 min)
1. Check which models support websearch
2. Either disable for unsupported models
3. OR switch expert analysis to use glm-4-plus

### Step 3: Clean .env (5 min)
1. Remove duplicate WATCHER_TIMEOUT_SECS
2. Simplify GLM_* vs ZHIPUAI_* vars
3. Add comments

### Step 4: Test (10 min)
1. Restart daemon
2. Run analyze test
3. Verify it completes without hanging

---

## 📊 ROOT CAUSE SUMMARY

**Why workflow tools hang:**
1. zhipuai SDK was old version (FIXED ✅)
2. glm-4.5-flash doesn't support websearch tools
3. SDK hangs waiting for response that never comes
4. No timeout on SDK calls
5. No validation that model supports websearch

**Why tests reference wrong models:**
1. Test scripts copied from examples
2. Examples use glm-4-plus (which works)
3. Our config doesn't have glm-4-plus
4. No validation catches this mismatch

**Why configuration is messy:**
1. Multiple sources of truth (.env, glm_config.py, test scripts)
2. No central validation
3. Legacy vars (ZHIPUAI_*) not cleaned up
4. Aliases used incorrectly

---

**Status:** Issues documented, ready for systematic fixes  
**Next:** Fix glm_config.py first, then test

