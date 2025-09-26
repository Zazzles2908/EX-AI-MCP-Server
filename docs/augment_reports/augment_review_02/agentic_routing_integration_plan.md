# Agentic Routing Integration Plan (RouterService + RequestAnalyzer + GLMFlashManager)

Status: PARTIAL YES — ThinkDeep step 1 completed (kimi-latest); step 2 timed out. Proceeding with synthesized plan; will retry step 2 if desired.

## EXAI‑MCP call summary
- Tool: thinkdeep (step 1/2 complete)
- Provider/Model: Kimi / kimi-latest
- Duration: ~0s (tool returned quickly)
- Tokens: ~469 (reported)

## Current state (observed)
- server.py registers tools and dispatches to src/server/handlers/request_handler.py.
- request_handler performs early model resolution (auto → specific) via heuristics and sentinels; injects into tool args.
- ChatTool (tools/chat.py) is a SimpleTool that calls provider.generate_content() with the resolved model.
- Providers are configured by src/server/providers/provider_config.py from .env; ModelProviderRegistry maps models→providers.
- Intelligent routing components exist (src/router/service.py using src/core/agentic RequestAnalyzer + GLMFlashManager) and have tests, but are not wired into request_handler for chat/analyze paths.

## Goals
- Make intelligent routing the default path (env-gated), preserving current behavior when disabled.
- Centralize routing decisions in RouterService with clear logs, minimizing code churn.

## Env flags (proposed)
- ENABLE_INTELLIGENT_ROUTING=true|false (default: false)
- INTELLIGENT_ROUTING_STRATEGY=hybrid|capability|cost|performance (default: hybrid)
- ROUTING_SUMMARY_MAX_TOKENS=500 (already supported by RequestAnalyzer)
- FAST_MODEL_DEFAULT=glm-4.5-flash; LONG_MODEL_DEFAULT=kimi-k2-0711-preview (preserve)
- ROUTER_DIAGNOSTICS_ENABLED=true|false (default: false)

## Integration point (MCP boundary)
File: src/server/handlers/request_handler.py

1) Create module-level singleton accessor:
````python
router_singleton = None

def _get_router():
    global router_singleton
    if router_singleton is None:
        from src.router.service import RouterService
        router_singleton = RouterService()
    return router_singleton
````

2) In resolve_auto_model / model=="auto" block:
````python
if _env_true("ENABLE_INTELLIGENT_ROUTING", "false"):
    try:
        router = _get_router()
        # request_payload should include messages, files, images, use_websearch, tool name
        decision = router.choose_model_intelligent(request_payload, hint={"tool": tool_name})
        recommended = decision.get("recommended_model")
        if recommended:
            model = recommended
        logger.info(json.dumps({"event":"routing_decision","decision":decision}, ensure_ascii=False))
    except Exception as e:
        logger.warning("intelligent routing failed; falling back: %s", e)
# legacy heuristics fallback remains unchanged
````

No changes needed in tools/simple/base.py or providers; they already respect model selection and web-capable tooling.

## Staged deprecations
- Stage 1 (enable flag; no removals): keep legacy heuristics as fallback.
- Stage 2 (post-validation): shrink legacy heuristics; deprecate sentinel model toggles; route everything through RouterService when flag on.
- Stage 3: remove dead paths (<1% usage by telemetry) and any unused server_original scripts.

## Verification strategy
- Unit tests (extend tests/test_intelligent_routing.py):
  - Flag off: auto chat → GLM-4.5-flash (legacy path)
  - Flag on: simple chat → GLM-4.5-flash; long context → Kimi thinking; web intent → web-capable config; hybrid (file+web) handled
  - Provider disabled scenarios: router chooses available provider; consistent error if none
- MCP smoke (docs/augment_reports/augment_review_02):
  - Three prompts: short chat, long context (~1000+ tokens), recent-news web query
  - Capture chosen model/provider and logs (intelligent_routing_analysis + routing_decision events)

## Rollback plan
- Single env toggle: ENABLE_INTELLIGENT_ROUTING=false restores legacy behavior instantly; code paths coexist.

## Implementation Checklist
- [ ] Add _get_router() and flag-gated call in request_handler
- [ ] Add structured logs for analysis and decisions
- [ ] Extend tests/test_intelligent_routing.py with boundary tests
- [ ] Append MCP smoke results to validation_run_webbrowse_kimi.md
- [ ] (Later) Consolidate legacy heuristics and deprecate sentinels

## Notes
- Keep explicit model arguments respected (if user specifies model, do not override).
- Maintain provider capability layer; RouterService decides model/provider; tools/providers remain unchanged.

