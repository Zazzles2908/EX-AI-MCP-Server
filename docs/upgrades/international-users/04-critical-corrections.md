# CRITICAL CORRECTIONS: GLM & Z.ai SDK Research

**Date:** 2025-10-01  
**Research Method:** Native Web Search via GLM-4.5  
**Status:** ⚠️ MAJOR INACCURACIES FOUND IN PREVIOUS DOCUMENTATION

---

## 🚨 CRITICAL ERRORS IDENTIFIED

### Error #1: Wrong SDK Package Name

**❌ INCORRECT (What I documented):**
- Package name: `zai-sdk`
- Version: `0.0.4`

**✅ CORRECT (Actual facts):**
- **TWO DIFFERENT PACKAGES EXIST:**
  1. **`zhipuai`** - Official SDK for Mainland China users
     - Latest version: **`2.1.5.20250825`** (Released August 25, 2025)
     - PyPI: https://pypi.org/project/zhipuai/
     - Base URL: `https://open.bigmodel.cn/api/paas/v4/`
  
  2. **`zai-sdk`** - Official SDK for Overseas users
     - Latest version: **`0.0.4`** (Released September 30, 2025)
     - GitHub: https://github.com/THUDM/z-ai-sdk-python
     - Base URL: `https://api.z.ai/api/paas/v4/`

**Impact:** Our codebase uses `zai-sdk>=0.0.3.3` which is correct for overseas users, but I failed to document that there are TWO separate SDKs!

---

### Error #2: GLM-4.6 Release Date

**❌ INCORRECT (What I might have implied):**
- GLM-4.6 was released in July 2025 alongside GLM-4.5

**✅ CORRECT (Actual facts):**
- **GLM-4.5** was released on **July 28, 2025**
- **GLM-4.6** was released on **September 30, 2025** (TODAY!)
- Source: https://z.ai/blog/glm-4.6

**Impact:** GLM-4.6 is BRAND NEW (released today), not an older model!

---

### Error #3: GLM-4.6 Specifications

**✅ CORRECT SPECIFICATIONS:**
- **Total Parameters:** 355B (same as GLM-4.5)
- **Active Parameters:** 32B (same as GLM-4.5)
- **Context Length:** **200K tokens** (INCREASED from 128K in GLM-4.5)
- **Key Improvements:**
  - Extended context: 128K → 200K tokens
  - Stronger coding capabilities
  - Enhanced agentic workflows
  - Better reasoning abilities

**Source:** https://z.ai/blog/glm-4.6

---

## 📊 CORRECT SDK INFORMATION

### For Mainland China Users: `zhipuai`

```bash
pip install zhipuai
```

**Latest Version:** `2.1.5.20250825` (August 25, 2025)

**Client Initialization:**
```python
from zhipuai import ZhipuAI

client = ZhipuAI(
    api_key="your-api-key",
    base_url="https://open.bigmodel.cn/api/paas/v4/"
)
```

**Features:**
- Chat completions (standard & streaming)
- Tool calling (web_search, function calling)
- Multimodal chat (vision models)
- Character role-playing (charglm-3)
- Assistant API
- Video generation (cogvideox-2)
- Audio transcription
- Embeddings
- File management
- Batch operations

---

### For Overseas Users: `zai-sdk`

```bash
pip install zai-sdk
```

**Latest Version:** `0.0.4` (September 30, 2025)

**Client Initialization:**
```python
from zai import ZaiClient

client = ZaiClient(
    api_key="your-api-key",
    base_url="https://api.z.ai/api/paas/v4/"
)
```

**Features:** (Same as zhipuai package)
- Chat completions
- Tool calling
- Multimodal chat
- Character role-playing
- Assistant API
- Video generation
- Audio transcription
- Embeddings
- File management
- Batch operations

---

## 🎯 CORRECT MODEL LINEUP

### GLM-4.6 (Released September 30, 2025)
- **Context:** 200K tokens
- **Parameters:** 355B total, 32B active
- **Strengths:** Coding, agentic workflows, reasoning
- **Availability:** Z.ai API platform

### GLM-4.5 (Released July 28, 2025)
- **Context:** 128K tokens
- **Parameters:** 355B total, 32B active
- **Variants:**
  - `glm-4.5` - Full model
  - `glm-4.5-flash` - Fast inference
  - `glm-4.5-air` - Lightweight variant

### GLM-4.5V (Released August 11, 2025)
- **Type:** Multimodal (vision)
- **Context:** 128K tokens
- **Capabilities:** Image understanding

### GLM-4 (Previous generation)
- **Context:** 128K tokens
- **Variants:**
  - `glm-4` - Standard model
  - `glm-4v` - Vision model
  - `glm-4-assistant` - Assistant API model

### CharGLM-3
- **Type:** Character role-playing
- **Use case:** Conversational AI with character personas

### CogVideoX-2
- **Type:** Video generation
- **Capabilities:** Text-to-video, image-to-video
- **Quality modes:** "quality" or "speed"
- **Resolution:** Up to 4K (3840x2160)
- **FPS:** 30 or 60

---

## 🔧 CORRECT API ENDPOINTS

### Mainland China
- **Base URL:** `https://open.bigmodel.cn/api/paas/v4/`
- **Platform:** https://open.bigmodel.cn/
- **SDK Package:** `zhipuai`

### Overseas
- **Base URL:** `https://api.z.ai/api/paas/v4/`
- **Platform:** https://z.ai/
- **SDK Package:** `zai-sdk`

### API Endpoints (Both regions)
- `/chat/completions` - Chat completions
- `/embeddings` - Text embeddings
- `/videos/generations` - Video generation
- `/videos/retrieve_videos_result` - Get video results
- `/assistant/conversation` - Assistant conversations
- `/files` - File management
- `/web_search` - Web search tool

---

## 📦 CORRECT DEPENDENCIES

### zhipuai (Mainland China)
```
httpx>=0.23.0
pydantic>=1.9.0,<3.0.0
typing-extensions>=4.0.0
```

### zai-sdk (Overseas)
```
httpx>=0.23.0
pydantic>=1.9.0,<3.0.0
typing-extensions>=4.0.0
cachetools>=4.2.2
pyjwt>=2.8.0
```

**Python Support:** 3.8, 3.9, 3.10, 3.11, 3.12

---

## 🎯 WHAT I MISSED IN MY PREVIOUS DOCUMENTATION

### 1. Two Separate SDKs
- I only documented `zai-sdk` without mentioning `zhipuai`
- I didn't explain the regional differences
- I didn't document that users need to choose based on their region

### 2. GLM-4.6 Release Date
- I may have implied GLM-4.6 was released earlier
- I didn't emphasize it's a BRAND NEW model (released today!)
- I didn't highlight the context extension (128K → 200K)

### 3. SDK Version Numbers
- `zhipuai` is at version 2.1.5.20250825 (much higher than I thought)
- `zai-sdk` is at version 0.0.4 (which I got right, but didn't explain the dual-SDK situation)

### 4. Client Class Names
- `zhipuai` uses: `ZhipuAI` class
- `zai-sdk` uses: `ZaiClient` and `ZhipuAiClient` classes
- I didn't document this difference

### 5. Video Generation
- I didn't document CogVideoX-2 video generation capabilities
- I didn't mention 4K support, FPS options, audio generation

### 6. Assistant API
- I didn't document the assistant conversation API
- I didn't mention the assistant_id parameter

### 7. Character Role-Playing
- I didn't document CharGLM-3 model
- I didn't mention the meta parameter for character setup

---

## ✅ WHAT I GOT RIGHT

1. ✅ GLM-4.5 specifications (355B total, 32B active, 128K context)
2. ✅ GLM-4.5-flash and GLM-4.5-air variants
3. ✅ Web search tool integration
4. ✅ Streaming support
5. ✅ Function calling capabilities
6. ✅ Multimodal (vision) support
7. ✅ Base API URL structure

---

## 🔄 REQUIRED UPDATES TO PREVIOUS DOCUMENTATION

### File: `docs/upgrades/glm-4.6-and-sdk-changes.md`

**Must Update:**
1. Add section on dual SDK packages (zhipuai vs zai-sdk)
2. Correct GLM-4.6 release date to September 30, 2025
3. Update context length: 200K tokens (not 128K)
4. Add video generation capabilities
5. Add assistant API documentation
6. Add character role-playing documentation
7. Clarify regional differences

### File: `docs/upgrades/zai-sdk-upgrade-implementation-plan.md`

**Must Update:**
1. Clarify which SDK we're using (zai-sdk for overseas)
2. Update version numbers correctly
3. Add migration notes for dual-SDK awareness
4. Update client initialization examples
5. Add new features (video, assistant, character)

---

## 📝 SUMMARY OF CORRECTIONS

| Item | Previous (Incorrect) | Corrected |
|------|---------------------|-----------|
| SDK Package | zai-sdk only | zhipuai (China) + zai-sdk (Overseas) |
| zhipuai Version | Not documented | 2.1.5.20250825 |
| zai-sdk Version | 0.0.4 | 0.0.4 ✅ |
| GLM-4.6 Release | Unclear/July 2025 | September 30, 2025 |
| GLM-4.6 Context | 128K | 200K tokens |
| Client Classes | Not documented | ZhipuAI, ZaiClient, ZhipuAiClient |
| Video Generation | Not documented | CogVideoX-2, up to 4K, 30/60 FPS |
| Assistant API | Not documented | Full conversation API |
| Character RP | Not documented | CharGLM-3 with meta params |

---

## 🎯 ACTION ITEMS

1. ✅ Document the dual-SDK situation
2. ✅ Correct GLM-4.6 release date and specs
3. ✅ Update context length to 200K
4. ⏳ Rewrite glm-4.6-and-sdk-changes.md with corrections
5. ⏳ Rewrite zai-sdk-upgrade-implementation-plan.md with corrections
6. ⏳ Add video generation to implementation plan
7. ⏳ Add assistant API to implementation plan
8. ⏳ Add character role-playing to implementation plan

---

**Research Completed:** 2025-10-01  
**Method:** Native GLM-4.5 Web Search  
**Sources:** PyPI, GitHub, Z.ai Blog, Official Documentation  
**Confidence:** HIGH (verified through multiple sources)

