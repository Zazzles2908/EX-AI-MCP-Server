# Phase 8 Validation Memo (EXAI-WS MCP)

Router Unit Tests
- tests/phase8/test_router_routing.py: PASS
  - Explicit available → chooses requested, reason=explicit
  - Explicit unavailable → auto fallback to fast default
  - Auto: prefers long when only long available; otherwise first available

Provider Tests
- tests/phase8/test_provider_glm_websearch.py: PASS
  - GLMCapabilities.get_websearch_tool_schema returns tools=[{"type":"web_search"}] when use_websearch=True
- tests/phase8/test_provider_kimi_tools_schema.py: PASS
  - KimiCapabilities schema returns function or builtin_function depending on KIMI_WEBSEARCH_SCHEMA env

Workflow Tests
- tests/phase8/test_workflows_end_to_end.py: PASS
  - ChatTool across two turns with same continuation_id; history reconstructed; context block includes prior turns

Risks / Next Steps (true provider E2E)
- Streaming/upload/cache require live provider calls; recommend controlled EXAI MCP smoke tests
- Add integration tests with provider response mocks for streaming/upload/cache behavior

