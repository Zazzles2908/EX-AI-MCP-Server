# GLM (ZhipuAI) API Integration Guide

> **Version:** 1.0.0
> **Last Updated:** 2025-11-10
> **Status:** ✅ **Complete**

## 🎯 Overview

This guide covers GLM (ZhipuAI) provider integration with the EX-AI MCP Server, including available models, API usage, authentication, and best practices.

---

## 📊 GLM Provider Overview

### Available Models
- **GLM-4.6** - Latest flagship model (128K context, 8K output)
- **GLM-4.5** - Balanced performance model
- **GLM-4.5-flash** - Fast response model
- **GLM-4** - Stable production model

### API Endpoint
```
https://z.ai/api/paas/v4/chat/completions
```

### Authentication
```python
headers = {
    "Authorization": f"Bearer {GLM_API_KEY}",
    "Content-Type": "application/json"
}
```

---

## 🔧 Model Configuration

### GLM-4.6 (Recommended)
```python
config = {
    "model": "glm-4.6",
    "messages": messages,
    "temperature": 0.3,
    "max_tokens": 8000,
    "top_p": 0.9,
    "stream": False
}
```

### GLM-4.5-flash (Fast)
```python
config = {
    "model": "glm-4.5-flash",
    "messages": messages,
    "temperature": 0.3,
    "max_tokens": 4000,
    "top_p": 0.9
}
```

---

## 💻 Code Examples

### Basic Chat
```python
import requests

response = requests.post(
    "https://z.ai/api/paas/v4/chat/completions",
    headers={
        "Authorization": f"Bearer {GLM_API_KEY}",
        "Content-Type": "application/json"
    },
    json={
        "model": "glm-4.6",
        "messages": [
            {"role": "user", "content": "Hello, GLM!"}
        ]
    }
)

data = response.json()
print(data["choices"][0]["message"]["content"])
```

### With Streaming
```python
import sseclient

response = requests.post(
    "https://z.ai/api/paas/v4/chat/completions",
    headers={
        "Authorization": f"Bearer {GLM_API_KEY}",
        "Content-Type": "application/json"
    },
    json={
        "model": "glm-4.6",
        "messages": [{"role": "user", "content": "Write a long story"}],
        "stream": True
    },
    stream=True
)

for line in response.iter_lines():
    if line:
        data = json.loads(line.decode('utf-8').split('data: ')[1])
        if "choices" in data:
            content = data["choices"][0]["delta"].get("content", "")
            print(content, end="", flush=True)
```

---

## 🔑 API Key Management

### Getting Your API Key
1. Visit: https://z.ai/manage-apikey/apikey-list
2. Login to your ZhipuAI account
3. Navigate to API Keys section
4. Generate new API key
5. Copy and store securely

### Environment Configuration
```bash
# .env file
GLM_API_KEY=your_glm_api_key_here
```

### Key Rotation
- Rotate every 90 days
- Monitor usage in dashboard
- Set up usage alerts
- Revoke old keys immediately

---

## 📊 Rate Limits & Pricing

### Rate Limits
- **Requests per minute**: 100 (standard)
- **Tokens per minute**: 10,000
- **Concurrent requests**: 10

### Pricing (per 1K tokens)
- **GLM-4.6**: $0.05 (input), $0.10 (output)
- **GLM-4.5**: $0.03 (input), $0.06 (output)
- **GLM-4.5-flash**: $0.01 (input), $0.02 (output)

---

## 🎯 Best Practices

### 1. Model Selection
```python
# Use GLM-4.6 for complex reasoning
if task == "complex_analysis":
    model = "glm-4.6"
    
# Use GLM-4.5-flash for simple tasks
elif task == "quick_response":
    model = "glm-4.5-flash"
```

### 2. Error Handling
```python
try:
    response = requests.post(API_ENDPOINT, json=data, headers=headers)
    response.raise_for_status()
    return response.json()
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
    return {"error": str(e)}
```

### 3. Token Management
```python
def count_tokens(text):
    # Rough estimation: 1 token ≈ 4 characters
    return len(text) // 4

def check_limit(text, max_tokens=8000):
    if count_tokens(text) > max_tokens:
        raise ValueError(f"Text exceeds {max_tokens} tokens")
```

---

## 🔄 Migration from OpenAI

### 10-Step Migration Checklist

1. **Update endpoint URL**
   ```python
   # Old
   "https://api.openai.com/v1/chat/completions"
   
   # New
   "https://z.ai/api/paas/v4/chat/completions"
   ```

2. **Change model names**
   ```python
   # Old
   "model": "gpt-4"
   
   # New
   "model": "glm-4.6"
   ```

3. **Update headers**
   ```python
   headers = {
       "Authorization": f"Bearer {GLM_API_KEY}",
       "Content-Type": "application/json"
   }
   ```

4. **Adjust parameters**
   - `max_tokens` - same usage
   - `temperature` - same range (0-1)
   - `top_p` - same usage

5. **Test compatibility**
   - Verify response format
   - Check streaming behavior
   - Test error handling

6. **Update streaming**
   ```python
   # GLM uses Server-Sent Events
   for line in response.iter_lines():
       # Parse SSE format
   ```

7. **Monitor usage**
   - Set up GLM dashboard monitoring
   - Track token consumption
   - Set budget alerts

8. **Handle rate limits**
   - Implement exponential backoff
   - Use retry logic
   - Queue requests

9. **Update documentation**
   - Change API references
   - Update examples
   - Train team

10. **Gradual rollout**
    - Start with non-critical features
    - Monitor performance
    - Full migration

---

## 🔍 Troubleshooting

### Common Issues

**Issue: "Invalid API key"**
- Verify key is correct
- Check key hasn't expired
- Ensure proper Bearer format

**Issue: "Rate limit exceeded"**
- Implement exponential backoff
- Reduce request frequency
- Consider upgrading plan

**Issue: "Invalid model name"**
- Check available models list
- Use correct model ID
- Verify model is active

### Error Codes
- `401`: Invalid API key
- `429`: Rate limit exceeded
- `500`: Server error
- `503`: Service unavailable

---

## 📚 Related Documentation

- **Kimi API**: [02_kimi_api.md](02_kimi_api.md)
- **Provider Selection**: [03_provider_selection.md](03_provider_selection.md)
- **MCP Tools**: [../mcp-tools-reference/](../mcp-tools-reference/)
- **System Architecture**: [../../../01-architecture-overview/01_system_architecture.md../../../01-architecture-overview/01_system_architecture.md)

---

**Document Version:** 1.0.0
**Created:** 2025-11-10
**Author:** EX-AI MCP Server API Team
**Status:** ✅ **Complete - GLM API Integration Guide**
