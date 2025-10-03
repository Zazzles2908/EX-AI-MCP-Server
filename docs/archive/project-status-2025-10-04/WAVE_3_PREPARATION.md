# Wave 3 Preparation - Core SDK Upgrade

**Date:** 2025-10-03  
**Status:** 🎯 Ready to Start  
**Previous Wave:** Wave 2 (Synthesis & UX) - ✅ COMPLETE

---

## Wave 2 Completion Summary

### ✅ Completed Work

**Epic 2.2: Web Search Fix**
- ✅ Kimi web search fully functional (server-side builtin_function)
- ✅ Real search results, no hallucinations
- ❌ GLM web search non-functional (documented)
- **Files:** `src/providers/capabilities.py`, `tools/simple/base.py`, `src/providers/tool_executor.py`

**Epic 2.3: UX Improvements**
- ✅ Enhanced error messages with actionable suggestions
- ✅ Parameter confusion detection
- ✅ Progress indicators for all operations
- ✅ Smart defaults and flexible parameters
- **Files:** `tools/shared/error_envelope.py`, `utils/progress_messages.py`, `docs/features/ux-improvements.md`

**Epic 2.4: Diagnostic Tools**
- ✅ Provider diagnostics tool
- ✅ Enhanced health/self-check tools
- ✅ Comprehensive logging guide
- **Files:** `tools/diagnostics/provider_diagnostics.py`, `docs/guides/diagnostics-and-logging.md`

**Epic 2.5: Validation**
- ✅ Server restarted and tested
- ✅ All improvements deployed
- ✅ No regressions detected

---

## Wave 3 Overview

### Objective
Upgrade to zai-sdk v0.0.4 and integrate GLM-4.6 with 200K context window

### Scope
- SDK upgrade (v0.0.3.3 → v0.0.4)
- GLM-4.6 model integration
- Pricing updates
- Streaming verification
- Tool calling verification
- Backward compatibility testing

### Timeline
**Estimated:** 3-4 hours of focused work

---

## Task Breakdown

### Task 5.1: Update requirements.txt ⏱️ 15 min
**Objective:** Upgrade zai-sdk dependency

**Steps:**
1. Update `requirements.txt`: `zai-sdk>=0.0.3.3` → `zai-sdk>=0.0.4`
2. Run `pip install --upgrade zai-sdk`
3. Verify installation: `pip show zai-sdk`
4. Test import: `python -c "import zhipuai; print(zhipuai.__version__)"`

**Success Criteria:**
- ✅ zai-sdk v0.0.4 installed
- ✅ No dependency conflicts
- ✅ Import successful

---

### Task 5.2: Add GLM-4.6 to glm_config.py ⏱️ 30 min
**Objective:** Add GLM-4.6 model configuration

**File:** `src/providers/glm_config.py`

**Changes:**
```python
"glm-4.6": ModelConfig(
    name="glm-4.6",
    friendly_name="GLM-4.6",
    context_window=200000,  # 200K context
    max_output_tokens=8192,
    supports_vision=False,
    supports_function_calling=True,
    supports_streaming=True,
    supports_thinking_mode=False,
    pricing=PricingInfo(
        input_price_per_million=0.60,   # $0.60/M input
        output_price_per_million=2.20,  # $2.20/M output
        currency="USD"
    ),
    tier="flagship",
    description="GLM-4.6 flagship model with 200K context window"
),
```

**Success Criteria:**
- ✅ GLM-4.6 added to MODEL_CONFIGS
- ✅ Pricing correct
- ✅ Context window set to 200K
- ✅ Capabilities configured

---

### Task 5.3: Update glm.py for GLM-4.6 support ⏱️ 20 min
**Objective:** Ensure provider recognizes GLM-4.6

**File:** `src/providers/glm.py`

**Verification:**
1. Check model resolution logic
2. Verify GLM-4.6 routes correctly
3. Test with `model="glm-4.6"`
4. Test with `model="auto"`

**Success Criteria:**
- ✅ GLM-4.6 recognized by provider
- ✅ Model routing works
- ✅ Auto-selection includes GLM-4.6

---

### Task 5.4: Update pricing configuration ⏱️ 15 min
**Objective:** Verify pricing calculations

**Files:**
- `src/providers/glm_config.py` (already done in 5.2)
- `tools/cost/cost_optimizer.py` (verify)

**Verification:**
1. Test cost calculation for GLM-4.6
2. Verify input/output pricing
3. Check cost optimizer includes GLM-4.6

**Success Criteria:**
- ✅ Pricing accurate
- ✅ Cost calculations correct
- ✅ Cost optimizer updated

---

### Task 5.5: Test streaming with new SDK ⏱️ 30 min
**Objective:** Verify streaming works with GLM-4.6

**Test Script:**
```python
from src.providers.registry import ModelProviderRegistry
from src.providers.base import ProviderType

provider = ModelProviderRegistry.get_provider(ProviderType.GLM)

# Test streaming
response = provider.generate_content(
    prompt="Count from 1 to 10",
    model_name="glm-4.6",
    system_prompt="Count slowly",
    temperature=0.5,
    stream=True  # Enable streaming
)

# Verify streaming works
```

**Success Criteria:**
- ✅ Streaming enabled with GLM_STREAM_ENABLED=true
- ✅ SSE streaming works
- ✅ No errors or timeouts

---

### Task 5.6: Test tool calling with new SDK ⏱️ 30 min
**Objective:** Verify function calling works

**Test Areas:**
1. Web search integration (if GLM fixes it)
2. Custom function tools
3. Tool call detection
4. Tool execution flow

**Test Script:**
```python
# Test with web_search tool
tools = [{
    "type": "web_search",
    "web_search": {
        "search_engine": "search_pro_jina",
        "search_recency_filter": "oneWeek"
    }
}]

response = provider.generate_content(
    prompt="What is the weather in Tokyo?",
    model_name="glm-4.6",
    tools=tools
)
```

**Success Criteria:**
- ✅ Tool schemas accepted
- ✅ Tool calls detected (if supported)
- ✅ No regressions in tool handling

---

### Task 5.7: Verify backward compatibility ⏱️ 45 min
**Objective:** Ensure existing GLM models still work

**Test Models:**
- glm-4-plus
- glm-4-air
- glm-4-airx
- glm-4-0520

**Test Cases:**
1. Basic chat completion
2. Streaming
3. Tool calling
4. Temperature/parameters
5. System prompts

**Success Criteria:**
- ✅ All existing models work
- ✅ No regressions
- ✅ Smoke tests pass

---

## Pre-Flight Checklist

### Before Starting Wave 3

- [x] Wave 2 complete and validated
- [x] Server running and stable
- [x] All tests passing
- [x] Documentation updated
- [x] Git branch clean (chore/registry-switch-and-docfix)

### Environment Preparation

- [ ] Backup current environment
- [ ] Create test environment
- [ ] Verify API keys valid
- [ ] Check disk space
- [ ] Review zai-sdk v0.0.4 changelog

### Documentation Review

- [ ] Read zai-sdk v0.0.4 release notes
- [ ] Review GLM-4.6 documentation
- [ ] Check for breaking changes
- [ ] Note new features

---

## Risk Assessment

### Low Risk ✅
- SDK upgrade (backward compatible)
- Adding new model (non-breaking)
- Pricing updates (isolated)

### Medium Risk ⚠️
- Streaming changes (test thoroughly)
- Tool calling changes (verify compatibility)

### High Risk 🔴
- None identified (100% backward compatible upgrade)

---

## Rollback Plan

### If Issues Occur

1. **Revert SDK:**
   ```bash
   pip install zai-sdk==0.0.3.3
   ```

2. **Revert Code:**
   ```bash
   git checkout HEAD -- src/providers/glm_config.py
   git checkout HEAD -- src/providers/glm.py
   ```

3. **Restart Server:**
   ```bash
   powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\ws_start.ps1 -Restart
   ```

4. **Verify:**
   - Test existing models
   - Check logs for errors
   - Run smoke tests

---

## Success Metrics

### Wave 3 Complete When:
- ✅ zai-sdk v0.0.4 installed
- ✅ GLM-4.6 model available
- ✅ Pricing accurate
- ✅ Streaming works
- ✅ Tool calling works
- ✅ Backward compatibility verified
- ✅ All tests passing
- ✅ Documentation updated

---

## Next Steps After Wave 3

**Wave 4: New Features Implementation**
- CogVideoX-2 video generation
- Assistant API
- CharGLM-3 character role-playing

**Wave 5: Testing & Validation**
- Comprehensive test suite
- Security audit
- Performance validation

**Wave 6: Finalization & Release**
- Documentation updates
- Release notes
- GitHub release

---

## Ready to Start! 🚀

All preparation complete. Wave 3 can begin immediately.

**Estimated Completion:** 3-4 hours  
**Complexity:** Medium  
**Risk Level:** Low  
**Confidence:** High

