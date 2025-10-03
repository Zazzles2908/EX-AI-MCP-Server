# GLM – Chat Completions Integration

## Purpose
Integrate GLM chat completions with system prompts, tools, streaming, and model aliasing.

## Current Implementation (code paths)
- src/providers/glm.py: generate_content → _build_payload (messages, system, temperature, max_tokens, tools, tool_choice, stream) → SDK/HTTP call → ModelResponse.

## Parameters
- GLM_API_URL, temperature, max_tokens, stream

## Dependencies
- zhipuai SDK or GLM HTTP API

## Integration Points
- Boundary resolves model and passes _model_context and use_websearch/stream to tools; tools construct provider calls.

## Status Assessment
- ✅ Existing & Complete

## Implementation Notes
- Token estimation heuristic included for CJK‑heavy inputs.

## Next Steps
- Ensure RoutePlan/metadata records actual model used, stream flag, and tools injected.

