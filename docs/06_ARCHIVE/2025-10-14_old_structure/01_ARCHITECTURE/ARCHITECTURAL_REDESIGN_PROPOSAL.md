# Architectural Redesign Proposal - Response Handling & Validation

**Date:** 2025-10-14  
**Purpose:** Comprehensive architectural redesign to fix fundamental gaps  
**Status:** PROPOSAL - Awaiting approval

---

## Executive Summary

Based on the critical analysis and user requirements, this proposal outlines a **proper architectural redesign** that:

1. **Separates concerns** into focused, modular components
2. **Follows documented architecture** (SDK-first with HTTP fallback)
3. **Centralizes timeout management** in .env configuration
4. **Implements model capability routing** based on documented capabilities
5. **Handles provider-specific response schemas** properly

**This is NOT a quick fix - this is proper architecture.**

---

## 🏗️ Proposed Architecture

### Component Separation

```
src/providers/
├── response_handlers/          # NEW: Response handling layer
│   ├── __init__.py
│   ├── base_handler.py        # Base response handler interface
│   ├── kimi_handler.py        # Kimi-specific response handling
│   ├── glm_handler.py         # GLM-specific response handling
│   └── validator.py           # Response validation logic
│
├── model_capabilities/         # NEW: Model capability registry
│   ├── __init__.py
│   ├── registry.py            # Capability registry
│   ├── kimi_capabilities.py   # Kimi model capabilities
│   └── glm_capabilities.py    # GLM model capabilities
│
├── timeout_manager/            # NEW: Centralized timeout management
│   ├── __init__.py
│   ├── config.py              # Timeout configuration from .env
│   ├── coordinator.py         # Timeout hierarchy coordination
│   └── context.py             # Timeout context propagation
│
└── [existing files...]
```

---

## 📋 Design Principle #1: Response Handler Separation

### Problem
Currently, response handling is mixed into provider code:
- `kimi_chat.py` extracts content but NOT finish_reason
- `openai_compatible.py` extracts finish_reason for GLM
- No consistent validation across providers

### Solution: Dedicated Response Handlers

**File:** `src/providers/response_handlers/base_handler.py`
```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional

@dataclass
class ParsedResponse:
    """Standardized response structure across all providers."""
    content: str
    finish_reason: str  # ALWAYS extracted
    usage: Optional[dict]
    tool_calls: Optional[list]
    raw: dict
    metadata: dict
    
    @property
    def is_complete(self) -> bool:
        """Check if response is complete (not truncated)."""
        return self.finish_reason in ["stop", "tool_calls"]
    
    @property
    def is_truncated(self) -> bool:
        """Check if response was truncated."""
        return self.finish_reason == "length"
    
    @property
    def is_filtered(self) -> bool:
        """Check if response was content filtered."""
        return self.finish_reason == "content_filter"


class BaseResponseHandler(ABC):
    """Base class for provider-specific response handlers."""
    
    @abstractmethod
    def parse(self, raw_response: Any) -> ParsedResponse:
        """Parse provider-specific response into standardized format."""
        pass
    
    @abstractmethod
    def validate_structure(self, raw_response: Any) -> tuple[bool, str]:
        """Validate response structure before parsing."""
        pass
```

**File:** `src/providers/response_handlers/kimi_handler.py`
```python
class KimiResponseHandler(BaseResponseHandler):
    """Kimi-specific response handler."""
    
    def validate_structure(self, raw_response: Any) -> tuple[bool, str]:
        """Validate Kimi response structure."""
        if not isinstance(raw_response, dict):
            return False, "Response is not a dictionary"
        
        choices = raw_response.get("choices", [])
        if not choices:
            return False, "Response has no choices"
        
        if not isinstance(choices[0], dict):
            return False, "First choice is not a dictionary"
        
        message = choices[0].get("message")
        if not message:
            return False, "First choice has no message"
        
        return True, ""
    
    def parse(self, raw_response: Any) -> ParsedResponse:
        """Parse Kimi response."""
        # Validate first
        is_valid, error = self.validate_structure(raw_response)
        if not is_valid:
            raise ValueError(f"Invalid Kimi response structure: {error}")
        
        choice0 = raw_response["choices"][0]
        message = choice0["message"]
        
        return ParsedResponse(
            content=message.get("content", ""),
            finish_reason=choice0.get("finish_reason", "unknown"),  # ALWAYS extract
            usage=raw_response.get("usage"),
            tool_calls=message.get("tool_calls"),
            raw=raw_response,
            metadata={
                "provider": "KIMI",
                "model": raw_response.get("model"),
                "id": raw_response.get("id"),
            }
        )
```

**File:** `src/providers/response_handlers/glm_handler.py`
```python
class GLMResponseHandler(BaseResponseHandler):
    """GLM-specific response handler."""
    
    def validate_structure(self, raw_response: Any) -> tuple[bool, str]:
        """Validate GLM response structure."""
        # Similar to Kimi but may have GLM-specific fields
        pass
    
    def parse(self, raw_response: Any) -> ParsedResponse:
        """Parse GLM response."""
        # GLM-specific parsing logic
        pass
```

### Integration

**Update:** `src/providers/kimi_chat.py`
```python
from .response_handlers import KimiResponseHandler

def chat_completions_create(...) -> dict:
    # ... existing code ...
    
    # NEW: Use response handler
    handler = KimiResponseHandler()
    parsed = handler.parse(raw_payload)
    
    return {
        "provider": "KIMI",
        "model": model,
        "content": parsed.content,
        "tool_calls": parsed.tool_calls,
        "usage": parsed.usage,
        "finish_reason": parsed.finish_reason,  # NOW INCLUDED
        "raw": parsed.raw,
        "metadata": parsed.metadata,
    }
```

---

## 📋 Design Principle #2: SDK-First with HTTP Fallback

### Current Issue
GLM should use zai-sdk FIRST, then fallback to OpenAI-compatible HTTP.

### Solution: Proper Fallback Chain

**File:** `src/providers/glm.py` (MODIFY)
```python
class GLMProvider(OpenAICompatibleProvider):
    """GLM provider with SDK-first, HTTP fallback pattern."""
    
    def __init__(self, ...):
        super().__init__(...)
        
        # Primary: zai-sdk client
        self.sdk_client = self._init_sdk_client()
        
        # Fallback: OpenAI-compatible HTTP client
        self.http_client = self._init_http_client()
    
    def _init_sdk_client(self):
        """Initialize zai-sdk client."""
        try:
            from zai import ZAI
            return ZAI(api_key=self.api_key, base_url=self.base_url)
        except Exception as e:
            logger.warning(f"Failed to initialize zai-sdk: {e}")
            return None
    
    def _init_http_client(self):
        """Initialize OpenAI-compatible HTTP client."""
        from openai import OpenAI
        return OpenAI(api_key=self.api_key, base_url=self.base_url)
    
    def generate_content(self, ...) -> ModelResponse:
        """Generate content with SDK-first, HTTP fallback."""
        
        # Try SDK first
        if self.sdk_client:
            try:
                response = self._generate_with_sdk(...)
                logger.info("GLM SDK call successful")
                return response
            except Exception as e:
                logger.warning(f"GLM SDK failed: {e}, falling back to HTTP")
        
        # Fallback to HTTP
        if self.http_client:
            response = self._generate_with_http(...)
            logger.info("GLM HTTP fallback successful")
            return response
        
        raise RuntimeError("Both SDK and HTTP clients unavailable")
    
    def _generate_with_sdk(self, ...) -> ModelResponse:
        """Generate using zai-sdk."""
        response = self.sdk_client.chat.completions.create(...)
        
        # Use GLM response handler
        from .response_handlers import GLMResponseHandler
        handler = GLMResponseHandler()
        parsed = handler.parse(response)
        
        return ModelResponse(
            content=parsed.content,
            usage=parsed.usage,
            model_name=model_name,
            friendly_name="GLM",
            provider=ProviderType.GLM,
            metadata={
                "finish_reason": parsed.finish_reason,
                "sdk_used": "zai-sdk",
                **parsed.metadata
            }
        )
    
    def _generate_with_http(self, ...) -> ModelResponse:
        """Generate using OpenAI-compatible HTTP."""
        # Use parent class implementation
        return super().generate_content(...)
```

---

## 📋 Design Principle #3: Model Capability Registry

### Problem
No validation of which parameters each model supports.

### Solution: Capability-Based Routing

**File:** `src/providers/model_capabilities/registry.py`
```python
from dataclasses import dataclass
from typing import Optional, List
from enum import Enum

class ParameterSupport(Enum):
    """Parameter support levels."""
    SUPPORTED = "supported"
    NOT_SUPPORTED = "not_supported"
    EXPERIMENTAL = "experimental"

@dataclass
class ModelCapabilities:
    """Capabilities for a specific model."""
    model_name: str
    provider: str
    context_window: int
    supports_thinking_mode: ParameterSupport
    supports_temperature: ParameterSupport
    supports_tools: ParameterSupport
    supports_web_search: ParameterSupport
    supports_streaming: ParameterSupport
    supports_vision: ParameterSupport
    max_output_tokens: Optional[int] = None
    
    def validate_parameter(self, param_name: str, param_value: any) -> tuple[bool, Optional[str]]:
        """Validate if parameter is supported."""
        support_attr = f"supports_{param_name}"
        if not hasattr(self, support_attr):
            return True, None  # Unknown parameter, allow
        
        support = getattr(self, support_attr)
        if support == ParameterSupport.NOT_SUPPORTED:
            return False, f"Model {self.model_name} does not support {param_name}"
        elif support == ParameterSupport.EXPERIMENTAL:
            return True, f"Parameter {param_name} is experimental for {self.model_name}"
        
        return True, None


class ModelCapabilityRegistry:
    """Registry of model capabilities."""
    
    def __init__(self):
        self._capabilities = {}
        self._load_capabilities()
    
    def _load_capabilities(self):
        """Load capabilities from configuration modules."""
        from .kimi_capabilities import KIMI_CAPABILITIES
        from .glm_capabilities import GLM_CAPABILITIES
        
        self._capabilities.update(KIMI_CAPABILITIES)
        self._capabilities.update(GLM_CAPABILITIES)
    
    def get_capabilities(self, model_name: str) -> Optional[ModelCapabilities]:
        """Get capabilities for a model."""
        return self._capabilities.get(model_name)
    
    def validate_parameters(self, model_name: str, params: dict) -> tuple[dict, List[str]]:
        """Validate parameters for a model.
        
        Returns:
            (valid_params, warnings)
        """
        caps = self.get_capabilities(model_name)
        if not caps:
            return params, [f"Unknown model: {model_name}"]
        
        valid_params = {}
        warnings = []
        
        for param_name, param_value in params.items():
            is_valid, warning = caps.validate_parameter(param_name, param_value)
            if is_valid:
                valid_params[param_name] = param_value
                if warning:
                    warnings.append(warning)
            else:
                warnings.append(warning)
        
        return valid_params, warnings
```

**File:** `src/providers/model_capabilities/kimi_capabilities.py`
```python
from .registry import ModelCapabilities, ParameterSupport

KIMI_CAPABILITIES = {
    "kimi-k2-0905-preview": ModelCapabilities(
        model_name="kimi-k2-0905-preview",
        provider="KIMI",
        context_window=256000,
        supports_thinking_mode=ParameterSupport.NOT_SUPPORTED,  # K2 doesn't support thinking_mode
        supports_temperature=ParameterSupport.SUPPORTED,
        supports_tools=ParameterSupport.SUPPORTED,
        supports_web_search=ParameterSupport.SUPPORTED,
        supports_streaming=ParameterSupport.SUPPORTED,
        supports_vision=ParameterSupport.NOT_SUPPORTED,
        max_output_tokens=32768,
    ),
    
    "kimi-thinking-preview": ModelCapabilities(
        model_name="kimi-thinking-preview",
        provider="KIMI",
        context_window=256000,
        supports_thinking_mode=ParameterSupport.SUPPORTED,  # Thinking model supports it
        supports_temperature=ParameterSupport.SUPPORTED,
        supports_tools=ParameterSupport.SUPPORTED,
        supports_web_search=ParameterSupport.SUPPORTED,
        supports_streaming=ParameterSupport.SUPPORTED,
        supports_vision=ParameterSupport.NOT_SUPPORTED,
        max_output_tokens=32768,
    ),
    
    # Add other Kimi models...
}
```

**File:** `src/providers/model_capabilities/glm_capabilities.py`
```python
GLM_CAPABILITIES = {
    "glm-4.6": ModelCapabilities(
        model_name="glm-4.6",
        provider="GLM",
        context_window=200000,
        supports_thinking_mode=ParameterSupport.SUPPORTED,
        supports_temperature=ParameterSupport.SUPPORTED,
        supports_tools=ParameterSupport.SUPPORTED,
        supports_web_search=ParameterSupport.SUPPORTED,
        supports_streaming=ParameterSupport.SUPPORTED,
        supports_vision=ParameterSupport.NOT_SUPPORTED,
        max_output_tokens=65536,
    ),
    
    # Add other GLM models...
}
```

---

## 📋 Design Principle #4: Centralized Timeout Management

### Problem
Timeouts hardcoded in scripts instead of .env configuration.

### Solution: Timeout Manager

**File:** `src/providers/timeout_manager/config.py`
```python
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class TimeoutConfig:
    """Centralized timeout configuration from .env."""
    
    # Foundation
    http_client: float
    
    # Tool level
    simple_tool: float
    workflow_tool: float
    expert_analysis: float
    
    # Provider level
    glm: float
    kimi: float
    kimi_web_search: float
    
    # Infrastructure (auto-calculated)
    daemon: float
    shim: float
    client: float
    
    @classmethod
    def from_env(cls) -> "TimeoutConfig":
        """Load timeout configuration from environment."""
        http_client = float(os.getenv("EX_HTTP_TIMEOUT_SECONDS", "300"))
        simple_tool = float(os.getenv("SIMPLE_TOOL_TIMEOUT_SECS", "60"))
        workflow_tool = float(os.getenv("WORKFLOW_TOOL_TIMEOUT_SECS", "300"))
        expert_analysis = float(os.getenv("EXPERT_ANALYSIS_TIMEOUT_SECS", "180"))
        
        glm = float(os.getenv("GLM_TIMEOUT_SECS", "90"))
        kimi = float(os.getenv("KIMI_TIMEOUT_SECS", "120"))
        kimi_web_search = float(os.getenv("KIMI_WEB_SEARCH_TIMEOUT_SECS", "150"))
        
        # Auto-calculate infrastructure timeouts
        daemon = workflow_tool * 1.5
        shim = workflow_tool * 2.0
        client = workflow_tool * 2.5
        
        return cls(
            http_client=http_client,
            simple_tool=simple_tool,
            workflow_tool=workflow_tool,
            expert_analysis=expert_analysis,
            glm=glm,
            kimi=kimi,
            kimi_web_search=kimi_web_search,
            daemon=daemon,
            shim=shim,
            client=client,
        )
    
    def validate_hierarchy(self) -> List[str]:
        """Validate timeout hierarchy is correct."""
        errors = []
        
        if self.expert_analysis >= self.workflow_tool:
            errors.append(f"Expert analysis timeout ({self.expert_analysis}s) must be < workflow tool timeout ({self.workflow_tool}s)")
        
        if self.workflow_tool >= self.daemon:
            errors.append(f"Workflow tool timeout ({self.workflow_tool}s) must be < daemon timeout ({self.daemon}s)")
        
        if self.http_client < self.workflow_tool:
            errors.append(f"HTTP client timeout ({self.http_client}s) must be >= workflow tool timeout ({self.workflow_tool}s)")
        
        return errors


# Global timeout configuration
_timeout_config: Optional[TimeoutConfig] = None

def get_timeout_config() -> TimeoutConfig:
    """Get global timeout configuration."""
    global _timeout_config
    if _timeout_config is None:
        _timeout_config = TimeoutConfig.from_env()
        errors = _timeout_config.validate_hierarchy()
        if errors:
            logger.warning(f"Timeout hierarchy validation errors: {errors}")
    return _timeout_config
```

---

## 📋 Implementation Plan

### Phase 1: Response Handlers (Week 1)
1. Create `response_handlers/` module
2. Implement `BaseResponseHandler`
3. Implement `KimiResponseHandler`
4. Implement `GLMResponseHandler`
5. Update `kimi_chat.py` to use handler
6. Update `glm_chat.py` to use handler
7. Test all providers with edge cases

### Phase 2: Model Capabilities (Week 2)
1. Create `model_capabilities/` module
2. Implement `ModelCapabilityRegistry`
3. Define Kimi model capabilities
4. Define GLM model capabilities
5. Integrate with parameter validation
6. Test parameter validation

### Phase 3: Timeout Management (Week 3)
1. Create `timeout_manager/` module
2. Implement `TimeoutConfig`
3. Implement timeout hierarchy validation
4. Update all timeout references to use config
5. Test timeout coordination

### Phase 4: Integration & Testing (Week 4)
1. Integration testing
2. Edge case testing
3. Documentation updates
4. Performance testing

---

## 📊 Success Criteria

1. ✅ All providers extract finish_reason
2. ✅ Response completeness validated
3. ✅ Invalid parameters rejected with warnings
4. ✅ Timeouts coordinated properly
5. ✅ No hardcoded timeouts in scripts
6. ✅ SDK-first fallback working for GLM
7. ✅ Provider-specific schemas handled correctly

---

**This is proper architecture, not a quick fix.**

