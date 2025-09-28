# Script Inventory and Phase Mapping

This inventory maps project scripts/modules to the phases in IMPLEMENTATION_ROADMAP.md, with proposed actions, status, and dependencies.

Legend:
- Actions: KEEP (no change), ADJUST (modify), DELETE (remove/retire), ADD (to be created)
- Phases: 0..8 as defined in the roadmap

---

## Phase 0 – Bootstrap & Layout
Files and infrastructure ensuring a minimal runnable skeleton.

- server.py – KEEP – Stdio entrypoint; ensure CLI flags consistent with docs – Depends on src/server/*
- config.py – KEEP – Central config loader – Depends on utils/config_bootstrap.py
- pyproject.toml, requirements*.txt, pytest.ini – KEEP – Tooling/dep config
- utils/* (config_bootstrap, http_client, file_utils, cache, search_cache) – KEEP – Shared infra
- logs/, .logs/ – KEEP – Log targets
- scripts/setup_venvs.ps1 – KEEP – Dev convenience

Notes: No blocking gaps. Ensure minimum env hints exist in docs.

## Phase 1 – MCP Boundary & Request Handling
- src/server/handlers/request_handler.py – ADJUST – Ensure RoutePlan plumbing, continuation_id passthrough – Depends on router/service.py, tools/*
- src/server/handlers/mcp_handlers.py – ADJUST – Normalize tool map wiring and progress capture
- src/server/tools/tool_filter.py – KEEP – Tool allow/deny filtering
- src/server/context/thread_context.py – KEEP – Conversation/thread state
- src/server/registry_bridge.py – KEEP – Bridge to providers registry
- src/server/utils.py – KEEP – Small helpers
- src/server/fallback_orchestrator.py – ADJUST – Align with manager-first routing decisions

Status: Boundary exists; enrich with RoutePlan emission and structured telemetry.

## Phase 2 – Providers & Registry
- src/providers/registry.py – KEEP – Central registry and availability
- src/providers/base.py – KEEP – Shared provider interface
- src/providers/glm.py – ADJUST – Ensure SSE/streaming surface and web_search tools injection path
- src/providers/kimi.py – ADJUST – Expose cache-token capture, optional streaming; align with new docs
- src/providers/capabilities.py – KEEP – Capability adapters (web search)
- src/providers/metadata.py – KEEP – Token usage and model meta
- src/providers/openai_compatible.py – KEEP – Wrapper used by Kimi
- src/providers/zhipu_optional.py – KEEP – Optional GLM extras
- src/providers/hybrid_platform_manager.py – ADJUST – Align or fold into router/service if redundant
- src/providers/custom.py – DELETE – Legacy customization not used by roadmap
- src/providers/openrouter.py – DELETE – Not in current provider scope
- src/providers/openrouter_registry.py – DELETE – Not in current provider scope
- src/providers/moonshot/ – KEEP – Placeholder for native Moonshot integration if expanded later

Status: Core paths present; prune legacy OpenRouter; tighten GLM/Kimi implementations per docs.

## Phase 3 – Manager-First Routing (RoutePlan)
- src/router/service.py – ADJUST – Implement choose_model_with_hint() and RoutePlan struct (requested, chosen, reasons)
- src/router/unified_router.py – KEEP – May serve as compatibility layer; converge with service.py
- src/server/fallback_orchestrator.py – ADJUST – Ensure coherent with RoutePlan

Dependencies: utils/model_context.py, utils/token_utils.py, utils/observability.py

## Phase 4 – Classification & Complexity
- src/core/agentic/task_router.py – ADJUST – Implement classify() outputs (intent, task_type)
- utils/token_utils.py – KEEP – Token estimation for complexity scoring
- systemprompts/*_prompt.py – KEEP – Prompt templates supporting workflows
- utils/model_context.py – KEEP – Thread/session metadata

Status: Building blocks exist; wire classification outputs to Router hints.

## Phase 5 – Tools & Workflows
- tools/registry.py – ADJUST – Consume _route_plan and propagate use_websearch/stream flags
- tools/workflows/*.py (analyze, debug, codereview, refactor, testgen, thinkdeep, tracer, secaudit, planner, consensus, precommit, docgen) – ADJUST – Ensure continuation_id and budget propagation
- tools/providers/glm/glm_files.py – KEEP – File ops integration
- tools/providers/glm/glm_files_cleanup.py – KEEP – Maintenance
- tools/providers/kimi/kimi_upload.py – KEEP – File upload & extract
- tools/providers/kimi/kimi_tools_chat.py – KEEP – Kimi chat wrapper
- tools/capabilities/provider_capabilities.py – KEEP – Expose provider-native features
- tools/streaming/* – KEEP – Streaming demos/helpers
- tools/chat.py – ADJUST – Respect manager routing hints

Status: Rich surface present; ensure consistent flags and metadata propagation.

## Phase 6 – Streaming & Long-Context Excellence
- streaming/streaming_adapter.py – KEEP – Shared streaming utilities
- src/providers/glm.py – KEEP – SSE path present; verify end-to-end
- src/providers/kimi.py – ADJUST – Add env-gated streaming path
- docs: API_platforms/Kimi/context_caching/context_caching_fixed.md – KEEP – Doc alignment

Dependencies: utils/http_client.py timeouts; config flags in config.py.

## Phase 7 – Observability & Health
- utils/observability.py – KEEP – Log/trace helpers
- utils/metrics.py – KEEP – Token/latency metrics
- utils/progress.py – KEEP – Progress capture for long ops
- monitoring/*.py (telemetry.py, health_monitor.py, file_sink.py, slo.py, worker_pool.py, predictive.py, autoscale.py) – KEEP – Infra telemetry
- scripts/diagnostics/* – KEEP – Smoke diagnostics and probes

Status: Observability present; add RoutePlan logging and per-provider aggregates.

## Phase 8 – Test & Verification
- run_tests.py – KEEP – Unified test entry
- scripts/diagnostics/router_service_diagnostics_smoke.py – KEEP – Router smoke
- scripts/ws/* – KEEP – WS daemon smoke flows
- scripts/validate_exai_ws_kimi_tools.py – KEEP – Kimi path validation
- tests (TBD) – ADD – Unit tests for router decisions, providers, workflows, streaming

---

## Cross-Cutting Utilities (referenced across phases)
- utils/*: model_restrictions.py, tool_events.py, file_types.py, instrumention.py, health.py, costs.py – KEEP – Shared services
- src/daemon/ws_server.py, src/daemon/session_manager.py – KEEP – WS daemon
- scripts/mcp_server_wrapper.py, scripts/run_ws_shim.py – KEEP – Stdio↔WS shim

---

## Proposed Deletes (legacy)
- src/providers/custom.py – DELETE – Not used
- src/providers/openrouter.py – DELETE – Out of scope
- src/providers/openrouter_registry.py – DELETE – Out of scope

---

## Gaps To Add (ADD)
- Tests per Phase 8 (router/provider/workflow/streaming)
- RoutePlan schema docs in code (dataclass or TypedDict) and emission in boundary
- Kimi streaming path + env flag

---

## Integration Map (high level)
- Boundary (Phase 1) → Router (Phase 3) with hints from Classification (Phase 4)
- Router decision → Providers (Phase 2) with Capability adapter
- Workflows (Phase 5) drive provider calls; Streaming/Context caching (Phase 6) optimize UX
- Observability (Phase 7) logs RoutePlan and telemetry; Tests (Phase 8) verify end-to-end

