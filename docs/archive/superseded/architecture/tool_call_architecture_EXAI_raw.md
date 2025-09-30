# EXAI MCP (chat) — Raw Output: Tool-Call Architecture Analysis

Below is the raw content returned by the EXAI-WS MCP chat tool for the architecture-mapping prompt. This preserves the model’s own identification line and narrative so we can compare with our local analysis.

---

Model answering this prompt: Claude

Based on the provided files, I'll analyze the EX-AI MCP Server architecture to map tool-call entrance points and identify potential issues. Note that some critical files were skipped due to token limits, so I'll indicate where additional context is needed.

## 1) Entry Points Overview

### WS Daemon Path (`src/daemon/ws_server.py`)
- **Receives call**: WebSocket daemon listens on `EXAI_WS_HOST:EXAI_WS_PORT` (default 127.0.0.1:8765)
- **Tool name normalization**: `_normalize_tool_name()` (L207-234) strips suffixes like "_EXAI-WS" and uses aliases (e.g., "chat_EXAI-WS" → "chat")
- **Server boundary call**: Calls `SERVER_HANDLE_CALL_TOOL` (imported from server.py) at L491 after acquiring semaphores
- **Concurrency/backpressure**: 
  - Global semaphore (`GLOBAL_MAX_INFLIGHT`=24)
  - Provider-specific semaphores (KIMI=6, GLM=4)
  - Session-level semaphore (`SESSION_MAX_INFLIGHT`=8)
  - Request de-duplication via semantic call keys
- **Response shaping**: `_normalize_outputs()` (L238-252) ensures consistent format, error handling at L552-570

### stdio MCP Server Path (`server.py`)
- **Handler registration**: Decorators register handlers:
  - `@server.list_tools()` → `list_tools_handler` (L338)
  - `@server.call_tool()` → `call_tool_handler` (L343)
  - `@server.list_prompts()` → `list_prompts_handler` (L464)
  - `@server.get_prompt()` → `get_prompt_handler` (L469)
- **Wiring**: All handlers delegate to functions in `src.server.handlers` module (L136-141)

## 2) call_tool Pipeline (Server Boundary)

*Note: `src/server/handlers/request_handler.py` was skipped - critical details inferred from imports*

### Sequence in `handle_call_tool()` (inferred)
1. Model resolution from arguments or defaults
2. Provider validation via `ModelProviderRegistry`
3. `ModelContext` creation
4. File-size preflight validation (env-gated)
5. Smart Websearch heuristics application
6. Tool execution with auto-continue for workflows

### Key Resolution Points
- **Model resolution**: Occurs in WS daemon at L321-335 and presumably in `request_handler.py`
- **Auto-routing**: WS daemon uses `ModelProviderRegistry` to determine provider from model name (L330-333)
- **ModelContext creation**: Not visible in provided files - likely in `request_handler.py`
- **File-size validation**: Not visible - likely in `request_handler.py` with env flags
- **Smart Websearch**: Not visible - likely tool-specific logic
- **Auto-continue**: Not visible - likely in workflow tools like `thinkdeep.py`

## 3) Tool Registry and Schema Exposure

### Tool Building and Exposure
- **Registry**: `src/server/registry_bridge.py` provides singleton access to `tools.registry.ToolRegistry`
- **MCP exposure**: `handle_list_tools()` in `mcp_handlers.py` (L19-68) uses registry bridge
- **WS exposure**: Directly uses `SERVER_TOOLS` from server.py (L291-289)

### Tool Filtering
- **Client filtering**: In `mcp_handlers.py` (L37-49) via `CLIENT_TOOL_ALLOWLIST`/`DENYLIST`
- **Global filtering**: `DISABLED_TOOLS` and `LEAN_MODE` handled in `ToolRegistry` (not provided)

## 4) Provider Configuration and Routing

### Provider Setup
- `configure_providers()` (imported in server.py L134) - implementation not provided
- Sets up Kimi, GLM, Custom, OpenRouter providers

### RouterService Role (`src/router/service.py`)
- **Decision logging**: Logs to `.logs/router.jsonl` via `router` logger
- **Preflight**: `preflight()` (L53-69) checks provider availability and probes connectivity
- **Model selection**: `choose_model()` (L179-212) and `choose_model_with_hint()` (L128-177)

### Routing vs Auto-routing
- **Router decisions**: Made in `RouterService` when explicitly called
- **Auto-routing**: Occurs in WS daemon (L321-335) without RouterService involvement
- **Discrepancy**: WS daemon bypasses RouterService for provider selection

## 5) Observability

### Log Outputs
- **`.logs/router.jsonl`**: Route decisions and preflight results from RouterService
- **`.logs/toolcalls.jsonl`**: Tool call results with previews/summaries (server.py L350-404)
- **`.logs/toolcalls_raw.jsonl`**: Full model outputs when `EXAI_TOOLCALL_LOG_RAW_FULL=true` (server.py L406-442)
- **MCP activity**: Not visible in provided files

### Request ID Propagation
- **Generation**: Client-provided in WS (L307), from arguments in MCP (L353)
- **Propagation**: Passed through tool calls, used in caching and logging

## 6) Known Pitfalls / Discrepancy Analysis

### thinkdeep Tool Issues
- **Timeout causes**: Hard deadlines in WS daemon (L505-522) may interrupt long-running thinkdeep
- **Model override**: Environment variables `THINKDEEP_FAST_EXPERT` and `THINKDEEP_OVERRIDE_EXPLICIT` may bypass explicit model requests
- **Provider confusion**: Auto-routing in WS daemon (L330-333) may select Kimi even when glm-4.5 requested

### AI Manager Bypass Risks
- **Weak points**: 
  1. WS daemon's direct provider resolution (L321-335) bypasses RouterService
  2. Tools with internal model selection may ignore routing decisions
  3. Provider-specific tools (kimi_*, glm_*) may not use unified boundary

## 7) Specific Recommendations

### Unify AI-Manager Boundary
1. **Patch WS daemon model resolution**:
   - Replace L321-335 in `ws_server.py` with call to `RouterService.choose_model_with_hint()`
   - Remove direct `ModelProviderRegistry` usage

2. **Centralize model context creation**:
   - Move model resolution to `request_handler.py`
   - Create `ModelContext` only after RouterService decision

3. **Env flags for gating**:
   - Add `EXAI_UNIFIED_ROUTING=true` to enable new behavior
   - Add `EXAI_ROUTER_ENFORCE=true` to prevent bypasses

### Minimal Diffs (illustrative)
```
# ws_server.py (replace L321-335):
from src.router.service import RouterService
router = RouterService()
decision = router.choose_model_with_hint(
    requested=arguments.get("model"),
    hint={"platform": arguments.get("platform")}
)
prov_key = decision.provider
```

```
# request_handler.py (insert early):
from src.router.service import RouterService
router = RouterService()
decision = router.choose_model_with_hint(
    requested=arguments.get("model"),
    hint=arguments.get("agentic_hint")
)
arguments["model"] = decision.chosen
```

### Validation Checklist
- [ ] Router decisions present in router.jsonl for every call
- [ ] toolcalls.jsonl shows resolved_model and correlation id
- [ ] thinkdeep respects explicit model and finishes within timeouts
- [ ] Provider semaphores align with chosen provider

---

End of raw EXAI output.

