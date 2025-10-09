# Phase 5 Testing Findings - CRITICAL BUG FOUND

**Date:** 2025-10-09 14:30 AEDT (Melbourne, Australia)  
**Status:** 🔴 CRITICAL BUG - GLM Embeddings Not Working  
**Tester:** First-time user simulation via EXAI MCP

---

## Testing Approach

Simulated a first-time user testing the GLM embeddings feature through EXAI MCP function calls:

1. ✅ **Web Search Test** - glm-4.5-flash with use_websearch=true - WORKING
2. ✅ **Thinking Mode Test** - glm-4.5 with thinking_mode=high - WORKING  
3. ✅ **File Context Test** - Passed files parameter - WORKING
4. ❌ **GLM Embeddings Test** - FAILED with "Unknown Model" error

---

## Critical Bug Found

### Error Message
```
Error code: 400, with error text {"error":{"code":"1211","message":"Unknown Model, please check the model code."}}
```

### Test Script Output
```bash
python scripts/test_glm_embeddings.py

================================================================================
GLM EMBEDDINGS PROVIDER TEST SUITE
Phase 5 Implementation - 2025-10-09
================================================================================
✅ GLM_API_KEY: 90c4c8f531...U2mAgGZRUD
✅ GLM_BASE_URL: https://api.z.ai/api/paas/v4
✅ GLM_EMBED_MODEL: embedding-3

================================================================================
TEST 1: Single Text Embedding
================================================================================
Failed to generate GLM embeddings: Error code: 400, with error text {"error":{"code":"1211","message":"Unknown Model, please check the model code."}}
```

---

## Root Cause Analysis

### Investigation Steps

**1. Model Name Verification**
- ✅ Found examples using "embedding-2" in the wild
- ✅ Documentation mentions "embedding-2" and "embedding-3"
- ✅ Model name format is correct

**2. API Endpoint Investigation**
- ❓ Using: `https://api.z.ai/api/paas/v4`
- ❓ This is the z.ai international proxy (3x faster for chat)
- ❓ **HYPOTHESIS**: z.ai proxy might not support embeddings endpoint

**3. Official Documentation**
- Documentation URL: `https://open.bigmodel.cn/dev/api/vector/embedding`
- Official API: `https://open.bigmodel.cn/api/paas/v4/embeddings`
- **FINDING**: Official docs use `open.bigmodel.cn`, not `api.z.ai`

---

## Hypothesis

**The z.ai proxy endpoint (https://api.z.ai/api/paas/v4) may not support the embeddings API.**

### Evidence:
1. Chat API works fine with z.ai proxy
2. Embeddings API returns "Unknown Model" error
3. Official documentation uses open.bigmodel.cn for embeddings
4. No evidence of z.ai supporting /embeddings endpoint

### Possible Solutions:

**Option 1: Use bigmodel.cn for embeddings**
```python
# For embeddings only, use official endpoint
self.base_url = "https://open.bigmodel.cn/api/paas/v4"
```

**Option 2: Make base_url configurable**
```bash
# .env
GLM_BASE_URL=https://api.z.ai/api/paas/v4  # For chat
GLM_EMBEDDINGS_BASE_URL=https://open.bigmodel.cn/api/paas/v4  # For embeddings
```

**Option 3: Auto-fallback**
```python
# Try z.ai first, fallback to bigmodel.cn for embeddings
try:
    response = self.client.embeddings.create(...)
except APIRequestFailedError as e:
    if "Unknown Model" in str(e):
        # Fallback to official endpoint
        client = ZhipuAI(api_key=self.api_key, base_url="https://open.bigmodel.cn/api/paas/v4")
        response = client.embeddings.create(...)
```

---

## EXAI MCP Testing Results

### ✅ What Worked

**1. Web Search (glm-4.5-flash)**
```json
{
  "model": "glm-4.5-flash",
  "use_websearch": true
}
```
- Web search tool calling worked correctly
- DuckDuckGo fallback engine used
- Results returned successfully

**2. Thinking Mode (glm-4.5)**
```json
{
  "model": "glm-4.5",
  "thinking_mode": "high"
}
```
- Thinking mode activated correctly
- Extended reasoning performed
- No errors

**3. File Context**
```json
{
  "files": ["path/to/file1.py", "path/to/file2.py"]
}
```
- Files loaded successfully
- Context provided to model
- Analysis performed correctly

**4. Continuation IDs**
- Multi-turn conversations working
- Context maintained across turns
- No issues with continuation_id parameter

---

### ❌ What Failed

**1. GLM Embeddings**
- Model name "embedding-3" not recognized
- API returns "Unknown Model" error
- Likely due to z.ai proxy not supporting embeddings endpoint

**2. Test Script .env Loading**
- Initial run failed because subprocess didn't load .env
- Fixed by adding `python-dotenv` loading
- Now works correctly

---

## Recommendations

### Immediate Actions

**1. Fix GLM Embeddings Base URL**
- Change embeddings to use `open.bigmodel.cn` instead of `api.z.ai`
- Add separate `GLM_EMBEDDINGS_BASE_URL` env var
- Update documentation

**2. Update Test Script**
- ✅ Already fixed .env loading issue
- Add test for base_url fallback
- Add test for both endpoints

**3. Update Documentation**
- Document that z.ai proxy may not support all endpoints
- Clarify which endpoints work with z.ai vs bigmodel.cn
- Update Phase 5 completion docs

### Long-term Improvements

**1. Endpoint Discovery**
- Add automatic endpoint detection
- Test endpoints on initialization
- Log which endpoints are being used

**2. Better Error Messages**
- Catch "Unknown Model" errors
- Suggest trying different base_url
- Provide helpful troubleshooting steps

**3. Configuration Validation**
- Validate model names against known models
- Validate endpoints support required features
- Warn users about potential issues

---

## User Experience Impact

### First-Time User Perspective

**What Went Well:**
- ✅ EXAI MCP tools are intuitive and easy to use
- ✅ Web search integration works seamlessly
- ✅ Thinking mode provides deeper analysis
- ✅ File context loading is straightforward
- ✅ Error messages are clear (when they occur)

**What Needs Improvement:**
- ❌ GLM embeddings fail silently with cryptic error
- ❌ No guidance on which endpoints support which features
- ❌ Documentation assumes z.ai works for everything
- ❌ No fallback or retry logic for failed endpoints

---

## Next Steps

1. **Fix GLM Embeddings** - Use correct base_url for embeddings
2. **Test Fix** - Verify embeddings work with bigmodel.cn endpoint
3. **Update Documentation** - Clarify endpoint support
4. **Proceed with Phase 6** - Timestamp improvements

---

## Testing Summary

| Feature | Status | Notes |
|---------|--------|-------|
| EXAI Web Search | ✅ PASS | Works correctly with glm-4.5-flash |
| EXAI Thinking Mode | ✅ PASS | Works correctly with glm-4.5 |
| EXAI File Context | ✅ PASS | Files loaded and analyzed |
| EXAI Continuation | ✅ PASS | Multi-turn conversations work |
| GLM Embeddings | ❌ FAIL | "Unknown Model" error - wrong base_url |
| Test Script | ✅ PASS | Fixed .env loading issue |

---

**Last Updated:** 2025-10-09 14:30 AEDT  
**Next Action:** Fix GLM embeddings base_url issue

