# Session Implementation Updates (2025-09-28)

This file summarizes what we completed and validated, mapping to the checklist items, with concrete files/scripts touched.

## Completed and validated

- Phase 1 – MCP Boundary & Request Handling
  - RoutePlan plumbing at boundary: implemented and emitting reasons/telemetry
  - Continuation and context threading: preserved across workflows (continuation_id)
  - Tool map normalization: discoverable tools with allow/deny filtering
  - Evidence: ws_probe full validations; server registration; telemetry notes
  - Files:
    - server.py (tool registration, boundary plumbing)
    - src/providers/registry.py (diagnostics, normalization)
    - src/server/providers/provider_config.py (guarded imports)

- Phase 3 – Manager-First Routing
  - choose_model_with_hint() and capability pruning: GLM-first routing with reason codes
  - Fallback coherency: route_plan.history appended with reasons
  - Files:
    - server.py (routing integration)

- GLM Web Search tool
  - Endpoint: https://api.z.ai/api/paas/v4/web_search
  - Headers: Authorization, Content-Type, Accept, Accept-Language (default en-US,en)
  - Payload: search_query, count (1..50 clamp), search_engine (default search-prime), search_recency_filter, request_id/user_id optional
  - Files:
    - tools/providers/glm/glm_web_search.py (implementation + compliance fixes)

- Kimi Intent Classification tool
  - Strict JSON hints for routing; validated via ws_probe
  - Files:
    - tools/providers/kimi/kimi_intent.py

- Diagnostics probe enhancements
  - Full output capture; multiple test cases; validators; error pattern scan; artifact saving
  - Files:
    - scripts/diagnostics/ws_probe.py
  - Artifacts:
    - docs/System_layout/_raw/ws_probe_glm_web_search_*_*.json
    - docs/System_layout/_raw/ws_probe_kimi_intent_analysis_*_*.json

## In progress / Next priority

- Phase 6 – Streaming & Long-Context
  - GLM streaming (env-gated) – implement SSE/SDK aggregation, extend ws_probe streaming tests, save JSONL traces
  - Kimi text/event-stream (env-gated) – implement event parsing, extend probe tests
  - Note: requires permission to add zai-sdk (recommended) or implement raw SSE; will request before installing

## Notes
- Phase 2 streaming-related AC remains pending; web_search portion is implemented and validated.
- Phase 4 router-hints wiring is gated/optional; classification tool is implemented and validated; full AC not claimed yet.

