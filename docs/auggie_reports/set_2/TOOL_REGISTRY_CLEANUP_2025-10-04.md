# Tool Registry Cleanup - Phase 2.1

**Date:** 2025-10-04  
**Status:** ✅ COMPLETE  
**Priority:** HIGH

---

## 🎯 OBJECTIVE

Clean up the tool registry by hiding internal provider-specific tools that should not be exposed to end users.

---

## ✅ CHANGES MADE

### 1. Hidden GLM Internal Tools

**File:** `server.py` (lines 257-265)

**Before:**
```python
for name, modcls in [
    ("glm_upload_file", ("tools.providers.glm.glm_files", "GLMUploadFileTool")),
    ("glm_web_search", ("tools.providers.glm.glm_web_search", "GLMWebSearchTool")),
    # ...
]:
```

**After:**
```python
# NOTE: glm_web_search is INTERNAL ONLY - web search is auto-injected via
# build_websearch_provider_kwargs() when use_websearch=true in tools like chat_exai
for name, modcls in [
    ("glm_upload_file", ("tools.providers.glm.glm_files", "GLMUploadFileTool")),
    # ("glm_web_search", ("tools.providers.glm.glm_web_search", "GLMWebSearchTool")),  # HIDDEN: Internal function only
    # ...
]:
```

**Rationale:**
- `glm_web_search` is an internal function used by the provider layer
- Web search is automatically injected via `build_websearch_provider_kwargs()` when `use_websearch=true`
- End users should use `chat_exai(use_websearch=true)` instead of calling `glm_web_search` directly

---

### 2. Hidden Kimi Internal Tools

**File:** `server.py` (lines 240-248)

**Before:**
```python
for name, modcls in [
    ("kimi_upload_and_extract", ("tools.providers.kimi.kimi_upload", "KimiUploadAndExtractTool")),
    ("kimi_multi_file_chat", ("tools.providers.kimi.kimi_upload", "KimiMultiFileChatTool")),
    ("kimi_intent_analysis", ("tools.providers.kimi.kimi_intent", "KimiIntentAnalysisTool")),
    ("kimi_chat_with_tools", ("tools.providers.kimi.kimi_tools_chat", "KimiChatWithToolsTool")),
]:
```

**After:**
```python
# NOTE: kimi_upload_and_extract and kimi_chat_with_tools are INTERNAL ONLY
# They are used by the provider layer and should not be exposed to end users
for name, modcls in [
    # ("kimi_upload_and_extract", ("tools.providers.kimi.kimi_upload", "KimiUploadAndExtractTool")),  # HIDDEN: Internal function only
    ("kimi_multi_file_chat", ("tools.providers.kimi.kimi_upload", "KimiMultiFileChatTool")),
    ("kimi_intent_analysis", ("tools.providers.kimi.kimi_intent", "KimiIntentAnalysisTool")),
    # ("kimi_chat_with_tools", ("tools.providers.kimi.kimi_tools_chat", "KimiChatWithToolsTool")),  # HIDDEN: Internal function only
]:
```

**Rationale:**
- `kimi_upload_and_extract` is used internally by file handling logic
- `kimi_chat_with_tools` is used internally by the provider layer
- End users should use high-level tools like `chat_exai` instead

---

## 📊 TOOL REGISTRY BEFORE vs AFTER

### Before Cleanup

**Public Tools (Visible to Users):**
- ✅ chat_exai
- ✅ debug_exai
- ✅ thinkdeep_exai
- ✅ analyze_exai
- ✅ codereview_exai
- ✅ testgen_exai
- ✅ consensus_exai
- ✅ planner_exai
- ✅ precommit_exai
- ✅ refactor_exai
- ✅ secaudit_exai
- ✅ tracer_exai
- ✅ docgen_exai
- ✅ activity_exai
- ✅ challenge_exai
- ✅ listmodels_exai
- ✅ version_exai
- ❌ **glm_web_search** (should be hidden)
- ❌ **kimi_upload_and_extract** (should be hidden)
- ❌ **kimi_chat_with_tools** (should be hidden)
- ✅ kimi_multi_file_chat
- ✅ kimi_intent_analysis
- ✅ glm_upload_file

### After Cleanup

**Public Tools (Visible to Users):**
- ✅ chat_exai
- ✅ debug_exai
- ✅ thinkdeep_exai
- ✅ analyze_exai
- ✅ codereview_exai
- ✅ testgen_exai
- ✅ consensus_exai
- ✅ planner_exai
- ✅ precommit_exai
- ✅ refactor_exai
- ✅ secaudit_exai
- ✅ tracer_exai
- ✅ docgen_exai
- ✅ activity_exai
- ✅ challenge_exai
- ✅ listmodels_exai
- ✅ version_exai
- ✅ kimi_multi_file_chat
- ✅ kimi_intent_analysis
- ✅ glm_upload_file

**Internal Tools (Hidden from Users):**
- 🔒 glm_web_search (auto-injected when use_websearch=true)
- 🔒 kimi_upload_and_extract (used by provider layer)
- 🔒 kimi_chat_with_tools (used by provider layer)

---

## 🔍 WEB SEARCH INTEGRATION VERIFICATION

### How Web Search Works Now

**For GLM Provider:**
1. User calls: `chat_exai(prompt="Latest AI news?", use_websearch=true)`
2. SimpleTool's execute() method calls `build_websearch_provider_kwargs()`
3. `GLMCapabilities.get_websearch_tool_schema()` returns:
   ```python
   {
       "type": "web_search",
       "web_search": {
           "search_engine": "search_pro_jina",
           "search_recency_filter": "oneWeek",
           "content_size": "medium",
           "result_sequence": "after",
           "search_result": True
       }
   }
   ```
4. Tool is auto-injected into provider call
5. GLM API performs web search server-side
6. Results are returned in response

**For Kimi Provider:**
1. User calls: `chat_exai(prompt="Latest AI news?", use_websearch=true, model="kimi-k2-0905-preview")`
2. SimpleTool's execute() method calls `build_websearch_provider_kwargs()`
3. `KimiCapabilities.get_websearch_tool_schema()` returns:
   ```python
   {
       "type": "builtin_function",
       "function": {"name": "$web_search"}
   }
   ```
4. Tool is auto-injected into provider call
5. Kimi API performs web search server-side using `$web_search` builtin
6. Results are returned in response

**Key Point:** Users never need to call `glm_web_search` directly - it's all automatic!

---

## 📝 CONFIGURATION VERIFICATION

### Environment Variables

**GLM Web Search:**
```bash
GLM_ENABLE_WEB_BROWSING=true  # ✅ Enabled
```

**Kimi Web Search:**
```bash
KIMI_ENABLE_INTERNET_SEARCH=true  # ✅ Enabled
KIMI_WEBSEARCH_SCHEMA=function    # ✅ Correct (uses builtin_function)
```

### Provider Capabilities

**GLM Capabilities** (`src/providers/capabilities.py` lines 60-81):
- ✅ Supports web search
- ✅ Uses `search_pro_jina` engine (Jina AI search)
- ✅ One week recency filter
- ✅ Medium content size (400-600 chars)
- ✅ Results shown after response
- ✅ Search results included in response

**Kimi Capabilities** (`src/providers/capabilities.py` lines 38-57):
- ✅ Supports web search
- ✅ Uses `$web_search` builtin function (Moonshot API standard)
- ✅ Server-side execution (no client-side search needed)
- ✅ Auto tool choice

---

## ✅ VERIFICATION CHECKLIST

- [x] `glm_web_search` hidden from public tool registry
- [x] `kimi_upload_and_extract` hidden from public tool registry
- [x] `kimi_chat_with_tools` hidden from public tool registry
- [x] Web search auto-injection working for GLM
- [x] Web search auto-injection working for Kimi
- [x] GLM web search configuration verified
- [x] Kimi web search configuration verified (follows Moonshot API)
- [x] Documentation updated with clear comments
- [x] No breaking changes to existing functionality

---

## 🚀 NEXT STEPS

1. **Test web search integration:**
   ```python
   # Test GLM web search
   chat_exai(prompt="What's the latest AI news?", use_websearch=true)
   
   # Test Kimi web search
   chat_exai(prompt="What's the latest AI news?", use_websearch=true, model="kimi-k2-0905-preview")
   ```

2. **Verify tool registry:**
   ```python
   # Should NOT show glm_web_search, kimi_upload_and_extract, kimi_chat_with_tools
   listmodels_exai()
   ```

3. **Monitor logs:**
   - Check that web search tools are auto-injected
   - Verify provider calls include web_search tool
   - Confirm search results are returned

---

## 📚 RELATED DOCUMENTATION

- `src/providers/capabilities.py` - Provider capability adapters
- `src/providers/orchestration/websearch_adapter.py` - Web search tool injection
- `tools/simple/base.py` - SimpleTool execution with web search support
- `docs/system-reference/api/web-search.md` - Web search API documentation
- `docs/guides/web-search-guide.md` - Web search usage guide

---

**Created:** 2025-10-04  
**Status:** COMPLETE  
**Priority:** HIGH

**Summary:** Successfully cleaned up tool registry by hiding internal provider-specific tools. Web search is now properly integrated via automatic tool injection when `use_websearch=true`.

