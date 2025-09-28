# Cleanup Plan (Initial Draft)

Scope
- Consolidate daemon/shim scripts and provider tool registration
- Remove dead/duplicate adapters; keep one canonical path per feature
- Preserve current file structure for now; changes staged behind wrappers

Findings (current)
- WS daemon entrypoints:
  - Canonical: scripts/ws/run_ws_daemon.py
  - Back-compat shim: scripts/run_ws_daemon.py (forwards to canonical)
  - WS Shim client (MCP stdio bridge): scripts/run_ws_shim.py
- Provider tool registration previously ran at import time, leading to missing tools in WS daemon. Fixed by runtime, idempotent registration invoked on list_tools and call_tool.

Proposed consolidation (phase 1 - no breaking changes)
1) Keep scripts/ws/run_ws_daemon.py as canonical. Keep scripts/run_ws_daemon.py as a thin forwarder (already done).
2) Document scripts/run_ws_shim.py as the only stdio entry client for IDEs/CLIs.
3) Centralize tool registration: server.register_provider_specific_tools() is the single mutator; WS daemon invokes it as needed.
4) Add lightweight thread lock around registration (optional) to guard concurrent list/call.

Proposed consolidation (phase 2 - small refactors, backward-compatible)
1) Create docs/ops/runbook_ws_daemon.md with env, ports, and restart instructions.
2) Move provider-specific diagnostics under scripts/diagnostics/providers/* and add small CLI helpers (e.g., create GLM test agent via zai-sdk).
3) Flatten legacy provider registry variants; keep src/providers/registry as the source of truth.

Deletion candidates (to stage after validation)
- Any duplicate daemon runners beyond the canonical + shim.
- Legacy tool discovery code once server.register_provider_specific_tools() covers all cases.

Artifacts to produce
- docs/ops/runbook_ws_daemon.md (how to run, restart, troubleshoot)
- docs/validation/provider_params.md (Kimi files, GLM agents/web_search payloads)
- docs/external_review/* live run transcripts (already capturing)

Next steps
- Decide on adding a lock to provider registration now (safe) or later.
- Add a small diagnostic to create a temporary GLM agent via zai-sdk for live agent tests.
- Continue capturing live MCP runs and update this plan with concrete deletions.

