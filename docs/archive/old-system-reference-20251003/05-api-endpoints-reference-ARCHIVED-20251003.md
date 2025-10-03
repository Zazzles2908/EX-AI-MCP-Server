# API Endpoints Reference

**Version:** 1.0  
**Last Updated:** 2025-10-02  
**Related:** `02-provider-architecture.md`, `04-features-and-capabilities.md`

---

## Base URLs

### International Users (api.z.ai)

**Primary Base URL:**
```
https://api.z.ai/v1
```

**Full API Path:**
```
https://api.z.ai/api/paas/v4/
```

**Alternative Endpoints:**
- **Anthropic-compatible:** `https://api.z.ai/api/anthropic`
- **Coding-specific:** `https://api.z.ai/api/coding/paas/v4`

### Mainland China (NOT our target)

**Base URL:**
```
https://open.bigmodel.cn/api/paas/v4/
```

**Note:** This documentation focuses on international users (api.z.ai) only.

---

## Authentication

### Bearer Token Authentication

**Header Format:**
```
Authorization: Bearer <your_api_key>
```

**Example:**
```bash
curl -H "Authorization: Bearer sk-abc123..." \
     https://api.z.ai/api/paas/v4/chat/completions
```

### API Key Management

**Get API Key:**
1. Visit https://z.ai/manage-apikey/apikey-list
2. Create new API key
3. Copy and store securely

**Environment Variable:**
```env
GLM_API_KEY=your_api_key_here
```

---

## Chat Completions

### Endpoint

```
POST /paas/v4/chat/completions
```

**Full URL:**
```
https://api.z.ai/api/paas/v4/chat/completions
```

### Request Headers

```
Authorization: Bearer <token>
Content-Type: application/json
Accept-Language: en-US,en
```

### Request Body

**Basic Request:**
```json
{
  "model": "glm-4.6",
  "messages": [
    {
      "role": "system",
      "content": "You are a helpful assistant."
    },
    {
      "role": "user",
      "content": "What is artificial intelligence?"
    }
  ],
  "temperature": 0.6,
  "max_tokens": 65536,
  "stream": false
}
```

### Parameters

**Required:**
- `model` (string): Model to use (e.g., "glm-4.6")
- `messages` (array): Conversation messages

**Optional:**
- `temperature` (number, 0-1): Sampling temperature (default: 0.6)
- `top_p` (number, 0-1): Top-p sampling (default: 0.95)
- `max_tokens` (integer): Maximum output tokens (default: model-specific)
- `stream` (boolean): Enable streaming (default: false)
- `tools` (array): Tool definitions (functions, web search, retrieval)
- `tool_choice` (string/object): Tool selection strategy
- `tool_stream` (boolean): Enable streaming for function calls (GLM-4.6 only)
- `thinking` (object): Chain of thought configuration
- `response_format` (object): Output format (text or json_object)
- `stop` (array): Stop sequences (max 1)
- `user_id` (string): End user ID (6-128 chars)
- `request_id` (string): Unique request identifier
- `do_sample` (boolean): Enable sampling (default: true)

### Response

**Non-Streaming Response:**
```json
{
  "id": "chat_123",
  "request_id": "req_456",
  "created": 1696118400,
  "model": "glm-4.6",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Artificial intelligence (AI) is...",
        "reasoning_content": null,
        "tool_calls": null
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 25,
    "completion_tokens": 150,
    "prompt_tokens_details": {
      "cached_tokens": 0
    },
    "total_tokens": 175
  },
  "web_search": null
}
```

**Streaming Response:**
```
data: {"id":"chat_123","choices":[{"index":0,"delta":{"role":"assistant","content":"Artificial"}}]}

data: {"id":"chat_123","choices":[{"index":0,"delta":{"content":" intelligence"}}]}

data: {"id":"chat_123","choices":[{"index":0,"delta":{"content":" is"}}]}

data: [DONE]
```

### Finish Reasons

- `stop`: Natural completion
- `length`: Max tokens reached
- `tool_calls`: Function calling triggered
- `sensitive`: Content filtered
- `network_error`: Network issue

---

## Video Generation

### Generate Video (Async)

```
POST /paas/v4/videos/generations
```

**Request:**
```json
{
  "model": "cogvideox-2",
  "prompt": "A cat playing piano in a jazz club",
  "quality": "high",
  "fps": 30,
  "size": "1280x720",
  "duration": 5,
  "audio": true
}
```

**Parameters:**
- `model` (string): "cogvideox-2"
- `prompt` (string): Text description
- `image_url` (string, optional): Starting image for image-to-video
- `quality` (string): "low", "medium", "high"
- `fps` (integer): 24, 30, or 60
- `size` (string): "1280x720", "1920x1080"
- `duration` (integer): 1-10 seconds
- `audio` (boolean): Include audio

**Response:**
```json
{
  "task_id": "video_task_123",
  "status": "processing",
  "created": 1696118400
}
```

### Retrieve Video Result

```
GET /paas/v4/videos/retrieve_videos_result?task_id={task_id}
```

**Response (Processing):**
```json
{
  "task_id": "video_task_123",
  "status": "processing",
  "progress": 45
}
```

**Response (Complete):**
```json
{
  "task_id": "video_task_123",
  "status": "completed",
  "video_url": "https://cdn.z.ai/videos/abc123.mp4",
  "duration": 5,
  "size": "1280x720",
  "fps": 30
}
```

---

## Web Search Tool

### Tool Definition

```json
{
  "tools": [
    {
      "type": "web_search",
      "web_search": {
        "search_engine": "search_pro_jina",
        "search_recency_filter": "oneWeek",
        "domain_whitelist": ["example.com"],
        "content_size": "medium",
        "result_sequence": "after",
        "search_result": true,
        "require_search": false,
        "search_prompt": "Custom search processing prompt"
      }
    }
  ]
}
```

### Parameters

- `search_engine` (string): "search_pro_jina" or "search_pro_bing"
- `search_recency_filter` (string): "oneDay", "oneWeek", "oneMonth", "oneYear", "noLimit"
- `domain_whitelist` (array): Limit to specific domains
- `content_size` (string): "medium" (400-600 chars) or "high" (2500 chars)
- `result_sequence` (string): "before" or "after"
- `search_result` (boolean): Return search results
- `require_search` (boolean): Force model to use search
- `search_prompt` (string): Custom processing prompt

### Response with Web Search

```json
{
  "choices": [...],
  "web_search": [
    {
      "title": "AI Research Paper",
      "content": "Summary of the research...",
      "link": "https://example.com/paper",
      "media": "Example Journal",
      "icon": "https://example.com/icon.png",
      "refer": "1",
      "publish_date": "2025-10-01"
    }
  ]
}
```

---

## Assistant API

### Endpoint

```
POST /paas/v4/assistant/conversation
```

**Request:**
```json
{
  "model": "glm-4-assistant",
  "messages": [
    {
      "role": "user",
      "content": "Help me plan a project"
    }
  ],
  "metadata": {
    "user_id": "user_123",
    "session_id": "session_456"
  },
  "attachments": [
    {
      "file_id": "file_789",
      "tools": ["retrieval"]
    }
  ],
  "stream": false
}
```

**Response:**
```json
{
  "id": "asst_123",
  "conversation_id": "conv_456",
  "messages": [
    {
      "role": "assistant",
      "content": "I'd be happy to help..."
    }
  ],
  "metadata": {
    "tokens_used": 150
  }
}
```

---

## File Upload

### Endpoint

```
POST /paas/v4/files/upload
```

**Request (multipart/form-data):**
```
POST /paas/v4/files/upload
Content-Type: multipart/form-data

file: <binary data>
purpose: assistants
```

**Response:**
```json
{
  "id": "file_123",
  "object": "file",
  "bytes": 102400,
  "created_at": 1696118400,
  "filename": "document.pdf",
  "purpose": "assistants"
}
```

### Supported Formats

- **Documents:** PDF, TXT, DOCX
- **Images:** JPEG, PNG, GIF
- **Audio:** MP3, WAV
- **Video:** MP4, AVI

---

## Embeddings

### Endpoint

```
POST /paas/v4/embeddings
```

**Request:**
```json
{
  "model": "embedding-2",
  "input": "Text to embed",
  "dimensions": 1024
}
```

**Batch Request:**
```json
{
  "model": "embedding-2",
  "input": [
    "First text",
    "Second text",
    "Third text"
  ],
  "dimensions": 1024
}
```

**Response:**
```json
{
  "object": "list",
  "data": [
    {
      "object": "embedding",
      "embedding": [0.123, -0.456, 0.789, ...],
      "index": 0
    }
  ],
  "model": "embedding-2",
  "usage": {
    "prompt_tokens": 10,
    "total_tokens": 10
  }
}
```

---

## Function Calling

### Tool Definition

```json
{
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
            },
            "unit": {
              "type": "string",
              "enum": ["celsius", "fahrenheit"],
              "description": "Temperature unit"
            }
          },
          "required": ["location"]
        }
      }
    }
  ],
  "tool_choice": "auto"
}
```

### Tool Choice Options

**Auto (Default):**
```json
{
  "tool_choice": "auto"
}
```

**None:**
```json
{
  "tool_choice": "none"
}
```

**Force Specific Function:**
```json
{
  "tool_choice": {
    "type": "function",
    "function": {
      "name": "get_weather"
    }
  }
}
```

### Response with Tool Calls

```json
{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": null,
        "tool_calls": [
          {
            "id": "call_123",
            "type": "function",
            "function": {
              "name": "get_weather",
              "arguments": "{\"location\": \"San Francisco\", \"unit\": \"celsius\"}"
            }
          }
        ]
      },
      "finish_reason": "tool_calls"
    }
  ]
}
```

### Tool Response

```json
{
  "messages": [
    {
      "role": "tool",
      "tool_call_id": "call_123",
      "content": "{\"temperature\": 18, \"condition\": \"sunny\"}"
    }
  ]
}
```

---

## Retrieval Tool

### Tool Definition

```json
{
  "tools": [
    {
      "type": "retrieval",
      "retrieval": {
        "knowledge_id": "kb_123",
        "prompt_template": "Search for the answer to {{question}} in {{knowledge}}"
      }
    }
  ]
}
```

### Parameters

- `knowledge_id` (string): Knowledge base ID
- `prompt_template` (string, optional): Custom retrieval prompt

---

## Rate Limits

### Default Limits

**GLM-4.6:**
- Requests per minute: 60
- Tokens per minute: 100,000

**GLM-4.5 Series:**
- Requests per minute: 100
- Tokens per minute: 150,000

### Rate Limit Headers

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1696118460
```

---

## Error Responses

### Error Format

```json
{
  "error": {
    "message": "Invalid API key",
    "type": "invalid_request_error",
    "code": "invalid_api_key"
  }
}
```

### Common Error Codes

**Authentication:**
- `invalid_api_key`: API key is invalid
- `insufficient_quota`: Quota exceeded

**Request:**
- `invalid_request_error`: Malformed request
- `invalid_model`: Model not found
- `context_length_exceeded`: Input too long

**Rate Limiting:**
- `rate_limit_exceeded`: Too many requests

**Server:**
- `server_error`: Internal server error
- `service_unavailable`: Service temporarily unavailable

---

## SDK Examples

### Python (zai-sdk)

```python
from zai import ZAI

client = ZAI(
    api_key="your_api_key",
    base_url="https://api.z.ai/v1"
)

response = client.chat.completions.create(
    model="glm-4.6",
    messages=[
        {"role": "user", "content": "Hello!"}
    ]
)

print(response.choices[0].message.content)
```

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
        {"role": "user", "content": "Hello!"}
    ]
)

print(response.choices[0].message.content)
```

### cURL

```bash
curl -X POST https://api.z.ai/api/paas/v4/chat/completions \
  -H "Authorization: Bearer your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "glm-4.6",
    "messages": [
      {"role": "user", "content": "Hello!"}
    ]
  }'
```

---

**Next:** Read `06-deployment-guide.md` for installation and setup instructions

