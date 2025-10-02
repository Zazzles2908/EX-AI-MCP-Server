# GLM-4.6 and Z.ai SDK Changes - Comprehensive Research

**Date:** 2025-10-01  
**Research Conducted By:** Augment Agent  
**Purpose:** Deep dive into z.ai upgrade with GLM-4.6 model and zai-sdk 0.0.4 library

---

## Executive Summary

Z.ai (ZhipuAI) has released significant updates including:
- **GLM-4.6**: New flagship model with 355B total parameters, 32B active parameters
- **zai-sdk 0.0.4**: Latest Python SDK with enhanced features and new client classes
- **New Models**: GLM-4.5-Air, GLM-4.5V (vision), and enhanced capabilities
- **API Enhancements**: Assistant API, video generation, improved streaming

---

## GLM-4.6 Model Release

### Model Architecture
- **Total Parameters:** 355 billion
- **Active Parameters:** 32 billion (MoE architecture)
- **Context Length:** 128K tokens (extended from previous versions)
- **Architecture Type:** Hybrid Reasoning Model with MoE (Mixture of Experts)

### Key Features

#### 1. Hybrid Reasoning Modes
- **Thinking Mode:** For complex reasoning and tool using
- **Non-Thinking Mode:** For instant responses
- Automatically selects appropriate mode based on task complexity

#### 2. Unified Capabilities
GLM-4.6 unifies three critical capabilities in a single model:
- **Reasoning:** Advanced logical and mathematical reasoning
- **Coding:** Full-stack development, debugging, code generation
- **Agentic Tasks:** Tool calling, web browsing, multi-turn interactions

#### 3. Performance Benchmarks

**Agentic Tasks:**
- TAU-bench-Retail: 79.7% (vs Claude 4 Sonnet: 80.5%)
- TAU-bench-Airline: 60.4% (vs Claude 4 Sonnet: 60.0%)
- BFCL v3: 77.8% (vs Claude 4 Sonnet: 75.2%)
- BrowseComp: 26.4% (vs Claude 4 Opus: 18.8%)

**Reasoning:**
- MMLU Pro: 84.6%
- AIME24: 91.0%
- MATH 500: 98.2%
- GPQA: 79.1%

**Coding:**
- SWE-bench Verified: 64.2%
- Terminal-Bench: 37.5%
- LiveCodeBench: 72.9%

### Model Variants

#### GLM-4.6 (Flagship)
- 355B total params, 32B active
- Best for: Complex reasoning, agentic tasks, full-stack coding
- Context: 128K tokens

#### GLM-4.5-Air
- 106B total params, 12B active
- Best for: Fast responses, cost-effective operations
- Context: 128K tokens
- Performance: Competitive with larger models on many tasks

#### GLM-4.5V (Vision)
- Multimodal capabilities
- Image understanding and analysis
- Best for: Visual reasoning, image-based tasks

---

## zai-sdk 0.0.4 Release

### Installation
```bash
# Install latest version
pip install zai-sdk==0.0.4

# Or upgrade from existing
pip install --upgrade zai-sdk==0.0.4
```

### New Client Classes

#### ZaiClient (International/Overseas)
```python
from zai import ZaiClient

client = ZaiClient(
    api_key="your-api-key",
    base_url="https://api.z.ai/api/paas/v4/"  # Default
)
```

#### ZhipuAiClient (Mainland China)
```python
from zai import ZhipuAiClient

client = ZhipuAiClient(
    api_key="your-api-key",
    base_url="https://open.bigmodel.cn/api/paas/v4/"  # Default
)
```

### Core Features

#### 1. Chat Completions
```python
response = client.chat.completions.create(
    model="glm-4.6",
    messages=[
        {"role": "user", "content": "Hello, Z.ai!"}
    ]
)
```

#### 2. Streaming Support
```python
response = client.chat.completions.create(
    model='glm-4.6',
    messages=[...],
    stream=True
)

for chunk in response:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end='')
```

#### 3. Tool Calling / Web Search
```python
response = client.chat.completions.create(
    model='glm-4.6',
    messages=[...],
    tools=[
        {
            'type': 'web_search',
            'web_search': {
                'search_query': 'What is artificial intelligence?',
                'search_result': True,
            },
        }
    ]
)
```

#### 4. Multimodal Chat (Vision)
```python
import base64

def encode_image(image_path):
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

base64_image = encode_image('image.jpeg')

response = client.chat.completions.create(
    model='glm-4v',
    messages=[
        {
            'role': 'user',
            'content': [
                {'type': 'text', 'text': "What's in this image?"},
                {'type': 'image_url', 'image_url': {'url': f'data:image/jpeg;base64,{base64_image}'}},
            ],
        }
    ]
)
```

#### 5. Assistant API
```python
response = client.assistant.conversation(
    assistant_id='your-assistant-id',
    model='glm-4-assistant',
    messages=[...],
    stream=True
)
```

#### 6. Video Generation
```python
response = client.videos.generations(
    model="cogvideox-3",
    prompt="A cat is playing with a ball.",
    quality="quality",  # or "speed"
    with_audio=True,
    size="1920x1080",
    fps=30
)

# Retrieve result
result = client.videos.retrieve_videos_result(id=response.id)
```

### Error Handling
```python
import zai

try:
    response = client.chat.completions.create(...)
except zai.APIStatusError as err:
    print(f"API Status Error: {err}")
except zai.APITimeoutError as err:
    print(f"Request Timeout: {err}")
except Exception as err:
    print(f"Unexpected Error: {err}")
```

### Advanced Configuration
```python
import httpx
from zai import ZaiClient

client = ZaiClient(
    api_key="your-api-key",
    base_url="https://api.z.ai/api/paas/v4/",
    timeout=httpx.Timeout(timeout=300.0, connect=8.0),
    max_retries=3
)
```

---

## Z.ai API Platform Updates

### API Endpoints

**International (Overseas):**
```
https://api.z.ai/api/paas/v4/
```

**Mainland China:**
```
https://open.bigmodel.cn/api/paas/v4/
```

### Available Models

| Model | Context | Parameters | Best For |
|-------|---------|------------|----------|
| glm-4.6 | 128K | 355B total, 32B active | Complex reasoning, agentic tasks |
| glm-4.5 | 128K | 355B total, 32B active | General purpose, coding |
| glm-4.5-air | 128K | 106B total, 12B active | Fast responses, cost-effective |
| glm-4.5v | 128K | Vision model | Image understanding |
| glm-4-assistant | 128K | - | Assistant conversations |
| cogvideox-3 | - | - | Video generation |

### New API Features

1. **Enhanced Function Calling**
   - Native web_search tool
   - Custom function definitions
   - Streaming tool calls

2. **Assistant API**
   - Conversation management
   - Metadata support
   - File attachments

3. **Video Generation**
   - Text-to-video
   - Image-to-video
   - Customizable quality, FPS, resolution

4. **File Management**
   - Upload files for context
   - Download generated content
   - File-based conversations

---

## Migration Considerations

### Breaking Changes from Previous SDK

1. **Client Initialization**
   - Old: `from zhipuai import ZhipuAI`
   - New: `from zai import ZaiClient` or `ZhipuAiClient`

2. **Error Classes**
   - New exception hierarchy under `zai` module
   - More specific error types

3. **Response Structure**
   - Enhanced metadata in responses
   - Streaming chunk format updates

### Backward Compatibility

The new SDK maintains compatibility with OpenAI-style interfaces:
- Similar method signatures
- Compatible response formats
- Familiar parameter names

---

## Integration with EX-AI-MCP-Server

### Current Architecture
- Provider-based system (src/providers/glm.py)
- Registry-based model management
- MCP WebSocket daemon
- Streaming support with provider isolation

### Required Changes
1. Update zai-sdk dependency
2. Integrate new client classes
3. Add GLM-4.6 and new models to registry
4. Update streaming implementation
5. Add assistant API support
6. Enhance video generation capabilities

---

## References

- **Official Documentation:** https://docs.z.ai/
- **Python SDK Guide:** https://docs.z.ai/guides/develop/python/introduction
- **GitHub Repository:** https://github.com/THUDM/z-ai-sdk-python
- **GLM-4.5 Blog Post:** https://z.ai/blog/glm-4.5
- **API Reference:** https://docs.z.ai/api-reference/introduction
- **Pricing:** https://open.bigmodel.cn/pricing

---

**Last Updated:** 2025-10-01  
**Next Review:** After implementation completion

