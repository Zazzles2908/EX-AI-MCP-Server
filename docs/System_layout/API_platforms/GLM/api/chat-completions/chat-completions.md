# GLM (Z.ai) API – Chat Completions

## Authentication
- HTTP Authorization: `Bearer ${ZAI_API_KEY}` (alias: `GLM_API_KEY`)
- Base URL: `https://api.z.ai/api/paas/v4`

## Endpoint
- POST `/chat/completions`

## Request (JSON)
- model: string (e.g., `glm-4.5-flash`)
- messages: [{role: system|user|assistant|tool, content: string|array}]
- stream: boolean (optional)
- tools: array (optional; include `{type: "web_search", web_search: {}}` when browsing)
- tool_choice: "auto" | {type: string} (optional)
- temperature, max_tokens, top_p (optional)

## Streaming
- SSE with `stream=true` returns chunked delta messages and a terminal `[DONE]` event.

## Response (abridged)
```json
{
  "id": "...",
  "model": "glm-4.5-flash",
  "choices": [{
    "message": {"role": "assistant", "content": "..."},
    "finish_reason": "stop"
  }],
  "usage": {"prompt_tokens": 123, "completion_tokens": 45, "total_tokens": 168}
}
```

## Notes
- For native web search, include `tools` and `tool_choice` as above; provider decides when to invoke browsing.

