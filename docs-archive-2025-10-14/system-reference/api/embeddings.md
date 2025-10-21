# Embeddings API

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Related:** [../05-api-endpoints-reference.md](../05-api-endpoints-reference.md), [authentication.md](authentication.md)

---

## Overview

Generate vector embeddings for text. Useful for semantic search, clustering, and similarity comparisons.

---

## Endpoint

**POST** `/embeddings`

**Base URLs:**
- GLM: `https://api.z.ai/v1/embeddings`
- Kimi: Not available (GLM only)

---

## Request

### Basic Request

```json
{
  "model": "embedding-3",
  "input": "The quick brown fox jumps over the lazy dog"
}
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `model` | string | Yes | Embedding model (e.g., "embedding-3") |
| `input` | string or array | Yes | Text to embed (string or array of strings) |
| `encoding_format` | string | No | Format for embeddings ("float", "base64") |

---

## Response

```json
{
  "object": "list",
  "data": [
    {
      "object": "embedding",
      "index": 0,
      "embedding": [0.123, -0.456, 0.789, ...]
    }
  ],
  "model": "embedding-3",
  "usage": {
    "prompt_tokens": 10,
    "total_tokens": 10
  }
}
```

---

## Examples

### Python (OpenAI SDK)

```python
from openai import OpenAI

client = OpenAI(
    api_key="your_glm_api_key",
    base_url="https://api.z.ai/v1"
)

response = client.embeddings.create(
    model="embedding-3",
    input="The quick brown fox jumps over the lazy dog"
)

embedding = response.data[0].embedding
print(f"Embedding dimension: {len(embedding)}")
```

### Batch Embeddings

```python
response = client.embeddings.create(
    model="embedding-3",
    input=[
        "First text to embed",
        "Second text to embed",
        "Third text to embed"
    ]
)

for i, data in enumerate(response.data):
    print(f"Embedding {i}: {len(data.embedding)} dimensions")
```

---

## Use Cases

### Semantic Search
- Index documents with embeddings
- Search by semantic similarity
- Rank results by cosine similarity

### Clustering
- Group similar texts together
- Identify topics and themes
- Detect duplicates

### Similarity Comparison
- Compare text similarity
- Find related content
- Recommend similar items

---

## Provider Support

| Provider | Embeddings Support |
|----------|-------------------|
| GLM | ✅ embedding-3 model |
| Kimi | ❌ Not available |

---

## Related Documentation

- [../05-api-endpoints-reference.md](../05-api-endpoints-reference.md) - API endpoints overview
- [authentication.md](authentication.md) - Authentication details
- [../providers/glm.md](../providers/glm.md) - GLM provider details

