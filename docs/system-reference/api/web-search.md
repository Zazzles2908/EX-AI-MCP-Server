# Web Search API

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Related:** [../05-api-endpoints-reference.md](../05-api-endpoints-reference.md), [../features/web-search.md](../features/web-search.md)

---

## Overview

Native web search integration for GLM provider. Web search is automatically triggered by query content without manual intervention.

**Note:** Web search is only available for GLM provider, not Kimi.

---

## Endpoint

**POST** `/api/paas/v4/web_search`

**Base URL:**
- GLM: `https://api.z.ai/api/paas/v4/web_search`

---

## Configuration

### Environment Variables

```env
GLM_ENABLE_WEB_BROWSING=true
```

---

## Request

### Basic Request

```json
{
  "model": "glm-4.6",
  "messages": [
    {"role": "user", "content": "What's the latest news about AI?"}
  ],
  "tools": [
    {
      "type": "web_search",
      "web_search": {
        "search_engine": "search_pro_jina",
        "search_recency_filter": "oneWeek"
      }
    }
  ]
}
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `search_engine` | string | Search engine ("search_pro_jina", "search_pro_bing") |
| `search_recency_filter` | string | Time range ("oneDay", "oneWeek", "oneMonth", "oneYear", "noLimit") |
| `domain_whitelist` | array | Limit to specific domains |
| `content_size` | string | Summary length ("medium": 400-600 chars, "high": 2500 chars) |
| `result_sequence` | string | Show results "before" or "after" response |
| `search_result` | boolean | Whether to return search results |
| `require_search` | boolean | Force model to use search results |
| `search_prompt` | string | Custom prompt for processing results |

---

## Response

```json
{
  "id": "chatcmpl-123",
  "object": "chat.completion",
  "created": 1677652288,
  "model": "glm-4.6",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Based on recent news...",
        "web_search_results": [
          {
            "title": "Latest AI Developments",
            "url": "https://example.com/ai-news",
            "snippet": "Recent advancements in AI..."
          }
        ]
      },
      "finish_reason": "stop"
    }
  ]
}
```

---

## Examples

### Python (OpenAI SDK)

```python
from openai import OpenAI

client = OpenAI(
    api_key="your_glm_api_key",
    base_url="https://api.z.ai/v1"
)

response = client.chat.completions.create(
    model="glm-4.6",
    messages=[
        {"role": "user", "content": "What's the latest news about AI?"}
    ],
    tools=[
        {
            "type": "web_search",
            "web_search": {
                "search_engine": "search_pro_jina",
                "search_recency_filter": "oneWeek"
            }
        }
    ]
)

print(response.choices[0].message.content)
```

---

## Search Engines

### Jina AI Search (Default)
- **ID:** `search_pro_jina`
- **Features:** Fast, comprehensive results
- **Best For:** General web search

### Bing Search
- **ID:** `search_pro_bing`
- **Features:** Microsoft Bing integration
- **Best For:** Enterprise search

---

## Provider Support

| Provider | Web Search Support |
|----------|-------------------|
| GLM | ✅ Native integration |
| Kimi | ❌ Not available |

---

## Related Documentation

- [../05-api-endpoints-reference.md](../05-api-endpoints-reference.md) - API endpoints overview
- [../features/web-search.md](../features/web-search.md) - Web search features
- [../providers/glm.md](../providers/glm.md) - GLM provider details
- [chat-completions.md](chat-completions.md) - Chat completions API

