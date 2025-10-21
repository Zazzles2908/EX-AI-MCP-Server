# GLM API Reference (ZhipuAI)
**Last Updated:** 2025-10-14 (14th October 2025)  
**Provider:** ZhipuAI (Z.ai)  
**Base URL:** https://api.z.ai/api/paas/v4  
**Documentation:** https://docs.z.ai/api-reference/llm/chat-completion

---

## 🔑 Authentication

```python
headers = {
    "Authorization": "Bearer <GLM_API_KEY>",
    "Content-Type": "application/json"
}
```

**Environment Variable:** `GLM_API_KEY`

---

## 📡 Endpoints

### Chat Completions
```
POST https://api.z.ai/api/paas/v4/chat/completions
```

### Web Search
```
POST https://api.z.ai/api/paas/v4/web_search
```

### File Upload
```
POST https://api.z.ai/api/paas/v4/files
```

---

## 🤖 Available Models

### Production Models

**glm-4.6** (Latest)
- Supports: Thinking mode, function calling, web search, retrieval
- Context: 200K tokens
- Best for: Complex reasoning, tool use, long context

**glm-4.5**
- Supports: Thinking mode, function calling, web search, retrieval
- Context: 128K tokens
- Best for: General purpose tasks

**glm-4.5-flash**
- Supports: Function calling, web search
- Does NOT support: Thinking mode
- Context: 128K tokens
- Best for: Fast responses, routing decisions

**glm-4.5-air**
- Supports: Function calling
- Does NOT support: Thinking mode, web search
- Context: 128K tokens
- Best for: Lightweight tasks

**glm-4.6-v** (Vision Model)
- Supports: Vision (images, videos), function calling
- Context: 128K tokens
- Best for: Image/video analysis
- **Special:** Accepts `video_url` and `image_url` in message content

---

## 💬 Chat Completions API

### Basic Request

```python
import requests

url = "https://api.z.ai/api/paas/v4/chat/completions"

payload = {
    "model": "glm-4.6",
    "messages": [
        {
            "role": "user",
            "content": "Explain quantum computing"
        }
    ]
}

headers = {
    "Authorization": "Bearer <GLM_API_KEY>",
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)
print(response.json())
```

### With Thinking Mode

```python
payload = {
    "model": "glm-4.6",
    "messages": [
        {
            "role": "user",
            "content": "Solve this complex problem..."
        }
    ],
    "thinking": {
        "type": "enabled"  # or "disabled"
    }
}
```

**Supported Values:**
- `"enabled"` - Enable chain of thought (default)
- `"disabled"` - Disable chain of thought

**Supported Models:** glm-4.6, glm-4.5, glm-4.5V

**Behavior:**
- GLM-4.6 and GLM-4.5: Automatically determine whether to think
- GLM-4.5V: Thinks compulsorily when enabled

### With Streaming

```python
payload = {
    "model": "glm-4.6",
    "messages": [...],
    "stream": True
}

response = requests.post(url, json=payload, headers=headers, stream=True)

for line in response.iter_lines():
    if line:
        print(line.decode('utf-8'))
```

### With Vision (glm-4.6-v)

```python
import requests

url = "https://api.z.ai/api/paas/v4/chat/completions"

payload = {
    "model": "glm-4.6-v",
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "video_url",
                    "video_url": {"url": "https://cdn.bigmodel.cn/agent-demos/lark/113123.mov"}
                },
                {
                    "type": "text",
                    "text": "What are the video show about?"
                }
            ]
        }
    ]
}

headers = {
    "Authorization": "Bearer <GLM_API_KEY>",
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)
print(response.json())
```

**Vision Content Types:**
- `"type": "image_url"` - For images
- `"type": "video_url"` - For videos
- `"type": "text"` - For text prompts

---

## 🔧 Function Calling

### Request Format

```python
payload = {
    "model": "glm-4.6",
    "messages": [...],
    "tools": [
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
    "tool_choice": "auto"  # or "none" or {"type": "function", "function": {"name": "get_weather"}}
}
```

**tool_choice Options:**
- `"auto"` - Model decides whether to call functions (default)
- `"none"` - Model will not call functions
- `{"type": "function", "function": {"name": "function_name"}}` - Force specific function

**Note:** glm-4.6 may require explicit `tool_choice: "auto"` to execute function calls instead of returning raw JSON.

---

## 🔍 Web Search

### Method 1: Separate Endpoint

```python
url = "https://api.z.ai/api/paas/v4/web_search"

payload = {
    "search_query": "latest AI news",
    "count": 10,
    "search_engine": "search_pro_jina",  # or "search_pro_bing"
    "search_recency_filter": "oneWeek"  # oneDay, oneWeek, oneMonth, oneYear, noLimit
}

response = requests.post(url, json=payload, headers=headers)
```

### Method 2: Tools Array in Chat

```python
payload = {
    "model": "glm-4.6",
    "messages": [...],
    "tools": [
        {
            "type": "web_search",
            "web_search": {
                "search_engine": "search_pro_jina",  # or "search_pro_bing"
                "enable": True,
                "count": 10,  # 1-50 results
                "search_recency_filter": "oneWeek",
                "content_size": "medium",  # "medium" (400-600 chars) or "high" (2500 chars)
                "result_sequence": "after",  # "before" or "after"
                "search_result": True,  # Return search results
                "require_search": False  # Force model to use search
            }
        }
    ]
}
```

**Web Search Parameters:**
- `search_engine`: "search_pro_jina" or "search_pro_bing"
- `enable`: Boolean - Enable web search
- `search_query`: Optional - Force specific query
- `count`: Integer (1-50) - Number of results
- `search_domain_filter`: String - Filter by domain (e.g., "www.example.com")
- `search_recency_filter`: "oneDay", "oneWeek", "oneMonth", "oneYear", "noLimit"
- `content_size`: "medium" (400-600 chars) or "high" (2500 chars)
- `result_sequence`: "before" or "after" - When to show results
- `search_result`: Boolean - Return search results
- `require_search`: Boolean - Force model to use search
- `search_prompt`: String - Custom search prompt

---

## 📚 Retrieval (Knowledge Base)

```python
payload = {
    "model": "glm-4.6",
    "messages": [...],
    "tools": [
        {
            "type": "retrieval",
            "retrieval": {
                "knowledge_id": "kb_id_here",
                "prompt_template": "Search for {{question}} in {{knowledge}}"
            }
        }
    ]
}
```

---

## 📤 Response Format

### Standard Response

```json
{
    "id": "chat_id",
    "created": 1234567890,
    "model": "glm-4.6",
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

### With Thinking Mode

```json
{
    "choices": [
        {
            "message": {
                "role": "assistant",
                "content": "Final response",
                "reasoning_content": "Thinking process here..."
            },
            "finish_reason": "stop"
        }
    ]
}
```

**Note:** GLM-4.5V may include `<think>` tags or `<|begin_of_box|>` markers in content that should be cleaned.

### With Function Calls

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

### Finish Reasons

- `"stop"` - Natural completion
- `"tool_calls"` - Model called a function
- `"length"` - Max tokens reached
- `"sensitive"` - Content filtered
- `"network_error"` - Network error occurred

---

## 🔧 Implementation in EX-AI-MCP-Server

### Provider: `src/providers/glm_chat.py`

**Thinking Mode Conversion:**
```python
if 'thinking_mode' in kwargs:
    thinking_mode = kwargs.pop('thinking_mode', None)
    from .glm_config import get_capabilities
    caps = get_capabilities(model_name)
    if caps.supports_extended_thinking:
        payload["thinking"] = {"type": "enabled"}
        logger.debug(f"Enabled thinking mode for GLM model {model_name}")
```

**Tool Choice for glm-4.6:**
```python
if model_name == "glm-4.6" and payload.get("tools"):
    if not payload.get("tool_choice"):
        payload["tool_choice"] = "auto"
        logger.info(f"GLM-4.6: Forcing tool_choice='auto' for function calling")
```

### GLM-Specific Tools

**Web Search:** `tools/providers/glm/glm_web_search.py`
- Uses separate `/web_search` endpoint
- Backend: `src/providers/tool_executor.py`

**File Upload:** `tools/providers/glm/glm_files.py`
- Uses `/files` endpoint with purpose='agent'

**Payload Preview:** `tools/providers/glm/glm_payload_preview.py`
- Preview API payloads before sending

---

## 📝 Notes

1. **NOT OpenAI Compatible:** GLM uses custom API format
2. **Thinking Mode:** Boolean only (`enabled`/`disabled`), NOT categories
3. **Web Search:** Two methods available (separate endpoint or tools array)
4. **glm-4.6 Tool Choice:** May need explicit `tool_choice: "auto"`
5. **Artifact Cleaning:** GLM-4.5V may include `<think>` tags that need cleaning

---

**Last Updated:** 2025-10-14 (14th October 2025)  
**Source:** https://docs.z.ai/api-reference/llm/chat-completion

