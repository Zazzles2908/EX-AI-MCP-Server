# System Reference Update Plan
**Date:** 2025-10-14 (14th October 2025)  
**Purpose:** Update outdated system-reference documentation  
**Status:** IN PROGRESS

---

## 🔍 Issues Identified

### 1. GLM Provider Documentation (glm.md)
**Last Updated:** 2025-10-03 (11 days old)

**Outdated Information:**
- ❌ Base URL: `https://api.z.ai/v1` (WRONG - should be `/api/paas/v4`)
- ❌ Missing glm-4.6-v (vision model)
- ❌ Uses zai-sdk (we use direct API calls)
- ✅ Correct: glm-4.6 has 200K context

**Needs Update:**
1. Correct base URL to `https://api.z.ai/api/paas/v4`
2. Add glm-4.6-v vision model with video_url/image_url examples
3. Remove zai-sdk references (we use requests library)
4. Update to match 02_API_REFERENCE/GLM_API_REFERENCE.md

### 2. Kimi Provider Documentation (kimi.md)
**Last Updated:** 2025-10-03 (11 days old)

**Outdated Information:**
- ❌ Missing kimi-k2-turbo-preview
- ❌ Missing kimi-thinking-preview
- ❌ Context: Says 256K (should be 128K for K2 models)
- ❌ Missing reasoning_content extraction

**Needs Update:**
1. Add kimi-k2-turbo-preview
2. Add kimi-thinking-preview with reasoning extraction
3. Correct context window (128K for K2, not 256K)
4. Update to match 02_API_REFERENCE/KIMI_API_REFERENCE.md

### 3. Routing Documentation (routing.md)
**Last Updated:** 2025-10-03 (11 days old)

**Status:** Mostly accurate, but needs minor updates

**Needs Update:**
1. Add note about glm-4.6 200K context
2. Add note about Kimi thinking mode
3. Update escalation strategy with thinking modes

### 4. Upgrade Roadmap (07-upgrade-roadmap.md)
**Last Updated:** 2025-10-02 (12 days old)

**Status:** OUTDATED - Wave 2 in progress, but we're now on different work

**Needs Update:**
1. Mark as ARCHIVED (old roadmap)
2. Create new roadmap based on MASTER_CHECKLIST_2025-10-14.md
3. Move to 07_ARCHIVE/

---

## 📋 Action Plan

### Step 1: Update GLM Provider Documentation
**File:** `docs/system-reference/providers/glm.md`

**Changes:**
```markdown
# GLM Provider (ZhipuAI/Z.ai)

**Version:** 1.2  
**Last Updated:** 2025-10-14  
**Related:** [kimi.md](kimi.md), [routing.md](routing.md), [../../02_API_REFERENCE/GLM_API_REFERENCE.md](../../02_API_REFERENCE/GLM_API_REFERENCE.md)

---

## Configuration

**Environment Variables:**
```env
# Required
GLM_API_KEY=your_api_key_here
GLM_BASE_URL=https://api.z.ai/api/paas/v4  # ← CORRECTED

# Optional
GLM_STREAM_ENABLED=true
GLM_DEFAULT_MODEL=glm-4.6
GLM_TEMPERATURE=0.6
GLM_MAX_TOKENS=65536
```

## Available Models

**GLM-4.6 Series (Latest):**
- `glm-4.6` - Flagship model with 200K context window
  - **Context:** 200,000 tokens
  - **Pricing:** $0.60 input / $2.20 output per million tokens
  - **Features:** Thinking mode, function calling, web search, retrieval

- `glm-4.6-v` - Vision model  # ← NEW
  - **Context:** 128K tokens
  - **Features:** Vision (images, videos), function calling
  - **Content Types:** image_url, video_url, text

**GLM-4.5 Series:**
- `glm-4.5` - Previous flagship with 128K context
- `glm-4.5-flash` - Fast, cost-effective (default manager)
- `glm-4.5-air` - Lightweight version

## API Integration (Direct HTTP)

**Note:** We use direct HTTP requests, NOT zai-sdk

**Basic Usage:**
```python
import requests

url = "https://api.z.ai/api/paas/v4/chat/completions"

payload = {
    "model": "glm-4.6",
    "messages": [
        {"role": "user", "content": "Hello!"}
    ]
}

headers = {
    "Authorization": "Bearer <GLM_API_KEY>",
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)
```

**Vision Example (glm-4.6-v):**
```python
payload = {
    "model": "glm-4.6-v",
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "video_url",
                    "video_url": {"url": "https://example.com/video.mov"}
                },
                {
                    "type": "text",
                    "text": "What is in this video?"
                }
            ]
        }
    ]
}
```

**For complete API reference, see:** [GLM_API_REFERENCE.md](../../02_API_REFERENCE/GLM_API_REFERENCE.md)
```

### Step 2: Update Kimi Provider Documentation
**File:** `docs/system-reference/providers/kimi.md`

**Changes:**
```markdown
# Kimi Provider (Moonshot)

**Version:** 1.2  
**Last Updated:** 2025-10-14  
**Related:** [glm.md](glm.md), [routing.md](routing.md), [../../02_API_REFERENCE/KIMI_API_REFERENCE.md](../../02_API_REFERENCE/KIMI_API_REFERENCE.md)

---

## Available Models

### K2 Series (Agentic Intelligence)

**kimi-k2-0905-preview** - Latest K2 **[RECOMMENDED]**
- **Context:** 128K tokens  # ← CORRECTED (was 256K)
- **Architecture:** 1T/32B MoE (Mixture of Experts)
- **Pricing:** $0.60 input / $2.50 output per million tokens
- **Features:** Enhanced coding, tool-calling, agentic workflows

**kimi-k2-turbo-preview** - Fast K2  # ← NEW
- **Context:** 128K tokens
- **Features:** Faster responses, same K2 capabilities

**kimi-thinking-preview** - Thinking Mode  # ← NEW
- **Context:** 128K tokens
- **Features:** Reasoning extraction via reasoning_content field
- **Use Case:** Complex reasoning, deep analysis

**For complete API reference, see:** [KIMI_API_REFERENCE.md](../../02_API_REFERENCE/KIMI_API_REFERENCE.md)
```

### Step 3: Update Routing Documentation
**File:** `docs/system-reference/providers/routing.md`

**Minor updates to reflect new capabilities**

### Step 4: Archive Upgrade Roadmap
**File:** `docs/system-reference/07-upgrade-roadmap.md`

**Action:** Move to `docs/07_ARCHIVE/OLD_UPGRADE_ROADMAP.md`

---

## 🎯 Decision: Consolidate or Keep Separate?

**Option A: Keep system-reference/ Separate**
- Pros: Maintains historical structure
- Cons: Duplicate information with 02_API_REFERENCE/

**Option B: Consolidate into 02_API_REFERENCE/**
- Pros: Single source of truth
- Cons: Loses system-reference context

**Option C: Update system-reference/ to Reference 02_API_REFERENCE/**
- Pros: Keeps both, avoids duplication
- Cons: Requires cross-references

**RECOMMENDATION: Option C**
- Update system-reference/ files to be lightweight
- Add prominent links to 02_API_REFERENCE/ for complete docs
- Keep system-reference/ for historical context and high-level overview

---

## ✅ Execution Steps

1. **Update GLM Provider Doc**
   - Correct base URL
   - Add glm-4.6-v
   - Remove zai-sdk references
   - Add link to 02_API_REFERENCE/GLM_API_REFERENCE.md

2. **Update Kimi Provider Doc**
   - Correct context window (128K)
   - Add kimi-k2-turbo-preview
   - Add kimi-thinking-preview
   - Add link to 02_API_REFERENCE/KIMI_API_REFERENCE.md

3. **Update Routing Doc**
   - Add note about 200K context for glm-4.6
   - Add note about thinking modes

4. **Archive Upgrade Roadmap**
   - Move to 07_ARCHIVE/OLD_UPGRADE_ROADMAP.md
   - Create note in system-reference/ pointing to MASTER_CHECKLIST

---

**Status:** READY TO EXECUTE  
**Estimated Time:** 30 minutes  
**Priority:** MEDIUM (not blocking bug fixes)

