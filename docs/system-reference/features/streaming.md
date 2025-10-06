# Streaming Support

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Related:** [../04-features-and-capabilities.md](../04-features-and-capabilities.md), [../02-provider-architecture.md](../02-provider-architecture.md)

---

## Overview

The EX-AI-MCP-Server provides real-time streaming support for both GLM and Kimi providers using Server-Sent Events (SSE) protocol. Streaming enables token-by-token delivery for better user experience and lower perceived latency.

---

## Configuration

### Environment Variables

**GLM Provider:**
```env
GLM_STREAM_ENABLED=true
```

**Kimi Provider:**
```env
KIMI_STREAM_ENABLED=true
```

---

## Benefits

- **Real-time response generation** - See responses as they're generated
- **Lower perceived latency** - Immediate feedback instead of waiting for complete response
- **Better user experience** - Progressive display of long responses
- **Token-by-token delivery** - Smooth streaming without buffering
- **Immediate feedback** - Users see progress immediately

---

## Implementation

### Server-Sent Events (SSE) Protocol

**Automatic chunk aggregation:**
- Chunks are aggregated automatically
- Metadata tracking (`metadata.streamed = true`)
- Graceful fallback to non-streaming if errors occur

**Usage:**
```python
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

## Provider Support

| Provider | Streaming Support | Protocol |
|----------|------------------|----------|
| GLM | ✅ Yes | SSE |
| Kimi | ✅ Yes | SSE |

---

## Best Practices

- Enable streaming for long responses
- Handle connection interruptions gracefully
- Aggregate chunks for display
- Monitor metadata for streaming status
- Use fallback for non-streaming scenarios

---

## Related Documentation

- [../04-features-and-capabilities.md](../04-features-and-capabilities.md) - Features overview
- [../providers/glm.md](../providers/glm.md) - GLM streaming details
- [../providers/kimi.md](../providers/kimi.md) - Kimi streaming details

