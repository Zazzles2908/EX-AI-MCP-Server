# Kimi  Streaming Capabilities

## Purpose
Support token streaming for Kimi where available to enable real-time experiences.

## Current Implementation (code paths)
- src/providers/kimi.py: generate_content() defaults stream=False; streaming path not enabled by default.

## Parameters
- KIMI_STREAM_ENABLED (proposed env), KIMI_DEFAULT_READ_TIMEOUT_SECS

## Dependencies
- Moonshot client streaming support

## Integration Points
- Tools should propagate stream=True when env allows; provider should aggregate chunks similarly to GLM SSE.

## Status Assessment
- Missing/Incomplete: No end-to-end streaming enabled for Kimi by default.

## Implementation Notes
- Kimi provider already exposes long timeouts suitable for streaming scenarios.

## Next Steps
1) Add env-gated streaming in Kimi provider; mirror GLM chunk aggregation pattern.
2) Add streaming smoke tests for Kimi path.

