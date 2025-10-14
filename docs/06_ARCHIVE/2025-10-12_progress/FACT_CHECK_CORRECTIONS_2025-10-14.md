# Fact-Check Corrections
**Date:** 2025-10-14 (14th October 2025)  
**Purpose:** Document corrections after user fact-check  
**Status:** COMPLETE

---

## 🔍 User Fact-Check Request

User provided screenshot showing actual Kimi K2 model specifications and requested validation of all documentation.

---

## ❌ Errors Found & Corrected

### 1. Kimi K2 Context Windows - CORRECTED

**My Original Claim (WRONG):**
> "All K2 models have 128K context"

**Actual Truth (from user screenshot):**
- **kimi-k2-0905-preview:** 262,144 tokens (256K) ✅
- **kimi-k2-0711-preview:** 131,072 tokens (128K) ✅
- **kimi-k2-turbo-preview:** 262,144 tokens (256K) ✅

**What I Got Wrong:**
- I incorrectly stated ALL K2 models have 128K
- Only kimi-k2-0711-preview has 128K
- kimi-k2-0905-preview and kimi-k2-turbo-preview have 256K

**Files Corrected:**
- ✅ `docs/02_API_REFERENCE/KIMI_API_REFERENCE.md`
- ✅ `docs/system-reference/providers/kimi.md`

---

### 2. Kimi K2 Pricing - ADDED

**What Was Missing:**
- Cache hit vs cache miss pricing
- kimi-k2-turbo-preview pricing

**Added (from user screenshot):**

**kimi-k2-0905-preview:**
- Input: $0.15 (cache hit) / $0.60 (cache miss) per million tokens
- Output: $2.50 per million tokens

**kimi-k2-0711-preview:**
- Input: $0.15 (cache hit) / $0.60 (cache miss) per million tokens
- Output: $2.50 per million tokens

**kimi-k2-turbo-preview:**
- Input: $0.60 (cache hit) / $2.40 (cache miss) per million tokens
- Output: $10.00 per million tokens

**Files Updated:**
- ✅ `docs/02_API_REFERENCE/KIMI_API_REFERENCE.md`
- ✅ `docs/system-reference/providers/kimi.md`

---

### 3. GLM Base URL - CORRECTED

**What Was Wrong:**
- `docs/system-reference/providers/glm.md` showed BOTH `/v1` and `/api/paas/v4`
- Inconsistent throughout the file

**Corrected To:**
- ✅ `https://api.z.ai/api/paas/v4` (everywhere)

**Files Corrected:**
- ✅ `docs/system-reference/providers/glm.md`

---

### 4. GLM Vision Model - ADDED

**What Was Missing:**
- glm-4.6-v (vision model)
- Video URL support

**Added:**
- ✅ glm-4.6-v model with 128K context
- ✅ Vision support (image_url, video_url)
- ✅ Example code from user

**Files Updated:**
- ✅ `docs/02_API_REFERENCE/GLM_API_REFERENCE.md`
- ✅ `docs/system-reference/providers/glm.md`

---

### 5. GLM SDK References - REMOVED

**What Was Wrong:**
- system-reference/providers/glm.md referenced zai-sdk
- EX-AI-MCP-Server uses direct HTTP requests, NOT zai-sdk

**Corrected:**
- ✅ Removed zai-sdk references
- ✅ Replaced with direct HTTP examples using `requests` library
- ✅ Added note: "EX-AI-MCP-Server uses direct HTTP requests, NOT zai-sdk"

**Files Corrected:**
- ✅ `docs/system-reference/providers/glm.md`

---

## ✅ What Was Already Correct

### GLM-4.6 Context Window
- ✅ 200K tokens (200,000 tokens) - CORRECT in all files

### Kimi OpenAI SDK Compatibility
- ✅ Correctly documented as OpenAI SDK compatible

### GLM Thinking Mode
- ✅ Correctly documented as boolean (enabled/disabled)

### Kimi Thinking Mode
- ✅ Correctly documented as model-based (kimi-thinking-preview)

---

## 📊 Summary of Changes

### Files Modified: 3

1. **docs/02_API_REFERENCE/KIMI_API_REFERENCE.md**
   - Corrected K2 context windows (256K for 0905/turbo, 128K for 0711)
   - Added pricing with cache hit/miss
   - Added kimi-k2-turbo-preview details

2. **docs/system-reference/providers/kimi.md**
   - Corrected K2 context windows
   - Added pricing with cache hit/miss
   - Added kimi-k2-turbo-preview
   - Added kimi-thinking-preview

3. **docs/system-reference/providers/glm.md**
   - Corrected base URL to `/api/paas/v4` everywhere
   - Added glm-4.6-v vision model
   - Removed zai-sdk references
   - Replaced with direct HTTP examples

---

## 🎓 Lessons Learned

### 1. Always Verify Against Official Sources
- Don't assume context windows are uniform across model series
- Check actual API documentation and pricing pages

### 2. User Screenshots Are Authoritative
- User provided screenshot from official Moonshot pricing page
- This is more reliable than my assumptions

### 3. Check Implementation vs Documentation
- We use direct HTTP, not zai-sdk
- Documentation should reflect actual implementation

### 4. Cache Pricing Matters
- Kimi has cache hit vs cache miss pricing
- This is important for cost optimization
- Should be documented prominently

---

## 📋 Verification Checklist

### Kimi Models ✅
- [x] kimi-k2-0905-preview: 256K context, $0.15/$0.60 input, $2.50 output
- [x] kimi-k2-0711-preview: 128K context, $0.15/$0.60 input, $2.50 output
- [x] kimi-k2-turbo-preview: 256K context, $0.60/$2.40 input, $10.00 output
- [x] kimi-thinking-preview: 128K context, reasoning extraction

### GLM Models ✅
- [x] glm-4.6: 200K context, $0.60 input, $2.20 output
- [x] glm-4.6-v: 128K context, vision support (image_url, video_url)
- [x] glm-4.5-flash: Fast, cost-effective (default manager)

### Base URLs ✅
- [x] GLM: https://api.z.ai/api/paas/v4
- [x] Kimi: https://api.moonshot.ai/v1

### Implementation ✅
- [x] GLM: Direct HTTP with requests library
- [x] Kimi: OpenAI SDK compatible

---

## 🔗 Related Documentation

**Updated Files:**
- [KIMI_API_REFERENCE.md](../02_API_REFERENCE/KIMI_API_REFERENCE.md)
- [GLM_API_REFERENCE.md](../02_API_REFERENCE/GLM_API_REFERENCE.md)
- [kimi.md](../system-reference/providers/kimi.md)
- [glm.md](../system-reference/providers/glm.md)

**Reference:**
- User screenshot: Moonshot AI pricing page showing K2 model specifications

---

## ✅ Status: COMPLETE

All errors identified by user have been corrected. Documentation now accurately reflects:
- Correct context windows for all K2 models
- Correct pricing with cache hit/miss
- Correct base URLs
- Correct implementation approach (HTTP vs SDK)
- Complete model listings including vision models

---

**Last Updated:** 2025-10-14 (14th October 2025)  
**Verified By:** User fact-check with official pricing screenshot  
**Status:** ✅ COMPLETE - All corrections applied

