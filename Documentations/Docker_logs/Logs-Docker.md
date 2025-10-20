2025-10-20 18:49:20.540 | 2025-10-20 18:49:20 INFO root: [ASYNC_LOGGING] Async-safe logging configured successfully
2025-10-20 18:49:20.540 | 2025-10-20 18:49:20 INFO root: [LOGGING] Configured websockets library logging to suppress handshake noise
2025-10-20 18:49:20.540 | 2025-10-20 18:49:20 INFO ws_daemon: [AUTH] Authentication enabled (token first 10 chars): test-token...
2025-10-20 18:49:21.523 | 2025-10-20 18:49:21 INFO src.bootstrap.singletons: Building tool registry (first-time initialization)
2025-10-20 18:49:21.963 | 2025-10-20 18:49:21 INFO src.bootstrap.singletons: Tool registry built successfully with 30 tools
2025-10-20 18:49:21.963 | 2025-10-20 18:49:21 INFO src.daemon.session_manager: [SESSION_MANAGER] Initialized with timeout=3600s, max_sessions=5, cleanup_interval=300s
2025-10-20 18:49:21.979 | 2025-10-20 18:49:21 INFO src.middleware.correlation: [CORRELATION] Correlation ID logging configured
2025-10-20 18:49:21.979 | 2025-10-20 18:49:21 INFO __main__: [MAIN] Correlation ID logging configured
2025-10-20 18:49:21.979 | 2025-10-20 18:49:21 INFO src.daemon.monitoring_endpoint: [MONITORING] Broadcast hook installed
2025-10-20 18:49:21.979 | 2025-10-20 18:49:21 INFO __main__: [MAIN] Monitoring broadcast hook configured
2025-10-20 18:49:21.997 | 2025-10-20 18:49:21 INFO src.monitoring.metrics: [METRICS] Prometheus metrics server started on port 8000
2025-10-20 18:49:21.997 | 2025-10-20 18:49:21 INFO src.monitoring.metrics: [METRICS] Metrics available at http://localhost:8000/metrics
2025-10-20 18:49:21.997 | 2025-10-20 18:49:21 INFO __main__: [MAIN] Metrics server started on port 8000
2025-10-20 18:49:21.997 | 2025-10-20 18:49:21 INFO __main__: [MAIN] Monitoring dashboard will be available at http://localhost:8080/monitoring_dashboard.html
2025-10-20 18:49:21.997 | 2025-10-20 18:49:21 INFO __main__: [MAIN] Health check will be available at http://localhost:8082/health
2025-10-20 18:49:21.997 | 2025-10-20 18:49:21 INFO __main__: [MAIN] Periodic metrics updates enabled (60s interval)
2025-10-20 18:49:21.997 | 2025-10-20 18:49:21 INFO __main__: [MAIN] Starting 4 servers concurrently
2025-10-20 18:49:21.998 | 2025-10-20 18:49:21 WARNING ws_daemon: Stale PID file or no active listener detected; removing /app/logs/ws_daemon.pid
2025-10-20 18:49:22.001 | 2025-10-20 18:49:22 INFO src.bootstrap.singletons: Configuring providers (first-time initialization)
2025-10-20 18:49:22.001 | 2025-10-20 18:49:22 INFO src.server.providers.provider_detection: Kimi API key found - Moonshot AI models available
2025-10-20 18:49:22.001 | 2025-10-20 18:49:22 INFO src.server.providers.provider_detection: GLM API key found - ZhipuAI models available
2025-10-20 18:49:22.001 | 2025-10-20 18:49:22 INFO src.server.providers.provider_diagnostics: Available providers: Kimi, GLM
2025-10-20 18:49:22.001 | 2025-10-20 18:49:22 INFO src.providers.kimi: Kimi provider using centralized timeout: 240s
2025-10-20 18:49:22.001 | 2025-10-20 18:49:22 INFO root: Model allow-list not configured for OpenAI Compatible - all models permitted. To restrict access, set KIMI_ALLOWED_MODELS with comma-separated model names.
2025-10-20 18:49:22.001 | 2025-10-20 18:49:22 INFO ws_daemon: Configuring providers and registering tools at daemon startup...
2025-10-20 18:49:22.002 | 2025-10-20 18:49:22 INFO root: Using extended timeouts for custom endpoint: https://api.moonshot.ai/v1
2025-10-20 18:49:22.122 | 2025-10-20 18:49:22 INFO src.providers.glm: GLM provider using SDK with base_url=https://api.z.ai/api/paas/v4, timeout=120s, max_retries=3
2025-10-20 18:49:22.122 | 2025-10-20 18:49:22 INFO src.server.providers.provider_diagnostics: Providers configured: KIMI, GLM; GLM models: 6; Kimi models: 18
2025-10-20 18:49:22.128 | 2025-10-20 18:49:22 INFO src.server.providers.provider_restrictions: No model restrictions configured - all models allowed
2025-10-20 18:49:22.128 | 2025-10-20 18:49:22 INFO src.bootstrap.singletons: Providers configured successfully
2025-10-20 18:49:22.128 | 2025-10-20 18:49:22 INFO ws_daemon: Providers configured successfully. Total tools available: 30
2025-10-20 18:49:22.129 | 2025-10-20 18:49:22 INFO ws_daemon: Initializing conversation storage at daemon startup...
2025-10-20 18:49:22.133 | 2025-10-20 18:49:22 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Initializing conversation storage at startup...
2025-10-20 18:49:22.133 | 2025-10-20 18:49:22 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-20 18:49:22.257 | 2025-10-20 18:49:22 INFO src.storage.supabase_client: [SUPABASE_INIT] SUPABASE_URL=SET
2025-10-20 18:49:22.257 | 2025-10-20 18:49:22 INFO src.storage.supabase_client: [SUPABASE_INIT] SUPABASE_SERVICE_ROLE_KEY=SET
2025-10-20 18:49:22.257 | 2025-10-20 18:49:22 INFO src.storage.supabase_client: Supabase storage initialized: https://mxaazuhlqewmkweewyaz.supabase.co
2025-10-20 18:49:22.638 | 2025-10-20 18:49:22 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/schema_version?select=version&limit=1 "HTTP/2 200 OK"
2025-10-20 18:49:22.640 | 2025-10-20 18:49:22 INFO utils.caching.base_cache_manager: [CONVERSATION_CACHE] L1 initialized: TTLCache(maxsize=100, ttl=300s)
2025-10-20 18:49:22.640 | 2025-10-20 18:49:22 INFO utils.caching.base_cache_manager: [CONVERSATION_CACHE] Base cache manager initialized
2025-10-20 18:49:22.640 | 2025-10-20 18:49:22 INFO utils.conversation.cache_manager: [CACHE_MANAGER] Conversation cache manager initialized (L1_TTL=300s, L2_TTL=1800s)
2025-10-20 18:49:22.640 | 2025-10-20 18:49:22 INFO utils.conversation.supabase_memory: [ASYNC_SUPABASE] Will use async queue for writes
2025-10-20 18:49:22.640 | 2025-10-20 18:49:22 INFO utils.infrastructure.storage_backend: Redis storage initialized (ttl=86400s) at redis://:****@redis:6379/0
2025-10-20 18:49:22.640 | 2025-10-20 18:49:22 INFO utils.infrastructure.storage_backend: Initialized Redis conversation storage
2025-10-20 18:49:22.640 | 2025-10-20 18:49:22 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory) with context engineering
2025-10-20 18:49:22.640 | 2025-10-20 18:49:22 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Singleton storage instance created: DualStorageConversation
2025-10-20 18:49:22.640 | 2025-10-20 18:49:22 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Startup initialization complete: DualStorageConversation
2025-10-20 18:49:22.640 | 2025-10-20 18:49:22 INFO ws_daemon: Conversation storage initialized successfully
2025-10-20 18:49:22.640 | 2025-10-20 18:49:22 INFO ws_daemon: Pre-warming external connections...
2025-10-20 18:49:22.645 | 2025-10-20 18:49:22 INFO src.daemon.warmup: [WARMUP] ========================================
2025-10-20 18:49:22.645 | 2025-10-20 18:49:22 INFO src.daemon.warmup: [WARMUP] Starting connection warmup...
2025-10-20 18:49:22.646 | 2025-10-20 18:49:22 INFO src.daemon.warmup: [WARMUP] ========================================
2025-10-20 18:49:22.646 | 2025-10-20 18:49:22 INFO src.daemon.monitoring_endpoint: [MONITORING] Starting monitoring server on 0.0.0.0:8080
2025-10-20 18:49:22.646 | 2025-10-20 18:49:22 INFO src.monitoring.metrics: [METRICS] Starting periodic updates (interval: 60s)
2025-10-20 18:49:22.747 | 2025-10-20 18:49:22 INFO src.daemon.warmup: [WARMUP] Initializing Supabase connection...
2025-10-20 18:49:22.831 | 2025-10-20 18:49:22 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=id&limit=1 "HTTP/2 200 OK"
2025-10-20 18:49:22.832 | 2025-10-20 18:49:22 INFO src.daemon.warmup: [WARMUP] ✅ Supabase connection warmed up successfully (0.084s)
2025-10-20 18:49:22.832 | 2025-10-20 18:49:22 INFO src.daemon.warmup: [WARMUP] Initializing Redis connection...
2025-10-20 18:49:22.843 | 2025-10-20 18:49:22 INFO src.daemon.monitoring_endpoint: [MONITORING] Monitoring server running on ws://0.0.0.0:8080
2025-10-20 18:49:22.843 | 2025-10-20 18:49:22 INFO src.daemon.monitoring_endpoint: [MONITORING] Dashboard available at http://0.0.0.0:8080/monitoring_dashboard.html
2025-10-20 18:49:22.843 | 2025-10-20 18:49:22 INFO src.daemon.health_endpoint: [HEALTH] Health check server running on http://0.0.0.0:8082/health
2025-10-20 18:49:22.845 | 2025-10-20 18:49:22 INFO src.daemon.warmup: [WARMUP] ✅ Redis connection warmed up successfully (0.013s)
2025-10-20 18:49:22.845 | 2025-10-20 18:49:22 INFO src.daemon.warmup: [WARMUP] ========================================
2025-10-20 18:49:22.845 | 2025-10-20 18:49:22 INFO src.daemon.warmup: [WARMUP] ✅ All connections warmed up successfully (0.199s)
2025-10-20 18:49:22.845 | 2025-10-20 18:49:22 INFO src.daemon.warmup: [WARMUP] ========================================
2025-10-20 18:49:22.845 | 2025-10-20 18:49:22 INFO ws_daemon: External connections pre-warmed successfully
2025-10-20 18:49:22.845 | 2025-10-20 18:49:22 INFO ws_daemon: Initializing conversation queue...
2025-10-20 18:49:22.850 | 2025-10-20 18:49:22 INFO src.daemon.conversation_queue: [CONV_QUEUE] Consumer started (max_size=1000, warning_threshold=500)
2025-10-20 18:49:22.850 | 2025-10-20 18:49:22 INFO src.daemon.conversation_queue: [CONV_QUEUE] Global queue initialized
2025-10-20 18:49:22.850 | 2025-10-20 18:49:22 INFO ws_daemon: Conversation queue initialized successfully
2025-10-20 18:49:22.851 | 2025-10-20 18:49:22 INFO ws_daemon: Initializing session semaphore manager...
2025-10-20 18:49:22.856 | 2025-10-20 18:49:22 INFO src.daemon.session_semaphore_manager: [SESSION_SEM] Initialized SessionSemaphoreManager (max_concurrent_per_session=1, cleanup_interval=300s, inactive_timeout=300s)
2025-10-20 18:49:22.856 | 2025-10-20 18:49:22 INFO src.daemon.session_semaphore_manager: [SESSION_SEM] Cleanup task started
2025-10-20 18:49:22.856 | 2025-10-20 18:49:22 INFO src.daemon.session_semaphore_manager: [SESSION_SEM] Global session semaphore manager initialized (max_concurrent_per_conversation=1)
2025-10-20 18:49:22.856 | 2025-10-20 18:49:22 INFO src.monitoring.resilient_websocket: Started retry background task
2025-10-20 18:49:22.856 | 2025-10-20 18:49:22 INFO src.monitoring.resilient_websocket: Started cleanup background task
2025-10-20 18:49:22.856 | 2025-10-20 18:49:22 INFO ws_daemon: Session semaphore manager initialized successfully
2025-10-20 18:49:22.856 | 2025-10-20 18:49:22 INFO ws_daemon: Validating timeout hierarchy...
2025-10-20 18:49:22.856 | 2025-10-20 18:49:22 INFO ws_daemon: Timeout hierarchy validated: daemon=270s, tool=180.0s (ratio=1.50x)
2025-10-20 18:49:22.856 | 2025-10-20 18:49:22 INFO ws_daemon: [RESILIENT_WS] Started resilient WebSocket manager with background tasks
2025-10-20 18:49:22.857 | 2025-10-20 18:49:22 INFO ws_daemon: Starting WS daemon on ws://0.0.0.0:8079
2025-10-20 18:49:22.863 | 2025-10-20 18:49:22 INFO src.daemon.conversation_queue: [CONV_QUEUE] Consumer loop started
2025-10-20 18:49:22.863 | 2025-10-20 18:49:22 INFO src.daemon.session_semaphore_manager: [SESSION_SEM] Cleanup task started
2025-10-20 18:49:22.863 | 2025-10-20 18:49:22 INFO src.monitoring.resilient_websocket: Starting pending message retry task
2025-10-20 18:49:22.863 | 2025-10-20 18:49:22 INFO src.monitoring.resilient_websocket: Starting expired message cleanup task
2025-10-20 18:49:23.245 | 2025-10-20 18:49:23 INFO src.daemon.connection_manager: ConnectionManager initialized: max_connections=1000, max_per_ip=10
2025-10-20 18:49:23.245 | 2025-10-20 18:49:23 INFO src.daemon.connection_manager: Connection registered: db8a403f-a11b-4989-9ceb-9c41abe5e64d from 172.18.0.1 (total: 1, ip_total: 1)
2025-10-20 18:49:23.245 | 2025-10-20 18:49:23 INFO ws_daemon: [WS_CONNECTION] New connection from 172.18.0.1:57576 (id: db8a403f-a11b-4989-9ceb-9c41abe5e64d)
2025-10-20 18:49:23.246 | 2025-10-20 18:49:23 INFO src.daemon.session_manager: [SESSION_MANAGER] Created session fc61f73c-a117-4d28-adec-3b436a0efc1a (total sessions: 1)
2025-10-20 18:49:23.247 | 2025-10-20 18:49:23 INFO src.resilience.rate_limiter: RateLimiter initialized: global=1000/100.0t/s, ip=100/10.0t/s, user=50/5.0t/s, cleanup_interval=3600s
2025-10-20 18:49:23.247 | 2025-10-20 18:49:23 INFO ws_daemon: === TOOL CALL RECEIVED ===
2025-10-20 18:49:23.247 | 2025-10-20 18:49:23 INFO ws_daemon: Session: fc61f73c-a117-4d28-adec-3b436a0efc1a
2025-10-20 18:49:23.247 | 2025-10-20 18:49:23 INFO ws_daemon: Tool: chat (original: chat)
2025-10-20 18:49:23.247 | 2025-10-20 18:49:23 INFO ws_daemon: Request ID: f8098b1c-977f-4d88-b6dd-33a494d12e6c
2025-10-20 18:49:23.248 | 2025-10-20 18:49:23 INFO ws_daemon: Arguments (first 500 chars): {
2025-10-20 18:49:23.248 |   "prompt": "Test message with continuation to check if message arrays work",
2025-10-20 18:49:23.248 |   "continuation_id": "5dff8e35-3b2c-4954-b40c-fa54e8ea292a",
2025-10-20 18:49:23.248 |   "model": "glm-4.6",
2025-10-20 18:49:23.248 |   "use_websearch": false
2025-10-20 18:49:23.248 | }
2025-10-20 18:49:23.248 | 2025-10-20 18:49:23 INFO ws_daemon: === PROCESSING ===
2025-10-20 18:49:23.249 | 2025-10-20 18:49:23 INFO src.server.handlers.request_handler_init: MCP tool call: chat req_id=03de832c-ccf8-4f56-84c1-22d6e7b40732
2025-10-20 18:49:23.253 | 2025-10-20 18:49:23 INFO mcp_activity: TOOL_CALL: chat with 6 arguments req_id=03de832c-ccf8-4f56-84c1-22d6e7b40732
2025-10-20 18:49:23.257 | 2025-10-20 18:49:23 INFO src.server.handlers.request_handler: MCP tool call: chat req_id=03de832c-ccf8-4f56-84c1-22d6e7b40732
2025-10-20 18:49:23.257 | 2025-10-20 18:49:23 INFO mcp_activity: CONVERSATION_RESUME: chat resuming thread 5dff8e35-3b2c-4954-b40c-fa54e8ea292a req_id=03de832c-ccf8-4f56-84c1-22d6e7b40732
2025-10-20 18:49:23.257 | 2025-10-20 18:49:23 INFO utils.conversation.threads: [STORAGE_INTEGRATION] Storage factory available - will use configured backend
2025-10-20 18:49:23.257 | 2025-10-20 18:49:23 INFO utils.conversation.threads: [STORAGE_INTEGRATION] Created cached storage backend instance
2025-10-20 18:49:23.259 | 2025-10-20 18:49:23 INFO utils.caching.base_cache_manager: [CONVERSATION_CACHE] L2 (Redis) connected: redis:6379/0
2025-10-20 18:49:23.377 | 2025-10-20 18:49:23 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.5dff8e35-3b2c-4954-b40c-fa54e8ea292a "HTTP/2 200 OK"
2025-10-20 18:49:23.379 | 2025-10-20 18:49:23 INFO utils.performance.timing: [TIMING] SupabaseMemory.get_conversation_by_continuation_id took 0.119s
2025-10-20 18:49:23.427 | 2025-10-20 18:49:23 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/messages?select=%2A&conversation_id=eq.576ca1c1-cf56-4bc1-98a3-6d41b20f330c&order=created_at.asc&limit=5 "HTTP/2 200 OK"
2025-10-20 18:49:23.428 | 2025-10-20 18:49:23 INFO utils.performance.timing: [TIMING] SupabaseMemory.get_conversation_messages took 0.049s
2025-10-20 18:49:23.428 | 2025-10-20 18:49:23 INFO utils.conversation.supabase_memory: [CONTEXT_PRUNING] Loaded 5 messages for 5dff8e35-3b2c-4954-b40c-fa54e8ea292a (limit=5)
2025-10-20 18:49:23.430 | 2025-10-20 18:49:23 INFO utils.performance.timing: [TIMING] SupabaseMemory.get_thread completed in 0.173s
2025-10-20 18:49:23.430 | 2025-10-20 18:49:23 INFO utils.performance.timing: [TIMING] SupabaseMemory.get_thread completed in 0.000s
2025-10-20 18:49:26.292 | 2025-10-20 18:49:26 INFO utils.conversation.supabase_memory: [ASYNC_SUPABASE] Submitting write to async queue for 5dff8e35-3b2c-4954-b40c-fa54e8ea292a
2025-10-20 18:49:26.292 | 2025-10-20 18:49:26 INFO utils.conversation.supabase_memory: [ASYNC_SUPABASE] Queued write for 5dff8e35-3b2c-4954-b40c-fa54e8ea292a
2025-10-20 18:49:26.292 | 2025-10-20 18:49:26 INFO utils.performance.timing: [TIMING] SupabaseMemory.add_turn completed in 0.000s
2025-10-20 18:49:26.295 | 2025-10-20 18:49:26 INFO src.server.context.thread_context: [MESSAGE_ARRAY] Building message array for thread 5dff8e35-3b2c-4954-b40c-fa54e8ea292a
2025-10-20 18:49:26.295 | 2025-10-20 18:49:26 INFO src.server.context.thread_context: [MESSAGE_ARRAY] Thread has 5 turns, tool: chat
2025-10-20 18:49:26.295 | 2025-10-20 18:49:26 INFO utils.performance.timing: [TIMING] SupabaseMemory.get_thread completed in 0.000s
2025-10-20 18:49:26.295 | 2025-10-20 18:49:26 INFO utils.conversation.supabase_memory: [MESSAGE_ARRAY] Built array for 5dff8e35-3b2c-4954-b40c-fa54e8ea292a: 5 messages
2025-10-20 18:49:26.295 | 2025-10-20 18:49:26 INFO src.server.context.thread_context: [MESSAGE_ARRAY] Message array built: 5 messages
2025-10-20 18:49:26.295 | 2025-10-20 18:49:26 INFO src.server.context.thread_context: [MESSAGE_ARRAY] Message array tokens: ~449
2025-10-20 18:49:26.295 | 2025-10-20 18:49:26 INFO src.server.context.thread_context: Reconstructed context for thread 5dff8e35-3b2c-4954-b40c-fa54e8ea292a (turn 5)
2025-10-20 18:49:26.295 | 2025-10-20 18:49:26 INFO mcp_activity: CONVERSATION_CONTINUATION: Thread 5dff8e35-3b2c-4954-b40c-fa54e8ea292a turn 5 - 5 previous turns loaded
2025-10-20 18:49:26.364 | 2025-10-20 18:49:26 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.5dff8e35-3b2c-4954-b40c-fa54e8ea292a "HTTP/2 200 OK"
2025-10-20 18:49:26.444 | 2025-10-20 18:49:26 INFO httpx: HTTP Request: POST https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/messages "HTTP/2 201 Created"
2025-10-20 18:49:26.446 | 2025-10-20 18:49:26 INFO utils.conversation.supabase_memory: [CONV_QUEUE] Processed update for 5dff8e35-3b2c-4954-b40c-fa54e8ea292a
2025-10-20 18:49:26.446 | 2025-10-20 18:49:26 INFO mcp_activity: [PROGRESS] tool=chat req_id=03de832c-ccf8-4f56-84c1-22d6e7b40732 elapsed=0.2s — heartbeat
2025-10-20 18:49:26.446 | 2025-10-20 18:49:26 INFO tools.chat: chat tool called with arguments: ['prompt', 'continuation_id', 'model', 'use_websearch', '_session_id', '_call_key', '_messages', '_original_user_prompt', '_remaining_tokens', '_model_context', '_resolved_model_name', '_today']
2025-10-20 18:49:26.446 | 2025-10-20 18:49:26 INFO mcp_activity: [PROGRESS] chat: Starting execution
2025-10-20 18:49:26.446 | 2025-10-20 18:49:26 INFO mcp_activity: [PROGRESS] chat: Request validated
2025-10-20 18:49:26.463 | 2025-10-20 18:49:26 INFO mcp_activity: [PROGRESS] chat: Model/context ready: glm-4.6
2025-10-20 18:49:26.640 | 2025-10-20 18:49:26 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.5dff8e35-3b2c-4954-b40c-fa54e8ea292a "HTTP/2 200 OK"
2025-10-20 18:49:26.641 | 2025-10-20 18:49:26 INFO utils.performance.timing: [TIMING] SupabaseMemory.get_conversation_by_continuation_id took 0.178s
2025-10-20 18:49:26.714 | 2025-10-20 18:49:26 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/messages?select=%2A&conversation_id=eq.576ca1c1-cf56-4bc1-98a3-6d41b20f330c&order=created_at.asc&limit=5 "HTTP/2 200 OK"
2025-10-20 18:49:26.714 | 2025-10-20 18:49:26 INFO utils.performance.timing: [TIMING] SupabaseMemory.get_conversation_messages took 0.074s
2025-10-20 18:49:26.714 | 2025-10-20 18:49:26 INFO utils.conversation.supabase_memory: [CONTEXT_PRUNING] Loaded 5 messages for 5dff8e35-3b2c-4954-b40c-fa54e8ea292a (limit=5)
2025-10-20 18:49:26.715 | 2025-10-20 18:49:26 INFO utils.performance.timing: [TIMING] SupabaseMemory.get_thread completed in 0.252s
2025-10-20 18:49:26.749 | 2025-10-20 18:49:26 INFO utils.performance.timing: [TIMING] SupabaseMemory.get_thread completed in 0.000s
2025-10-20 18:49:26.750 | 2025-10-20 18:49:26 INFO utils.conversation.supabase_memory: [CONTEXT_PRUNING] BEFORE pruning: 5 messages, 1,800 chars, ~450 tokens
2025-10-20 18:49:26.750 | 2025-10-20 18:49:26 INFO utils.conversation.supabase_memory: [CONTEXT_PRUNING] AFTER pruning for 5dff8e35-3b2c-4954-b40c-fa54e8ea292a: 5/5 messages kept, 1,933 chars, ~483 tokens | Pruned 0 messages, removed 0 file contents, removed -133 chars (-7.4% reduction)
2025-10-20 18:49:26.750 | 2025-10-20 18:49:26 INFO utils.conversation.supabase_memory: [ASYNC_SUPABASE] Submitting write to async queue for 5dff8e35-3b2c-4954-b40c-fa54e8ea292a
2025-10-20 18:49:26.750 | 2025-10-20 18:49:26 INFO utils.conversation.supabase_memory: [ASYNC_SUPABASE] Queued write for 5dff8e35-3b2c-4954-b40c-fa54e8ea292a
2025-10-20 18:49:26.750 | 2025-10-20 18:49:26 INFO utils.performance.timing: [TIMING] SupabaseMemory.add_turn completed in 0.000s
2025-10-20 18:49:26.750 | 2025-10-20 18:49:26 INFO mcp_activity: [PROGRESS] chat: Generating response (~1,226 tokens)
2025-10-20 18:49:26.750 | 2025-10-20 18:49:26 INFO tools.chat: Sending request to glm API for chat
2025-10-20 18:49:26.750 | 2025-10-20 18:49:26 INFO tools.chat: Using model: glm-4.6 via glm provider
2025-10-20 18:49:26.769 | 2025-10-20 18:49:26 INFO src.providers.orchestration.websearch_adapter: [WEBSEARCH_DEBUG] provider_type=ProviderType.GLM, use_websearch=False, model_name=glm-4.6
2025-10-20 18:49:26.769 | 2025-10-20 18:49:26 INFO src.providers.orchestration.websearch_adapter: [WEBSEARCH_DEBUG] ws.tools=None, ws.tool_choice=None
2025-10-20 18:49:26.769 | 2025-10-20 18:49:26 INFO src.providers.orchestration.websearch_adapter: [WEBSEARCH_DEBUG] Final provider_kwargs keys: []
2025-10-20 18:49:26.779 | 2025-10-20 18:49:26 INFO utils.infrastructure.semantic_cache: Semantic cache initialized (TTL=600s, max_size=1000, max_response_size=1048576 bytes)
2025-10-20 18:49:26.779 | 2025-10-20 18:49:26 INFO utils.infrastructure.semantic_cache: Initialized global semantic cache (TTL=600s, max_size=1000, max_response_size=1048576 bytes)
2025-10-20 18:49:26.779 | 2025-10-20 18:49:26 INFO src.providers.glm_chat: GLM chat using SDK: model=glm-4.6, stream=True, messages_count=2
2025-10-20 18:49:36.611 | 2025-10-20 18:49:36 INFO httpx: HTTP Request: POST https://api.z.ai/api/paas/v4/chat/completions "HTTP/1.1 200 OK"
2025-10-20 18:49:41.139 | 2025-10-20 18:49:41 INFO tools.chat: Received response from glm API for chat
2025-10-20 18:49:41.139 | 2025-10-20 18:49:41 INFO mcp_activity: [PROGRESS] 📝 Processing response...
2025-10-20 18:49:41.144 | 2025-10-20 18:49:41 INFO utils.performance.timing: [TIMING] SupabaseMemory.get_thread completed in 0.000s
2025-10-20 18:49:41.144 | 2025-10-20 18:49:41 INFO utils.conversation.supabase_memory: [ASYNC_SUPABASE] Submitting write to async queue for 5dff8e35-3b2c-4954-b40c-fa54e8ea292a
2025-10-20 18:49:41.144 | 2025-10-20 18:49:41 INFO utils.conversation.supabase_memory: [ASYNC_SUPABASE] Queued write for 5dff8e35-3b2c-4954-b40c-fa54e8ea292a
2025-10-20 18:49:41.144 | 2025-10-20 18:49:41 INFO utils.performance.timing: [TIMING] SupabaseMemory.add_turn completed in 0.000s
2025-10-20 18:49:41.144 | 2025-10-20 18:49:41 INFO utils.performance.timing: [TIMING] SupabaseMemory.get_thread completed in 0.000s
2025-10-20 18:49:41.144 | 2025-10-20 18:49:41 INFO utils.conversation.supabase_memory: [ASYNC_SUPABASE] Submitting write to async queue for 5dff8e35-3b2c-4954-b40c-fa54e8ea292a
2025-10-20 18:49:41.144 | 2025-10-20 18:49:41 INFO utils.conversation.supabase_memory: [ASYNC_SUPABASE] Queued write for 5dff8e35-3b2c-4954-b40c-fa54e8ea292a
2025-10-20 18:49:41.144 | 2025-10-20 18:49:41 INFO utils.performance.timing: [TIMING] SupabaseMemory.add_turn completed in 0.000s
2025-10-20 18:49:41.146 | 2025-10-20 18:49:41 INFO utils.performance.timing: [TIMING] SupabaseMemory.get_thread completed in 0.000s
2025-10-20 18:49:41.146 | 2025-10-20 18:49:41 INFO tools.chat: chat tool completed successfully
2025-10-20 18:49:41.146 | 2025-10-20 18:49:41 INFO ws_daemon: [WS_PROGRESS_NOTIFIER] Called with message: chat: Starting execution, level: info
2025-10-20 18:49:41.147 | 2025-10-20 18:49:41 INFO ws_daemon: [WS_PROGRESS_NOTIFIER] Successfully sent progress + heartbeat frames
2025-10-20 18:49:41.147 | 2025-10-20 18:49:41 INFO ws_daemon: [WS_PROGRESS_NOTIFIER] Called with message: chat: Request validated, level: info
2025-10-20 18:49:41.147 | 2025-10-20 18:49:41 INFO ws_daemon: [WS_PROGRESS_NOTIFIER] Successfully sent progress + heartbeat frames
2025-10-20 18:49:41.147 | 2025-10-20 18:49:41 INFO ws_daemon: [WS_PROGRESS_NOTIFIER] Called with message: chat: Model/context ready: glm-4.6, level: info
2025-10-20 18:49:41.148 | 2025-10-20 18:49:41 INFO ws_daemon: [WS_PROGRESS_NOTIFIER] Successfully sent progress + heartbeat frames
2025-10-20 18:49:41.249 | 2025-10-20 18:49:41 INFO httpx: HTTP Request: POST https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/messages "HTTP/2 201 Created"
2025-10-20 18:49:41.252 | 2025-10-20 18:49:41 INFO utils.conversation.supabase_memory: [CONV_QUEUE] Processed update for 5dff8e35-3b2c-4954-b40c-fa54e8ea292a
2025-10-20 18:49:41.340 | 2025-10-20 18:49:41 INFO httpx: HTTP Request: POST https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/messages "HTTP/2 201 Created"
2025-10-20 18:49:41.341 | 2025-10-20 18:49:41 INFO utils.conversation.supabase_memory: [CONV_QUEUE] Processed update for 5dff8e35-3b2c-4954-b40c-fa54e8ea292a
2025-10-20 18:49:41.466 | 2025-10-20 18:49:41 INFO httpx: HTTP Request: POST https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/messages "HTTP/2 201 Created"
2025-10-20 18:49:41.467 | 2025-10-20 18:49:41 INFO utils.conversation.supabase_memory: [CONV_QUEUE] Processed update for 5dff8e35-3b2c-4954-b40c-fa54e8ea292a
2025-10-20 18:49:41.467 | 2025-10-20 18:49:41 INFO ws_daemon: [WS_PROGRESS_NOTIFIER] Called with message: chat: Generating response (~1,226 tokens), level: info
2025-10-20 18:49:41.467 | 2025-10-20 18:49:41 INFO ws_daemon: [WS_PROGRESS_NOTIFIER] Successfully sent progress + heartbeat frames
2025-10-20 18:49:41.468 | 2025-10-20 18:49:41 INFO ws_daemon: [WS_PROGRESS_NOTIFIER] Called with message: 📝 Processing response..., level: info
2025-10-20 18:49:41.468 | 2025-10-20 18:49:41 INFO ws_daemon: [WS_PROGRESS_NOTIFIER] Successfully sent progress + heartbeat frames
2025-10-20 18:49:41.469 | 2025-10-20 18:49:41 INFO mcp_activity: TOOL_CANCELLED: chat req_id=03de832c-ccf8-4f56-84c1-22d6e7b40732
2025-10-20 18:49:41.469 | 2025-10-20 18:49:41 INFO src.daemon.connection_manager: Connection unregistered: db8a403f-a11b-4989-9ceb-9c41abe5e64d from 172.18.0.1 (duration: 18.22s, remaining: 0)
2025-10-20 18:49:41.469 | 2025-10-20 18:49:41 INFO src.daemon.session_manager: [SESSION_MANAGER] Removed session fc61f73c-a117-4d28-adec-3b436a0efc1a (total sessions: 0)
2025-10-20 18:49:49.984 | 2025-10-20 18:49:49 INFO src.daemon.connection_manager: Connection registered: ae2008a6-9652-4fc7-acf2-6f872b8eabd3 from 172.18.0.1 (total: 1, ip_total: 1)
2025-10-20 18:49:49.984 | 2025-10-20 18:49:49 INFO ws_daemon: [WS_CONNECTION] New connection from 172.18.0.1:60246 (id: ae2008a6-9652-4fc7-acf2-6f872b8eabd3)
2025-10-20 18:49:49.984 | 2025-10-20 18:49:49 INFO src.daemon.session_manager: [SESSION_MANAGER] Created session db35f3ef-baec-48ec-a2af-90476a5f7e7b (total sessions: 1)
2025-10-20 18:49:49.985 | 2025-10-20 18:49:49 INFO ws_daemon: === TOOL CALL RECEIVED ===
2025-10-20 18:49:49.986 | 2025-10-20 18:49:49 INFO ws_daemon: Session: db35f3ef-baec-48ec-a2af-90476a5f7e7b
2025-10-20 18:49:49.986 | 2025-10-20 18:49:49 INFO ws_daemon: Tool: chat (original: chat)
2025-10-20 18:49:49.986 | 2025-10-20 18:49:49 INFO ws_daemon: Request ID: bdc29852-226e-4334-b66d-ad4af30dab3c
2025-10-20 18:49:49.987 | 2025-10-20 18:49:49 INFO ws_daemon: Arguments (first 500 chars): {
2025-10-20 18:49:49.987 |   "prompt": "This is a follow-up message to test if message arrays are working. Can you confirm you see the previous message in your context?",
2025-10-20 18:49:49.987 |   "continuation_id": "5dff8e35-3b2c-4954-b40c-fa54e8ea292a",
2025-10-20 18:49:49.987 |   "model": "glm-4.6",
2025-10-20 18:49:49.987 |   "use_websearch": true
2025-10-20 18:49:49.987 | }
2025-10-20 18:49:49.987 | 2025-10-20 18:49:49 INFO ws_daemon: === PROCESSING ===
2025-10-20 18:49:49.988 | 2025-10-20 18:49:49 INFO src.server.handlers.request_handler_init: MCP tool call: chat req_id=8c397c4c-70f1-40ac-a97b-c39d24a5823e
2025-10-20 18:49:49.988 | 2025-10-20 18:49:49 INFO mcp_activity: TOOL_CALL: chat with 6 arguments req_id=8c397c4c-70f1-40ac-a97b-c39d24a5823e
2025-10-20 18:49:49.988 | 2025-10-20 18:49:49 INFO src.server.handlers.request_handler: MCP tool call: chat req_id=8c397c4c-70f1-40ac-a97b-c39d24a5823e
2025-10-20 18:49:49.988 | 2025-10-20 18:49:49 INFO mcp_activity: CONVERSATION_RESUME: chat resuming thread 5dff8e35-3b2c-4954-b40c-fa54e8ea292a req_id=8c397c4c-70f1-40ac-a97b-c39d24a5823e
2025-10-20 18:49:50.076 | 2025-10-20 18:49:50 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.5dff8e35-3b2c-4954-b40c-fa54e8ea292a "HTTP/2 200 OK"
2025-10-20 18:49:50.077 | 2025-10-20 18:49:50 INFO utils.performance.timing: [TIMING] SupabaseMemory.get_conversation_by_continuation_id took 0.088s
2025-10-20 18:49:50.140 | 2025-10-20 18:49:50 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/messages?select=%2A&conversation_id=eq.576ca1c1-cf56-4bc1-98a3-6d41b20f330c&order=created_at.asc&limit=5 "HTTP/2 200 OK"
2025-10-20 18:49:50.140 | 2025-10-20 18:49:50 INFO utils.performance.timing: [TIMING] SupabaseMemory.get_conversation_messages took 0.064s
2025-10-20 18:49:50.140 | 2025-10-20 18:49:50 INFO utils.conversation.supabase_memory: [CONTEXT_PRUNING] Loaded 5 messages for 5dff8e35-3b2c-4954-b40c-fa54e8ea292a (limit=5)
2025-10-20 18:49:50.142 | 2025-10-20 18:49:50 INFO utils.performance.timing: [TIMING] SupabaseMemory.get_thread completed in 0.154s
2025-10-20 18:49:50.142 | 2025-10-20 18:49:50 INFO utils.performance.timing: [TIMING] SupabaseMemory.get_thread completed in 0.000s
2025-10-20 18:49:50.142 | 2025-10-20 18:49:50 INFO utils.conversation.supabase_memory: [ASYNC_SUPABASE] Submitting write to async queue for 5dff8e35-3b2c-4954-b40c-fa54e8ea292a
2025-10-20 18:49:50.142 | 2025-10-20 18:49:50 INFO utils.conversation.supabase_memory: [ASYNC_SUPABASE] Queued write for 5dff8e35-3b2c-4954-b40c-fa54e8ea292a
2025-10-20 18:49:50.142 | 2025-10-20 18:49:50 INFO utils.performance.timing: [TIMING] SupabaseMemory.add_turn completed in 0.000s
2025-10-20 18:49:50.144 | 2025-10-20 18:49:50 INFO src.server.context.thread_context: [MESSAGE_ARRAY] Building message array for thread 5dff8e35-3b2c-4954-b40c-fa54e8ea292a
2025-10-20 18:49:50.144 | 2025-10-20 18:49:50 INFO src.server.context.thread_context: [MESSAGE_ARRAY] Thread has 5 turns, tool: chat
2025-10-20 18:49:50.144 | 2025-10-20 18:49:50 INFO utils.performance.timing: [TIMING] SupabaseMemory.get_thread completed in 0.000s
2025-10-20 18:49:50.144 | 2025-10-20 18:49:50 INFO utils.conversation.supabase_memory: [MESSAGE_ARRAY] Built array for 5dff8e35-3b2c-4954-b40c-fa54e8ea292a: 5 messages
2025-10-20 18:49:50.144 | 2025-10-20 18:49:50 INFO src.server.context.thread_context: [MESSAGE_ARRAY] Message array built: 5 messages
2025-10-20 18:49:50.144 | 2025-10-20 18:49:50 INFO src.server.context.thread_context: [MESSAGE_ARRAY] Message array tokens: ~449
2025-10-20 18:49:50.144 | 2025-10-20 18:49:50 INFO src.server.context.thread_context: Reconstructed context for thread 5dff8e35-3b2c-4954-b40c-fa54e8ea292a (turn 5)
2025-10-20 18:49:50.144 | 2025-10-20 18:49:50 INFO mcp_activity: CONVERSATION_CONTINUATION: Thread 5dff8e35-3b2c-4954-b40c-fa54e8ea292a turn 5 - 5 previous turns loaded
2025-10-20 18:49:50.232 | 2025-10-20 18:49:50 INFO httpx: HTTP Request: POST https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/messages "HTTP/2 201 Created"
2025-10-20 18:49:50.233 | 2025-10-20 18:49:50 INFO utils.conversation.supabase_memory: [CONV_QUEUE] Processed update for 5dff8e35-3b2c-4954-b40c-fa54e8ea292a
2025-10-20 18:49:50.233 | 2025-10-20 18:49:50 INFO mcp_activity: [PROGRESS] tool=chat req_id=8c397c4c-70f1-40ac-a97b-c39d24a5823e elapsed=0.1s — heartbeat
2025-10-20 18:49:50.233 | 2025-10-20 18:49:50 INFO tools.chat: chat tool called with arguments: ['prompt', 'continuation_id', 'model', 'use_websearch', '_session_id', '_call_key', '_messages', '_original_user_prompt', '_remaining_tokens', '_model_context', '_resolved_model_name', '_today']
2025-10-20 18:49:50.233 | 2025-10-20 18:49:50 INFO mcp_activity: [PROGRESS] chat: Starting execution
2025-10-20 18:49:50.233 | 2025-10-20 18:49:50 INFO mcp_activity: [PROGRESS] chat: Request validated
2025-10-20 18:49:50.233 | 2025-10-20 18:49:50 INFO mcp_activity: [PROGRESS] chat: Model/context ready: glm-4.6
2025-10-20 18:49:50.344 | 2025-10-20 18:49:50 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.5dff8e35-3b2c-4954-b40c-fa54e8ea292a "HTTP/2 200 OK"
2025-10-20 18:49:50.345 | 2025-10-20 18:49:50 INFO utils.performance.timing: [TIMING] SupabaseMemory.get_conversation_by_continuation_id took 0.111s
2025-10-20 18:49:50.424 | 2025-10-20 18:49:50 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/messages?select=%2A&conversation_id=eq.576ca1c1-cf56-4bc1-98a3-6d41b20f330c&order=created_at.asc&limit=5 "HTTP/2 200 OK"
2025-10-20 18:49:50.424 | 2025-10-20 18:49:50 INFO utils.performance.timing: [TIMING] SupabaseMemory.get_conversation_messages took 0.080s
2025-10-20 18:49:50.424 | 2025-10-20 18:49:50 INFO utils.conversation.supabase_memory: [CONTEXT_PRUNING] Loaded 5 messages for 5dff8e35-3b2c-4954-b40c-fa54e8ea292a (limit=5)
2025-10-20 18:49:50.425 | 2025-10-20 18:49:50 INFO utils.performance.timing: [TIMING] SupabaseMemory.get_thread completed in 0.192s
2025-10-20 18:49:50.426 | 2025-10-20 18:49:50 INFO utils.performance.timing: [TIMING] SupabaseMemory.get_thread completed in 0.000s
2025-10-20 18:49:50.426 | 2025-10-20 18:49:50 INFO utils.conversation.supabase_memory: [CONTEXT_PRUNING] BEFORE pruning: 5 messages, 1,800 chars, ~450 tokens
2025-10-20 18:49:50.426 | 2025-10-20 18:49:50 INFO utils.conversation.supabase_memory: [CONTEXT_PRUNING] AFTER pruning for 5dff8e35-3b2c-4954-b40c-fa54e8ea292a: 5/5 messages kept, 1,933 chars, ~483 tokens | Pruned 0 messages, removed 0 file contents, removed -133 chars (-7.4% reduction)
2025-10-20 18:49:50.426 | 2025-10-20 18:49:50 INFO utils.conversation.supabase_memory: [ASYNC_SUPABASE] Submitting write to async queue for 5dff8e35-3b2c-4954-b40c-fa54e8ea292a
2025-10-20 18:49:50.426 | 2025-10-20 18:49:50 INFO utils.conversation.supabase_memory: [ASYNC_SUPABASE] Queued write for 5dff8e35-3b2c-4954-b40c-fa54e8ea292a
2025-10-20 18:49:50.426 | 2025-10-20 18:49:50 INFO utils.performance.timing: [TIMING] SupabaseMemory.add_turn completed in 0.000s
2025-10-20 18:49:50.427 | 2025-10-20 18:49:50 INFO mcp_activity: [PROGRESS] chat: Generating response (~1,314 tokens)
2025-10-20 18:49:50.427 | 2025-10-20 18:49:50 INFO tools.chat: Sending request to glm API for chat
2025-10-20 18:49:50.427 | 2025-10-20 18:49:50 INFO tools.chat: Using model: glm-4.6 via glm provider
2025-10-20 18:49:50.427 | 2025-10-20 18:49:50 INFO src.providers.orchestration.websearch_adapter: [WEBSEARCH_DEBUG] provider_type=ProviderType.GLM, use_websearch=True, model_name=glm-4.6
2025-10-20 18:49:50.427 | 2025-10-20 18:49:50 INFO src.providers.orchestration.websearch_adapter: [WEBSEARCH_DEBUG] ws.tools=[{'type': 'web_search', 'web_search': {'search_engine': 'search_pro_jina', 'search_recency_filter': 'oneWeek', 'content_size': 'medium', 'result_sequence': 'after', 'search_result': True}}], ws.tool_choice=auto
2025-10-20 18:49:50.427 | 2025-10-20 18:49:50 INFO src.providers.orchestration.websearch_adapter: [WEBSEARCH_DEBUG] Added tools to provider_kwargs: [{'type': 'web_search', 'web_search': {'search_engine': 'search_pro_jina', 'search_recency_filter': 'oneWeek', 'content_size': 'medium', 'result_sequence': 'after', 'search_result': True}}]
2025-10-20 18:49:50.427 | 2025-10-20 18:49:50 INFO src.providers.orchestration.websearch_adapter: [WEBSEARCH_DEBUG] Added tool_choice to provider_kwargs: auto
2025-10-20 18:49:50.427 | 2025-10-20 18:49:50 INFO src.providers.orchestration.websearch_adapter: [WEBSEARCH_DEBUG] Final provider_kwargs keys: ['tools', 'tool_choice']
2025-10-20 18:49:50.427 | 2025-10-20 18:49:50 INFO src.providers.glm_chat: GLM chat using SDK: model=glm-4.6, stream=True, messages_count=2
2025-10-20 18:49:52.115 | 2025-10-20 18:49:52 INFO httpx: HTTP Request: POST https://api.z.ai/api/paas/v4/chat/completions "HTTP/1.1 200 OK"
2025-10-20 18:49:55.674 | 2025-10-20 18:49:55 INFO tools.chat: Received response from glm API for chat
2025-10-20 18:49:55.674 | 2025-10-20 18:49:55 INFO mcp_activity: [PROGRESS] 📝 Processing response...
2025-10-20 18:49:55.674 | 2025-10-20 18:49:55 INFO utils.performance.timing: [TIMING] SupabaseMemory.get_thread completed in 0.000s
2025-10-20 18:49:55.675 | 2025-10-20 18:49:55 INFO utils.conversation.supabase_memory: [ASYNC_SUPABASE] Submitting write to async queue for 5dff8e35-3b2c-4954-b40c-fa54e8ea292a
2025-10-20 18:49:55.675 | 2025-10-20 18:49:55 INFO utils.conversation.supabase_memory: [ASYNC_SUPABASE] Queued write for 5dff8e35-3b2c-4954-b40c-fa54e8ea292a
2025-10-20 18:49:55.675 | 2025-10-20 18:49:55 INFO utils.performance.timing: [TIMING] SupabaseMemory.add_turn completed in 0.000s
2025-10-20 18:49:55.675 | 2025-10-20 18:49:55 INFO utils.performance.timing: [TIMING] SupabaseMemory.get_thread completed in 0.000s
2025-10-20 18:49:55.675 | 2025-10-20 18:49:55 INFO utils.conversation.supabase_memory: [ASYNC_SUPABASE] Submitting write to async queue for 5dff8e35-3b2c-4954-b40c-fa54e8ea292a
2025-10-20 18:49:55.675 | 2025-10-20 18:49:55 INFO utils.conversation.supabase_memory: [ASYNC_SUPABASE] Queued write for 5dff8e35-3b2c-4954-b40c-fa54e8ea292a
2025-10-20 18:49:55.675 | 2025-10-20 18:49:55 INFO utils.performance.timing: [TIMING] SupabaseMemory.add_turn completed in 0.000s
2025-10-20 18:49:55.677 | 2025-10-20 18:49:55 INFO ws_daemon: [WS_PROGRESS_NOTIFIER] Called with message: chat: Starting execution, level: info
2025-10-20 18:49:55.677 | 2025-10-20 18:49:55 INFO utils.performance.timing: [TIMING] SupabaseMemory.get_thread completed in 0.000s
2025-10-20 18:49:55.677 | 2025-10-20 18:49:55 INFO tools.chat: chat tool completed successfully
2025-10-20 18:49:55.677 | 2025-10-20 18:49:55 INFO ws_daemon: [WS_PROGRESS_NOTIFIER] Successfully sent progress + heartbeat frames
2025-10-20 18:49:55.678 | 2025-10-20 18:49:55 INFO ws_daemon: [WS_PROGRESS_NOTIFIER] Called with message: chat: Request validated, level: info
2025-10-20 18:49:55.678 | 2025-10-20 18:49:55 INFO ws_daemon: [WS_PROGRESS_NOTIFIER] Successfully sent progress + heartbeat frames
2025-10-20 18:49:55.678 | 2025-10-20 18:49:55 INFO ws_daemon: [WS_PROGRESS_NOTIFIER] Called with message: chat: Model/context ready: glm-4.6, level: info
2025-10-20 18:49:55.679 | 2025-10-20 18:49:55 INFO ws_daemon: [WS_PROGRESS_NOTIFIER] Successfully sent progress + heartbeat frames
2025-10-20 18:49:55.751 | 2025-10-20 18:49:55 INFO httpx: HTTP Request: POST https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/messages "HTTP/2 201 Created"
2025-10-20 18:49:55.755 | 2025-10-20 18:49:55 INFO utils.conversation.supabase_memory: [CONV_QUEUE] Processed update for 5dff8e35-3b2c-4954-b40c-fa54e8ea292a
2025-10-20 18:49:55.801 | 2025-10-20 18:49:55 INFO httpx: HTTP Request: POST https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/messages "HTTP/2 201 Created"
2025-10-20 18:49:55.802 | 2025-10-20 18:49:55 INFO utils.conversation.supabase_memory: [CONV_QUEUE] Processed update for 5dff8e35-3b2c-4954-b40c-fa54e8ea292a
2025-10-20 18:49:55.849 | 2025-10-20 18:49:55 INFO httpx: HTTP Request: POST https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/messages "HTTP/2 201 Created"
2025-10-20 18:49:55.850 | 2025-10-20 18:49:55 INFO ws_daemon: [WS_PROGRESS_NOTIFIER] Called with message: chat: Generating response (~1,314 tokens), level: info
2025-10-20 18:49:55.850 | 2025-10-20 18:49:55 INFO utils.conversation.supabase_memory: [CONV_QUEUE] Processed update for 5dff8e35-3b2c-4954-b40c-fa54e8ea292a
2025-10-20 18:49:55.851 | 2025-10-20 18:49:55 INFO ws_daemon: [WS_PROGRESS_NOTIFIER] Successfully sent progress + heartbeat frames
2025-10-20 18:49:55.851 | 2025-10-20 18:49:55 INFO ws_daemon: [WS_PROGRESS_NOTIFIER] Called with message: 📝 Processing response..., level: info
2025-10-20 18:49:55.852 | 2025-10-20 18:49:55 INFO ws_daemon: [WS_PROGRESS_NOTIFIER] Successfully sent progress + heartbeat frames
2025-10-20 18:49:55.852 | 2025-10-20 18:49:55 INFO src.server.handlers.request_handler: Tool 'chat' execution completed
2025-10-20 18:49:55.852 | 2025-10-20 18:49:55 INFO ws_daemon: === TOOL CALL COMPLETE ===
2025-10-20 18:49:55.852 | 2025-10-20 18:49:55 INFO ws_daemon: Tool: chat
2025-10-20 18:49:55.853 | 2025-10-20 18:49:55 INFO ws_daemon: Duration: 5.86s
2025-10-20 18:49:55.853 | 2025-10-20 18:49:55 INFO ws_daemon: Provider: GLM
2025-10-20 18:49:55.853 | 2025-10-20 18:49:55 INFO ws_daemon: Session: db35f3ef-baec-48ec-a2af-90476a5f7e7b
2025-10-20 18:49:55.853 | 2025-10-20 18:49:55 INFO ws_daemon: Request ID: bdc29852-226e-4334-b66d-ad4af30dab3c
2025-10-20 18:49:55.854 | 2025-10-20 18:49:55 INFO ws_daemon: Success: True
2025-10-20 18:49:55.854 | 2025-10-20 18:49:55 INFO ws_daemon: === END ===
2025-10-20 18:50:05.868 | 2025-10-20 18:50:05 INFO src.daemon.connection_manager: Connection unregistered: ae2008a6-9652-4fc7-acf2-6f872b8eabd3 from 172.18.0.1 (duration: 15.88s, remaining: 0)
2025-10-20 18:50:05.868 | 2025-10-20 18:50:05 INFO src.daemon.session_manager: [SESSION_MANAGER] Removed session db35f3ef-baec-48ec-a2af-90476a5f7e7b (total sessions: 0)