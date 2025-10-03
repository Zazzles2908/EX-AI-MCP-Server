# IMPLEMENTATION ROADMAP – EX‑AI MCP Server (Manager‑First Architecture)

This roadmap guides a team to build (or rebuild) the EX‑AI MCP Server from scratch to the target architecture reflected in the decision‑tree diagrams and the System_layout docs.

References to gap‑aware docs in this folder:
- AI Manager: AI_manager/glm-routing-logic/glm-routing-logic.md; AI_manager/kimi-routing-logic/kimi-routing-logic.md
- Decision flows: decision_tree/glm-routing-flows/glm-routing-flows.md; decision_tree/kimi-routing-flows/kimi-routing-flows.md
- Classification (general): classification/classification_intent_and_capability.md
- Classification (providers): classification/glm-intent-analysis/glm-intent-analysis.md; classification/kimi-intent-analysis/kimi-intent-analysis.md
- Observability: observability/glm-observability/glm-observability.md; observability/kimi-observability/kimi-observability.md
- Tool Registry integration: tool_function/glm-tool-registry-integration/glm-tool-registry-integration.md; tool_function/kimi-tool-registry-integration/kimi-tool-registry-integration.md
- GLM provider docs: API_platforms/GLM/* (web_search, streaming, file_operations, chat_completions, api/*)
- Kimi provider docs: API_platforms/Kimi/* (file_processing, context_caching, chat_completions, streaming, api/*)
- Script inventory & phase mapping: implementation_roadmap/script-inventory-and-phase-mapping.md

---

## Phase 0 – Bootstrap & Layout (Foundation)
Goal: Minimal runnable skeleton and repo hygiene.
- Create repo layout: server.py (stdio entry), src/server/*, src/providers/*, tools/*, docs/*, .logs/.
- Config & env: .env with keys (GLM_API_KEY/ZHIPUAI_API_KEY, KIMI_API_KEY/MOONSHOT_API_KEY); .env.example with guidance.
- Dependency baseline: requirements.txt (mcp, zhipuai, httpx, python‑dotenv, zai‑sdk), lock files.
- Basic CI: lint + unit tests.
Checkpoint: `python -m server --stdio` starts; logs directory created.

## Phase 1 – MCP Boundary & Request Handling
Goal: Single entrypoint for tool calls with model resolution stub.
- Implement src/server/handlers/request_handler.py to: parse calls, build TOOL_MAP, alias think → thinkdeep, watch‑dog/heartbeat, progress capture.
- Inject _model_context placeholder and pass through to tools.
- Add early file‑size guard (utils/file_utils) and client defaults.
Checkpoint: Simple tools (status/listmodels) execute and return JSONL‑mirrored logs.

## Phase 2 – Providers & Registry
Goal: GLM + Kimi providers with registry, availability, and health.
- Implement src/providers/registry.py (priority order, health/circuit optional, cost/free‑tier preferences, telemetry).
- Implement GLM provider (SDK+HTTP fallback): chat, streaming (SSE), file upload.
- Implement Kimi provider (OpenAI‑compatible): chat wrapper with idempotency + context cache token capture; file upload.
- Provider capability adapters: src/providers/capabilities.py for native web_search schema injection.
Checkpoint: Preflight lists available models; trivial chat calls succeed for both providers.

## Phase 3 – Manager‑First Routing (RoutePlan)
Goal: Deterministic, explainable routing up front.
- RouterService (src/router/service.py): choose_model_with_hint(), accept_agentic_hint(), RouteDecision logs.
- Boundary integration: build and attach RoutePlan (requested, chosen, provider, reasons, capabilities: web_search/stream/context target) into arguments["_route_plan"], mirror to toolcalls JSONL.
- Capability matrix: encode min context window, requires_web_search, requires_stream; prune candidates before fallback.
Checkpoint: For ‘auto’ requests, resolved model + route_plan present; logs show reason codes.

## Phase 4 – Classification & Complexity
Goal: Route based on intent and workload.
- Wire src/core/agentic/task_router.IntelligentTaskRouter.classify() at boundary; emit _agentic_task_type.
- Add utils/complexity scorer: token estimate, file count/size, images, latency hints → _complexity_score + flags.
- Feed RouterService hints (platform/task_type) to bias candidate order.
Checkpoint: Long‑context/file‑heavy prompts route to Kimi; fast/short prompts route to GLM‑flash.

## Phase 5 – Tools & Workflows
Goal: Minimal but solid tool surface with provider‑native capabilities.
- tools/registry.py and tools/simple/base.py consume _model_context; ensure use_websearch and stream flags propagate to provider payloads via capabilities adapter.
- Workflows: analyze, debug, codereview, refactor, testgen, thinkdeep; respect continuation_id and budget.
- Optional GLM synthesis hop: after Kimi heavy‑lift, optionally send results to GLM for final analysis summary.
Checkpoint: Tool calls exercise both providers; thinkdeep can optionally enable smart web_search.

## Phase 6 – Streaming & Long‑Context Excellence
Goal: Real‑time UX and cost‑aware long‑context optimization.
- GLM streaming end‑to‑end already supported (SDK/SSE); ensure tool surfaces stream=True path.
- Kimi streaming: env‑gated (KIMI_STREAM_ENABLED) with chunk aggregation similar to GLM.
- Kimi context caching: consistently pass _session_id/_call_key/_tool_name to capture/reuse cache tokens.
Checkpoint: Streaming smoke tests pass for GLM and (when enabled) for Kimi; cache tokens reduce latency.

## Phase 7 – Observability & Health
Goal: Single‑pane observability for routing and provider calls.
- JSONL: router decisions, boundary model resolution, toolcalls with route_plan, provider telemetry with token usage.
- Optional health manager + circuit breaker gating.
- Minimal metrics (success/failure/latency per provider/model) with export hooks.
Checkpoint: RoutePlan appears per call; telemetry aggregates tokens and latencies.

## Phase 8 – Test & Verification Strategy
Goal: High‑confidence, incremental validation.
- Unit tests:
  - Routing: explicit vs auto; long‑context → Kimi; web_search required → GLM tools injected; synthesis hop.
  - Providers: GLM SSE streaming path; Kimi chat wrapper (idempotency + cache token capture); file uploads.
  - Capabilities: web_search schema injection correctness.
- Integration smoke:
  - Preflight (router preflight chat ok/fail paths)
  - Stream demo (GLM, optional Kimi)
  - Workflow chaining with continuation_id and RoutePlan presence
- Non‑destructive by default; use short prompts and small max_tokens.
Checkpoint: CI green; local smoke produces expected logs and metadata.

---

## Priority Order
1) Providers & Registry (Phase 2) – without these, nothing routes.
2) MCP Boundary + Manager Routing (Phases 1 & 3) – make routing explainable (RoutePlan).
3) Classification & Complexity (Phase 4) – correctness and cost optimization.
4) Tools & Workflows (Phase 5) – usable surface.
5) Streaming/Long‑Context (Phase 6) – UX/performance.
6) Observability (Phase 7) – operational visibility.
7) Tests (Phase 8) – regression safety.

## Integration Checkpoints (cross‑phase)
- Preflight: provider availability logged; trivial chats succeed.
- RoutePlan: present on every call; shows web_search/stream/context requirements.
- Web Search: when use_websearch=true, GLM payload includes tools=[{"type":"web_search"}] and tool_choice="auto"; route prunes providers lacking browsing when required.
- Streaming: stream=True propagates end‑to‑end; ModelResponse.metadata.streamed=true.
- Synthesis Hop: when enabled, secondary GLM call executed and annotated in metadata.

## Using the Gap Analysis
- Each doc’s “Status Assessment” calls out ✅ / 🔧 / ❌ / 🗑️ states.
- Implement 🔧/❌ items in priority order above; remove 🗑️ legacy where flagged.
- Re‑run smoke tests and confirm RoutePlan and telemetry reflect intended decisions after each change.

## Deliverables by Phase
- Code changes (providers/registry/router/tools) + env toggles
- Unit/integration tests per checkpoint
- Updated docs in docs/System_layout with decisions and outcomes

This plan yields a manager‑first, provider‑native, observable MCP server aligned with your decision‑tree architecture and the gap analysis captured in this folder.

