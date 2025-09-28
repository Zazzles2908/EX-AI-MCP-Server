# AI Manager – Routing Logic (GLM‑4.5‑flash manager)

## Purpose
Explain and govern manager‑first routing: resolve model/provider up front, apply policy (fast vs long‑context), accept agentic hints, emit a structured route plan.

## Current Implementation (code paths)
- src/router/service.py: RouterService with choose_model()/choose_model_with_hint(), RouteDecision logging to "router" logger.
- src/server/handlers/request_handler.py: early model resolution (_route_auto_model, resolve_auto_model), boundary logs (boundary_model_resolution_attempt, boundary_model_resolved), tool aliasing (think → thinkdeep), consensus auto‑model selection.
- src/providers/registry.py: capability/cost-aware provider registry, fallback chain, health/circuit options.

## Parameters (env/config)
- FAST_MODEL_DEFAULT, LONG_MODEL_DEFAULT, DEFAULT_MODEL
- GLM_FLASH_MODEL, KIMI_DEFAULT_MODEL, KIMI_THINKING_MODEL, GLM_QUALITY_MODEL, GLM_SPEED_MODEL, KIMI_QUALITY_MODEL, KIMI_SPEED_MODEL
- ROUTER_LOG_LEVEL, ROUTER_DIAGNOSTICS_ENABLED, ROUTER_PREFLIGHT_CHAT
- HIDDEN_MODEL_ROUTER_ENABLED, ROUTER_SENTINEL_MODELS
- ENABLE_INTELLIGENT_SELECTION, THINK_ROUTING_ENABLED

## Dependencies
- Provider registry (src/providers/registry.py)
- Provider SDKs: zhipuai (GLM), Moonshot client via OpenAI‑compatible (Kimi)

## Integration Points
- MCP boundary: src/server/handlers/request_handler.py injects _model_context and resolved model into tool args
- Tools consume _model_context (tools/simple/base.py, workflows/*)
- Observability: router logger + mcp_activity logs for route diagnostics

## Status Assessment
- 🔧 Requires Adjustment: Manager selects models, but does not surface a structured RoutePlan to the caller; capability‑aware pruning (web_search/long‑context/stream) is implicit, not explicit.

## Implementation Notes
- RouterService.accept_agentic_hint() provides candidate ordering based on platform/task_type but is not consistently fed by a classifier.
- request_handler performs multiple routing passes (aliasing, auto selection, hidden router); ensure single source of truth for final decision.

## Next Steps
1) Add RoutePlan struct at boundary; include requested, chosen, provider, reasons, capabilities (web_search, streaming, context window target); attach to arguments["_route_plan"] and to output metadata/logs.
2) Feed RouterService.choose_model_with_hint() with classification + complexity hints (see classification/* docs).
3) Introduce capability matrix filter (min context window, requires_web_search, requires_stream) before fallback.
4) Add tests that assert RoutePlan presence and correct provider/model under different scenarios.

