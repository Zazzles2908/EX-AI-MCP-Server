# Kimi Context Caching Metadata (Phase 2)

Summary
- Kimi provider attaches cache metadata to responses:
  - `metadata.cache.attached`: whether a cache token was sent via `Msh-Context-Cache-Token`
  - `metadata.cache.saved`: whether the provider returned `Msh-Context-Cache-Token-Saved`
- Idempotency and trace headers are included when available.

Implementation notes
- Provider: `src/providers/kimi.py` now returns `metadata.cache` with `attached` and `saved` flags.
- Diagnostic tool: `tools/providers/kimi/kimi_capture_headers.py` performs a real non-stream chat and returns normalized dict with metadata.
- Script: `scripts/diagnostics/kimi/capture_headers_run.py` writes a sample response JSON.

Evidence
- Artifact: `docs/System_layout/_raw/phase2_kimi_capture_headers_response.json` shows metadata presence.
- MCP proof: `docs/System_layout/_raw/phase2_kimi_mcp_chat_response.json` shows real Kimi output (content provenance).

