"""
Conversation Context Cache - Parallax-Inspired Implementation

This module provides intelligent conversation context caching for AI model providers.
It caches conversation history, context, and responses to improve performance
and reduce token usage for repeated interactions.

Features:
- Automatic conversation history caching
- Context-aware response reuse
- Provider-specific caching strategies
- Memory-efficient storage
- Intelligent invalidation based on conversation changes
"""

import asyncio
import hashlib
import json
import logging
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict

from .kv_cache_manager import get_kv_cache, ParallaxKVCacheManager

logger = logging.getLogger(__name__)


@dataclass
class ConversationContext:
    """Represents a conversation context with metadata."""
    conversation_id: str
    messages: List[Dict[str, Any]]
    model: str
    provider: str
    system_prompt: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: float = None
    last_accessed: float = None
    
    def __post_init__(self):
        import time
        if self.created_at is None:
            self.created_at = time.time()
        if self.last_accessed is None:
            self.last_accessed = time.time()
        if self.metadata is None:
            self.metadata = {}


@dataclass
class CachedResponse:
    """Represents a cached AI response."""
    response_id: str
    content: str
    model: str
    provider: str
    usage: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
    thinking_process: Optional[str] = None
    timestamp: float = None
    
    def __post_init__(self):
        import time
        if self.timestamp is None:
            self.timestamp = time.time()
        if self.metadata is None:
            self.metadata = {}


class ConversationContextCache:
    """
    Intelligent conversation context caching system.
    
    Features:
    - Automatic conversation history caching
    - Context-based response lookup
    - Provider-aware caching strategies
    - Intelligent cache invalidation
    - Performance optimization
    """
    
    def __init__(
        self,
        cache_manager: ParallaxKVCacheManager,
        enable_response_caching: bool = True,
        max_conversation_history: int = 50,
        similarity_threshold: float = 0.8
    ):
        """
        Initialize conversation context cache.
        
        Args:
            cache_manager: Underlying KV cache manager
            enable_response_caching: Enable response caching
            max_conversation_history: Maximum messages to cache per conversation
            similarity_threshold: Threshold for context similarity
        """
        self.cache_manager = cache_manager
        self.enable_response_caching = enable_response_caching
        self.max_conversation_history = max_conversation_history
        self.similarity_threshold = similarity_threshold
        
        # Cache key prefixes
        self.CONTEXT_PREFIX = "context:"
        self.RESPONSE_PREFIX = "response:"
        self.SIMILARITY_PREFIX = "similar:"
        
        # Provider-specific configurations
        self.provider_configs = {
            'minimax': {
                'cache_context': True,
                'max_tokens_per_request': 4000,
                'thinking_cache_ttl': 7200,  # 2 hours
                'response_cache_ttl': 3600,  # 1 hour
            },
            'glm': {
                'cache_context': True,
                'max_tokens_per_request': 4096,
                'response_cache_ttl': 1800,  # 30 minutes
            },
            'kimi': {
                'cache_context': True,
                'max_tokens_per_request': 4096,
                'response_cache_ttl': 1800,  # 30 minutes
            }
        }
        
        logger.info(
            f"ConversationContextCache initialized: "
            f"response_caching={enable_response_caching}, "
            f"max_history={max_conversation_history}, "
            f"similarity_threshold={similarity_threshold}"
        )

    def _generate_conversation_hash(self, conversation_id: str) -> str:
        """Generate hash for conversation identification."""
        return hashlib.sha256(conversation_id.encode()).hexdigest()[:16]

    def _generate_context_key(self, conversation_id: str, provider: str, model: str) -> str:
        """Generate cache key for conversation context."""
        conv_hash = self._generate_conversation_hash(conversation_id)
        return f"{self.CONTEXT_PREFIX}{conv_hash}:{provider}:{model}"

    def _generate_response_key(self, request_hash: str, provider: str, model: str) -> str:
        """Generate cache key for AI response."""
        return f"{self.RESPONSE_PREFIX}{request_hash}:{provider}:{model}"

    def _generate_similarity_key(self, content_hash: str) -> str:
        """Generate cache key for similar content lookup."""
        return f"{self.SIMILARITY_PREFIX}{content_hash}"

    def _calculate_content_similarity(self, content1: str, content2: str) -> float:
        """
        Calculate similarity between two content strings.
        
        Uses a simple token-based similarity calculation.
        For production, consider using embeddings or more sophisticated methods.
        """
        # Simple word-based similarity
        words1 = set(content1.lower().split())
        words2 = set(content2.lower().split())
        
        if not words1 and not words2:
            return 1.0
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union) if union else 0.0

    async def get_conversation_context(
        self,
        conversation_id: str,
        provider: str,
        model: str
    ) -> Optional[ConversationContext]:
        """
        Retrieve cached conversation context.
        
        Args:
            conversation_id: Unique conversation identifier
            provider: AI provider (minimax, glm, kimi)
            model: Model name
            
        Returns:
            Cached conversation context or None
        """
        context_key = self._generate_context_key(conversation_id, provider, model)
        
        try:
            cached_data = await self.cache_manager.get(context_key)
            if cached_data:
                # Convert back to ConversationContext
                if isinstance(cached_data, dict):
                    return ConversationContext(**cached_data)
                else:
                    logger.warning(f"Unexpected cache data format for context {context_key}")
                    return None
        except Exception as e:
            logger.error(f"Error retrieving conversation context {context_key}: {e}")
            return None

    async def cache_conversation_context(
        self,
        conversation_id: str,
        messages: List[Dict[str, Any]],
        provider: str,
        model: str,
        system_prompt: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Cache conversation context.
        
        Args:
            conversation_id: Unique conversation identifier
            messages: List of conversation messages
            provider: AI provider
            model: Model name
            system_prompt: Optional system prompt
            metadata: Optional metadata
            
        Returns:
            True if successfully cached
        """
        try:
            # Limit conversation history size
            if len(messages) > self.max_conversation_history:
                messages = messages[-self.max_conversation_history:]
            
            context = ConversationContext(
                conversation_id=conversation_id,
                messages=messages,
                model=model,
                provider=provider,
                system_prompt=system_prompt,
                metadata=metadata or {}
            )
            
            context_key = self._generate_context_key(conversation_id, provider, model)
            
            # Get provider-specific TTL
            provider_config = self.provider_configs.get(provider, {})
            ttl = provider_config.get('context_cache_ttl', 3600)  # Default 1 hour
            
            await self.cache_manager.set(
                context_key,
                asdict(context),
                ttl=ttl,
                tags={'conversation', provider, model}
            )
            
            logger.debug(f"Cached conversation context: {conversation_id} ({len(messages)} messages)")
            return True
            
        except Exception as e:
            logger.error(f"Error caching conversation context: {e}")
            return False

    async def get_cached_response(
        self,
        provider: str,
        model: str,
        messages: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        **kwargs
    ) -> Optional[CachedResponse]:
        """
        Retrieve cached AI response if available.
        
        Args:
            provider: AI provider
            model: Model name
            messages: Conversation messages
            system_prompt: Optional system prompt
            temperature: Generation temperature
            **kwargs: Additional generation parameters
            
        Returns:
            Cached response or None
        """
        if not self.enable_response_caching:
            return None
        
        try:
            # Generate request hash for caching
            request_data = {
                'messages': messages,
                'system_prompt': system_prompt,
                'temperature': temperature,
                **kwargs
            }
            request_hash = hashlib.sha256(
                json.dumps(request_data, sort_keys=True).encode()
            ).hexdigest()[:16]
            
            response_key = self._generate_response_key(request_hash, provider, model)
            
            cached_data = await self.cache_manager.get(response_key)
            if cached_data:
                if isinstance(cached_data, dict):
                    return CachedResponse(**cached_data)
                else:
                    logger.warning(f"Unexpected cache data format for response {response_key}")
                    return None
        except Exception as e:
            logger.error(f"Error retrieving cached response: {e}")
            
        return None

    async def cache_response(
        self,
        provider: str,
        model: str,
        messages: List[Dict[str, Any]],
        response_content: str,
        usage: Dict[str, Any],
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        thinking_process: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> bool:
        """
        Cache AI response for future reuse.
        
        Args:
            provider: AI provider
            model: Model name
            messages: Conversation messages
            response_content: Generated response content
            usage: Token usage information
            system_prompt: Optional system prompt
            temperature: Generation temperature
            thinking_process: Optional thinking process (for MiniMax)
            metadata: Optional metadata
            **kwargs: Additional generation parameters
            
        Returns:
            True if successfully cached
        """
        if not self.enable_response_caching:
            return False
        
        try:
            # Generate request hash for caching
            request_data = {
                'messages': messages,
                'system_prompt': system_prompt,
                'temperature': temperature,
                **kwargs
            }
            request_hash = hashlib.sha256(
                json.dumps(request_data, sort_keys=True).encode()
            ).hexdigest()[:16]
            
            response = CachedResponse(
                response_id=request_hash,
                content=response_content,
                model=model,
                provider=provider,
                usage=usage,
                thinking_process=thinking_process,
                metadata=metadata or {}
            )
            
            response_key = self._generate_response_key(request_hash, provider, model)
            
            # Get provider-specific TTL
            provider_config = self.provider_configs.get(provider, {})
            ttl = provider_config.get('response_cache_ttl', 1800)  # Default 30 minutes
            
            await self.cache_manager.set(
                response_key,
                asdict(response),
                ttl=ttl,
                tags={'response', provider, model}
            )
            
            logger.debug(f"Cached response for {provider}:{model} ({len(response_content)} chars)")
            return True
            
        except Exception as e:
            logger.error(f"Error caching response: {e}")
            return False

    async def find_similar_contexts(
        self,
        content: str,
        provider: str,
        model: str,
        limit: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Find similar conversation contexts for reuse.
        
        Args:
            content: Content to match against
            provider: AI provider
            model: Model name
            limit: Maximum number of results
            
        Returns:
            List of (context_id, similarity_score) tuples
        """
        try:
            # Get all conversation contexts for this provider/model
            contexts = await self.cache_manager.get_by_tags({provider, model})
            
            if not contexts:
                return []
            
            # Calculate similarity scores
            similarities = []
            content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
            
            for context_key, context_data in contexts.items():
                if isinstance(context_data, ConversationContext):
                    # Get the last message for comparison
                    if context_data.messages:
                        last_message = context_data.messages[-1].get('content', '')
                        similarity = self._calculate_content_similarity(content, last_message)
                        if similarity >= self.similarity_threshold:
                            conversation_id = context_data.conversation_id
                            similarities.append((conversation_id, similarity))
            
            # Sort by similarity and return top results
            similarities.sort(key=lambda x: x[1], reverse=True)
            return similarities[:limit]
            
        except Exception as e:
            logger.error(f"Error finding similar contexts: {e}")
            return []

    async def clear_conversation(
        self,
        conversation_id: str,
        provider: str,
        model: str
    ) -> bool:
        """Clear cached context for a specific conversation."""
        try:
            context_key = self._generate_context_key(conversation_id, provider, model)
            deleted = await self.cache_manager.delete(context_key)
            
            if deleted:
                logger.debug(f"Cleared conversation context: {conversation_id}")
            
            return deleted
        except Exception as e:
            logger.error(f"Error clearing conversation context: {e}")
            return False

    async def clear_provider_cache(self, provider: str) -> int:
        """Clear all cached data for a specific provider."""
        try:
            tags = {'conversation', provider}
            deleted_count = await self.cache_manager.clear_tags(tags)
            
            logger.info(f"Cleared {deleted_count} entries for provider {provider}")
            return deleted_count
        except Exception as e:
            logger.error(f"Error clearing provider cache: {e}")
            return 0

    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        try:
            metrics = self.cache_manager.get_metrics()
            
            # Add conversation-specific metrics
            conversation_stats = {
                'cached_contexts': 0,
                'cached_responses': 0,
                'providers': set(),
                'models': set()
            }
            
            # Count contexts and responses by scanning cache
            for key in self.cache_manager._cache.keys():
                if key.startswith(self.CONTEXT_PREFIX):
                    conversation_stats['cached_contexts'] += 1
                elif key.startswith(self.RESPONSE_PREFIX):
                    conversation_stats['cached_responses'] += 1
                    
                # Extract provider/model info from key
                if ':' in key:
                    parts = key.split(':')
                    if len(parts) >= 3:
                        conversation_stats['providers'].add(parts[2])
                        conversation_stats['models'].add(parts[3])
            
            # Convert sets to lists for JSON serialization
            conversation_stats['providers'] = list(conversation_stats['providers'])
            conversation_stats['models'] = list(conversation_stats['models'])
            
            return {**metrics, **conversation_stats}
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {}


# Global conversation cache instance
_global_conversation_cache: Optional[ConversationContextCache] = None


async def get_conversation_cache() -> ConversationContextCache:
    """Get the global conversation cache instance."""
    global _global_conversation_cache
    if _global_conversation_cache is None:
        cache_manager = await get_kv_cache()
        _global_conversation_cache = ConversationContextCache(
            cache_manager=cache_manager,
            enable_response_caching=True,
            max_conversation_history=50,
            similarity_threshold=0.8
        )
    return _global_conversation_cache


async def close_conversation_cache():
    """Close the global conversation cache instance."""
    global _global_conversation_cache
    if _global_conversation_cache:
        await _global_conversation_cache.cache_manager.close()
        _global_conversation_cache = None
