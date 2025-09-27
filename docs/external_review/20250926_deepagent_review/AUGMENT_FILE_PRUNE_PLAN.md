# EX-AI MCP Server – File Prune and Keep Plan (PR3/PR4 Baseline)

Date: 2025-09-26
Owner: Augment Agent
Goal: Identify the minimal set of files we need going forward (based on PR #3/#4 production-ready baseline) and propose safe deletions for everything else, executed in waves with verification.

Important: Per your direction, we will use both .env and .env.example (no “minimal env”). Both will be maintained together; .env.example remains authoritative guidance and .env is the active environment.

## A. Core KEEP set (authoritative)
These are required by the new production-ready stack (and/or the deepagent test suite):

- Root modules
  - server.py
  - intelligent_router.py
  - providers.py
  - config.py
  - requirements.txt, pyproject.toml, pytest.ini
  - run_tests.py
- Tests (from deepagent suite)
  - tests/test_mcp_protocol_compliance.py
  - tests/test_intelligent_routing.py
  - tests/test_provider_integration.py
  - tests/test_end_to_end_workflows.py
  - tests/test_configuration_environment.py
  - tests/test_basic_functionality.py
  - tests/conftest.py, tests/mock_helpers.py, tests/load_test.py
- Documentation (must keep)
  - docs/external_review/20250926_deepagent_review/* (including this plan)
  - docs/external_review/20250926_review/* (alignment set requested earlier)
  - docs/architecture (we will add decision tree + updated diagrams)
- src modules required by server.py
  - src/server/**/* (handlers, tools filter, providers wiring, utils)
  - src/router/service.py (if referenced by tests/handlers)
  - Keep only what server.py imports or its immediate dependencies require
- Tool registry (short term)
  - tools/* as referenced by server.py TOOLS import list (we can trim after we reduce tool registration)

## B. Candidates to KEEP (short-term), revisit later
- src/providers/* (some parts may be legacy/overlap with root providers.py)
- monitoring/*, utils/* (observability helpers referenced by server)
- logs/* (runtime artifacts)
- scripts/ws_start.ps1 and a small subset used in daily ops

Rationale: server.py currently imports src.server.* modules and tools.*; until we narrow the tool surface and confirm no transitive dependencies, we keep these to avoid breakage.

## C. DELETE candidates (Wave 1)
Remove obvious legacy/unnecessary items not used by the PR3/PR4 baseline, with pre-checks (grep/import checks):

- simulator_tests/**
- test_simulation_files/**
- outputs/** (report artifacts)
- ex_mcp_server.egg-info/**
- venvs/** (local environments)
- docs/augment_reports/previous_audit/** (historical)
- docs/external_review/superseeded/**
- patch/** (temporary utilities now superceded)
- nl/** (legacy command processor)
- dr/** (recovery plan prototype)
- ui/** (non-essential for server runtime)
- templates/** (legacy project templates)

We will run a reference scan before deletion: confirm no imports or file reads reference these paths.

## D. DELETE candidates (Wave 2)
After server/tool surface is trimmed and tests pass:

- Unused tools subpackages not referenced by the final TOOLS set in server.py
- Redundant providers under src/providers if root-level providers.py is canonical
- Redundant docs under docs/standard_tools that conflict with the new single source of truth

This wave follows code changes to reduce dependencies (e.g., shrinking TOOLS in server.py), then verifying tests.

## E. Tests to REMOVE (Wave 1)
The current tests/ contains a very large legacy suite. Keep only the deepagent suite listed in section A. Hard delete all other tests in tests/.

## F. Process and safeguards
1) Create cleanup branch (e.g., chore/prune-pr3pr4-01)
2) Automated reference scan for each DELETE candidate
   - Grep for import/use
   - If references found, move candidate to Wave 2
3) Apply deletions for Wave 1
4) Run the deepagent test suite only (no real keys by default)
5) Open PR with detailed change log and a KEEP/DELETE matrix

## G. Environment policy (per your instruction)
- Maintain both .env and .env.example. No “minimal env” reduction.
- Keep .env.example authoritative and align .env accordingly (add comments where necessary).

## H. Request for confirmation
- Are you comfortable with Wave 1 DELETE set above?
- For legacy tests: archive to docs/augment_reports/archive or delete outright?
- Preferred branch name for the cleanup PR?

Once you confirm, I’ll execute Wave 1 quickly and open the cleanup PR with the KEEP/DELETE matrix and reference-scan results.



## I. Adopted Implementation Summary (Deepagent Test Guide)
We are aligning the KEEP set and verification plan exactly to the categories below. This becomes the authoritative scope for what we retain and how we validate after pruning.

- MCP Protocol Compliance (tests/test_mcp_protocol_compliance.py)
  - Tool discovery/registration, WebSocket/stdio, message format, error handling, concurrent requests
- Intelligent Routing (tests/test_intelligent_routing.py)
  - GLM-4.5-Flash manager, GLM←web, Kimi←files, cost-aware routing, fallback/provider switching, confidence scoring
- Provider Integration (tests/test_provider_integration.py)
  - GLM native browsing, Kimi file processing, real-key integration, timeout/retry, rate limiting, health checks, concurrency
- End-to-End Workflows (tests/test_end_to_end_workflows.py)
  - Full user flows, routing validation, multi-step, perf baseline, resource cleanup, error recovery
- Configuration & Environment (tests/test_configuration_environment.py)
  - Production config loading, API key validation, env handling, logging/monitoring, security, dev vs prod
- Performance & Load (tests/load_test.py)
  - Locust load testing, concurrent WS sessions, stress tests, response time, throughput

Understanding/Implications:
- These tests define the production-ready baseline; everything else is optional/legacy and can be archived/deleted after reference scans.
- We will not run tests until you lift the pause on local testing. When approved, we’ll run only the suite above first.
- Env policy confirmed: use .env and .env.example (no “minimal env”).
- server.py remains the entrypoint; we will remove its unused imports (intelligent_router/providers) after Wave 1 unless needed.
- server_original.py will be hard deleted in Wave 1 (per your instruction).


## II. Wave 1 removals executed
Hard-deleted the following files (directories may remain empty due to tooling constraints; will be removed in PR via git):
- server_original.py
- docs/external_review/superseeded/* (8 files)
- patch/* (3 files)
- nl/command_processor.py
- dr/recovery_plan.py
- ui/progressive_config.py, ui/suggestions.py
- templates/auggie/* (4 files)
- ex_mcp_server.egg-info/* (6 files)
- simulator_tests/* (37 files)
- test_simulation_files/* (4 files)
- outputs/reports/ws_chat_analysis_README.md

Remaining empty dirs to remove in PR: docs/external_review/superseeded, patch, nl/__pycache__, dr/__pycache__, ui/__pycache__, templates/auggie, ex_mcp_server.egg-info, simulator_tests/__pycache__, test_simulation_files (now empty), outputs/reports (now empty), venvs.
