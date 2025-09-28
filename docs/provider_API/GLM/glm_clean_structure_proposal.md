# Proposed clean code structure for EX-AI MCP Server

Goal: keep transports thin, centralize handlers, keep providers cohesive, make tools modular. This matches common MCP server patterns and the current repo direction.

## Target layout (high level)
```
src/
  server/
    __init__.py
    handlers/
      __init__.py
      mcp_handlers.py        # list_tools/get_prompt, etc.
      request_handler.py     # single boundary for call_tool
    providers/
      __init__.py
      provider_config.py     # detect env, register concrete providers
    registry_bridge.py       # tool registry adapter
    utils/                   # server-only utilities (progress, limits)
  providers/
    __init__.py
    base.py                  # ModelProvider, ProviderType, caps
    registry.py              # ModelProviderRegistry
    glm.py                   # GLMModelProvider (SDK-first, HTTP fallback)
    kimi.py                  # KimiModelProvider (OpenAI-compatible)
  daemon/
    ws_server.py             # optional WS shim, transport only
  utils/
    http_client.py           # one HTTP wrapper (httpx)
    logging.py, files.py, ...

tools/
  __init__.py
  registry.py                # Tool registry map
  shared/
    base_tool.py             # abstract Tool base
  providers/
    glm/
      glm_files.py           # upload, multi-file chat
      glm_agents.py          # /v1 agents APIs
      glm_web_search.py      # /paas/v4 web_search
    kimi/
      ...

docs/
  provider_API/
    GLM/
      ... (analysis documents)
    Kimi/
      ...
```

## Specific recommendations
- Remove root-level `providers.py` after verifying no imports (duplicated by `src/providers/*`).
- Keep `src/providers/zhipu` empty or remove it; prefer a single `src/providers/glm.py`.
- Standardize HTTP calls on `utils/http_client.py` (httpx) and gradually remove ad-hoc `requests` uses in tools.
- Keep the WS shim optional; no tool or provider logic should live there.
- Limit cross-package imports: tools -> providers via registry only; providers never import tools.

## Benefits
- Clear single execution boundary; easy to test.
- Providers are self-contained and discoverable.
- Transport choices (stdio vs WS) don’t affect business logic.
- Consistent HTTP/SDK behavior and telemetry.

