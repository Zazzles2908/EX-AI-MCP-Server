# Phase 3 – RoutePlan JSONL enrichment (evidence)

- Function: utils/observability.append_routeplan_jsonl
- Integration: src/router/service.py calls append_routeplan_jsonl on route decisions (explicit/auto/no_models_available)
- Test: tests/phase3/test_routeplan_jsonl.py (passing)

Output example:
- Created JSONL under docs/System_layout/_raw/routeplan_test_out/<YYYY-MM-DD>.jsonl during test execution
- JSONL line contains fields: {event:"route_plan", ts:"...Z", requested, chosen, reason, provider, meta}

