# Kimi (Moonshot AI) API Integration Guide

> **Version:** 2.0 (Updated with K2 models)
> **Last Updated:** 2025-11-16
> **Status:** ✅ **Complete - K2 Models Added**

## 🎯 Overview

This guide covers Kimi (Moonshot AI) provider integration with the EX-AI MCP Server, including available models, file processing, vision capabilities, and best practices. **Updated to include K2 powerhouse models.**

---

## 📊 Kimi Provider Overview

### Available Models

#### 🚀 **K2 POWERHOUSE MODELS (TOP PRIORITY)**
- **kimi-k2-thinking-turbo** - 256K context, thinking mode (RECOMMENDED)
- **kimi-k2-thinking** - 256K context, thinking mode
- **kimi-k2-turbo-preview** - 256K context, high speed
- **kimi-k2-0905-preview** - 256K context

#### 🧠 **K2 THINKING MODELS (PREMIUM)**
- **kimi-thinking-preview** - 128K context with thinking capabilities

#### 📱 **LEGACY MODELS (Still Supported)**
- **moonshot-v1-128k** - 128K context, 8K output
- **moonshot-v1-32k** - 32K context, 8K output  
- **moonshot-v1-8k** - 8K context, 8K output

#### 🔄 **LATEST VARIANTS**
- **kimi-latest** - Auto-selects best available model
- **kimi-latest-8k** - Latest 8K context model
- **kimi-latest-32k** - Latest 32K context model
- **kimi-latest-128k** - Latest 128K context model

### API Endpoint
```
https://api.moonshot.ai/v1/chat/completions
```

### SDK Integration
```python
from openai import AsyncOpenAI

# Initialize client (Kimi uses OpenAI-compatible SDK)
client = AsyncOpenAI(
    api_key="your-api-key",
    base_url="https://api.moonshot.ai/v1"
)

# Chat completion
response = await client.chat.completions.create(
    model="kimi-k2-thinking-turbo",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

### Authentication
```python
headers = {
    "Authorization": f"Bearer {KIMI_API_KEY}",
    "Content-Type": "application/json"
}
```

---

## 🔧 Model Configuration

### K2 Thinking Models (Recommended)
```python
config = {
    "model": "kimi-k2-thinking-turbo",
    "messages": messages,
    "temperature": 0.3,
    "max_tokens": 8192,
    "top_p": 0.9,
    "stream": False
}
```

### Legacy Models
```python
config = {
    "model": "moonshot-v1-128k",
    "messages": messages,
    "temperature": 0.3,
    "max_tokens": 8192,
    "top_p": 0.9
}
```

---

## 💻 Code Examples

### Basic Chat
```python
from openai import AsyncOpenAI

client = AsyncOpenAI(
    api_key="your-api-key",
    base_url="https://api.moonshot.ai/v1"
)

response = await client.chat.completions.create(
    model="kimi-k2-thinking-turbo",
    messages=[
        {"role": "user", "content": "Hello, Kimi!"}
    ],
    temperature=0.3,
    max_tokens=4000
)

print(response.choices[0].message.content)
```

### Streaming Chat
```python
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key="your-key", base_url="https://api.moonshot.ai/v1")

# Streaming response
stream = await client.chat.completions.create(
    model="kimi-k2-thinking",
    messages=[{"role": "user", "content": "Tell me a story"}],
    stream=True
)

async for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

### Image Processing
```python
import base64

# Encode image
with open("image.jpg", "rb") as f:
    image_b64 = base64.b64encode(f.read()).decode()

response = await client.chat.completions.create(
    model="kimi-k2-thinking-turbo",
    messages=[
        {
            "role": "user", 
            "content": [
                {"type": "text", "text": "Describe this image"},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}}
            ]
        }
    ]
)
```

---

## 🔐 Environment Variables

### Configuration
```bash
KIMI_API_KEY=your-api-key
KIMI_BASE_URL=https://api.moonshot.ai/v1
```

### Default Settings
- **Context Window**: Varies by model (8K to 256K)
- **Max Output Tokens**: 8K for most models
- **Temperature Range**: 0.0 to 2.0
- **Image Support**: Yes (up to 100MB)
- **Function Calling**: Yes

---

## ⚡ Best Practices

### 1. Use K2 Models for Premium Features
- ✅ **Recommended**: `kimi-k2-thinking-turbo` for complex reasoning
- ✅ **Recommended**: `kimi-k2-thinking` for balanced thinking mode
- ⚠️ **Legacy**: `moonshot-v1-*` for backward compatibility

### 2. Handle Errors Gracefully
```python
from openai import AsyncOpenAI
from openai import APIError, APITimeoutError

try:
    client = AsyncOpenAI(api_key="your-key", base_url="https://api.moonshot.ai/v1")
    response = await client.chat.completions.create(
        model="kimi-k2-thinking-turbo",
        messages=[{"role": "user", "content": "Hello"}]
    )
except APIError as e:
    print(f"API Error: {e}")
except APITimeoutError:
    print("Request timed out")
```

### 3. Configure Timeouts
```python
from openai import AsyncOpenAI

client = AsyncOpenAI(
    api_key="your-key",
    base_url="https://api.moonshot.ai/v1",
    timeout=60.0  # 60 second timeout
)
```

### 4. Use Appropriate Models
- **K2 Thinking Models**: Complex reasoning, long context, thinking mode
- **K2 Turbo**: Fast responses with K2 capabilities
- **Legacy Models**: Simple tasks, backward compatibility

---

## 🆕 Recent Changes (2025-11-16)

### K2 Model Integration
- ✅ **Added**: K2 powerhouse models (256K context)
- ✅ **Added**: K2 Thinking models with extended reasoning
- ✅ **Updated**: Premium model recommendations
- ✅ **Maintained**: Legacy moonshot-v1 compatibility

### Model Capabilities
- **K2 Models**: 256K context, thinking mode, image processing
- **Legacy Models**: 8K-128K context, standard features
- **All Models**: Function calling, streaming, system prompts

---

## 📈 Model Selection Guide

### For Complex Reasoning
```python
model = "kimi-k2-thinking-turbo"  # Best for complex problems
```

### For Speed
```python
model = "kimi-k2-turbo-preview"  # Fast K2 model
```

### For Long Context
```python
model = "kimi-k2-thinking"  # 256K context
```

### For Simple Tasks
```python
model = "moonshot-v1-32k"  # Legacy but reliable
```

---

## 🐛 Troubleshooting

### Common Issues

**Model Not Found**
```python
# Use exact model names
model = "kimi-k2-thinking-turbo"  # ✅ Correct
model = "kimi-k2"               # ❌ Too generic
```

**Context Window Too Small**
```python
# For long conversations, use K2 models
model = "kimi-k2-thinking-turbo"  # 256K context
model = "moonshot-v1-128k"        # 128K context
```

**API Endpoint**
```python
# Always use the correct endpoint
base_url = "https://api.moonshot.ai/v1"  # ✅ Correct
```

---

## 📚 Additional Resources

- **Moonshot AI Documentation**: https://platform.moonshot.ai/docs
- **EX-AI Architecture**: `docs/architecture/SDK_ARCHITECTURE_FINAL.md`

**Last Updated**: 2025-11-16 (K2 model integration complete)
