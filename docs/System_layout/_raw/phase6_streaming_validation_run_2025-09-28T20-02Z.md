# Phase 6 – Streaming Validation Run (2025-09-28T20:02Z)

## Summary
- Environment confirmed and aligned:
  - GLM_STREAM_ENABLED=true
  - KIMI_STREAM_ENABLED=true
- Server restarted with exact command:
  - powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\ws_start.ps1 -Restart
- Registered missing tool in registry:
  - kimi_chat_with_tools → tools.providers.kimi.kimi_tools_chat.KimiChatWithToolsTool (TOOL_MAP)
  - Visibility set to advanced in TOOL_VISIBILITY
- WS daemon started and reachable at ws://127.0.0.1:8765

## Evidence – Server Restart
- Logs (excerpt):
  - Registering provider-specific tools: ['glm_upload_file', 'glm_web_search', 'kimi_chat_with_tools', 'kimi_intent_analysis', 'kimi_multi_file_chat', 'kimi_upload_and_extract']
  - Starting WS daemon on ws://127.0.0.1:8765

## Tool Registry – Presence Check
- ws_probe reports tools (23), includes:
  - 'kimi_chat_with_tools' present ✓

## GLM Streaming Validation
- Script: scripts/diagnostics/ws_probe.py (glm_stream)
- Artifacts:
  - docs/System_layout/_raw/ws_probe_glm_stream_paragraph_bullets_20250928T100201Z.json
  - docs/System_layout/_raw/ws_probe_glm_stream_paragraph_bullets_20250928T100201Z.jsonl
- Observation:
  - Chat tool streamed via GLM when GLM_STREAM_ENABLED=true. JSONL trace captured. Content rendered progressively (probe prints final aggregation).

## Kimi Streaming Validation
- Script: scripts/diagnostics/ws_probe.py (kimi_stream via kimi_chat_with_tools)
- Artifacts:
  - docs/System_layout/_raw/ws_probe_kimi_stream_bullets_20250928T100151Z.json
  - docs/System_layout/_raw/ws_probe_kimi_stream_bullets_20250928T100151Z.jsonl (trace: provider chunk events)
- Result excerpt (normalized):
  - provider=KIMI, model=kimi-k2-0711-preview, stream=True
  - content begins with: "- **Instant feedback**: Users see partial results immediately..."
  - raw.items contains first ~10 ChatCompletionChunk entries (text/event-stream)
- Observation:
  - Kimi streaming path is now fully operational via env gate (KIMI_STREAM_ENABLED=true) and the new tool exposure.

## Additional Smoke
- tools/diagnostics/ws_daemon_smoke.py OK (tools count: 23; basic version/listmodels happy path)
- scripts/ws/ws_chat_roundtrip.py OK for glm-4.5-flash and kimi-k2-0711-preview (non-streaming roundtrip sanity)

## Acceptance Criteria Cross-check
- Phase 6 – Streaming & Long-Context
  - [x] Kimi streaming (env-gated) — Stream demo runs end-to-end via kimi_chat_with_tools
  - [x] GLM streaming (env-gated) — Chat tool streams when GLM_STREAM_ENABLED=true; traces saved
  - [ ] Context caching consistency — Kimi cache token capture validated for non-streaming path; streaming header token propagation added (best-effort). Defer full test to Phase 6.2 tests.

## Notes / Implementation Details
- Kimi streaming implemented via KimiChatWithToolsTool using provider client streaming (text/event-stream), chunk aggregation, idempotency+context cache headers (best-effort), and normalized output with raw.items sample for diagnostics.
- Registry updated to expose the tool; generic chat path for Kimi remains non-streaming by default to preserve tool-call loop stability for web-enabled prompts.
- For websearch-enabled prompts, streaming is auto-disabled to preserve tool_call handling.

## Next (Optional) Hardening
- Add unit tests around:
  - Streaming on/off toggles for Kimi and GLM
  - Kimi cache token capture (non-stream vs stream headers) and session-aware reuse
- Consider centralizing streaming adapters (streaming/streaming_adapter.py) and moving the event loop out of the tool into provider or shared util for maximum reuse.

