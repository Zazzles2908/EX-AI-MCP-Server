# Phase 6 – Gap Analysis and Completion Tasks (2025-09-28)

## Summary
GLM streaming is operational. Kimi streaming remains unimplemented/unexposed despite example env docs. Prior checklist incorrectly marked Kimi streaming complete. Below is the concrete plan to complete Phase 6.

## Acceptance criteria (from IMPLEMENTATION_ROADMAP.md)
- GLM streaming end‑to‑end supported.
- Kimi streaming: env‑gated (KIMI_STREAM_ENABLED) with chunk aggregation similar to GLM.
- Kimi context caching: consistently pass _session_id/_call_key/_tool_name to capture/reuse cache tokens.
- Checkpoint: Streaming smoke tests pass for GLM and (when enabled) for Kimi; cache tokens reduce latency.

## Current gaps
1) Provider implementation
   - src/providers/kimi.py lacks an env‑gated streaming codepath (text/event-stream) and chunk aggregation.
   - No metadata.streamed=true flag set for Kimi results.
2) Tool exposure/registry
   - No `kimi_chat_with_tools` or dedicated `stream_demo` path for Kimi in tools/registry; ws_probe shows Unknown tool.
3) Tests & diagnostics
   - No Kimi streaming smoke analogous to GLM SSE path; ws_probe has a branch but fails due to missing tool support.
4) Context caching validation
   - Lacks explicit tests ensuring session_id/call_key/token reuse across Kimi streaming calls.

## Completion tasks
1) Implement Kimi streaming (provider)
   - Add env gate: KIMI_STREAM_ENABLED; default False.
   - Implement streaming via Moonshot text/event-stream; aggregate deltas into final content.
   - Return ModelResponse with metadata.streamed=true; include chunk count and timings.
   - Respect timeouts (e.g., KIMI_DEFAULT_READ_TIMEOUT_SECS if present) and backoff on transient errors.
2) Expose Kimi streaming tool
   - Register `kimi_chat_with_tools` (or similar) in tools/registry with a `stream` boolean arg; route to Kimi provider.
   - Mirror GLM stream_demo behavior; save JSON/JSONL traces to docs/System_layout/_raw.
3) Wire flags end‑to‑end
   - tools/chat should propagate stream=True into provider payloads when KIMI_STREAM_ENABLED=true.
   - Ensure boundary/request handler can request stream for Kimi as it does for GLM.
4) Tests & validation
   - Extend scripts/diagnostics/ws_probe.py to retry Kimi streaming once tool is exposed; assert streamed=true metadata.
   - Add unit tests for Kimi streaming aggregation and error handling.
   - Update tools/diagnostics/ws_daemon_smoke.py to include a Kimi streaming first‑chunk preview.
5) Context caching consistency
   - Ensure _session_id/_call_key/_tool_name are passed for Kimi streaming; capture returned cache token.
   - Add a follow‑up call reusing token and assert reduced latency or cache hit indicator.

## Evidence (current run)
- GLM streaming OK: docs/System_layout/_raw/ws_probe_glm_stream_paragraph_bullets_20250928T094608Z.json(.jsonl)
- Kimi streaming missing: `Unknown tool: kimi_chat_with_tools` → docs/System_layout/_raw/ws_probe_kimi_stream_bullets_20250928T094558Z.jsonl

## Risks/considerations
- Moonshot streaming framing differences vs GLM SSE; validate end markers and error semantics.
- Backwards compatibility: keep non‑stream path as default when env disabled.

## Done when
- ws_probe shows Kimi streaming success with streamed=true metadata and saved traces.
- Roundtrip + smoke scripts include Kimi streaming examples.
- Checklist updated: mark Kimi streaming complete only after validations pass.

