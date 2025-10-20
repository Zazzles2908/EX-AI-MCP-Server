# Kimi API Reference (Moonshot AI)
**Last Updated:** 2025-10-14 (14th October 2025)  
**Provider:** Moonshot AI  
**Base URL:** https://api.moonshot.ai/v1  
**Documentation:** https://platform.moonshot.ai/docs  
**OpenAI SDK Compatible:** ✅ YES - Uses OpenAI SDK format for all parameters

---

## 🔑 Authentication

```python
headers = {
    "Authorization": "Bearer <KIMI_API_KEY>",
    "Content-Type": "application/json"
}
```

**Environment Variable:** `KIMI_API_KEY`

---

## ✅ OpenAI SDK Compatibility

**Kimi API is fully compatible with OpenAI SDK!**

```python
from openai import OpenAI

client = OpenAI(
    api_key="<KIMI_API_KEY>",
    base_url="https://api.moonshot.ai/v1"
)

response = client.chat.completions.create(
    model="kimi-k2-0905-preview",
    messages=[
        {"role": "user", "content": "Hello!"}
    ]
)
```

**This means:**
- All OpenAI SDK parameters work with Kimi
- Streaming uses OpenAI streaming format
- Function calling uses OpenAI function calling format
- File upload uses OpenAI file upload format

---

## 📡 Endpoints

### Chat Completions
```
POST https://api.moonshot.ai/v1/chat/completions
```

### File Upload
```
POST https://api.moonshot.ai/v1/files
```

---

## 🤖 Available Models

### K2 Series (Latest - Recommended)

**kimi-k2-0905-preview** (Default)
- Context: 256K tokens (262,144 tokens)
- Pricing: $0.15 (cache hit) / $0.60 (cache miss) input, $2.50 output per million tokens
- Best for: General purpose, long context
- Features: Function calling, web search, file upload, automatic caching

**kimi-k2-0711-preview** (Original K2)
- Context: 128K tokens (131,072 tokens)
- Pricing: $0.15 (cache hit) / $0.60 (cache miss) input, $2.50 output per million tokens
- Best for: Legacy compatibility
- Features: Function calling, web search, file upload

**kimi-k2-turbo-preview** (Recommended - Fast)
- Context: 256K tokens (262,144 tokens)
- Pricing: $0.60 (cache hit) / $2.40 (cache miss) input, $10.00 output per million tokens
- Best for: Fast responses with long context
- Features: Function calling, web search, file upload, automatic caching

**kimi-thinking-preview** (Thinking Mode)
- Context: 128K tokens
- Best for: Complex reasoning, deep analysis
- Features: Reasoning extraction, function calling
- **Special:** Returns `reasoning_content` field in streaming

### Legacy Models (Moonshot V1)

**moonshot-v1-128k**
- Context: 128K tokens
- Best for: Long conversations (superseded by K2)

**moonshot-v1-32k**
- Context: 32K tokens
- Best for: Medium conversations (legacy)

**moonshot-v1-8k**
- Context: 8K tokens
- Best for: Short conversations (legacy)

**moonshot-v1-8k-vision-preview**
- Context: 8K tokens
- Features: Vision support (images)

**kimi-latest**
- Alias for latest stable model
- Context: Varies

**Note:** K2 series (kimi-k2-*) are recommended over legacy moonshot-v1-* models

---

## 💬 Chat Completions API

### Basic Request (OpenAI SDK Format)

```python
from openai import OpenAI

client = OpenAI(
    api_key="<KIMI_API_KEY>",
    base_url="https://api.moonshot.ai/v1"
)

response = client.chat.completions.create(
    model="kimi-k2-0905-preview",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain quantum computing"}
    ],
    temperature=0.7,
    max_tokens=1000
)

print(response.choices[0].message.content)
```

### With Streaming

```python
stream = client.chat.completions.create(
    model="kimi-k2-0905-preview",
    messages=[...],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

---

## 🧠 Thinking Mode (Model-Based)

**Kimi thinking mode is MODEL-BASED, not parameter-based!**

### Using Thinking Mode

```python
response = client.chat.completions.create(
    model="kimi-thinking-preview",  # ← Use thinking model!
    messages=[
        {"role": "user", "content": "Solve this complex problem..."}
    ],
    stream=True  # Streaming recommended for reasoning extraction
)
```

### Extracting Reasoning Content

```python
reasoning_parts = []
content_parts = []

for chunk in stream:
    delta = chunk.choices[0].delta
    
    # Extract reasoning (if available)
    if hasattr(delta, "reasoning_content"):
        reasoning = getattr(delta, "reasoning_content")
        if reasoning:
            reasoning_parts.append(reasoning)
    
    # Extract content
    if delta.content:
        content_parts.append(delta.content)

# Format output
if reasoning_parts:
    print("[Reasoning]")
    print("".join(reasoning_parts))
    print("\n[Response]")
print("".join(content_parts))
```

**Environment Variable:** `KIMI_EXTRACT_REASONING=true` (default)

---

## 🔧 Function Calling (OpenAI Format)

### Request Format

```python
response = client.chat.completions.create(
    model="kimi-k2-0905-preview",
    messages=[...],
    tools=[
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get current weather for a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "City name"
                        }
                    },
                    "required": ["location"]
                }
            }
        }
    ],
    tool_choice="auto"  # or "none" or {"type": "function", "function": {"name": "get_weather"}}
)
```

**tool_choice Options (OpenAI Format):**
- `"auto"` - Model decides whether to call functions (default)
- `"none"` - Model will not call functions
- `{"type": "function", "function": {"name": "function_name"}}` - Force specific function

---

## 🔍 Web Search (Builtin Function)

### Request Format

```python
response = client.chat.completions.create(
    model="kimi-k2-0905-preview",
    messages=[
        {"role": "user", "content": "What's the latest AI news?"}
    ],
    tools=[
        {
            "type": "builtin_function",
            "name": "$web_search"
        }
    ]
)
```

**Note:** Web search is a builtin function, not a separate parameter!

**Environment Variable:** `use_websearch=true/false` controls whether to include web search tool

---

## 📁 File Upload (OpenAI Format)

### Upload File

```python
# Upload file
file = client.files.create(
    file=open("document.pdf", "rb"),
    purpose="file-extract"
)

# Use in chat
response = client.chat.completions.create(
    model="kimi-k2-0905-preview",
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant."
        },
        {
            "role": "system",
            "content": f"<file>{file.id}</file>"
        },
        {
            "role": "user",
            "content": "Summarize this document"
        }
    ]
)
```

**Environment Variable:** `TEST_FILES_DIR` - Directories for file upload testing

---

## 📤 Response Format (OpenAI Compatible)

### Standard Response

```json
{
    "id": "chat_id",
    "object": "chat.completion",
    "created": 1234567890,
    "model": "kimi-k2-0905-preview",
    "choices": [
        {
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "Response text here"
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

### With Thinking Mode (Streaming)

```json
{
    "id": "chat_id",
    "object": "chat.completion.chunk",
    "created": 1234567890,
    "model": "kimi-thinking-preview",
    "choices": [
        {
            "index": 0,
            "delta": {
                "reasoning_content": "Thinking process...",
                "content": "Response text"
            },
            "finish_reason": null
        }
    ]
}
```

### With Function Calls (OpenAI Format)

```json
{
    "choices": [
        {
            "message": {
                "role": "assistant",
                "content": null,
                "tool_calls": [
                    {
                        "id": "call_id",
                        "type": "function",
                        "function": {
                            "name": "get_weather",
                            "arguments": "{\"location\": \"San Francisco\"}"
                        }
                    }
                ]
            },
            "finish_reason": "tool_calls"
        }
    ]
}
```

---

## 🔧 Implementation in EX-AI-MCP-Server

### Provider: `src/providers/kimi_chat.py`

**Uses OpenAI SDK:**
```python
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("KIMI_API_KEY"),
    base_url=os.getenv("KIMI_BASE_URL", "https://api.moonshot.ai/v1")
)
```

### Streaming Adapter: `streaming/streaming_adapter.py`

**Reasoning Extraction:**
```python
def stream_openai_chat_events(
    *,
    client: Any,
    create_kwargs: dict[str, Any],
    on_delta: Optional[Callable[[str], None]] = None,
    extract_reasoning: Optional[bool] = None,
) -> Tuple[str, List[Any]]:
    """Iterate OpenAI-compatible chat.completions.create(stream=True) events."""
    
    # Read extract_reasoning from env if not explicitly provided
    if extract_reasoning is None:
        extract_reasoning = os.getenv("KIMI_EXTRACT_REASONING", "true").strip().lower() in ("1", "true", "yes")
    
    reasoning_parts = []
    content_parts = []
    
    for chunk in stream:
        delta = chunk.choices[0].delta
        
        # Extract reasoning_content for Kimi thinking mode
        if extract_reasoning and hasattr(delta, "reasoning_content"):
            reasoning_piece = getattr(delta, "reasoning_content")
            if reasoning_piece:
                reasoning_parts.append(str(reasoning_piece))
        
        # Extract content
        if delta.content:
            content_parts.append(delta.content)
    
    # Format output
    final_text = ""
    if reasoning_parts:
        reasoning_text = "".join(reasoning_parts)
        final_text = f"[Reasoning]\n{reasoning_text}\n\n[Response]\n"
    final_text += "".join(content_parts)
    
    return final_text, tool_calls
```

---

## 📝 Notes

1. **OpenAI SDK Compatible:** All parameters follow OpenAI format
2. **Thinking Mode:** Model-based (`kimi-thinking-preview`), NOT parameter-based
3. **Web Search:** Builtin function (`$web_search`), NOT separate endpoint
4. **File Upload:** OpenAI format with `purpose="file-extract"`
5. **Streaming:** Supports `reasoning_content` extraction for thinking mode
6. **K2 Models Preferred:** Use K2 series over legacy moonshot-v1 models

---

## ⚠️ Known Issues

**K2 Consistency (SAFETY CRITICAL):**
- K2 models may give inconsistent results for calculations
- User reported 9x difference (11.2 vs 1.22 cal/cm²) for arc flash calculations
- Investigation ongoing - see `scripts/testing/test_k2_consistency.py`

---

**Last Updated:** 2025-10-14 (14th October 2025)  
**Source:** https://platform.moonshot.ai/docs

