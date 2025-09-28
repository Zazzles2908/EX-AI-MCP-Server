# EX-AI-MCP-Server – Phase Implementation Issues Log (2025-09-28)

This living log records unexpected issues, anomalies, and deviations discovered during each roadmap phase. Update immediately when issues are found, not only at phase completion.

---

## Phase 1 – MCP Boundary & Request Handling
- Expected vs Actual Behavior
  - Expected: Clean boundary wiring with route-plan emission, continuation_id threading, allow/deny enforcement.
  - Actual: Import error surfaced early from provider_config (custom provider import) interrupting provider setup; boundary tasks completed after fix.
- Root Cause Analysis
  - Unconditional import of `src.providers.custom` in provider_config; legacy module removed during cleanup.
- Resolution Applied
  - Deferred/guarded import for CustomProvider only when `CUSTOM_API_URL` is set; soft-skip on ImportError.
- Impact Assessment
  - Blocked provider setup until fixed; after fix, GLM and Kimi worked.
- Lessons Learned
  - Always guard optional provider imports; prefer lazy, env‑gated imports to avoid brittle optional deps.

---

## Phase 2 – Provider Registry Diagnostics
- Expected vs Actual Behavior
  - Expected: Diagnostics reflect provider registration/initialization across contexts.
  - Actual: Ad-hoc Python diagnostics showed `registered=false`/`initialized=false` while MCP daemon worked.
- Root Cause Analysis
  - Registry singleton is process‑local; ad‑hoc processes don’t run `configure_providers()` and thus see an empty registry.
- Resolution Applied
  - Implemented `ProviderDiagnostics` in `src/providers/registry.py`.
  - Added daemon-first diagnostics: read `logs/provider_registry_snapshot.json` if present.
  - Added daemon snapshot writer in `configure_providers()` to capture registered/initialized providers and available models.
- Impact Assessment
  - Improved observability; eliminated false negatives when snapshot exists. No functional impact on providers.
- Lessons Learned
  - Cross‑process state requires explicit handoff (snapshot/IPC). Avoid assuming singletons reflect daemon truth.

- Unexpected Item: Missing snapshot file after restart
  - Hypothesis: Working directory variance or early log path not created in the actual daemon context.
  - Mitigation: Snapshot write is guarded; plan a secondary write on first tool-call if needed. Monitor on subsequent restarts.

---

## Phase 3 – Manager-first routing + GLM native web_search integration
- Expected vs Actual Behavior
  - Expected: Manager-first routing prefers `glm-4.5-flash` for simple tools; GLM native web_search exposed as first-class MCP tool and via chat capabilities injection when `use_websearch` is enabled.
  - Actual: (pending validation) Implemented new tool `glm_web_search` and registered it; Chat already supports capabilities injection via `GLMCapabilities.get_websearch_tool_schema()`.
- Root Cause Analysis
  - N/A yet. Implementation work ongoing.
- Resolution Applied
  - Added `tools/providers/glm/glm_web_search.py` calling `POST {GLM_API_URL}/web_search` with Bearer auth.
  - Re-enabled registration in `server.register_provider_specific_tools()` and added to `tools/registry.TOOL_MAP`.
- Impact Assessment
  - Enables direct GLM web browsing via MCP, and chat-driven native browsing via capabilities; should not affect streaming paths.
- Lessons Learned
  - Prefer provider-native tools via capabilities for reliability; keep direct endpoint tool for explicit operations and diagnostics.

---

## Add new issues below this line as they occur

- [ ] (placeholder) Document any HTTP 4xx/5xx from `glm_web_search` and rate-limit behavior; include request/response snippets and environment toggles involved.

- Unexpected Item: PowerShell here-doc failure during ad-hoc MCP probe
  - Root Cause: PowerShell does not support bash-style `python - <<'PY'` heredoc syntax.
  - Resolution: Use `scripts/diagnostics/ws_probe.py` for WS interactions instead of inline heredocs; or create a temp .py file.
  - Impact: None on server; affected only transient validation approach.


- Unexpected Item: Kimi intent tool default model not explicitly configured in some environments
  - Root Cause: KIMI_INTENT_MODEL not set; falls back to kimi-k2-0905-preview which is acceptable but may differ from cost/perf expectations.
  - Resolution: Provide env var KIMI_INTENT_MODEL to override; keep safe defaults.
  - Impact: None; classification returned structured JSON correctly.
