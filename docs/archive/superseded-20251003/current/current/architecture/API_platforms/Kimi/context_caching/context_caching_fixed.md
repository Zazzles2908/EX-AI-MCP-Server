# Kimi – Context Caching and Long-Context Optimization

## Purpose
Reduce cost/latency for long-context conversations using Kimi's context cache headers and large context windows.

## Current Implementation (code paths)
- src/providers/kimi.py: in-process LRU for cache tokens; chat_completions_create() attaches/records Msh-Context-Cache-Token{,-Saved} via with_raw_response; keying by session_id/tool/prefix_hash.
- Long-context models present (kimi-k2-turbo-preview 256k, moonshot-v1-128k).

## Parameters
- KIMI_CACHE_TOKEN_TTL_SECS, KIMI_CACHE_TOKEN_LRU_MAX

## Dependencies
- Moonshot client with raw response access

## Integration Points
- Tools should pass session_id/call_key/tool_name so provider wrapper can attach/extract tokens.

## Status Assessment
- Requires Adjustment: Mechanism exists; ensure workflows consistently pass session_id/call_key and reuse cache tokens across steps.

## Implementation Notes
- Prefix hash uses first few messages; safe and deterministic.

## Next Steps
1) Standardize passing session_id and call_key from boundary/workflows.
2) Add tests that verify token is reused and reduces latency.

