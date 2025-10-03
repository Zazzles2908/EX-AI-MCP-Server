# Provider Architecture

**Version:** 1.0  
**Last Updated:** 2025-10-02  
**Related:** `01-system-overview.md`, `04-features-and-capabilities.md`

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
| **Best For** | General tasks, web search, multimodal | Quality reasoning, long context |

---

## GLM Provider (ZhipuAI/Z.ai)

### Configuration

**Environment Variables:**
```env
# Required
GLM_API_KEY=your_api_key_here
GLM_BASE_URL=https://api.z.ai/v1

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

**GLM-4.5V Series (Vision):**
- `glm-4.5v` - Vision model with multimodal support
- `glm-4.5v-plus` - Enhanced vision capabilities

**Legacy:**
- `glm-4-32b-0414-128k` - 32B parameter model

### SDK Integration (zai-sdk v0.0.4)

**Installation:**
```bash
pip install zai-sdk>=0.0.4
```

**Basic Usage:**
```python
from zai import ZAI

client = ZAI(
    api_key="your_api_key",
    base_url="https://api.z.ai/v1"
)

response = client.chat.completions.create(
    model="glm-4.6",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ],
    temperature=0.6,
    max_tokens=65536,
    stream=False
)
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

## Kimi Provider (Moonshot)

### Configuration

**Environment Variables:**
```env
# Required
KIMI_API_KEY=your_moonshot_api_key
KIMI_BASE_URL=https://api.moonshot.ai/v1

# Optional
KIMI_DEFAULT_MODEL=kimi-k2-0905-preview
KIMI_TEMPERATURE=0.5
KIMI_MAX_TOKENS=32768
```

### Available Models

**K2 Series (Agentic Intelligence):**
- `kimi-k2-0905-preview` - Latest K2 (256K context, enhanced coding/tool-calling) **[RECOMMENDED]**
- `kimi-k2-0711-preview` - Original K2 (256K context)

**Legacy Models:**
- `moonshot-v1-128k` - 128K context window (superseded by K2)
- `moonshot-v1-32k` - 32K context window (legacy)
- `moonshot-v1-8k` - 8K context window (legacy)

**Note:** Use `kimi-k2-0905-preview` for production (version pinning ensures stability)

### SDK Integration

**OpenAI-Compatible API:**
```python
from openai import OpenAI

client = OpenAI(
    api_key="your_moonshot_api_key",
    base_url="https://api.moonshot.ai/v1"
)

response = client.chat.completions.create(
    model="kimi-k2-0905-preview",
    messages=[...],
    temperature=0.5
)
```

### Features

**Advanced Caching:**
- Automatic prompt caching
- Reduced costs for repeated prompts
- Faster response times

**Quality Reasoning:**
- Superior reasoning capabilities
- Better for complex analysis
- Excellent for long-context tasks

---

## Manager-First Routing Architecture

### Routing Strategy

**Default Manager: GLM-4.5-flash**
- Fast response time (~1-2 seconds)
- Cost-effective ($0.10/$0.30 per M tokens)
- Intelligent task classification
- Automatic escalation to appropriate model

### Routing Decision Tree

```
User Request
    ↓
GLM-4.5-flash (Manager)
    ↓
Task Classification
    ↓
    ├─→ Simple Query → GLM-4.5-flash (same model)
    ├─→ Complex Reasoning → GLM-4.6 (advanced)
    ├─→ Quality Analysis → Kimi (caching + quality)
    ├─→ Web Search → GLM-4.6 (native search)
    ├─→ Multimodal → GLM-4.5V (vision)
    └─→ Tool Execution → Workflow Tools
```

### Classification Criteria

**Simple Tasks (GLM-4.5-flash):**
- Basic questions
- Simple code snippets
- Quick clarifications
- Routing decisions

**Complex Tasks (GLM-4.6):**
- Advanced reasoning
- Code generation
- Web search required
- Multimodal inputs
- Tool calling

**Quality Tasks (Kimi):**
- Long-context analysis
- Repeated prompts (caching benefit)
- High-quality reasoning
- Complex problem-solving

### Implementation

**Routing Logic:**
```python
async def route_request(request: ChatRequest) -> str:
    """Route request to appropriate model."""
    
    # Use manager to classify
    classification = await glm_flash.classify(request)
    
    if classification.complexity == "simple":
        return "glm-4.5-flash"
    elif classification.requires_web_search:
        return "glm-4.6"
    elif classification.requires_tool_use or classification.requires_coding:
        return "kimi-k2-0905-preview"  # Best for agentic tasks
    elif classification.is_multimodal:
        return "glm-4.5v"
    else:
        return "glm-4.6"  # Default to flagship
```

---

## Dual SDK/HTTP Fallback Pattern

### Architecture

**Primary Path: SDK**
- Use official SDK (zai-sdk, OpenAI SDK)
- Better error handling
- Automatic retries
- Type safety

**Fallback Path: HTTP**
- Direct API calls with httpx
- More control over requests
- Easier debugging
- Works when SDK fails

### Benefits

1. **Resilience:** Automatic fallback if SDK fails
2. **Flexibility:** Can use HTTP for debugging
3. **Compatibility:** Works with both approaches
4. **Reliability:** Multiple paths to success

### Implementation Pattern

**Provider Base Class:**
```python
class BaseProvider:
    def __init__(self, api_key: str, base_url: str):
        self.sdk_client = self._init_sdk(api_key, base_url)
        self.http_client = httpx.AsyncClient(
            base_url=base_url,
            headers={"Authorization": f"Bearer {api_key}"}
        )
    
    async def generate(self, **kwargs):
        try:
            return await self._generate_sdk(**kwargs)
        except Exception as e:
            logger.warning(f"SDK failed: {e}, using HTTP")
            return await self._generate_http(**kwargs)
```

---

## Streaming Implementation

### Server-Sent Events (SSE)

**GLM Streaming:**
```python
async def stream_response(model: str, messages: list):
    """Stream response from GLM."""
    
    async with httpx.stream(
        "POST",
        f"{base_url}/chat/completions",
        json={"model": model, "messages": messages, "stream": True}
    ) as stream:
        async for line in stream.aiter_lines():
            if line.startswith("data: "):
                data = line[6:]
                if data == "[DONE]":
                    break
                
                chunk = json.loads(data)
                content = chunk["choices"][0]["delta"].get("content", "")
                if content:
                    yield content
```

**Kimi Streaming:**
```python
async def stream_kimi(model: str, messages: list):
    """Stream response from Kimi."""
    
    stream = await kimi_client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True
    )
    
    async for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
```

### Environment-Gated Streaming

**Configuration:**
```env
GLM_STREAM_ENABLED=true   # Enable GLM streaming
KIMI_STREAM_ENABLED=true  # Enable Kimi streaming
```

**Runtime Check:**
```python
def should_stream(provider: str) -> bool:
    """Check if streaming is enabled for provider."""
    
    if provider == "glm":
        return os.getenv("GLM_STREAM_ENABLED", "false").lower() == "true"
    elif provider == "kimi":
        return os.getenv("KIMI_STREAM_ENABLED", "false").lower() == "true"
    return False
```

---

## Error Handling and Retries

### SDK Error Handling

**Automatic Retries:**
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def call_sdk(client, **kwargs):
    """Call SDK with automatic retries."""
    return await client.chat.completions.create(**kwargs)
```

### HTTP Fallback on SDK Failure

**Graceful Degradation:**
```python
async def generate_with_fallback(**kwargs):
    """Generate with SDK, fallback to HTTP."""
    
    try:
        return await call_sdk(sdk_client, **kwargs)
    except SDKError as e:
        logger.warning(f"SDK error: {e}, using HTTP fallback")
        return await call_http(http_client, **kwargs)
    except Exception as e:
        logger.error(f"Both SDK and HTTP failed: {e}")
        raise
```

---

## Performance Optimization

### Caching Strategy

**Kimi Prompt Caching:**
- Automatic caching of repeated prompts
- Reduced costs for similar requests
- Faster response times

**GLM Prompt Caching:**
- Available in GLM-4.6
- Configurable cache TTL
- Significant cost savings

### Connection Pooling

**HTTP Client Configuration:**
```python
http_client = httpx.AsyncClient(
    limits=httpx.Limits(
        max_keepalive_connections=20,
        max_connections=100
    ),
    timeout=httpx.Timeout(60.0)
)
```

---

## Cost Optimization

### Model Selection Strategy

**Cost Tiers:**
1. **GLM-4.5-flash:** $0.10/$0.30 per M tokens (cheapest)
2. **GLM-4.6:** $0.60/$2.20 per M tokens (flagship)
3. **Kimi:** Tier 2 pricing (quality)

**Optimization Rules:**
- Use GLM-4.5-flash for simple tasks
- Use GLM-4.6 for complex tasks requiring web search
- Use Kimi for quality reasoning with caching benefits
- Monitor token usage and adjust routing

### Token Efficiency

**GLM-4.6 Improvements:**
- ~15% fewer tokens than GLM-4.5
- Better compression of responses
- More efficient reasoning

---

**Next:** Read `03-tool-ecosystem.md` for complete tool catalog and usage

