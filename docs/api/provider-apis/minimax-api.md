# MiniMax Provider API Documentation

## Overview
MiniMax provides advanced AI models (MiniMax-M2, MiniMax-M2-Stable, abab6.5s-chat, abab6.5g-chat) through an Anthropic-compatible API at `https://api.minimax.io/anthropic`.

**API Base URL**: `https://api.minimax.io/anthropic`  
**Provider Classification**: Advanced Anthropic-compatible models  
**Access Method**: Anthropic SDK with OpenAI SDK support  

## Official Documentation
**Reference**: https://platform.minimax.io/docs/api-reference/text-anthropic-api

## Available Models

### 1. MiniMax-M2
- **Model Name**: `MiniMax-M2`
- **Context Window**: 8,192 tokens
- **Max Output**: 4,096 tokens
- **Features**: Full thinking, function calling, streaming, tool use
- **Specialization**: Advanced reasoning with interleaved thinking
- **Status**: Premium model with full capabilities

### 2. MiniMax-M2-Stable  
- **Model Name**: `MiniMax-M2-Stable`
- **Context Window**: 8,192 tokens
- **Max Output**: 4,096 tokens
- **Features**: Full thinking, function calling, streaming, tool use
- **Status**: Stable version for production use
- **Recommended for**: Production deployments requiring stability

### 3. ABAB 6.5s Chat
- **Model Name**: `abab6.5s-chat`
- **Context Window**: 8,192 tokens
- **Max Output**: 4,096 tokens
- **Features**: Full thinking, function calling, streaming, tool use
- **Specialization**: Fast response with thinking capabilities
- **Aliases**: `abab6.5s`, `6.5s-chat`

### 4. ABAB 6.5g Chat
- **Model Name**: `abab6.5g-chat`
- **Context Window**: 8,192 tokens
- **Max Output**: 4,096 tokens
- **Features**: Full thinking, function calling, streaming, tool use
- **Specialization**: General purpose with enhanced capabilities
- **Aliases**: `abab6.5g`, `6.5g-chat`

## ✅ Fully Supported Features

### Core Capabilities
- ✅ **Thinking Process**: Interleaved thinking with reasoning content
- ✅ **Function Calling**: Full tool calling support
- ✅ **Streaming**: Real-time streaming responses
- ✅ **Tool Use**: Complete tool integration
- ✅ **Temperature**: Range (0.0, 1.0]
- ✅ **Max Tokens**: Up to 4,096 tokens
- ✅ **System Prompts**: Full support
- ✅ **Metadata**: Metadata support

### Message Types Support
- ✅ **Text Messages**: `type="text"` fully supported
- ✅ **Tool Calls**: `type="tool_use"` fully supported  
- ✅ **Tool Results**: `type="tool_result"` fully supported
- ✅ **Thinking Content**: `type="thinking"` fully supported
- ❌ **Images**: `type="image"` not supported yet
- ❌ **Documents**: `type="document"` not supported yet

## API Integration

### Authentication
```python
from anthropic import Anthropic

client = Anthropic(
    api_key=os.getenv("MINIMAX_API_KEY"),
    base_url="https://api.minimax.io/anthropic"
)
```

### Basic Usage
```python
response = client.messages.create(
    model="MiniMax-M2",
    max_tokens=1000,
    messages=[
        {"role": "user", "content": "Hello, how are you?"}
    ]
)
```

### Interleaved Thinking Process
```python
def extract_thinking_and_answer(response):
    thinking_content = ""
    final_answer = ""
    
    for content_block in response.content:
        if hasattr(content_block, 'thinking'):
            thinking_content = str(content_block.thinking)
        elif hasattr(content_block, 'text'):
            final_answer = content_block.text
    
    return thinking_content, final_answer
```

### Streaming with Thinking
```python
stream = client.messages.create(
    model="MiniMax-M2",
    max_tokens=1000,
    system="You are a helpful assistant.",
    messages=[{"role": "user", "content": "Explain quantum computing"}],
    stream=True,
)

for chunk in stream:
    if chunk.type == "content_block_delta":
        if hasattr(chunk.delta, 'thinking'):
            print(chunk.delta.thinking, end="", flush=True)  # Thinking process
        elif hasattr(chunk.delta, 'text'):
            print(chunk.delta.text, end="", flush=True)  # Response content
```

## Tool Use Example

```python
import anthropic
import json

# Define tools
tools = [
    {
        "name": "get_weather",
        "description": "Get weather of a location",
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, US",
                }
            },
            "required": ["location"]
        }
    }
]

# Use tools in conversation
response = client.messages.create(
    model="MiniMax-M2",
    max_tokens=4096,
    messages=[{"role": "user", "content": "How's the weather in San Francisco?"}],
    tools=tools,
)

# Handle tool calls and continue conversation
if response.content:
    for block in response.content:
        if block.type == "thinking":
            print(f"Thinking: {block.thinking}")
        elif block.type == "tool_use":
            print(f"Tool call: {block.name}({block.input})")
            # Execute tool and continue conversation
        elif block.type == "text":
            print(f"Response: {block.text}")
```

## OpenAI SDK Compatibility

```python
from openai import OpenAI

# Configure for MiniMax
client = OpenAI(
    base_url="https://api.minimax.io/v1",
    api_key=os.getenv("MINIMAX_API_KEY")
)

# Use with reasoning_split for cleaner output
response = client.chat.completions.create(
    model="MiniMax-M2",
    messages=[{"role": "user", "content": "Analyze this problem"}],
    extra_body={"reasoning_split": True},  # Separate thinking content
)

# Access thinking and response separately
thinking = response.choices[0].message.reasoning_details[0]['text']
content = response.choices[0].message.content
```

## Configuration

### Environment Variables
```bash
MINIMAX_API_KEY=your_minimax_api_key_here
MINIMAX_API_URL=https://api.minimax.io/anthropic
MINIMAX_TIMEOUT=30
MINIMAX_RETRY=3
```

### Provider Registration
```python
ProviderType.MINIMAX: {
    "api_key_env": "MINIMAX_API_KEY",
    "base_url": "https://api.minimax.io/anthropic",
    "models": ["MiniMax-M2", "MiniMax-M2-Stable", "abab6.5s-chat", "abab6.5g-chat"],
    "capabilities": {
        "thinking_mode": True,
        "context_window": 8192,
        "max_output_tokens": 4096,
        "supports_streaming": True,
        "supports_vision": False,
        "supports_function_calling": True,
        "supports_tools": True
    }
}
```

## Parameter Support Matrix

| Parameter | Support Status | Description |
|-----------|----------------|-------------|
| model | ✅ Fully supported | MiniMax-M2, MiniMax-M2-Stable, abab6.5s-chat, abab6.5g-chat |
| messages | ✅ Partial support | Text and tool calls, no image/document input |
| max_tokens | ✅ Fully supported | Maximum generation tokens |
| stream | ✅ Fully supported | Streaming response |
| system | ✅ Fully supported | System prompt |
| temperature | ✅ Fully supported | Range (0.0, 1.0], controls output randomness |
| tool_choice | ✅ Fully supported | Tool selection strategy |
| tools | ✅ Fully supported | Tool definitions |
| thinking | ✅ Fully supported | Reasoning Content (key feature!) |
| top_p | ✅ Fully supported | Nucleus sampling parameter |
| metadata | ✅ Fully supported | Metadata |
| top_k | ❌ Ignored | This parameter will be ignored |
| stop_sequences | ❌ Ignored | This parameter will be ignored |
| service_tier | ❌ Ignored | This parameter will be ignored |
| mcp_servers | ❌ Ignored | This parameter will be ignored |
| context_management | ❌ Ignored | This parameter will be ignored |
| container | ❌ Ignored | This parameter will be ignored |

## Error Handling

### Common Error Patterns
- **Timeout Errors**: Increase `MINIMAX_TIMEOUT`
- **Rate Limiting**: Implement exponential backoff
- **Authentication**: Verify `MINIMAX_API_KEY` is valid
- **Max Tokens**: Adjust `max_tokens` parameter (max 4096)

### Retry Strategy
```python
import asyncio
import time

async def call_minimax_with_retry(client, request, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await client.messages.create(**request)
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

## Performance Characteristics

### Strengths
- **Advanced Reasoning**: Interleaved thinking process for complex analysis
- **Tool Integration**: Full function calling and tool use support
- **Streaming**: Real-time response streaming
- **Anthropic Compatibility**: Familiar API patterns
- **OpenAI Compatibility**: Dual SDK support with reasoning_split

### Limitations
- **No Vision**: Image/document input not supported yet
- **Context Limit**: 8,192 tokens (vs some models with 200K+)
- **Max Output**: 4,096 tokens per request

### Recommended Usage
- **Use for**: Complex reasoning, tool integration, streaming applications
- **Avoid for**: Image processing, extremely long documents
- **Best for**: Applications requiring advanced reasoning with tools

## Integration Best Practices

### 1. Provider Selection Logic
```python
def should_use_minimax(task_type, needs_tools, needs_thinking):
    """Determine if MiniMax is appropriate for the task"""
    if needs_thinking and needs_tools:
        return True  # Perfect for MiniMax capabilities
    if task_type in ['debug', 'analyze', 'complex_reasoning']:
        return True
    return False
```

### 2. Thinking Process Integration
```python
def handle_minimax_response(response):
    """Extract thinking and answer from MiniMax response"""
    thinking = ""
    answer = ""
    
    for block in response.content:
        if block.type == "thinking":
            thinking = block.thinking
        elif block.type == "text":
            answer = block.text
    
    return {"thinking": thinking, "answer": answer, "has_thinking": bool(thinking)}
```

### 3. Tool Integration
```python
def handle_minimax_tools(response):
    """Process tool calls from MiniMax response"""
    tool_calls = [block for block in response.content if block.type == "tool_use"]
    
    for tool_call in tool_calls:
        # Execute tool with tool_call.input parameters
        # Continue conversation with tool results
        pass
```

## Comparison with Other Providers

| Feature | MiniMax M2 | GLM | Kimi |
|---------|------------|-----|------|
| **Context Window** | 8,192 | 200,000 | 256,000 |
| **Thinking Mode** | ✅ Interleaved | ✅ Available | ✅ Available |
| **Function Calling** | ✅ Full Support | ✅ Yes | ✅ Yes |
| **Tool Use** | ✅ Full Support | ✅ Yes | ✅ Yes |
| **Streaming** | ✅ Full Support | ✅ Yes | ✅ Yes |
| **Vision Support** | ❌ No | ✅ Yes | ✅ Yes |
| **Reasoning Quality** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Tool Integration** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Specialization** | Advanced Reasoning | General Purpose | Balanced |

---

**Last Updated**: 2025-11-16  
**Version**: 3.0 (Complete 4-Model Support)  
**Status**: Production Ready
