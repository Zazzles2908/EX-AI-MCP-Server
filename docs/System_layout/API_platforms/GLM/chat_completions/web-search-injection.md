# Web Search Tool Injection for GLM Chat Completions (Phase 2)

Summary
- GLM chat payload now supports explicit `tools` and optional `tool_choice` injection.
- When `tools=[{"type":"web_search"}]` is provided, it propagates end-to-end to the provider.
- Provider responses surface `metadata.tools` and `metadata.tool_choice` (non-stream and stream paths).

Implementation notes
- Provider: `src/providers/glm.py` surfaces `metadata["tools"]` and `metadata["tool_choice"]` in ModelResponse.
- Preview tool (no network): `tools/providers/glm/glm_payload_preview.py` shows assembled payload.
- Tests: `tests/phase2/test_glm_tool_injection.py` validates payload injection path.

Evidence
- Artifact: `docs/System_layout/_raw/phase2_glm_payload_preview_artefact.json` shows payload with `tools=[{"type":"web_search"}]`.
- MCP: `docs/System_layout/_raw/phase2_glm_web_search_results.json` demonstrates provider web-search capability.

