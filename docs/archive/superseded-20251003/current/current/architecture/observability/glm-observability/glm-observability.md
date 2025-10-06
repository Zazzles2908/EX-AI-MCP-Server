# Observability – GLM Path

## Purpose
Trace GLM provider calls, routing decisions, and token/latency metrics.

## Current Implementation
- JSONL logs: router decisions, boundary model resolution, toolcalls.
- Provider telemetry: token usage and elapsed time.

## Integration Points
- RoutePlan should be mirrored in logs; stream=true should mark metadata.streamed.

## Status
- 🔧 Requires Adjustment: ensure RoutePlan present on every call and mirrored to JSONL.

## Next Steps
1) Add RoutePlan logging at boundary and provider layers.
2) Add counters for web_search usage and streaming.

