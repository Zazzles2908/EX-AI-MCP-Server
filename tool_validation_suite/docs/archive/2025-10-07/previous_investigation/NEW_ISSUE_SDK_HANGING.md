# NEW ISSUE DISCOVERED - SDK Still Hanging

**Date:** 2025-10-06 22:00  
**Status:** 🔍 INVESTIGATING  
**Issue:** SDK call hangs even after websearch adapter fix

---

## 🎯 WHAT WE FIXED

✅ **Workflow tools now use websearch adapter**  
✅ **Websearch adapter validates model support**  
✅ **Provider kwargs correctly empty for glm-4.5-flash**  
✅ **SDK kwargs correctly exclude tools/tool_choice**

---

## 🚨 NEW PROBLEM

**The SDK call still hangs even though:**
- Websearch adapter is working (provider_kwargs = {})
- SDK kwargs are correct (['model', 'messages', 'stream', 'temperature'])
- No tools or tool_choice being passed

**Evidence from logs:**
```
INFO:src.providers.capabilities:Model glm-4.5-flash does not support native web search tool calling
INFO:src.providers.capabilities:Web search is still available via direct /web_search API endpoint
[PRINT_DEBUG] Provider kwargs (websearch): {}
[GLM_CHAT] SDK kwargs keys: ['model', 'messages', 'stream', 'temperature']
```

**Note:** The message correctly indicates glm-4.5-flash doesn't support NATIVE tool calling, but can use direct API.

**Then it hangs at:**
```python
resp = sdk_client.chat.completions.create(**sdk_kwargs)
```

---

## 🔍 INVESTIGATION PATHWAY

### Step 1: Trace the Call
```
expert_analysis.py:355 → provider.generate_content()
  ↓
glm.py:88 → glm_chat.generate_content()
  ↓
glm_chat.py:100 → build_payload()
  ↓
glm_chat.py:136 → sdk_client.chat.completions.create(**sdk_kwargs)
  ↓
❌ HANGS HERE
```

### Step 2: Check SDK kwargs
```python
sdk_kwargs = {
    "model": "glm-4.5-flash",
    "messages": [...],
    "stream": False,
    "temperature": 0.2
}
```

**This looks correct!**

### Step 3: Possible Causes

1. **API is genuinely slow** (unlikely - 4+ minutes is too long)
2. **SDK version issue** (we have 2.1.5, should be compatible)
3. **Base URL issue** (using z.ai, might need bigmodel.cn for SDK?)
4. **Unknown parameter in kwargs** (thinking_mode, images, use_websearch?)
5. **SDK bug with specific model** (glm-4.5-flash might have issues)

---

## 🧪 HYPOTHESIS

The SDK might be receiving parameters it doesn't recognize and hanging instead of rejecting them.

**Parameters being passed to generate_content:**
- prompt ✅
- model_name ✅
- system_prompt ✅
- temperature ✅
- thinking_mode ❓ (not used by build_payload)
- images ❓ (not used by build_payload)
- use_websearch ❓ (not used by build_payload)

**These extra parameters are in `**kwargs` but not being filtered out!**

---

## 🔧 NEXT STEPS

1. Check if `thinking_mode` is being passed to SDK
2. Check if `images` is being passed to SDK
3. Check if `use_websearch` is being passed to SDK
4. Filter out unknown parameters before calling SDK
5. Test with minimal parameters only

---

## 📝 FILES TO INVESTIGATE

1. ✅ `tools/workflow/expert_analysis.py` line 355 - Calls provider.generate_content()
2. ✅ `src/providers/glm.py` line 88 - Passes **kwargs through
3. ✅ `src/providers/glm_chat.py` line 100 - build_payload()
4. ✅ `src/providers/glm_chat.py` line 136 - SDK call
5. ❓ Need to check what's actually in **kwargs

---

## 🎯 ACTION PLAN

1. Add debug logging to see ALL kwargs being passed
2. Filter out non-SDK parameters before calling SDK
3. Test with minimal parameters
4. If still hangs, try different base URL
5. If still hangs, try HTTP client instead of SDK

---

**Status:** Investigating why SDK hangs even with correct parameters

