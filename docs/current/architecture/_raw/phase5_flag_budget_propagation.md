# Phase 5: Flag and Budget Propagation – Validation Artifact

Summary of evidence for flag propagation (use_websearch, stream) and budget filtering.

- Tests
  - tests/phase5/test_flag_propagation_and_budget.py: PASS
    - Asserts:
      - Budget filter steers selection to cheaper model (glm-4.5-flash) given MODEL_COSTS_JSON and budget=0.03
      - RoutePlan JSONL includes meta.budget field
      - Chat tool toggles GLM_STREAM_ENABLED during prepare_prompt() when stream=True and restores on format_response()
- Implementation
  - tools/chat.py
    - Added ChatRequest.use_websearch and .stream
    - prepare_prompt(): temporarily sets GLM_STREAM_ENABLED per request.stream; restored in format_response()
  - src/router/service.py
    - _filter_by_budget() honors MODEL_COSTS_JSON and hint.budget
    - choose_model_with_hint(): includes meta.budget when provided
  - utils/observability.py
    - append_routeplan_jsonl() used to persist decisions and flags
- Files written during tests
  - docs/System_layout/_raw/routeplan_budget_test_out/*.jsonl (route plan events including budget)

Conclusion: Flag propagation and budget constraints are functional and observable.

