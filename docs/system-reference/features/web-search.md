# Web Search Integration

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Related:** [../04-features-and-capabilities.md](../04-features-and-capabilities.md), [../providers/glm.md](../providers/glm.md)

---

## Overview

Native GLM web search integration with automatic triggering and multiple search engine support. Web search is automatically triggered by query content without manual intervention.

**Note:** Web search is only available for GLM provider, not Kimi.

---

## Configuration

### Environment Variables

```env
GLM_ENABLE_WEB_BROWSING=true
```

---

## Search Engines

- `search_pro_jina` (default) - Jina AI search
- `search_pro_bing` - Bing search

---

## Parameters

**Search Configuration:**
```json
{
  "tools": [
    {
      "type": "web_search",
      "web_search": {
        "search_engine": "search_pro_jina",
        "search_recency_filter": "oneWeek",
        "content_size": "medium",
        "result_sequence": "after",
        "search_result": true
      }
    }
  ]
}
```

**Parameters:**
- `search_engine`: Which search engine to use
- `search_recency_filter`: Time range (oneDay, oneWeek, oneMonth, oneYear, noLimit)
- `domain_whitelist`: Limit to specific domains
- `content_size`: Summary length (medium: 400-600 chars, high: 2500 chars)
- `result_sequence`: Show results before or after response
- `search_result`: Whether to return search results
- `require_search`: Force model to use search results
- `search_prompt`: Custom prompt for processing results

---

## Usage

Web search is automatically triggered when the query content suggests it would be helpful. No manual search required.

---

## Provider Support

| Provider | Web Search Support |
|----------|-------------------|
| GLM | ✅ Native integration |
| Kimi | ❌ Not available |

---

## Related Documentation

- [../04-features-and-capabilities.md](../04-features-and-capabilities.md) - Features overview
- [../providers/glm.md](../providers/glm.md) - GLM provider details
- [../api/web-search.md](../api/web-search.md) - Web search API

