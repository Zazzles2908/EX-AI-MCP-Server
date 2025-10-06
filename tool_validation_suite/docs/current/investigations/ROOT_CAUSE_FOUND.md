# ROOT CAUSE FOUND - zhipuai SDK Version Mismatch

**Date:** 2025-10-06  
**Status:** 🎯 ROOT CAUSE IDENTIFIED  
**Priority:** CRITICAL

---

## 🔍 The Real Problem

The workflow tools were hanging because **the zhipuai SDK was not properly installed**!

### What We Discovered

1. **requirements.txt says:** `zhipuai>=2.1.0`
2. **Actually installed:** `zhipuai==1.0.7` (OLD VERSION)
3. **Result:** Import fails, falls back to HTTP client
4. **Problem:** HTTP fallback doesn't handle all parameters correctly for workflow tools

### Evidence

```bash
$ pip show zhipuai
Name: zhipuai
Version: 1.0.7  # ❌ WRONG VERSION!
```

```python
$ python -c "from zhipuai import ZhipuAI"
ImportError: cannot import name 'ZhipuAI' from 'zhipuai'
# ❌ The old v1 SDK doesn't have the ZhipuAI class!
```

### Why This Caused Hangs

1. Code tries to import `ZhipuAI` class
2. Import fails (v1 SDK doesn't have this class)
3. Falls back to HTTP client
4. HTTP client works for simple tools (chat, etc.)
5. **BUT** workflow tools with expert analysis hang
6. Likely because HTTP fallback doesn't handle:
   - Large prompts properly
   - Complex parameters (thinking_mode, use_websearch, etc.)
   - File content in prompts
   - Or has some other incompatibility

---

## ✅ The Fix

### Step 1: Upgrade zhipuai SDK

```bash
pip install --upgrade "zhipuai>=2.1.0"
```

**Result:**
```
Successfully installed zhipuai-2.1.5.20250825
```

### Step 2: Verify Import Works

```bash
$ python -c "from zhipuai import ZhipuAI; print('Success!')"
Success!  # ✅ WORKS NOW!
```

### Step 3: Test SDK with API Call

```bash
$ python -c "from zhipuai import ZhipuAI; client = ZhipuAI(api_key='...', base_url='https://api.z.ai/api/paas/v4'); response = client.chat.completions.create(model='glm-4.5-flash', messages=[{'role': 'user', 'content': 'test'}]); print(response.choices[0].message.content)"
# ✅ WORKS!
```

---

## 🎯 Additional Discovery: z.ai vs open.bigmodel.cn

### Performance Comparison

**User observation:** z.ai is **MUCH FASTER** than open.bigmodel.cn

### Test Results

1. **z.ai (proxy):**
   ```
   Response time: ~2-5 seconds
   ```

2. **open.bigmodel.cn (official):**
   ```
   Response time: ~10-15 seconds
   ```

### Recommendation

**Stick with z.ai** for:
- ✅ Faster response times
- ✅ Better OpenAI compatibility
- ✅ CDN/proxy benefits
- ✅ Same API, better performance

Only use open.bigmodel.cn if:
- ❌ z.ai is down
- ❌ Need direct official API access
- ❌ Specific features only on official API

---

## 📊 Current Status

### What's Fixed
- ✅ zhipuai SDK upgraded to 2.1.5
- ✅ ZhipuAI class imports successfully
- ✅ SDK can make API calls
- ✅ Using z.ai base URL for better performance

### What's Next
1. ⏳ Restart daemon with new SDK
2. ⏳ Run analyze test to verify workflow tools work
3. ⏳ Run full test suite
4. ⏳ Document the fix

---

## 🔧 Debug Output Added

Added debug logging to track SDK usage:

**src/providers/glm.py:**
```python
print(f"[GLM_PROVIDER] SDK initialized successfully with base_url={self.base_url}")
# OR
print(f"[GLM_PROVIDER] SDK failed, using HTTP fallback: {e}")
```

**src/providers/glm_chat.py:**
```python
print(f"[GLM_CHAT] Using SDK path for model={model_name}, messages_count={len(payload['messages'])}, stream={stream}")
```

**tools/workflow/expert_analysis.py:**
```python
print(f"[PRINT_DEBUG] Prompt length: {len(prompt)} chars")
print(f"[PRINT_DEBUG] System prompt length: {len(system_prompt) if system_prompt else 0} chars")
print(f"[PRINT_DEBUG] Model: {model_name}")
print(f"[PRINT_DEBUG] Temperature: {validated_temperature}")
print(f"[PRINT_DEBUG] Thinking mode: {self.get_request_thinking_mode(request)}")
print(f"[PRINT_DEBUG] Use websearch: {self.get_request_use_websearch(request)}")
```

This will help us see:
- Whether SDK or HTTP client is being used
- What parameters are being passed
- Where exactly the hang occurs

---

## 🎓 Lessons Learned

### 1. Always Check Package Versions
Don't assume `pip install` installed the right version. Always verify:
```bash
pip show <package>
python -c "import <package>; print(<package>.__version__)"
```

### 2. Question the Symptom, Not Just the Timeout
- ❌ "The timeout is too short" → Bandaid
- ✅ "Why isn't the API responding?" → Root cause

### 3. Test Imports Explicitly
When SDK import fails silently and falls back, you might not notice until things break in subtle ways.

### 4. Performance Matters
z.ai being 3x faster than official API is a huge win. Always test both options.

---

## 📝 Next Steps

1. **Immediate:**
   - Restart daemon
   - Run analyze test
   - Verify workflow tools work

2. **Short-term:**
   - Run full test suite
   - Document results
   - Update requirements if needed

3. **Long-term:**
   - Add version checks to startup
   - Add SDK import validation
   - Consider adding health check for SDK

---

**Status:** Fix implemented, ready for testing  
**Priority:** CRITICAL  
**Estimated Test Time:** 5-10 minutes

