# WS Daemon Restart — Validation Excerpts (2025-09-28)

Command executed:

- powershell -NoProfile -ExecutionPolicy Bypass -File .\\scripts\\ws_start.ps1 -Restart

Key log excerpts:

```
Restart requested: stopping any running daemon...
Stopping WS daemon (PID=34420)...
WS daemon stopped (port free).
Starting WS daemon...
Stopping WS daemon (PID=34420)...
WS daemon stopped (port free).
2025-09-28 14:23:46,775 - server - INFO - Registering provider-specific tools: ['glm_upload_file', 'kimi_multi_file_chat', 'kimi_upload_and_extract']
2025-09-28 14:23:46,776 - ws_daemon - INFO - Starting WS daemon on ws://127.0.0.1:8765
2025-09-28 14:23:46,777 - websockets.server - INFO - server listening on 127.0.0.1:8765
2025-09-28 14:23:50,166 - websockets.server - INFO - connection open
2025-09-28 14:23:50,168 - src.server.providers.provider_config - INFO - Kimi API key found - Moonshot AI models available
2025-09-28 14:23:50,169 - src.server.providers.provider_config - INFO - GLM API key found - ZhipuAI models available
2025-09-28 14:23:50,169 - src.server.providers.provider_config - INFO - Available providers: Kimi, GLM
2025-09-28 14:23:50,169 - root - INFO - Model allow-list not configured for OpenAI Compatible - all models permitted. To restrict access, set KIMI_ALLOWED_MODELS with comma-separated model names.
2025-09-28 14:23:50,169 - root - INFO - Using extended timeouts for custom endpoint: https://api.moonshot.ai/v1
2025-09-28 14:23:50,438 - src.server.providers.provider_config - INFO - Providers configured: KIMI, GLM; GLM models: 4; Kimi models: 15
2025-09-28 14:23:50,438 - src.server.providers.provider_config - INFO - No model restrictions configured - all models allowed
2025-09-28 14:24:32,676 - src.server.handlers.request_handler - INFO - MCP tool call: chat req_id=cd0e211c-b745-4d31-8901-cc79aff1fbdd
2025-09-28 14:24:32,685 - src.server.handlers.request_handler - INFO - [MODEL_ROUTE] tool=chat requested=kimi-latest resolved=kimi-latest reason=explicit
2025-09-28 14:25:01,089 - httpx - INFO - HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2025-09-28 14:25:08,609 - src.server.handlers.request_handler - INFO - MCP tool call: chat req_id=fba1226b-054c-43d5-8858-a276edae6a94
2025-09-28 14:25:08,610 - src.server.handlers.request_handler - INFO - [MODEL_ROUTE] tool=chat requested=glm-4.5 resolved=glm-4.5 reason=explicit
2025-09-28 14:25:24,311 - httpx - INFO - HTTP Request: POST https://open.bigmodel.cn/api/paas/v4/chat/completions "HTTP/1.1 200 OK"
2025-09-28 14:25:33,549 - src.server.handlers.request_handler - INFO - MCP tool call: analyze req_id=00ff69ee-f487-4b11-9b18-dd2dce66dd4a
2025-09-28 14:25:42,828 - src.server.handlers.request_handler - INFO - MCP tool call: thinkdeep req_id=135c644b-7619-4b23-8f17-06964c8f38d3
```

Git/branch state at time of snapshot:

- Branch: feature/exai-mcp-roadmap-implementation
- Dirty: false
- Ahead/Behind vs main: 0/0 (main=stage1-cleanup-complete)

Push step executed:

- gh: push origin feature/exai-mcp-roadmap-implementation (no local changes to commit at this step)

