# API SDK REFERENCE - Z.ai (GLM) & Moonshot (Kimi)

**Date:** 2025-10-16  
**GLM-4.6 Research:** `debb44af-15b9-456d-9b88-6a2519f81427` (6 turns remaining)  
**Status:** Comprehensive SDK Documentation  

---

## 🎯 OVERVIEW

This guide provides comprehensive documentation for integrating Z.ai (GLM) and Moonshot (Kimi) SDK libraries with the EXAI MCP Server. Based on official API documentation and best practices research.

**Supported SDKs:**
- **Z.ai SDK:** Official Python SDK for GLM models (glm-4.6, glm-4.5-flash, etc.)
- **Moonshot SDK:** OpenAI-compatible SDK for Kimi models (kimi-k2, moonshot-v1-*)

---

## 📦 INSTALLATION

### Z.ai (GLM) SDK

```bash
# Install official Z.ai SDK
pip install zhipuai

# Verify installation
python -c "import zhipuai; print(zhipuai.__version__)"
```

**Package:** `zhipuai`  
**Repository:** https://github.com/zhipuai/zhipuai-sdk  
**Documentation:** https://open.bigmodel.cn/dev/api  

### Moonshot (Kimi) SDK

```bash
# Install OpenAI SDK (Moonshot is compatible)
pip install openai

# Verify installation
python -c "import openai; print(openai.__version__)"
```

**Package:** `openai`  
**Repository:** https://github.com/openai/openai-python  
**Moonshot Docs:** https://platform.moonshot.cn/docs  

---

## 🔐 AUTHENTICATION

### Z.ai (GLM) Authentication

**Method 1: Environment Variable (Recommended)**
```bash
# .env or .env.docker
ZHIPUAI_API_KEY=your_api_key_here
```

```python
import zhipuai
import os

# Automatically uses ZHIPUAI_API_KEY from environment
client = zhipuai.ZhipuAI()
```

**Method 2: Direct Initialization**
```python
import zhipuai

client = zhipuai.ZhipuAI(api_key="your_api_key_here")
```

**Get API Key:** https://platform.zhipuai.ai/

### Moonshot (Kimi) Authentication

**Method 1: Environment Variable (Recommended)**
```bash
# .env or .env.docker
MOONSHOT_API_KEY=your_api_key_here
```

```python
from openai import OpenAI
import os

client = OpenAI(
    api_key=os.getenv("MOONSHOT_API_KEY"),
    base_url="https://api.moonshot.cn/v1"
)
```

**Method 2: Direct Initialization**
```python
from openai import OpenAI

client = OpenAI(
    api_key="your_api_key_here",
    base_url="https://api.moonshot.cn/v1"
)
```

**Get API Key:** https://platform.moonshot.cn/console

---

## 🚀 BASIC USAGE

### Z.ai (GLM) - Basic Chat Completion

```python
import zhipuai

client = zhipuai.ZhipuAI()

response = client.chat.completions.create(
    model="glm-4.6",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is Python?"}
    ],
    temperature=0.7,
    max_tokens=1000
)

print(response.choices[0].message.content)
```

### Moonshot (Kimi) - Basic Chat Completion

```python
from openai import OpenAI

client = OpenAI(
    api_key="your_api_key",
    base_url="https://api.moonshot.cn/v1"
)

response = client.chat.completions.create(
    model="moonshot-v1-8k",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is Python?"}
    ],
    temperature=0.7,
    max_tokens=1000
)

print(response.choices[0].message.content)
```

---

## 🌊 STREAMING RESPONSES

### Z.ai (GLM) - Streaming

```python
import zhipuai

client = zhipuai.ZhipuAI()

stream = client.chat.completions.create(
    model="glm-4.6",
    messages=[{"role": "user", "content": "Tell me a story"}],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

### Moonshot (Kimi) - Streaming

```python
from openai import OpenAI

client = OpenAI(
    api_key="your_api_key",
    base_url="https://api.moonshot.cn/v1"
)

stream = client.chat.completions.create(
    model="moonshot-v1-8k",
    messages=[{"role": "user", "content": "Tell me a story"}],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

**Streaming Format:** Server-Sent Events (SSE)  
**Timeout Handling:** Set appropriate timeouts for streaming (5-10 minutes)  

---

## 📁 FILE UPLOAD & PROCESSING

### Moonshot (Kimi) - File Upload

```python
from openai import OpenAI

client = OpenAI(
    api_key="your_api_key",
    base_url="https://api.moonshot.cn/v1"
)

# Upload file
file_object = client.files.create(
    file=open("document.pdf", "rb"),
    purpose="file-extract"
)

print(f"File ID: {file_object.id}")

# Use file in chat
response = client.chat.completions.create(
    model="moonshot-v1-32k",
    messages=[
        {
            "role": "system",
            "content": f"File uploaded: {file_object.id}"
        },
        {
            "role": "user",
            "content": "Summarize this document"
        }
    ]
)

print(response.choices[0].message.content)
```

**Supported Formats:** PDF, DOCX, TXT, MD, XLSX, PPT  
**File Size Limit:** 100MB  
**Endpoint:** `/files`  

### File Extraction API

```python
# Get file content
file_content = client.files.content(file_id="file-xxx")

# List uploaded files
files = client.files.list()

# Delete file
client.files.delete(file_id="file-xxx")
```

---

## 🔍 WEB SEARCH INTEGRATION

### Z.ai (GLM) - Native Web Search

```python
import zhipuai

client = zhipuai.ZhipuAI()

# GLM models have built-in web search
response = client.chat.completions.create(
    model="glm-4.6",
    messages=[
        {
            "role": "user",
            "content": "What are the latest developments in AI?"
        }
    ],
    # Web search is automatically triggered when needed
    tools=[{
        "type": "web_search",
        "web_search": {
            "enable": True,
            "search_query": "latest AI developments 2025"
        }
    }]
)

print(response.choices[0].message.content)
```

**GLM Web Search Parameters:**
- `enable`: Enable/disable web search
- `search_query`: Custom search query
- `search_engine`: Search engine to use (default: "search-prime")
- `count`: Number of results (default: 10)
- `recency_filter`: Time filter (oneDay, oneWeek, oneMonth, oneYear, all)

---

## 🧠 THINKING MODE

### Z.ai (GLM) - Thinking Mode

```python
import zhipuai

client = zhipuai.ZhipuAI()

response = client.chat.completions.create(
    model="glm-4.6",
    messages=[
        {
            "role": "user",
            "content": "Solve this complex problem step by step: ..."
        }
    ],
    # Enable thinking mode for reasoning tasks
    thinking={
        "type": "enabled"  # or "disabled"
    }
)

# Access reasoning content
if hasattr(response.choices[0].message, 'reasoning_content'):
    print("Reasoning:", response.choices[0].message.reasoning_content)

print("Answer:", response.choices[0].message.content)
```

### Moonshot (Kimi) - Thinking Mode

```python
from openai import OpenAI

client = OpenAI(
    api_key="your_api_key",
    base_url="https://api.moonshot.cn/v1"
)

# Use kimi-thinking-preview model
response = client.chat.completions.create(
    model="kimi-thinking-preview",
    messages=[
        {
            "role": "user",
            "content": "Solve this complex problem step by step: ..."
        }
    ]
)

# Access reasoning content
if hasattr(response.choices[0].message, 'reasoning_content'):
    print("Reasoning:", response.choices[0].message.reasoning_content)

print("Answer:", response.choices[0].message.content)
```

---

## 💬 MULTI-TURN CONVERSATIONS

### Conversation History Management

```python
# Both SDKs use the same pattern
conversation_history = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is Python?"},
    {"role": "assistant", "content": "Python is a programming language..."},
    {"role": "user", "content": "Can you give me an example?"}
]

response = client.chat.completions.create(
    model="glm-4.6",  # or "moonshot-v1-8k"
    messages=conversation_history
)

# Add assistant response to history
conversation_history.append({
    "role": "assistant",
    "content": response.choices[0].message.content
})
```

### Continuation ID Pattern (EXAI)

```python
# EXAI pattern for conversation persistence
def chat_with_continuation(prompt, continuation_id=None):
    if continuation_id:
        # Load conversation history from storage
        history = load_conversation(continuation_id)
    else:
        # Create new conversation
        history = []
        continuation_id = str(uuid.uuid4())
    
    # Add user message
    history.append({"role": "user", "content": prompt})
    
    # Call model
    response = client.chat.completions.create(
        model="glm-4.6",
        messages=history
    )
    
    # Add assistant response
    history.append({
        "role": "assistant",
        "content": response.choices[0].message.content
    })
    
    # Save to storage
    save_conversation(continuation_id, history)
    
    return {
        "content": response.choices[0].message.content,
        "continuation_id": continuation_id
    }
```

---

## ⚙️ ADVANCED CONFIGURATION

### Z.ai (GLM) - Full Configuration

```python
import zhipuai

client = zhipuai.ZhipuAI(
    api_key="your_api_key",
    base_url="https://open.bigmodel.cn/api/paas/v4/",
    timeout=30.0,  # Request timeout in seconds
    max_retries=3,  # Maximum retry attempts
    # Additional httpx client options
    http_client=httpx.Client(
        limits=httpx.Limits(
            max_connections=100,
            max_keepalive_connections=20
        )
    )
)
```

### Moonshot (Kimi) - Full Configuration

```python
from openai import OpenAI
import httpx

client = OpenAI(
    api_key="your_api_key",
    base_url="https://api.moonshot.cn/v1",
    timeout=30.0,  # Request timeout in seconds
    max_retries=3,  # Maximum retry attempts
    # Additional httpx client options
    http_client=httpx.Client(
        limits=httpx.Limits(
            max_connections=100,
            max_keepalive_connections=20
        )
    )
)
```

---

## 🔄 ERROR HANDLING & RETRY LOGIC

### Comprehensive Error Handling

```python
import zhipuai
from zhipuai import ZhipuAIError
import time

def call_with_retry(client, max_retries=3, backoff_factor=2):
    """Call API with exponential backoff retry"""
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="glm-4.6",
                messages=[{"role": "user", "content": "Hello"}],
                timeout=30
            )
            return response
        
        except ZhipuAIError as e:
            if attempt == max_retries - 1:
                raise
            
            # Exponential backoff
            wait_time = backoff_factor ** attempt
            print(f"Retry {attempt + 1}/{max_retries} after {wait_time}s")
            time.sleep(wait_time)
        
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise

# Usage
try:
    response = call_with_retry(client)
    print(response.choices[0].message.content)
except Exception as e:
    print(f"Failed after retries: {e}")
```

### Common Error Codes

**Z.ai (GLM):**
- `401`: Invalid API key
- `429`: Rate limit exceeded
- `500`: Server error
- `503`: Service unavailable

**Moonshot (Kimi):**
- `401`: Authentication failed
- `429`: Too many requests
- `500`: Internal server error
- `503`: Service temporarily unavailable

---

## 📊 RATE LIMITING & QUOTAS

### Z.ai (GLM) Rate Limits

**Free Tier:**
- 100 requests/minute
- 10,000 tokens/minute

**Standard Tier:**
- 500 requests/minute
- 50,000 tokens/minute

**Enterprise Tier:**
- Custom limits

### Moonshot (Kimi) Rate Limits

**Standard Tier:**
- 100 requests/minute
- 20,000 tokens/minute

**Premium Tier:**
- 500 requests/minute
- 100,000 tokens/minute

**Enterprise Tier:**
- Custom limits

### Rate Limit Handling

```python
import time
from collections import deque

class RateLimiter:
    def __init__(self, max_requests=100, time_window=60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = deque()
    
    def wait_if_needed(self):
        now = time.time()
        
        # Remove old requests outside time window
        while self.requests and self.requests[0] < now - self.time_window:
            self.requests.popleft()
        
        # Check if we've hit the limit
        if len(self.requests) >= self.max_requests:
            sleep_time = self.time_window - (now - self.requests[0])
            if sleep_time > 0:
                time.sleep(sleep_time)
        
        self.requests.append(now)

# Usage
limiter = RateLimiter(max_requests=100, time_window=60)

for i in range(200):
    limiter.wait_if_needed()
    response = client.chat.completions.create(...)
```

---

## 📝 LOGGING BEST PRACTICES

### Structured Logging

```python
import logging
import json

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def log_api_call(model, messages, response, duration):
    """Log API call with structured data"""
    log_data = {
        "model": model,
        "message_count": len(messages),
        "response_tokens": response.usage.total_tokens if hasattr(response, 'usage') else None,
        "duration_ms": duration * 1000,
        "request_id": response.id if hasattr(response, 'id') else None
    }
    logger.info(f"API call completed: {json.dumps(log_data)}")

# Usage
import time

start = time.time()
response = client.chat.completions.create(
    model="glm-4.6",
    messages=[{"role": "user", "content": "Hello"}]
)
duration = time.time() - start

log_api_call("glm-4.6", messages, response, duration)
```

---

## ✅ BEST PRACTICES CHECKLIST

### Security
- [ ] Store API keys in environment variables (never hardcode)
- [ ] Use secret management for production (AWS Secrets Manager, etc.)
- [ ] Rotate API keys quarterly
- [ ] Implement API key validation on startup
- [ ] Mask API keys in logs

### Performance
- [ ] Implement connection pooling for high throughput
- [ ] Set appropriate timeouts (30s for chat, 5-10min for streaming)
- [ ] Use caching for frequently requested data
- [ ] Implement rate limiting to respect quotas
- [ ] Monitor API usage and costs

### Reliability
- [ ] Implement retry logic with exponential backoff
- [ ] Handle all error cases gracefully
- [ ] Implement circuit breaker pattern for failures
- [ ] Log all API calls for debugging
- [ ] Monitor API status pages

### Development
- [ ] Keep SDK versions updated
- [ ] Test with smaller contexts before scaling
- [ ] Implement graceful degradation for API failures
- [ ] Use type hints for better IDE support
- [ ] Write unit tests for API integrations

---

**Document Status:** ✅ COMPREHENSIVE - Based on official API documentation  
**Research Source:** GLM-4.6 with web search enabled  
**Conversation ID:** `debb44af-15b9-456d-9b88-6a2519f81427` (6 turns remaining)  
**Next Update:** As APIs evolve or new features are added

