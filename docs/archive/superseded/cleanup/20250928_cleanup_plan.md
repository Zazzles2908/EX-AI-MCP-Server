# Massive Cleanup Plan (Execute on chore/massive-cleanup-20250928)

## Stepwise plan (≤12 steps)
1) Extract provider-tool registration from server.py
   - Create src/server/provider_tools/registration.py with `register_provider_specific_tools_impl(TOOLS, logger)`; keep server.py thin wrapper calling it. Success: server starts; list_tools includes kimi_* and glm_* when available.
2) Normalize diagnostics scripts
   - Keep scripts/diagnostics/ws_probe.py as canonical; deprecate redundant probes via comments and a README. Success: ws_probe still runs; docs/external_review captures logs.
3) Centralize provider HTTP wrappers
   - Ensure GLM/Kimi wrappers add UA header and optional retry/backoff (env-gated). Success: unit smoke runs; no behavior change by default.
4) Consolidate provider tool registration patterns
   - Ensure lenient import-and-register pattern is identical across Kimi and GLM blocks. Success: identical logging and failure handling.
5) Organize docs and audits
   - Add docs/cleanup/ folder; update provider_params.md links and add Implementation Locations section (done). Success: docs build and link paths valid.
6) Thin server.py
   - Move low-level helpers to src/server/utils/, keep server.py focused on MCP handlers and top-level registry. Success: no signature changes; handlers intact.
7) WS daemon compatibility checks
   - Verify UnifiedRouter shim continues to route; add small smoke in ws_probe. Success: end-to-end flow unchanged.
8) Test coverage shim
   - Add minimal tests for tool registration and list_tools visibility filtering. Success: tests pass locally.
9) Logging hygiene
   - Standardize logger names and levels for provider imports/registration. Success: consistent prefixes; no noisy stacktraces on optional imports.
10) Dead code sweep (non-breaking)
   - Mark unused modules for removal later; add TODOs only (no deletions yet). Success: CI/linters unchanged.
11) Config surface audit
   - Document ENABLE_* flags and provider envs in .env.example; keep .env minimal. Success: parity with current behavior.
12) Prepare Phase 2 (deletions) plan
   - Identify files safe to delete after validation. Success: a PR draft with proposed removals and justifications.

## Risk register (≤6)
- Hidden dependency in server.py
  - Mitigation: wrapper pattern preserves signature; immediate smoke tests and daemon restart.
- Provider tool import errors
  - Mitigation: lenient try/except + informative logs; no crash on failure.
- Behavior drift via retries
  - Mitigation: off by default; gated by env; covered by smoke tests.
- WS daemon coupling
  - Mitigation: no API changes; only internal refactor; ws_probe validation.
- Documentation mismatch
  - Mitigation: update docs alongside changes; link-check locally.
- Test gaps
  - Mitigation: add small focused tests on registration and visibility.

## Test/validation checklist per step
- Step 1: list_tools shows provider tools; call a provider tool; restart daemon OK.
- Step 2: run ws_probe; confirm artifacts in docs/external_review.
- Step 3: unit smoke for wrappers; env OFF path matches previous outputs.
- Step 4: logging outputs match; registration idempotent.
- Step 5: open docs; verify links and paths.
- Step 6: start server; run list_tools/call_tool smoke.
- Step 7: end-to-end simple chat with use_websearch=true logs OK.
- Step 8: run tests; assert visibility and registration behavior.
- Step 9: inspect logs; no stacktraces on missing optional deps.
- Step 10: build/linters unaffected.
- Step 11: env example renders; .env unchanged.
- Step 12: create PR draft; no code deletions yet.

