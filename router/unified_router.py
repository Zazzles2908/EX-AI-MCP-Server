
"""
Unified Router for EX-AI MCP Server

Integrates RouterService into the main request pipeline to eliminate dual routing.
Provides centralized model selection and request routing.
"""
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass
import json
import os

from src.providers.registry import ModelProviderRegistry as R
from src.providers.base import ProviderType

logger = logging.getLogger("unified_router")

@dataclass
class RouteDecision:
    """Represents a routing decision with metadata."""
    requested: str
    chosen: str
    reason: str
    provider: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None

    def to_json(self) -> str:
        return json.dumps({
            "event": "route_decision",
            "requested": self.requested,
            "chosen": self.chosen,
            "reason": self.reason,
            "provider": self.provider,
            "meta": self.meta or {},
        }, ensure_ascii=False)

class UnifiedRouter:
    """Unified router that handles all model selection and request routing."""
    
    def __init__(self):
        # Model preferences from environment
        self._fast_default = os.getenv("FAST_MODEL_DEFAULT", "glm-4.5-flash")
        self._long_default = os.getenv("LONG_MODEL_DEFAULT", "kimi-k2-0711-preview")
        self._default_model = os.getenv("DEFAULT_MODEL", self._fast_default)
        
        # Diagnostics
        self._diag_enabled = os.getenv("ROUTER_DIAGNOSTICS_ENABLED", "false").lower() == "true"
        
        # Initialize provider registry
        self._registry = R()
        
        logger.info(f"Unified router initialized with defaults: fast={self._fast_default}, long={self._long_default}")
    
    async def initialize(self) -> None:
        """Initialize the router and perform preflight checks."""
        try:
            # Perform provider availability checks
            available_providers = []
            
            if self._registry.has_provider(ProviderType.GLM):
                available_providers.append("GLM")
            
            if self._registry.has_provider(ProviderType.KIMI):
                available_providers.append("KIMI")
            
            logger.info(f"Available providers: {available_providers}")
            
            if not available_providers:
                logger.warning("No providers available - check API keys")
            
        except Exception as e:
            logger.error(f"Router initialization failed: {e}")
            raise
    
    def choose_model(self, requested: Optional[str] = None, context: Optional[str] = None) -> RouteDecision:
        """
        Choose the best model for a request.
        
        Args:
            requested: Explicitly requested model name
            context: Context hint for model selection (e.g., 'long', 'fast')
        
        Returns:
            RouteDecision with chosen model and reasoning
        """
        # Handle explicit model requests
        if requested and requested != "auto":
            if self._is_model_available(requested):
                decision = RouteDecision(
                    requested=requested,
                    chosen=requested,
                    reason="explicit_request",
                    provider=self._get_provider_for_model(requested)
                )
            else:
                # Fallback to default if requested model unavailable
                chosen = self._default_model
                decision = RouteDecision(
                    requested=requested,
                    chosen=chosen,
                    reason="fallback_unavailable",
                    provider=self._get_provider_for_model(chosen),
                    meta={"original_unavailable": requested}
                )
        else:
            # Auto selection based on context
            if context == "long":
                chosen = self._long_default
                reason = "auto_long_context"
            elif context == "fast":
                chosen = self._fast_default
                reason = "auto_fast"
            else:
                chosen = self._default_model
                reason = "auto_default"
            
            decision = RouteDecision(
                requested=requested or "auto",
                chosen=chosen,
                reason=reason,
                provider=self._get_provider_for_model(chosen)
            )
        
        # Log decision if diagnostics enabled
        if self._diag_enabled:
            logger.info(decision.to_json())
        
        return decision
    
    def _is_model_available(self, model_name: str) -> bool:
        """Check if a model is available through any provider."""
        try:
            # Check GLM models
            if model_name.startswith("glm-") and self._registry.has_provider(ProviderType.GLM):
                return True
            
            # Check Kimi models  
            if model_name.startswith("kimi-") and self._registry.has_provider(ProviderType.KIMI):
                return True
            
            return False
        except Exception:
            return False
    
    def _get_provider_for_model(self, model_name: str) -> Optional[str]:
        """Get the provider name for a given model."""
        if model_name.startswith("glm-"):
            return "GLM"
        elif model_name.startswith("kimi-"):
            return "KIMI"
        return None
    
    def get_available_models(self) -> Dict[str, list]:
        """Get list of available models by provider."""
        models = {}
        
        if self._registry.has_provider(ProviderType.GLM):
            models["GLM"] = ["glm-4.5-flash", "glm-4-plus", "glm-4-air", "glm-4-airx"]
        
        if self._registry.has_provider(ProviderType.KIMI):
            models["KIMI"] = ["kimi-k2-0711-preview", "moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"]
        
        return models
    
    def get_router_status(self) -> Dict[str, Any]:
        """Get router status for diagnostics."""
        return {
            "fast_default": self._fast_default,
            "long_default": self._long_default,
            "default_model": self._default_model,
            "diagnostics_enabled": self._diag_enabled,
            "available_models": self.get_available_models()
        }
