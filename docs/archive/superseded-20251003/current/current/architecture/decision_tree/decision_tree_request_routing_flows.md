# Decision Tree – Request Classification and Routing Flows

## Purpose
Describe end‑to‑end flow: parse → classify → capability/complexity analysis → route (GLM/Kimi/general) → execute → optional synthesis → return results + metadata.

## Current Implementation (code paths)
- Boundary dispatch: src/server/handlers/request_handler.py (tool aliasing, auto model routing, consensus auto‑selection).
- Manager: src/router/service.py (choose_model_with_hint, diagnostics).
- Provider selection/fallback: src/providers/registry.py (get_preferred_fallback_model, call_with_fallback).

## Parameters
- EX_TOOL_TIMEOUT_SECONDS, EX_HEARTBEAT_SECONDS, EX_WATCHDOG_WARN_SECONDS, EX_WATCHDOG_ERROR_SECONDS
- CLIENT_DEFAULTS_USE_WEBSEARCH, ENABLE_SMART_WEBSEARCH (thinkdeep only)

## Integration Points
- Classification signals should be placed into arguments (e.g., _agentic_task_type, _complexity_score) before routing.
- Route decision should be emitted as RoutePlan for observability and returned metadata.

## Status Assessment
- 🔧 Requires Adjustment: Flow partially implemented via heuristics; missing explicit classification/complexity stage and structured route plan emission.

## Implementation Notes
- Current heuristics: _route_auto_model (per tool), resolve_auto_model (locale/CJK, category), hidden sentinel routing.
- Web search enabling is ad‑hoc (thinkdeep smart websearch) and client‑default based; not expressed as a plan requirement.

## Next Steps
1) Insert an explicit “classify + complexity” step at boundary; persist results into args.
2) Compute RoutePlan that includes web_search "required|allowed|off", streaming mode, and min context requirement.
3) If provider chosen ≠ GLM and synthesis flag is set, perform optional final GLM synthesis hop; include in metadata.

