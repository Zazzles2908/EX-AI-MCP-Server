2025-10-16 13:53:22.648 | 2025-10-16 02:53:22 INFO root: [ASYNC_LOGGING] Async-safe logging configured successfully
2025-10-16 13:53:22.649 | 2025-10-16 02:53:22 INFO ws_daemon: [AUTH] Authentication enabled (token first 10 chars): test-token...
2025-10-16 13:53:22.649 | 2025-10-16 02:53:22 INFO root: [LOGGING] Configured websockets library logging to suppress handshake noise
2025-10-16 13:53:22.839 | 2025-10-16 02:53:22 INFO utils.infrastructure.performance_metrics: Performance metrics collector initialized (enabled=True, window_size=1000)
2025-10-16 13:53:22.915 | 2025-10-16 02:53:22 INFO src.bootstrap.singletons: Building tool registry (first-time initialization)
2025-10-16 13:53:23.082 | 2025-10-16 02:53:23 INFO src.bootstrap.singletons: Tool registry built successfully with 29 tools
2025-10-16 13:53:23.082 | 2025-10-16 02:53:23 INFO src.daemon.session_manager: [SESSION_MANAGER] Initialized with timeout=3600s, max_sessions=100, cleanup_interval=300s
2025-10-16 13:53:23.084 | 2025-10-16 02:53:23 INFO ws_daemon: Configuring providers and registering tools at daemon startup...
2025-10-16 13:53:23.085 | 2025-10-16 02:53:23 INFO src.bootstrap.singletons: Configuring providers (first-time initialization)
2025-10-16 13:53:23.085 | 2025-10-16 02:53:23 INFO src.server.providers.provider_detection: Kimi API key found - Moonshot AI models available
2025-10-16 13:53:23.085 | 2025-10-16 02:53:23 INFO src.server.providers.provider_detection: GLM API key found - ZhipuAI models available
2025-10-16 13:53:23.085 | 2025-10-16 02:53:23 INFO src.server.providers.provider_diagnostics: Available providers: Kimi, GLM
2025-10-16 13:53:23.085 | 2025-10-16 02:53:23 INFO root: Model allow-list not configured for OpenAI Compatible - all models permitted. To restrict access, set KIMI_ALLOWED_MODELS with comma-separated model names.
2025-10-16 13:53:23.085 | 2025-10-16 02:53:23 INFO root: Using extended timeouts for custom endpoint: https://api.moonshot.ai/v1
2025-10-16 13:53:23.150 | 2025-10-16 02:53:23 INFO src.providers.glm: GLM provider using SDK with base_url=https://api.z.ai/api/paas/v4
2025-10-16 13:53:23.150 | 2025-10-16 02:53:23 INFO src.server.providers.provider_diagnostics: Providers configured: KIMI, GLM; GLM models: 6; Kimi models: 18
2025-10-16 13:53:23.150 | 2025-10-16 02:53:23 INFO src.server.providers.provider_restrictions: No model restrictions configured - all models allowed
2025-10-16 13:53:23.150 | 2025-10-16 02:53:23 INFO src.bootstrap.singletons: Providers configured successfully
2025-10-16 13:53:23.150 | 2025-10-16 02:53:23 INFO ws_daemon: Providers configured successfully. Total tools available: 29
2025-10-16 13:53:23.150 | 2025-10-16 02:53:23 INFO ws_daemon: Starting WS daemon on ws://0.0.0.0:8079
2025-10-16 13:54:57.653 | 2025-10-16 02:54:57 INFO ws_daemon: [WS_CONNECTION] New connection from 172.17.0.1:48378
2025-10-16 13:54:57.654 | 2025-10-16 02:54:57 INFO src.daemon.session_manager: [SESSION_MANAGER] Created session 51da5b3e-3b0e-428d-84ce-286afa858595 (total sessions: 1)
2025-10-16 13:54:57.654 | 2025-10-16 02:54:57 INFO ws_daemon: === TOOL CALL RECEIVED ===
2025-10-16 13:54:57.655 | 2025-10-16 02:54:57 INFO ws_daemon: Session: 51da5b3e-3b0e-428d-84ce-286afa858595
2025-10-16 13:54:57.655 | 2025-10-16 02:54:57 INFO ws_daemon: Tool: chat (original: chat)
2025-10-16 13:54:57.655 | 2025-10-16 02:54:57 INFO ws_daemon: Request ID: 049addbf-a653-489a-965e-fd79d20f72bf
2025-10-16 13:54:57.655 | 2025-10-16 02:54:57 INFO ws_daemon: Arguments (first 500 chars): {
2025-10-16 13:54:57.655 |   "prompt": "Great news! I've successfully rebuilt the Docker image and the Supabase files are now in the container:\n\n\u2705 /app/utils/conversation/storage_factory.py\n\u2705 /app/utils/conversation/supabase_memory.py  \n\u2705 /app/src/storage/supabase_client.py\n\nThe container is running and daemon started successfully. Now I need to:\n\n1. Test if the storage factory is actually being used by the conversation system\n2. Verify Supabase connectivity from the container\n3. Check if dual s
2025-10-16 13:54:57.656 | 2025-10-16 02:54:57 INFO ws_daemon: === PROCESSING ===
2025-10-16 13:54:57.656 | 2025-10-16 02:54:57 INFO src.server.handlers.request_handler_init: MCP tool call: chat req_id=965ddd50-8236-4876-98d4-b4fce1ab9069
2025-10-16 13:54:57.658 | 2025-10-16 02:54:57 INFO mcp_activity: TOOL_CALL: chat with 6 arguments req_id=965ddd50-8236-4876-98d4-b4fce1ab9069
2025-10-16 13:54:57.660 | 2025-10-16 02:54:57 INFO src.server.handlers.request_handler: MCP tool call: chat req_id=965ddd50-8236-4876-98d4-b4fce1ab9069
2025-10-16 13:54:57.660 | 2025-10-16 02:54:57 INFO mcp_activity: CONVERSATION_RESUME: chat resuming thread dfb181bd-eeff-40d9-be8f-6add2f7c5093 req_id=965ddd50-8236-4876-98d4-b4fce1ab9069
2025-10-16 13:54:57.660 | 2025-10-16 02:54:57 INFO utils.conversation.threads: [STORAGE_INTEGRATION] Storage factory available - will use configured backend
2025-10-16 13:54:57.660 | 2025-10-16 02:54:57 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:54:57.666 | 2025-10-16 02:54:57 INFO src.storage.supabase_client: [SUPABASE_INIT] SUPABASE_URL=SET
2025-10-16 13:54:57.666 | 2025-10-16 02:54:57 INFO src.storage.supabase_client: [SUPABASE_INIT] SUPABASE_SERVICE_ROLE_KEY=SET
2025-10-16 13:54:57.666 | 2025-10-16 02:54:57 INFO src.storage.supabase_client: Supabase storage initialized: https://mxaazuhlqewmkweewyaz.supabase.co
2025-10-16 13:54:58.149 | 2025-10-16 02:54:58 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/schema_version?select=version&limit=1 "HTTP/2 200 OK"
2025-10-16 13:54:58.151 | 2025-10-16 02:54:58 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:54:58.236 | 2025-10-16 02:54:58 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:54:58.237 | 2025-10-16 02:54:58 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:54:58.237 | 2025-10-16 02:54:58 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:54:58.333 | 2025-10-16 02:54:58 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:54:58.334 | 2025-10-16 02:54:58 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:54:58.334 | 2025-10-16 02:54:58 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:54:58.390 | 2025-10-16 02:54:58 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:54:58.391 | 2025-10-16 02:54:58 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:54:58.391 | 2025-10-16 02:54:58 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:54:58.452 | 2025-10-16 02:54:58 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:54:58.452 | 2025-10-16 02:54:58 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:54:58.452 | 2025-10-16 02:54:58 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:54:58.511 | 2025-10-16 02:54:58 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:54:58.512 | 2025-10-16 02:54:58 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:54:58.512 | 2025-10-16 02:54:58 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:54:58.588 | 2025-10-16 02:54:58 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:54:58.588 | 2025-10-16 02:54:58 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:54:58.588 | 2025-10-16 02:54:58 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:54:58.694 | 2025-10-16 02:54:58 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:54:58.695 | 2025-10-16 02:54:58 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:54:58.695 | 2025-10-16 02:54:58 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:54:58.754 | 2025-10-16 02:54:58 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:54:58.755 | 2025-10-16 02:54:58 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:54:58.755 | 2025-10-16 02:54:58 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:54:58.822 | 2025-10-16 02:54:58 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:54:58.823 | 2025-10-16 02:54:58 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:54:58.823 | 2025-10-16 02:54:58 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:54:58.883 | 2025-10-16 02:54:58 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:54:58.884 | 2025-10-16 02:54:58 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:54:58.884 | 2025-10-16 02:54:58 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:54:58.964 | 2025-10-16 02:54:58 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:54:58.964 | 2025-10-16 02:54:58 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:54:58.964 | 2025-10-16 02:54:58 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:54:59.022 | 2025-10-16 02:54:59 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:54:59.022 | 2025-10-16 02:54:59 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:54:59.022 | 2025-10-16 02:54:59 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:54:59.094 | 2025-10-16 02:54:59 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:54:59.094 | 2025-10-16 02:54:59 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:54:59.095 | 2025-10-16 02:54:59 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:54:59.178 | 2025-10-16 02:54:59 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:54:59.179 | 2025-10-16 02:54:59 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:54:59.179 | 2025-10-16 02:54:59 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:54:59.237 | 2025-10-16 02:54:59 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:54:59.238 | 2025-10-16 02:54:59 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:54:59.238 | 2025-10-16 02:54:59 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:54:59.301 | 2025-10-16 02:54:59 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:54:59.302 | 2025-10-16 02:54:59 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:54:59.302 | 2025-10-16 02:54:59 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:54:59.355 | 2025-10-16 02:54:59 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:54:59.355 | 2025-10-16 02:54:59 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:54:59.355 | 2025-10-16 02:54:59 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:54:59.408 | 2025-10-16 02:54:59 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:54:59.409 | 2025-10-16 02:54:59 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:54:59.409 | 2025-10-16 02:54:59 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:54:59.453 | 2025-10-16 02:54:59 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:54:59.454 | 2025-10-16 02:54:59 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:54:59.454 | 2025-10-16 02:54:59 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:54:59.519 | 2025-10-16 02:54:59 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:54:59.520 | 2025-10-16 02:54:59 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:54:59.520 | 2025-10-16 02:54:59 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:54:59.571 | 2025-10-16 02:54:59 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:54:59.572 | 2025-10-16 02:54:59 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:54:59.572 | 2025-10-16 02:54:59 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:54:59.642 | 2025-10-16 02:54:59 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:54:59.643 | 2025-10-16 02:54:59 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:54:59.643 | 2025-10-16 02:54:59 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:54:59.715 | 2025-10-16 02:54:59 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:54:59.716 | 2025-10-16 02:54:59 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:54:59.716 | 2025-10-16 02:54:59 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:54:59.789 | 2025-10-16 02:54:59 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:54:59.790 | 2025-10-16 02:54:59 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:54:59.790 | 2025-10-16 02:54:59 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:54:59.856 | 2025-10-16 02:54:59 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:54:59.857 | 2025-10-16 02:54:59 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:54:59.857 | 2025-10-16 02:54:59 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:54:59.912 | 2025-10-16 02:54:59 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:54:59.913 | 2025-10-16 02:54:59 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:54:59.913 | 2025-10-16 02:54:59 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:00.004 | 2025-10-16 02:55:00 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:00.005 | 2025-10-16 02:55:00 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:00.005 | 2025-10-16 02:55:00 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:00.066 | 2025-10-16 02:55:00 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:00.067 | 2025-10-16 02:55:00 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:00.067 | 2025-10-16 02:55:00 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:00.132 | 2025-10-16 02:55:00 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:00.132 | 2025-10-16 02:55:00 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:00.132 | 2025-10-16 02:55:00 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:00.187 | 2025-10-16 02:55:00 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:00.189 | 2025-10-16 02:55:00 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:00.189 | 2025-10-16 02:55:00 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:00.242 | 2025-10-16 02:55:00 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:00.243 | 2025-10-16 02:55:00 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:00.243 | 2025-10-16 02:55:00 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:00.297 | 2025-10-16 02:55:00 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:00.298 | 2025-10-16 02:55:00 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:00.298 | 2025-10-16 02:55:00 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:00.359 | 2025-10-16 02:55:00 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:00.360 | 2025-10-16 02:55:00 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:00.360 | 2025-10-16 02:55:00 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:00.411 | 2025-10-16 02:55:00 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:00.411 | 2025-10-16 02:55:00 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:00.411 | 2025-10-16 02:55:00 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:00.458 | 2025-10-16 02:55:00 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:00.459 | 2025-10-16 02:55:00 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:00.459 | 2025-10-16 02:55:00 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:00.513 | 2025-10-16 02:55:00 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:00.514 | 2025-10-16 02:55:00 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:00.514 | 2025-10-16 02:55:00 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:00.560 | 2025-10-16 02:55:00 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:00.561 | 2025-10-16 02:55:00 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:00.561 | 2025-10-16 02:55:00 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:00.609 | 2025-10-16 02:55:00 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:00.610 | 2025-10-16 02:55:00 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:00.610 | 2025-10-16 02:55:00 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:00.656 | 2025-10-16 02:55:00 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:00.657 | 2025-10-16 02:55:00 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:00.657 | 2025-10-16 02:55:00 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:00.716 | 2025-10-16 02:55:00 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:00.717 | 2025-10-16 02:55:00 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:00.717 | 2025-10-16 02:55:00 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:00.772 | 2025-10-16 02:55:00 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:00.773 | 2025-10-16 02:55:00 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:00.773 | 2025-10-16 02:55:00 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:00.820 | 2025-10-16 02:55:00 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:00.821 | 2025-10-16 02:55:00 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:00.821 | 2025-10-16 02:55:00 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:00.873 | 2025-10-16 02:55:00 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:00.873 | 2025-10-16 02:55:00 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:00.873 | 2025-10-16 02:55:00 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:00.925 | 2025-10-16 02:55:00 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:00.925 | 2025-10-16 02:55:00 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:00.925 | 2025-10-16 02:55:00 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:00.978 | 2025-10-16 02:55:00 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:00.979 | 2025-10-16 02:55:00 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:00.979 | 2025-10-16 02:55:00 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:01.065 | 2025-10-16 02:55:01 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:01.066 | 2025-10-16 02:55:01 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:01.066 | 2025-10-16 02:55:01 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:01.129 | 2025-10-16 02:55:01 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:01.130 | 2025-10-16 02:55:01 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:01.130 | 2025-10-16 02:55:01 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:01.228 | 2025-10-16 02:55:01 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:01.229 | 2025-10-16 02:55:01 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:01.229 | 2025-10-16 02:55:01 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:01.308 | 2025-10-16 02:55:01 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:01.309 | 2025-10-16 02:55:01 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:01.309 | 2025-10-16 02:55:01 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:01.379 | 2025-10-16 02:55:01 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:01.380 | 2025-10-16 02:55:01 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:01.380 | 2025-10-16 02:55:01 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:01.429 | 2025-10-16 02:55:01 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:01.430 | 2025-10-16 02:55:01 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:01.430 | 2025-10-16 02:55:01 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:01.494 | 2025-10-16 02:55:01 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:01.495 | 2025-10-16 02:55:01 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:01.495 | 2025-10-16 02:55:01 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:01.554 | 2025-10-16 02:55:01 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:01.555 | 2025-10-16 02:55:01 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:01.555 | 2025-10-16 02:55:01 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:01.705 | 2025-10-16 02:55:01 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:01.706 | 2025-10-16 02:55:01 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:01.706 | 2025-10-16 02:55:01 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:01.782 | 2025-10-16 02:55:01 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:01.783 | 2025-10-16 02:55:01 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:01.783 | 2025-10-16 02:55:01 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:01.840 | 2025-10-16 02:55:01 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:01.841 | 2025-10-16 02:55:01 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:01.841 | 2025-10-16 02:55:01 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:01.906 | 2025-10-16 02:55:01 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:01.907 | 2025-10-16 02:55:01 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:01.907 | 2025-10-16 02:55:01 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:01.966 | 2025-10-16 02:55:01 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:01.966 | 2025-10-16 02:55:01 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:01.966 | 2025-10-16 02:55:01 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:02.016 | 2025-10-16 02:55:02 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:02.016 | 2025-10-16 02:55:02 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:02.016 | 2025-10-16 02:55:02 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:02.063 | 2025-10-16 02:55:02 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:02.064 | 2025-10-16 02:55:02 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:02.064 | 2025-10-16 02:55:02 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:02.119 | 2025-10-16 02:55:02 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:02.120 | 2025-10-16 02:55:02 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:02.120 | 2025-10-16 02:55:02 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:02.178 | 2025-10-16 02:55:02 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:02.179 | 2025-10-16 02:55:02 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:02.179 | 2025-10-16 02:55:02 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:02.295 | 2025-10-16 02:55:02 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:02.297 | 2025-10-16 02:55:02 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:02.297 | 2025-10-16 02:55:02 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:02.382 | 2025-10-16 02:55:02 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:02.383 | 2025-10-16 02:55:02 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:02.384 | 2025-10-16 02:55:02 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:02.504 | 2025-10-16 02:55:02 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:02.505 | 2025-10-16 02:55:02 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:02.505 | 2025-10-16 02:55:02 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:02.560 | 2025-10-16 02:55:02 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:02.561 | 2025-10-16 02:55:02 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:02.561 | 2025-10-16 02:55:02 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:02.643 | 2025-10-16 02:55:02 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:02.645 | 2025-10-16 02:55:02 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:02.645 | 2025-10-16 02:55:02 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:02.786 | 2025-10-16 02:55:02 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:02.788 | 2025-10-16 02:55:02 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:02.788 | 2025-10-16 02:55:02 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:02.849 | 2025-10-16 02:55:02 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:02.850 | 2025-10-16 02:55:02 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:02.850 | 2025-10-16 02:55:02 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:02.901 | 2025-10-16 02:55:02 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:02.902 | 2025-10-16 02:55:02 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:02.902 | 2025-10-16 02:55:02 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:02.964 | 2025-10-16 02:55:02 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:02.965 | 2025-10-16 02:55:02 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:02.965 | 2025-10-16 02:55:02 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:03.025 | 2025-10-16 02:55:03 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:03.025 | 2025-10-16 02:55:03 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:03.026 | 2025-10-16 02:55:03 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:03.125 | 2025-10-16 02:55:03 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:03.126 | 2025-10-16 02:55:03 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:03.126 | 2025-10-16 02:55:03 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:03.191 | 2025-10-16 02:55:03 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:03.192 | 2025-10-16 02:55:03 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:03.192 | 2025-10-16 02:55:03 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:03.245 | 2025-10-16 02:55:03 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:03.246 | 2025-10-16 02:55:03 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:03.246 | 2025-10-16 02:55:03 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:03.321 | 2025-10-16 02:55:03 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:03.322 | 2025-10-16 02:55:03 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:03.322 | 2025-10-16 02:55:03 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:03.397 | 2025-10-16 02:55:03 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:03.397 | 2025-10-16 02:55:03 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:03.397 | 2025-10-16 02:55:03 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:03.461 | 2025-10-16 02:55:03 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:03.462 | 2025-10-16 02:55:03 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:03.462 | 2025-10-16 02:55:03 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:03.518 | 2025-10-16 02:55:03 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:03.519 | 2025-10-16 02:55:03 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:03.519 | 2025-10-16 02:55:03 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:03.586 | 2025-10-16 02:55:03 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:03.587 | 2025-10-16 02:55:03 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:03.587 | 2025-10-16 02:55:03 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:03.656 | 2025-10-16 02:55:03 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:03.657 | 2025-10-16 02:55:03 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:03.657 | 2025-10-16 02:55:03 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:03.733 | 2025-10-16 02:55:03 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:03.734 | 2025-10-16 02:55:03 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:03.734 | 2025-10-16 02:55:03 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:03.811 | 2025-10-16 02:55:03 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:03.812 | 2025-10-16 02:55:03 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:03.812 | 2025-10-16 02:55:03 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:03.883 | 2025-10-16 02:55:03 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:03.884 | 2025-10-16 02:55:03 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:03.884 | 2025-10-16 02:55:03 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:03.947 | 2025-10-16 02:55:03 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:03.948 | 2025-10-16 02:55:03 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:03.948 | 2025-10-16 02:55:03 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:04.018 | 2025-10-16 02:55:04 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:04.018 | 2025-10-16 02:55:04 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:04.018 | 2025-10-16 02:55:04 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:04.077 | 2025-10-16 02:55:04 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:04.078 | 2025-10-16 02:55:04 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:04.078 | 2025-10-16 02:55:04 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:04.139 | 2025-10-16 02:55:04 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:04.140 | 2025-10-16 02:55:04 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:04.140 | 2025-10-16 02:55:04 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:04.201 | 2025-10-16 02:55:04 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:04.202 | 2025-10-16 02:55:04 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:04.202 | 2025-10-16 02:55:04 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:04.261 | 2025-10-16 02:55:04 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:04.262 | 2025-10-16 02:55:04 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:04.262 | 2025-10-16 02:55:04 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:04.360 | 2025-10-16 02:55:04 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:04.360 | 2025-10-16 02:55:04 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:04.360 | 2025-10-16 02:55:04 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:04.404 | 2025-10-16 02:55:04 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:04.405 | 2025-10-16 02:55:04 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:04.405 | 2025-10-16 02:55:04 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:04.471 | 2025-10-16 02:55:04 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:04.472 | 2025-10-16 02:55:04 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:04.472 | 2025-10-16 02:55:04 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:04.534 | 2025-10-16 02:55:04 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:04.535 | 2025-10-16 02:55:04 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:04.535 | 2025-10-16 02:55:04 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:04.607 | 2025-10-16 02:55:04 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:04.608 | 2025-10-16 02:55:04 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:04.608 | 2025-10-16 02:55:04 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:04.690 | 2025-10-16 02:55:04 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:04.691 | 2025-10-16 02:55:04 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:04.691 | 2025-10-16 02:55:04 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:04.754 | 2025-10-16 02:55:04 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:04.756 | 2025-10-16 02:55:04 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:04.756 | 2025-10-16 02:55:04 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:04.817 | 2025-10-16 02:55:04 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:04.818 | 2025-10-16 02:55:04 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:04.818 | 2025-10-16 02:55:04 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:04.887 | 2025-10-16 02:55:04 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:04.889 | 2025-10-16 02:55:04 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:04.889 | 2025-10-16 02:55:04 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:04.977 | 2025-10-16 02:55:04 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:04.978 | 2025-10-16 02:55:04 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:04.978 | 2025-10-16 02:55:04 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:05.051 | 2025-10-16 02:55:05 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:05.053 | 2025-10-16 02:55:05 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:05.053 | 2025-10-16 02:55:05 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:05.132 | 2025-10-16 02:55:05 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:05.135 | 2025-10-16 02:55:05 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:05.135 | 2025-10-16 02:55:05 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:05.207 | 2025-10-16 02:55:05 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:05.208 | 2025-10-16 02:55:05 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:05.208 | 2025-10-16 02:55:05 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:05.274 | 2025-10-16 02:55:05 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:05.275 | 2025-10-16 02:55:05 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:05.275 | 2025-10-16 02:55:05 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:05.353 | 2025-10-16 02:55:05 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:05.354 | 2025-10-16 02:55:05 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:05.354 | 2025-10-16 02:55:05 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:05.412 | 2025-10-16 02:55:05 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:05.412 | 2025-10-16 02:55:05 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:05.412 | 2025-10-16 02:55:05 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:05.471 | 2025-10-16 02:55:05 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:05.472 | 2025-10-16 02:55:05 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:05.472 | 2025-10-16 02:55:05 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:05.523 | 2025-10-16 02:55:05 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:05.524 | 2025-10-16 02:55:05 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:05.524 | 2025-10-16 02:55:05 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:05.575 | 2025-10-16 02:55:05 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:05.576 | 2025-10-16 02:55:05 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:05.576 | 2025-10-16 02:55:05 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:05.623 | 2025-10-16 02:55:05 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:05.624 | 2025-10-16 02:55:05 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:05.624 | 2025-10-16 02:55:05 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:05.681 | 2025-10-16 02:55:05 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:05.681 | 2025-10-16 02:55:05 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:05.682 | 2025-10-16 02:55:05 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:05.749 | 2025-10-16 02:55:05 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:05.750 | 2025-10-16 02:55:05 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:05.750 | 2025-10-16 02:55:05 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:05.796 | 2025-10-16 02:55:05 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:05.797 | 2025-10-16 02:55:05 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:05.797 | 2025-10-16 02:55:05 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:05.911 | 2025-10-16 02:55:05 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:05.912 | 2025-10-16 02:55:05 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:05.912 | 2025-10-16 02:55:05 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:05.981 | 2025-10-16 02:55:05 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:05.982 | 2025-10-16 02:55:05 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:05.982 | 2025-10-16 02:55:05 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:06.033 | 2025-10-16 02:55:06 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:06.034 | 2025-10-16 02:55:06 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:06.034 | 2025-10-16 02:55:06 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:06.080 | 2025-10-16 02:55:06 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:06.081 | 2025-10-16 02:55:06 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:06.081 | 2025-10-16 02:55:06 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:06.131 | 2025-10-16 02:55:06 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:06.132 | 2025-10-16 02:55:06 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:06.132 | 2025-10-16 02:55:06 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:06.177 | 2025-10-16 02:55:06 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:06.178 | 2025-10-16 02:55:06 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:06.178 | 2025-10-16 02:55:06 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:06.226 | 2025-10-16 02:55:06 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:06.226 | 2025-10-16 02:55:06 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:06.226 | 2025-10-16 02:55:06 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:06.285 | 2025-10-16 02:55:06 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:06.285 | 2025-10-16 02:55:06 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:06.285 | 2025-10-16 02:55:06 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:06.331 | 2025-10-16 02:55:06 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:06.332 | 2025-10-16 02:55:06 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:06.332 | 2025-10-16 02:55:06 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:06.380 | 2025-10-16 02:55:06 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:06.381 | 2025-10-16 02:55:06 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:06.381 | 2025-10-16 02:55:06 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:06.425 | 2025-10-16 02:55:06 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:06.425 | 2025-10-16 02:55:06 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:06.425 | 2025-10-16 02:55:06 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:06.483 | 2025-10-16 02:55:06 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:06.484 | 2025-10-16 02:55:06 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:06.484 | 2025-10-16 02:55:06 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:06.543 | 2025-10-16 02:55:06 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:06.543 | 2025-10-16 02:55:06 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:06.543 | 2025-10-16 02:55:06 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:06.602 | 2025-10-16 02:55:06 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:06.603 | 2025-10-16 02:55:06 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:06.603 | 2025-10-16 02:55:06 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:06.701 | 2025-10-16 02:55:06 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:06.701 | 2025-10-16 02:55:06 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:06.701 | 2025-10-16 02:55:06 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:06.751 | 2025-10-16 02:55:06 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:06.751 | 2025-10-16 02:55:06 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:06.751 | 2025-10-16 02:55:06 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:06.802 | 2025-10-16 02:55:06 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:06.802 | 2025-10-16 02:55:06 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:06.802 | 2025-10-16 02:55:06 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:06.851 | 2025-10-16 02:55:06 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:06.852 | 2025-10-16 02:55:06 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:06.852 | 2025-10-16 02:55:06 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:06.914 | 2025-10-16 02:55:06 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:06.915 | 2025-10-16 02:55:06 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:06.915 | 2025-10-16 02:55:06 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:06.984 | 2025-10-16 02:55:06 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:06.985 | 2025-10-16 02:55:06 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:06.985 | 2025-10-16 02:55:06 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:07.039 | 2025-10-16 02:55:07 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:07.040 | 2025-10-16 02:55:07 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:07.040 | 2025-10-16 02:55:07 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:07.086 | 2025-10-16 02:55:07 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:07.086 | 2025-10-16 02:55:07 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:07.087 | 2025-10-16 02:55:07 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:07.149 | 2025-10-16 02:55:07 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:07.150 | 2025-10-16 02:55:07 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:07.150 | 2025-10-16 02:55:07 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:07.196 | 2025-10-16 02:55:07 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:07.198 | 2025-10-16 02:55:07 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:07.198 | 2025-10-16 02:55:07 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:07.251 | 2025-10-16 02:55:07 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:07.253 | 2025-10-16 02:55:07 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:07.253 | 2025-10-16 02:55:07 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:07.313 | 2025-10-16 02:55:07 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:07.315 | 2025-10-16 02:55:07 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:07.315 | 2025-10-16 02:55:07 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:07.364 | 2025-10-16 02:55:07 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:07.365 | 2025-10-16 02:55:07 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:07.365 | 2025-10-16 02:55:07 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:07.412 | 2025-10-16 02:55:07 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:07.413 | 2025-10-16 02:55:07 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:07.413 | 2025-10-16 02:55:07 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:07.475 | 2025-10-16 02:55:07 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:07.475 | 2025-10-16 02:55:07 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:07.475 | 2025-10-16 02:55:07 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:07.534 | 2025-10-16 02:55:07 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:07.535 | 2025-10-16 02:55:07 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:07.535 | 2025-10-16 02:55:07 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:07.584 | 2025-10-16 02:55:07 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:07.585 | 2025-10-16 02:55:07 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:07.585 | 2025-10-16 02:55:07 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:07.669 | 2025-10-16 02:55:07 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:07.670 | 2025-10-16 02:55:07 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:07.670 | 2025-10-16 02:55:07 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:07.720 | 2025-10-16 02:55:07 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:07.720 | 2025-10-16 02:55:07 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:07.720 | 2025-10-16 02:55:07 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:07.770 | 2025-10-16 02:55:07 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:07.771 | 2025-10-16 02:55:07 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:07.771 | 2025-10-16 02:55:07 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:07.831 | 2025-10-16 02:55:07 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:07.832 | 2025-10-16 02:55:07 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:07.832 | 2025-10-16 02:55:07 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:07.878 | 2025-10-16 02:55:07 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:07.880 | 2025-10-16 02:55:07 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:07.880 | 2025-10-16 02:55:07 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:07.939 | 2025-10-16 02:55:07 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:07.940 | 2025-10-16 02:55:07 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:07.940 | 2025-10-16 02:55:07 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:07.988 | 2025-10-16 02:55:07 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:07.989 | 2025-10-16 02:55:07 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:07.989 | 2025-10-16 02:55:07 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:08.039 | 2025-10-16 02:55:08 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:08.040 | 2025-10-16 02:55:08 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:08.040 | 2025-10-16 02:55:08 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:08.085 | 2025-10-16 02:55:08 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:08.086 | 2025-10-16 02:55:08 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:08.086 | 2025-10-16 02:55:08 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:08.134 | 2025-10-16 02:55:08 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:08.135 | 2025-10-16 02:55:08 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:08.135 | 2025-10-16 02:55:08 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:08.194 | 2025-10-16 02:55:08 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:08.195 | 2025-10-16 02:55:08 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:08.195 | 2025-10-16 02:55:08 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:08.242 | 2025-10-16 02:55:08 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:08.242 | 2025-10-16 02:55:08 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:08.242 | 2025-10-16 02:55:08 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:08.290 | 2025-10-16 02:55:08 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:08.290 | 2025-10-16 02:55:08 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:08.290 | 2025-10-16 02:55:08 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:08.338 | 2025-10-16 02:55:08 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:08.339 | 2025-10-16 02:55:08 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:08.339 | 2025-10-16 02:55:08 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:08.397 | 2025-10-16 02:55:08 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:08.398 | 2025-10-16 02:55:08 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:08.398 | 2025-10-16 02:55:08 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:08.452 | 2025-10-16 02:55:08 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:08.452 | 2025-10-16 02:55:08 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:08.452 | 2025-10-16 02:55:08 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:08.496 | 2025-10-16 02:55:08 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:08.497 | 2025-10-16 02:55:08 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:08.497 | 2025-10-16 02:55:08 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:08.543 | 2025-10-16 02:55:08 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:08.544 | 2025-10-16 02:55:08 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:08.544 | 2025-10-16 02:55:08 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:08.608 | 2025-10-16 02:55:08 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:08.609 | 2025-10-16 02:55:08 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:08.609 | 2025-10-16 02:55:08 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:08.667 | 2025-10-16 02:55:08 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:08.668 | 2025-10-16 02:55:08 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:08.668 | 2025-10-16 02:55:08 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:08.740 | 2025-10-16 02:55:08 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:08.741 | 2025-10-16 02:55:08 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:08.741 | 2025-10-16 02:55:08 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:08.797 | 2025-10-16 02:55:08 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:08.797 | 2025-10-16 02:55:08 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:08.797 | 2025-10-16 02:55:08 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:08.854 | 2025-10-16 02:55:08 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:08.854 | 2025-10-16 02:55:08 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:08.854 | 2025-10-16 02:55:08 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:08.943 | 2025-10-16 02:55:08 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:08.944 | 2025-10-16 02:55:08 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:08.944 | 2025-10-16 02:55:08 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:09.001 | 2025-10-16 02:55:09 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:09.002 | 2025-10-16 02:55:09 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:09.002 | 2025-10-16 02:55:09 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:09.047 | 2025-10-16 02:55:09 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:09.048 | 2025-10-16 02:55:09 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:09.048 | 2025-10-16 02:55:09 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:09.112 | 2025-10-16 02:55:09 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:09.113 | 2025-10-16 02:55:09 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:09.113 | 2025-10-16 02:55:09 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:09.178 | 2025-10-16 02:55:09 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:09.179 | 2025-10-16 02:55:09 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:09.179 | 2025-10-16 02:55:09 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:09.238 | 2025-10-16 02:55:09 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:09.239 | 2025-10-16 02:55:09 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:09.239 | 2025-10-16 02:55:09 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:09.307 | 2025-10-16 02:55:09 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:09.310 | 2025-10-16 02:55:09 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:09.310 | 2025-10-16 02:55:09 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:09.376 | 2025-10-16 02:55:09 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:09.378 | 2025-10-16 02:55:09 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:09.378 | 2025-10-16 02:55:09 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:09.443 | 2025-10-16 02:55:09 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:09.445 | 2025-10-16 02:55:09 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:09.445 | 2025-10-16 02:55:09 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:09.494 | 2025-10-16 02:55:09 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:09.496 | 2025-10-16 02:55:09 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:09.496 | 2025-10-16 02:55:09 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:09.556 | 2025-10-16 02:55:09 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:09.557 | 2025-10-16 02:55:09 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:09.557 | 2025-10-16 02:55:09 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:09.606 | 2025-10-16 02:55:09 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:09.607 | 2025-10-16 02:55:09 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:09.607 | 2025-10-16 02:55:09 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:09.656 | 2025-10-16 02:55:09 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:09.656 | 2025-10-16 02:55:09 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:09.657 | 2025-10-16 02:55:09 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:09.717 | 2025-10-16 02:55:09 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:09.718 | 2025-10-16 02:55:09 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:09.718 | 2025-10-16 02:55:09 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:09.774 | 2025-10-16 02:55:09 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:09.775 | 2025-10-16 02:55:09 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:09.775 | 2025-10-16 02:55:09 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:09.826 | 2025-10-16 02:55:09 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:09.827 | 2025-10-16 02:55:09 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:09.827 | 2025-10-16 02:55:09 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:09.876 | 2025-10-16 02:55:09 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:09.877 | 2025-10-16 02:55:09 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:09.877 | 2025-10-16 02:55:09 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:09.929 | 2025-10-16 02:55:09 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:09.930 | 2025-10-16 02:55:09 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:09.930 | 2025-10-16 02:55:09 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:10.023 | 2025-10-16 02:55:10 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:10.024 | 2025-10-16 02:55:10 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:10.024 | 2025-10-16 02:55:10 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:10.086 | 2025-10-16 02:55:10 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:10.087 | 2025-10-16 02:55:10 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:10.087 | 2025-10-16 02:55:10 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:10.167 | 2025-10-16 02:55:10 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:10.168 | 2025-10-16 02:55:10 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:10.168 | 2025-10-16 02:55:10 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:10.250 | 2025-10-16 02:55:10 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:10.251 | 2025-10-16 02:55:10 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:10.251 | 2025-10-16 02:55:10 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:10.380 | 2025-10-16 02:55:10 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:10.380 | 2025-10-16 02:55:10 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:10.380 | 2025-10-16 02:55:10 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:10.446 | 2025-10-16 02:55:10 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:10.447 | 2025-10-16 02:55:10 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:10.447 | 2025-10-16 02:55:10 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:10.503 | 2025-10-16 02:55:10 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:10.504 | 2025-10-16 02:55:10 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:10.504 | 2025-10-16 02:55:10 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:10.561 | 2025-10-16 02:55:10 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:10.562 | 2025-10-16 02:55:10 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:10.562 | 2025-10-16 02:55:10 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:10.618 | 2025-10-16 02:55:10 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:10.619 | 2025-10-16 02:55:10 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:10.619 | 2025-10-16 02:55:10 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:10.699 | 2025-10-16 02:55:10 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:10.700 | 2025-10-16 02:55:10 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:10.700 | 2025-10-16 02:55:10 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:10.753 | 2025-10-16 02:55:10 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:10.753 | 2025-10-16 02:55:10 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:10.753 | 2025-10-16 02:55:10 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:10.798 | 2025-10-16 02:55:10 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:10.799 | 2025-10-16 02:55:10 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:10.799 | 2025-10-16 02:55:10 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:10.857 | 2025-10-16 02:55:10 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:10.858 | 2025-10-16 02:55:10 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:10.858 | 2025-10-16 02:55:10 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:10.909 | 2025-10-16 02:55:10 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:10.909 | 2025-10-16 02:55:10 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:10.909 | 2025-10-16 02:55:10 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:10.981 | 2025-10-16 02:55:10 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:10.982 | 2025-10-16 02:55:10 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:10.982 | 2025-10-16 02:55:10 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:11.028 | 2025-10-16 02:55:11 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:11.028 | 2025-10-16 02:55:11 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:11.028 | 2025-10-16 02:55:11 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:11.107 | 2025-10-16 02:55:11 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:11.108 | 2025-10-16 02:55:11 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:11.108 | 2025-10-16 02:55:11 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:11.209 | 2025-10-16 02:55:11 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:11.210 | 2025-10-16 02:55:11 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:11.210 | 2025-10-16 02:55:11 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:11.300 | 2025-10-16 02:55:11 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:11.301 | 2025-10-16 02:55:11 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:11.301 | 2025-10-16 02:55:11 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:11.373 | 2025-10-16 02:55:11 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:11.376 | 2025-10-16 02:55:11 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:11.376 | 2025-10-16 02:55:11 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:11.431 | 2025-10-16 02:55:11 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:11.432 | 2025-10-16 02:55:11 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:11.432 | 2025-10-16 02:55:11 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:11.498 | 2025-10-16 02:55:11 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:11.499 | 2025-10-16 02:55:11 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:11.499 | 2025-10-16 02:55:11 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:11.551 | 2025-10-16 02:55:11 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:11.552 | 2025-10-16 02:55:11 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:11.552 | 2025-10-16 02:55:11 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:11.640 | 2025-10-16 02:55:11 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:11.642 | 2025-10-16 02:55:11 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:11.642 | 2025-10-16 02:55:11 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:11.713 | 2025-10-16 02:55:11 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:11.715 | 2025-10-16 02:55:11 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:11.715 | 2025-10-16 02:55:11 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:11.782 | 2025-10-16 02:55:11 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:11.782 | 2025-10-16 02:55:11 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:11.782 | 2025-10-16 02:55:11 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:11.829 | 2025-10-16 02:55:11 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:11.831 | 2025-10-16 02:55:11 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:11.831 | 2025-10-16 02:55:11 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:11.878 | 2025-10-16 02:55:11 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:11.879 | 2025-10-16 02:55:11 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:11.879 | 2025-10-16 02:55:11 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:11.943 | 2025-10-16 02:55:11 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:11.945 | 2025-10-16 02:55:11 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:11.945 | 2025-10-16 02:55:11 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:12.040 | 2025-10-16 02:55:12 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:12.041 | 2025-10-16 02:55:12 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:12.041 | 2025-10-16 02:55:12 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:12.116 | 2025-10-16 02:55:12 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:12.117 | 2025-10-16 02:55:12 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:12.117 | 2025-10-16 02:55:12 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:12.196 | 2025-10-16 02:55:12 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:12.197 | 2025-10-16 02:55:12 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:12.197 | 2025-10-16 02:55:12 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:12.249 | 2025-10-16 02:55:12 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:12.249 | 2025-10-16 02:55:12 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:12.249 | 2025-10-16 02:55:12 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:12.309 | 2025-10-16 02:55:12 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:12.310 | 2025-10-16 02:55:12 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:12.310 | 2025-10-16 02:55:12 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:12.385 | 2025-10-16 02:55:12 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:12.386 | 2025-10-16 02:55:12 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:12.386 | 2025-10-16 02:55:12 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:12.447 | 2025-10-16 02:55:12 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:12.448 | 2025-10-16 02:55:12 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:12.448 | 2025-10-16 02:55:12 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:12.512 | 2025-10-16 02:55:12 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:12.513 | 2025-10-16 02:55:12 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:12.513 | 2025-10-16 02:55:12 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:12.559 | 2025-10-16 02:55:12 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:12.560 | 2025-10-16 02:55:12 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:12.560 | 2025-10-16 02:55:12 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:12.613 | 2025-10-16 02:55:12 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:12.614 | 2025-10-16 02:55:12 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:12.614 | 2025-10-16 02:55:12 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:12.676 | 2025-10-16 02:55:12 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:12.676 | 2025-10-16 02:55:12 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:12.676 | 2025-10-16 02:55:12 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:12.725 | 2025-10-16 02:55:12 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:12.726 | 2025-10-16 02:55:12 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:12.726 | 2025-10-16 02:55:12 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:12.786 | 2025-10-16 02:55:12 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:12.786 | 2025-10-16 02:55:12 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:12.786 | 2025-10-16 02:55:12 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:12.838 | 2025-10-16 02:55:12 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:12.839 | 2025-10-16 02:55:12 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:12.839 | 2025-10-16 02:55:12 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:12.898 | 2025-10-16 02:55:12 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:12.899 | 2025-10-16 02:55:12 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:12.899 | 2025-10-16 02:55:12 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:12.965 | 2025-10-16 02:55:12 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:12.966 | 2025-10-16 02:55:12 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:12.966 | 2025-10-16 02:55:12 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:13.026 | 2025-10-16 02:55:13 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:13.027 | 2025-10-16 02:55:13 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:13.027 | 2025-10-16 02:55:13 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:13.079 | 2025-10-16 02:55:13 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:13.079 | 2025-10-16 02:55:13 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:13.079 | 2025-10-16 02:55:13 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:13.143 | 2025-10-16 02:55:13 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:13.144 | 2025-10-16 02:55:13 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:13.144 | 2025-10-16 02:55:13 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:13.203 | 2025-10-16 02:55:13 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:13.204 | 2025-10-16 02:55:13 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:13.204 | 2025-10-16 02:55:13 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:13.260 | 2025-10-16 02:55:13 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:13.261 | 2025-10-16 02:55:13 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:13.261 | 2025-10-16 02:55:13 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:13.310 | 2025-10-16 02:55:13 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:13.311 | 2025-10-16 02:55:13 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:13.311 | 2025-10-16 02:55:13 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:13.369 | 2025-10-16 02:55:13 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:13.370 | 2025-10-16 02:55:13 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:13.370 | 2025-10-16 02:55:13 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:13.464 | 2025-10-16 02:55:13 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:13.465 | 2025-10-16 02:55:13 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:13.465 | 2025-10-16 02:55:13 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:13.508 | 2025-10-16 02:55:13 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:13.508 | 2025-10-16 02:55:13 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:13.508 | 2025-10-16 02:55:13 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:13.553 | 2025-10-16 02:55:13 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:13.554 | 2025-10-16 02:55:13 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:13.554 | 2025-10-16 02:55:13 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:13.608 | 2025-10-16 02:55:13 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:13.609 | 2025-10-16 02:55:13 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:13.609 | 2025-10-16 02:55:13 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:13.670 | 2025-10-16 02:55:13 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:13.672 | 2025-10-16 02:55:13 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:13.672 | 2025-10-16 02:55:13 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:13.731 | 2025-10-16 02:55:13 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:13.731 | 2025-10-16 02:55:13 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:13.731 | 2025-10-16 02:55:13 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:13.795 | 2025-10-16 02:55:13 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:13.796 | 2025-10-16 02:55:13 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:13.796 | 2025-10-16 02:55:13 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:13.839 | 2025-10-16 02:55:13 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:13.840 | 2025-10-16 02:55:13 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:13.840 | 2025-10-16 02:55:13 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:13.886 | 2025-10-16 02:55:13 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:13.888 | 2025-10-16 02:55:13 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:13.888 | 2025-10-16 02:55:13 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:13.954 | 2025-10-16 02:55:13 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:13.954 | 2025-10-16 02:55:13 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:13.955 | 2025-10-16 02:55:13 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:14.011 | 2025-10-16 02:55:14 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:14.012 | 2025-10-16 02:55:14 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:14.012 | 2025-10-16 02:55:14 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:14.075 | 2025-10-16 02:55:14 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:14.076 | 2025-10-16 02:55:14 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:14.076 | 2025-10-16 02:55:14 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:14.135 | 2025-10-16 02:55:14 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:14.136 | 2025-10-16 02:55:14 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:14.136 | 2025-10-16 02:55:14 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:14.183 | 2025-10-16 02:55:14 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:14.184 | 2025-10-16 02:55:14 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:14.184 | 2025-10-16 02:55:14 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:14.242 | 2025-10-16 02:55:14 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:14.243 | 2025-10-16 02:55:14 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:14.243 | 2025-10-16 02:55:14 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:14.324 | 2025-10-16 02:55:14 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:14.324 | 2025-10-16 02:55:14 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:14.324 | 2025-10-16 02:55:14 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:14.386 | 2025-10-16 02:55:14 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:14.386 | 2025-10-16 02:55:14 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:14.386 | 2025-10-16 02:55:14 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:14.439 | 2025-10-16 02:55:14 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:14.440 | 2025-10-16 02:55:14 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:14.440 | 2025-10-16 02:55:14 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:14.495 | 2025-10-16 02:55:14 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:14.496 | 2025-10-16 02:55:14 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:14.496 | 2025-10-16 02:55:14 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:14.555 | 2025-10-16 02:55:14 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:14.556 | 2025-10-16 02:55:14 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:14.556 | 2025-10-16 02:55:14 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:14.633 | 2025-10-16 02:55:14 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:14.633 | 2025-10-16 02:55:14 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:14.633 | 2025-10-16 02:55:14 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:14.737 | 2025-10-16 02:55:14 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:14.738 | 2025-10-16 02:55:14 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:14.738 | 2025-10-16 02:55:14 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:14.787 | 2025-10-16 02:55:14 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:14.788 | 2025-10-16 02:55:14 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:14.788 | 2025-10-16 02:55:14 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:14.838 | 2025-10-16 02:55:14 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:14.839 | 2025-10-16 02:55:14 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:14.839 | 2025-10-16 02:55:14 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:14.894 | 2025-10-16 02:55:14 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:14.895 | 2025-10-16 02:55:14 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:14.895 | 2025-10-16 02:55:14 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:14.977 | 2025-10-16 02:55:14 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:14.978 | 2025-10-16 02:55:14 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:14.978 | 2025-10-16 02:55:14 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:15.055 | 2025-10-16 02:55:15 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:15.056 | 2025-10-16 02:55:15 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:15.056 | 2025-10-16 02:55:15 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:15.125 | 2025-10-16 02:55:15 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:15.126 | 2025-10-16 02:55:15 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:15.126 | 2025-10-16 02:55:15 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:15.195 | 2025-10-16 02:55:15 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:15.196 | 2025-10-16 02:55:15 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:15.196 | 2025-10-16 02:55:15 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:15.249 | 2025-10-16 02:55:15 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:15.250 | 2025-10-16 02:55:15 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:15.250 | 2025-10-16 02:55:15 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:15.313 | 2025-10-16 02:55:15 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:15.314 | 2025-10-16 02:55:15 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:15.314 | 2025-10-16 02:55:15 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:15.370 | 2025-10-16 02:55:15 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:15.371 | 2025-10-16 02:55:15 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:15.371 | 2025-10-16 02:55:15 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:15.422 | 2025-10-16 02:55:15 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:15.423 | 2025-10-16 02:55:15 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:15.423 | 2025-10-16 02:55:15 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:15.473 | 2025-10-16 02:55:15 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:15.473 | 2025-10-16 02:55:15 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:15.473 | 2025-10-16 02:55:15 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:15.541 | 2025-10-16 02:55:15 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:15.541 | 2025-10-16 02:55:15 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:15.542 | 2025-10-16 02:55:15 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:15.615 | 2025-10-16 02:55:15 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:15.616 | 2025-10-16 02:55:15 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:15.616 | 2025-10-16 02:55:15 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:15.663 | 2025-10-16 02:55:15 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:15.663 | 2025-10-16 02:55:15 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:15.663 | 2025-10-16 02:55:15 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:15.732 | 2025-10-16 02:55:15 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:15.732 | 2025-10-16 02:55:15 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:15.732 | 2025-10-16 02:55:15 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:15.785 | 2025-10-16 02:55:15 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:15.786 | 2025-10-16 02:55:15 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:15.786 | 2025-10-16 02:55:15 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:15.847 | 2025-10-16 02:55:15 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:15.848 | 2025-10-16 02:55:15 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:15.848 | 2025-10-16 02:55:15 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:15.913 | 2025-10-16 02:55:15 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:15.914 | 2025-10-16 02:55:15 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:15.914 | 2025-10-16 02:55:15 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:15.974 | 2025-10-16 02:55:15 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:15.975 | 2025-10-16 02:55:15 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:15.975 | 2025-10-16 02:55:15 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:16.029 | 2025-10-16 02:55:16 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:16.031 | 2025-10-16 02:55:16 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:16.031 | 2025-10-16 02:55:16 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:16.108 | 2025-10-16 02:55:16 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:16.109 | 2025-10-16 02:55:16 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:16.109 | 2025-10-16 02:55:16 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:16.173 | 2025-10-16 02:55:16 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:16.175 | 2025-10-16 02:55:16 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:16.175 | 2025-10-16 02:55:16 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:16.237 | 2025-10-16 02:55:16 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:16.239 | 2025-10-16 02:55:16 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:16.239 | 2025-10-16 02:55:16 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:16.298 | 2025-10-16 02:55:16 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:16.299 | 2025-10-16 02:55:16 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:16.299 | 2025-10-16 02:55:16 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:16.345 | 2025-10-16 02:55:16 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:16.346 | 2025-10-16 02:55:16 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:16.346 | 2025-10-16 02:55:16 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:16.391 | 2025-10-16 02:55:16 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:16.392 | 2025-10-16 02:55:16 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:16.392 | 2025-10-16 02:55:16 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:16.443 | 2025-10-16 02:55:16 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:16.444 | 2025-10-16 02:55:16 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:16.444 | 2025-10-16 02:55:16 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:16.505 | 2025-10-16 02:55:16 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:16.506 | 2025-10-16 02:55:16 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:16.506 | 2025-10-16 02:55:16 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:16.555 | 2025-10-16 02:55:16 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:16.556 | 2025-10-16 02:55:16 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:16.556 | 2025-10-16 02:55:16 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:16.605 | 2025-10-16 02:55:16 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:16.605 | 2025-10-16 02:55:16 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:16.605 | 2025-10-16 02:55:16 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:16.655 | 2025-10-16 02:55:16 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:16.656 | 2025-10-16 02:55:16 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:16.656 | 2025-10-16 02:55:16 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:16.701 | 2025-10-16 02:55:16 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:16.701 | 2025-10-16 02:55:16 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:16.701 | 2025-10-16 02:55:16 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:16.753 | 2025-10-16 02:55:16 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:16.754 | 2025-10-16 02:55:16 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:16.754 | 2025-10-16 02:55:16 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:16.806 | 2025-10-16 02:55:16 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:16.806 | 2025-10-16 02:55:16 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:16.806 | 2025-10-16 02:55:16 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:16.872 | 2025-10-16 02:55:16 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:16.873 | 2025-10-16 02:55:16 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:16.873 | 2025-10-16 02:55:16 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:16.948 | 2025-10-16 02:55:16 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:16.949 | 2025-10-16 02:55:16 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:16.949 | 2025-10-16 02:55:16 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:17.026 | 2025-10-16 02:55:17 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:17.028 | 2025-10-16 02:55:17 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:17.028 | 2025-10-16 02:55:17 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:17.081 | 2025-10-16 02:55:17 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:17.082 | 2025-10-16 02:55:17 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:17.082 | 2025-10-16 02:55:17 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:17.128 | 2025-10-16 02:55:17 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:17.129 | 2025-10-16 02:55:17 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:17.129 | 2025-10-16 02:55:17 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:17.181 | 2025-10-16 02:55:17 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:17.182 | 2025-10-16 02:55:17 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:17.182 | 2025-10-16 02:55:17 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:17.245 | 2025-10-16 02:55:17 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:17.246 | 2025-10-16 02:55:17 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:17.246 | 2025-10-16 02:55:17 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:17.295 | 2025-10-16 02:55:17 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:17.296 | 2025-10-16 02:55:17 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:17.296 | 2025-10-16 02:55:17 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:17.380 | 2025-10-16 02:55:17 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:17.381 | 2025-10-16 02:55:17 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:17.381 | 2025-10-16 02:55:17 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:17.436 | 2025-10-16 02:55:17 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:17.437 | 2025-10-16 02:55:17 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:17.437 | 2025-10-16 02:55:17 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:17.485 | 2025-10-16 02:55:17 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:17.486 | 2025-10-16 02:55:17 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:17.486 | 2025-10-16 02:55:17 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:17.539 | 2025-10-16 02:55:17 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:17.540 | 2025-10-16 02:55:17 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:17.540 | 2025-10-16 02:55:17 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:17.590 | 2025-10-16 02:55:17 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:17.591 | 2025-10-16 02:55:17 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:17.591 | 2025-10-16 02:55:17 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:17.640 | 2025-10-16 02:55:17 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:17.641 | 2025-10-16 02:55:17 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:17.641 | 2025-10-16 02:55:17 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:17.709 | 2025-10-16 02:55:17 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:17.709 | 2025-10-16 02:55:17 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:17.709 | 2025-10-16 02:55:17 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:17.776 | 2025-10-16 02:55:17 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:17.777 | 2025-10-16 02:55:17 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:17.777 | 2025-10-16 02:55:17 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:17.845 | 2025-10-16 02:55:17 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:17.846 | 2025-10-16 02:55:17 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:17.846 | 2025-10-16 02:55:17 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:17.937 | 2025-10-16 02:55:17 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:17.938 | 2025-10-16 02:55:17 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:17.938 | 2025-10-16 02:55:17 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:17.986 | 2025-10-16 02:55:17 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:17.987 | 2025-10-16 02:55:17 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:17.987 | 2025-10-16 02:55:17 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:18.040 | 2025-10-16 02:55:18 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:18.041 | 2025-10-16 02:55:18 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:18.041 | 2025-10-16 02:55:18 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:18.094 | 2025-10-16 02:55:18 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:18.095 | 2025-10-16 02:55:18 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:18.095 | 2025-10-16 02:55:18 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:18.147 | 2025-10-16 02:55:18 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:18.147 | 2025-10-16 02:55:18 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:18.147 | 2025-10-16 02:55:18 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:18.193 | 2025-10-16 02:55:18 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:18.194 | 2025-10-16 02:55:18 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:18.194 | 2025-10-16 02:55:18 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:18.265 | 2025-10-16 02:55:18 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:18.266 | 2025-10-16 02:55:18 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:18.266 | 2025-10-16 02:55:18 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:18.319 | 2025-10-16 02:55:18 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:18.321 | 2025-10-16 02:55:18 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:18.321 | 2025-10-16 02:55:18 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:18.368 | 2025-10-16 02:55:18 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.dfb181bd-eeff-40d9-be8f-6add2f7c5093 "HTTP/2 200 OK"
2025-10-16 13:55:18.368 | 2025-10-16 02:55:18 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:18.368 | 2025-10-16 02:55:18 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:18.429 | --- Logging error ---
2025-10-16 13:55:18.429 | 2025-10-16 02:55:18 ERROR src.storage.supabase_client: Failed to get conversation dfb181bd-eeff-40d9-be8f-6add2f7c5093: maximum recursion depth exceeded
2025-10-16 13:55:18.429 | 2025-10-16 02:55:18 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:18.429 | 2025-10-16 02:55:18 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:18.429 | 2025-10-16 02:55:18 ERROR src.storage.supabase_client: Failed to get conversation dfb181bd-eeff-40d9-be8f-6add2f7c5093: maximum recursion depth exceeded
2025-10-16 13:55:18.429 | 2025-10-16 02:55:18 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:18.430 | 2025-10-16 02:55:18 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:18.430 | 2025-10-16 02:55:18 ERROR src.storage.supabase_client: Failed to get conversation dfb181bd-eeff-40d9-be8f-6add2f7c5093: maximum recursion depth exceeded
2025-10-16 13:55:18.430 | --- Logging error ---
2025-10-16 13:55:18.430 | 2025-10-16 02:55:18 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:18.430 | 2025-10-16 02:55:18 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:18.430 | 2025-10-16 02:55:18 ERROR src.storage.supabase_client: Failed to get conversation dfb181bd-eeff-40d9-be8f-6add2f7c5093: maximum recursion depth exceeded
2025-10-16 13:55:18.430 | 2025-10-16 02:55:18 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:18.430 | 2025-10-16 02:55:18 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory)
2025-10-16 13:55:18.431 | 2025-10-16 02:55:18 ERROR src.storage.supabase_client: Failed to get conversation dfb181bd-eeff-40d9-be8f-6add2f7c5093: maximum recursion depth exceeded
2025-10-16 13:55:18.431 | 2025-10-16 02:55:18 ERROR ws_daemon: === TOOL CALL FAILED ===
2025-10-16 13:55:18.431 | 2025-10-16 02:55:18 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-16 13:55:18.431 | 2025-10-16 02:55:18 INFO utils.infrastructure.storage_backend: In-memory storage initialized with 24h timeout, cleanup every 144m
2025-10-16 13:55:18.431 | 2025-10-16 02:55:18 INFO utils.infrastructure.storage_backend: Initialized in-memory conversation storage
2025-10-16 13:55:18.431 | 2025-10-16 02:55:18 WARNING src.server.context.thread_context: Thread not found: dfb181bd-eeff-40d9-be8f-6add2f7c5093
2025-10-16 13:55:18.431 | 2025-10-16 02:55:18 INFO mcp_activity: CONVERSATION_ERROR: Thread dfb181bd-eeff-40d9-be8f-6add2f7c5093 not found or expired
2025-10-16 13:55:18.432 | 2025-10-16 02:55:18 ERROR ws_daemon: Tool: chat
2025-10-16 13:55:18.432 | 2025-10-16 02:55:18 ERROR ws_daemon: Duration: 20.78s
2025-10-16 13:55:18.432 | 2025-10-16 02:55:18 ERROR ws_daemon: Session: 51da5b3e-3b0e-428d-84ce-286afa858595
2025-10-16 13:55:18.432 | 2025-10-16 02:55:18 ERROR ws_daemon: Request ID: 049addbf-a653-489a-965e-fd79d20f72bf
2025-10-16 13:55:18.432 | 2025-10-16 02:55:18 ERROR ws_daemon: Error: Conversation thread 'dfb181bd-eeff-40d9-be8f-6add2f7c5093' was not found or has expired. This may happen if the conversation was created more than 3 hours ago or if the server was restarted. Please restart the conversation by providing your full question/prompt without the continuation_id parameter. This will create a new conversation thread that can continue with follow-up exchanges.
2025-10-16 13:55:18.437 | 2025-10-16 02:55:18 ERROR ws_daemon: Full traceback:
2025-10-16 13:55:18.437 | Traceback (most recent call last):
2025-10-16 13:55:18.437 |   File "/app/src/daemon/ws_server.py", line 659, in _handle_message
2025-10-16 13:55:18.437 |     outputs = await asyncio.wait_for(tool_task, timeout=PROGRESS_INTERVAL)
2025-10-16 13:55:18.437 |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-10-16 13:55:18.437 |   File "/usr/local/lib/python3.13/asyncio/tasks.py", line 507, in wait_for
2025-10-16 13:55:18.437 |     return await fut
2025-10-16 13:55:18.437 |            ^^^^^^^^^
2025-10-16 13:55:18.437 |   File "/app/src/server/handlers/request_handler.py", line 86, in handle_call_tool
2025-10-16 13:55:18.437 |     arguments = await reconstruct_context(name, arguments, req_id)
2025-10-16 13:55:18.437 |                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-10-16 13:55:18.437 |   File "/app/src/server/handlers/request_handler_context.py", line 53, in reconstruct_context
2025-10-16 13:55:18.437 |     arguments = await reconstruct_thread_context(arguments)
2025-10-16 13:55:18.437 |                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-10-16 13:55:18.437 |   File "/app/src/server/context/thread_context.py", line 115, in reconstruct_thread_context
2025-10-16 13:55:18.437 |     raise ValueError(
2025-10-16 13:55:18.437 |     ...<6 lines>...
2025-10-16 13:55:18.437 |     )
2025-10-16 13:55:18.437 | ValueError: Conversation thread 'dfb181bd-eeff-40d9-be8f-6add2f7c5093' was not found or has expired. This may happen if the conversation was created more than 3 hours ago or if the server was restarted. Please restart the conversation by providing your full question/prompt without the continuation_id parameter. This will create a new conversation thread that can continue with follow-up exchanges.
2025-10-16 13:55:18.437 | 2025-10-16 02:55:18 ERROR ws_daemon: === END ===