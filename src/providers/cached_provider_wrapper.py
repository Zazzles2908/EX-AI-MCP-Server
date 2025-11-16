"""
Provider Wrapper with Conversation Context Caching

This module provides wrapped versions of AI providers that automatically
cache conversation contexts and responses to improve performance and
reduce token usage.

Features:
- Automatic conversation context caching
- Response caching and reuse
- Provider-specific optimization strategies
- Intelligent cache invalidation
- Performance monitoring and metrics
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

from .conversation_context_cache import get_conversation_cache, ConversationContextCache
from .base import ModelProvider, ModelResponse

logger = logging.getLogger(__name__)


class CachedModelProvider:
    """
    Wrapper for ModelProvider that adds intelligent conversation caching.
    
    This wrapper:
    - Automatically caches conversation contexts
    - Caches and reuses responses when appropriate
    - Provides performance optimization
    - Handles cache invalidation and cleanup
    """
    
    def __init__(
        self,
        provider: ModelProvider,
        conversation_cache: ConversationContextCache,
        enable_context_caching: bool = True,
        enable_response_caching: bool = True
    ):
        """
        Initialize cached provider wrapper.
        
        Args:
            provider: Underlying model provider
            conversation_cache: Conversation context cache
            enable_context_caching: Enable context caching
            enable_response_caching: Enable response caching
        """
        self.provider = provider
        self.conversation_cache = conversation_cache
        self.enable_context_caching = enable_context_caching
        self.enable_response_caching = enable_response_caching
        
        logger.info(
            f"CachedModelProvider initialized for {provider.get_provider_type().value}: "
            f"context={enable_context_caching}, response={enable_response_caching}"
        )

    async def chat_completions_create(
        self,
        *,
        model: str,
        messages: List[Dict[str, Any]],
        conversation_id: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create chat completion with caching support.
        
        Args:
            model: Model name
            messages: Conversation messages
            conversation_id: Optional conversation identifier for context caching
            system_prompt: Optional system prompt
            temperature: Generation temperature
            **kwargs: Additional parameters
            
        Returns:
            Chat completion response
        """
        provider_type = self.provider.get_provider_type().value
        
        # Try to get cached response if response caching is enabled
        if self.enable_response_caching and conversation_id:
            cached_response = await self.conversation_cache.get_cached_response(
                provider=provider_type,
                model=model,
                messages=messages,
                system_prompt=system_prompt,
                temperature=temperature,
                **kwargs
            )
            
            if cached_response:
                logger.debug(f"Using cached response for {provider_type}:{model}")
                
                # Return cached response in the expected format
                return {
                    "provider": cached_response.provider,
                    "model": cached_response.model,
                    "content": cached_response.content,
                    "thinking": cached_response.thinking_process,
                    "usage": cached_response.usage,
                    "metadata": {
                        **cached_response.metadata,
                        "cached": True,
                        "cache_timestamp": cached_response.timestamp
                    }
                }
        
        # Generate new response
        try:
            response = await self.provider.chat_completions_create(
                model=model,
                messages=messages,
                temperature=temperature,
                **kwargs
            )
            
            # Cache the response if enabled and we have a conversation ID
            if self.enable_response_caching and conversation_id and response.get('content'):
                await self.conversation_cache.cache_response(
                    provider=provider_type,
                    model=model,
                    messages=messages,
                    response_content=response.get('content', ''),
                    usage=response.get('usage', {}),
                    system_prompt=system_prompt,
                    temperature=temperature,
                    thinking_process=response.get('thinking'),
                    metadata=response.get('metadata', {})
                )
            
            # Cache conversation context if enabled
            if self.enable_context_caching and conversation_id:
                await self.conversation_cache.cache_conversation_context(
                    conversation_id=conversation_id,
                    messages=messages,
                    provider=provider_type,
                    model=model,
                    system_prompt=system_prompt,
                    metadata={"last_response": response.get('content', '')[:100]}
                )
            
            return response
            
        except Exception as e:
            logger.error(f"Error in chat completion for {provider_type}:{model}: {e}")
            raise

    async def generate_content(
        self,
        prompt: str,
        model_name: str,
        conversation_id: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_output_tokens: Optional[int] = None,
        **kwargs
    ) -> ModelResponse:
        """
        Generate content with caching support.
        
        Args:
            prompt: Text prompt
            model_name: Model name
            conversation_id: Optional conversation identifier
            system_prompt: Optional system prompt
            temperature: Generation temperature
            max_output_tokens: Maximum output tokens
            **kwargs: Additional parameters
            
        Returns:
            Generated content response
        """
        provider_type = self.provider.get_provider_type().value
        
        # Convert to messages format for caching consistency
        messages = [{"role": "user", "content": prompt}]
        if system_prompt:
            messages.insert(0, {"role": "system", "content": system_prompt})
        
        # Try to get cached response if response caching is enabled
        if self.enable_response_caching and conversation_id:
            cached_response = await self.conversation_cache.get_cached_response(
                provider=provider_type,
                model=model_name,
                messages=messages,
                system_prompt=system_prompt,
                temperature=temperature,
                max_output_tokens=max_output_tokens,
                **kwargs
            )
            
            if cached_response:
                logger.debug(f"Using cached content for {provider_type}:{model_name}")
                
                # Return cached response
                return ModelResponse(
                    content=cached_response.content,
                    provider=self.provider.get_provider_type(),
                    model=cached_response.model,
                    usage=cached_response.usage,
                    metadata={
                        **cached_response.metadata,
                        "cached": True,
                        "cache_timestamp": cached_response.timestamp
                    }
                )
        
        # Generate new content
        try:
            response = await self.provider.generate_content(
                prompt=prompt,
                model_name=model_name,
                system_prompt=system_prompt,
                temperature=temperature,
                max_output_tokens=max_output_tokens,
                **kwargs
            )
            
            # Cache the response if enabled and we have a conversation ID
            if self.enable_response_caching and conversation_id:
                await self.conversation_cache.cache_response(
                    provider=provider_type,
                    model=model_name,
                    messages=messages,
                    response_content=response.content,
                    usage=response.usage,
                    system_prompt=system_prompt,
                    temperature=temperature,
                    metadata=response.metadata
                )
            
            # Cache conversation context if enabled
            if self.enable_context_caching and conversation_id:
                await self.conversation_cache.cache_conversation_context(
                    conversation_id=conversation_id,
                    messages=messages,
                    provider=provider_type,
                    model=model_name,
                    system_prompt=system_prompt,
                    metadata={"last_response": response.content[:100]}
                )
            
            return response
            
        except Exception as e:
            logger.error(f"Error in content generation for {provider_type}:{model_name}: {e}")
            raise

    async def get_conversation_context(
        self,
        conversation_id: str,
        model: str
    ) -> Optional[Dict[str, Any]]:
        """Get cached conversation context."""
        provider_type = self.provider.get_provider_type().value
        
        context = await self.conversation_cache.get_conversation_context(
            conversation_id=conversation_id,
            provider=provider_type,
            model=model
        )
        
        if context:
            return {
                "conversation_id": context.conversation_id,
                "messages": context.messages,
                "system_prompt": context.system_prompt,
                "metadata": context.metadata,
                "created_at": context.created_at,
                "last_accessed": context.last_accessed
            }
        
        return None

    async def clear_conversation(self, conversation_id: str, model: str) -> bool:
        """Clear cached conversation context."""
        provider_type = self.provider.get_provider_type().value
        
        return await self.conversation_cache.clear_conversation(
            conversation_id=conversation_id,
            provider=provider_type,
            model=model
        )

    async def find_similar_contexts(
        self,
        content: str,
        model: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Find similar conversation contexts for reuse."""
        provider_type = self.provider.get_provider_type().value
        
        similar_contexts = await self.conversation_cache.find_similar_contexts(
            content=content,
            provider=provider_type,
            model=model,
            limit=limit
        )
        
        return [
            {
                "conversation_id": conv_id,
                "similarity_score": score
            }
            for conv_id, score in similar_contexts
        ]

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        return asyncio.create_task(self.conversation_cache.get_cache_stats())

    # Delegate all other methods to the underlying provider
    def __getattr__(self, name):
        """Delegate attribute access to the underlying provider."""
        return getattr(self.provider, name)


class CachedProviderFactory:
    """
    Factory for creating cached providers with different caching strategies.
    
    Provides pre-configured cached providers for common use cases:
    - Full caching (context + response)
    - Context only
    - Response only
    - No caching
    """
    
    def __init__(self, conversation_cache: ConversationContextCache):
        self.conversation_cache = conversation_cache
    
    async def create_cached_provider(
        self,
        provider: ModelProvider,
        caching_strategy: str = "full"
    ) -> CachedModelProvider:
        """
        Create a cached provider with specified strategy.
        
        Args:
            provider: Underlying model provider
            caching_strategy: Caching strategy ("full", "context", "response", "none")
            
        Returns:
            CachedModelProvider instance
        """
        strategies = {
            "full": {"context": True, "response": True},
            "context": {"context": True, "response": False},
            "response": {"context": False, "response": True},
            "none": {"context": False, "response": False}
        }
        
        if caching_strategy not in strategies:
            raise ValueError(f"Unknown caching strategy: {caching_strategy}")
        
        config = strategies[caching_strategy]
        
        return CachedModelProvider(
            provider=provider,
            conversation_cache=self.conversation_cache,
            enable_context_caching=config["context"],
            enable_response_caching=config["response"]
        )


# Global cached provider factory
_cached_provider_factory: Optional[CachedProviderFactory] = None


async def get_cached_provider_factory() -> CachedProviderFactory:
    """Get the global cached provider factory."""
    global _cached_provider_factory
    if _cached_provider_factory is None:
        conversation_cache = await get_conversation_cache()
        _cached_provider_factory = CachedProviderFactory(conversation_cache)
    return _cached_provider_factory


async def create_cached_provider(
    provider: ModelProvider,
    caching_strategy: str = "full"
) -> CachedModelProvider:
    """
    Convenience function to create a cached provider.
    
    Args:
        provider: Underlying model provider
        caching_strategy: Caching strategy
        
    Returns:
        CachedModelProvider instance
    """
    factory = await get_cached_provider_factory()
    return await factory.create_cached_provider(provider, caching_strategy)
