# GLM (Z.ai) API Integration Guide

> **Version:** 2.0 (Updated for zai-sdk)
> **Last Updated:** 2025-11-16
> **Status:** ✅ **Complete - zai-sdk Migration**

## 🎯 Overview

This guide covers GLM (Z.ai) provider integration with the EX-AI MCP Server, including available models, API usage, authentication, and best practices. **Updated to use zai-sdk==0.0.4 exclusively.**

---

## 📊 GLM Provider Overview

### Available Models
- **GLM-4.6** - Latest flagship model (200K context, 8K output)
- **GLM-4.5** - Balanced performance model
- **GLM-4.5-flash** - Fast response model
- **GLM-4** - Stable production model

### API Endpoint
```
https://api.z.ai/api/paas/v4
```

### SDK Integration
```python
from zai import ZaiClient

# Initialize client
client = ZaiClient(
    api_key="your-api-key",
    base_url="https://api.z.ai/api/paas/v4"
)

# Chat completion
response = client.chat.completions.create(
    model="glm-4.5-flash",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

### Authentication
```python
headers = {
    "Authorization": f"Bearer {ZAI_API_KEY}",
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

### Basic Chat (zai-sdk)
```python
from zai import ZaiClient

# Initialize client
client = ZaiClient(
    api_key="your-api-key",
    base_url="https://api.z.ai/api/paas/v4"
)

# Chat completion
response = client.chat.completions.create(
    model="glm-4.6",
    messages=[
        {"role": "user", "content": "Hello, GLM!"}
    ],
    temperature=0.3,
    max_tokens=4000
)

print(response.choices[0].message.content)
```

### Streaming Chat (zai-sdk)
```python
from zai import ZaiClient

client = ZaiClient(api_key="your-api-key")

# Streaming response
stream = client.chat.completions.create(
    model="glm-4.5-flash",
    messages=[{"role": "user", "content": "Tell me a story"}],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

### File Upload (zai-sdk)
```python
from zai import ZaiClient

client = ZaiClient(api_key="your-api-key")

# Upload file
with open("document.pdf", "rb") as f:
    file_response = client.files.create(file=f, purpose="file")
    file_id = file_response.id

# Use file in chat
response = client.chat.completions.create(
    model="glm-4.6",
    messages=[
        {
            "role": "user", 
            "content": [
                {"type": "text", "text": "Summarize this document"},
                {"type": "image_url", "image_url": {"url": f"file://{file_id}"}}
            ]
        }
    ]
)
```

---

## 🔐 Environment Variables

### Primary (Recommended)
```bash
ZAI_API_KEY=your-api-key
ZAI_BASE_URL=https://api.z.ai/api/paas/v4
```

### Backward Compatibility
```bash
GLM_API_KEY=your-api-key
GLM_API_URL=https://api.z.ai/api/paas/v4
```

### Legacy Fallback
```bash
ZHIPUAI_API_KEY=your-api-key
ZHIPUAI_API_URL=https://api.z.ai/api/paas/v4
```

---

## ⚡ Best Practices

### 1. Use zai-sdk Instead of HTTP
- ✅ **Recommended**: Use `from zai import ZaiClient`
- ❌ **Avoid**: Raw HTTP requests (legacy approach)

### 2. Handle Errors Gracefully
```python
from zai import ZaiClient
from zai.core import ZaiError

try:
    client = ZaiClient(api_key="your-key")
    response = client.chat.completions.create(
        model="glm-4.5-flash",
        messages=[{"role": "user", "content": "Hello"}]
    )
except ZaiError as e:
    print(f"Error: {e}")
```

### 3. Configure Timeouts
```python
from zai import ZaiClient

client = ZaiClient(
    api_key="your-key",
    timeout=60.0,  # 60 second timeout
    max_retries=3
)
```

### 4. Use Appropriate Models
- **GLM-4.6**: Complex reasoning, long context
- **GLM-4.5**: Balanced performance
- **GLM-4.5-flash**: Fast responses, real-time chat

---

## 🆕 Recent Changes (2025-11-16)

### Migration from zhipuai to zai-sdk
- ✅ **Updated**: All imports now use `from zai import ZaiClient`
- ✅ **Updated**: Base URL changed to `https://api.z.ai/api/paas/v4`
- ✅ **Updated**: Environment variables prioritize `ZAI_API_KEY`
- ✅ **Maintained**: Backward compatibility with legacy variables

### SDK Capabilities
The zai-sdk provides comprehensive functionality:
- Chat completions with streaming
- File upload and management
- Image processing
- Audio processing
- Web search
- Tool calling
- Batch processing
- Embeddings
- Moderations

---

## 🐛 Troubleshooting

### Common Issues

**Import Error**
```python
# Make sure zai-sdk is installed
pip install zai-sdk==0.0.4

# Then import correctly
from zai import ZaiClient  # Not zhipuai!
```

**Authentication Error**
```python
# Use correct environment variable
import os
api_key = os.getenv("ZAI_API_KEY")  # Primary
# or
api_key = os.getenv("GLM_API_KEY")   # Backward compatibility
```

**API Endpoint**
```python
# Always use the non-China endpoint
base_url = "https://api.z.ai/api/paas/v4"  # ✅ Correct
# base_url = "https://open.bigmodel.cn"       # ❌ Old China endpoint
```

---

## 📚 Additional Resources

- **Z.ai Official Documentation**: https://docs.z.ai
- **zai-sdk GitHub**: https://github.com/zai-org/zai-sdk
- **EX-AI Architecture**: `docs/architecture/SDK_ARCHITECTURE_FINAL.md`

**Last Updated**: 2025-11-16 (zai-sdk migration complete)
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
