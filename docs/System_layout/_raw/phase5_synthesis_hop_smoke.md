# Phase 5: Synthesis Hop (Optional) – Validation Artifact

Evidence that the synthesis hop metadata and logs are emitted when enabled.

- Env toggles
  - SYNTHESIS_ENABLED=true
  - SYNTHESIS_MODEL (optional; default glm-4.5-flash)
- Tests
  - tests/phase5/test_synthesis_hop.py: PASS
    - Asserts:
      - route_plan JSONL written for selection
      - A `synthesis_hop` JSONL event is present in ROUTEPLAN_LOG_DIR
- Implementation
  - src/router/synthesis.py: synthesize_if_enabled() returns metadata and logs synthesis_hop JSONL
  - src/router/service.py: invokes synthesis function and attaches result to decision.meta
  - utils/observability.py: append_synthesis_hop_jsonl()

Conclusion: Optional synthesis hop path is wired with observability; provider call is intentionally stubbed for offline unit testing.

