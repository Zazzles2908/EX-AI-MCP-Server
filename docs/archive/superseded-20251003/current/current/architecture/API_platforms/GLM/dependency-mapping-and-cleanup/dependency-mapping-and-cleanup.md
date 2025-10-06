# Dependency Mapping and Cleanup Candidates (GLM/Z.ai)

## Inter-script dependencies (concise)
- server.py → src/server/handlers/{mcp_handlers, request_handler}
- server.py → src/server/providers/provider_config
- server.py → tools/providers/glm/* (dynamic registration)
- request_handler → src/server/registry_bridge → ToolMap
- request_handler → src/providers/registry → GLMModelProvider
- GLM tools → src/providers/glm.py (SDK-first; HTTP fallback)
- WS shim → server.py handlers (delegation only)

## Candidates for removal or consolidation
- providers.py (repo root)
  - Why: alternate provider abstraction; overlaps with src/providers/*.
  - Risk: low if no imports from runtime path; verify with grep/tests.
- src/providers/zhipu/ (package is empty besides __init__.py)
  - Why: legacy placeholder; superseded by src/providers/glm.py.
  - Risk: none once imports confirmed absent.
- tools/providers/glm/glm_files_cleanup.py
  - Why: dev-only account hygiene CLI; not part of production flow.
  - Action: keep under scripts/ or docs/recipes; do not register as tool.
- src/server/fallback_orchestrator.py
  - Why: auxiliary helper; not on hot path; keep if you want cross-provider fallback; otherwise remove when unused.

## Staging strategy (updated)
- Phase 1 (no behavior change; WS is P0-critical in this deployment)
  - Keep WS daemon path fully intact; do not alter src/daemon/*
  - Add DEPRECATED banners to providers.py and src/providers/zhipu/__init__.py
  - Keep files, remove any lingering imports
- Phase 2 (delete/move)
  - Delete providers.py; delete src/providers/zhipu/
  - Move glm_files_cleanup.py to scripts/maintenance/
- Phase 3 (unification)
  - Standardize HTTP on utils/http_client.py (httpx)
  - (Optional) adapt glm_agent_* into provider-mediated calls for uniform auth/telemetry

## Validation checklist per phase
- Stdio: handshake + list_tools + chat (glm-4.5-flash)
- GLM tools: upload_file, multi_file_chat, web_search, agents
- WS (if enabled): list_tools + chat


