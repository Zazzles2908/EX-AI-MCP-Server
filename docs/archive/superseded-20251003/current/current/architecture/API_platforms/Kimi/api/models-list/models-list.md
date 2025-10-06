# Kimi (Moonshot) API – Models List

## Authentication
- HTTP Authorization: `Bearer ${MOONSHOT_API_KEY}`
- Base URL: `https://api.moonshot.ai/v1`

## List Models
- GET `/models`

## Response (abridged)
```json
{
  "data": [
    {"id": "kimi-k2-0711-preview", "object": "model"},
    {"id": "moonshot-v1-128k", "object": "model"}
  ]
}
```

