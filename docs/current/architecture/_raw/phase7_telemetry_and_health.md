# Phase 7: Telemetry & Health  Validation Artifact

Telemetry JSONL + Aggregates
- Per-call telemetry emitted to TELEMETRY_LOG_DIR (default logs/telemetry/<YYYY-MM-DD>.jsonl)
- Aggregates written to logs/telemetry/aggregates/<YYYY-MM-DD>.json via utils.observability.rollup_aggregates()
- Test: tests/phase7/test_telemetry_jsonl_and_aggregates.py: PASS
  - Asserts an aggregate file exists and includes counts["GLM"]["glm-4.5-flash"]

Health/Circuit (Optional)
- Lightweight in-memory circuit with utils.health
  - Sync helpers: is_blocked(name), open_circuit(name), reset(name)
  - RouterService skips blocked models in choose_model_with_hint()
- Test: tests/phase7/test_health_circuit.py: PASS
  - Forces circuit open for glm-4.5-flash; service chooses kimi-k2-0711-preview

Notes
- Circuit expresses an always-open state in unit tests for determinism; in production integrate with provider error paths to mark failures.
- Telemetry events include provider, model, hint/budget/synthesis flags; extend with tokens/latency later.

