# Kimi – Chat Completions Integration

## Purpose
Integrate Kimi chat with idempotency, context cache, and OpenAI‑compatible interface.

## Current Implementation (code paths)
- src/providers/kimi.py: chat_completions_create() wraps client call, sets Idempotency‑Key + Msh‑Trace‑Mode, attaches/records cache tokens, normalizes usage/content.
- generate_content delegates to OpenAI‑compatible base with Kimi base_url.

## Parameters
- KIMI_API_URL, temperature, stream (default False in provider), extra_headers Idempotency‑Key, Msh‑Trace‑Mode, Msh‑Context‑Cache‑Token

## Dependencies
- Moonshot client

## Integration Points
- Workflows should pass _session_id/_call_key/_tool_name to enable cache reuse.

## Status Assessment
- ✅ Existing & Complete (core integration)
- 🔧 Requires Adjustment (streaming default off)

## Implementation Notes
- Normalizes usage to plain dict for JSON serialization.

## Next Steps
1) Allow env‑gated streaming for Kimi (KIMI_STREAM_ENABLED) and tests to validate.

