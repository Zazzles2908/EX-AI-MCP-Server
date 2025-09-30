# Phase 4: Routing Hints Wiring – Validation Artifact

Summary: Verified that classification-driven hints influence routing decisions.

- Method: RouterService.build_hint_from_request() produces a hint using classifier outputs
- Expectation: quick_chat -> GLM fast; long_context_analysis -> Kimi long
- Test: tests/phase4/test_routing_hints_bias.py: PASS
  - Asserts chosen == glm-4.5-flash for short prompt
  - Asserts chosen == kimi-k2-0711-preview for long prompt with multiple files
- Scripts: src/router/service.py (accept_agentic_hint, build_hint_from_request)
- Notes: Evidence complements existing route_plan JSONL logging for each decision

