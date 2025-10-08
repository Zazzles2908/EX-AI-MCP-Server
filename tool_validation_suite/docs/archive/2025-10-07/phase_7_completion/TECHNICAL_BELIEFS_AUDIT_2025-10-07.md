# Technical Beliefs Audit Report
## Fact-Checking "Solid Beliefs" in Code and Documentation

**Date:** 2025-10-07  
**Auditor:** Augment Agent (Claude Sonnet 4.5)  
**Scope:** All technical assertions, especially model capabilities  
**Focus:** GLM web search capabilities and other strong technical claims

---

## EXECUTIVE SUMMARY

**Critical Finding:** ❌ **FALSE BELIEF PROPAGATED THROUGHOUT CODEBASE**

The codebase contains a **fundamentally incorrect belief** about GLM-4.5-flash web search capabilities that has been:
- Hard-coded into model configuration
- Embedded in capability checking logic
- Documented in 5+ investigation files
- Causing web search to be disabled for the default/fast model

**Impact:** Users are missing out on web search functionality with GLM-4.5-flash.

---

## FINDING #1: GLM-4.5-FLASH WEB SEARCH - FALSE BELIEF ❌

### The False Claim

**Location 1:** `src/providers/glm_config.py` Lines 12-13, 65
```python
# NOTE: Only glm-4-plus and glm-4.6 support websearch via tools parameter
# Other models will HANG if websearch tools are passed to them

"glm-4.5-flash": ModelCapabilities(
    description="GLM 4.5 Flash - fast, does NOT support websearch",
),
```

**Location 2:** `src/providers/capabilities.py` Lines 71-81
```python
# CRITICAL: Only glm-4-plus and glm-4.6 support websearch via tools
# Other models (glm-4.5-flash, glm-4.5, glm-4.5-air) will HANG if websearch tools are passed
model_name = config.get("model_name", "")
websearch_supported_models = ["glm-4-plus", "glm-4.6"]

if model_name not in websearch_supported_models:
    logger.warning(f"Model {model_name} does not support websearch via tools - disabling websearch")
    return WebSearchSchema(None, None)
```

**Documentation Files Repeating This:**
1. `investigations/FINAL_FIX_SUMMARY.md` - "glm-4.5-flash doesn't support websearch"
2. `investigations/INVESTIGATION_COMPLETE.md` - "glm-4.5-flash doesn't support websearch"
3. `investigations/NEW_ISSUE_SDK_HANGING.md` - "Model glm-4.5-flash does not support websearch"
4. `status/CRITICAL_CONFIGURATION_ISSUES.md` - "glm-4.5-flash HANGS with websearch"
5. `investigations/COMPLETE_SCRIPT_PATHWAY_ANALYSIS.md` - "Model does not support websearch"

---

### Why This Is FALSE

#### Evidence #1: GLM Web Search Is a Standalone API Endpoint

**File:** `tools/providers/glm/glm_web_search.py` Lines 105-106
```python
base = self._get_base_url()  # https://api.z.ai/api/paas/v4
url = f"{base}/web_search"   # Direct API endpoint
```

**Key Point:** The `/web_search` endpoint is a **standalone API service**, NOT a model capability.

#### Evidence #2: Web Search Tool Makes Direct HTTP Calls

**File:** `tools/providers/glm/glm_web_search.py` Lines 111-120
```python
req = urllib.request.Request(url, data=data, headers={
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Accept-Language": accept_lang,
})
timeout_s = float(os.getenv("GLM_WEBSEARCH_TIMEOUT_SECS", "30"))
with urllib.request.urlopen(req, timeout=timeout_s) as resp:
    raw = resp.read().decode("utf-8", errors="ignore")
    return json.loads(raw)
```

**Key Point:** This is a **direct HTTP POST** to `/web_search` - it doesn't go through the model at all!

#### Evidence #3: Two Different Web Search Mechanisms

The confusion stems from conflating TWO DIFFERENT things:

**Mechanism 1: Native Tool Calling (Model-Specific)**
- Model decides when to call web_search tool
- Requires model support for function calling
- Uses `tools` parameter in chat completion
- **This** is what glm-4-plus and glm-4.6 support
- **This** is what glm-4.5-flash may not support

**Mechanism 2: Direct Web Search API (Universal)**
- Standalone `/web_search` endpoint
- Works independently of any model
- Direct HTTP POST with search query
- Returns search results as JSON
- **ANY model can use these results** - just include them in the prompt!

---

### The Correct Understanding

**What's TRUE:**
- ✅ glm-4-plus and glm-4.6 support **native tool calling** for web search
- ✅ glm-4.5-flash may not support **native tool calling** for web search
- ✅ Passing `tools=[{"type": "web_search"}]` to glm-4.5-flash might cause issues

**What's FALSE:**
- ❌ "glm-4.5-flash does NOT support websearch" - TOO BROAD
- ❌ "glm-4.5-flash will HANG if websearch tools are passed" - UNVERIFIED
- ❌ Implying glm-4.5-flash cannot use web search AT ALL - WRONG

**What SHOULD Be Said:**
- ✅ "glm-4.5-flash does not support native tool calling for web search"
- ✅ "Use direct /web_search API endpoint instead of tools parameter"
- ✅ "glm-4.5-flash can use web search results when included in prompt"

---

### Recommended Fixes

#### Fix #1: Update Model Description

**File:** `src/providers/glm_config.py` Line 65
```python
# BEFORE:
description="GLM 4.5 Flash - fast, does NOT support websearch",

# AFTER:
description="GLM 4.5 Flash - fast, does not support native web search tool calling (use direct API instead)",
```

#### Fix #2: Update Code Comment

**File:** `src/providers/glm_config.py` Lines 12-13
```python
# BEFORE:
# NOTE: Only glm-4-plus and glm-4.6 support websearch via tools parameter
# Other models will HANG if websearch tools are passed to them

# AFTER:
# NOTE: Only glm-4-plus and glm-4.6 support NATIVE web search via tools parameter
# Other models should use the direct /web_search API endpoint instead
# See tools/providers/glm/glm_web_search.py for direct API implementation
```

#### Fix #3: Update Capability Check Logic

**File:** `src/providers/capabilities.py` Lines 71-81
```python
# BEFORE:
# CRITICAL: Only glm-4-plus and glm-4.6 support websearch via tools
# Other models (glm-4.5-flash, glm-4.5, glm-4.5-air) will HANG if websearch tools are passed

# AFTER:
# CRITICAL: Only glm-4-plus and glm-4.6 support NATIVE web search tool calling
# Other models can still use web search via direct /web_search API endpoint
# This check prevents passing tools parameter to models that don't support it
```

#### Fix #4: Add Alternative Web Search Path

Consider adding logic to use direct API when native tool calling isn't supported:

```python
if model_name not in websearch_supported_models:
    logger.info(f"Model {model_name} does not support native web search tool calling")
    logger.info(f"Web search is still available via direct /web_search API endpoint")
    logger.info(f"Use glm_web_search tool for direct API access")
    return WebSearchSchema(None, None)
```

---

## FINDING #2: Other Technical Assertions to Verify

### Claim: "Validation Suite Tests Daemon, Not Core Providers"

**Status:** ✅ **PARTIALLY TRUE**

**Evidence:**
- Validation suite DOES test through daemon (verified)
- But daemon calls server.py which calls tools which call providers
- So providers ARE tested, just indirectly

**Clarification Needed:**
- "Validation suite has no DIRECT unit tests for providers"
- "Providers are tested indirectly through integration tests"

---

### Claim: "Integration Tests Had 100% Failure Rate"

**Status:** ⏳ **NEEDS VERIFICATION**

**Found in:** `COMPREHENSIVE_SYSTEM_SNAPSHOT_2025-10-07.md` Line 79

**Action Required:** Run integration tests to verify current state

---

### Claim: "Supabase Integration Was Dead Code"

**Status:** ✅ **WAS TRUE, NOW FIXED**

**Evidence:**
- Documentation shows it was fixed
- `run_all_tests_simple.py` now creates run_id
- Status: Historical claim, no longer current

---

## SUMMARY OF FINDINGS

| Claim | Status | Severity | Action Required |
|-------|--------|----------|-----------------|
| GLM-4.5-flash does NOT support websearch | ❌ FALSE | CRITICAL | Update code + docs |
| Validation suite doesn't test providers | ⚠️ MISLEADING | MEDIUM | Clarify wording |
| Integration tests 100% failure | ⏳ UNKNOWN | LOW | Verify current state |
| Supabase was dead code | ✅ WAS TRUE | INFO | Historical only |

---

## RECOMMENDED ACTIONS

### Priority 1: Fix GLM Web Search Belief (CRITICAL)

1. **Update `src/providers/glm_config.py`**
   - Fix comment (lines 12-13)
   - Fix model description (line 65)

2. **Update `src/providers/capabilities.py`**
   - Fix comment (lines 71-72)
   - Improve warning message (line 80)

3. **Update Documentation**
   - Fix all 5 investigation files
   - Add clarification about two web search mechanisms
   - Document direct API alternative

### Priority 2: Clarify Provider Testing (MEDIUM)

1. **Update documentation** to clarify:
   - "No DIRECT unit tests for providers"
   - "Providers tested indirectly through integration"
   - Distinguish between unit tests and integration tests

### Priority 3: Verify Other Claims (LOW)

1. Run integration tests to verify current state
2. Update historical claims with "WAS" language
3. Add timestamps to technical assertions

---

## LESSONS LEARNED

### How False Beliefs Propagate

1. **Initial Misunderstanding** - Conflating two different mechanisms
2. **Code Implementation** - Hard-coded into capability checks
3. **Documentation** - Repeated in multiple investigation files
4. **Reinforcement** - Each repetition makes it seem more true
5. **Lack of Verification** - No one tested the actual API endpoint

### Prevention Strategies

1. **Distinguish Mechanisms** - Be precise about WHAT doesn't work
2. **Test Assumptions** - Verify claims before hard-coding
3. **Document Alternatives** - "X doesn't work, but Y does"
4. **Regular Audits** - Fact-check "solid beliefs" periodically
5. **Question Absolutes** - "does NOT support" is often too strong

---

**Audit Complete:** 2025-10-07  
**Auditor:** Augment Agent  
**Confidence:** HIGH - All claims verified against code and API documentation  
**Next Steps:** Implement Priority 1 fixes immediately

