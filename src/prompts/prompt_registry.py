"""
Provider-Aware Prompt Registry

Centralized prompt management with provider-specific variants for optimal token efficiency
and response quality. Implements Tier 3 of the 4-tier architecture.

Phase 1.3 Implementation - Provider-Aware Prompt Optimization
"""

import logging
from enum import Enum
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class ProviderType(Enum):
    """Supported AI providers."""
    KIMI = "kimi"
    GLM = "glm"
    AUTO = "auto"


class PromptRegistry:
    """
    Centralized prompt management with provider-specific variants.
    
    Architecture:
    - Base prompts: Universal prompts that work with all providers
    - Kimi variants: Optimized for OpenAI-compatible SDK (concise, English-focused)
    - GLM variants: Optimized for zai-sdk (supports Chinese, different format)
    
    Usage:
        registry = PromptRegistry()
        prompt = registry.get_prompt("debug", ProviderType.KIMI)
    """
    
    def __init__(self):
        """Initialize prompt registry with base and variant prompts."""
        self.prompts: Dict[str, Dict[str, str]] = {}
        self._load_prompts()
    
    def _load_prompts(self):
        """Load all prompts from systemprompts module."""
        # Import base tool prompts
        from .chat_prompt import CHAT_PROMPT
        from .debug_prompt import DEBUG_ISSUE_PROMPT
        from .analyze_prompt import ANALYZE_PROMPT
        from .codereview_prompt import CODEREVIEW_PROMPT
        from .thinkdeep_prompt import THINKDEEP_PROMPT

        # Import provider-specific variants
        from .provider_variants import (
            DEBUG_KIMI_VARIANT, DEBUG_GLM_VARIANT,
            ANALYZE_KIMI_VARIANT, ANALYZE_GLM_VARIANT,
            CODEREVIEW_KIMI_VARIANT, CODEREVIEW_GLM_VARIANT,
            CHAT_KIMI_VARIANT, CHAT_GLM_VARIANT,
            THINKDEEP_KIMI_VARIANT, THINKDEEP_GLM_VARIANT,
        )

        # Register base prompts and provider-specific variants
        self.prompts = {
            "chat": {
                "base": CHAT_PROMPT,
                "kimi_variant": CHAT_KIMI_VARIANT,
                "glm_variant": CHAT_GLM_VARIANT,
            },
            "debug": {
                "base": DEBUG_ISSUE_PROMPT,
                "kimi_variant": DEBUG_KIMI_VARIANT,
                "glm_variant": DEBUG_GLM_VARIANT,
            },
            "analyze": {
                "base": ANALYZE_PROMPT,
                "kimi_variant": ANALYZE_KIMI_VARIANT,
                "glm_variant": ANALYZE_GLM_VARIANT,
            },
            "codereview": {
                "base": CODEREVIEW_PROMPT,
                "kimi_variant": CODEREVIEW_KIMI_VARIANT,
                "glm_variant": CODEREVIEW_GLM_VARIANT,
            },
            "thinkdeep": {
                "base": THINKDEEP_PROMPT,
                "kimi_variant": THINKDEEP_KIMI_VARIANT,
                "glm_variant": THINKDEEP_GLM_VARIANT,
            },
        }
    
    def get_prompt(self, tool_name: str, provider: ProviderType) -> str:
        """
        Get prompt with provider-specific optimizations.
        
        Args:
            tool_name: Name of the tool (e.g., "debug", "analyze")
            provider: Provider type (KIMI, GLM, or AUTO)
        
        Returns:
            Optimized prompt string for the provider
        
        Fallback Strategy:
            1. Try provider-specific variant
            2. Fall back to base prompt if variant not available
            3. Raise error if tool not found
        """
        if tool_name not in self.prompts:
            raise ValueError(f"Unknown tool: {tool_name}. Available tools: {list(self.prompts.keys())}")
        
        tool_prompts = self.prompts[tool_name]
        
        # Handle AUTO provider (use base prompt)
        if provider == ProviderType.AUTO:
            return tool_prompts["base"]
        
        # Try provider-specific variant first
        variant_key = f"{provider.value}_variant"
        if variant_key in tool_prompts and tool_prompts[variant_key] is not None:
            return tool_prompts[variant_key]

        # Fall back to base prompt (log for monitoring)
        logger.info(f"Prompt fallback: tool={tool_name}, provider={provider.value}, reason=variant_missing")
        return tool_prompts["base"]
    
    def register_variant(self, tool_name: str, provider: ProviderType, prompt: str):
        """
        Register a provider-specific prompt variant.
        
        Args:
            tool_name: Name of the tool
            provider: Provider type
            prompt: Optimized prompt string
        """
        if tool_name not in self.prompts:
            self.prompts[tool_name] = {"base": None}
        
        variant_key = f"{provider.value}_variant"
        self.prompts[tool_name][variant_key] = prompt
    
    def has_variant(self, tool_name: str, provider: ProviderType) -> bool:
        """
        Check if a provider-specific variant exists.
        
        Args:
            tool_name: Name of the tool
            provider: Provider type
        
        Returns:
            True if variant exists and is not None
        """
        if tool_name not in self.prompts:
            return False
        
        variant_key = f"{provider.value}_variant"
        return (variant_key in self.prompts[tool_name] and 
                self.prompts[tool_name][variant_key] is not None)
    
    def get_available_tools(self) -> list:
        """Get list of all registered tools."""
        return list(self.prompts.keys())
    
    def get_variant_status(self) -> Dict[str, Dict[str, bool]]:
        """
        Get status of all variants across all tools.
        
        Returns:
            Dictionary mapping tool names to variant availability
            Example: {"debug": {"kimi": True, "glm": False}}
        """
        status = {}
        for tool_name in self.prompts:
            status[tool_name] = {
                "kimi": self.has_variant(tool_name, ProviderType.KIMI),
                "glm": self.has_variant(tool_name, ProviderType.GLM),
            }
        return status


# Global registry instance
_registry: Optional[PromptRegistry] = None


def get_registry() -> PromptRegistry:
    """Get or create the global prompt registry instance."""
    global _registry
    if _registry is None:
        _registry = PromptRegistry()
    return _registry

