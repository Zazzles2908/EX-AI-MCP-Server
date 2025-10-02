# Features and Capabilities

**Version:** 1.0  
**Last Updated:** 2025-10-02  
**Related:** `02-provider-architecture.md`, `05-api-endpoints-reference.md`

---

## Overview

The EX-AI-MCP-Server provides comprehensive AI capabilities through the ZhipuAI (Z.ai) and Moonshot (Kimi) platforms. This document details all available features, their configurations, and usage patterns.

---

## Core Features

### 1. Streaming Support

**Environment-Gated Streaming:**
```env
GLM_STREAM_ENABLED=true   # Enable streaming for GLM provider
KIMI_STREAM_ENABLED=true  # Enable Kimi streaming
```

**Benefits:**
- Real-time response generation
- Lower perceived latency
- Better user experience for long responses
- Token-by-token delivery
- Immediate feedback

**Implementation:**
- Server-Sent Events (SSE) protocol
- Automatic chunk aggregation
- Metadata tracking (`metadata.streamed = true`)
- Graceful fallback to non-streaming

**Usage:**
```python
# Streaming request
response = await client.chat.completions.create(
    model="glm-4.6",
    messages=[...],
    stream=True
)

async for chunk in response:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

---

### 2. Web Search Integration

**Native GLM Web Search:**
- Automatically triggered by query content
- No manual search required
- Integrated into chat responses
- Multiple search engines supported

**Search Engines:**
- `search_pro_jina` (default) - Jina AI search
- `search_pro_bing` - Bing search

**Configuration:**
```json
{
  "tools": [
    {
      "type": "web_search",
      "web_search": {
        "search_engine": "search_pro_jina",
        "search_recency_filter": "oneWeek",
        "content_size": "medium",
        "result_sequence": "after",
        "search_result": true
      }
    }
  ]
}
```

**Parameters:**
- `search_engine`: Which search engine to use
- `search_recency_filter`: Time range (oneDay, oneWeek, oneMonth, oneYear, noLimit)
- `domain_whitelist`: Limit to specific domains
- `content_size`: Summary length (medium: 400-600 chars, high: 2500 chars)
- `result_sequence`: Show results before or after response
- `search_result`: Whether to return search results
- `require_search`: Force model to use search results
- `search_prompt`: Custom prompt for processing results

**Response Format:**
```json
{
  "choices": [...],
  "web_search": [
    {
      "title": "Result title",
      "content": "Summary content",
      "link": "https://example.com",
      "media": "Website name",
      "icon": "https://icon.url",
      "refer": "1",
      "publish_date": "2025-10-01"
    }
  ]
}
```

---

### 3. Tool Calling and Function Execution

**OpenAI-Compatible Function Calling:**

**Function Definition:**
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
              "enum": ["celsius", "fahrenheit"]
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

**Tool Choice Options:**
- `auto` - Model decides when to call functions
- `none` - Never call functions
- `{"type": "function", "function": {"name": "get_weather"}}` - Force specific function

**Response with Tool Calls:**
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

**Tool Streaming:**
```env
GLM_TOOL_STREAM_ENABLED=true  # Enable streaming for function calls (GLM-4.6 only)
```

---

### 4. Multimodal Support

**Supported Input Types:**

**Text:**
```json
{
  "role": "user",
  "content": "Explain this concept"
}
```

**Images (Vision Models):**
```json
{
  "role": "user",
  "content": [
    {
      "type": "text",
      "text": "What's in this image?"
    },
    {
      "type": "image_url",
      "image_url": {
        "url": "https://example.com/image.jpg"
      }
    }
  ]
}
```

**Files (Document Analysis):**
```json
{
  "role": "user",
  "content": [
    {
      "type": "text",
      "text": "Summarize this document"
    },
    {
      "type": "file",
      "file": {
        "file_id": "file_123"
      }
    }
  ]
}
```

**Audio:**
```json
{
  "role": "user",
  "content": [
    {
      "type": "audio",
      "audio": {
        "url": "https://example.com/audio.mp3"
      }
    }
  ]
}
```

**Video:**
```json
{
  "role": "user",
  "content": [
    {
      "type": "video",
      "video": {
        "url": "https://example.com/video.mp4"
      }
    }
  ]
}
```

**Vision Models:**
- `glm-4.5v` - Vision model with multimodal support
- `glm-4.5v-plus` - Enhanced vision capabilities
- `glm-4.6` - Flagship with multimodal support

---

### 5. Multi-Turn Conversations

**Conversation Context:**
```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are a helpful assistant."
    },
    {
      "role": "user",
      "content": "What is Python?"
    },
    {
      "role": "assistant",
      "content": "Python is a high-level programming language..."
    },
    {
      "role": "user",
      "content": "What are its main features?"
    }
  ]
}
```

**Context Management:**
- Automatic context tracking
- Token limit management
- Context window optimization
- Conversation history pruning

**Continuation ID:**
```json
{
  "continuation_id": "conv_123",
  "prompt": "Continue the previous discussion"
}
```

---

## Advanced Features (New in zai-sdk v0.0.4)

### 1. Video Generation (CogVideoX-2)

**Endpoint:** `POST /paas/v4/videos/generations`

**Text-to-Video:**
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

**Image-to-Video:**
```json
{
  "model": "cogvideox-2",
  "prompt": "Animate this image with smooth motion",
  "image_url": "https://example.com/image.jpg",
  "quality": "high",
  "fps": 30
}
```

**Parameters:**
- `model`: "cogvideox-2"
- `prompt`: Text description of desired video
- `image_url`: Starting image for image-to-video
- `quality`: "low", "medium", "high"
- `fps`: Frames per second (24, 30, 60)
- `size`: Video dimensions ("1280x720", "1920x1080")
- `duration`: Video length in seconds (1-10)
- `audio`: Include audio generation (true/false)

**Async Workflow:**
1. Submit generation request → Receive task ID
2. Poll for completion: `GET /paas/v4/videos/retrieve_videos_result?task_id={id}`
3. Download generated video from returned URL

---

### 2. Assistant API

**Endpoint:** `POST /paas/v4/assistant/conversation`

**Model:** `glm-4-assistant`

**Features:**
- Structured conversations
- Context management
- Streaming support
- Metadata tracking
- File attachments

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
  ]
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
      "content": "I'd be happy to help you plan your project..."
    }
  ],
  "metadata": {
    "tokens_used": 150
  }
}
```

---

### 3. Character Role-Playing (CharGLM-3)

**Model:** `charglm-3`

**Features:**
- Character creation
- Meta parameters for personality
- Conversation handling
- Role-playing scenarios

**Character Definition:**
```json
{
  "model": "charglm-3",
  "meta": {
    "user_info": "A software developer learning AI",
    "bot_info": "An experienced AI researcher and mentor",
    "bot_name": "Dr. AI",
    "user_name": "Student"
  },
  "messages": [
    {
      "role": "user",
      "content": "Can you explain neural networks?"
    }
  ]
}
```

**Meta Parameters:**
- `user_info`: Description of the user
- `bot_info`: Description of the character/bot
- `bot_name`: Character's name
- `user_name`: User's name

---

### 4. File Upload and Management

**Upload Endpoint:** `POST /paas/v4/files/upload`

**Upload File:**
```python
with open("document.pdf", "rb") as f:
    response = client.files.create(
        file=f,
        purpose="assistants"
    )
    file_id = response.id
```

**Use in Chat:**
```json
{
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "Summarize this document"
        },
        {
          "type": "file",
          "file": {
            "file_id": "file_123"
          }
        }
      ]
    }
  ]
}
```

**Supported Formats:**
- PDF documents
- Text files
- Images (JPEG, PNG, GIF)
- Audio files (MP3, WAV)
- Video files (MP4, AVI)

---

### 5. Embeddings

**Endpoint:** `POST /paas/v4/embeddings`

**Generate Embeddings:**
```json
{
  "model": "embedding-2",
  "input": "Text to embed",
  "dimensions": 1024
}
```

**Batch Processing:**
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
      "embedding": [0.123, -0.456, ...],
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

## Configuration Parameters

### Temperature

**Range:** 0.0 - 1.0  
**Default:** 0.6 (GLM-4.6), 0.75 (GLM-4-32B)

**Effect:**
- 0.0: Deterministic, focused responses
- 0.5: Balanced creativity and consistency
- 1.0: Maximum creativity and randomness

### Top-P Sampling

**Range:** 0.0 - 1.0  
**Default:** 0.95 (GLM-4.6), 0.9 (GLM-4-32B)

**Effect:**
- Lower values: More focused on likely tokens
- Higher values: More diverse token selection

### Max Tokens

**GLM-4.6:** Up to 98,304 tokens output  
**GLM-4.5 Series:** Up to 96,000 tokens output  
**GLM-4.5V Series:** Up to 16,000 tokens output

### Thinking Mode (Chain of Thought)

**GLM-4.5+ Only:**
```json
{
  "thinking": {
    "type": "enabled"
  }
}
```

**Options:**
- `enabled`: Model automatically determines when to think
- `disabled`: No chain of thought reasoning

**Response with Thinking:**
```json
{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "The answer is 42",
        "reasoning_content": "<think>Let me analyze this step by step...</think>"
      }
    }
  ]
}
```

---

## Response Formats

### Text Mode (Default)

```json
{
  "response_format": {
    "type": "text"
  }
}
```

Returns natural language text.

### JSON Mode

```json
{
  "response_format": {
    "type": "json_object"
  }
}
```

Returns valid JSON data. Recommended to request JSON in prompt.

**Example:**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Return user data as JSON with fields: name, age, email"
    }
  ],
  "response_format": {
    "type": "json_object"
  }
}
```

---

## OpenAI Compatibility

### Drop-In Replacement

**OpenAI Code:**
```python
from openai import OpenAI

client = OpenAI(
    api_key="sk-...",
    base_url="https://api.openai.com/v1"
)
```

**Z.ai Equivalent:**
```python
from openai import OpenAI

client = OpenAI(
    api_key="your_zai_key",
    base_url="https://api.z.ai/v1"
)
```

### Compatible Tools

**Claude Code Integration:**
```env
ANTHROPIC_API_KEY=your_zai_key
ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic
```

**Kilo Code, Roo Code, Cline:**
```env
OPENAI_API_KEY=your_zai_key
OPENAI_BASE_URL=https://api.z.ai/v1
```

---

## Performance Characteristics

### GLM-4.6 Performance

**Context Window:** 200,000 tokens  
**Response Speed:** ~50 tokens/second (streaming)  
**Token Efficiency:** ~15% fewer tokens than GLM-4.5  
**Cost:** $0.60 input / $2.20 output per million tokens

**Benchmarks:**
- Near parity with Claude Sonnet 4 (48.6% win rate)
- Lags behind Claude Sonnet 4.5 in coding tasks
- Superior agentic abilities
- Advanced reasoning capabilities

### Kimi K2 Performance

**Context Window:** 256,000 tokens (256K) - Largest available
**Architecture:** 1T total parameters, 32B active (MoE)
**Pricing:** $0.60 input / $2.50 output per million tokens
**Caching:** Advanced prompt caching
**Quality:** Superior for tool use, coding, agentic workflows
**Cost:** Competitive (1/5th cost of Claude Sonnet 4)

**Key Capabilities:**
- **Agentic Intelligence:** Specifically designed for autonomous problem-solving
- **Tool Use:** Enhanced tool-calling integration (native MCP support)
- **Coding:** Specifically tuned for code generation and debugging
- **Multi-Step Reasoning:** Complex task decomposition and planning
- **Long Context:** 256K window ideal for large codebase analysis

**Performance Benchmarks:**
- SOTA on SWE Bench Verified (among open models)
- SOTA on Tau2 and AceBench
- Enhanced coding capabilities (especially front-end)
- Superior agentic abilities vs competitors

---

## Error Handling

### Common Error Codes

**Authentication Errors:**
- `401 Unauthorized`: Invalid API key
- `403 Forbidden`: Insufficient permissions

**Rate Limiting:**
- `429 Too Many Requests`: Rate limit exceeded

**Request Errors:**
- `400 Bad Request`: Invalid request format
- `422 Unprocessable Entity`: Invalid parameters

**Server Errors:**
- `500 Internal Server Error`: Server-side issue
- `503 Service Unavailable`: Service temporarily unavailable

### Retry Strategy

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def call_api(**kwargs):
    return await client.chat.completions.create(**kwargs)
```

---

**Next:** Read `05-api-endpoints-reference.md` for complete API documentation

