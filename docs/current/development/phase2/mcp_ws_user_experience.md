# Direct EXAI-WS MCP Integration — User Experience Notes (Phase 1/2)

This note captures observations when invoking tools directly over the EXAI WebSocket MCP interface, compared to stdio/terminal scripts.

## Summary

- WS interface provides real-time feedback and structured responses suitable for UI integration
- Continuation offers are present in GLM chat streaming responses in WS runs
- Kimi streaming via SSE is well-supported; partials are flagged via metadata.streamed in raw traces
- Tool discovery over WS exposes a slightly smaller set than stdio sweep (diagnostic tools are hidden)

## Key Scenarios

1) Tool discovery via WS
- list_tools returned ~23 tools; names/inputs match stdio sweep core set
- Diagnostic-only tools present in stdio are intentionally hidden on WS

2) GLM web search via WS
- Results contain url/title/snippet; latency acceptable; output size small and UI-friendly
- Matches structure from stdio tests; minor diff in metadata wrapper

3) Kimi streaming and file operations via WS
- SSE chunks arrive steadily; final aggregation captured
- Raw JSONL traces include per-chunk events, enabling UI progress bars
- File upload/extract is not typically streamed; outputs arrive as a single payload

4) Chat with continuation_id via WS
- GLM chat stream includes continuation_offer; clients should adopt offered id
- Manual reuse of invented ids is rejected (thread not found), consistent with stdio
- Follow-up using offered id should be validated after auto-mode resolution fix (see Phase 1 findings)

## UX Differences vs Terminal/Stdio

- WS:
  - Designed for UI: events and payloads are composable, with progress-friendly structure
  - Streaming traces easier to display progressively
  - Tool set curated for product experience
- Stdio:
  - Better for bulk validation and schema dumps
  - Easier offline artifact capture for audits
  - Shows internal/diagnostic tools not meant for UI

## Issues/Improvements

- Auto-mode model resolution regression on follow-up chat using continuation_id (tracked in Phase 1 findings)
- Consider harmonizing absolute path guidance across chat and Kimi file tools; document policy prominently
- Consider standard metadata key for streaming state and response completion status across providers

## References

- WS probe raw artifacts: docs/System_layout/_raw/ws_probe_*.json (+ .jsonl)
- Stdio evidence: docs/augmentcode_phase2/raw/mcp_chat_context_*.json

