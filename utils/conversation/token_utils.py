"""
Token counting and validation utilities for conversation management.

This module provides token counting functionality with caching and support
for multiple model tokenizers (GPT, GLM, Kimi).
"""

from typing import Dict, Optional, List, Any
import tiktoken
import functools
import logging

logger = logging.getLogger(__name__)

# Token limits (from EXAI recommendations)
MAX_HISTORY_TOKENS = 50_000  # Hard limit per conversation
MAX_HISTORY_MESSAGES = 20    # Keep last 20 messages only
MAX_SINGLE_MESSAGE_TOKENS = 10_000  # Warn if single message exceeds this
MAX_TOTAL_BUDGET = 8_000     # Per-request token budget


class TokenCounter:
    """
    Token counter with caching and multi-model support.
    
    Supports GPT, GLM, and Kimi models with appropriate tokenizers.
    Uses LRU caching to avoid recalculation of token counts.
    """
    
    def __init__(self):
        self._tokenizers: Dict[str, any] = {}
        self.cache_size_limit = 1000
    
    def _get_tokenizer(self, model_name: str):
        """Get or create tokenizer for the specified model."""
        if model_name not in self._tokenizers:
            # Default to cl100k_base (GPT-4) if model not recognized
            try:
                if "gpt" in model_name.lower():
                    self._tokenizers[model_name] = tiktoken.encoding_for_model(model_name)
                elif "glm" in model_name.lower():
                    # Use a generic tokenizer for GLM models
                    self._tokenizers[model_name] = tiktoken.get_encoding("cl100k_base")
                elif "kimi" in model_name.lower() or "moonshot" in model_name.lower():
                    # Use a generic tokenizer for Kimi/Moonshot models
                    self._tokenizers[model_name] = tiktoken.get_encoding("cl100k_base")
                else:
                    # Default fallback
                    self._tokenizers[model_name] = tiktoken.get_encoding("cl100k_base")
            except Exception as e:
                logger.warning(f"Failed to get tokenizer for {model_name}: {e}. Using cl100k_base fallback.")
                # Fallback to cl100k_base if model-specific encoding fails
                self._tokenizers[model_name] = tiktoken.get_encoding("cl100k_base")
        
        return self._tokenizers[model_name]
    
    @functools.lru_cache(maxsize=1000)
    def count_tokens(self, text: str, model_name: str = "gpt-4") -> int:
        """
        Count tokens in text for the specified model.
        Uses LRU cache to avoid recalculation.
        
        Args:
            text: Text to count tokens for
            model_name: Model name (gpt-4, glm-4.6, kimi-k2-0905-preview, etc.)
            
        Returns:
            Number of tokens in the text
        """
        if not text:
            return 0
        
        try:
            tokenizer = self._get_tokenizer(model_name)
            return len(tokenizer.encode(text))
        except Exception as e:
            logger.error(f"Error counting tokens: {e}")
            # Fallback: rough estimate (4 chars per token)
            return len(text) // 4
    
    def count_messages_tokens(self, messages: List[Any], model_name: str = "gpt-4") -> int:
        """
        Count tokens in a list of messages.
        
        Args:
            messages: List of messages (dict or string format)
            model_name: Model name for tokenization
            
        Returns:
            Total number of tokens across all messages
        """
        total = 0
        for message in messages:
            if isinstance(message, dict):
                # Handle message dict format
                content = message.get("content", "")
                role = message.get("role", "")
                total += self.count_tokens(content, model_name)
                total += self.count_tokens(role, model_name)
                # Add some tokens for formatting (approximate)
                total += 4
            else:
                # Handle string format
                total += self.count_tokens(str(message), model_name)
        
        return total


def validate_token_budget(content: str, history: List[Dict[str, Any]], 
                         max_total: int = MAX_TOTAL_BUDGET,
                         model_name: str = "gpt-4") -> tuple[str, List[Dict[str, Any]]]:
    """
    Validate and enforce token budget across content and history.
    
    This implements EXAI's dual-layer validation strategy:
    - Layer 1: Validate individual message doesn't exceed budget
    - Layer 2: Trim history to fit within remaining budget
    
    Args:
        content: New content to add
        history: Existing conversation history
        max_total: Maximum total tokens allowed
        model_name: Model name for tokenization
        
    Returns:
        Tuple of (validated_content, trimmed_history)
        
    Raises:
        ValueError: If content alone exceeds max_total (circuit breaker)
    """
    counter = TokenCounter()
    content_tokens = counter.count_tokens(content, model_name)
    
    # Circuit breaker - fail fast if content exceeds budget
    if content_tokens > max_total:
        raise ValueError(
            f"Content exceeds token budget: {content_tokens} > {max_total}. "
            f"This is a circuit breaker to prevent token explosion."
        )
    
    remaining_tokens = max_total - content_tokens
    
    # Build history within remaining budget (newest first)
    trimmed_history = []
    current_tokens = 0
    
    for turn in reversed(history):
        turn_tokens = turn.get('tokens', counter.count_tokens(turn.get('content', ''), model_name))
        
        if current_tokens + turn_tokens <= remaining_tokens:
            trimmed_history.insert(0, turn)
            current_tokens += turn_tokens
        else:
            # Can't fit this turn, stop here
            break
    
    if len(trimmed_history) < len(history):
        logger.info(
            f"Trimmed history from {len(history)} to {len(trimmed_history)} turns "
            f"to fit within {max_total} token budget"
        )
    
    return content, trimmed_history


def truncate_to_token_limit(text: str, max_tokens: int, model_name: str = "gpt-4") -> str:
    """
    Truncate text to fit within token limit.
    
    Args:
        text: Text to truncate
        max_tokens: Maximum tokens allowed
        model_name: Model name for tokenization
        
    Returns:
        Truncated text that fits within token limit
    """
    counter = TokenCounter()
    current_tokens = counter.count_tokens(text, model_name)
    
    if current_tokens <= max_tokens:
        return text
    
    # Binary search to find the right truncation point
    tokenizer = counter._get_tokenizer(model_name)
    tokens = tokenizer.encode(text)
    
    if len(tokens) <= max_tokens:
        return text
    
    # Truncate tokens and decode
    truncated_tokens = tokens[:max_tokens]
    truncated_text = tokenizer.decode(truncated_tokens)
    
    logger.warning(
        f"Truncated text from {current_tokens} to {max_tokens} tokens "
        f"({len(text)} to {len(truncated_text)} chars)"
    )
    
    return truncated_text


def validate_message_tokens(content: str, model_name: str = "gpt-4", 
                            max_tokens: int = MAX_SINGLE_MESSAGE_TOKENS) -> tuple[bool, int]:
    """
    Validate that a single message doesn't exceed token limits.
    
    Args:
        content: Message content to validate
        model_name: Model name for tokenization
        max_tokens: Maximum tokens allowed for a single message
        
    Returns:
        Tuple of (is_valid, token_count)
    """
    counter = TokenCounter()
    token_count = counter.count_tokens(content, model_name)
    
    is_valid = token_count <= max_tokens
    
    if not is_valid:
        logger.warning(
            f"Message exceeds token limit: {token_count} > {max_tokens} tokens"
        )
    
    return is_valid, token_count


# Global token counter instance for reuse
_global_counter = TokenCounter()


def count_tokens(text: str, model_name: str = "gpt-4") -> int:
    """
    Convenience function for counting tokens using global counter.
    
    Args:
        text: Text to count tokens for
        model_name: Model name for tokenization
        
    Returns:
        Number of tokens in the text
    """
    return _global_counter.count_tokens(text, model_name)

