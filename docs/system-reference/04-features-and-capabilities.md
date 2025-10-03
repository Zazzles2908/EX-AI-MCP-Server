# Features and Capabilities

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Related:** [02-provider-architecture.md](02-provider-architecture.md), [05-api-endpoints-reference.md](05-api-endpoints-reference.md)

---

## Overview

The EX-AI-MCP-Server provides comprehensive AI capabilities through the ZhipuAI (Z.ai) and Moonshot (Kimi) platforms. This document provides an overview of all available features with links to detailed documentation.

**Upgrade Status:** Wave 2 (Synthesis & UX Improvements) - IN PROGRESS  
**Target SDK:** zai-sdk v0.0.4  
**Breaking Changes:** **NONE** - 100% backward compatible upgrade

---

## Core Features

### Streaming Support
Real-time response generation with token-by-token delivery for better user experience.

**📖 For complete streaming documentation, see:** [features/streaming.md](features/streaming.md)

---

### Web Search Integration
Native GLM web search with automatic triggering and multiple search engine support.

**📖 For complete web search documentation, see:** [features/web-search.md](features/web-search.md)

---

### Multimodal Support
Process images, audio, video, and files alongside text for comprehensive AI interactions.

**📖 For complete multimodal documentation, see:** [features/multimodal.md](features/multimodal.md)

---

### Caching
Prompt caching and advanced caching strategies for improved performance and cost reduction.

**📖 For complete caching documentation, see:** [features/caching.md](features/caching.md)

---

### Tool Calling
OpenAI-compatible function calling for agentic workflows and tool integration.

**📖 For complete tool calling documentation, see:** [features/tool-calling.md](features/tool-calling.md)

---

## Feature Comparison

| Feature | GLM Provider | Kimi Provider |
|---------|--------------|---------------|
| **Streaming** | ✅ SSE streaming | ✅ SSE streaming |
| **Web Search** | ✅ Native integration | ❌ Not available |
| **Multimodal** | ✅ Images, audio, video, files | ❌ Text only |
| **Caching** | ✅ Prompt caching | ✅ Advanced caching |
| **Tool Calling** | ✅ OpenAI-compatible | ✅ OpenAI-compatible |
| **Context Window** | 200K tokens (GLM-4.6) | 256K tokens (kimi-k2-0905-preview) |

---

## Configuration

### Environment Variables

**GLM Provider:**
```env
GLM_STREAM_ENABLED=true
GLM_ENABLE_WEB_BROWSING=true
GLM_DEFAULT_MODEL=glm-4.6
```

**Kimi Provider:**
```env
KIMI_STREAM_ENABLED=true
KIMI_DEFAULT_MODEL=kimi-k2-0905-preview
```

---

## Related Documentation

- [features/streaming.md](features/streaming.md) - Streaming implementation details
- [features/web-search.md](features/web-search.md) - Web search configuration
- [features/multimodal.md](features/multimodal.md) - Multimodal capabilities
- [features/caching.md](features/caching.md) - Caching strategies
- [features/tool-calling.md](features/tool-calling.md) - Tool calling patterns
- [02-provider-architecture.md](02-provider-architecture.md) - Provider details
- [05-api-endpoints-reference.md](05-api-endpoints-reference.md) - API endpoints

