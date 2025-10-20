2025-10-20 19:41:46.698 | 2025-10-20 19:41:46 INFO root: [ASYNC_LOGGING] Async-safe logging configured successfully
2025-10-20 19:41:46.699 | 2025-10-20 19:41:46 INFO ws_daemon: [AUTH] Authentication enabled (token first 10 chars): test-token...
2025-10-20 19:41:46.699 | 2025-10-20 19:41:46 INFO root: [LOGGING] Configured websockets library logging to suppress handshake noise
2025-10-20 19:41:47.539 | 2025-10-20 19:41:47 INFO src.bootstrap.singletons: Building tool registry (first-time initialization)
2025-10-20 19:41:47.868 | 2025-10-20 19:41:47 INFO src.bootstrap.singletons: Tool registry built successfully with 30 tools
2025-10-20 19:41:47.868 | 2025-10-20 19:41:47 INFO src.daemon.session_manager: [SESSION_MANAGER] Initialized with timeout=3600s, max_sessions=5, cleanup_interval=300s
2025-10-20 19:41:47.882 | 2025-10-20 19:41:47 INFO src.middleware.correlation: [CORRELATION] Correlation ID logging configured
2025-10-20 19:41:47.882 | 2025-10-20 19:41:47 INFO __main__: [MAIN] Correlation ID logging configured
2025-10-20 19:41:47.882 | 2025-10-20 19:41:47 INFO src.daemon.monitoring_endpoint: [MONITORING] Broadcast hook installed
2025-10-20 19:41:47.882 | 2025-10-20 19:41:47 INFO __main__: [MAIN] Monitoring broadcast hook configured
2025-10-20 19:41:47.900 | 2025-10-20 19:41:47 INFO src.monitoring.metrics: [METRICS] Prometheus metrics server started on port 8000
2025-10-20 19:41:47.900 | 2025-10-20 19:41:47 INFO src.monitoring.metrics: [METRICS] Metrics available at http://localhost:8000/metrics
2025-10-20 19:41:47.900 | 2025-10-20 19:41:47 INFO __main__: [MAIN] Metrics server started on port 8000
2025-10-20 19:41:47.900 | 2025-10-20 19:41:47 INFO __main__: [MAIN] Monitoring dashboard will be available at http://localhost:8080/monitoring_dashboard.html
2025-10-20 19:41:47.900 | 2025-10-20 19:41:47 INFO __main__: [MAIN] Health check will be available at http://localhost:8082/health
2025-10-20 19:41:47.900 | 2025-10-20 19:41:47 INFO __main__: [MAIN] Periodic metrics updates enabled (60s interval)
2025-10-20 19:41:47.900 | 2025-10-20 19:41:47 INFO __main__: [MAIN] Starting 4 servers concurrently
2025-10-20 19:41:47.902 | 2025-10-20 19:41:47 INFO ws_daemon: Configuring providers and registering tools at daemon startup...
2025-10-20 19:41:47.902 | 2025-10-20 19:41:47 INFO src.bootstrap.singletons: Configuring providers (first-time initialization)
2025-10-20 19:41:47.902 | 2025-10-20 19:41:47 INFO src.server.providers.provider_detection: Kimi API key found - Moonshot AI models available
2025-10-20 19:41:47.902 | 2025-10-20 19:41:47 INFO src.server.providers.provider_detection: GLM API key found - ZhipuAI models available
2025-10-20 19:41:47.902 | 2025-10-20 19:41:47 INFO src.server.providers.provider_diagnostics: Available providers: Kimi, GLM
2025-10-20 19:41:47.902 | 2025-10-20 19:41:47 INFO src.providers.kimi: Kimi provider using centralized timeout: 240s
2025-10-20 19:41:47.902 | 2025-10-20 19:41:47 INFO root: Model allow-list not configured for OpenAI Compatible - all models permitted. To restrict access, set KIMI_ALLOWED_MODELS with comma-separated model names.
2025-10-20 19:41:47.902 | 2025-10-20 19:41:47 INFO root: Using extended timeouts for custom endpoint: https://api.moonshot.ai/v1
2025-10-20 19:41:47.972 | 2025-10-20 19:41:47 INFO src.providers.glm: GLM provider using SDK with base_url=https://api.z.ai/api/paas/v4, timeout=120s, max_retries=3
2025-10-20 19:41:47.972 | 2025-10-20 19:41:47 INFO src.server.providers.provider_diagnostics: Providers configured: KIMI, GLM; GLM models: 6; Kimi models: 18
2025-10-20 19:41:47.978 | 2025-10-20 19:41:47 INFO ws_daemon: Providers configured successfully. Total tools available: 30
2025-10-20 19:41:47.978 | 2025-10-20 19:41:47 INFO src.server.providers.provider_restrictions: No model restrictions configured - all models allowed
2025-10-20 19:41:47.979 | 2025-10-20 19:41:47 INFO ws_daemon: Initializing conversation storage at daemon startup...
2025-10-20 19:41:47.979 | 2025-10-20 19:41:47 INFO src.bootstrap.singletons: Providers configured successfully
2025-10-20 19:41:47.983 | 2025-10-20 19:41:47 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Initializing conversation storage at startup...
2025-10-20 19:41:47.983 | 2025-10-20 19:41:47 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-20 19:41:48.065 | 2025-10-20 19:41:48 INFO src.storage.supabase_client: [SUPABASE_INIT] SUPABASE_URL=SET
2025-10-20 19:41:48.065 | 2025-10-20 19:41:48 INFO src.storage.supabase_client: [SUPABASE_INIT] SUPABASE_SERVICE_ROLE_KEY=SET
2025-10-20 19:41:48.065 | 2025-10-20 19:41:48 INFO src.storage.supabase_client: Supabase storage initialized: https://mxaazuhlqewmkweewyaz.supabase.co
2025-10-20 19:41:48.594 | 2025-10-20 19:41:48 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/schema_version?select=version&limit=1 "HTTP/2 200 OK"
2025-10-20 19:41:48.596 | 2025-10-20 19:41:48 INFO ws_daemon: Conversation storage initialized successfully
2025-10-20 19:41:48.596 | 2025-10-20 19:41:48 INFO ws_daemon: Pre-warming external connections...
2025-10-20 19:41:48.596 | 2025-10-20 19:41:48 INFO utils.caching.base_cache_manager: [CONVERSATION_CACHE] L1 initialized: TTLCache(maxsize=100, ttl=300s)
2025-10-20 19:41:48.596 | 2025-10-20 19:41:48 INFO utils.caching.base_cache_manager: [CONVERSATION_CACHE] Base cache manager initialized
2025-10-20 19:41:48.596 | 2025-10-20 19:41:48 INFO utils.conversation.cache_manager: [CACHE_MANAGER] Conversation cache manager initialized (L1_TTL=300s, L2_TTL=1800s)
2025-10-20 19:41:48.596 | 2025-10-20 19:41:48 INFO utils.conversation.supabase_memory: [ASYNC_SUPABASE] Will use async queue for writes
2025-10-20 19:41:48.596 | 2025-10-20 19:41:48 INFO utils.infrastructure.storage_backend: Redis storage initialized (ttl=86400s) at redis://:****@redis:6379/0
2025-10-20 19:41:48.596 | 2025-10-20 19:41:48 INFO utils.infrastructure.storage_backend: Initialized Redis conversation storage
2025-10-20 19:41:48.596 | 2025-10-20 19:41:48 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory) with context engineering
2025-10-20 19:41:48.596 | 2025-10-20 19:41:48 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Singleton storage instance created: DualStorageConversation
2025-10-20 19:41:48.596 | 2025-10-20 19:41:48 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Startup initialization complete: DualStorageConversation
2025-10-20 19:41:48.602 | 2025-10-20 19:41:48 INFO src.daemon.warmup: [WARMUP] ========================================
2025-10-20 19:41:48.602 | 2025-10-20 19:41:48 INFO src.daemon.warmup: [WARMUP] Starting connection warmup...
2025-10-20 19:41:48.602 | 2025-10-20 19:41:48 INFO src.daemon.warmup: [WARMUP] ========================================
2025-10-20 19:41:48.602 | 2025-10-20 19:41:48 INFO src.daemon.monitoring_endpoint: [MONITORING] Starting monitoring server on 0.0.0.0:8080
2025-10-20 19:41:48.602 | 2025-10-20 19:41:48 INFO src.monitoring.metrics: [METRICS] Starting periodic updates (interval: 60s)
2025-10-20 19:41:48.703 | 2025-10-20 19:41:48 INFO src.daemon.warmup: [WARMUP] Initializing Supabase connection...
2025-10-20 19:41:48.921 | 2025-10-20 19:41:48 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=id&limit=1 "HTTP/2 200 OK"
2025-10-20 19:41:48.931 | 2025-10-20 19:41:48 INFO src.daemon.warmup: [WARMUP] ✅ Supabase connection warmed up successfully (0.228s)
2025-10-20 19:41:48.931 | 2025-10-20 19:41:48 INFO src.daemon.warmup: [WARMUP] Initializing Redis connection...
2025-10-20 19:41:48.953 | 2025-10-20 19:41:48 INFO src.daemon.monitoring_endpoint: [MONITORING] Monitoring server running on ws://0.0.0.0:8080
2025-10-20 19:41:48.953 | 2025-10-20 19:41:48 INFO src.daemon.monitoring_endpoint: [MONITORING] Dashboard available at http://0.0.0.0:8080/monitoring_dashboard.html
2025-10-20 19:41:48.953 | 2025-10-20 19:41:48 INFO src.daemon.health_endpoint: [HEALTH] Health check server running on http://0.0.0.0:8082/health
2025-10-20 19:41:48.954 | 2025-10-20 19:41:48 INFO ws_daemon: External connections pre-warmed successfully
2025-10-20 19:41:48.954 | 2025-10-20 19:41:48 INFO src.daemon.warmup: [WARMUP] ✅ Redis connection warmed up successfully (0.023s)
2025-10-20 19:41:48.954 | 2025-10-20 19:41:48 INFO src.daemon.warmup: [WARMUP] ========================================
2025-10-20 19:41:48.954 | 2025-10-20 19:41:48 INFO src.daemon.warmup: [WARMUP] ✅ All connections warmed up successfully (0.353s)
2025-10-20 19:41:48.954 | 2025-10-20 19:41:48 INFO src.daemon.warmup: [WARMUP] ========================================
2025-10-20 19:41:48.955 | 2025-10-20 19:41:48 INFO ws_daemon: Initializing conversation queue...
2025-10-20 19:41:48.959 | 2025-10-20 19:41:48 INFO ws_daemon: Conversation queue initialized successfully
2025-10-20 19:41:48.959 | 2025-10-20 19:41:48 INFO src.daemon.conversation_queue: [CONV_QUEUE] Consumer started (max_size=1000, warning_threshold=500)
2025-10-20 19:41:48.959 | 2025-10-20 19:41:48 INFO src.daemon.conversation_queue: [CONV_QUEUE] Global queue initialized
2025-10-20 19:41:48.960 | 2025-10-20 19:41:48 INFO ws_daemon: Initializing session semaphore manager...
2025-10-20 19:41:48.964 | 2025-10-20 19:41:48 INFO ws_daemon: Session semaphore manager initialized successfully
2025-10-20 19:41:48.964 | 2025-10-20 19:41:48 INFO src.daemon.session_semaphore_manager: [SESSION_SEM] Initialized SessionSemaphoreManager (max_concurrent_per_session=5, cleanup_interval=300s, inactive_timeout=300s)
2025-10-20 19:41:48.964 | 2025-10-20 19:41:48 INFO src.daemon.session_semaphore_manager: [SESSION_SEM] Cleanup task started
2025-10-20 19:41:48.964 | 2025-10-20 19:41:48 INFO src.daemon.session_semaphore_manager: [SESSION_SEM] Global session semaphore manager initialized
2025-10-20 19:41:48.964 | 2025-10-20 19:41:48 INFO ws_daemon: Validating timeout hierarchy...
2025-10-20 19:41:48.964 | 2025-10-20 19:41:48 INFO ws_daemon: Timeout hierarchy validated: daemon=270s, tool=180.0s (ratio=1.50x)
2025-10-20 19:41:48.965 | 2025-10-20 19:41:48 INFO ws_daemon: [RESILIENT_WS] Started resilient WebSocket manager with background tasks
2025-10-20 19:41:48.965 | 2025-10-20 19:41:48 INFO ws_daemon: Starting WS daemon on ws://0.0.0.0:8079
2025-10-20 19:41:48.965 | 2025-10-20 19:41:48 INFO src.monitoring.resilient_websocket: Started retry background task
2025-10-20 19:41:48.965 | 2025-10-20 19:41:48 INFO src.monitoring.resilient_websocket: Started cleanup background task
2025-10-20 19:41:48.968 | 2025-10-20 19:41:48 INFO src.daemon.conversation_queue: [CONV_QUEUE] Consumer loop started
2025-10-20 19:41:48.968 | 2025-10-20 19:41:48 INFO src.daemon.session_semaphore_manager: [SESSION_SEM] Cleanup task started
2025-10-20 19:41:48.968 | 2025-10-20 19:41:48 INFO src.monitoring.resilient_websocket: Starting pending message retry task
2025-10-20 19:41:48.968 | 2025-10-20 19:41:48 INFO src.monitoring.resilient_websocket: Starting expired message cleanup task
2025-10-20 19:41:52.481 | 2025-10-20 19:41:52 INFO ws_daemon: [RESILIENT_WS] Stopped resilient WebSocket manager
2025-10-20 19:41:52.482 | 2025-10-20 19:41:52 INFO src.monitoring.resilient_websocket: Stopped retry background task
2025-10-20 19:41:52.482 | 2025-10-20 19:41:52 INFO src.monitoring.resilient_websocket: Stopped cleanup background task
2025-10-20 19:41:52.483 | 2025-10-20 19:41:52 INFO root: [ASYNC_LOGGING] Shutting down async logging listener
2025-10-20 19:41:58.347 | 2025-10-20 19:41:58 INFO root: [ASYNC_LOGGING] Async-safe logging configured successfully
2025-10-20 19:41:58.348 | 2025-10-20 19:41:58 INFO ws_daemon: [AUTH] Authentication enabled (token first 10 chars): test-token...
2025-10-20 19:41:58.348 | 2025-10-20 19:41:58 INFO root: [LOGGING] Configured websockets library logging to suppress handshake noise
2025-10-20 19:41:59.143 | 2025-10-20 19:41:59 INFO src.bootstrap.singletons: Building tool registry (first-time initialization)
2025-10-20 19:41:59.455 | 2025-10-20 19:41:59 INFO src.bootstrap.singletons: Tool registry built successfully with 30 tools
2025-10-20 19:41:59.455 | 2025-10-20 19:41:59 INFO src.daemon.session_manager: [SESSION_MANAGER] Initialized with timeout=3600s, max_sessions=5, cleanup_interval=300s
2025-10-20 19:41:59.469 | 2025-10-20 19:41:59 INFO src.middleware.correlation: [CORRELATION] Correlation ID logging configured
2025-10-20 19:41:59.469 | 2025-10-20 19:41:59 INFO __main__: [MAIN] Correlation ID logging configured
2025-10-20 19:41:59.469 | 2025-10-20 19:41:59 INFO src.daemon.monitoring_endpoint: [MONITORING] Broadcast hook installed
2025-10-20 19:41:59.469 | 2025-10-20 19:41:59 INFO __main__: [MAIN] Monitoring broadcast hook configured
2025-10-20 19:41:59.482 | 2025-10-20 19:41:59 INFO src.monitoring.metrics: [METRICS] Prometheus metrics server started on port 8000
2025-10-20 19:41:59.482 | 2025-10-20 19:41:59 INFO src.monitoring.metrics: [METRICS] Metrics available at http://localhost:8000/metrics
2025-10-20 19:41:59.482 | 2025-10-20 19:41:59 INFO __main__: [MAIN] Metrics server started on port 8000
2025-10-20 19:41:59.482 | 2025-10-20 19:41:59 INFO __main__: [MAIN] Monitoring dashboard will be available at http://localhost:8080/monitoring_dashboard.html
2025-10-20 19:41:59.482 | 2025-10-20 19:41:59 INFO __main__: [MAIN] Health check will be available at http://localhost:8082/health
2025-10-20 19:41:59.482 | 2025-10-20 19:41:59 INFO __main__: [MAIN] Periodic metrics updates enabled (60s interval)
2025-10-20 19:41:59.482 | 2025-10-20 19:41:59 INFO __main__: [MAIN] Starting 4 servers concurrently
2025-10-20 19:41:59.483 | 2025-10-20 19:41:59 INFO ws_daemon: Configuring providers and registering tools at daemon startup...
2025-10-20 19:41:59.484 | 2025-10-20 19:41:59 INFO src.bootstrap.singletons: Configuring providers (first-time initialization)
2025-10-20 19:41:59.484 | 2025-10-20 19:41:59 INFO src.server.providers.provider_detection: Kimi API key found - Moonshot AI models available
2025-10-20 19:41:59.484 | 2025-10-20 19:41:59 INFO src.server.providers.provider_detection: GLM API key found - ZhipuAI models available
2025-10-20 19:41:59.484 | 2025-10-20 19:41:59 INFO src.server.providers.provider_diagnostics: Available providers: Kimi, GLM
2025-10-20 19:41:59.484 | 2025-10-20 19:41:59 INFO src.providers.kimi: Kimi provider using centralized timeout: 240s
2025-10-20 19:41:59.484 | 2025-10-20 19:41:59 INFO root: Model allow-list not configured for OpenAI Compatible - all models permitted. To restrict access, set KIMI_ALLOWED_MODELS with comma-separated model names.
2025-10-20 19:41:59.484 | 2025-10-20 19:41:59 INFO root: Using extended timeouts for custom endpoint: https://api.moonshot.ai/v1
2025-10-20 19:41:59.552 | 2025-10-20 19:41:59 INFO src.providers.glm: GLM provider using SDK with base_url=https://api.z.ai/api/paas/v4, timeout=120s, max_retries=3
2025-10-20 19:41:59.552 | 2025-10-20 19:41:59 INFO src.server.providers.provider_diagnostics: Providers configured: KIMI, GLM; GLM models: 6; Kimi models: 18
2025-10-20 19:41:59.559 | 2025-10-20 19:41:59 INFO ws_daemon: Providers configured successfully. Total tools available: 30
2025-10-20 19:41:59.559 | 2025-10-20 19:41:59 INFO ws_daemon: Initializing conversation storage at daemon startup...
2025-10-20 19:41:59.559 | 2025-10-20 19:41:59 INFO src.server.providers.provider_restrictions: No model restrictions configured - all models allowed
2025-10-20 19:41:59.559 | 2025-10-20 19:41:59 INFO src.bootstrap.singletons: Providers configured successfully
2025-10-20 19:41:59.564 | 2025-10-20 19:41:59 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Initializing conversation storage at startup...
2025-10-20 19:41:59.564 | 2025-10-20 19:41:59 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-20 19:41:59.649 | 2025-10-20 19:41:59 INFO src.storage.supabase_client: [SUPABASE_INIT] SUPABASE_URL=SET
2025-10-20 19:41:59.649 | 2025-10-20 19:41:59 INFO src.storage.supabase_client: [SUPABASE_INIT] SUPABASE_SERVICE_ROLE_KEY=SET
2025-10-20 19:41:59.649 | 2025-10-20 19:41:59 INFO src.storage.supabase_client: Supabase storage initialized: https://mxaazuhlqewmkweewyaz.supabase.co
2025-10-20 19:41:59.796 | 2025-10-20 19:41:59 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/schema_version?select=version&limit=1 "HTTP/2 200 OK"
2025-10-20 19:41:59.798 | 2025-10-20 19:41:59 INFO ws_daemon: Conversation storage initialized successfully
2025-10-20 19:41:59.798 | 2025-10-20 19:41:59 INFO utils.caching.base_cache_manager: [CONVERSATION_CACHE] L1 initialized: TTLCache(maxsize=100, ttl=300s)
2025-10-20 19:41:59.798 | 2025-10-20 19:41:59 INFO utils.caching.base_cache_manager: [CONVERSATION_CACHE] Base cache manager initialized
2025-10-20 19:41:59.798 | 2025-10-20 19:41:59 INFO utils.conversation.cache_manager: [CACHE_MANAGER] Conversation cache manager initialized (L1_TTL=300s, L2_TTL=1800s)
2025-10-20 19:41:59.798 | 2025-10-20 19:41:59 INFO utils.conversation.supabase_memory: [ASYNC_SUPABASE] Will use async queue for writes
2025-10-20 19:41:59.798 | 2025-10-20 19:41:59 INFO utils.infrastructure.storage_backend: Redis storage initialized (ttl=86400s) at redis://:****@redis:6379/0
2025-10-20 19:41:59.798 | 2025-10-20 19:41:59 INFO utils.infrastructure.storage_backend: Initialized Redis conversation storage
2025-10-20 19:41:59.798 | 2025-10-20 19:41:59 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory) with context engineering
2025-10-20 19:41:59.798 | 2025-10-20 19:41:59 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Singleton storage instance created: DualStorageConversation
2025-10-20 19:41:59.798 | 2025-10-20 19:41:59 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Startup initialization complete: DualStorageConversation
2025-10-20 19:41:59.798 | 2025-10-20 19:41:59 INFO ws_daemon: Pre-warming external connections...
2025-10-20 19:41:59.803 | 2025-10-20 19:41:59 INFO src.daemon.warmup: [WARMUP] ========================================
2025-10-20 19:41:59.804 | 2025-10-20 19:41:59 INFO src.daemon.warmup: [WARMUP] Starting connection warmup...
2025-10-20 19:41:59.804 | 2025-10-20 19:41:59 INFO src.daemon.warmup: [WARMUP] ========================================
2025-10-20 19:41:59.804 | 2025-10-20 19:41:59 INFO src.daemon.monitoring_endpoint: [MONITORING] Starting monitoring server on 0.0.0.0:8080
2025-10-20 19:41:59.804 | 2025-10-20 19:41:59 INFO src.monitoring.metrics: [METRICS] Starting periodic updates (interval: 60s)
2025-10-20 19:41:59.905 | 2025-10-20 19:41:59 INFO src.daemon.warmup: [WARMUP] Initializing Supabase connection...
2025-10-20 19:42:00.018 | 2025-10-20 19:42:00 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=id&limit=1 "HTTP/2 200 OK"
2025-10-20 19:42:00.018 | 2025-10-20 19:42:00 INFO src.daemon.warmup: [WARMUP] ✅ Supabase connection warmed up successfully (0.113s)
2025-10-20 19:42:00.018 | 2025-10-20 19:42:00 INFO src.daemon.warmup: [WARMUP] Initializing Redis connection...
2025-10-20 19:42:00.040 | 2025-10-20 19:42:00 INFO src.daemon.monitoring_endpoint: [MONITORING] Monitoring server running on ws://0.0.0.0:8080
2025-10-20 19:42:00.040 | 2025-10-20 19:42:00 INFO src.daemon.monitoring_endpoint: [MONITORING] Dashboard available at http://0.0.0.0:8080/monitoring_dashboard.html
2025-10-20 19:42:00.040 | 2025-10-20 19:42:00 INFO src.daemon.health_endpoint: [HEALTH] Health check server running on http://0.0.0.0:8082/health
2025-10-20 19:42:00.041 | 2025-10-20 19:42:00 INFO src.daemon.warmup: [WARMUP] ✅ Redis connection warmed up successfully (0.023s)
2025-10-20 19:42:00.041 | 2025-10-20 19:42:00 INFO src.daemon.warmup: [WARMUP] ========================================
2025-10-20 19:42:00.041 | 2025-10-20 19:42:00 INFO src.daemon.warmup: [WARMUP] ✅ All connections warmed up successfully (0.238s)
2025-10-20 19:42:00.041 | 2025-10-20 19:42:00 INFO ws_daemon: External connections pre-warmed successfully
2025-10-20 19:42:00.042 | 2025-10-20 19:42:00 INFO src.daemon.warmup: [WARMUP] ========================================
2025-10-20 19:42:00.042 | 2025-10-20 19:42:00 INFO ws_daemon: Initializing conversation queue...
2025-10-20 19:42:00.046 | 2025-10-20 19:42:00 INFO src.daemon.conversation_queue: [CONV_QUEUE] Consumer started (max_size=1000, warning_threshold=500)
2025-10-20 19:42:00.046 | 2025-10-20 19:42:00 INFO src.daemon.conversation_queue: [CONV_QUEUE] Global queue initialized
2025-10-20 19:42:00.046 | 2025-10-20 19:42:00 INFO ws_daemon: Conversation queue initialized successfully
2025-10-20 19:42:00.047 | 2025-10-20 19:42:00 INFO ws_daemon: Initializing session semaphore manager...
2025-10-20 19:42:00.052 | 2025-10-20 19:42:00 INFO src.daemon.session_semaphore_manager: [SESSION_SEM] Initialized SessionSemaphoreManager (max_concurrent_per_session=5, cleanup_interval=300s, inactive_timeout=300s)
2025-10-20 19:42:00.052 | 2025-10-20 19:42:00 INFO src.daemon.session_semaphore_manager: [SESSION_SEM] Cleanup task started
2025-10-20 19:42:00.052 | 2025-10-20 19:42:00 INFO src.daemon.session_semaphore_manager: [SESSION_SEM] Global session semaphore manager initialized
2025-10-20 19:42:00.052 | 2025-10-20 19:42:00 INFO ws_daemon: Session semaphore manager initialized successfully
2025-10-20 19:42:00.052 | 2025-10-20 19:42:00 INFO ws_daemon: Validating timeout hierarchy...
2025-10-20 19:42:00.053 | 2025-10-20 19:42:00 INFO src.monitoring.resilient_websocket: Started retry background task
2025-10-20 19:42:00.053 | 2025-10-20 19:42:00 INFO src.monitoring.resilient_websocket: Started cleanup background task
2025-10-20 19:42:00.053 | 2025-10-20 19:42:00 INFO ws_daemon: Timeout hierarchy validated: daemon=270s, tool=180.0s (ratio=1.50x)
2025-10-20 19:42:00.053 | 2025-10-20 19:42:00 INFO ws_daemon: [RESILIENT_WS] Started resilient WebSocket manager with background tasks
2025-10-20 19:42:00.053 | 2025-10-20 19:42:00 INFO ws_daemon: Starting WS daemon on ws://0.0.0.0:8079
2025-10-20 19:42:00.054 | 2025-10-20 19:42:00 INFO src.daemon.conversation_queue: [CONV_QUEUE] Consumer loop started
2025-10-20 19:42:00.054 | 2025-10-20 19:42:00 INFO src.daemon.session_semaphore_manager: [SESSION_SEM] Cleanup task started
2025-10-20 19:42:00.054 | 2025-10-20 19:42:00 INFO src.monitoring.resilient_websocket: Starting pending message retry task
2025-10-20 19:42:00.054 | 2025-10-20 19:42:00 INFO src.monitoring.resilient_websocket: Starting expired message cleanup task
2025-10-20 19:45:30.779 | 2025-10-20 19:45:30 INFO src.daemon.connection_manager: ConnectionManager initialized: max_connections=1000, max_per_ip=10
2025-10-20 19:45:30.779 | 2025-10-20 19:45:30 INFO src.daemon.connection_manager: Connection registered: a1537040-3058-4390-b9df-2853e4464f02 from 172.18.0.1 (total: 1, ip_total: 1)
2025-10-20 19:45:30.779 | 2025-10-20 19:45:30 INFO src.daemon.session_manager: [SESSION_MANAGER] Created session 3e321057-92f7-45e5-adaa-dafe0c2def32 (total sessions: 1)
2025-10-20 19:45:30.779 | 2025-10-20 19:45:30 INFO ws_daemon: [WS_CONNECTION] New connection from 172.18.0.1:47406 (id: a1537040-3058-4390-b9df-2853e4464f02)
2025-10-20 19:45:30.780 | 2025-10-20 19:45:30 INFO src.resilience.rate_limiter: RateLimiter initialized: global=1000/100.0t/s, ip=100/10.0t/s, user=50/5.0t/s, cleanup_interval=3600s
2025-10-20 19:45:53.205 | 2025-10-20 19:45:53 INFO src.daemon.connection_manager: Connection registered: 4334685b-3453-4124-9bdb-5650d3e9549b from 172.18.0.1 (total: 2, ip_total: 2)
2025-10-20 19:45:53.205 | 2025-10-20 19:45:53 INFO ws_daemon: [WS_CONNECTION] New connection from 172.18.0.1:49460 (id: 4334685b-3453-4124-9bdb-5650d3e9549b)
2025-10-20 19:45:53.205 | 2025-10-20 19:45:53 INFO src.daemon.session_manager: [SESSION_MANAGER] Created session 56ce3cc7-24bc-428a-b8d6-2782821b8ce6 (total sessions: 2)
2025-10-20 19:45:53.206 | 2025-10-20 19:45:53 INFO ws_daemon: === TOOL CALL RECEIVED ===
2025-10-20 19:45:53.206 | 2025-10-20 19:45:53 INFO ws_daemon: Session: 56ce3cc7-24bc-428a-b8d6-2782821b8ce6
2025-10-20 19:45:53.207 | 2025-10-20 19:45:53 INFO ws_daemon: Tool: chat (original: chat)
2025-10-20 19:45:53.207 | 2025-10-20 19:45:53 INFO ws_daemon: Request ID: db963352-d9dc-4f71-86d4-f3daddaccd06
2025-10-20 19:45:53.207 | 2025-10-20 19:45:53 INFO ws_daemon: Arguments (first 500 chars): {
2025-10-20 19:45:53.207 |   "prompt": "I'm investigating a critical issue with DeepSeek-R1-Distill-Qwen-7B deployed with TensorRT-LLM 1.0.0 FP8 quantization on RTX 5070 Ti (Blackwell SM 12.0).\n\n**THE PROBLEM:**\nThe model generates garbage output - after producing a small amount of valid text, it fills the remaining tokens (up to 8,192 max_seq_len) with repeated `<\uff5cend\u2581of\u2581sentence\uff5c>` tokens. This happens in BOTH the official test script AND the FastAPI backend.\n\n**EVIDENCE:**\n1. Official test s
2025-10-20 19:45:53.207 | 2025-10-20 19:45:53 INFO ws_daemon: === PROCESSING ===
2025-10-20 19:45:53.208 | 2025-10-20 19:45:53 INFO src.server.handlers.request_handler_init: MCP tool call: chat req_id=b7ce28e3-3c28-4bb3-b01e-d82a2e0c97cd
2025-10-20 19:45:53.215 | 2025-10-20 19:45:53 INFO mcp_activity: TOOL_CALL: chat with 6 arguments req_id=b7ce28e3-3c28-4bb3-b01e-d82a2e0c97cd
2025-10-20 19:45:53.220 | 2025-10-20 19:45:53 INFO src.server.handlers.request_handler: MCP tool call: chat req_id=b7ce28e3-3c28-4bb3-b01e-d82a2e0c97cd
2025-10-20 19:45:53.220 | 2025-10-20 19:45:53 INFO utils.caching.base_cache_manager: [ROUTING:PROVIDER_CACHE] L1 initialized: TTLCache(maxsize=50, ttl=300s)
2025-10-20 19:45:53.220 | 2025-10-20 19:45:53 INFO utils.caching.base_cache_manager: [ROUTING:PROVIDER_CACHE] Base cache manager initialized
2025-10-20 19:45:53.220 | 2025-10-20 19:45:53 INFO utils.caching.base_cache_manager: [ROUTING:MODEL_CACHE] L1 initialized: TTLCache(maxsize=100, ttl=180s)
2025-10-20 19:45:53.220 | 2025-10-20 19:45:53 INFO utils.caching.base_cache_manager: [ROUTING:MODEL_CACHE] Base cache manager initialized
2025-10-20 19:45:53.220 | 2025-10-20 19:45:53 INFO src.router.routing_cache: [ROUTING_CACHE] Tool cache: LRUCache(maxsize=200)
2025-10-20 19:45:53.220 | 2025-10-20 19:45:53 INFO utils.caching.base_cache_manager: [ROUTING:FALLBACK_CACHE] L1 initialized: TTLCache(maxsize=50, ttl=600s)
2025-10-20 19:45:53.220 | 2025-10-20 19:45:53 INFO utils.caching.base_cache_manager: [ROUTING:FALLBACK_CACHE] Base cache manager initialized
2025-10-20 19:45:53.220 | 2025-10-20 19:45:53 INFO src.router.routing_cache: [ROUTING_CACHE] Initialized with Redis L2: provider_ttl=300s, model_ttl=180s, fallback_ttl=600s, redis_enabled=True
2025-10-20 19:45:53.222 | 2025-10-20 19:45:53 INFO utils.caching.base_cache_manager: [ROUTING:MODEL_CACHE] L2 (Redis) connected: redis:6379/0
2025-10-20 19:45:53.223 | 2025-10-20 19:45:53 INFO mcp_activity: [PROGRESS] tool=chat req_id=b7ce28e3-3c28-4bb3-b01e-d82a2e0c97cd elapsed=0.0s — heartbeat
2025-10-20 19:45:53.223 | 2025-10-20 19:45:53 INFO tools.chat: chat tool called with arguments: ['prompt', 'model', 'thinking_mode', 'use_websearch', '_session_id', '_call_key', '_model_context', '_resolved_model_name', '_today']
2025-10-20 19:45:53.223 | 2025-10-20 19:45:53 INFO mcp_activity: [PROGRESS] chat: Starting execution
2025-10-20 19:45:53.223 | 2025-10-20 19:45:53 INFO mcp_activity: [PROGRESS] chat: Request validated
2025-10-20 19:45:53.240 | 2025-10-20 19:45:53 INFO mcp_activity: [PROGRESS] chat: Model/context ready: glm-4.5-flash
2025-10-20 19:45:53.256 | 2025-10-20 19:45:53 INFO mcp_activity: [PROGRESS] chat: Generating response (~1,088 tokens)
2025-10-20 19:45:53.256 | 2025-10-20 19:45:53 INFO tools.chat: Sending request to glm API for chat
2025-10-20 19:45:53.256 | 2025-10-20 19:45:53 INFO tools.chat: Using model: glm-4.5-flash via glm provider
2025-10-20 19:45:53.276 | 2025-10-20 19:45:53 INFO src.providers.orchestration.websearch_adapter: [WEBSEARCH_DEBUG] provider_type=ProviderType.GLM, use_websearch=True, model_name=glm-4.5-flash
2025-10-20 19:45:53.276 | 2025-10-20 19:45:53 INFO src.providers.orchestration.websearch_adapter: [WEBSEARCH_DEBUG] ws.tools=[{'type': 'web_search', 'web_search': {'search_engine': 'search_pro_jina', 'search_recency_filter': 'oneWeek', 'content_size': 'medium', 'result_sequence': 'after', 'search_result': True}}], ws.tool_choice=auto
2025-10-20 19:45:53.276 | 2025-10-20 19:45:53 INFO src.providers.orchestration.websearch_adapter: [WEBSEARCH_DEBUG] Added tools to provider_kwargs: [{'type': 'web_search', 'web_search': {'search_engine': 'search_pro_jina', 'search_recency_filter': 'oneWeek', 'content_size': 'medium', 'result_sequence': 'after', 'search_result': True}}]
2025-10-20 19:45:53.276 | 2025-10-20 19:45:53 INFO src.providers.orchestration.websearch_adapter: [WEBSEARCH_DEBUG] Added tool_choice to provider_kwargs: auto
2025-10-20 19:45:53.276 | 2025-10-20 19:45:53 INFO src.providers.orchestration.websearch_adapter: [WEBSEARCH_DEBUG] Final provider_kwargs keys: ['tools', 'tool_choice']
2025-10-20 19:45:53.288 | 2025-10-20 19:45:53 INFO utils.infrastructure.semantic_cache: Semantic cache initialized (TTL=600s, max_size=1000, max_response_size=1048576 bytes)
2025-10-20 19:45:53.288 | 2025-10-20 19:45:53 INFO utils.infrastructure.semantic_cache: Initialized global semantic cache (TTL=600s, max_size=1000, max_response_size=1048576 bytes)
2025-10-20 19:45:53.288 | 2025-10-20 19:45:53 WARNING src.providers.glm_chat: ⚠️ Model glm-4.5-flash doesn't support thinking_mode - parameter ignored. Use glm-4.6, glm-4.5, or glm-4.5-air for thinking mode support. Requested mode: None
2025-10-20 19:45:53.288 | 2025-10-20 19:45:53 INFO src.providers.glm_chat: GLM chat using SDK: model=glm-4.5-flash, stream=True, messages_count=2
2025-10-20 19:45:54.858 | 2025-10-20 19:45:54 INFO httpx: HTTP Request: POST https://api.z.ai/api/paas/v4/chat/completions "HTTP/1.1 200 OK"
2025-10-20 19:46:12.580 | 2025-10-20 19:46:12 INFO tools.chat: Received response from glm API for chat
2025-10-20 19:46:12.580 | 2025-10-20 19:46:12 INFO mcp_activity: [PROGRESS] 📝 Processing response...
2025-10-20 19:46:12.586 | 2025-10-20 19:46:12 INFO utils.conversation.threads: [STORAGE_INTEGRATION] Storage factory available - will use configured backend
2025-10-20 19:46:12.586 | 2025-10-20 19:46:12 INFO utils.conversation.threads: [STORAGE_INTEGRATION] Created cached storage backend instance
2025-10-20 19:46:12.588 | 2025-10-20 19:46:12 INFO utils.caching.base_cache_manager: [CONVERSATION_CACHE] L2 (Redis) connected: redis:6379/0
2025-10-20 19:46:13.225 | 2025-10-20 19:46:13 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.facd6e46-607c-4b5c-8c73-194cd80c9bd9 "HTTP/2 200 OK"
2025-10-20 19:46:13.226 | 2025-10-20 19:46:13 WARNING src.storage.supabase_client: Slow operation: get_conversation_by_continuation_id took 0.638s
2025-10-20 19:46:13.226 | 2025-10-20 19:46:13 INFO utils.performance.timing: [TIMING] SupabaseMemory.get_conversation_by_continuation_id took 0.638s
2025-10-20 19:46:13.226 | 2025-10-20 19:46:13 INFO utils.performance.timing: [TIMING] SupabaseMemory.get_thread completed in 0.640s
2025-10-20 19:46:13.285 | 2025-10-20 19:46:13 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.facd6e46-607c-4b5c-8c73-194cd80c9bd9 "HTTP/2 200 OK"
2025-10-20 19:46:13.286 | 2025-10-20 19:46:13 INFO utils.performance.timing: [TIMING] SupabaseMemory.get_conversation_by_continuation_id took 0.058s
2025-10-20 19:46:13.286 | 2025-10-20 19:46:13 INFO utils.performance.timing: [TIMING] SupabaseMemory.get_thread completed in 0.058s
2025-10-20 19:46:13.359 | 2025-10-20 19:46:13 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.facd6e46-607c-4b5c-8c73-194cd80c9bd9 "HTTP/2 200 OK"
2025-10-20 19:46:13.359 | 2025-10-20 19:46:13 INFO utils.performance.timing: [TIMING] SupabaseMemory.get_conversation_by_continuation_id took 0.072s
2025-10-20 19:46:13.359 | 2025-10-20 19:46:13 INFO utils.performance.timing: [TIMING] SupabaseMemory.get_thread completed in 0.073s
2025-10-20 19:46:16.824 | 2025-10-20 19:46:16 INFO utils.conversation.supabase_memory: [ASYNC_SUPABASE] Submitting write to async queue for facd6e46-607c-4b5c-8c73-194cd80c9bd9
2025-10-20 19:46:16.824 | 2025-10-20 19:46:16 INFO utils.conversation.supabase_memory: [ASYNC_SUPABASE] Queued write for facd6e46-607c-4b5c-8c73-194cd80c9bd9
2025-10-20 19:46:16.824 | 2025-10-20 19:46:16 INFO utils.performance.timing: [TIMING] SupabaseMemory.add_turn completed in 0.000s
2025-10-20 19:46:16.825 | 2025-10-20 19:46:16 INFO utils.conversation.supabase_memory: [ASYNC_SUPABASE] Submitting write to async queue for facd6e46-607c-4b5c-8c73-194cd80c9bd9
2025-10-20 19:46:16.825 | 2025-10-20 19:46:16 INFO utils.conversation.supabase_memory: [ASYNC_SUPABASE] Queued write for facd6e46-607c-4b5c-8c73-194cd80c9bd9
2025-10-20 19:46:16.825 | 2025-10-20 19:46:16 INFO utils.performance.timing: [TIMING] SupabaseMemory.add_turn completed in 0.000s
2025-10-20 19:46:16.825 | 2025-10-20 19:46:16 INFO ws_daemon: [WS_PROGRESS_NOTIFIER] Called with message: chat: Starting execution, level: info
2025-10-20 19:46:16.825 | 2025-10-20 19:46:16 INFO tools.chat: chat tool completed successfully
2025-10-20 19:46:16.826 | 2025-10-20 19:46:16 INFO ws_daemon: [WS_PROGRESS_NOTIFIER] Successfully sent progress + heartbeat frames
2025-10-20 19:46:16.826 | 2025-10-20 19:46:16 INFO ws_daemon: [WS_PROGRESS_NOTIFIER] Called with message: chat: Request validated, level: info
2025-10-20 19:46:16.827 | 2025-10-20 19:46:16 INFO ws_daemon: [WS_PROGRESS_NOTIFIER] Successfully sent progress + heartbeat frames
2025-10-20 19:46:16.827 | 2025-10-20 19:46:16 INFO ws_daemon: [WS_PROGRESS_NOTIFIER] Called with message: chat: Model/context ready: glm-4.5-flash, level: info
2025-10-20 19:46:16.827 | 2025-10-20 19:46:16 INFO ws_daemon: [WS_PROGRESS_NOTIFIER] Successfully sent progress + heartbeat frames
2025-10-20 19:46:16.827 | 2025-10-20 19:46:16 INFO ws_daemon: [WS_PROGRESS_NOTIFIER] Called with message: chat: Generating response (~1,088 tokens), level: info
2025-10-20 19:46:16.828 | 2025-10-20 19:46:16 INFO ws_daemon: [WS_PROGRESS_NOTIFIER] Successfully sent progress + heartbeat frames
2025-10-20 19:46:16.828 | 2025-10-20 19:46:16 INFO ws_daemon: [WS_PROGRESS_NOTIFIER] Called with message: 📝 Processing response..., level: info
2025-10-20 19:46:16.829 | 2025-10-20 19:46:16 INFO ws_daemon: [WS_PROGRESS_NOTIFIER] Successfully sent progress + heartbeat frames
2025-10-20 19:46:16.887 | 2025-10-20 19:46:16 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.facd6e46-607c-4b5c-8c73-194cd80c9bd9 "HTTP/2 200 OK"
2025-10-20 19:46:16.944 | 2025-10-20 19:46:16 INFO httpx: HTTP Request: POST https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations "HTTP/2 201 Created"
2025-10-20 19:46:16.945 | 2025-10-20 19:46:16 INFO src.storage.supabase_client: Saved conversation: facd6e46-607c-4b5c-8c73-194cd80c9bd9 -> 5aad206e-2bfe-4276-851f-00476d6054d8
2025-10-20 19:46:16.945 | 2025-10-20 19:46:16 INFO src.storage.conversation_mapper: Created new conversation: facd6e46-607c-4b5c-8c73-194cd80c9bd9 -> 5aad206e-2bfe-4276-851f-00476d6054d8
2025-10-20 19:46:16.988 | 2025-10-20 19:46:16 INFO httpx: HTTP Request: POST https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/messages "HTTP/2 201 Created"
2025-10-20 19:46:16.989 | 2025-10-20 19:46:16 INFO utils.conversation.supabase_memory: [CONV_QUEUE] Processed update for facd6e46-607c-4b5c-8c73-194cd80c9bd9
2025-10-20 19:46:17.063 | 2025-10-20 19:46:17 INFO httpx: HTTP Request: POST https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/messages "HTTP/2 201 Created"
2025-10-20 19:46:17.064 | 2025-10-20 19:46:17 INFO utils.conversation.supabase_memory: [CONV_QUEUE] Processed update for facd6e46-607c-4b5c-8c73-194cd80c9bd9
2025-10-20 19:46:17.064 | 2025-10-20 19:46:17 INFO src.server.handlers.request_handler: Tool 'chat' execution completed
2025-10-20 19:46:17.065 | 2025-10-20 19:46:17 INFO ws_daemon: === TOOL CALL COMPLETE ===
2025-10-20 19:46:17.065 | 2025-10-20 19:46:17 INFO ws_daemon: Tool: chat
2025-10-20 19:46:17.066 | 2025-10-20 19:46:17 INFO ws_daemon: Duration: 23.86s
2025-10-20 19:46:17.066 | 2025-10-20 19:46:17 INFO ws_daemon: Provider: unknown
2025-10-20 19:46:17.066 | 2025-10-20 19:46:17 INFO ws_daemon: Session: 56ce3cc7-24bc-428a-b8d6-2782821b8ce6
2025-10-20 19:46:17.066 | 2025-10-20 19:46:17 INFO ws_daemon: Request ID: db963352-d9dc-4f71-86d4-f3daddaccd06
2025-10-20 19:46:17.066 | 2025-10-20 19:46:17 INFO ws_daemon: Success: True
2025-10-20 19:46:17.066 | 2025-10-20 19:46:17 INFO ws_daemon: === END ===
2025-10-20 19:46:22.849 | 2025-10-20 19:46:22 INFO ws_daemon: === TOOL CALL RECEIVED ===
2025-10-20 19:46:22.849 | 2025-10-20 19:46:22 INFO ws_daemon: Session: 56ce3cc7-24bc-428a-b8d6-2782821b8ce6
2025-10-20 19:46:22.849 | 2025-10-20 19:46:22 INFO ws_daemon: Tool: chat (original: chat)
2025-10-20 19:46:22.849 | 2025-10-20 19:46:22 INFO ws_daemon: Request ID: 6b10a81b-1c0e-4d0d-aaaa-3a4ccdb018a7
2025-10-20 19:46:22.850 | 2025-10-20 19:46:22 INFO ws_daemon: Arguments (first 500 chars): {
2025-10-20 19:46:22.850 |   "prompt": "Continue with your analysis. Based on the web search results, what are the actionable solutions?",
2025-10-20 19:46:22.850 |   "continuation_id": "facd6e46-607c-4b5c-8c73-194cd80c9bd9",
2025-10-20 19:46:22.850 |   "model": "auto",
2025-10-20 19:46:22.850 |   "thinking_mode": "max",
2025-10-20 19:46:22.850 |   "use_websearch": true
2025-10-20 19:46:22.850 | }
2025-10-20 19:46:22.850 | 2025-10-20 19:46:22 INFO ws_daemon: === PROCESSING ===
2025-10-20 19:46:22.851 | 2025-10-20 19:46:22 ERROR ws_daemon: === TOOL CALL FAILED ===
2025-10-20 19:46:22.851 | 2025-10-20 19:46:22 INFO src.server.handlers.request_handler_init: MCP tool call: chat req_id=9f504398-17aa-4d9d-9a1f-9edd0c84e768
2025-10-20 19:46:22.851 | 2025-10-20 19:46:22 INFO mcp_activity: TOOL_CALL: chat with 7 arguments req_id=9f504398-17aa-4d9d-9a1f-9edd0c84e768
2025-10-20 19:46:22.851 | 2025-10-20 19:46:22 INFO src.server.handlers.request_handler: MCP tool call: chat req_id=9f504398-17aa-4d9d-9a1f-9edd0c84e768
2025-10-20 19:46:22.851 | 2025-10-20 19:46:22 INFO mcp_activity: CONVERSATION_RESUME: chat resuming thread facd6e46-607c-4b5c-8c73-194cd80c9bd9 req_id=9f504398-17aa-4d9d-9a1f-9edd0c84e768
2025-10-20 19:46:22.851 | 2025-10-20 19:46:22 ERROR ws_daemon: Tool: chat
2025-10-20 19:46:22.851 | 2025-10-20 19:46:22 ERROR ws_daemon: Duration: 0.00s
2025-10-20 19:46:22.852 | 2025-10-20 19:46:22 ERROR ws_daemon: Session: 56ce3cc7-24bc-428a-b8d6-2782821b8ce6
2025-10-20 19:46:22.852 | 2025-10-20 19:46:22 ERROR ws_daemon: Request ID: 6b10a81b-1c0e-4d0d-aaaa-3a4ccdb018a7
2025-10-20 19:46:22.852 | 2025-10-20 19:46:22 ERROR ws_daemon: Error: cannot import name 'build_conversation_history' from 'utils.conversation.memory' (/app/utils/conversation/memory.py)
2025-10-20 19:46:22.872 | 2025-10-20 19:46:22 ERROR ws_daemon: Full traceback:
2025-10-20 19:46:22.872 | Traceback (most recent call last):
2025-10-20 19:46:22.872 |   File "/app/src/daemon/ws_server.py", line 957, in _handle_message
2025-10-20 19:46:22.872 |     outputs = await asyncio.wait_for(tool_task, timeout=PROGRESS_INTERVAL)
2025-10-20 19:46:22.872 |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-10-20 19:46:22.872 |   File "/usr/local/lib/python3.13/asyncio/tasks.py", line 507, in wait_for
2025-10-20 19:46:22.872 |     return await fut
2025-10-20 19:46:22.872 |            ^^^^^^^^^
2025-10-20 19:46:22.872 |   File "/app/src/server/handlers/request_handler.py", line 86, in handle_call_tool
2025-10-20 19:46:22.872 |     arguments = await reconstruct_context(name, arguments, req_id)
2025-10-20 19:46:22.872 |                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-10-20 19:46:22.872 |   File "/app/src/server/handlers/request_handler_context.py", line 53, in reconstruct_context
2025-10-20 19:46:22.872 |     arguments = await reconstruct_thread_context(arguments)
2025-10-20 19:46:22.872 |                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-10-20 19:46:22.872 |   File "/app/src/server/context/thread_context.py", line 96, in reconstruct_thread_context
2025-10-20 19:46:22.872 |     from utils.conversation.memory import add_turn, build_conversation_history, get_thread
2025-10-20 19:46:22.872 | ImportError: cannot import name 'build_conversation_history' from 'utils.conversation.memory' (/app/utils/conversation/memory.py)
2025-10-20 19:46:22.872 | 2025-10-20 19:46:22 ERROR ws_daemon: === END ===
2025-10-20 19:46:43.529 | 2025-10-20 19:46:43 INFO ws_daemon: === TOOL CALL RECEIVED ===
2025-10-20 19:46:43.529 | 2025-10-20 19:46:43 INFO ws_daemon: Session: 3e321057-92f7-45e5-adaa-dafe0c2def32
2025-10-20 19:46:43.530 | 2025-10-20 19:46:43 INFO ws_daemon: Tool: chat (original: chat)
2025-10-20 19:46:43.530 | 2025-10-20 19:46:43 INFO ws_daemon: Request ID: e122809b-2247-47d1-891b-6ec8c04f869a
2025-10-20 19:46:43.530 | 2025-10-20 19:46:43 INFO ws_daemon: Arguments (first 500 chars): {
2025-10-20 19:46:43.530 |   "prompt": "Hello! This is a test to verify the EXAI MCP server is working correctly after Phase 1 and Phase 3 fixes. Can you confirm you're receiving this message?",
2025-10-20 19:46:43.530 |   "model": "glm-4.5-flash",
2025-10-20 19:46:43.530 |   "use_websearch": false
2025-10-20 19:46:43.530 | }
2025-10-20 19:46:43.531 | 2025-10-20 19:46:43 INFO ws_daemon: === PROCESSING ===
2025-10-20 19:46:43.532 | 2025-10-20 19:46:43 INFO src.server.handlers.request_handler_init: MCP tool call: chat req_id=a41e9103-f9f9-4ffa-8ab7-242a121a2989
2025-10-20 19:46:43.532 | 2025-10-20 19:46:43 INFO mcp_activity: TOOL_CALL: chat with 5 arguments req_id=a41e9103-f9f9-4ffa-8ab7-242a121a2989
2025-10-20 19:46:43.532 | 2025-10-20 19:46:43 INFO src.server.handlers.request_handler: MCP tool call: chat req_id=a41e9103-f9f9-4ffa-8ab7-242a121a2989
2025-10-20 19:46:43.532 | 2025-10-20 19:46:43 INFO mcp_activity: [PROGRESS] tool=chat req_id=a41e9103-f9f9-4ffa-8ab7-242a121a2989 elapsed=0.0s — heartbeat
2025-10-20 19:46:43.532 | 2025-10-20 19:46:43 INFO tools.chat: chat tool called with arguments: ['prompt', 'model', 'use_websearch', '_session_id', '_call_key', '_model_context', '_resolved_model_name', '_today']
2025-10-20 19:46:43.532 | 2025-10-20 19:46:43 INFO mcp_activity: [PROGRESS] chat: Starting execution
2025-10-20 19:46:43.532 | 2025-10-20 19:46:43 INFO mcp_activity: [PROGRESS] chat: Request validated
2025-10-20 19:46:43.532 | 2025-10-20 19:46:43 INFO mcp_activity: [PROGRESS] chat: Model/context ready: glm-4.5-flash
2025-10-20 19:46:43.534 | 2025-10-20 19:46:43 INFO mcp_activity: [PROGRESS] chat: Generating response (~415 tokens)
2025-10-20 19:46:43.534 | 2025-10-20 19:46:43 INFO tools.chat: Sending request to glm API for chat
2025-10-20 19:46:43.534 | 2025-10-20 19:46:43 INFO tools.chat: Using model: glm-4.5-flash via glm provider
2025-10-20 19:46:43.534 | 2025-10-20 19:46:43 INFO src.providers.orchestration.websearch_adapter: [WEBSEARCH_DEBUG] provider_type=ProviderType.GLM, use_websearch=False, model_name=glm-4.5-flash
2025-10-20 19:46:43.534 | 2025-10-20 19:46:43 INFO src.providers.orchestration.websearch_adapter: [WEBSEARCH_DEBUG] ws.tools=None, ws.tool_choice=None
2025-10-20 19:46:43.534 | 2025-10-20 19:46:43 INFO src.providers.orchestration.websearch_adapter: [WEBSEARCH_DEBUG] Final provider_kwargs keys: []
2025-10-20 19:46:43.534 | 2025-10-20 19:46:43 WARNING src.providers.glm_chat: ⚠️ Model glm-4.5-flash doesn't support thinking_mode - parameter ignored. Use glm-4.6, glm-4.5, or glm-4.5-air for thinking mode support. Requested mode: None
2025-10-20 19:46:43.534 | 2025-10-20 19:46:43 INFO src.providers.glm_chat: GLM chat using SDK: model=glm-4.5-flash, stream=True, messages_count=2
2025-10-20 19:46:45.837 | 2025-10-20 19:46:45 INFO httpx: HTTP Request: POST https://api.z.ai/api/paas/v4/chat/completions "HTTP/1.1 200 OK"
2025-10-20 19:46:50.738 | 2025-10-20 19:46:50 INFO tools.chat: Received response from glm API for chat
2025-10-20 19:46:50.738 | 2025-10-20 19:46:50 INFO mcp_activity: [PROGRESS] 📝 Processing response...
2025-10-20 19:46:50.888 | 2025-10-20 19:46:50 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.c60eeee8-3641-4332-b4e0-1eda1bf3882d "HTTP/2 200 OK"
2025-10-20 19:46:50.890 | 2025-10-20 19:46:50 INFO utils.performance.timing: [TIMING] SupabaseMemory.get_conversation_by_continuation_id took 0.151s
2025-10-20 19:46:50.890 | 2025-10-20 19:46:50 INFO utils.performance.timing: [TIMING] SupabaseMemory.get_thread completed in 0.152s
2025-10-20 19:46:50.970 | 2025-10-20 19:46:50 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.c60eeee8-3641-4332-b4e0-1eda1bf3882d "HTTP/2 200 OK"
2025-10-20 19:46:50.970 | 2025-10-20 19:46:50 INFO utils.performance.timing: [TIMING] SupabaseMemory.get_conversation_by_continuation_id took 0.080s
2025-10-20 19:46:50.970 | 2025-10-20 19:46:50 INFO utils.performance.timing: [TIMING] SupabaseMemory.get_thread completed in 0.080s
2025-10-20 19:46:51.026 | 2025-10-20 19:46:51 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.c60eeee8-3641-4332-b4e0-1eda1bf3882d "HTTP/2 200 OK"
2025-10-20 19:46:51.026 | 2025-10-20 19:46:51 INFO utils.performance.timing: [TIMING] SupabaseMemory.get_conversation_by_continuation_id took 0.055s
2025-10-20 19:46:51.026 | 2025-10-20 19:46:51 INFO utils.performance.timing: [TIMING] SupabaseMemory.get_thread completed in 0.056s
2025-10-20 19:46:51.027 | 2025-10-20 19:46:51 INFO utils.conversation.supabase_memory: [ASYNC_SUPABASE] Submitting write to async queue for c60eeee8-3641-4332-b4e0-1eda1bf3882d
2025-10-20 19:46:51.027 | 2025-10-20 19:46:51 INFO utils.conversation.supabase_memory: [ASYNC_SUPABASE] Queued write for c60eeee8-3641-4332-b4e0-1eda1bf3882d
2025-10-20 19:46:51.027 | 2025-10-20 19:46:51 INFO utils.performance.timing: [TIMING] SupabaseMemory.add_turn completed in 0.000s
2025-10-20 19:46:51.027 | 2025-10-20 19:46:51 INFO utils.conversation.supabase_memory: [ASYNC_SUPABASE] Submitting write to async queue for c60eeee8-3641-4332-b4e0-1eda1bf3882d
2025-10-20 19:46:51.027 | 2025-10-20 19:46:51 INFO utils.conversation.supabase_memory: [ASYNC_SUPABASE] Queued write for c60eeee8-3641-4332-b4e0-1eda1bf3882d
2025-10-20 19:46:51.027 | 2025-10-20 19:46:51 INFO utils.performance.timing: [TIMING] SupabaseMemory.add_turn completed in 0.000s
2025-10-20 19:46:51.027 | 2025-10-20 19:46:51 INFO tools.chat: chat tool completed successfully
2025-10-20 19:46:51.027 | 2025-10-20 19:46:51 INFO ws_daemon: [WS_PROGRESS_NOTIFIER] Called with message: chat: Starting execution, level: info
2025-10-20 19:46:51.028 | 2025-10-20 19:46:51 INFO ws_daemon: [WS_PROGRESS_NOTIFIER] Successfully sent progress + heartbeat frames
2025-10-20 19:46:51.028 | 2025-10-20 19:46:51 INFO ws_daemon: [WS_PROGRESS_NOTIFIER] Called with message: chat: Request validated, level: info
2025-10-20 19:46:51.028 | 2025-10-20 19:46:51 INFO ws_daemon: [WS_PROGRESS_NOTIFIER] Successfully sent progress + heartbeat frames
2025-10-20 19:46:51.029 | 2025-10-20 19:46:51 INFO ws_daemon: [WS_PROGRESS_NOTIFIER] Called with message: chat: Model/context ready: glm-4.5-flash, level: info
2025-10-20 19:46:51.029 | 2025-10-20 19:46:51 INFO ws_daemon: [WS_PROGRESS_NOTIFIER] Successfully sent progress + heartbeat frames
2025-10-20 19:46:51.029 | 2025-10-20 19:46:51 INFO ws_daemon: [WS_PROGRESS_NOTIFIER] Called with message: chat: Generating response (~415 tokens), level: info
2025-10-20 19:46:51.029 | 2025-10-20 19:46:51 INFO ws_daemon: [WS_PROGRESS_NOTIFIER] Successfully sent progress + heartbeat frames
2025-10-20 19:46:51.030 | 2025-10-20 19:46:51 INFO ws_daemon: [WS_PROGRESS_NOTIFIER] Called with message: 📝 Processing response..., level: info
2025-10-20 19:46:51.030 | 2025-10-20 19:46:51 INFO ws_daemon: [WS_PROGRESS_NOTIFIER] Successfully sent progress + heartbeat frames
2025-10-20 19:46:51.111 | 2025-10-20 19:46:51 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.c60eeee8-3641-4332-b4e0-1eda1bf3882d "HTTP/2 200 OK"
2025-10-20 19:46:51.186 | 2025-10-20 19:46:51 INFO httpx: HTTP Request: POST https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations "HTTP/2 201 Created"
2025-10-20 19:46:51.187 | 2025-10-20 19:46:51 INFO src.storage.supabase_client: Saved conversation: c60eeee8-3641-4332-b4e0-1eda1bf3882d -> 86c3a246-07dd-498c-b879-07ad02b750d6
2025-10-20 19:46:51.187 | 2025-10-20 19:46:51 INFO src.storage.conversation_mapper: Created new conversation: c60eeee8-3641-4332-b4e0-1eda1bf3882d -> 86c3a246-07dd-498c-b879-07ad02b750d6
2025-10-20 19:46:51.254 | 2025-10-20 19:46:51 INFO httpx: HTTP Request: POST https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/messages "HTTP/2 201 Created"
2025-10-20 19:46:51.255 | 2025-10-20 19:46:51 INFO utils.conversation.supabase_memory: [CONV_QUEUE] Processed update for c60eeee8-3641-4332-b4e0-1eda1bf3882d
2025-10-20 19:46:51.312 | 2025-10-20 19:46:51 INFO httpx: HTTP Request: POST https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/messages "HTTP/2 201 Created"
2025-10-20 19:46:51.313 | 2025-10-20 19:46:51 INFO utils.conversation.supabase_memory: [CONV_QUEUE] Processed update for c60eeee8-3641-4332-b4e0-1eda1bf3882d
2025-10-20 19:46:51.313 | 2025-10-20 19:46:51 INFO src.server.handlers.request_handler: Tool 'chat' execution completed
2025-10-20 19:46:51.313 | 2025-10-20 19:46:51 INFO ws_daemon: === TOOL CALL COMPLETE ===
2025-10-20 19:46:51.313 | 2025-10-20 19:46:51 INFO ws_daemon: Tool: chat
2025-10-20 19:46:51.313 | 2025-10-20 19:46:51 INFO ws_daemon: Duration: 7.78s
2025-10-20 19:46:51.314 | 2025-10-20 19:46:51 INFO ws_daemon: Provider: GLM
2025-10-20 19:46:51.314 | 2025-10-20 19:46:51 INFO ws_daemon: Session: 3e321057-92f7-45e5-adaa-dafe0c2def32
2025-10-20 19:46:51.314 | 2025-10-20 19:46:51 INFO ws_daemon: Request ID: e122809b-2247-47d1-891b-6ec8c04f869a
2025-10-20 19:46:51.314 | 2025-10-20 19:46:51 INFO ws_daemon: Success: True
2025-10-20 19:46:51.314 | 2025-10-20 19:46:51 INFO ws_daemon: === END ===
2025-10-20 19:47:00.366 | 2025-10-20 19:47:00 INFO ws_daemon: === TOOL CALL RECEIVED ===
2025-10-20 19:47:00.367 | 2025-10-20 19:47:00 INFO ws_daemon: Session: 3e321057-92f7-45e5-adaa-dafe0c2def32
2025-10-20 19:47:00.367 | 2025-10-20 19:47:00 INFO ws_daemon: Tool: debug (original: debug)
2025-10-20 19:47:00.367 | 2025-10-20 19:47:00 INFO ws_daemon: Request ID: 8b2aa1f2-f9d9-42f6-b6c9-020ac0eb302a
2025-10-20 19:47:00.368 | 2025-10-20 19:47:00 INFO ws_daemon: Arguments (first 500 chars): {
2025-10-20 19:47:00.368 |   "step": "Test the circuit breaker fix by investigating a simple hypothetical issue: \"Why might a Python function return None unexpectedly?\" This is a simple test case to verify the workflow tool works without hanging.",
2025-10-20 19:47:00.368 |   "step_number": 1,
2025-10-20 19:47:00.368 |   "total_steps": 1,
2025-10-20 19:47:00.368 |   "next_step_required": false,
2025-10-20 19:47:00.368 |   "findings": "This is a test to verify the debug workflow tool works correctly after Phase 1 fixes. Testing that circuit breaker doesn't cause infinite loops.",
2025-10-20 19:47:00.368 |   "confidence": "high",
2025-10-20 19:47:00.368 |   "model": "glm-4
2025-10-20 19:47:00.368 | 2025-10-20 19:47:00 INFO ws_daemon: === PROCESSING ===
2025-10-20 19:47:00.369 | 2025-10-20 19:47:00 INFO src.server.handlers.request_handler_init: MCP tool call: debug req_id=511521e4-cf57-4d6e-a921-229614c01de8
2025-10-20 19:47:00.369 | 2025-10-20 19:47:00 INFO mcp_activity: TOOL_CALL: debug with 10 arguments req_id=511521e4-cf57-4d6e-a921-229614c01de8
2025-10-20 19:47:00.369 | 2025-10-20 19:47:00 INFO src.server.handlers.request_handler: MCP tool call: debug req_id=511521e4-cf57-4d6e-a921-229614c01de8
2025-10-20 19:47:00.369 | 2025-10-20 19:47:00 INFO mcp_activity: [PROGRESS] tool=debug req_id=511521e4-cf57-4d6e-a921-229614c01de8 elapsed=0.0s — heartbeat
2025-10-20 19:47:00.369 | 2025-10-20 19:47:00 INFO mcp_activity: [PROGRESS] debug: Starting step 1/1 - Test the circuit breaker fix by investigating a simple hypothetical issue: "Why 
2025-10-20 19:47:00.369 | 2025-10-20 19:47:00 INFO utils.conversation.threads: [STORAGE_INTEGRATION] Creating thread 75322ce2-acbb-4fd5-9b30-03adcebe4d12 using storage factory
2025-10-20 19:47:00.373 | 2025-10-20 19:47:00 INFO mcp_activity: [PROGRESS] debug: Processed step data. Updating findings...
2025-10-20 19:47:00.373 | 2025-10-20 19:47:00 INFO mcp_activity: [PROGRESS] debug: Finalizing - calling expert analysis if required...
2025-10-20 19:47:00.373 | 2025-10-20 19:47:00 INFO mcp_activity: [PROGRESS] debug: Step 1/1 complete
2025-10-20 19:47:00.373 | 2025-10-20 19:47:00 INFO utils.conversation.supabase_memory: [ASYNC_SUPABASE] Submitting write to async queue for 75322ce2-acbb-4fd5-9b30-03adcebe4d12
2025-10-20 19:47:00.373 | 2025-10-20 19:47:00 INFO utils.conversation.supabase_memory: [ASYNC_SUPABASE] Queued write for 75322ce2-acbb-4fd5-9b30-03adcebe4d12
2025-10-20 19:47:00.373 | 2025-10-20 19:47:00 INFO utils.performance.timing: [TIMING] SupabaseMemory.add_turn completed in 0.000s
2025-10-20 19:47:00.373 | 2025-10-20 19:47:00 INFO tools.workflow.orchestration: [SERIALIZATION_DEBUG] About to serialize response_data for debug
2025-10-20 19:47:00.373 | 2025-10-20 19:47:00 INFO ws_daemon: [WS_PROGRESS_NOTIFIER] Called with message: debug: Starting step 1/1 - Test the circuit breaker fix by investigating a simple hypothetical issue: "Why , level: info
2025-10-20 19:47:00.373 | 2025-10-20 19:47:00 INFO tools.workflow.orchestration: [SERIALIZATION_DEBUG] response_data type: <class 'dict'>
2025-10-20 19:47:00.373 | 2025-10-20 19:47:00 INFO tools.workflow.orchestration: [SERIALIZATION_DEBUG] response_data keys: dict_keys(['status', 'step_number', 'total_steps', 'next_step_required', 'continuation_id', 'next_call', 'next_steps', 'investigation_status', 'investigation_complete', 'metadata'])
2025-10-20 19:47:00.373 | 2025-10-20 19:47:00 INFO tools.workflow.orchestration: [SERIALIZATION_DEBUG] JSON serialization successful, length: 1119
2025-10-20 19:47:00.373 | 2025-10-20 19:47:00 INFO tools.workflow.orchestration: [SERIALIZATION_DEBUG] About to create TextContent and return
2025-10-20 19:47:00.373 | 2025-10-20 19:47:00 INFO tools.workflow.orchestration: [SERIALIZATION_DEBUG] TextContent created, about to return
2025-10-20 19:47:00.374 | 2025-10-20 19:47:00 INFO ws_daemon: [WS_PROGRESS_NOTIFIER] Successfully sent progress + heartbeat frames
2025-10-20 19:47:00.374 | 2025-10-20 19:47:00 INFO ws_daemon: [WS_PROGRESS_NOTIFIER] Called with message: debug: Processed step data. Updating findings..., level: info
2025-10-20 19:47:00.374 | 2025-10-20 19:47:00 INFO ws_daemon: [WS_PROGRESS_NOTIFIER] Successfully sent progress + heartbeat frames
2025-10-20 19:47:00.375 | 2025-10-20 19:47:00 INFO ws_daemon: [WS_PROGRESS_NOTIFIER] Called with message: debug: Finalizing - calling expert analysis if required..., level: info
2025-10-20 19:47:00.375 | 2025-10-20 19:47:00 INFO ws_daemon: [WS_PROGRESS_NOTIFIER] Successfully sent progress + heartbeat frames
2025-10-20 19:47:00.375 | 2025-10-20 19:47:00 INFO ws_daemon: [WS_PROGRESS_NOTIFIER] Called with message: debug: Step 1/1 complete, level: info
2025-10-20 19:47:00.376 | 2025-10-20 19:47:00 INFO ws_daemon: [WS_PROGRESS_NOTIFIER] Successfully sent progress + heartbeat frames
2025-10-20 19:47:00.470 | 2025-10-20 19:47:00 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.75322ce2-acbb-4fd5-9b30-03adcebe4d12 "HTTP/2 200 OK"
2025-10-20 19:47:00.526 | 2025-10-20 19:47:00 INFO httpx: HTTP Request: POST https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations "HTTP/2 201 Created"
2025-10-20 19:47:00.527 | 2025-10-20 19:47:00 INFO src.storage.supabase_client: Saved conversation: 75322ce2-acbb-4fd5-9b30-03adcebe4d12 -> d1908009-249d-44f7-8a87-6f0026d18658
2025-10-20 19:47:00.527 | 2025-10-20 19:47:00 INFO src.storage.conversation_mapper: Created new conversation: 75322ce2-acbb-4fd5-9b30-03adcebe4d12 -> d1908009-249d-44f7-8a87-6f0026d18658
2025-10-20 19:47:00.585 | 2025-10-20 19:47:00 INFO httpx: HTTP Request: POST https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/messages "HTTP/2 201 Created"
2025-10-20 19:47:00.586 | 2025-10-20 19:47:00 INFO utils.conversation.supabase_memory: [CONV_QUEUE] Processed update for 75322ce2-acbb-4fd5-9b30-03adcebe4d12
2025-10-20 19:47:00.586 | 2025-10-20 19:47:00 INFO src.server.handlers.request_handler: Tool 'debug' execution completed
2025-10-20 19:47:00.586 | 2025-10-20 19:47:00 INFO ws_daemon: === TOOL CALL COMPLETE ===
2025-10-20 19:47:00.587 | 2025-10-20 19:47:00 INFO ws_daemon: Tool: debug
2025-10-20 19:47:00.587 | 2025-10-20 19:47:00 INFO ws_daemon: Duration: 0.22s
2025-10-20 19:47:00.587 | 2025-10-20 19:47:00 INFO ws_daemon: Provider: GLM
2025-10-20 19:47:00.587 | 2025-10-20 19:47:00 INFO ws_daemon: Session: 3e321057-92f7-45e5-adaa-dafe0c2def32
2025-10-20 19:47:00.588 | 2025-10-20 19:47:00 INFO ws_daemon: Request ID: 8b2aa1f2-f9d9-42f6-b6c9-020ac0eb302a
2025-10-20 19:47:00.588 | 2025-10-20 19:47:00 INFO ws_daemon: Success: True
2025-10-20 19:47:00.588 | 2025-10-20 19:47:00 INFO ws_daemon: === END ===
2025-10-20 19:47:28.732 | 2025-10-20 19:47:28 INFO ws_daemon: === TOOL CALL RECEIVED ===
2025-10-20 19:47:28.732 | 2025-10-20 19:47:28 INFO ws_daemon: Session: 3e321057-92f7-45e5-adaa-dafe0c2def32
2025-10-20 19:47:28.732 | 2025-10-20 19:47:28 INFO ws_daemon: Tool: chat (original: chat)
2025-10-20 19:47:28.733 | 2025-10-20 19:47:28 INFO ws_daemon: Request ID: b686da2f-739c-4cd3-b002-0741f1a21d30
2025-10-20 19:47:28.733 | 2025-10-20 19:47:28 INFO ws_daemon: Arguments (first 500 chars): {
2025-10-20 19:47:28.733 |   "prompt": "This is a follow-up message to test conversation continuation and cache performance.",
2025-10-20 19:47:28.733 |   "continuation_id": "c60eeee8-3641-4332-b4e0-1eda1bf3882d",
2025-10-20 19:47:28.733 |   "model": "glm-4.5-flash",
2025-10-20 19:47:28.733 |   "use_websearch": false
2025-10-20 19:47:28.733 | }
2025-10-20 19:47:28.733 | 2025-10-20 19:47:28 INFO ws_daemon: === PROCESSING ===
2025-10-20 19:47:28.734 | 2025-10-20 19:47:28 INFO src.server.handlers.request_handler_init: MCP tool call: chat req_id=9dd8b6a9-2f9a-4c9f-b130-16afe9c7b32e
2025-10-20 19:47:28.734 | 2025-10-20 19:47:28 INFO mcp_activity: TOOL_CALL: chat with 6 arguments req_id=9dd8b6a9-2f9a-4c9f-b130-16afe9c7b32e
2025-10-20 19:47:28.734 | 2025-10-20 19:47:28 INFO src.server.handlers.request_handler: MCP tool call: chat req_id=9dd8b6a9-2f9a-4c9f-b130-16afe9c7b32e
2025-10-20 19:47:28.734 | 2025-10-20 19:47:28 INFO mcp_activity: CONVERSATION_RESUME: chat resuming thread c60eeee8-3641-4332-b4e0-1eda1bf3882d req_id=9dd8b6a9-2f9a-4c9f-b130-16afe9c7b32e
2025-10-20 19:47:28.734 | 2025-10-20 19:47:28 ERROR ws_daemon: === TOOL CALL FAILED ===
2025-10-20 19:47:28.734 | 2025-10-20 19:47:28 ERROR ws_daemon: Tool: chat
2025-10-20 19:47:28.735 | 2025-10-20 19:47:28 ERROR ws_daemon: Duration: 0.00s
2025-10-20 19:47:28.735 | 2025-10-20 19:47:28 ERROR ws_daemon: Session: 3e321057-92f7-45e5-adaa-dafe0c2def32
2025-10-20 19:47:28.735 | 2025-10-20 19:47:28 ERROR ws_daemon: Request ID: b686da2f-739c-4cd3-b002-0741f1a21d30
2025-10-20 19:47:28.735 | 2025-10-20 19:47:28 ERROR ws_daemon: Error: cannot import name 'build_conversation_history' from 'utils.conversation.memory' (/app/utils/conversation/memory.py)
2025-10-20 19:47:28.740 | 2025-10-20 19:47:28 ERROR ws_daemon: Full traceback:
2025-10-20 19:47:28.740 | Traceback (most recent call last):
2025-10-20 19:47:28.740 |   File "/app/src/daemon/ws_server.py", line 957, in _handle_message
2025-10-20 19:47:28.740 |     outputs = await asyncio.wait_for(tool_task, timeout=PROGRESS_INTERVAL)
2025-10-20 19:47:28.740 |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-10-20 19:47:28.740 |   File "/usr/local/lib/python3.13/asyncio/tasks.py", line 507, in wait_for
2025-10-20 19:47:28.740 |     return await fut
2025-10-20 19:47:28.740 |            ^^^^^^^^^
2025-10-20 19:47:28.740 |   File "/app/src/server/handlers/request_handler.py", line 86, in handle_call_tool
2025-10-20 19:47:28.740 |     arguments = await reconstruct_context(name, arguments, req_id)
2025-10-20 19:47:28.740 |                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-10-20 19:47:28.740 |   File "/app/src/server/handlers/request_handler_context.py", line 53, in reconstruct_context
2025-10-20 19:47:28.740 |     arguments = await reconstruct_thread_context(arguments)
2025-10-20 19:47:28.740 |                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-10-20 19:47:28.741 |   File "/app/src/server/context/thread_context.py", line 96, in reconstruct_thread_context
2025-10-20 19:47:28.741 |     from utils.conversation.memory import add_turn, build_conversation_history, get_thread
2025-10-20 19:47:28.741 | ImportError: cannot import name 'build_conversation_history' from 'utils.conversation.memory' (/app/utils/conversation/memory.py)
2025-10-20 19:47:28.741 | 2025-10-20 19:47:28 ERROR ws_daemon: === END ===
2025-10-20 19:49:32.792 | 2025-10-20 19:49:32 INFO ws_daemon: [RESILIENT_WS] Stopped resilient WebSocket manager
2025-10-20 19:49:32.791 | 2025-10-20 19:49:32 INFO src.daemon.connection_manager: Connection unregistered: a1537040-3058-4390-b9df-2853e4464f02 from 172.18.0.1 (duration: 242.01s, remaining: 1)
2025-10-20 19:49:32.792 | 2025-10-20 19:49:32 INFO src.daemon.session_manager: [SESSION_MANAGER] Removed session 3e321057-92f7-45e5-adaa-dafe0c2def32 (total sessions: 1)
2025-10-20 19:49:32.792 | 2025-10-20 19:49:32 INFO src.daemon.connection_manager: Connection unregistered: 4334685b-3453-4124-9bdb-5650d3e9549b from 172.18.0.1 (duration: 219.59s, remaining: 0)
2025-10-20 19:49:32.792 | 2025-10-20 19:49:32 INFO src.daemon.session_manager: [SESSION_MANAGER] Removed session 56ce3cc7-24bc-428a-b8d6-2782821b8ce6 (total sessions: 0)
2025-10-20 19:49:32.792 | 2025-10-20 19:49:32 INFO src.monitoring.resilient_websocket: Stopped retry background task
2025-10-20 19:49:32.792 | 2025-10-20 19:49:32 INFO src.monitoring.resilient_websocket: Stopped cleanup background task
2025-10-20 19:49:32.793 | 2025-10-20 19:49:32 INFO root: [ASYNC_LOGGING] Shutting down async logging listener
2025-10-20 19:49:39.123 | 2025-10-20 19:49:39 INFO root: [ASYNC_LOGGING] Async-safe logging configured successfully
2025-10-20 19:49:39.124 | 2025-10-20 19:49:39 INFO root: [LOGGING] Configured websockets library logging to suppress handshake noise
2025-10-20 19:49:39.123 | 2025-10-20 19:49:39 INFO ws_daemon: [AUTH] Authentication enabled (token first 10 chars): test-token...
2025-10-20 19:49:39.974 | 2025-10-20 19:49:39 INFO src.bootstrap.singletons: Building tool registry (first-time initialization)
2025-10-20 19:49:40.420 | 2025-10-20 19:49:40 INFO src.bootstrap.singletons: Tool registry built successfully with 30 tools
2025-10-20 19:49:40.420 | 2025-10-20 19:49:40 INFO src.daemon.session_manager: [SESSION_MANAGER] Initialized with timeout=3600s, max_sessions=5, cleanup_interval=300s
2025-10-20 19:49:40.435 | 2025-10-20 19:49:40 INFO src.middleware.correlation: [CORRELATION] Correlation ID logging configured
2025-10-20 19:49:40.435 | 2025-10-20 19:49:40 INFO __main__: [MAIN] Correlation ID logging configured
2025-10-20 19:49:40.435 | 2025-10-20 19:49:40 INFO src.daemon.monitoring_endpoint: [MONITORING] Broadcast hook installed
2025-10-20 19:49:40.435 | 2025-10-20 19:49:40 INFO __main__: [MAIN] Monitoring broadcast hook configured
2025-10-20 19:49:40.449 | 2025-10-20 19:49:40 INFO src.monitoring.metrics: [METRICS] Prometheus metrics server started on port 8000
2025-10-20 19:49:40.449 | 2025-10-20 19:49:40 INFO src.monitoring.metrics: [METRICS] Metrics available at http://localhost:8000/metrics
2025-10-20 19:49:40.449 | 2025-10-20 19:49:40 INFO __main__: [MAIN] Metrics server started on port 8000
2025-10-20 19:49:40.449 | 2025-10-20 19:49:40 INFO __main__: [MAIN] Monitoring dashboard will be available at http://localhost:8080/monitoring_dashboard.html
2025-10-20 19:49:40.449 | 2025-10-20 19:49:40 INFO __main__: [MAIN] Health check will be available at http://localhost:8082/health
2025-10-20 19:49:40.449 | 2025-10-20 19:49:40 INFO __main__: [MAIN] Periodic metrics updates enabled (60s interval)
2025-10-20 19:49:40.449 | 2025-10-20 19:49:40 INFO __main__: [MAIN] Starting 4 servers concurrently
2025-10-20 19:49:40.451 | 2025-10-20 19:49:40 INFO ws_daemon: Configuring providers and registering tools at daemon startup...
2025-10-20 19:49:40.452 | 2025-10-20 19:49:40 INFO src.bootstrap.singletons: Configuring providers (first-time initialization)
2025-10-20 19:49:40.452 | 2025-10-20 19:49:40 INFO src.server.providers.provider_detection: Kimi API key found - Moonshot AI models available
2025-10-20 19:49:40.452 | 2025-10-20 19:49:40 INFO src.server.providers.provider_detection: GLM API key found - ZhipuAI models available
2025-10-20 19:49:40.452 | 2025-10-20 19:49:40 INFO src.server.providers.provider_diagnostics: Available providers: Kimi, GLM
2025-10-20 19:49:40.452 | 2025-10-20 19:49:40 INFO src.providers.kimi: Kimi provider using centralized timeout: 240s
2025-10-20 19:49:40.452 | 2025-10-20 19:49:40 INFO root: Model allow-list not configured for OpenAI Compatible - all models permitted. To restrict access, set KIMI_ALLOWED_MODELS with comma-separated model names.
2025-10-20 19:49:40.452 | 2025-10-20 19:49:40 INFO root: Using extended timeouts for custom endpoint: https://api.moonshot.ai/v1
2025-10-20 19:49:40.564 | 2025-10-20 19:49:40 INFO src.providers.glm: GLM provider using SDK with base_url=https://api.z.ai/api/paas/v4, timeout=120s, max_retries=3
2025-10-20 19:49:40.564 | 2025-10-20 19:49:40 INFO src.server.providers.provider_diagnostics: Providers configured: KIMI, GLM; GLM models: 6; Kimi models: 18
2025-10-20 19:49:40.571 | 2025-10-20 19:49:40 INFO ws_daemon: Providers configured successfully. Total tools available: 30
2025-10-20 19:49:40.571 | 2025-10-20 19:49:40 INFO src.server.providers.provider_restrictions: No model restrictions configured - all models allowed
2025-10-20 19:49:40.571 | 2025-10-20 19:49:40 INFO src.bootstrap.singletons: Providers configured successfully
2025-10-20 19:49:40.572 | 2025-10-20 19:49:40 INFO ws_daemon: Initializing conversation storage at daemon startup...
2025-10-20 19:49:40.576 | 2025-10-20 19:49:40 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Initializing conversation storage at startup...
2025-10-20 19:49:40.576 | 2025-10-20 19:49:40 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Creating conversation storage: backend=dual, fallback=True
2025-10-20 19:49:40.686 | 2025-10-20 19:49:40 INFO src.storage.supabase_client: [SUPABASE_INIT] SUPABASE_URL=SET
2025-10-20 19:49:40.686 | 2025-10-20 19:49:40 INFO src.storage.supabase_client: [SUPABASE_INIT] SUPABASE_SERVICE_ROLE_KEY=SET
2025-10-20 19:49:40.686 | 2025-10-20 19:49:40 INFO src.storage.supabase_client: Supabase storage initialized: https://mxaazuhlqewmkweewyaz.supabase.co
2025-10-20 19:49:41.106 | 2025-10-20 19:49:41 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/schema_version?select=version&limit=1 "HTTP/2 200 OK"
2025-10-20 19:49:41.108 | 2025-10-20 19:49:41 INFO utils.caching.base_cache_manager: [CONVERSATION_CACHE] L1 initialized: TTLCache(maxsize=100, ttl=300s)
2025-10-20 19:49:41.108 | 2025-10-20 19:49:41 INFO utils.caching.base_cache_manager: [CONVERSATION_CACHE] Base cache manager initialized
2025-10-20 19:49:41.108 | 2025-10-20 19:49:41 INFO utils.conversation.cache_manager: [CACHE_MANAGER] Conversation cache manager initialized (L1_TTL=300s, L2_TTL=1800s)
2025-10-20 19:49:41.108 | 2025-10-20 19:49:41 INFO utils.conversation.supabase_memory: [ASYNC_SUPABASE] Will use async queue for writes
2025-10-20 19:49:41.108 | 2025-10-20 19:49:41 INFO utils.infrastructure.storage_backend: Redis storage initialized (ttl=86400s) at redis://:****@redis:6379/0
2025-10-20 19:49:41.108 | 2025-10-20 19:49:41 INFO ws_daemon: Conversation storage initialized successfully
2025-10-20 19:49:41.108 | 2025-10-20 19:49:41 INFO utils.infrastructure.storage_backend: Initialized Redis conversation storage
2025-10-20 19:49:41.108 | 2025-10-20 19:49:41 INFO utils.conversation.storage_factory: Initialized dual storage (Supabase + in-memory) with context engineering
2025-10-20 19:49:41.108 | 2025-10-20 19:49:41 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Singleton storage instance created: DualStorageConversation
2025-10-20 19:49:41.108 | 2025-10-20 19:49:41 INFO utils.conversation.storage_factory: [STORAGE_FACTORY] Startup initialization complete: DualStorageConversation
2025-10-20 19:49:41.109 | 2025-10-20 19:49:41 INFO ws_daemon: Pre-warming external connections...
2025-10-20 19:49:41.114 | 2025-10-20 19:49:41 INFO src.daemon.warmup: [WARMUP] ========================================
2025-10-20 19:49:41.114 | 2025-10-20 19:49:41 INFO src.daemon.warmup: [WARMUP] Starting connection warmup...
2025-10-20 19:49:41.114 | 2025-10-20 19:49:41 INFO src.daemon.warmup: [WARMUP] ========================================
2025-10-20 19:49:41.114 | 2025-10-20 19:49:41 INFO src.daemon.monitoring_endpoint: [MONITORING] Starting monitoring server on 0.0.0.0:8080
2025-10-20 19:49:41.114 | 2025-10-20 19:49:41 INFO src.monitoring.metrics: [METRICS] Starting periodic updates (interval: 60s)
2025-10-20 19:49:41.215 | 2025-10-20 19:49:41 INFO src.daemon.warmup: [WARMUP] Initializing Supabase connection...
2025-10-20 19:49:41.321 | 2025-10-20 19:49:41 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=id&limit=1 "HTTP/2 200 OK"
2025-10-20 19:49:41.321 | 2025-10-20 19:49:41 INFO src.daemon.warmup: [WARMUP] ✅ Supabase connection warmed up successfully (0.106s)
2025-10-20 19:49:41.321 | 2025-10-20 19:49:41 INFO src.daemon.warmup: [WARMUP] Initializing Redis connection...
2025-10-20 19:49:41.343 | 2025-10-20 19:49:41 INFO src.daemon.monitoring_endpoint: [MONITORING] Monitoring server running on ws://0.0.0.0:8080
2025-10-20 19:49:41.343 | 2025-10-20 19:49:41 INFO src.daemon.monitoring_endpoint: [MONITORING] Dashboard available at http://0.0.0.0:8080/monitoring_dashboard.html
2025-10-20 19:49:41.343 | 2025-10-20 19:49:41 INFO src.daemon.health_endpoint: [HEALTH] Health check server running on http://0.0.0.0:8082/health
2025-10-20 19:49:41.344 | 2025-10-20 19:49:41 INFO ws_daemon: External connections pre-warmed successfully
2025-10-20 19:49:41.344 | 2025-10-20 19:49:41 INFO src.daemon.warmup: [WARMUP] ✅ Redis connection warmed up successfully (0.023s)
2025-10-20 19:49:41.344 | 2025-10-20 19:49:41 INFO src.daemon.warmup: [WARMUP] ========================================
2025-10-20 19:49:41.344 | 2025-10-20 19:49:41 INFO src.daemon.warmup: [WARMUP] ✅ All connections warmed up successfully (0.231s)
2025-10-20 19:49:41.344 | 2025-10-20 19:49:41 INFO src.daemon.warmup: [WARMUP] ========================================
2025-10-20 19:49:41.345 | 2025-10-20 19:49:41 INFO ws_daemon: Initializing conversation queue...
2025-10-20 19:49:41.350 | 2025-10-20 19:49:41 INFO src.daemon.conversation_queue: [CONV_QUEUE] Consumer started (max_size=1000, warning_threshold=500)
2025-10-20 19:49:41.350 | 2025-10-20 19:49:41 INFO src.daemon.conversation_queue: [CONV_QUEUE] Global queue initialized
2025-10-20 19:49:41.350 | 2025-10-20 19:49:41 INFO ws_daemon: Conversation queue initialized successfully
2025-10-20 19:49:41.350 | 2025-10-20 19:49:41 INFO ws_daemon: Initializing session semaphore manager...
2025-10-20 19:49:41.355 | 2025-10-20 19:49:41 INFO src.daemon.session_semaphore_manager: [SESSION_SEM] Initialized SessionSemaphoreManager (max_concurrent_per_session=5, cleanup_interval=300s, inactive_timeout=300s)
2025-10-20 19:49:41.355 | 2025-10-20 19:49:41 INFO src.daemon.session_semaphore_manager: [SESSION_SEM] Cleanup task started
2025-10-20 19:49:41.355 | 2025-10-20 19:49:41 INFO src.daemon.session_semaphore_manager: [SESSION_SEM] Global session semaphore manager initialized
2025-10-20 19:49:41.355 | 2025-10-20 19:49:41 INFO ws_daemon: Session semaphore manager initialized successfully
2025-10-20 19:49:41.355 | 2025-10-20 19:49:41 INFO ws_daemon: Validating timeout hierarchy...
2025-10-20 19:49:41.355 | 2025-10-20 19:49:41 INFO ws_daemon: Timeout hierarchy validated: daemon=270s, tool=180.0s (ratio=1.50x)
2025-10-20 19:49:41.356 | 2025-10-20 19:49:41 INFO src.monitoring.resilient_websocket: Started retry background task
2025-10-20 19:49:41.356 | 2025-10-20 19:49:41 INFO src.monitoring.resilient_websocket: Started cleanup background task
2025-10-20 19:49:41.356 | 2025-10-20 19:49:41 INFO ws_daemon: [RESILIENT_WS] Started resilient WebSocket manager with background tasks
2025-10-20 19:49:41.356 | 2025-10-20 19:49:41 INFO ws_daemon: Starting WS daemon on ws://0.0.0.0:8079
2025-10-20 19:49:41.358 | 2025-10-20 19:49:41 INFO src.daemon.conversation_queue: [CONV_QUEUE] Consumer loop started
2025-10-20 19:49:41.358 | 2025-10-20 19:49:41 INFO src.daemon.session_semaphore_manager: [SESSION_SEM] Cleanup task started
2025-10-20 19:49:41.358 | 2025-10-20 19:49:41 INFO src.monitoring.resilient_websocket: Starting pending message retry task
2025-10-20 19:49:41.358 | 2025-10-20 19:49:41 INFO src.monitoring.resilient_websocket: Starting expired message cleanup task
2025-10-20 19:49:46.276 | 2025-10-20 19:49:46 INFO src.daemon.connection_manager: ConnectionManager initialized: max_connections=1000, max_per_ip=10
2025-10-20 19:49:46.276 | 2025-10-20 19:49:46 INFO src.daemon.connection_manager: Connection registered: f580c68d-cff5-47f8-ad52-9d69e81e692c from 172.18.0.1 (total: 1, ip_total: 1)
2025-10-20 19:49:46.276 | 2025-10-20 19:49:46 INFO ws_daemon: [WS_CONNECTION] New connection from 172.18.0.1:35910 (id: f580c68d-cff5-47f8-ad52-9d69e81e692c)
2025-10-20 19:49:46.277 | 2025-10-20 19:49:46 INFO src.daemon.session_manager: [SESSION_MANAGER] Created session 08f214ae-e9ed-40c6-8d47-aecd946d54a1 (total sessions: 1)
2025-10-20 19:49:46.278 | 2025-10-20 19:49:46 INFO src.resilience.rate_limiter: RateLimiter initialized: global=1000/100.0t/s, ip=100/10.0t/s, user=50/5.0t/s, cleanup_interval=3600s
2025-10-20 19:49:46.278 | 2025-10-20 19:49:46 INFO ws_daemon: === TOOL CALL RECEIVED ===
2025-10-20 19:49:46.278 | 2025-10-20 19:49:46 INFO ws_daemon: Session: 08f214ae-e9ed-40c6-8d47-aecd946d54a1
2025-10-20 19:49:46.278 | 2025-10-20 19:49:46 INFO ws_daemon: Tool: chat (original: chat)
2025-10-20 19:49:46.279 | 2025-10-20 19:49:46 INFO ws_daemon: Request ID: 0af2a3b0-1103-4152-99ef-d08ba947099e
2025-10-20 19:49:46.279 | 2025-10-20 19:49:46 INFO ws_daemon: Arguments (first 500 chars): {
2025-10-20 19:49:46.279 |   "prompt": "This is a follow-up message to test conversation continuation and cache performance after fixing all imports.",
2025-10-20 19:49:46.279 |   "continuation_id": "c60eeee8-3641-4332-b4e0-1eda1bf3882d",
2025-10-20 19:49:46.279 |   "model": "glm-4.5-flash",
2025-10-20 19:49:46.279 |   "use_websearch": false
2025-10-20 19:49:46.279 | }
2025-10-20 19:49:46.279 | 2025-10-20 19:49:46 INFO ws_daemon: === PROCESSING ===
2025-10-20 19:49:46.280 | 2025-10-20 19:49:46 INFO src.server.handlers.request_handler_init: MCP tool call: chat req_id=16de3c04-7fce-47bf-81ba-daf549021402
2025-10-20 19:49:46.285 | 2025-10-20 19:49:46 INFO mcp_activity: TOOL_CALL: chat with 6 arguments req_id=16de3c04-7fce-47bf-81ba-daf549021402
2025-10-20 19:49:46.291 | 2025-10-20 19:49:46 INFO src.server.handlers.request_handler: MCP tool call: chat req_id=16de3c04-7fce-47bf-81ba-daf549021402
2025-10-20 19:49:46.291 | 2025-10-20 19:49:46 INFO mcp_activity: CONVERSATION_RESUME: chat resuming thread c60eeee8-3641-4332-b4e0-1eda1bf3882d req_id=16de3c04-7fce-47bf-81ba-daf549021402
2025-10-20 19:49:46.291 | 2025-10-20 19:49:46 INFO utils.conversation.threads: [STORAGE_INTEGRATION] Storage factory available - will use configured backend
2025-10-20 19:49:46.291 | 2025-10-20 19:49:46 INFO utils.conversation.threads: [STORAGE_INTEGRATION] Created cached storage backend instance
2025-10-20 19:49:46.293 | 2025-10-20 19:49:46 INFO utils.caching.base_cache_manager: [CONVERSATION_CACHE] L2 (Redis) connected: redis:6379/0
2025-10-20 19:49:46.371 | 2025-10-20 19:49:46 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.c60eeee8-3641-4332-b4e0-1eda1bf3882d "HTTP/2 200 OK"
2025-10-20 19:49:46.373 | 2025-10-20 19:49:46 INFO utils.performance.timing: [TIMING] SupabaseMemory.get_conversation_by_continuation_id took 0.079s
2025-10-20 19:49:46.430 | 2025-10-20 19:49:46 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/messages?select=%2A&conversation_id=eq.86c3a246-07dd-498c-b879-07ad02b750d6&order=created_at.asc&limit=5 "HTTP/2 200 OK"
2025-10-20 19:49:46.430 | 2025-10-20 19:49:46 INFO utils.performance.timing: [TIMING] SupabaseMemory.get_conversation_messages took 0.058s
2025-10-20 19:49:46.430 | 2025-10-20 19:49:46 INFO utils.conversation.supabase_memory: [CONTEXT_PRUNING] Loaded 2 messages for c60eeee8-3641-4332-b4e0-1eda1bf3882d (limit=5)
2025-10-20 19:49:46.433 | 2025-10-20 19:49:46 INFO utils.conversation.supabase_memory: [REQUEST_CACHE STORE] Cached thread c60eeee8-3641-4332-b4e0-1eda1bf3882d for this request (loaded from Supabase)
2025-10-20 19:49:46.433 | 2025-10-20 19:49:46 INFO utils.performance.timing: [TIMING] SupabaseMemory.get_thread completed in 0.142s
2025-10-20 19:49:46.433 | 2025-10-20 19:49:46 INFO utils.conversation.supabase_memory: [REQUEST_CACHE HIT] Thread c60eeee8-3641-4332-b4e0-1eda1bf3882d from request cache (0ms, no Supabase query)
2025-10-20 19:49:46.433 | 2025-10-20 19:49:46 INFO utils.performance.timing: [TIMING] SupabaseMemory.get_thread completed in 0.000s
2025-10-20 19:49:46.526 | 2025-10-20 19:49:46 INFO utils.conversation.supabase_memory: [ASYNC_SUPABASE] Submitting write to async queue for c60eeee8-3641-4332-b4e0-1eda1bf3882d
2025-10-20 19:49:46.526 | 2025-10-20 19:49:46 INFO utils.conversation.supabase_memory: [ASYNC_SUPABASE] Queued write for c60eeee8-3641-4332-b4e0-1eda1bf3882d
2025-10-20 19:49:46.526 | 2025-10-20 19:49:46 INFO utils.performance.timing: [TIMING] SupabaseMemory.add_turn completed in 0.000s
2025-10-20 19:49:46.595 | 2025-10-20 19:49:46 INFO httpx: HTTP Request: GET https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/conversations?select=%2A&continuation_id=eq.c60eeee8-3641-4332-b4e0-1eda1bf3882d "HTTP/2 200 OK"
2025-10-20 19:49:46.673 | 2025-10-20 19:49:46 INFO httpx: HTTP Request: POST https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/messages "HTTP/2 201 Created"
2025-10-20 19:49:46.674 | 2025-10-20 19:49:46 INFO utils.conversation.supabase_memory: [CONV_QUEUE] Processed update for c60eeee8-3641-4332-b4e0-1eda1bf3882d
2025-10-20 19:49:46.674 | 2025-10-20 19:49:46 ERROR ws_daemon: === TOOL CALL FAILED ===
2025-10-20 19:49:46.675 | 2025-10-20 19:49:46 ERROR ws_daemon: Tool: chat
2025-10-20 19:49:46.675 | 2025-10-20 19:49:46 ERROR ws_daemon: Duration: 0.39s
2025-10-20 19:49:46.675 | 2025-10-20 19:49:46 ERROR ws_daemon: Session: 08f214ae-e9ed-40c6-8d47-aecd946d54a1
2025-10-20 19:49:46.675 | 2025-10-20 19:49:46 ERROR ws_daemon: Request ID: 0af2a3b0-1103-4152-99ef-d08ba947099e
2025-10-20 19:49:46.676 | 2025-10-20 19:49:46 ERROR ws_daemon: Error: name 'build_conversation_history' is not defined
2025-10-20 19:49:46.690 | 2025-10-20 19:49:46 ERROR ws_daemon: Full traceback:
2025-10-20 19:49:46.690 | Traceback (most recent call last):
2025-10-20 19:49:46.690 |   File "/app/src/daemon/ws_server.py", line 957, in _handle_message
2025-10-20 19:49:46.690 |     outputs = await asyncio.wait_for(tool_task, timeout=PROGRESS_INTERVAL)
2025-10-20 19:49:46.690 |               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-10-20 19:49:46.690 |   File "/usr/local/lib/python3.13/asyncio/tasks.py", line 507, in wait_for
2025-10-20 19:49:46.690 |     return await fut
2025-10-20 19:49:46.690 |            ^^^^^^^^^
2025-10-20 19:49:46.690 |   File "/app/src/server/handlers/request_handler.py", line 86, in handle_call_tool
2025-10-20 19:49:46.690 |     arguments = await reconstruct_context(name, arguments, req_id)
2025-10-20 19:49:46.690 |                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-10-20 19:49:46.690 |   File "/app/src/server/handlers/request_handler_context.py", line 53, in reconstruct_context
2025-10-20 19:49:46.690 |     arguments = await reconstruct_thread_context(arguments)
2025-10-20 19:49:46.690 |                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-10-20 19:49:46.690 |   File "/app/src/server/context/thread_context.py", line 256, in reconstruct_thread_context
2025-10-20 19:49:46.690 |     conversation_history, conversation_tokens = build_conversation_history(context, model_context)
2025-10-20 19:49:46.690 |                                                 ^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-10-20 19:49:46.690 | NameError: name 'build_conversation_history' is not defined
2025-10-20 19:49:46.691 | 2025-10-20 19:49:46 ERROR ws_daemon: === END ===
2025-10-20 19:51:44.452 | 2025-10-20 19:51:44 INFO src.daemon.connection_manager: Connection unregistered: f580c68d-cff5-47f8-ad52-9d69e81e692c from 172.18.0.1 (duration: 118.18s, remaining: 0)
2025-10-20 19:51:44.452 | 2025-10-20 19:51:44 INFO src.daemon.session_manager: [SESSION_MANAGER] Removed session 08f214ae-e9ed-40c6-8d47-aecd946d54a1 (total sessions: 0)
2025-10-20 19:51:44.452 | 2025-10-20 19:51:44 INFO src.monitoring.resilient_websocket: Stopped retry background task
2025-10-20 19:51:44.452 | 2025-10-20 19:51:44 INFO src.monitoring.resilient_websocket: Stopped cleanup background task
2025-10-20 19:51:44.452 | 2025-10-20 19:51:44 INFO ws_daemon: [RESILIENT_WS] Stopped resilient WebSocket manager
2025-10-20 19:51:44.457 | 2025-10-20 19:51:44 INFO root: [ASYNC_LOGGING] Shutting down async logging listener
2025-10-20 19:51:50.551 | 2025-10-20 19:51:50 INFO root: [ASYNC_LOGGING] Async-safe logging configured successfully
2025-10-20 19:51:50.552 | 2025-10-20 19:51:50 INFO root: [LOGGING] Configured websockets library logging to suppress handshake noise
2025-10-20 19:51:50.552 | 2025-10-20 19:51:50 INFO ws_daemon: [AUTH] Authentication enabled (token first 10 chars): test-token...
2025-10-20 19:51:51.144 | Traceback (most recent call last):
2025-10-20 19:51:51.145 |   File "/app/scripts/ws/run_ws_daemon.py", line 24, in <module>
2025-10-20 19:51:51.145 |     from src.daemon.ws_server import main_async
2025-10-20 19:51:51.145 |   File "/app/src/daemon/ws_server.py", line 220, in <module>
2025-10-20 19:51:51.145 |     from server import TOOLS as SERVER_TOOLS  # type: ignore
2025-10-20 19:51:51.145 |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-10-20 19:51:51.145 |   File "/app/server.py", line 95, in <module>
2025-10-20 19:51:51.145 |     from src.server.utils import get_follow_up_instructions  # type: ignore
2025-10-20 19:51:51.145 |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-10-20 19:51:51.145 |   File "/app/src/server/__init__.py", line 10, in <module>
2025-10-20 19:51:51.145 |     from .tools import filter_disabled_tools
2025-10-20 19:51:51.145 |   File "/app/src/server/tools/__init__.py", line 5, in <module>
2025-10-20 19:51:51.145 |     from .tool_filter import (
2025-10-20 19:51:51.145 |     ...<6 lines>...
2025-10-20 19:51:51.145 |     )
2025-10-20 19:51:51.145 |   File "/app/src/server/tools/tool_filter.py", line 33, in <module>
2025-10-20 19:51:51.145 |     ESSENTIAL_TOOLS: set[str] = _get_essential_tools()
2025-10-20 19:51:51.145 |                                 ~~~~~~~~~~~~~~~~~~~~^^
2025-10-20 19:51:51.145 |   File "/app/src/server/tools/tool_filter.py", line 21, in _get_essential_tools
2025-10-20 19:51:51.145 |     from tools.registry import TOOL_MAP
2025-10-20 19:51:51.145 |   File "/app/tools/__init__.py", line 6, in <module>
2025-10-20 19:51:51.145 |     from .challenge import ChallengeTool
2025-10-20 19:51:51.145 |   File "/app/tools/challenge.py", line 21, in <module>
2025-10-20 19:51:51.145 |     from .simple.base import SimpleTool
2025-10-20 19:51:51.145 |   File "/app/tools/simple/__init__.py", line 16, in <module>
2025-10-20 19:51:51.145 |     from .base import SimpleTool
2025-10-20 19:51:51.145 | ModuleNotFoundError: No module named 'tools.simple.base'
2025-10-20 19:51:56.499 | 2025-10-20 19:51:56 INFO root: [ASYNC_LOGGING] Async-safe logging configured successfully
2025-10-20 19:51:56.500 | 2025-10-20 19:51:56 INFO root: [LOGGING] Configured websockets library logging to suppress handshake noise
2025-10-20 19:51:56.500 | 2025-10-20 19:51:56 INFO ws_daemon: [AUTH] Authentication enabled (token first 10 chars): test-token...
2025-10-20 19:51:57.104 | Traceback (most recent call last):
2025-10-20 19:51:57.104 |   File "/app/scripts/ws/run_ws_daemon.py", line 24, in <module>
2025-10-20 19:51:57.104 |     from src.daemon.ws_server import main_async
2025-10-20 19:51:57.104 |   File "/app/src/daemon/ws_server.py", line 220, in <module>
2025-10-20 19:51:57.104 |     from server import TOOLS as SERVER_TOOLS  # type: ignore
2025-10-20 19:51:57.104 |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-10-20 19:51:57.104 |   File "/app/server.py", line 95, in <module>
2025-10-20 19:51:57.104 |     from src.server.utils import get_follow_up_instructions  # type: ignore
2025-10-20 19:51:57.104 |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-10-20 19:51:57.104 |   File "/app/src/server/__init__.py", line 10, in <module>
2025-10-20 19:51:57.104 |     from .tools import filter_disabled_tools
2025-10-20 19:51:57.104 |   File "/app/src/server/tools/__init__.py", line 5, in <module>
2025-10-20 19:51:57.104 |     from .tool_filter import (
2025-10-20 19:51:57.104 |     ...<6 lines>...
2025-10-20 19:51:57.104 |     )
2025-10-20 19:51:57.104 |   File "/app/src/server/tools/tool_filter.py", line 33, in <module>
2025-10-20 19:51:57.104 |     ESSENTIAL_TOOLS: set[str] = _get_essential_tools()
2025-10-20 19:51:57.104 |                                 ~~~~~~~~~~~~~~~~~~~~^^
2025-10-20 19:51:57.104 |   File "/app/src/server/tools/tool_filter.py", line 21, in _get_essential_tools
2025-10-20 19:51:57.104 |     from tools.registry import TOOL_MAP
2025-10-20 19:51:57.104 |   File "/app/tools/__init__.py", line 6, in <module>
2025-10-20 19:51:57.104 |     from .challenge import ChallengeTool
2025-10-20 19:51:57.104 |   File "/app/tools/challenge.py", line 21, in <module>
2025-10-20 19:51:57.104 |     from .simple.base import SimpleTool
2025-10-20 19:51:57.104 |   File "/app/tools/simple/__init__.py", line 16, in <module>
2025-10-20 19:51:57.104 |     from .base import SimpleTool
2025-10-20 19:51:57.104 | ModuleNotFoundError: No module named 'tools.simple.base'
2025-10-20 19:52:02.503 | 2025-10-20 19:52:02 INFO root: [ASYNC_LOGGING] Async-safe logging configured successfully
2025-10-20 19:52:02.504 | 2025-10-20 19:52:02 INFO ws_daemon: [AUTH] Authentication enabled (token first 10 chars): test-token...
2025-10-20 19:52:02.505 | 2025-10-20 19:52:02 INFO root: [LOGGING] Configured websockets library logging to suppress handshake noise
2025-10-20 19:52:03.104 | Traceback (most recent call last):
2025-10-20 19:52:03.104 |   File "/app/scripts/ws/run_ws_daemon.py", line 24, in <module>
2025-10-20 19:52:03.104 |     from src.daemon.ws_server import main_async
2025-10-20 19:52:03.104 |   File "/app/src/daemon/ws_server.py", line 220, in <module>
2025-10-20 19:52:03.104 |     from server import TOOLS as SERVER_TOOLS  # type: ignore
2025-10-20 19:52:03.104 |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-10-20 19:52:03.104 |   File "/app/server.py", line 95, in <module>
2025-10-20 19:52:03.104 |     from src.server.utils import get_follow_up_instructions  # type: ignore
2025-10-20 19:52:03.104 |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-10-20 19:52:03.104 |   File "/app/src/server/__init__.py", line 10, in <module>
2025-10-20 19:52:03.104 |     from .tools import filter_disabled_tools
2025-10-20 19:52:03.104 |   File "/app/src/server/tools/__init__.py", line 5, in <module>
2025-10-20 19:52:03.104 |     from .tool_filter import (
2025-10-20 19:52:03.104 |     ...<6 lines>...
2025-10-20 19:52:03.104 |     )
2025-10-20 19:52:03.104 |   File "/app/src/server/tools/tool_filter.py", line 33, in <module>
2025-10-20 19:52:03.104 |     ESSENTIAL_TOOLS: set[str] = _get_essential_tools()
2025-10-20 19:52:03.104 |                                 ~~~~~~~~~~~~~~~~~~~~^^
2025-10-20 19:52:03.104 |   File "/app/src/server/tools/tool_filter.py", line 21, in _get_essential_tools
2025-10-20 19:52:03.104 |     from tools.registry import TOOL_MAP
2025-10-20 19:52:03.104 |   File "/app/tools/__init__.py", line 6, in <module>
2025-10-20 19:52:03.104 |     from .challenge import ChallengeTool
2025-10-20 19:52:03.104 |   File "/app/tools/challenge.py", line 21, in <module>
2025-10-20 19:52:03.104 |     from .simple.base import SimpleTool
2025-10-20 19:52:03.104 |   File "/app/tools/simple/__init__.py", line 16, in <module>
2025-10-20 19:52:03.104 |     from .base import SimpleTool
2025-10-20 19:52:03.104 | ModuleNotFoundError: No module named 'tools.simple.base'
2025-10-20 19:52:08.093 | 2025-10-20 19:52:08 INFO root: [ASYNC_LOGGING] Async-safe logging configured successfully
2025-10-20 19:52:08.094 | 2025-10-20 19:52:08 INFO ws_daemon: [AUTH] Authentication enabled (token first 10 chars): test-token...
2025-10-20 19:52:08.094 | 2025-10-20 19:52:08 INFO root: [LOGGING] Configured websockets library logging to suppress handshake noise
2025-10-20 19:52:08.672 | Traceback (most recent call last):
2025-10-20 19:52:08.672 |   File "/app/scripts/ws/run_ws_daemon.py", line 24, in <module>
2025-10-20 19:52:08.672 |     from src.daemon.ws_server import main_async
2025-10-20 19:52:08.672 |   File "/app/src/daemon/ws_server.py", line 220, in <module>
2025-10-20 19:52:08.672 |     from server import TOOLS as SERVER_TOOLS  # type: ignore
2025-10-20 19:52:08.672 |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-10-20 19:52:08.672 |   File "/app/server.py", line 95, in <module>
2025-10-20 19:52:08.672 |     from src.server.utils import get_follow_up_instructions  # type: ignore
2025-10-20 19:52:08.672 |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-10-20 19:52:08.672 |   File "/app/src/server/__init__.py", line 10, in <module>
2025-10-20 19:52:08.672 |     from .tools import filter_disabled_tools
2025-10-20 19:52:08.672 |   File "/app/src/server/tools/__init__.py", line 5, in <module>
2025-10-20 19:52:08.672 |     from .tool_filter import (
2025-10-20 19:52:08.672 |     ...<6 lines>...
2025-10-20 19:52:08.672 |     )
2025-10-20 19:52:08.672 |   File "/app/src/server/tools/tool_filter.py", line 33, in <module>
2025-10-20 19:52:08.672 |     ESSENTIAL_TOOLS: set[str] = _get_essential_tools()
2025-10-20 19:52:08.672 |                                 ~~~~~~~~~~~~~~~~~~~~^^
2025-10-20 19:52:08.672 |   File "/app/src/server/tools/tool_filter.py", line 21, in _get_essential_tools
2025-10-20 19:52:08.672 |     from tools.registry import TOOL_MAP
2025-10-20 19:52:08.672 |   File "/app/tools/__init__.py", line 6, in <module>
2025-10-20 19:52:08.672 |     from .challenge import ChallengeTool
2025-10-20 19:52:08.672 |   File "/app/tools/challenge.py", line 21, in <module>
2025-10-20 19:52:08.672 |     from .simple.base import SimpleTool
2025-10-20 19:52:08.672 |   File "/app/tools/simple/__init__.py", line 16, in <module>
2025-10-20 19:52:08.672 |     from .base import SimpleTool
2025-10-20 19:52:08.672 | ModuleNotFoundError: No module named 'tools.simple.base'
2025-10-20 19:52:13.772 | 2025-10-20 19:52:13 INFO root: [ASYNC_LOGGING] Async-safe logging configured successfully
2025-10-20 19:52:13.773 | 2025-10-20 19:52:13 INFO ws_daemon: [AUTH] Authentication enabled (token first 10 chars): test-token...
2025-10-20 19:52:13.772 | 2025-10-20 19:52:13 INFO root: [LOGGING] Configured websockets library logging to suppress handshake noise
2025-10-20 19:52:14.359 | Traceback (most recent call last):
2025-10-20 19:52:14.360 |   File "/app/scripts/ws/run_ws_daemon.py", line 24, in <module>
2025-10-20 19:52:14.360 |     from src.daemon.ws_server import main_async
2025-10-20 19:52:14.360 |   File "/app/src/daemon/ws_server.py", line 220, in <module>
2025-10-20 19:52:14.360 |     from server import TOOLS as SERVER_TOOLS  # type: ignore
2025-10-20 19:52:14.360 |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-10-20 19:52:14.360 |   File "/app/server.py", line 95, in <module>
2025-10-20 19:52:14.360 |     from src.server.utils import get_follow_up_instructions  # type: ignore
2025-10-20 19:52:14.360 |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-10-20 19:52:14.360 |   File "/app/src/server/__init__.py", line 10, in <module>
2025-10-20 19:52:14.360 |     from .tools import filter_disabled_tools
2025-10-20 19:52:14.360 |   File "/app/src/server/tools/__init__.py", line 5, in <module>
2025-10-20 19:52:14.360 |     from .tool_filter import (
2025-10-20 19:52:14.360 |     ...<6 lines>...
2025-10-20 19:52:14.360 |     )
2025-10-20 19:52:14.360 |   File "/app/src/server/tools/tool_filter.py", line 33, in <module>
2025-10-20 19:52:14.360 |     ESSENTIAL_TOOLS: set[str] = _get_essential_tools()
2025-10-20 19:52:14.360 |                                 ~~~~~~~~~~~~~~~~~~~~^^
2025-10-20 19:52:14.360 |   File "/app/src/server/tools/tool_filter.py", line 21, in _get_essential_tools
2025-10-20 19:52:14.360 |     from tools.registry import TOOL_MAP
2025-10-20 19:52:14.360 |   File "/app/tools/__init__.py", line 6, in <module>
2025-10-20 19:52:14.360 |     from .challenge import ChallengeTool
2025-10-20 19:52:14.360 |   File "/app/tools/challenge.py", line 21, in <module>
2025-10-20 19:52:14.360 |     from .simple.base import SimpleTool
2025-10-20 19:52:14.360 |   File "/app/tools/simple/__init__.py", line 16, in <module>
2025-10-20 19:52:14.360 |     from .base import SimpleTool
2025-10-20 19:52:14.360 | ModuleNotFoundError: No module named 'tools.simple.base'
2025-10-20 19:52:19.396 | 2025-10-20 19:52:19 INFO root: [ASYNC_LOGGING] Async-safe logging configured successfully
2025-10-20 19:52:19.397 | 2025-10-20 19:52:19 INFO root: [LOGGING] Configured websockets library logging to suppress handshake noise
2025-10-20 19:52:19.397 | 2025-10-20 19:52:19 INFO ws_daemon: [AUTH] Authentication enabled (token first 10 chars): test-token...
2025-10-20 19:52:19.936 | Traceback (most recent call last):
2025-10-20 19:52:19.936 |   File "/app/scripts/ws/run_ws_daemon.py", line 24, in <module>
2025-10-20 19:52:19.936 |     from src.daemon.ws_server import main_async
2025-10-20 19:52:19.936 |   File "/app/src/daemon/ws_server.py", line 220, in <module>
2025-10-20 19:52:19.936 |     from server import TOOLS as SERVER_TOOLS  # type: ignore
2025-10-20 19:52:19.936 |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-10-20 19:52:19.936 |   File "/app/server.py", line 95, in <module>
2025-10-20 19:52:19.936 |     from src.server.utils import get_follow_up_instructions  # type: ignore
2025-10-20 19:52:19.936 |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-10-20 19:52:19.936 |   File "/app/src/server/__init__.py", line 10, in <module>
2025-10-20 19:52:19.936 |     from .tools import filter_disabled_tools
2025-10-20 19:52:19.936 |   File "/app/src/server/tools/__init__.py", line 5, in <module>
2025-10-20 19:52:19.936 |     from .tool_filter import (
2025-10-20 19:52:19.936 |     ...<6 lines>...
2025-10-20 19:52:19.936 |     )
2025-10-20 19:52:19.936 |   File "/app/src/server/tools/tool_filter.py", line 33, in <module>
2025-10-20 19:52:19.936 |     ESSENTIAL_TOOLS: set[str] = _get_essential_tools()
2025-10-20 19:52:19.936 |                                 ~~~~~~~~~~~~~~~~~~~~^^
2025-10-20 19:52:19.936 |   File "/app/src/server/tools/tool_filter.py", line 21, in _get_essential_tools
2025-10-20 19:52:19.936 |     from tools.registry import TOOL_MAP
2025-10-20 19:52:19.936 |   File "/app/tools/__init__.py", line 6, in <module>
2025-10-20 19:52:19.936 |     from .challenge import ChallengeTool
2025-10-20 19:52:19.936 |   File "/app/tools/challenge.py", line 21, in <module>
2025-10-20 19:52:19.936 |     from .simple.base import SimpleTool
2025-10-20 19:52:19.936 |   File "/app/tools/simple/__init__.py", line 16, in <module>
2025-10-20 19:52:19.936 |     from .base import SimpleTool
2025-10-20 19:52:19.936 | ModuleNotFoundError: No module named 'tools.simple.base'
2025-10-20 19:52:26.015 | 2025-10-20 19:52:26 INFO root: [ASYNC_LOGGING] Async-safe logging configured successfully
2025-10-20 19:52:26.016 | 2025-10-20 19:52:26 INFO root: [LOGGING] Configured websockets library logging to suppress handshake noise
2025-10-20 19:52:26.016 | 2025-10-20 19:52:26 INFO ws_daemon: [AUTH] Authentication enabled (token first 10 chars): test-token...
2025-10-20 19:52:26.589 | Traceback (most recent call last):
2025-10-20 19:52:26.590 |   File "/app/scripts/ws/run_ws_daemon.py", line 24, in <module>
2025-10-20 19:52:26.590 |     from src.daemon.ws_server import main_async
2025-10-20 19:52:26.590 |   File "/app/src/daemon/ws_server.py", line 220, in <module>
2025-10-20 19:52:26.590 |     from server import TOOLS as SERVER_TOOLS  # type: ignore
2025-10-20 19:52:26.590 |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-10-20 19:52:26.590 |   File "/app/server.py", line 95, in <module>
2025-10-20 19:52:26.590 |     from src.server.utils import get_follow_up_instructions  # type: ignore
2025-10-20 19:52:26.590 |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-10-20 19:52:26.590 |   File "/app/src/server/__init__.py", line 10, in <module>
2025-10-20 19:52:26.590 |     from .tools import filter_disabled_tools
2025-10-20 19:52:26.590 |   File "/app/src/server/tools/__init__.py", line 5, in <module>
2025-10-20 19:52:26.590 |     from .tool_filter import (
2025-10-20 19:52:26.590 |     ...<6 lines>...
2025-10-20 19:52:26.590 |     )
2025-10-20 19:52:26.590 |   File "/app/src/server/tools/tool_filter.py", line 33, in <module>
2025-10-20 19:52:26.590 |     ESSENTIAL_TOOLS: set[str] = _get_essential_tools()
2025-10-20 19:52:26.590 |                                 ~~~~~~~~~~~~~~~~~~~~^^
2025-10-20 19:52:26.590 |   File "/app/src/server/tools/tool_filter.py", line 21, in _get_essential_tools
2025-10-20 19:52:26.590 |     from tools.registry import TOOL_MAP
2025-10-20 19:52:26.590 |   File "/app/tools/__init__.py", line 6, in <module>
2025-10-20 19:52:26.590 |     from .challenge import ChallengeTool
2025-10-20 19:52:26.590 |   File "/app/tools/challenge.py", line 21, in <module>
2025-10-20 19:52:26.590 |     from .simple.base import SimpleTool
2025-10-20 19:52:26.590 |   File "/app/tools/simple/__init__.py", line 16, in <module>
2025-10-20 19:52:26.590 |     from .base import SimpleTool
2025-10-20 19:52:26.590 | ModuleNotFoundError: No module named 'tools.simple.base'
2025-10-20 19:52:35.920 | 2025-10-20 19:52:35 INFO root: [ASYNC_LOGGING] Async-safe logging configured successfully
2025-10-20 19:52:35.921 | 2025-10-20 19:52:35 INFO root: [LOGGING] Configured websockets library logging to suppress handshake noise
2025-10-20 19:52:35.921 | 2025-10-20 19:52:35 INFO ws_daemon: [AUTH] Authentication enabled (token first 10 chars): test-token...
2025-10-20 19:52:36.504 | Traceback (most recent call last):
2025-10-20 19:52:36.504 |   File "/app/scripts/ws/run_ws_daemon.py", line 24, in <module>
2025-10-20 19:52:36.504 |     from src.daemon.ws_server import main_async
2025-10-20 19:52:36.504 |   File "/app/src/daemon/ws_server.py", line 220, in <module>
2025-10-20 19:52:36.504 |     from server import TOOLS as SERVER_TOOLS  # type: ignore
2025-10-20 19:52:36.504 |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-10-20 19:52:36.504 |   File "/app/server.py", line 95, in <module>
2025-10-20 19:52:36.504 |     from src.server.utils import get_follow_up_instructions  # type: ignore
2025-10-20 19:52:36.504 |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-10-20 19:52:36.504 |   File "/app/src/server/__init__.py", line 10, in <module>
2025-10-20 19:52:36.504 |     from .tools import filter_disabled_tools
2025-10-20 19:52:36.504 |   File "/app/src/server/tools/__init__.py", line 5, in <module>
2025-10-20 19:52:36.504 |     from .tool_filter import (
2025-10-20 19:52:36.504 |     ...<6 lines>...
2025-10-20 19:52:36.504 |     )
2025-10-20 19:52:36.504 |   File "/app/src/server/tools/tool_filter.py", line 33, in <module>
2025-10-20 19:52:36.504 |     ESSENTIAL_TOOLS: set[str] = _get_essential_tools()
2025-10-20 19:52:36.504 |                                 ~~~~~~~~~~~~~~~~~~~~^^
2025-10-20 19:52:36.504 |   File "/app/src/server/tools/tool_filter.py", line 21, in _get_essential_tools
2025-10-20 19:52:36.504 |     from tools.registry import TOOL_MAP
2025-10-20 19:52:36.504 |   File "/app/tools/__init__.py", line 6, in <module>
2025-10-20 19:52:36.504 |     from .challenge import ChallengeTool
2025-10-20 19:52:36.504 |   File "/app/tools/challenge.py", line 21, in <module>
2025-10-20 19:52:36.504 |     from .simple.base import SimpleTool
2025-10-20 19:52:36.504 |   File "/app/tools/simple/__init__.py", line 16, in <module>
2025-10-20 19:52:36.504 |     from .base import SimpleTool
2025-10-20 19:52:36.504 | ModuleNotFoundError: No module named 'tools.simple.base'
2025-10-20 19:52:52.262 | 2025-10-20 19:52:52 INFO root: [ASYNC_LOGGING] Async-safe logging configured successfully
2025-10-20 19:52:52.263 | 2025-10-20 19:52:52 INFO ws_daemon: [AUTH] Authentication enabled (token first 10 chars): test-token...
2025-10-20 19:52:52.263 | 2025-10-20 19:52:52 INFO root: [LOGGING] Configured websockets library logging to suppress handshake noise
2025-10-20 19:52:52.895 | Traceback (most recent call last):
2025-10-20 19:52:52.896 |   File "/app/scripts/ws/run_ws_daemon.py", line 24, in <module>
2025-10-20 19:52:52.896 |     from src.daemon.ws_server import main_async
2025-10-20 19:52:52.896 |   File "/app/src/daemon/ws_server.py", line 220, in <module>
2025-10-20 19:52:52.896 |     from server import TOOLS as SERVER_TOOLS  # type: ignore
2025-10-20 19:52:52.896 |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-10-20 19:52:52.896 |   File "/app/server.py", line 95, in <module>
2025-10-20 19:52:52.896 |     from src.server.utils import get_follow_up_instructions  # type: ignore
2025-10-20 19:52:52.896 |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-10-20 19:52:52.896 |   File "/app/src/server/__init__.py", line 10, in <module>
2025-10-20 19:52:52.896 |     from .tools import filter_disabled_tools
2025-10-20 19:52:52.896 |   File "/app/src/server/tools/__init__.py", line 5, in <module>
2025-10-20 19:52:52.896 |     from .tool_filter import (
2025-10-20 19:52:52.896 |     ...<6 lines>...
2025-10-20 19:52:52.896 |     )
2025-10-20 19:52:52.896 |   File "/app/src/server/tools/tool_filter.py", line 33, in <module>
2025-10-20 19:52:52.896 |     ESSENTIAL_TOOLS: set[str] = _get_essential_tools()
2025-10-20 19:52:52.896 |                                 ~~~~~~~~~~~~~~~~~~~~^^
2025-10-20 19:52:52.896 |   File "/app/src/server/tools/tool_filter.py", line 21, in _get_essential_tools
2025-10-20 19:52:52.896 |     from tools.registry import TOOL_MAP
2025-10-20 19:52:52.896 |   File "/app/tools/__init__.py", line 6, in <module>
2025-10-20 19:52:52.896 |     from .challenge import ChallengeTool
2025-10-20 19:52:52.896 |   File "/app/tools/challenge.py", line 21, in <module>
2025-10-20 19:52:52.896 |     from .simple.base import SimpleTool
2025-10-20 19:52:52.896 |   File "/app/tools/simple/__init__.py", line 16, in <module>
2025-10-20 19:52:52.896 |     from .base import SimpleTool
2025-10-20 19:52:52.896 | ModuleNotFoundError: No module named 'tools.simple.base'
2025-10-20 19:53:21.332 | 2025-10-20 19:53:21 INFO root: [ASYNC_LOGGING] Async-safe logging configured successfully
2025-10-20 19:53:21.333 | 2025-10-20 19:53:21 INFO ws_daemon: [AUTH] Authentication enabled (token first 10 chars): test-token...
2025-10-20 19:53:21.333 | 2025-10-20 19:53:21 INFO root: [LOGGING] Configured websockets library logging to suppress handshake noise
2025-10-20 19:53:21.889 | Traceback (most recent call last):
2025-10-20 19:53:21.890 |   File "/app/scripts/ws/run_ws_daemon.py", line 24, in <module>
2025-10-20 19:53:21.890 |     from src.daemon.ws_server import main_async
2025-10-20 19:53:21.890 |   File "/app/src/daemon/ws_server.py", line 220, in <module>
2025-10-20 19:53:21.890 |     from server import TOOLS as SERVER_TOOLS  # type: ignore
2025-10-20 19:53:21.890 |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-10-20 19:53:21.890 |   File "/app/server.py", line 95, in <module>
2025-10-20 19:53:21.890 |     from src.server.utils import get_follow_up_instructions  # type: ignore
2025-10-20 19:53:21.890 |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-10-20 19:53:21.890 |   File "/app/src/server/__init__.py", line 10, in <module>
2025-10-20 19:53:21.890 |     from .tools import filter_disabled_tools
2025-10-20 19:53:21.890 |   File "/app/src/server/tools/__init__.py", line 5, in <module>
2025-10-20 19:53:21.890 |     from .tool_filter import (
2025-10-20 19:53:21.890 |     ...<6 lines>...
2025-10-20 19:53:21.890 |     )
2025-10-20 19:53:21.890 |   File "/app/src/server/tools/tool_filter.py", line 33, in <module>
2025-10-20 19:53:21.890 |     ESSENTIAL_TOOLS: set[str] = _get_essential_tools()
2025-10-20 19:53:21.890 |                                 ~~~~~~~~~~~~~~~~~~~~^^
2025-10-20 19:53:21.890 |   File "/app/src/server/tools/tool_filter.py", line 21, in _get_essential_tools
2025-10-20 19:53:21.890 |     from tools.registry import TOOL_MAP
2025-10-20 19:53:21.890 |   File "/app/tools/__init__.py", line 6, in <module>
2025-10-20 19:53:21.890 |     from .challenge import ChallengeTool
2025-10-20 19:53:21.890 |   File "/app/tools/challenge.py", line 21, in <module>
2025-10-20 19:53:21.890 |     from .simple.base import SimpleTool
2025-10-20 19:53:21.890 |   File "/app/tools/simple/__init__.py", line 16, in <module>
2025-10-20 19:53:21.890 |     from .base import SimpleTool
2025-10-20 19:53:21.890 | ModuleNotFoundError: No module named 'tools.simple.base'