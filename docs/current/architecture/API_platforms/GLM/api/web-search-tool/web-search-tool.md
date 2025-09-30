# GLM (Z.ai) API – Web Search Tool

## Authentication
- HTTP Authorization: `Bearer ${ZAI_API_KEY}`
- Base URL: `https://api.z.ai/api/paas/v4`

## Endpoint (tool schema)
- When using chat completions with browsing enabled, include `tools: [{type: "web_search", web_search: {}}]` and `tool_choice: "auto"`.
- Direct HTTP endpoint commonly used by custom tools:
  - POST `/web_search` (payload varies by engine)

## Request (example)
```json
{
  "search_query": "latest LangChain alternatives",
  "count": 5
}
```

## Response (example)
```json
{
  "results": [{"title": "...", "url": "...", "snippet": "..."}]
}
```

## Notes
- Prefer provider-native `tools` injection over custom HTTP where possible.

