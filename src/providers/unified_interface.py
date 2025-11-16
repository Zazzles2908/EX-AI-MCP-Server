"""
Unified Provider Interface

Abstracts SDK differences between Kimi (OpenAI-compatible) and GLM (Z.ai) providers
while maintaining provider-specific optimizations.

Phase 1.4 Implementation - Unified Provider Interface
"""

import logging
import os
from typing import Any, Dict, Optional, Protocol
from enum import Enum

# Import PromptRegistry for provider-aware prompts
from src.prompts.prompt_registry import ProviderType, get_registry

logger = logging.getLogger(__name__)


class ProviderAdapter(Protocol):
    """Protocol defining the interface all provider adapters must implement."""
    
    def format_prompt(self, system_prompt: str, user_prompt: str, **kwargs) -> Dict[str, Any]:
        """Format prompt according to provider requirements."""
        ...
    
    def format_messages(self, messages: list) -> Dict[str, Any]:
        """Format message array according to provider requirements."""
        ...
    
    def handle_error(self, error: Exception) -> Dict[str, Any]:
        """Handle provider-specific errors."""
        ...


class KimiAdapter:
    """
    Adapter for Kimi (Moonshot) provider using OpenAI-compatible SDK.
    
    Format: Messages array with role/content structure
    SDK: OpenAI-compatible (from openai import OpenAI)
    """
    
    def __init__(self):
        self.provider_type = ProviderType.KIMI
        logger.debug("KimiAdapter initialized")
    
    def format_prompt(self, system_prompt: str, user_prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Format prompt for Kimi using OpenAI messages format.
        
        Args:
            system_prompt: System-level instructions
            user_prompt: User's input/question
            **kwargs: Additional parameters (model, temperature, etc.)
        
        Returns:
            Dictionary with 'messages' key containing role/content array
        """
        formatted = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        }
        
        # Add optional parameters
        if "model" in kwargs:
            formatted["model"] = kwargs["model"]
        if "temperature" in kwargs:
            formatted["temperature"] = kwargs["temperature"]
        if "max_tokens" in kwargs:
            formatted["max_tokens"] = kwargs["max_tokens"]
        
        return formatted
    
    def format_messages(self, messages: list) -> Dict[str, Any]:
        """
        Format message array for Kimi.
        
        Args:
            messages: List of message dictionaries with role/content
        
        Returns:
            Dictionary with 'messages' key
        """
        return {"messages": messages}
    
    def handle_error(self, error: Exception) -> Dict[str, Any]:
        """
        Handle Kimi/OpenAI-specific errors.
        
        Args:
            error: Exception from Kimi API
        
        Returns:
            Standardized error dictionary
        """
        error_type = type(error).__name__
        error_msg = str(error)
        
        # Map common OpenAI errors
        if "rate_limit" in error_msg.lower():
            return {
                "error": "rate_limit_exceeded",
                "message": "Kimi API rate limit exceeded",
                "provider": "kimi",
                "retry_after": 60
            }
        elif "invalid_api_key" in error_msg.lower():
            return {
                "error": "authentication_failed",
                "message": "Invalid Kimi API key",
                "provider": "kimi"
            }
        elif "timeout" in error_msg.lower():
            return {
                "error": "timeout",
                "message": "Kimi API request timed out",
                "provider": "kimi",
                "retry_after": 30
            }
        else:
            return {
                "error": "provider_error",
                "message": f"Kimi error: {error_msg}",
                "provider": "kimi",
                "error_type": error_type
            }


class GLMAdapter:
    """
    Adapter for GLM (Z.ai) provider.
    
    Format: Concatenated prompt string
    SDK: zai-sdk==0.0.4 (from zai import ZaiClient)
    """
    
    def __init__(self):
        self.provider_type = ProviderType.GLM
        logger.debug("GLMAdapter initialized")
    
    def format_prompt(self, system_prompt: str, user_prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Format prompt for GLM using concatenated string format.
        
        Args:
            system_prompt: System-level instructions
            user_prompt: User's input/question
            **kwargs: Additional parameters (model, temperature, etc.)
        
        Returns:
            Dictionary with 'prompt' key containing concatenated string
        """
        # GLM uses concatenated format
        concatenated = f"System: {system_prompt}\n\nUser: {user_prompt}\n\nAssistant:"
        
        formatted = {"prompt": concatenated}
        
        # Add optional parameters
        if "model" in kwargs:
            formatted["model"] = kwargs["model"]
        if "temperature" in kwargs:
            formatted["temperature"] = kwargs["temperature"]
        if "max_tokens" in kwargs:
            formatted["max_tokens"] = kwargs["max_tokens"]
        
        return formatted
    
    def format_messages(self, messages: list) -> Dict[str, Any]:
        """
        Format message array for GLM by concatenating into single prompt.
        
        Args:
            messages: List of message dictionaries with role/content
        
        Returns:
            Dictionary with 'prompt' key
        """
        # Convert messages array to concatenated format
        parts = []
        for msg in messages:
            role = msg.get("role", "user").capitalize()
            content = msg.get("content", "")
            parts.append(f"{role}: {content}")
        
        parts.append("Assistant:")
        concatenated = "\n\n".join(parts)
        
        return {"prompt": concatenated}
    
    def handle_error(self, error: Exception) -> Dict[str, Any]:
        """
        Handle GLM/Z.ai-specific errors.
        
        Args:
            error: Exception from GLM API
        
        Returns:
            Standardized error dictionary
        """
        error_type = type(error).__name__
        error_msg = str(error)
        
        # Map common GLM errors
        if "rate_limit" in error_msg.lower() or "限流" in error_msg:
            return {
                "error": "rate_limit_exceeded",
                "message": "GLM API rate limit exceeded",
                "provider": "glm",
                "retry_after": 60
            }
        elif "invalid" in error_msg.lower() and "key" in error_msg.lower():
            return {
                "error": "authentication_failed",
                "message": "Invalid GLM API key",
                "provider": "glm"
            }
        elif "timeout" in error_msg.lower() or "超时" in error_msg:
            return {
                "error": "timeout",
                "message": "GLM API request timed out",
                "provider": "glm",
                "retry_after": 30
            }
        else:
            return {
                "error": "provider_error",
                "message": f"GLM error: {error_msg}",
                "provider": "glm",
                "error_type": error_type
            }


class UnifiedProviderInterface:
    """
    Unified interface abstracting provider SDK differences.
    
    Provides consistent API for interacting with different AI providers
    while maintaining provider-specific optimizations.
    
    Usage:
        interface = UnifiedProviderInterface(ProviderType.KIMI)
        formatted = interface.format_prompt("You are helpful", "Hello")
        # Returns: {"messages": [{"role": "system", "content": "You are helpful"}, ...]}
    """
    
    def __init__(self, provider_type: ProviderType):
        """
        Initialize unified interface for specified provider.
        
        Args:
            provider_type: Provider to use (KIMI or GLM)
        """
        self.provider_type = provider_type
        self.adapter = self._get_adapter()
        self.prompt_registry = get_registry()
        logger.info(f"UnifiedProviderInterface initialized for {provider_type.value}")
    
    def _get_adapter(self) -> ProviderAdapter:
        """Get appropriate adapter for provider type."""
        if self.provider_type == ProviderType.KIMI:
            return KimiAdapter()
        elif self.provider_type == ProviderType.GLM:
            return GLMAdapter()
        else:
            raise ValueError(f"Unsupported provider type: {self.provider_type}")
    
    def format_prompt(self, system_prompt: str, user_prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Format prompt according to provider requirements.
        
        Args:
            system_prompt: System-level instructions
            user_prompt: User's input/question
            **kwargs: Additional parameters
        
        Returns:
            Provider-specific formatted prompt
        """
        return self.adapter.format_prompt(system_prompt, user_prompt, **kwargs)
    
    def format_messages(self, messages: list) -> Dict[str, Any]:
        """
        Format message array according to provider requirements.
        
        Args:
            messages: List of message dictionaries
        
        Returns:
            Provider-specific formatted messages
        """
        return self.adapter.format_messages(messages)
    
    def get_optimized_prompt(self, tool_name: str) -> str:
        """
        Get provider-optimized prompt for specified tool.
        
        Args:
            tool_name: Name of the tool (e.g., "debug", "analyze")
        
        Returns:
            Provider-optimized prompt string
        """
        return self.prompt_registry.get_prompt(tool_name, self.provider_type)
    
    def handle_error(self, error: Exception) -> Dict[str, Any]:
        """
        Handle provider-specific errors with unified error format.
        
        Args:
            error: Exception from provider
        
        Returns:
            Standardized error dictionary
        """
        return self.adapter.handle_error(error)


# Factory function for easy instantiation
def get_provider_interface(provider: str) -> UnifiedProviderInterface:
    """
    Factory function to create provider interface.
    
    Args:
        provider: Provider name ("kimi", "glm", or "auto")
    
    Returns:
        UnifiedProviderInterface instance
    """
    provider_lower = provider.lower()
    
    if provider_lower == "kimi":
        return UnifiedProviderInterface(ProviderType.KIMI)
    elif provider_lower == "glm":
        return UnifiedProviderInterface(ProviderType.GLM)
    elif provider_lower == "auto":
        # Default to KIMI for AUTO
        return UnifiedProviderInterface(ProviderType.KIMI)
    else:
        raise ValueError(f"Unknown provider: {provider}")

