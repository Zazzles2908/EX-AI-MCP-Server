# Tool Function Registry – Kimi Integration

## Purpose
Describe how Kimi-specific tools are registered, gated, and invoked via the Tool Registry.

## Current Implementation
- server.py registers Kimi tools when Kimi provider is available (upload/extract, chat).
- src/providers/kimi.py wraps OpenAI-compatible client for chat + files.

## Integration Points
- Workflows pass _session_id/_call_key/_tool_name to enable context cache reuse.

## Status
- 🔧 Requires Adjustment: streaming path disabled by default; add env-gated toggle.

## Next Steps
1) Expose Kimi streaming flag in registry; propagate to provider.
2) Add registry status tool showing Kimi cache token reuse stats.

