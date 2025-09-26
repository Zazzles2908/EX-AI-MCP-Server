# Cleanup Log – Phase A kickoff

Date: 2025-09-26

## Validation summaries (EXAI‑MCP chat; no upload/browse)
- GLM: provider=glm, model=glm-4.5-flash, duration≈41.3s, tokens≈909, verdict=KEEP/REMOVE matrix valid; proceed phased
- Kimi: provider=kimi, model=kimi-k2-0711-preview, duration≈42.3s, tokens≈935, verdict=YES safe with archive-first + rollback guard

## KEEP
- src/router/service.py (RouterService) – authoritative routing
- src/core/agentic/__init__.py
- src/core/agentic/request_analyzer.py
- src/core/agentic/glm_flash_manager.py
- src/providers/**
- src/server/**
- utils/file_types.py, utils/health.py

## REMOVE/ARCHIVE (after short stabilization window)
- providers/ (legacy shim), routing/ (legacy shim)
- server_original.py, remote_server.py
- scripts/minimal_server.py
- README-ORIGINAL.md
- extra mcp-config.* (keep mcp-config.augmentcode.json)
- Slim tools/simple/base.py by removing pre-search injection and all routing behaviors (DONE)

## Safe deletion order
1) Docs/scripts: README-ORIGINAL.md; scripts/minimal_server.py
2) Server variants/config: server_original.py; remote_server.py; extra mcp-config.*
3) Legacy shim trees: providers/; routing/

## Rollback guard
- Env: ROLLBACK_PATH=archive/<ts>, USE_LEGACY_ROUTING=true (adds sys.path to archive)
- Shim: minimal import stubs in legacy paths if needed during transition
- CI: run legacy import blocker; full tests after each phase

## Decision
YES: Safe to proceed with phased removal


## Phase C update (post-shutdown)
- Archived: server_original.py, remote_server.py, scripts/minimal_server.py, README-ORIGINAL.md
- Archived configs: mcp-config.json, mcp-config.pylauncher.json (keep mcp-config.augmentcode.json at root)
- providers/ and routing/: no tracked files (only __pycache__), so nothing to move; leave dirs for now and remove in final cleanup

- Removed empty shim directories: providers/ and routing/ (contained only __pycache__)
- Kept operational scripts used in dev: run-server.ps1, run-server.sh, setup-auggie.sh (documented as retained)


## Phase D update (tests + docs)
- Updated tests to import canonical providers: src.providers.* (removed legacy top-level providers imports)
  - tests/test_o3_pro_output_text_fix.py
  - tests/helpers/free_first_registry_check.py
- Diagnostics now prefer mcp-config.augmentcode.json and no longer expect minimal_server.py or top-level providers/
  - scripts/diagnose_mcp.py
  - scripts/exai_diagnose.py
  - scripts/diagnostics/exai_diagnose.py
- Marked Remote Mode docs as Legacy and referenced archived remote_server.py
  - docs/standard_tools/REBRAND_NOTES.md
  - docs/standard_tools/remote.md
  - docs/standard_tools/remote-setup.md
- Legacy import blocker (scripts/check_no_legacy_imports.py): PASS locally
