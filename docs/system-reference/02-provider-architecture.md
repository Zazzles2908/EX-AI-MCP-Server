# Provider Architecture

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Related:** [01-system-overview.md](01-system-overview.md), [04-features-and-capabilities.md](04-features-and-capabilities.md)

---

## Overview

The EX-AI-MCP-Server implements a **dual-provider architecture** with intelligent routing between GLM (ZhipuAI/Z.ai) and Kimi (Moonshot) providers. This design maximizes cost-efficiency, performance, and reliability through a manager-first routing strategy and dual SDK/HTTP fallback pattern.

---

## Provider Comparison

| Feature | GLM Provider | Kimi Provider |
|---------|--------------|---------------|
| **SDK** | zai-sdk v0.0.4 | Moonshot API |
| **Flagship Model** | GLM-4.6 (200K context) | kimi-k2-0905-preview (256K context) |
| **Base URL** | https://api.z.ai/v1 | https://api.moonshot.ai/v1 |
| **Pricing** | $0.60/$2.20 per M tokens | $0.60/$2.50 per M tokens |
| **Web Search** | Native integration | Not available |
| **Streaming** | SSE streaming | SSE streaming |
| **Tool Calling** | OpenAI-compatible | OpenAI-compatible |
| **Best For** | Web search, cost optimization | Tool use, coding, agentic workflows |
| **Multimodal** | Images, audio, video, files | Text only |
| **Caching** | Prompt caching | Advanced caching |

---

## Providers

### GLM Provider (ZhipuAI/Z.ai)

**Primary Use Cases:**
- Web search integration
- Cost-effective general tasks
- Multimodal capabilities (images, audio, video)
- Fast routing decisions (GLM-4.5-flash as manager)

**📖 For complete GLM provider documentation, see:** [providers/glm.md](providers/glm.md)

---

### Kimi Provider (Moonshot)

**Primary Use Cases:**
- Quality reasoning and analysis
- Long context processing (256K tokens)
- Tool use and agentic workflows
- Code generation and debugging

**📖 For complete Kimi provider documentation, see:** [providers/kimi.md](providers/kimi.md)

---

## Agentic Routing

**Manager-First Architecture:**
- **Default Manager:** GLM-4.5-flash (fast, cost-effective routing decisions)
- **Routing Logic:** Intelligent task classification and model selection
- **Escalation:** Simple tasks → GLM-4.5-flash, Complex tasks → GLM-4.6 or Kimi
- **Benefits:** Optimal cost/performance balance, automatic complexity assessment

**📖 For complete routing documentation, see:** [providers/routing.md](providers/routing.md)

---

## Architecture Patterns

### Dual SDK/HTTP Fallback

**Pattern:**
```python
try:
    # Primary: Use SDK
    response = client.chat.completions.create(...)
except Exception:
    # Fallback: Use HTTP
    response = httpx.post(...)
```

**Benefits:**
- Reliability through redundancy
- Graceful degradation
- Compatibility across SDK versions

---

## Related Documentation

- [providers/glm.md](providers/glm.md) - Complete GLM provider details
- [providers/kimi.md](providers/kimi.md) - Complete Kimi provider details
- [providers/routing.md](providers/routing.md) - Agentic routing logic
- [04-features-and-capabilities.md](04-features-and-capabilities.md) - Feature details
- [05-api-endpoints-reference.md](05-api-endpoints-reference.md) - API endpoints

