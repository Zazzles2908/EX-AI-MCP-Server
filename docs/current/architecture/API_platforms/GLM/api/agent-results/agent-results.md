# GLM (Z.ai) API – Agent Results Retrieval

## Authentication
- HTTP Authorization: `Bearer ${ZAI_API_KEY}`
- Base URL: `https://api.z.ai/api/v1`

## Endpoint
- POST `/agents/async-result`

## Request (example)
```json
{
  "task_id": "task_12345"
}
```

## Response (example)
```json
{
  "status": "succeeded",
  "result": {"text": "..."}
}
```

## Notes
- Use after initiating an async agent operation.

