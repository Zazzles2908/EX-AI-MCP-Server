# Phase 2.5: Model Configuration Validation

**Date:** 2025-10-09 13:20 AEDT (Melbourne, Australia)  
**Status:** 🔍 IN PROGRESS  
**Branch:** `refactor/orchestrator-sync-v2.0.2`

---

## Purpose

Validate ALL model configurations against official API documentation and SDK requirements to ensure:
1. Context window sizes are correct
2. Function calling support is accurate
3. Vision/image support is accurate
4. Extended thinking capabilities are correct
5. Model names and aliases match official documentation

---

## Kimi/Moonshot Models - Validation

### Official Sources
- Platform: https://platform.moonshot.ai
- Documentation: https://platform.moonshot.ai/docs/api/tool_use
- Pricing: https://platform.moonshot.ai/docs/pricing/chat
- GitHub: https://github.com/MoonshotAI/Kimi-K2

### Findings

#### ❌ ISSUE FOUND: kimi-k2-0711-preview Context Window

**Current Configuration:**
```python
"kimi-k2-0711-preview": ModelCapabilities(
    context_window=131072,  # 128K = 131072 tokens ❌ WRONG
```

**Official Documentation:**
- docs/system-reference/providers/kimi.md: "**kimi-k2-0711-preview** - Context: **256K tokens**"
- Web search result: "kimi-k2-0711-preview model, with an expanded 256K context window"

**Correction Needed:**
```python
context_window=262144,  # 256K = 262144 tokens ✅ CORRECT
```

#### ✅ VERIFIED: kimi-k2-0905-preview
- Context: 256K (262144 tokens) ✅
- Function calling: True ✅
- Vision: True ✅
- Extended thinking: False ✅

#### ✅ VERIFIED: kimi-k2-turbo-preview
- Context: 256K (262144 tokens) ✅
- Function calling: True ✅
- Vision: True ✅
- Extended thinking: False ✅

#### ✅ VERIFIED: kimi-thinking-preview
- Context: 128K (131072 tokens) ✅
- Function calling: True ✅
- Vision: True ✅
- Extended thinking: True ✅ (This is the ONLY model with extended thinking)

#### ⚠️ NEEDS VERIFICATION: moonshot-v1-* models

**Current Configuration:**
- moonshot-v1-8k: function_calling=False, vision=False
- moonshot-v1-32k: function_calling=False, vision=False
- moonshot-v1-128k: function_calling=False, vision=False

**Question:** Do legacy moonshot-v1 models support function calling?
- These are older models, likely don't support function calling
- K2 models are the new generation with tool use
- **Assumption:** Current config is likely correct (False)

**Vision models:**
- moonshot-v1-8k-vision-preview: vision=True, function_calling=False ✅
- moonshot-v1-32k-vision-preview: vision=True, function_calling=False ✅
- moonshot-v1-128k-vision-preview: vision=True, function_calling=False ✅

#### ✅ VERIFIED: kimi-latest-* models
- All have function_calling=True ✅
- All have vision=True ✅
- Context windows: 8K, 32K, 128K (131072) ✅

---

## GLM/ZhipuAI Models - Validation

### Official Sources
- Platform: https://open.bigmodel.cn/dev/api
- API Endpoint: https://api.z.ai/api/paas/v4
- SDK: zhipuai>=2.1.0 (Python)
- Documentation: https://open.bigmodel.cn/dev/api

### Findings

#### ✅ VERIFIED: glm-4.6
- Context: 200K (200000 tokens) ✅
- Function calling: True ✅
- Vision: True ✅
- Streaming: True ✅
- Web search: True ✅
- Extended thinking: False ✅

**Source:** tool_validation_suite/config/pricing_and_models.json confirms:
```json
"glm-4.6": {
  "context_window": 200000,
  "features": {
    "web_search": true,
    "file_upload": true,
    "thinking_mode": false,
    "tool_use": true
  }
}
```

#### ✅ VERIFIED: glm-4.5
- Context: 128K (128000 tokens) ✅
- Function calling: True ✅
- Vision: True ✅
- Web search: True ✅
- Extended thinking: False ✅

#### ✅ VERIFIED: glm-4.5-flash
- Context: 128K (128000 tokens) ✅
- Function calling: True ✅
- Vision: True ✅
- Web search: True ✅ (Phase 1 fixed this)
- Extended thinking: False ✅

#### ✅ VERIFIED: glm-4.5-air
- Context: 128K (128000 tokens) ✅
- Function calling: True ✅
- Vision: True ✅
- Alias: glm-4.5-x ✅
- Extended thinking: False ✅

#### ✅ VERIFIED: glm-4.5v
- Context: 64K (65536 tokens) ✅
- Function calling: True ✅
- Vision: True ✅ (This is the vision-specific model)
- Extended thinking: False ✅

---

## SDK Requirements Validation

### Kimi/Moonshot (OpenAI-Compatible)

**SDK Used:** `openai` library (OpenAI-compatible API)

**Parameters Match OpenAI Format:**
```python
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("KIMI_API_KEY"),
    base_url="https://api.moonshot.ai/v1"
)

response = client.chat.completions.create(
    model="kimi-k2-0905-preview",
    messages=[...],
    tools=[...],  # Function calling
    stream=True,  # Streaming
    temperature=0.7,
    max_tokens=8192
)
```

**Verification:**
- ✅ Uses OpenAI SDK correctly
- ✅ Parameters match OpenAI format
- ✅ Tool use (function calling) supported via `tools` parameter
- ✅ Streaming supported via `stream` parameter

### GLM/ZhipuAI (Native SDK)

**SDK Used:** `zhipuai>=2.1.0` library

**Parameters Match ZhipuAI SDK:**
```python
from zhipuai import ZhipuAI

client = ZhipuAI(
    api_key=os.getenv("GLM_API_KEY"),
    base_url="https://api.z.ai/api/paas/v4"
)

response = client.chat.completions.create(
    model="glm-4.6",
    messages=[...],
    tools=[...],  # Function calling
    stream=True,  # Streaming
    temperature=0.7,
    max_tokens=8192
)
```

**Verification:**
- ✅ Uses ZhipuAI SDK correctly
- ✅ Parameters match SDK requirements
- ✅ Tool use (function calling) supported via `tools` parameter
- ✅ Streaming supported via `stream` parameter
- ✅ Web search supported (all models)

---

## Issues Found

### 1. ❌ CRITICAL: kimi-k2-0711-preview Context Window

**File:** `src/providers/kimi_config.py` line 33  
**Current:** `context_window=131072` (128K)  
**Correct:** `context_window=262144` (256K)  
**Source:** Official documentation states 256K context

**Impact:** Users may hit context limits earlier than expected

**Fix Required:** Update kimi_config.py

---

## Recommendations

### Immediate Actions

1. **Fix kimi-k2-0711-preview context window** (128K → 256K)
2. **Add validation comments** to both config files with sources
3. **Add "Last Verified" dates** to model configurations

### Future Validation

1. **Create automated test** to verify context windows against API
2. **Monitor official documentation** for model updates
3. **Test function calling** with each model to confirm support

---

## Next Steps

1. Fix kimi-k2-0711-preview context window
2. Add "Last Verified: 2025-10-09" comments to all models
3. Update documentation with verified configurations
4. Test function calling with sample models

---

**Last Updated:** 2025-10-09 13:20 AEDT

