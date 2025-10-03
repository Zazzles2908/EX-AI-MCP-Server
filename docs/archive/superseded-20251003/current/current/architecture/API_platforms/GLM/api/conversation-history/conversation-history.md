# GLM (Z.ai) API – Conversation History

## Authentication
- HTTP Authorization: `Bearer ${ZAI_API_KEY}`
- Base URL: `https://api.z.ai/api/v1`

## Endpoint
- POST `/agents/conversation`

## Request (example)
```json
{
  "agent_id": "agent_123",
  "conversation_id": "conv_abc",
  "limit": 50
}
```

## Response (example)
```json
{
  "conversation": [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
}
```

## Notes
- The Agents family of endpoints lives under `/api/v1`.

