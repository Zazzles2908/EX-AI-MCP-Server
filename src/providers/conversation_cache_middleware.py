"""
Conversation Cache Middleware Integration

This module provides middleware integration to easily add conversation
caching capabilities to the existing EX-AI MCP Server provider system.

Usage:
1. Import the middleware
2. Wrap existing providers with caching
3. Enable conversation ID tracking in requests
4. Automatic caching benefits with minimal code changes

Example integration:
    from providers.conversation_cache_middleware import ConversationCacheMiddleware
    
    middleware = ConversationCacheMiddleware()
    provider = middleware.wrap_provider(existing_provider)
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional

from .conversation_context_cache import get_conversation_cache, ConversationContextCache
from .cached_provider_wrapper import CachedModelProvider
from .base import ModelProvider

logger = logging.getLogger(__name__)


class ConversationCacheMiddleware:
    """
    Middleware for adding conversation caching to existing providers.
    
    This middleware:
    - Wraps existing providers transparently
    - Maintains backward compatibility
    - Provides configuration options
    - Handles conversation ID extraction from various sources
    """
    
    def __init__(
        self,
        conversation_cache: Optional[ConversationContextCache] = None,
        enable_by_default: bool = True,
        caching_strategies: Optional[Dict[str, str]] = None
    ):
        """
        Initialize conversation cache middleware.
        
        Args:
            conversation_cache: Optional conversation cache instance
            enable_by_default: Enable caching by default for all providers
            caching_strategies: Provider-specific caching strategies
        """
        self._conversation_cache = conversation_cache  # Store for lazy initialization
        self.enable_by_default = enable_by_default
        self.caching_strategies = caching_strategies or {
            "minimax": "full",      # MiniMax benefits from full caching
            "glm": "response",      # GLM: cache responses primarily
            "kimi": "context",      # Kimi: cache conversation context
            "openai": "response",   # Default strategies
            "anthropic": "full"
        }
        
        # Track wrapped providers
        self._wrapped_providers: Dict[str, CachedModelProvider] = {}
        
        logger.info(
            f"ConversationCacheMiddleware initialized: "
            f"enabled_by_default={enable_by_default}, "
            f"strategies={len(self.caching_strategies)} providers configured"
        )
    
    @property
    def conversation_cache(self) -> ConversationContextCache:
        """Lazy initialization of conversation cache."""
        if self._conversation_cache is None:
            # Use asyncio.run for synchronous property access
            self._conversation_cache = asyncio.run(get_conversation_cache())
        return self._conversation_cache

    def wrap_provider(
        self,
        provider: ModelProvider,
        provider_name: Optional[str] = None,
        enable_caching: Optional[bool] = None,
        caching_strategy: Optional[str] = None
    ) -> CachedModelProvider:
        """
        Wrap an existing provider with conversation caching.
        
        Args:
            provider: Existing model provider to wrap
            provider_name: Optional provider name for strategy lookup
            enable_caching: Override default caching enablement
            caching_strategy: Override default caching strategy
            
        Returns:
            CachedModelProvider wrapper
        """
        provider_type = provider.get_provider_type().value
        effective_name = provider_name or provider_type
        
        # Determine caching configuration
        should_enable_caching = (
            enable_caching if enable_caching is not None 
            else self.enable_by_default
        )
        
        strategy = (
            caching_strategy or 
            self.caching_strategies.get(effective_name, "full")
        )
        
        if not should_enable_caching:
            # Return original provider if caching is disabled
            logger.info(f"Caching disabled for provider {effective_name}")
            return provider
        
        # Check if already wrapped
        wrapper_key = f"{effective_name}_{id(provider)}"
        if wrapper_key in self._wrapped_providers:
            logger.debug(f"Provider {effective_name} already wrapped, returning existing wrapper")
            return self._wrapped_providers[wrapper_key]
        
        # Create cached provider
        cached_provider = CachedModelProvider(
            provider=provider,
            conversation_cache=self.conversation_cache,
            enable_context_caching=strategy in ["full", "context"],
            enable_response_caching=strategy in ["full", "response"]
        )
        
        self._wrapped_providers[wrapper_key] = cached_provider
        
        logger.info(
            f"Wrapped provider {effective_name} with caching strategy: {strategy}"
        )
        
        return cached_provider

    def extract_conversation_id(
        self,
        request_data: Dict[str, Any],
        fallback_sources: Optional[List[str]] = None
    ) -> Optional[str]:
        """
        Extract conversation ID from request data using various sources.
        
        Args:
            request_data: Request data to extract from
            fallback_sources: List of field names to check for conversation ID
            
        Returns:
            Extracted conversation ID or None
        """
        if fallback_sources is None:
            fallback_sources = [
                "conversation_id", "session_id", "chat_id", "thread_id",
                "user_id", "request_id", "correlation_id", "trace_id"
            ]
        
        # Check direct fields
        for field in fallback_sources:
            if field in request_data and request_data[field]:
                return str(request_data[field])
        
        # Check nested fields
        nested_paths = [
            ("metadata", "conversation_id"),
            ("context", "session_id"),
            ("headers", "x-conversation-id"),
            ("request", "conversation_id"),
            ("user", "session_id")
        ]
        
        for parent, child in nested_paths:
            if parent in request_data and isinstance(request_data[parent], dict):
                if child in request_data[parent] and request_data[parent][child]:
                    return str(request_data[parent][child])
        
        return None

    def get_caching_stats(self) -> Dict[str, Any]:
        """Get comprehensive caching statistics."""
        try:
            cache_stats = asyncio.create_task(self.conversation_cache.get_cache_stats())
            
            # Get wrapper statistics
            wrapper_stats = {
                "wrapped_providers": len(self._wrapped_providers),
                "provider_strategies": self.caching_strategies.copy(),
                "default_enabled": self.enable_by_default
            }
            
            return {
                "cache_performance": cache_stats,
                "wrapper_configuration": wrapper_stats
            }
            
        except Exception as e:
            logger.error(f"Error getting caching stats: {e}")
            return {"error": str(e)}

    async def clear_provider_cache(self, provider_name: str) -> int:
        """Clear cache for a specific provider."""
        try:
            provider_cache = await self.conversation_cache.clear_provider_cache(provider_name)
            logger.info(f"Cleared {provider_cache} entries for provider {provider_name}")
            return provider_cache
        except Exception as e:
            logger.error(f"Error clearing provider cache for {provider_name}: {e}")
            return 0

    async def clear_all_cache(self) -> int:
        """Clear all conversation caches."""
        try:
            total_cleared = 0
            for provider_name in self.caching_strategies.keys():
                cleared = await self.clear_provider_cache(provider_name)
                total_cleared += cleared
            
            logger.info(f"Cleared {total_cleared} total cache entries")
            return total_cleared
        except Exception as e:
            logger.error(f"Error clearing all cache: {e}")
            return 0

    def add_provider_strategy(self, provider_name: str, strategy: str):
        """Add or update caching strategy for a provider."""
        valid_strategies = ["full", "context", "response", "none"]
        if strategy not in valid_strategies:
            raise ValueError(f"Invalid strategy: {strategy}. Valid options: {valid_strategies}")
        
        self.caching_strategies[provider_name] = strategy
        logger.info(f"Updated caching strategy for {provider_name}: {strategy}")


# Global middleware instance
_global_middleware: Optional[ConversationCacheMiddleware] = None


async def get_conversation_cache_middleware() -> ConversationCacheMiddleware:
    """Get the global conversation cache middleware instance."""
    global _global_middleware
    if _global_middleware is None:
        _global_middleware = ConversationCacheMiddleware()
    return _global_middleware


# Integration helpers for easy deployment

async def wrap_existing_provider(
    provider: ModelProvider,
    enable_caching: bool = True,
    strategy: str = "full"
) -> CachedModelProvider:
    """
    Convenience function to wrap an existing provider with caching.
    
    Args:
        provider: Existing model provider
        enable_caching: Whether to enable caching
        strategy: Caching strategy ("full", "context", "response", "none")
        
    Returns:
        CachedModelProvider wrapper
    """
    middleware = await get_conversation_cache_middleware()
    
    if not enable_caching:
        return provider
    
    return middleware.wrap_provider(
        provider=provider,
        enable_caching=True,
        caching_strategy=strategy
    )


async def enable_caching_for_provider_registry(provider_registry):
    """
    Add caching to all providers in a provider registry.
    
    This function integrates with existing provider registries to add
    caching capabilities transparently.
    
    Args:
        provider_registry: Provider registry object
    """
    middleware = await get_conversation_cache_middleware()
    
    # Get list of providers from registry
    providers = getattr(provider_registry, '_providers', {})
    
    wrapped_count = 0
    for provider_name, provider in providers.items():
        try:
            wrapped_provider = middleware.wrap_provider(provider, provider_name)
            if wrapped_provider != provider:
                wrapped_count += 1
                logger.info(f"Wrapped provider {provider_name} with caching")
        except Exception as e:
            logger.error(f"Failed to wrap provider {provider_name}: {e}")
    
    logger.info(f"Caching middleware integration complete: {wrapped_count} providers wrapped")


async def setup_conversation_caching(
    max_cache_size_mb: int = 100,
    default_ttl: float = 3600,
    enable_metrics: bool = True
) -> ConversationCacheMiddleware:
    """
    Setup conversation caching system with configuration.
    
    Args:
        max_cache_size_mb: Maximum cache size in megabytes
        default_ttl: Default time-to-live for cache entries
        enable_metrics: Enable performance metrics collection
        
    Returns:
        Configured ConversationCacheMiddleware instance
    """
    global _global_middleware
    
    # Create conversation cache with specified configuration
    from .kv_cache_manager import ParallaxKVCacheManager
    
    cache_manager = ParallaxKVCacheManager(
        max_size_mb=max_cache_size_mb,
        default_ttl=default_ttl,
        enable_metrics=enable_metrics
    )
    
    conversation_cache = ConversationContextCache(
        cache_manager=cache_manager,
        enable_response_caching=True,
        max_conversation_history=50
    )
    
    # Create middleware with the configured cache
    _global_middleware = ConversationCacheMiddleware(
        conversation_cache=conversation_cache,
        enable_by_default=True
    )
    
    logger.info(
        f"Conversation caching system configured: "
        f"{max_cache_size_mb}MB cache, {default_ttl}s TTL, metrics={enable_metrics}"
    )
    
    return _global_middleware
