# Tool Calling

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Related:** [../04-features-and-capabilities.md](../04-features-and-capabilities.md), [../03-tool-ecosystem.md](../03-tool-ecosystem.md)

---

## Overview

OpenAI-compatible function calling for agentic workflows and tool integration. Both GLM and Kimi providers support tool calling with the same API.

---

## Configuration

**Environment Variables:**
```env
# Enable tool calling
GLM_ENABLE_TOOL_CALLING=true
KIMI_ENABLE_TOOL_CALLING=true
```

---

## Usage

### Define Tools

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
                    "location": {
                        "type": "string",
                        "description": "City name"
                    }
                },
                "required": ["location"]
            }
        }
    }
]
```

### Call with Tools

```python
response = client.chat.completions.create(
    model="glm-4.6",
    messages=[
        {"role": "user", "content": "What's the weather in San Francisco?"}
    ],
    tools=tools,
    tool_choice="auto"
)

# Handle tool calls
if response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        # Execute function and return result
```

---

## Provider Support

| Provider | Tool Calling Support |
|----------|---------------------|
| GLM | ✅ OpenAI-compatible |
| Kimi | ✅ OpenAI-compatible |

---

## Best Practices

- Define clear function descriptions
- Use strict parameter schemas
- Handle tool call errors gracefully
- Return structured results
- Use Kimi for complex tool workflows

---

## Related Documentation

- [../04-features-and-capabilities.md](../04-features-and-capabilities.md) - Features overview
- [../03-tool-ecosystem.md](../03-tool-ecosystem.md) - Available tools
- [../providers/glm.md](../providers/glm.md) - GLM tool calling
- [../providers/kimi.md](../providers/kimi.md) - Kimi tool calling

