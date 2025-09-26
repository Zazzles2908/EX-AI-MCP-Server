# EX-AI-MCP-Server — Legacy Reduction and Agentic Default Path Cleanup Plan

Owner: Augment Agent
Status: Draft (Phase A ready to execute)
Scope: Remove/retire redundant code paths and random top-level files; make RouterService + agentic stack the single source of truth for model/provider routing; keep safe rollbacks.

## Objectives (What “done” means)
- Single router of record: src/router/RouterService with RequestAnalyzer + GLMFlashManager.
- No routing logic in tools/simple/base.py or individual tools (only prompt utilities remain).
- No duplicate provider/tool wiring outside capabilities layer.
- Top-level (repo root) “random” or duplicated scripts removed or archived.
- Clean, minimal env flags; .env and .env.example aligned.
- Observability unified: RouterService JSON logs + thin boundary log in request_handler only.

## Principles
- Minimal, reversible changes per phase (env-gated where possible).
- Do not expand server.py; prefer boundary wiring and src/core modules.
- Prefer deletion over leaving dead code; when unsure, archive to docs/legacy/.
- Keep comprehensive audit trail in docs/augment_reports/augment_review_02/cleanup_log.md.

## Current-state summary (sources of duplication)
- Boundary routing: request_handler has legacy heuristics; RouterService not always consulted.
- tools/simple/base.py: contains pre-search injection, category routing, and parallel tool injection.
- capabilities: src/providers/capabilities.py is the intended place for provider-native tools.
- Top-level duplicate trees vs src/*: providers/, routing/, context/ exist at repo root while src/providers, src/router, src/core/context are the active code.
- Multiple server entrypoints/scripts: server.py, server_original.py, remote_server.py, scripts/minimal_server.py.
- Multiple READMEs and config variants: README-ORIGINAL.md vs README.md vs README-PUBLIC.md; many mcp-config.* files.

## Targets — Remove/Retain Matrix (initial)
- KEEP (authoritative)
  - src/router/service.py (RouterService) — single source of routing; DO NOT remove
  - src/core/agentic/__init__.py — exports for agentic stack; DO NOT remove
  - src/core/agentic/request_analyzer.py — Smart preprocessing; DO NOT remove
  - src/core/agentic/glm_flash_manager.py — Intelligent AI manager; DO NOT remove
  - src/providers/** (providers + capabilities)
  - src/server/** (MCP boundary)
- Remove or archive (legacy/duplicates)
  - tools/simple/base.py — remove routing and pre-search logic; keep only prompt utils; deprecate file if fully empty
  - request_handler._route_auto_model / resolve_auto_model — mark deprecated; reduce to minimal fallback when RouterService disabled
  - Top-level duplicate folders: providers/, routing/, context/ (confirm no unique code; otherwise move any stragglers into src/* and delete top-level)
  - server_original.py, remote_server.py (archive to docs/legacy/ if not used)
  - scripts/minimal_server.py (archive unless referenced by tests)
  - README-ORIGINAL.md (archive), keep README.md and README-PUBLIC.md
  - mcp-config.*: consolidate to one canonical config (mcp-config.augmentcode.json); move others to docs/legacy/configs/

## Phased plan

### Phase A (safe, behavior-preserving; enables agentic by default)
1) Boundary: Ensure RouterService runs at MCP boundary under env (AGENTIC_ROUTER_AT_BOUNDARY=true). Thin legacy routing to backstop only.
2) tools/simple/base.py: remove pre-search injection and category routing; delete parallel provider tool injection. Keep only small prompt utilities.
3) Capabilities: verify only src/providers/capabilities.py injects provider-native tools.
4) Observability: add RouterService JSON logs to validation markdown; keep request_handler one-line confirmation.
5) Docs: Create/maintain this plan; start cleanup_log.md; update .env.example to match .env.

### Phase B (align workflows + “think” paths)
1) Remove thinkdeep-specific overrides in request_handler; pass hints to RouterService instead.
2) Ensure analyze/codereview/debug/precommit/etc. don’t pick models; only pass hints (files present, long context, web intent) and call chat/analyze via router.
3) Remove tools/cost/model_selector.py (or reduce to constants consumed by RouterService).

### Phase C (top-level repository tidy)
1) Remove or archive top-level duplicate directories (providers/, routing/, context/). Migrate any unique files into src/** first.
2) Remove server_original.py, remote_server.py (archive to docs/legacy/ if needed by docs only).
3) Cull scripts/* duplicates (minimal_server.py, tmp_registry_probe.py) if not referenced by tests; keep ws_start/stop and diagnostics needed.
4) Consolidate configs: keep mcp-config.augmentcode.json; move others to docs/legacy/configs/ with a README mapping.

### Phase D (tests, docs, validation)
1) Extend/align tests so RouterService decisions are asserted for: file ops → Kimi, web browse → GLM, long context → Kimi, general chat → GLM.
2) Run focused tests (router/agentic) and full quick suite. Capture results to docs/augment_reports/augment_review_02/cleanup_log.md.
3) Update top-level README.md to reflect the simplified architecture and flags.

## Env flags and defaults
- AGENTIC_ROUTER_AT_BOUNDARY=true (default on; set false to revert to legacy backstop route)
- ENABLE_INTELLIGENT_ROUTING=true (enables RouterService.choose_model_intelligent)
- EX_DISABLE_PRESEARCH_INJECTION=true (ensure tools/base no longer pre-searches)
- GLM_BROWSE_MODEL=glm-4.5 (override when use_websearch=true)

## Execution order (checklist)
- [ ] Create cleanup_log.md and start capturing diffs/decisions
- [ ] Phase A edits: request_handler boundary + tools/base cleanup
- [ ] Verify browse + file ingestion validations; append RouterService decisions
- [ ] Phase B: deprecate per-workflow routing/overrides; re-run tests
- [ ] Phase C: remove/archive top-level duplicates; update imports and CI
- [ ] Phase D: docs + tests; finalize and announce flags

## Risk and rollback
- Risks: hidden imports referencing top-level providers/routing; tests expecting minimal_server.py; accidental removal of a used mcp-config.*
- Rollback: env flip (AGENTIC_ROUTER_AT_BOUNDARY=false) returns to legacy; top-level deletions go to docs/legacy/ with shim readme; a single revert commit restores files if needed.

## Validation cadence
- After each phase: run targeted tests and two MCP validations (GLM browse and Kimi file upload) and record RouterService JSON decisions + raw model outputs.

## Appendix A: Candidate File List (top-level)
- REMOVE/ARCHIVE candidates (verify usage first):
  - server_original.py — archive
  - remote_server.py — archive
  - providers/ — delete after migrating any unique bits into src/providers
  - routing/ — delete after migration
  - context/ — delete after migration
  - scripts/minimal_server.py — archive
  - README-ORIGINAL.md — archive
  - mcp-config.json, mcp-config.pylauncher.json — move to docs/legacy/configs/
  - Caddyfile, nginx.conf — keep only if used by current deployment; otherwise move to docs/legacy/deploy/

## Appendix B: One-Page diagram (high-level)
```mermaid
flowchart LR
  A[Client (MCP Tool)] --> B[MCP Boundary: request_handler]
  B -->|AGENTIC_ROUTER_AT_BOUNDARY=true| C[RouterService]
  C --> D[RequestAnalyzer]
  C --> E[GLMFlashManager]
  D --> C
  E --> F[(Provider Capabilities)]
  F --> G[Provider: GLM]
  F --> H[Provider: Kimi]
  B -->|false| I[Legacy Heuristic Backstop]
```

