# MODEL CAPABILITIES REFERENCE
**Last Updated:** 2025-10-12 1:45 PM AEDT  
**Last Verified:** 2025-10-12 (from codebase configuration files)  
**Status:** ✅ COMPLETE

---

## 🎯 PURPOSE

This document provides comprehensive information about all available models in the EXAI MCP Server, including their capabilities, limitations, and recommended use cases.

---

## 📊 QUICK REFERENCE TABLE

| Model | Provider | Context | Vision | Web Search | Thinking | File Upload | Streaming | Best For |
|-------|----------|---------|--------|------------|----------|-------------|-----------|----------|
| **kimi-k2-0905-preview** | Kimi | 256K | ✅ | ✅ | ❌ | ✅ | ✅ | General purpose, vision tasks |
| **kimi-k2-turbo-preview** | Kimi | 256K | ✅ | ✅ | ❌ | ✅ | ✅ | High-speed generation (60-100 tok/s) |
| **kimi-k2-0711-preview** | Kimi | 128K | ❌ | ✅ | ❌ | ✅ | ✅ | Text-only tasks |
| **kimi-latest** | Kimi | 128K | ❌ | ✅ | ❌ | ✅ | ✅ | Latest stable (alias) |
| **kimi-latest-8k** | Kimi | 8K | ❌ | ✅ | ❌ | ✅ | ✅ | Short context tasks |
| **kimi-latest-32k** | Kimi | 32K | ❌ | ✅ | ❌ | ✅ | ✅ | Medium context tasks |
| **kimi-latest-128k** | Kimi | 128K | ❌ | ✅ | ❌ | ✅ | ✅ | Long context tasks |
| **kimi-thinking-preview** | Kimi | 128K | ❌ | ✅ | ✅ | ✅ | ✅ | Complex reasoning |
| **moonshot-v1-8k** | Kimi | 8K | ❌ | ✅ | ❌ | ✅ | ✅ | Legacy 8K model |
| **moonshot-v1-32k** | Kimi | 32K | ❌ | ✅ | ❌ | ✅ | ✅ | Legacy 32K model |
| **moonshot-v1-128k** | Kimi | 128K | ❌ | ✅ | ❌ | ✅ | ✅ | Legacy 128K model |
| **glm-4.6** | GLM | 200K | ✅ | ✅ | ✅ | ✅ | ✅ | Flagship model, thinking mode |
| **glm-4.5** | GLM | 128K | ✅ | ✅ | ✅ | ✅ | ✅ | Hybrid reasoning |
| **glm-4.5-flash** | GLM | 128K | ✅ | ✅ | ❌ | ✅ | ✅ | Fast, cost-effective |
| **glm-4.5-air** | GLM | 128K | ✅ | ✅ | ✅ | ✅ | ✅ | Efficient reasoning |
| **glm-4.5v** | GLM | 64K | ✅ | ✅ | ❌ | ✅ | ✅ | Vision-language multimodal |

---

## 🔍 DETAILED MODEL SPECIFICATIONS

### KIMI/MOONSHOT MODELS

#### kimi-k2-0905-preview
**Context:** 256K (262,144 tokens)  
**Max Output:** 8,192 tokens  
**Vision:** ✅ Yes (20MB max image size)  
**Web Search:** ✅ Yes (via builtin_function)  
**Thinking Mode:** ❌ No  
**File Upload:** ✅ Yes (requires TEST_FILES_DIR)  
**Streaming:** ✅ Yes  
**Function Calling:** ✅ Yes (ToolCalls)  
**Aliases:** kimi-k2-0905, kimi-k2

**Best For:**
- General purpose tasks with large context
- Vision/image analysis tasks
- Document processing with images
- Multi-modal applications

**Limitations:**
- No extended thinking mode
- Requires TEST_FILES_DIR for file uploads

---

#### kimi-k2-turbo-preview
**Context:** 256K (262,144 tokens)  
**Max Output:** 8,192 tokens  
**Vision:** ✅ Yes (20MB max image size)  
**Web Search:** ✅ Yes (via builtin_function)  
**Thinking Mode:** ❌ No  
**File Upload:** ✅ Yes (requires TEST_FILES_DIR)  
**Streaming:** ✅ Yes (60-100 tokens/sec - HIGH SPEED)  
**Function Calling:** ✅ Yes (ToolCalls)  
**Aliases:** kimi-k2-turbo

**Best For:**
- High-speed generation requirements
- Real-time applications
- Interactive chat scenarios
- Large context with fast responses

**Limitations:**
- No extended thinking mode
- Requires TEST_FILES_DIR for file uploads

---

#### kimi-k2-0711-preview
**Context:** 128K (131,072 tokens)  
**Max Output:** 8,192 tokens  
**Vision:** ❌ No  
**Web Search:** ✅ Yes (via builtin_function)  
**Thinking Mode:** ❌ No  
**File Upload:** ✅ Yes (requires TEST_FILES_DIR)  
**Streaming:** ✅ Yes  
**Function Calling:** ✅ Yes (ToolCalls)  
**Aliases:** kimi-k2-0711

**Best For:**
- Text-only tasks
- Code analysis
- Document processing (text only)
- Long context text tasks

**Limitations:**
- No vision support
- No extended thinking mode
- Requires TEST_FILES_DIR for file uploads

---

#### moonshot-v1-8k / moonshot-v1-32k / moonshot-v1-128k
**Context:** 8K / 32K / 128K respectively  
**Max Output:** 2,048 / 4,096 / 8,192 tokens  
**Vision:** ❌ No  
**Web Search:** ✅ Yes (via builtin_function)  
**Thinking Mode:** ❌ No  
**File Upload:** ✅ Yes (requires TEST_FILES_DIR)  
**Streaming:** ✅ Yes  
**Function Calling:** ❌ No (legacy models)

**Best For:**
- Legacy compatibility
- Simple text tasks
- Cost-sensitive applications

**Limitations:**
- No vision support
- No function calling
- No extended thinking mode
- Older model architecture

---

### GLM MODELS

#### glm-4.6 (FLAGSHIP)
**Context:** 200K (200,000 tokens)  
**Max Output:** 8,192 tokens  
**Vision:** ✅ Yes  
**Web Search:** ✅ Yes (via z.ai SDK - ALL GLM models support web search)  
**Thinking Mode:** ✅ Yes (via "thinking": {"type": "enabled"})  
**File Upload:** ✅ Yes (different mechanism than Kimi)  
**Streaming:** ✅ Yes  
**Function Calling:** ✅ Yes (via tools parameter)

**Best For:**
- Complex reasoning tasks
- Flagship performance
- Thinking mode requirements
- Large context with web search
- Vision + reasoning combined

**Limitations:**
- Higher cost than flash/air variants
- Conversation IDs cannot be shared with Kimi

---

#### glm-4.5
**Context:** 128K (128,000 tokens)  
**Max Output:** 8,192 tokens  
**Vision:** ✅ Yes  
**Web Search:** ✅ Yes (via z.ai SDK)  
**Thinking Mode:** ✅ Yes (hybrid reasoning model)  
**File Upload:** ✅ Yes  
**Streaming:** ✅ Yes  
**Function Calling:** ✅ Yes

**Best For:**
- Hybrid reasoning tasks
- Thinking mode with medium context
- Vision + reasoning
- Balanced performance/cost

**Limitations:**
- Smaller context than glm-4.6
- Conversation IDs cannot be shared with Kimi

---

#### glm-4.5-flash (RECOMMENDED FOR SPEED)
**Context:** 128K (128,000 tokens)  
**Max Output:** 8,192 tokens  
**Vision:** ✅ Yes  
**Web Search:** ✅ Yes (via z.ai SDK)  
**Thinking Mode:** ❌ No  
**File Upload:** ✅ Yes  
**Streaming:** ✅ Yes  
**Function Calling:** ✅ Yes

**Best For:**
- Fast, cost-effective tasks
- Default manager model
- Simple prompts
- Web search tasks
- Vision tasks without thinking

**Limitations:**
- No thinking mode
- Conversation IDs cannot be shared with Kimi

---

#### glm-4.5-air
**Context:** 128K (128,000 tokens)  
**Max Output:** 8,192 tokens  
**Vision:** ✅ Yes  
**Web Search:** ✅ Yes (via z.ai SDK)  
**Thinking Mode:** ✅ Yes (efficient hybrid reasoning)  
**File Upload:** ✅ Yes  
**Streaming:** ✅ Yes  
**Function Calling:** ✅ Yes  
**Aliases:** glm-4.5-x

**Best For:**
- Efficient reasoning tasks
- Thinking mode with lower cost
- Balanced performance
- Vision + reasoning

**Limitations:**
- Conversation IDs cannot be shared with Kimi

---

#### glm-4.5v (VISION SPECIALIST)
**Context:** 64K (65,536 tokens)  
**Max Output:** 8,192 tokens  
**Vision:** ✅ Yes (specialized vision-language model)  
**Web Search:** ✅ Yes (via z.ai SDK)  
**Thinking Mode:** ❌ No  
**File Upload:** ✅ Yes  
**Streaming:** ✅ Yes  
**Function Calling:** ✅ Yes

**Best For:**
- Vision-language multimodal tasks
- Image analysis
- Visual reasoning
- OCR and document understanding

**Limitations:**
- Smaller context (64K)
- No thinking mode
- Conversation IDs cannot be shared with Kimi

---

## 🔑 KEY FACTS

### Web Search Support
- **ALL GLM models support web search** (verified 2025-10-09)
- **ALL Kimi models support web search** (via builtin_function)
- GLM uses z.ai SDK: `https://api.z.ai/api/paas/v4/web_search`
- Kimi uses builtin_function: `$web_search`
- Enable/disable via env vars: `GLM_ENABLE_WEB_BROWSING`, `KIMI_ENABLE_INTERNET_SEARCH`

### File Upload Support
- **ALL models support file uploads** (with different mechanisms)
- Kimi: Requires `TEST_FILES_DIR` environment variable
- GLM: Different file upload mechanism than Kimi
- **CRITICAL:** Conversation IDs cannot be shared between Kimi and GLM platforms

### Thinking Mode Support
- **GLM:** glm-4.6, glm-4.5, glm-4.5-air support thinking mode
- **Kimi:** kimi-thinking-preview supports thinking mode
- Enable via parameter: `"thinking": {"type": "enabled"}`

### Vision Support
- **Kimi:** kimi-k2-0905-preview, kimi-k2-turbo-preview (20MB max)
- **GLM:** ALL GLM models support vision (glm-4.5v is specialist)

---

## 📋 MODEL SELECTION GUIDELINES

### For Simple Prompts:
**Recommended:** `glm-4.5-flash`  
**Why:** Fast, cost-effective, web search support

### For Complex Reasoning:
**Recommended:** `glm-4.6` or `glm-4.5`  
**Why:** Thinking mode, large context, flagship performance

### For Vision Tasks:
**Recommended:** `kimi-k2-0905-preview` or `glm-4.5v`  
**Why:** Strong vision capabilities, multimodal support

### For Large Context:
**Recommended:** `kimi-k2-0905-preview` (256K) or `glm-4.6` (200K)  
**Why:** Largest context windows available

### For High-Speed Generation:
**Recommended:** `kimi-k2-turbo-preview`  
**Why:** 60-100 tokens/sec throughput

### For Cost-Effective Tasks:
**Recommended:** `glm-4.5-flash` or `glm-4.5-air`  
**Why:** Balanced performance/cost ratio

---

## ⚠️ CRITICAL LIMITATIONS

1. **Platform Isolation:** Conversation IDs cannot be shared between Kimi and GLM
2. **File Upload Mechanisms:** Different between Kimi (TEST_FILES_DIR) and GLM
3. **Model Availability:** Depends on provider initialization and API keys
4. **Context Limits:** Exceeding context window causes errors
5. **Thinking Mode:** Only specific models support extended thinking

---

**Last Updated:** 2025-10-12 1:45 PM AEDT  
**Source:** `src/providers/kimi_config.py` and `src/providers/glm_config.py`  
**Status:** ✅ COMPLETE - Task 2.K

