# Kimi (Moonshot) API – Chat Completions

## Authentication
- HTTP Authorization: `Bearer ${MOONSHOT_API_KEY}`
- Base URL: `https://api.moonshot.ai/v1`

## Endpoint
- POST `/chat/completions`

## Request (JSON)
- model: string (e.g., `kimi-k2-0711-preview`)
- messages: [{role, content}]
- stream: boolean (optional)
- temperature, max_tokens, top_p (optional)

## Response (abridged)
```json
{
  "id": "...",
  "model": "kimi-k2-0711-preview",
  "choices": [{"message": {"role": "assistant", "content": "..."}}],
  "usage": {"prompt_tokens": 10, "completion_tokens": 5}
}
```

