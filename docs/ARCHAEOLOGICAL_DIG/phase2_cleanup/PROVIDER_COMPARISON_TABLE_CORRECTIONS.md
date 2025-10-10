# PROVIDER COMPARISON TABLE CORRECTIONS
**Date:** 2025-10-11 (11th October 2025, Friday)  
**Status:** 🚨 CRITICAL INACCURACIES FOUND  
**Investigator:** User + Agent

---

## 🎯 INVESTIGATION SUMMARY

The user identified critical inaccuracies in the Provider Comparison Table found in:
- `docs/ARCHAEOLOGICAL_DIG/phase2_connections/PROVIDER_INTEGRATION_MAP.md` (line 579)
- `docs/system-reference/02-provider-architecture.md` (line 15)

---

## 🔍 FINDINGS

### 1. ✅ Kimi File Upload - CONFIRMED WORKING

**Test:** Uploaded 3 files via chat tool with `model=kimi-k2-0905-preview`

**Result:** ✅ SUCCESS
- All 3 files uploaded successfully
- Kimi read and summarized file contents
- Parallel upload working correctly
- Chat tool CAN use Kimi file upload intuitively via `files` parameter

**Table Status:** ✅ CORRECT

---

### 2. ✅ GLM File Upload - CONFIRMED WORKING (TABLE WAS WRONG!)

**Test:** Uploaded 1 file via chat tool with `model=glm-4.6`

**Result:** ✅ SUCCESS
- File uploaded successfully
- GLM read and summarized file contents
- GLM CAN upload and keep files!

**Table Claim:** "✅ Yes (agent purpose)"
**Reality:** ✅ CORRECT - GLM supports file upload

**Table Status:** ✅ CORRECT (but documentation elsewhere claims GLM can't keep files - THIS IS WRONG)

---

### 3. ❌ GLM Thinking Mode - TABLE IS WRONG!

**Table Claim:** "❌ No"

**Reality:** ✅ GLM SUPPORTS THINKING MODE

**Evidence from Code:**
```python
# src/providers/glm_config.py
"glm-4.6": ModelCapabilities(
    supports_extended_thinking=True,  # Line 31
    description="GLM 4.6 flagship with 200K context, web search, thinking mode",
),
"glm-4.5": ModelCapabilities(
    supports_extended_thinking=True,  # Line 57
    description="GLM 4.5 hybrid reasoning model with thinking mode and web search",
),
"glm-4.5-air": ModelCapabilities(
    supports_extended_thinking=True,  # Line 70
    description="GLM 4.5 Air - efficient hybrid reasoning with thinking mode",
),
```

**Models with Thinking Mode:**
- ✅ glm-4.6
- ✅ glm-4.5
- ✅ glm-4.5-air
- ❌ glm-4.5-flash (does NOT support thinking)
- ❌ glm-4.5v (does NOT support thinking)

**Table Status:** ❌ INCORRECT - Should be "✅ Yes (glm-4.6, glm-4.5, glm-4.5-air)"

---

### 4. ❌ Kimi Web Search - TABLE IS WRONG!

**Table Claim:** "❌ No"

**Reality:** ✅ KIMI SUPPORTS WEB SEARCH

**Evidence from Code:**
```python
# src/providers/capabilities.py (lines 42-57)
class KimiCapabilities(ProviderCapabilitiesBase):
    def supports_websearch(self) -> bool:
        return os.getenv("KIMI_ENABLE_INTERNET_SEARCH", "true").strip().lower() == "true"
    
    def get_websearch_tool_schema(self, config: Dict[str, Any]) -> WebSearchSchema:
        # Kimi supports builtin_function for SERVER-SIDE web search
        tools: list[dict] = [{
            "type": "builtin_function",
            "function": {"name": "$web_search"}
        }]
        return WebSearchSchema(tools=tools, tool_choice="auto")
```

**Documentation:**
- `docs/system-reference/features/web-search.md` confirms Kimi web search
- `docs/system-reference/api/web-search.md` documents Kimi `$web_search` function
- Environment variable: `KIMI_ENABLE_INTERNET_SEARCH=true`

**Table Status:** ❌ INCORRECT - Should be "✅ Yes ($web_search builtin)"

---

## 📊 CORRECTED PROVIDER COMPARISON TABLE

| Feature | Kimi Provider | GLM Provider |
|---------|---------------|--------------|
| **Base Class** | OpenAICompatibleProvider | ModelProvider |
| **API Style** | OpenAI-compatible | Native GLM API |
| **SDK** | OpenAI SDK | ZhipuAI SDK + HTTP fallback |
| **Base URL** | api.moonshot.ai/v1 | api.z.ai/api/paas/v4 |
| **Context Caching** | ✅ Yes (X-Kimi-Context-Cache) | ❌ No |
| **Idempotency** | ✅ Yes (X-Idempotency-Key) | ❌ No |
| **File Upload** | ✅ Yes (file-extract, assistants) | ✅ Yes (agent purpose) |
| **Web Search** | ✅ Yes ($web_search builtin) | ✅ Yes (native support) |
| **Vision Models** | ✅ Yes (kimi-k2-0905-preview, kimi-k2-0711-preview) | ✅ Yes (glm-4.5v) |
| **Thinking Mode** | ✅ Yes (kimi-thinking-preview) | ✅ Yes (glm-4.6, glm-4.5, glm-4.5-air) |
| **Default Timeout** | 300s | Standard HTTP timeout |
| **Model Count** | 14 models | 5 models |

---

## 🔧 CHANGES REQUIRED

### Files to Update:

1. **docs/ARCHAEOLOGICAL_DIG/phase2_connections/PROVIDER_INTEGRATION_MAP.md** (line 579-594)
   - Fix Web Search row for Kimi: ❌ No → ✅ Yes ($web_search builtin)
   - Fix Thinking Mode row for GLM: ❌ No → ✅ Yes (glm-4.6, glm-4.5, glm-4.5-air)

2. **docs/system-reference/02-provider-architecture.md** (line 15+)
   - Fix Web Search row for Kimi: ❌ No → ✅ Yes ($web_search builtin)
   - Fix Thinking Mode row for GLM: ❌ No → ✅ Yes (glm-4.6, glm-4.5, glm-4.5-air)

3. **Any other documentation claiming:**
   - "GLM can't keep files" → WRONG, GLM supports file upload
   - "Kimi doesn't support web search" → WRONG, Kimi supports $web_search
   - "GLM doesn't support thinking mode" → WRONG, 3 GLM models support thinking

---

## 🚨 CLAUDE APPLICATION EXAI ISSUE

**User Report:** "Claude application is having difficulty currently to actually use exai"

**Investigation Needed:**
1. Check if Claude app can connect to WebSocket daemon
2. Check if Claude app has correct MCP configuration
3. Check server logs for connection errors from Claude
4. Verify Claude app is using correct port (8079)
5. Check if there are any authentication issues

**Recommendation:** Create separate investigation document for Claude app connectivity issues

---

## ✅ ACTION ITEMS

### Immediate:
- [ ] Update PROVIDER_INTEGRATION_MAP.md table
- [ ] Update 02-provider-architecture.md table
- [ ] Search for and correct all documentation claiming GLM can't keep files
- [ ] Search for and correct all documentation claiming Kimi doesn't support web search
- [ ] Search for and correct all documentation claiming GLM doesn't support thinking mode

### Investigation:
- [ ] Investigate Claude application EXAI connectivity issues
- [ ] Create diagnostic script to test Claude app connection
- [ ] Check server logs for Claude-specific errors

---

**Status:** 🚨 CRITICAL DOCUMENTATION ERRORS IDENTIFIED  
**Priority:** HIGH - These errors affect user understanding of system capabilities  
**Next Steps:** Update all affected documentation files


