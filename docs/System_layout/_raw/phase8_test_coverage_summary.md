# Phase 8: Test & Verification — Coverage Summary

Router Unit Tests
- tests/phase8/test_router_routing.py: PASS
  - Explicit available -> chooses requested, reason=explicit
  - Explicit unavailable -> auto fallback to fast default
  - Auto: prefers long when only long available; otherwise first available

Provider Tests (Offline-Friendly)
- tests/phase8/test_provider_glm_websearch.py: PASS
  - GLMCapabilities.get_websearch_tool_schema returns tools=[{"type":"web_search"}] when use_websearch=True
- tests/phase8/test_provider_kimi_tools_schema.py: PASS
  - KimiCapabilities schema returns function or builtin_function depending on KIMI_WEBSEARCH_SCHEMA env
  - Complements earlier Phase 2 Kimi reliability test for chat tool schema and normalization

Workflow Tests
- tests/phase8/test_workflows_end_to_end.py: PASS
  - Uses ChatTool across two turns with the same continuation_id
  - Verifies history store has >=2 user and >=2 assistant turns
  - Assembled context block includes content from prior turns

Notes
- Provider tests avoid real network; they validate tooling/schema integration and build upon earlier passing tests for provider features
- For live provider E2E (streaming/upload/cache), run EXAI MCP smoke flows in a controlled environment as needed

