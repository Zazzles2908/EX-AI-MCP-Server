# Tool Function – Registry and Workflows

## Purpose
Document how MCP tools are registered, resolved, and executed (simple tools, workflows, streaming tools).

## Current Implementation (code paths)
- Registry bridge: src/server/registry_bridge.py builds active tool map.
- Tools: tools/registry.py (exposes tool classes); tools/simple/base.py; tools/workflows/* (analyze, debug, codereview, refactor, etc.).
- Boundary: request_handler acquires TOOL_MAP and dispatches; special path for kimi_multi_file_chat with safety‑net fallback to GLM.

## Parameters
- EX_AUTOCONTINUE_WORKFLOWS, EX_AUTOCONTINUE_ONLY_THINKDEEP, EX_AUTOCONTINUE_MAX_STEPS
- CLIENT_DEFAULTS_USE_WEBSEARCH, ENABLE_SMART_WEBSEARCH (thinkdeep)

## Dependencies
- Provider capabilities injection (tools/capabilities/provider_capabilities.py, src/providers/capabilities.py)

## Integration Points
- _model_context injected at boundary is consumed by tools for provider calls.
- For browsing: tools should request provider‑native web_search schema when use_websearch is set.

## Status Assessment
- ✅ Existing & Complete (registry and workflows): Active registry, dispatch works, workflow tools present.
- 🔧 Requires Adjustment (capability propagation): Ensure use_websearch and stream options flow from boundary → tool → provider.

## Implementation Notes
- Keep tool fallback logic minimal; prefer boundary routing + registry fallback.

## Next Steps
1) Add streaming/web_search flags to tool execution paths consistently.
2) Add tests for streaming smoke (GLM SSE) and websearch injection (GLM/Kimi paths).

