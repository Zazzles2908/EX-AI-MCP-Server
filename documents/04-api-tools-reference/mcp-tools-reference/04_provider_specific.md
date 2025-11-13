# MCP Provider-Specific Tools Reference

> **Version:** 1.0.0
> **Last Updated:** 2025-11-10
> **Status:** ✅ **Complete**

## 🎯 Overview

This section documents the 6 Provider-Specific Tools available in the EX-AI MCP Server. These tools provide direct access to GLM and Kimi provider capabilities, including direct API calls, streaming, batch processing, and specialized features.

---

## 📚 Tool Categories

### 🌐 Provider-Specific Tools (6 Total)
- **glm_complete** - Direct GLM API access
- **glm_stream** - GLM streaming responses
- **glm_batch** - Batch GLM requests
- **kimi_analyze** - Kimi document analysis
- **kimi_file_chat** - Kimi with file context
- **kimi_vision** - Kimi image analysis

---

## 💬 Tool Details

### 1. glm_complete

**Description:** Direct GLM API access with full parameter control

**Parameters:**
- `model` (string, required) - GLM model: 'glm-4', 'glm-4.5', 'glm-4.5-flash', 'glm-4.6'
- `messages` (array, required) - Conversation messages
- `temperature` (float, optional) - Creativity (0-1, default: 0.3)
- `max_tokens` (int, optional) - Maximum output tokens (default: 8000)
- `stream` (boolean, optional) - Enable streaming (default: false)

**Example Usage:**
```python
# Direct GLM completion
result = exai_mcp.glm_complete(
    model="glm-4.6",
    messages=[
        {"role": "user", "content": "Explain microservices architecture"}
    ],
    temperature=0.3,
    max_tokens=2000
)

# With system prompt
result = exai_mcp.glm_complete(
    model="glm-4.6",
    messages=[
        {"role": "system", "content": "You are a senior software architect"},
        {"role": "user", "content": "Design a scalable e-commerce system"}
    ]
)
```

**Response Format:**
```json
{
  "success": true,
  "data": {
    "model": "glm-4.6",
    "choices": [
      {
        "message": {
          "role": "assistant",
          "content": "Microservices architecture is a design pattern..."
        },
        "finish_reason": "stop"
      }
    ],
    "usage": {
      "prompt_tokens": 45,
      "completion_tokens": 234,
      "total_tokens": 279
    },
    "response_time": 1.2
  }
}
```

---

### 2. glm_stream

**Description:** GLM streaming responses for real-time interaction

**Parameters:**
- `model` (string, required) - GLM model
- `messages` (array, required) - Conversation messages
- `stream_options` (object, optional):
  - `chunk_size` (int) - Tokens per chunk (default: 10)
  - `delay_ms` (int) - Delay between chunks (default: 50)

**Example Usage:**
```python
# Streaming response
stream = exai_mcp.glm_stream(
    model="glm-4.6",
    messages=[
        {"role": "user", "content": "Write a detailed technical blog post"}
    ]
)

# Consume stream
for chunk in stream:
    print(chunk.data.token, end="", flush=True)
```

---

### 3. glm_batch

**Description:** Process multiple GLM requests efficiently

**Parameters:**
- `requests` (array, required) - List of request objects
- `parallel` (boolean, optional) - Process in parallel (default: true)
- `max_parallel` (int, optional) - Max concurrent requests (default: 5)

**Example Usage:**
```python
# Batch requests
results = exai_mcp.glm_batch(
    requests=[
        {
            "model": "glm-4.5",
            "messages": [{"role": "user", "content": "Explain Python"}]
        },
        {
            "model": "glm-4.5",
            "messages": [{"role": "user", "content": "Explain JavaScript"}]
        }
    ],
    parallel=True,
    max_parallel=2
)
```

---

### 4. kimi_analyze

**Description:** Kimi document analysis with advanced NLP

**Parameters:**
- `file_id` (string, required) - Provider file ID
- `analysis_type` (string, optional) - Type: 'summary', 'extract', 'translate', 'question'
- `language` (string, optional) - Target language
- `questions` (array, optional) - Specific questions to answer

**Example Usage:**
```python
# Analyze document
result = exai_mcp.kimi_analyze(
    file_id="file_abc123",
    analysis_type="summary",
    language="en"
)

# Ask specific questions
result = exai_mcp.kimi_analyze(
    file_id="file_abc123",
    analysis_type="question",
    questions=[
        "What are the main security concerns?",
        "What are the performance requirements?"
    ]
)
```

---

### 5. kimi_file_chat

**Description:** Interactive chat with file context using Kimi

**Parameters:**
- `file_id` (string, required) - File ID to discuss
- `message` (string, required) - User message
- `context_window` (int, optional) - Context size (default: 10)
- `model` (string, optional) - Kimi model

**Example Usage:**
```python
# Chat about file
result = exai_mcp.kimi_file_chat(
    file_id="file_abc123",
    message="What are the key points in this document?",
    context_window=20
)

# Follow-up questions
result = exai_mcp.kimi_file_chat(
    file_id="file_abc123",
    message="Can you elaborate on point 3?",
    context_window=15
)
```

---

### 6. kimi_vision

**Description:** Image analysis and understanding with Kimi vision

**Parameters:**
- `file_id` (string, required) - Image file ID
- `analysis_type` (string, optional) - Type: 'describe', 'ocr', 'detect', 'analyze'
- `language` (string, optional) - Response language
- `options` (object, optional) - Analysis options

**Example Usage:**
```python
# Describe image
result = exai_mcp.kimi_vision(
    file_id="image_abc123",
    analysis_type="describe"
)

# OCR text extraction
text = exai_mcp.kimi_vision(
    file_id="image_abc123",
    analysis_type="ocr"
)

# Detect objects
objects = exai_mcp.kimi_vision(
    file_id="image_abc123",
    analysis_type="detect"
)
```

---

**Document Version:** 1.0.0
**Created:** 2025-11-10
**Author:** EX-AI MCP Server API Team
**Status:** ✅ **Complete - Provider-Specific Tools Reference**
