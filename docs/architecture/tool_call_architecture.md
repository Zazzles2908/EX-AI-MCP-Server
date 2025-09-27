# EX-AI MCP Server – Tool-Call Architecture (Entrypoints → Providers)

This document maps how a user request to any MCP tool travels through the system, which scripts are involved, where routing/model decisions happen, and what each component’s purpose is. It also calls out gaps causing the GLM vs Kimi discrepancies and ThinkDeep timeouts.

## 1) Entrypoints (beginning of a request)

- WebSocket Daemon (WS path)
  - File: src/daemon/ws_server.py
  - Purpose: Long‑lived daemon accepting JSON messages over ws://host:port
  - Key responsibilities:
    - Normalize tool names (_normalize_tool_name)
    - Capacity/backpressure (global/provider/session semaphores)
    - Idempotency & duplicate suppression (req_id + semantic call_key)
    - Calls the unified server boundary: SERVER_HANDLE_CALL_TOOL(name, arguments)
    - Shapes outputs for clients and caches recent results

- stdio MCP Server (CLI/IDE MCP path)
  - File: server.py
  - Purpose: MCP-compliant server over stdio; registers handlers
  - Key registrations:
    - @server.list_tools → src/server/handlers/mcp_handlers.handle_list_tools
    - @server.call_tool → src/server/handlers/request_handler.handle_call_tool (via server.py wrapper)
    - @server.list_prompts → src/server/handlers/mcp_handlers.handle_list_prompts
    - @server.get_prompt → src/server/handlers/mcp_handlers.handle_get_prompt
  - Also: sets up structured logging (toolcalls.jsonl, toolcalls_raw.jsonl, router.jsonl)

ASCII sequences
- WS Flow
  Client → ws_server:call_tool → SERVER_HANDLE_CALL_TOOL → Tool → Response → ws_server (normalize/compat) → Client
- stdio Flow
  Client → server.call_tool_handler → handle_call_tool → Tool → server.call_tool_handler (log) → Client

## 2) Tool discovery/registry (what tools exist)

- Dynamic registry (MCP path)
  - File: src/server/registry_bridge.py
  - Purpose: Singleton bridge around tools/registry.ToolRegistry
  - Used by: src/server/handlers/mcp_handlers.handle_list_tools (builds & lists)

- Static registry (WS path)
  - File: server.py (TOOLS dict)
  - Purpose: Pre-instantiated core tools used directly by WS daemon for list_tools/call_tool

- Tool map & filtering
  - File: tools/registry.py (TOOL_MAP)
  - Purpose: Maps tool name → (module, class), builds instances honoring env flags
  - Additional filtering: src/server/tools/tool_filter.py (DISABLED_TOOLS, ESSENTIAL_TOOLS)

## 3) Server boundary pipeline (the critical path)

Handler: src/server/handlers/request_handler.handle_call_tool(name, arguments)
High‑level sequence (based on actual code):
1) Provider configuration guard: server._ensure_providers_configured()
2) Request_id: generated for logging; activity JSONL started
3) Tool lookup: via src/server/registry_bridge.get_registry().list_tools()
4) Thinking name aliasing: THINK_ROUTING_ENABLED → reroute deepthink → thinkdeep
5) Watchdog/heartbeat/timeout wrappers for long calls
6) Continuation (conversation) context reconstruction
7) Optional session cache injection
8) Centralized model routing (EARLY BOUNDARY RESOLUTION):
   - requested_model = arguments.model or DEFAULT_MODEL
   - _route_auto_model() heuristics:
     - Simple tools → GLM flash
     - thinkdeep → Kimi thinking (unless THINKDEEP_FAST_EXPERT=true, then GLM flash)
     - analyze/codereview/refactor/debug/testgen/planner → step-aware split
   - Boundary model resolution logs:
     - EVENT boundary_model_resolution_attempt
     - EVENT boundary_model_resolved
   - Hidden sentinel support: HIDDEN_MODEL_ROUTER_ENABLED + ROUTER_SENTINEL_MODELS
9) Parse model:option → parse_model_option (e.g., "glm-4.5:thinking")
10) Provider validation & fallback:
    - ModelProviderRegistry.get_provider_for_model(model)
    - If unavailable: suggest fallback via ModelProviderRegistry.get_preferred_fallback_model(tool_category)
11) ModelContext creation:
    - utils.model_context.ModelContext(model_name, model_option)
    - arguments["_model_context"], arguments["_resolved_model_name"]
12) File preflight (env-gated STRICT_FILE_SIZE_REJECTION)
13) Optional date injection (INJECT_CURRENT_DATE)
14) ThinkDeep smart websearch enablement (ENABLE_SMART_WEBSEARCH) + client defaults
15) Execute tool (monitoring wrapper, with Kimi→GLM fallback for kimi_multi_file_chat)
16) Normalize outputs, and optional auto-continue for workflow tools (EX_AUTOCONTINUE_WORKFLOWS)
17) Progress capture appended into final payload

Where each happens in code (request_handler.py):
- Aliasing: lines ~145–172
- Activity logs start: ~174–192
- Timeout/heartbeat: ~194–265
- Continuation/context: ~266–286; cache: ~287–303
- Early model routing: _route_auto_model() ~403–451; boundary logs ~493–504
- ThinkDeep deterministic override: ~507–525 (THINKDEEP_FAST_EXPERT, THINKDEEP_OVERRIDE_EXPLICIT)
- Hidden/sentinel boundary resolution: ~667–711
- Provider validation & fallback: ~711–748
- ModelContext injection: ~750–758
- File preflight: ~759–768
- Smart websearch: ~780–799; client defaults: ~803–814
- Execute + auto-continue: ~816–933

## 4) Provider system & router layer

- Provider configuration
  - File: src/server/providers/provider_config.py (configure_providers)
  - Purpose: Enable Kimi, GLM, Custom, OpenRouter by env keys; register with ModelProviderRegistry
  - Also validates model restrictions and logs availability summary

- Router service (decision logging / preflight)
  - File: src/router/service.py
  - Purpose: Preflight model availability; choose_model() / choose_model_with_hint()
  - Logging: JSONL via logger "router" to .logs/router.jsonl (events: preflight_models, preflight_chat_ok/preflight_chat_fail, route_decision, route_explicit_unavailable)

- Current reality: boundary routing is implemented directly in request_handler (_route_auto_model + boundary sentinels). RouterService is not yet wired into the main path; this is the likely source of inconsistent “glm vs kimi” perceptions across different entry paths.

## 5) Observability & IDs

- Tool call summaries: server.py call_tool_handler → .logs/toolcalls.jsonl (adaptive preview + prompt bullets + summary)
- Raw mirror (optional): server.py call_tool_handler → .logs/toolcalls_raw.jsonl when EXAI_TOOLCALL_LOG_RAW_FULL=true
- Router decisions: src/router/service.py → .logs/router.jsonl (pure JSON)
- Activity breadcrumbs: mcp_activity logger within request_handler
- Request IDs: req_id created at boundary; WS also caches by req_id and a semantic call_key

## 6) Why thinkdeep and some tools appear to “use Kimi” despite glm-4.5 requests

- Manager vs Provider layers: Your EXAI manager (glm-4.5) is separate from the provider model that answers the MCP tool call. Boundary auto-routing can override ambiguous or auto requests.
- Deterministic override: request_handler forces fast model for thinkdeep when THINKDEEP_FAST_EXPERT=true or THINKDEEP_OVERRIDE_EXPLICIT=true.
- WS pre-hint: ws_server infers provider (GLM vs KIMI) from the model string for capacity control; if model unspecified, this may differ from later boundary choice.
- Timeouts: WS daemon enforces hard deadlines; long thinkdeep runs can be cancelled (TIMEOUT) before finishing, creating the impression of non-responsiveness.

## 7) Recommendations (minimal, incremental)

A. Enforce unified AI-manager routing
- Introduce env flag EXAI_UNIFIED_ROUTING=true
- In src/daemon/ws_server.py, do NOT infer provider from model name; instead call RouterService.choose_model_with_hint(requested=arguments.get("model"), hint=arguments.get("agentic_hint")) to set a provisional provider key used only for capacity slots. Do not mutate arguments.model here.
- In src/server/handlers/request_handler.handle_call_tool(), before _route_auto_model(), call RouterService.choose_model_with_hint; log the route_decision JSON and then pass decision.chosen into the existing boundary logic. When EXAI_UNIFIED_ROUTING=true, skip _route_auto_model entirely and prefer RouterService’s decision (still keep parse_model_option + provider validation).

B. Soften thinkdeep overrides
- Default THINKDEEP_FAST_EXPERT=false; respect explicit user model
- Keep THINKDEEP_OVERRIDE_EXPLICIT=false unless a tool explicitly requests expert validation and the model is auto

C. Strengthen observability
- Emit boundary→router correlation id into both .logs/toolcalls*.jsonl and .logs/router.jsonl
- Add reason codes for each reroute (e.g., auto_step1, auto_deep, explicit, agentic_hint)

D. Validation checklist
- [ ] WS calls show route_decision before call_tool in logs/router.jsonl
- [ ] toolcalls.jsonl includes resolved_model and correlation id
- [ ] thinkdeep obeys explicit `model` and completes within heartbeat limits
- [ ] Kimi/GLM provider semaphores align with chosen provider

## 8) Script purposes (quick index)

- server.py – stdio MCP server, handler wiring, logging mirrors, TOOLS map (static), provider guard, call boundary wrapper
- src/daemon/ws_server.py – WS transport, capacity, deduplication, calls SERVER_HANDLE_CALL_TOOL
- src/server/handlers/mcp_handlers.py – MCP list_tools/list_prompts/get_prompt implementations using registry_bridge
- src/server/handlers/request_handler.py – Core boundary: context, auto-routing, provider validation, ModelContext, execution, auto-continue, progress injection
- src/server/providers/provider_config.py – Provider enablement (Kimi/GLM/Custom/OpenRouter) and restriction validation
- src/server/registry_bridge.py – Thin singleton bridge over tools.registry.ToolRegistry
- tools/registry.py – Declarative tool map + builders; supports LEAN/DISABLED gating
- tools/chat.py, tools/workflows/thinkdeep.py – Representative tool implementations and schema
- src/router/service.py – RouterService: preflight + model decision logger (not yet in main boundary path)

