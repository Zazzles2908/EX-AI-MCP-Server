# Kimi Provider (Moonshot)

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Related:** [glm.md](glm.md), [routing.md](routing.md), [../02-provider-architecture.md](../02-provider-architecture.md)

---

## Configuration

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

---

## Available Models

### K2 Series (Agentic Intelligence)

**kimi-k2-0905-preview** - Latest K2 **[RECOMMENDED]**
- **Context:** 256K tokens (262,144 tokens)
- **Architecture:** 1T/32B MoE (Mixture of Experts)
- **Pricing:** $0.15 (cache hit) / $0.60 (cache miss) input, $2.50 output per million tokens
- **Features:** Enhanced coding, tool-calling, agentic workflows, automatic caching
- **Performance:** SOTA on SWE Bench Verified, Tau2, AceBench (among open models)
- **Use Case:** Production deployments with version pinning for stability

**kimi-k2-0711-preview** - Original K2
- **Context:** 128K tokens (131,072 tokens)
- **Pricing:** $0.15 (cache hit) / $0.60 (cache miss) input, $2.50 output per million tokens
- **Features:** Original K2 capabilities
- **Use Case:** Legacy compatibility

**kimi-k2-turbo-preview** - Fast K2 **[RECOMMENDED FOR SPEED]**
- **Context:** 256K tokens (262,144 tokens)
- **Pricing:** $0.60 (cache hit) / $2.40 (cache miss) input, $10.00 output per million tokens
- **Features:** Faster responses, same K2 capabilities, automatic caching
- **Use Case:** Fast responses with long context

**kimi-thinking-preview** - Thinking Mode
- **Context:** 128K tokens
- **Features:** Reasoning extraction via `reasoning_content` field
- **Use Case:** Complex reasoning, deep analysis

### Legacy Models

- `moonshot-v1-128k` - 128K context window (superseded by K2)
- `moonshot-v1-32k` - 32K context window (legacy)
- `moonshot-v1-8k` - 8K context window (legacy)

**Note:** Use `kimi-k2-0905-preview` for production (version pinning ensures stability)

---

## SDK Integration

### OpenAI-Compatible API

**Installation:**
```bash
pip install openai>=1.55.2
```

**Basic Usage:**
```python
from openai import OpenAI

client = OpenAI(
    api_key="your_moonshot_api_key",
    base_url="https://api.moonshot.ai/v1"
)

response = client.chat.completions.create(
    model="kimi-k2-0905-preview",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ],
    temperature=0.5
)
```

### Streaming Support

```python
response = client.chat.completions.create(
    model="kimi-k2-0905-preview",
    messages=[...],
    stream=True
)

for chunk in response:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

---

## Features

### Advanced Caching

**Automatic Prompt Caching:**
- Caches repeated prompts automatically
- Reduced costs for repeated queries
- Faster response times for cached content
- No configuration required

**Benefits:**
- Up to 90% cost reduction for repeated prompts
- Significantly faster response times
- Ideal for iterative workflows

### Quality Reasoning

**Superior Reasoning Capabilities:**
- Better for complex analysis and problem-solving
- Excellent for long-context tasks (256K tokens)
- Strong performance on coding benchmarks
- Advanced tool-calling and agentic workflows

**Best For:**
- Code generation and debugging
- Long-context analysis
- Complex reasoning chains
- Agentic workflows with tool use

---

## File Management

### Upload Files

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
            "content": file.id  # Reference uploaded file
        },
        {
            "role": "user",
            "content": "Summarize this document"
        }
    ]
)
```

### Extract File Content

```python
# Extract content from uploaded file
content = client.files.content(file.id)
print(content.text)
```

### Delete Files

```python
# Delete file after use
client.files.delete(file.id)
```

**Best Practices:**
- Delete files after use to avoid accumulation
- Use batch uploads for multiple files
- Track file IDs for cleanup
- Verify cleanup with `files.list()` API

---

## Use Cases

### Code Generation & Debugging
- Superior coding capabilities
- Excellent for complex algorithms
- Strong debugging assistance

### Long-Context Analysis
- 256K token context window
- Ideal for large codebases
- Comprehensive document analysis

### Agentic Workflows
- Advanced tool-calling
- Multi-step reasoning
- Complex task orchestration

### Quality Reasoning
- Complex problem-solving
- Detailed analysis
- High-quality outputs

---

## Performance Characteristics

**Strengths:**
- Long context processing (256K tokens)
- Quality reasoning and analysis
- Advanced caching for cost reduction
- Strong coding and tool-calling

**Considerations:**
- Slightly higher cost than GLM ($0.60/$2.50 vs $0.60/$2.20)
- No native web search (use GLM for web search)
- Text-only (no multimodal support)

---

## Related Documentation

- [glm.md](glm.md) - GLM provider details
- [routing.md](routing.md) - Agentic routing logic
- [../02-provider-architecture.md](../02-provider-architecture.md) - Provider architecture overview
- [../api/files.md](../api/files.md) - File management API
- [../features/caching.md](../features/caching.md) - Caching strategies

