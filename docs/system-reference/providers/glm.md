# GLM Provider (ZhipuAI/Z.ai)

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Related:** [kimi.md](kimi.md), [routing.md](routing.md), [../02-provider-architecture.md](../02-provider-architecture.md)

---

## GLM Provider (ZhipuAI/Z.ai)

### Configuration

**Environment Variables:**
```env
# Required
GLM_API_KEY=your_api_key_here
GLM_BASE_URL=https://api.z.ai/api/paas/v4

# Optional
GLM_STREAM_ENABLED=true
GLM_DEFAULT_MODEL=glm-4.6
GLM_TEMPERATURE=0.6
GLM_MAX_TOKENS=65536
```

### Available Models

**GLM-4.6 Series (Latest - September 30, 2025):**
- `glm-4.6` - Flagship model with 200K context window
  - **Context:** 200,000 tokens (expanded from 128K)
  - **Pricing:** $0.60 input / $2.20 output per million tokens
  - **Performance:** Near parity with Claude Sonnet 4 (48.6% win rate)
  - **Features:** Advanced agentic abilities, superior coding, refined writing
  - **Token Efficiency:** ~15% fewer tokens than GLM-4.5

**GLM-4.5 Series:**
- `glm-4.5` - Previous flagship with 128K context
- `glm-4.5-air` - Lightweight version
- `glm-4.5-x` - Extended capabilities
- `glm-4.5-airx` - Air extended
- `glm-4.5-flash` - Fast, cost-effective (default manager)

**GLM-4.6V Series (Vision):**
- `glm-4.6-v` - Vision model with multimodal support (images, videos)
  - **Context:** 128K tokens
  - **Features:** Vision (image_url, video_url), function calling
  - **Use Case:** Image/video analysis

**GLM-4.5V Series (Vision - Legacy):**
- `glm-4.5v` - Vision model with multimodal support
- `glm-4.5v-plus` - Enhanced vision capabilities

**Legacy:**
- `glm-4-32b-0414-128k` - 32B parameter model

### API Integration

**Note:** EX-AI-MCP-Server uses direct HTTP requests, NOT zai-sdk

**Direct HTTP (Recommended):**
```python
import requests

url = "https://api.z.ai/api/paas/v4/chat/completions"

payload = {
    "model": "glm-4.6",
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ],
    "temperature": 0.6,
    "max_tokens": 65536,
    "stream": False
}

headers = {
    "Authorization": "Bearer <GLM_API_KEY>",
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)
print(response.json())
```

**Streaming:**
```python
stream = client.chat.completions.create(
    model="glm-4.6",
    messages=[...],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

**Tool Calling:**
```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"}
                },
                "required": ["location"]
            }
        }
    }
]

response = client.chat.completions.create(
    model="glm-4.6",
    messages=[...],
    tools=tools,
    tool_choice="auto"
)
```

### HTTP Fallback

**Direct API Call:**
```python
import httpx

response = httpx.post(
    "https://api.z.ai/api/paas/v4/chat/completions",
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    },
    json={
        "model": "glm-4.6",
        "messages": [...],
        "temperature": 0.6,
        "max_tokens": 65536,
        "stream": False
    }
)
```

**SSE Streaming:**
```python
with httpx.stream(
    "POST",
    "https://api.z.ai/api/paas/v4/chat/completions",
    headers={...},
    json={..., "stream": True}
) as stream:
    for line in stream.iter_lines():
        if line.startswith("data: "):
            data = line[6:]
            if data == "[DONE]":
                break
            chunk = json.loads(data)
            # Process chunk
```

### Implementation Pattern

**Dual SDK/HTTP Approach:**
```python
def generate_content(
    sdk_client: Any,
    http_client: Any,
    prompt: str,
    model_name: str,
    use_sdk: bool = True,
    **kwargs
) -> ModelResponse:
    """Generate content with SDK/HTTP fallback."""
    
    if use_sdk and sdk_client:
        try:
            # Primary: Use SDK
            response = sdk_client.chat.completions.create(
                model=model_name,
                messages=[...],
                **kwargs
            )
            return response
        except Exception as e:
            logger.warning(f"SDK failed: {e}, falling back to HTTP")
            use_sdk = False
    
    if not use_sdk and http_client:
        # Fallback: Use HTTP
        response = http_client.post(
            f"{base_url}/chat/completions",
            json={...}
        )
        return response
```

---
