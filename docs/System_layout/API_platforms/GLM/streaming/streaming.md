# GLM – Streaming (SSE/SDK iterator)

## Purpose
Provide end‑to‑end token streaming for interactive workflows and real‑time UX.

## Current Implementation (code paths)
- src/providers/glm.py:
  - SDK path: stream=True uses SDK iterator; aggregates delta/message content.
  - HTTP path: stream=True uses HttpClient.stream_sse("/chat/completions"); handles [DONE] and delta/message shapes.
- tools/streaming/*: streaming demos and smoke tests (present in repo) for validation.

## Parameters
- GLM_API_URL (default https://api.z.ai/api/paas/v4)

## Dependencies
- zhipuai SDK or SSE‑capable HTTP client (utils/http_client.py)

## Integration Points
- Boundary/tool should propagate stream=True when requested; provider returns ModelResponse with metadata.streamed=true.

## Status Assessment
- ✅ Existing & Complete: Provider streaming paths implemented and battle‑tested.

## Implementation Notes
- Ensure caller aggregates content consistently; consider exposing chunk callback for interactive tools.

## Next Steps
1) Add unit/integration tests that request stream=True via tools and assert streamed metadata.

