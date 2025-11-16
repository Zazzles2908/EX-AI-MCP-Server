# 🤖 FIX AGENT 2: AI PLATFORM INTEGRATIONS REMEDIATION

**Agent Type:** AI/ML Integration Specialist & API Compliance Engineer  
**Priority:** P0 (Critical)  
**Estimated Time:** 3-4 weeks  
**Scope:** MiniMax M2, GLM (ZhipuAI), Moonshot/Kimi AI Platform Integrations  

---

## 🎯 MISSION OBJECTIVE

Fix critical AI platform integration issues, implement missing MiniMax M2 provider, resolve GLM streaming contradictions, and standardize Moonshot/Kimi model compliance across all providers to achieve 100% production reliability.

---

## 🚨 CRITICAL ISSUES IDENTIFIED

### 1. MINIMAX M2 PROVIDER MISSING (P0-CRITICAL)
**Location:** `src/providers/` (NO minimax.py found)  
**Impact:** No MiniMax text generation capability available

**Current State:** MiniMax exists only as routing decision engine in `src/router/minimax_m2_router.py`

**Root Issue Analysis:**
```python
# CURRENT: Only router, no provider
class MiniMaxM2Router:
    def __init__(self):
        self.client = anthropic.AsyncAnthropic(
            base_url="https://api.minimax.io/anthropic",
            api_key=os.getenv("MINIMAX_M2_KEY"),
        )
        self.model = "MiniMax-M2-Stable"  # NOT in official docs

# MISSING: Full text generation provider implementation
class MiniMaxProvider(BaseProvider):
    async def complete(self, prompt: str, **kwargs) -> Response:
        # IMPLEMENTATION MISSING
```

**Official Documentation Analysis:**
- **Base URL:** `https://api.minimax.io/v1/text/chatcompletion_pro_v3`
- **Models:** `abab6.5s-chat`, `abab6.5g-chat`, `abab6.5t-chat`
- **Authentication:** Bearer token in Authorization header
- **Response Format:** OpenAI-compatible

### 2. GLM STREAMING CONTRADICTION (P1-HIGH)
**Location:** `src/providers/glm_provider.py`  
**Impact:** Misleading API interface, potential runtime failures

**Issue:** Provider advertises `supports_streaming=False` but builds streaming payloads

```python
# PROBLEMATIC CODE:
class GLMProvider(BaseProvider):
    def __init__(self):
        self.supports_streaming = False  # CONTRADICTION
    
    async def _build_chat_request(self, messages, **kwargs):
        if kwargs.get("stream", False):
            # Building streaming payload BUT streaming disabled
            payload["stream"] = True
            payload["model_settings"] = {"temperature": kwargs.get("temperature", 0.7)}
        return payload
```

**Required Fix:**
```python
# FIXED CODE:
class GLMProvider(BaseProvider):
    def __init__(self):
        self.supports_streaming = True  # CORRECT
    
    async def complete(self, prompt: str, stream: bool = False, **kwargs):
        if stream:
            return await self._stream_completion(prompt, **kwargs)
        else:
            return await self._standard_completion(prompt, **kwargs)
```

### 3. MOONSHOT/KIMI MODEL INCONSISTENCIES (P1-HIGH)
**Location:** `src/providers/kimi.py`  
**Impact:** Runtime failures, unsupported capability claims

**Official Model List vs Current Implementation:**

| Current Code | Official Docs | Status |
|--------------|---------------|--------|
| `moonshot-v1-8k` | ❌ Not listed | REMOVE |
| `moonshot-v1-32k` | ❌ Not listed | REMOVE |
| `moonshot-v1-128k` | ❌ Not listed | REMOVE |
| `moonshot-v1-8k-vision-preview` | ✅ Listed | KEEP |
| `kimi-k2-thinking-preview` | ✅ Listed | KEEP |
| `kimi-k2-turbo-preview` | ✅ Listed | KEEP |

**Function Calling Issues:**
```python
# PROBLEMATIC CODE:
MODELS_CONFIG = {
    "moonshot-v1-8k": {"function_calling": True},  # NOT SUPPORTED
    "moonshot-v1-32k": {"function_calling": True},  # NOT SUPPORTED
}

# FIXED CODE:
MODELS_CONFIG = {
    "moonshot-v1-8k-vision-preview": {
        "function_calling": True,
        "vision": True,
        "context_window": 8192
    },
    "kimi-k2-thinking-preview": {
        "function_calling": False,  # Correct
        "thinking": True,
        "context_window": 256000
    }
}
```

---

## 🏗️ IMPLEMENTATION PLAN

### Phase 1: MiniMax M2 Provider Implementation (Week 1-2)

#### Step 1: Provider Architecture Setup
```python
# src/providers/minimax.py
from typing import List, Dict, Any, Optional
import os
from .base import BaseProvider

class MiniMaxProvider(BaseProvider):
    """Official MiniMax text generation provider"""
    
    MODELS = {
        "abab6.5s-chat": {
            "context_window": 8192,
            "max_output_tokens": 4096,
            "function_calling": True,
            "description": "Fast response model"
        },
        "abab6.5g-chat": {
            "context_window": 32768,
            "max_output_tokens": 8192,
            "function_calling": True,
            "description": "General purpose model"
        },
        "abab6.5t-chat": {
            "context_window": 200000,
            "max_output_tokens": 16384,
            "function_calling": True,
            "description": "Long context model"
        }
    }
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("MINIMAX_API_KEY")
        self.base_url = "https://api.minimax.io/v1"
        self.model = "abab6.5g-chat"  # Default model
```

#### Step 2: OpenAI-Compatible API Implementation
```python
class MiniMaxProvider(BaseProvider):
    
    async def complete(
        self,
        prompt: str,
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = None,
        stream: bool = False,
        **kwargs
    ) -> Response:
        """Complete text using MiniMax API"""
        
        model = model or self.model
        if model not in self.MODELS:
            raise ValueError(f"Invalid model: {model}")
        
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens or self.MODELS[model]["max_output_tokens"],
            "stream": stream
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/text/chatcompletion_pro_v3",
                json=payload,
                headers=headers
            ) as response:
                return await self._handle_response(response)
    
    async def _handle_response(self, response):
        """Handle MiniMax API response"""
        data = await response.json()
        
        if "error" in data:
            raise ProviderError(data["error"]["message"])
        
        return Response(
            content=data["choices"][0]["message"]["content"],
            model=data["model"],
            usage=data.get("usage", {}),
            metadata={"provider": "minimax"}
        )
```

#### Step 3: Registry Integration
```python
# src/providers/registry_core.py additions
PROVIDERS = {
    "minimax": {
        "class": "MiniMaxProvider",
        "models": list(MiniMaxProvider.MODELS.keys()),
        "capabilities": {
            "text_generation": True,
            "function_calling": True,
            "streaming": True,
            "context_window": 200000
        }
    }
}
```

### Phase 2: GLM Streaming Fix (Week 3)

#### Step 1: Interface Correction
```python
# src/providers/glm_provider.py
class GLMProvider(BaseProvider):
    
    @property
    def supports_streaming(self) -> bool:
        return True  # FIXED: Remove contradiction
    
    async def stream_complete(self, prompt: str, **kwargs) -> AsyncGenerator[Response, None]:
        """Stream completion responses"""
        payload = self._build_chat_request([{"role": "user", "content": prompt}], **kwargs)
        payload["stream"] = True
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=self._get_headers()
            ) as response:
                async for line in response.content:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        chunk = json.loads(line[6:])
                        if chunk["choices"]:
                            delta = chunk["choices"][0]["delta"]
                            if "content" in delta:
                                yield Response(
                                    content=delta["content"],
                                    model=chunk["model"],
                                    is_partial=True
                                )
```

#### Step 2: Configuration Updates
```python
# config/glm_config.py
GLM_CONFIG = {
    "supports_streaming": True,  # CORRECTED
    "default_model": "glm-4.6",
    "streaming_timeout": 60,
    "models": {
        "glm-4.6": {
            "context_window": 128000,
            "max_output_tokens": 8192,
            "supports_streaming": True
        }
    }
}
```

### Phase 3: Moonshot/Kimi Model Compliance (Week 3-4)

#### Step 1: Model List Standardization
```python
# src/providers/kimi.py - Model configuration fix
MODELS_CONFIG = {
    # Official models only - remove unofficial ones
    "moonshot-v1-8k-vision-preview": {
        "context_window": 8192,
        "max_output_tokens": 4096,
        "function_calling": False,  # Corrected
        "vision": True,
        "max_image_size": "10MB",
        "supported_image_formats": ["jpg", "jpeg", "png", "webp"]
    },
    "moonshot-v1-32k-vision-preview": {
        "context_window": 32768,
        "max_output_tokens": 8192,
        "function_calling": False,  # Corrected
        "vision": True
    },
    "kimi-k2-thinking-preview": {
        "context_window": 256000,
        "max_output_tokens": 16384,
        "function_calling": False,
        "thinking": True,
        "special_features": ["long_context", "reasoning"]
    },
    "kimi-k2-turbo-preview": {
        "context_window": 256000,
        "max_output_tokens": 16384,
        "function_calling": False,
        "speed_optimized": True
    }
}
```

#### Step 2: Capability Validation
```python
class KimiProvider(BaseProvider):
    
    def _validate_model_capabilities(self, model: str, requested_features: List[str]) -> List[str]:
        """Validate model supports requested features"""
        if model not in MODELS_CONFIG:
            raise ValueError(f"Model {model} not supported")
        
        model_config = MODELS_CONFIG[model]
        supported_features = []
        
        for feature in requested_features:
            if feature in model_config and model_config[feature]:
                supported_features.append(feature)
            else:
                logger.warning(f"Model {model} does not support {feature}")
        
        return supported_features
    
    async def complete_with_validation(
        self,
        prompt: str,
        model: str,
        function_calling: bool = False,
        vision: bool = False,
        **kwargs
    ) -> Response:
        """Complete with capability validation"""
        
        requested_features = []
        if function_calling:
            requested_features.append("function_calling")
        if vision:
            requested_features.append("vision")
        
        validated_features = self._validate_model_capabilities(model, requested_features)
        
        if "function_calling" in requested_features and "function_calling" not in validated_features:
            logger.warning(f"Function calling not supported for {model}, falling back to standard completion")
            function_calling = False
        
        return await self.complete(
            prompt=prompt,
            model=model,
            function_calling=function_calling,
            vision=vision,
            **kwargs
        )
```

---

## 🧪 VALIDATION & TESTING

### MiniMax Provider Tests
```python
# tests/providers/test_minimax_provider.py
import pytest
from src.providers.minimax import MiniMaxProvider

class TestMiniMaxProvider:
    
    @pytest.mark.asyncio
    async def test_model_list(self):
        """Test all models are properly configured"""
        provider = MiniMaxProvider()
        models = list(provider.MODELS.keys())
        
        expected_models = [
            "abab6.5s-chat",
            "abab6.5g-chat", 
            "abab6.5t-chat"
        ]
        
        assert set(models) == set(expected_models)
    
    @pytest.mark.asyncio
    async def test_api_compatibility(self):
        """Test OpenAI-compatible API format"""
        provider = MiniMaxProvider()
        
        response = await provider.complete("Hello", model="abab6.5g-chat")
        
        assert hasattr(response, "content")
        assert hasattr(response, "model")
        assert response.metadata["provider"] == "minimax"
    
    @pytest.mark.asyncio
    async def test_context_window_validation(self):
        """Test context window limits"""
        provider = MiniMaxProvider()
        
        model_config = provider.MODELS["abab6.5g-chat"]
        assert model_config["context_window"] == 32768
        assert model_config["max_output_tokens"] == 8192
```

### GLM Streaming Tests
```python
# tests/providers/test_glm_streaming.py
import pytest

class TestGLMSteamting:
    
    @pytest.mark.asyncio
    async def test_streaming_interface(self):
        """Test streaming capability matches interface"""
        provider = GLMProvider()
        
        assert provider.supports_streaming is True
        
        chunks = []
        async for chunk in provider.stream_complete("Test"):
            chunks.append(chunk)
        
        assert len(chunks) > 0
        assert all(hasattr(chunk, "content") for chunk in chunks)
```

### Moonshot/Kimi Compliance Tests
```python
# tests/providers/test_kimi_compliance.py

class TestKimiCompliance:
    
    def test_model_availability(self):
        """Test only official models are supported"""
        provider = KimiProvider()
        
        official_models = [
            "moonshot-v1-8k-vision-preview",
            "moonshot-v1-32k-vision-preview", 
            "kimi-k2-thinking-preview",
            "kimi-k2-turbo-preview"
        ]
        
        configured_models = list(provider.MODELS_CONFIG.keys())
        
        # Should contain only official models
        for model in configured_models:
            assert model in official_models, f"Model {model} not in official list"
    
    def test_function_calling_capabilities(self):
        """Test function calling capability validation"""
        provider = KimiProvider()
        
        # Test model that doesn't support function calling
        result = provider._validate_model_capabilities(
            "moonshot-v1-8k-vision-preview", 
            ["function_calling"]
        )
        
        assert "function_calling" not in result
```

---

## 📚 API COMPLIANCE REFERENCES

### MiniMax Official Documentation
- **Base URL:** `https://api.minimax.io/v1/text/chatcompletion_pro_v3`
- **Authentication:** Bearer token
- **Model List:** abab6.5s-chat, abab6.5g-chat, abab6.5t-chat
- **Reference:** https://platform.minimax.io/docs/guides/text-generation

### GLM/ZhipuAI Official Documentation  
- **Base URL:** `https://api.z.ai/api/paas/v4/`
- **SDK:** zai-sdk official library
- **Reference:** https://docs.z.ai/guides/develop/python/introduction

### Moonshot/Kimi Official Documentation
- **Base URL:** `https://api.moonshot.cn/v1/chat/completions`
- **Models:** See official API reference
- **Reference:** https://platform.moonshot.ai/docs/api-reference#public-service-address

---

## 🎯 SUCCESS CRITERIA

### MiniMax Implementation
- [ ] Full MiniMax provider implemented with 3 models
- [ ] OpenAI-compatible API interface
- [ ] 256K context window support
- [ ] Function calling capability
- [ ] Streaming support
- [ ] Complete test coverage

### GLM Streaming Fix
- [ ] Streaming interface corrected
- [ ] No more contradiction in supports_streaming property
- [ ] Proper streaming implementation
- [ ] Timeout and error handling
- [ ] Performance validation

### Moonshot/Kimi Standardization
- [ ] Only official models supported
- [ ] Function calling accurately advertised
- [ ] Vision capabilities properly configured
- [ ] Context windows correct
- [ ] Capability validation working

### Overall Integration Quality
- [ ] All providers use consistent interfaces
- [ ] Unified error handling
- [ ] Proper model selection logic
- [ ] Cost optimization working
- [ ] Health monitoring operational

---

## 🚀 DEPLOYMENT STRATEGY

### Phase 1: MiniMax Provider
1. Implement provider with minimal models (abab6.5g-chat)
2. Add basic test coverage
3. Deploy to staging environment
4. Validate with real API calls

### Phase 2: GLM Streaming Fix
1. Update streaming interface
2. Add comprehensive streaming tests
3. Deploy to staging
4. Test with production workloads

### Phase 3: Moonshot/Kimi Standardization
1. Update model configuration
2. Add capability validation
3. Deploy to staging
4. Test with existing clients

### Phase 4: Integration Testing
1. Test all providers together
2. Validate routing logic
3. Performance benchmarking
4. Production deployment

---

**FIX AGENT 2 DELIVERABLES:**
- MiniMax M2 provider fully implemented
- GLM streaming contradiction resolved
- Moonshot/Kimi model compliance achieved
- Unified provider interface
- Complete test coverage
- Production-ready integrations

**Ready for implementation when all P0/P1 issues are resolved!**
