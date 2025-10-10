# Monitoring Integration Plan (EX-AI MCP Server)

Purpose: Describe how and when the monitoring/ modules will be connected to the GLM‑first MCP WebSocket daemon, and what contracts/flags they will use.

## Current status
- MCP WebSocket daemon is the primary runtime entrypoint (scripts/ws/run_ws_daemon.py)
- monitoring/ modules are not yet wired into the daemon; they are kept for future integration
- Observability today: JSONL metrics/logs written by server utilities (utils/metrics.py, utils/instrumentation.py)

## Monitoring modules (inventory)
- autoscale.py: hooks to scale workers based on queue depth/latency
- file_sink.py: basic sink for logs/metrics to files
- health_monitor.py / health_monitor_factory.py: periodic health checks (provider reachability, tool registry sanity)
- predictive.py: placeholders for simple predictive rules on latency/error rates
- slo.py: SLO helpers (latency/error budget tracking)
- telemetry.py: façade for emitting structured telemetry events
- worker_pool.py: pool management for background jobs

## Planned integration (phased)
1) Phase A (low‑risk wiring)
   - Emit telemetry via telemetry.py from daemon lifecycle
   - Replace direct JSONL writes with telemetry façade where possible (preserve file outputs)
   - Health monitor: run lightweight provider ping (GLM/Kimi) every N minutes; surface into logs + optional MCP health tool
2) Phase B (operational controls)
   - Introduce autoscale hooks to adjust worker pool based on queue depth/latency thresholds
   - Add SLO computation loop (p95 latency, error rate); log breaches and suggest config tweaks
3) Phase C (predictive & alerts)
   - Enable predictive rules, alert on anomaly (spike in failures/latency)
   - Optional: integrate with external sinks (OpenTelemetry/ELK) behind a sink interface

## Interfaces & contracts
- Emission: telemetry.emit(event_name, payload, level) → writes to JSONL + optional extra sinks
- Health: health_monitor.run(checks=["glm_ping","kimi_ping","registry"]) → returns summary; periodically scheduled
- Autoscale: autoscale.evaluate(queue_depth, inflight, latency_stats) → returns desired pool size; daemon applies if allowed

## Flags & configuration (proposed)
- MONITORING_ENABLED=true|false (default false)
- HEALTH_PROBE_INTERVAL_SEC=300
- TELEMETRY_FILE=logs/ws_daemon.metrics.jsonl (existing)
- SLO_TARGET_P95_MS=2500
- AUTOSCALE_MIN_WORKERS=2
- AUTOSCALE_MAX_WORKERS=8

## Acceptance criteria
- No change to default behavior unless MONITORING_ENABLED=true
- Daemon starts and runs with or without monitoring modules present
- Logs include clear start/stop of monitoring loops and health outcomes

## Risks & mitigations
- Risk: overhead from probes → Mitigate by conservative intervals and opt‑in flag
- Risk: too many logs → Level‑gated telemetry, file rotation
- Risk: coupling to providers → Use provider adapters’ lightweight ping endpoints

## Next steps
- Add MONITORING_ENABLED flag handling in ws daemon main()
- Wire telemetry façade into daemon events (start, connect, list_tools, call_tool begin/end)
- Implement health_monitor loop guarded by flag

