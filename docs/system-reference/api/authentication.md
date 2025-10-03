# Authentication

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Related:** [../05-api-endpoints-reference.md](../05-api-endpoints-reference.md), [../02-provider-architecture.md](../02-provider-architecture.md)

---

## Overview

Bearer token authentication for all API requests. Both GLM and Kimi providers use the same authentication mechanism.

---

## Configuration

### Environment Variables

**GLM Provider:**
```env
GLM_API_KEY=your_zhipuai_api_key
```

**Kimi Provider:**
```env
KIMI_API_KEY=your_moonshot_api_key
```

---

## Authentication Methods

### Bearer Token (Recommended)

**HTTP Header:**
```http
Authorization: Bearer your_api_key
```

**Python Example:**
```python
from openai import OpenAI

# GLM
glm_client = OpenAI(
    api_key="your_zhipuai_api_key",
    base_url="https://api.z.ai/v1"
)

# Kimi
kimi_client = OpenAI(
    api_key="your_moonshot_api_key",
    base_url="https://api.moonshot.ai/v1"
)
```

---

## Security Best Practices

### API Key Management

- **Never commit API keys** to version control
- **Use environment variables** for API keys
- **Rotate keys regularly** for security
- **Use separate keys** for development and production
- **Monitor API usage** for anomalies

### Environment Files

**.env (Local Development):**
```env
GLM_API_KEY=your_zhipuai_api_key
KIMI_API_KEY=your_moonshot_api_key
```

**.env.example (Template):**
```env
GLM_API_KEY=your_zhipuai_api_key_here
KIMI_API_KEY=your_moonshot_api_key_here
```

---

## Error Handling

### Invalid API Key

**Response:**
```json
{
  "error": {
    "message": "Invalid API key",
    "type": "invalid_request_error",
    "code": "invalid_api_key"
  }
}
```

### Missing API Key

**Response:**
```json
{
  "error": {
    "message": "Missing API key",
    "type": "invalid_request_error",
    "code": "missing_api_key"
  }
}
```

---

## Related Documentation

- [../05-api-endpoints-reference.md](../05-api-endpoints-reference.md) - API endpoints overview
- [../02-provider-architecture.md](../02-provider-architecture.md) - Provider details
- [chat-completions.md](chat-completions.md) - Chat completions API

