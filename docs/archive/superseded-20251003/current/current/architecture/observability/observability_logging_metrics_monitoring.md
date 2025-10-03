# Observability – Logging, Metrics, Monitoring

## Purpose
Provide actionable visibility into routing, tool execution, and provider calls for debugging, cost, and reliability.

## Current Implementation (code paths)
- Router logs: src/router/service.py (preflight, route_decision JSONL).
- Boundary/activity: src/server/handlers/request_handler.py (mcp_activity, boundary_model_resolution_attempt/resolved, WATCHDOG heartbeats, progress capture).
- Provider telemetry: src/providers/registry.py (record_telemetry, health/circuit breaker integration, token usage mirroring).

## Parameters
- ROUTER_LOG_LEVEL, ROUTER_DIAGNOSTICS_ENABLED, EX_MIRROR_ACTIVITY_TO_JSONL
- HEALTH_CHECKS_ENABLED, CIRCUIT_BREAKER_ENABLED, HEALTH_LOG_ONLY
- RETRY_ATTEMPTS, RETRY_BACKOFF_BASE, RETRY_BACKOFF_MAX

## Dependencies
- utils.observability (record_error, record_token_usage) – referenced by registry
- utils.metrics, utils.health – used by provider wrapper

## Integration Points
- RoutePlan: should be mirrored into toolcalls.jsonl for each call (requested, chosen, provider, reasons, capabilities).

## Status Assessment
- 🔧 Requires Adjustment: Strong logging exists, but per‑call RoutePlan mirroring and unified route diagnostics across boundary/manager/provider are not yet consolidated.

## Implementation Notes
- Ensure all logs are JSON‑serializable and redact keys if configured.

## Next Steps
1) Emit a compact route_plan object in toolcalls.jsonl from request_handler.
2) Add unit tests asserting route_plan presence and key fields under varied scenarios.
3) Consider minimal Prometheus counters for provider success/failure and latency if desired.

