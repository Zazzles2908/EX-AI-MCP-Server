# Chat Completions API

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Related:** [../05-api-endpoints-reference.md](../05-api-endpoints-reference.md), [authentication.md](authentication.md)

---

## Overview

Primary endpoint for conversational AI interactions. OpenAI-compatible API for both GLM and Kimi providers.

---

## Endpoint

**POST** `/chat/completions`

**Base URLs:**
- GLM: `https://api.z.ai/v1/chat/completions`
- Kimi: `https://api.moonshot.ai/v1/chat/completions`

---

## Request

### Basic Request

```json
{
  "model": "glm-4.6",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"}
  ],
  "temperature": 0.7,
  "max_tokens": 2048
}
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `model` | string | Yes | Model to use (e.g., "glm-4.6", "kimi-k2-0905-preview") |
| `messages` | array | Yes | Array of message objects |
| `temperature` | float | No | Sampling temperature (0.0-1.0, default: 0.7) |
| `max_tokens` | integer | No | Maximum tokens to generate |
| `stream` | boolean | No | Enable streaming (default: false) |
| `tools` | array | No | Function calling tools |
| `tool_choice` | string | No | Tool selection strategy ("auto", "none", specific tool) |

---

## Response

### Non-Streaming Response

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
        "content": "Hello! How can I help you today?"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 20,
    "total_tokens": 30
  }
}
```

### Streaming Response

```
data: {"id":"chatcmpl-123","object":"chat.completion.chunk","created":1677652288,"model":"glm-4.6","choices":[{"index":0,"delta":{"content":"Hello"},"finish_reason":null}]}

data: {"id":"chatcmpl-123","object":"chat.completion.chunk","created":1677652288,"model":"glm-4.6","choices":[{"index":0,"delta":{"content":"!"},"finish_reason":null}]}

data: {"id":"chatcmpl-123","object":"chat.completion.chunk","created":1677652288,"model":"glm-4.6","choices":[{"index":0,"delta":{},"finish_reason":"stop"}]}

data: [DONE]
```

---

## Examples

### Python (OpenAI SDK)

```python
from openai import OpenAI

client = OpenAI(
    api_key="your_api_key",
    base_url="https://api.z.ai/v1"
)

response = client.chat.completions.create(
    model="glm-4.6",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ]
)

print(response.choices[0].message.content)
```

### Streaming

```python
response = client.chat.completions.create(
    model="glm-4.6",
    messages=[...],
    stream=True
)

for chunk in response:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

---

## Related Documentation

- [../05-api-endpoints-reference.md](../05-api-endpoints-reference.md) - API endpoints overview
- [authentication.md](authentication.md) - Authentication details
- [../features/streaming.md](../features/streaming.md) - Streaming support
- [../features/tool-calling.md](../features/tool-calling.md) - Tool calling

