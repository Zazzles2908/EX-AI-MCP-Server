# PROVIDER INTEGRATION MAP
**Date:** 2025-10-10 (10th October 2025, Thursday)  
**Phase:** Phase 2 - Map Connections  
**Task:** 2.3 - Provider Integration Mapping  
**Status:** ✅ COMPLETE

---

## 🎯 PURPOSE

Map how AI providers are selected, initialized, and called for model execution.

**Components Analyzed:**
1. **src/providers/registry_core.py** - Provider registry and selection
2. **src/providers/kimi.py** - Kimi (Moonshot) provider implementation
3. **src/providers/glm.py** - GLM (ZhipuAI) provider implementation
4. **Request/Response Transformation** - How data flows through providers

---

## 📊 PROVIDER ARCHITECTURE OVERVIEW

```
Tool Execution
    ↓
Model Context Resolution (request_handler.py)
    ↓
┌─────────────────────────────────────────────────────────────┐
│ PROVIDER REGISTRY (ModelProviderRegistry)                   │
│ - Singleton pattern                                         │
│ - Provider registration and initialization                  │
│ - Model discovery and selection                             │
│ - Health monitoring and circuit breakers                    │
└─────────────────────────────────────────────────────────────┘
    ↓
Provider Selection (Priority Order)
    ↓
┌───────────────────────────┬─────────────────────────────────┐
│ KIMI PROVIDER             │ GLM PROVIDER                    │
│ (Moonshot API)            │ (ZhipuAI API)                   │
├───────────────────────────┼─────────────────────────────────┤
│ - OpenAI-compatible       │ - Native SDK + HTTP fallback    │
│ - Context caching         │ - Web search support            │
│ - File upload support     │ - File upload support           │
│ - Idempotency headers     │ - Tool calling support          │
└───────────────────────────┴─────────────────────────────────┘
    ↓
HTTP Request to AI Provider API
    ↓
Response Transformation
    ↓
ModelResponse returned to tool
```

---

## 🔍 COMPONENT 1: Provider Registry (registry_core.py)

### File Information
- **Path:** `src/providers/registry_core.py`
- **Size:** 504 lines
- **Purpose:** Core provider management and selection
- **Pattern:** Singleton with lazy initialization

### Provider Priority Order
```python
PROVIDER_PRIORITY_ORDER = [
    ProviderType.KIMI,       # Direct Kimi/Moonshot access (preferred)
    ProviderType.GLM,        # Direct GLM/ZhipuAI access (preferred)
    ProviderType.CUSTOM,     # Local/self-hosted models
    ProviderType.OPENROUTER, # Catch-all for cloud models (optional)
]
```

### Provider Registration

**1. Singleton Pattern:**
```python
class ModelProviderRegistry:
    _instance = None
    _telemetry: dict[str, dict[str, Any]] = {}
    _telemetry_lock = threading.RLock()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._providers = {}
            cls._instance._initialized_providers = {}
        return cls._instance
```

**2. Register Provider:**
```python
@classmethod
def register_provider(cls, provider_type: ProviderType, provider_class: type[ModelProvider]) -> None:
    instance = cls()
    instance._providers[provider_type] = provider_class
```

**3. Get Provider (Lazy Initialization):**
```python
@classmethod
def get_provider(cls, provider_type: ProviderType, force_new: bool = False) -> Optional[ModelProvider]:
    instance = cls()
    
    # Enforce allowlist if configured (security hardening)
    allowed = os.getenv("ALLOWED_PROVIDERS", "").strip()
    if allowed:
        allow = {p.strip().upper() for p in allowed.split(",") if p.strip()}
        if provider_type.name not in allow:
            return None
    
    # Return cached instance if available
    if not force_new and provider_type in instance._initialized_providers:
        return instance._initialized_providers[provider_type]
    
    # Check if provider class is registered
    if provider_type not in instance._providers:
        return None
    
    # Get API key from environment
    api_key = cls._get_api_key_for_provider(provider_type)
    if not api_key:
        return None
    
    # Get provider class
    provider_class = instance._providers[provider_type]
    
    # Initialize provider with API key and optional base_url
    if provider_type == ProviderType.KIMI:
        base_url = os.getenv("KIMI_API_URL") or os.getenv("MOONSHOT_API_URL")
        provider = provider_class(api_key=api_key, base_url=base_url) if base_url else provider_class(api_key=api_key)
    elif provider_type == ProviderType.GLM:
        base_url = os.getenv("GLM_API_URL") or os.getenv("ZHIPUAI_API_URL")
        provider = provider_class(api_key=api_key, base_url=base_url) if base_url else provider_class(api_key=api_key)
    else:
        provider = provider_class(api_key=api_key)
    
    # Wrap with health monitoring if enabled
    if _health_enabled():
        provider = HealthWrappedProvider(provider)
    
    # Cache the instance
    instance._initialized_providers[provider_type] = provider
    
    return provider
```

### Provider Selection for Model

**Get Provider for Model:**
```python
@classmethod
def get_provider_for_model(cls, model_name: str) -> Optional[ModelProvider]:
    """
    Get provider instance for a specific model name.
    
    Provider priority order:
    1. Native APIs (KIMI, GLM) - Most direct and efficient
    2. CUSTOM - For local/private models with specific endpoints
    3. OPENROUTER - Catch-all for cloud models via unified API
    """
    # Try each provider in priority order
    for provider_type in cls.PROVIDER_PRIORITY_ORDER:
        provider = cls.get_provider(provider_type)
        if provider and provider.supports_model(model_name):
            return provider
    
    return None
```

### API Key Resolution

**Get API Key for Provider:**
```python
@classmethod
def _get_api_key_for_provider(cls, provider_type: ProviderType) -> Optional[str]:
    # Map provider types to environment variable names
    key_map = {
        ProviderType.KIMI: ["KIMI_API_KEY", "MOONSHOT_API_KEY"],
        ProviderType.GLM: ["GLM_API_KEY", "ZHIPUAI_API_KEY"],
        ProviderType.CUSTOM: ["CUSTOM_API_KEY"],
        ProviderType.OPENROUTER: ["OPENROUTER_API_KEY"],
    }
    
    # Try each possible key name
    for key_name in key_map.get(provider_type, []):
        api_key = os.getenv(key_name)
        if api_key:
            return api_key
    
    return None
```

### Health Monitoring

**Health Wrapped Provider:**
```python
if _health_enabled():
    provider = HealthWrappedProvider(provider)
```

**Features:**
- Circuit breaker pattern
- Request/response tracking
- Latency monitoring
- Token usage tracking
- Failure rate tracking

---

## 🔍 COMPONENT 2: Kimi Provider (kimi.py)

### File Information
- **Path:** `src/providers/kimi.py`
- **Size:** 146 lines
- **Purpose:** Kimi (Moonshot) provider implementation
- **Base Class:** OpenAICompatibleProvider
- **API:** https://api.moonshot.ai/v1

### Class Hierarchy
```python
class KimiModelProvider(OpenAICompatibleProvider):
    # Inherits OpenAI-compatible interface
    # Adds Kimi-specific features (caching, file upload)
```

### Initialization

**Constructor:**
```python
def __init__(self, api_key: str, base_url: Optional[str] = None, **kwargs):
    self.base_url = base_url or self.DEFAULT_BASE_URL  # https://api.moonshot.ai/v1
    
    # Provider-specific timeout overrides
    rt = os.getenv("KIMI_READ_TIMEOUT_SECS", "").strip()
    ct = os.getenv("KIMI_CONNECT_TIMEOUT_SECS", "").strip()
    wt = os.getenv("KIMI_WRITE_TIMEOUT_SECS", "").strip()
    pt = os.getenv("KIMI_POOL_TIMEOUT_SECS", "").strip()
    
    if rt:
        kwargs["read_timeout"] = float(rt)
    if ct:
        kwargs["connect_timeout"] = float(ct)
    if wt:
        kwargs["write_timeout"] = float(wt)
    if pt:
        kwargs["pool_timeout"] = float(pt)
    
    # Default to 300s to avoid multi-minute hangs
    if "read_timeout" not in kwargs and not rt:
        kwargs["read_timeout"] = float(os.getenv("KIMI_DEFAULT_READ_TIMEOUT_SECS", "300"))
    
    super().__init__(api_key, base_url=self.base_url, **kwargs)
```

### Supported Models

**Model Configurations (from kimi_config.py):**
```python
SUPPORTED_MODELS = {
    "kimi-k2-0905-preview": ModelCapabilities(...),
    "kimi-k2-turbo-preview": ModelCapabilities(...),
    "moonshot-v1-8k": ModelCapabilities(...),
    "moonshot-v1-32k": ModelCapabilities(...),
    "moonshot-v1-128k": ModelCapabilities(...),
    "moonshot-v1-8k-vision-preview": ModelCapabilities(...),
    "kimi-latest": ModelCapabilities(...),  # Alias
    "kimi-thinking-preview": ModelCapabilities(...),
}
```

### Key Features

**1. Context Caching:**
```python
def save_cache_token(self, session_id: str, tool_name: str, prefix_hash: str, token: str) -> None:
    kimi_cache.save_cache_token(session_id, tool_name, prefix_hash, token)

def get_cache_token(self, session_id: str, tool_name: str, prefix_hash: str) -> Optional[str]:
    return kimi_cache.get_cache_token(session_id, tool_name, prefix_hash)
```

**2. File Upload:**
```python
def upload_file(self, file_path: str, purpose: str = "file-extract") -> str:
    """Upload a local file to Moonshot (Kimi) and return file_id."""
    return kimi_files.upload_file(self.client, file_path, purpose)
```

**3. Chat Completions (with Idempotency):**
```python
def chat_completions_create(self, *, model: str, messages: list[dict[str, Any]], tools: Optional[list[Any]] = None, tool_choice: Optional[Any] = None, temperature: float = 0.6, **kwargs) -> dict:
    """Wrapper that injects idempotency and Kimi context-cache headers."""
    return kimi_chat.chat_completions_create(
        self.client,
        model=model,
        messages=messages,
        tools=tools,
        tool_choice=tool_choice,
        temperature=temperature,
        **kwargs
    )
```

**4. Content Generation:**
```python
def generate_content(
    self,
    prompt: str,
    model_name: str,
    system_prompt: Optional[str] = None,
    temperature: float = 0.3,
    max_output_tokens: Optional[int] = None,
    images: Optional[list[str]] = None,
    **kwargs,
) -> ModelResponse:
    # Ensure non-streaming by default for MCP tools
    kwargs.setdefault("stream", False)
    return super().generate_content(
        prompt=prompt,
        model_name=self._resolve_model_name(model_name),
        system_prompt=system_prompt,
        temperature=temperature,
        max_output_tokens=max_output_tokens,
        images=images,
        **kwargs,
    )
```

### Request Transformation (Kimi)

**Request Flow:**
```
Tool → generate_content()
    ↓
Build OpenAI-compatible payload:
{
    "model": "kimi-k2-0905-preview",
    "messages": [
        {"role": "system", "content": "system_prompt"},
        {"role": "user", "content": "prompt"}
    ],
    "temperature": 0.3,
    "max_tokens": max_output_tokens,
    "stream": false
}
    ↓
Add Kimi-specific headers:
- X-Idempotency-Key: <session_id>:<tool_name>:<prefix_hash>
- X-Kimi-Context-Cache: <cache_token> (if available)
    ↓
POST https://api.moonshot.ai/v1/chat/completions
```

### Response Transformation (Kimi)

**Response Flow:**
```
HTTP Response from Kimi API
    ↓
Extract response data:
{
    "id": "chatcmpl-...",
    "object": "chat.completion",
    "created": 1234567890,
    "model": "kimi-k2-0905-preview",
    "choices": [{
        "index": 0,
        "message": {
            "role": "assistant",
            "content": "response text"
        },
        "finish_reason": "stop"
    }],
    "usage": {
        "prompt_tokens": 100,
        "completion_tokens": 50,
        "total_tokens": 150
    }
}
    ↓
Extract cache token from headers:
- X-Kimi-Context-Cache-Token: <new_cache_token>
    ↓
Transform to ModelResponse:
ModelResponse(
    text="response text",
    model_name="kimi-k2-0905-preview",
    finish_reason="stop",
    usage={
        "input_tokens": 100,
        "output_tokens": 50,
        "total_tokens": 150
    }
)
    ↓
Return to tool
```

---

## 🔍 COMPONENT 3: GLM Provider (glm.py)

### File Information
- **Path:** `src/providers/glm.py`
- **Size:** 110 lines
- **Purpose:** GLM (ZhipuAI) provider implementation
- **Base Class:** ModelProvider
- **API:** https://api.z.ai/api/paas/v4

### Class Hierarchy
```python
class GLMModelProvider(ModelProvider):
    # Implements ModelProvider interface
    # Uses native SDK + HTTP fallback
```

### Initialization

**Constructor (Dual SDK/HTTP):**
```python
def __init__(self, api_key: str, base_url: Optional[str] = None, **kwargs):
    super().__init__(api_key, **kwargs)
    self.base_url = base_url or self.DEFAULT_BASE_URL  # https://api.z.ai/api/paas/v4
    
    # Initialize HTTP client first (always needed as fallback)
    self.client = HttpClient(
        self.base_url,
        api_key=self.api_key,
        api_key_header="Authorization",
        api_key_prefix="Bearer "
    )
    
    # Prefer official SDK; fallback to HTTP if not available
    try:
        from zhipuai import ZhipuAI
        self._use_sdk = True
        # CRITICAL: Pass base_url to SDK to use z.ai proxy instead of bigmodel.cn
        self._sdk_client = ZhipuAI(api_key=self.api_key, base_url=self.base_url)
        logger.info(f"GLM provider using SDK with base_url={self.base_url}")
    except Exception as e:
        logger.warning("zhipuai SDK unavailable; falling back to HTTP client: %s", e)
        self._use_sdk = False
```

### Supported Models

**Model Configurations (from glm_config.py):**
```python
SUPPORTED_MODELS = {
    "glm-4.6": ModelCapabilities(...),
    "glm-4.5": ModelCapabilities(...),
    "glm-4.5-flash": ModelCapabilities(...),
    "glm-4.5-air": ModelCapabilities(...),
    "glm-4.5v": ModelCapabilities(...),  # Vision model
}
```

### Key Features

**1. Dual SDK/HTTP Pattern:**
```python
# Prefer SDK, fallback to HTTP
if self._use_sdk:
    response = self._sdk_client.chat.completions.create(...)
else:
    response = self.client.post("/chat/completions", payload)
```

**2. File Upload:**
```python
def upload_file(self, file_path: str, purpose: str = "agent") -> str:
    """Upload a file to GLM Files API and return its file id."""
    return glm_files.upload_file(
        sdk_client=getattr(self, "_sdk_client", None),
        http_client=self.client,
        file_path=file_path,
        purpose=purpose,
        use_sdk=getattr(self, "_use_sdk", False)
    )
```

**3. Content Generation:**
```python
def generate_content(
    self,
    prompt: str,
    model_name: str,
    system_prompt: Optional[str] = None,
    temperature: float = 0.3,
    max_output_tokens: Optional[int] = None,
    **kwargs,
) -> ModelResponse:
    resolved = self._resolve_model_name(model_name)
    effective_temp = self.get_effective_temperature(resolved, temperature)
    
    return glm_chat.generate_content(
        sdk_client=getattr(self, "_sdk_client", None),
        http_client=self.client,
        prompt=prompt,
        model_name=resolved,
        system_prompt=system_prompt,
        temperature=effective_temp,
        max_output_tokens=max_output_tokens,
        use_sdk=getattr(self, "_use_sdk", False),
        **kwargs
    )
```

### Request Transformation (GLM)

**Request Flow:**
```
Tool → generate_content()
    ↓
Build GLM payload:
{
    "model": "glm-4.5-flash",
    "messages": [
        {"role": "system", "content": "system_prompt"},
        {"role": "user", "content": "prompt"}
    ],
    "temperature": 0.3,
    "max_tokens": max_output_tokens,
    "stream": false
}
    ↓
If SDK available:
    sdk_client.chat.completions.create(**payload)
Else:
    POST https://api.z.ai/api/paas/v4/chat/completions
    Headers: {"Authorization": "Bearer <api_key>"}
```

### Response Transformation (GLM)

**Response Flow:**
```
HTTP Response from GLM API
    ↓
Extract response data:
{
    "id": "chatcmpl-...",
    "created": 1234567890,
    "model": "glm-4.5-flash",
    "choices": [{
        "index": 0,
        "message": {
            "role": "assistant",
            "content": "response text"
        },
        "finish_reason": "stop"
    }],
    "usage": {
        "prompt_tokens": 100,
        "completion_tokens": 50,
        "total_tokens": 150
    }
}
    ↓
Transform to ModelResponse:
ModelResponse(
    text="response text",
    model_name="glm-4.5-flash",
    finish_reason="stop",
    usage={
        "input_tokens": 100,
        "output_tokens": 50,
        "total_tokens": 150
    }
)
    ↓
Return to tool
```

---

## 📊 PROVIDER COMPARISON

| Feature | Kimi Provider | GLM Provider |
|---------|---------------|--------------|
| **Base Class** | OpenAICompatibleProvider | ModelProvider |
| **API Style** | OpenAI-compatible | Native GLM API |
| **SDK** | OpenAI SDK | ZhipuAI SDK + HTTP fallback |
| **Base URL** | api.moonshot.ai/v1 | api.z.ai/api/paas/v4 |
| **Context Caching** | ✅ Yes (X-Kimi-Context-Cache) | ❌ No |
| **Idempotency** | ✅ Yes (X-Idempotency-Key) | ❌ No |
| **File Upload** | ✅ Yes (file-extract, assistants) | ✅ Yes (agent purpose) |
| **Web Search** | ❌ No | ✅ Yes (native support) |
| **Vision Models** | ✅ Yes (moonshot-v1-8k-vision-preview) | ✅ Yes (glm-4.5v) |
| **Thinking Mode** | ✅ Yes (kimi-thinking-preview) | ❌ No |
| **Default Timeout** | 300s | Standard HTTP timeout |
| **Model Count** | 8 models | 5 models |

---

## 🔑 KEY INSIGHTS

### 1. Provider Selection Strategy
- **Priority Order:** KIMI → GLM → CUSTOM → OPENROUTER
- **Model-Based:** Provider selected based on model name support
- **Lazy Initialization:** Providers created on first use, then cached
- **Health Monitoring:** Optional health wrapper for circuit breaker pattern

### 2. API Key Management
- **Multiple Names:** Supports both canonical and vendor-specific names
  - Kimi: KIMI_API_KEY or MOONSHOT_API_KEY
  - GLM: GLM_API_KEY or ZHIPUAI_API_KEY
- **Security:** ALLOWED_PROVIDERS env var for allowlist enforcement

### 3. Request/Response Transformation
- **Kimi:** OpenAI-compatible format with custom headers
- **GLM:** Native format with SDK/HTTP dual path
- **Normalization:** Both transform to ModelResponse for consistency

### 4. Advanced Features
- **Kimi Caching:** Context cache tokens reduce costs and latency
- **GLM Web Search:** Native web search support via API
- **Dual SDK/HTTP:** GLM uses SDK when available, HTTP as fallback
- **Timeout Configuration:** Provider-specific timeout overrides

### 5. File Upload Mechanisms
- **Kimi:** Uses Moonshot Files API (file-extract, assistants)
- **GLM:** Uses ZhipuAI Files API (agent purpose)
- **Both:** Return file_id for use in chat completions

---

## ✅ TASK 2.3 COMPLETE

**Deliverable:** PROVIDER_INTEGRATION_MAP.md ✅

**Next Task:** Task 2.4 - Utils Dependency Tracing

**Time Taken:** ~30 minutes (as estimated)

---

**Status:** ✅ COMPLETE - All provider integration flows mapped with request/response transformation

