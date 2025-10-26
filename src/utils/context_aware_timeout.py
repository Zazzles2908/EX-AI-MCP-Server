"""Context-aware timeout calculator for AI model requests.

PHASE 2.3 FIX (2025-10-25): EXAI Recommendation #4
Implements dynamic timeout calculation based on context window usage.

Rationale:
- Larger context windows require more processing time
- Timeout should scale with context size to prevent premature failures
- Provides buffer for network variability and API processing time
"""

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


class ContextAwareTimeout:
    """Calculate timeouts based on context window usage.
    
    EXAI Recommendation: Consider context window size in timeout calculations.
    Larger contexts naturally require more processing time.
    """
    
    # Base timeout for minimal context (in seconds)
    BASE_TIMEOUT = 30
    
    # Context size thresholds (in tokens)
    SMALL_CONTEXT = 10_000      # < 10k tokens
    MEDIUM_CONTEXT = 50_000     # 10k-50k tokens
    LARGE_CONTEXT = 100_000     # 50k-100k tokens
    XLARGE_CONTEXT = 200_000    # 100k-200k tokens
    # > 200k tokens = XXLARGE
    
    # Timeout multipliers for each context size
    TIMEOUT_MULTIPLIERS = {
        "small": 1.0,    # 30s base
        "medium": 1.3,   # 39s (30% increase)
        "large": 1.6,    # 48s (60% increase)
        "xlarge": 2.0,   # 60s (100% increase)
        "xxlarge": 2.5,  # 75s (150% increase)
    }
    
    @classmethod
    def calculate_timeout(
        cls,
        context_tokens: int,
        base_timeout: Optional[int] = None,
        model_name: Optional[str] = None
    ) -> int:
        """Calculate timeout based on context size.
        
        Args:
            context_tokens: Number of tokens in the context
            base_timeout: Optional base timeout override (defaults to BASE_TIMEOUT)
            model_name: Optional model name for model-specific adjustments
            
        Returns:
            Calculated timeout in seconds
        """
        if base_timeout is None:
            base_timeout = cls.BASE_TIMEOUT
        
        # Determine context size category
        if context_tokens < cls.SMALL_CONTEXT:
            category = "small"
        elif context_tokens < cls.MEDIUM_CONTEXT:
            category = "medium"
        elif context_tokens < cls.LARGE_CONTEXT:
            category = "large"
        elif context_tokens < cls.XLARGE_CONTEXT:
            category = "xlarge"
        else:
            category = "xxlarge"
        
        # Get multiplier
        multiplier = cls.TIMEOUT_MULTIPLIERS[category]
        
        # Calculate timeout
        timeout = int(base_timeout * multiplier)
        
        logger.debug(
            f"Context-aware timeout: {context_tokens} tokens ({category}) "
            f"→ {timeout}s (base={base_timeout}s, multiplier={multiplier}x)"
        )
        
        return timeout
    
    @classmethod
    def estimate_context_tokens(
        cls,
        messages: list[dict],
        model_name: str = "unknown"
    ) -> int:
        """Estimate context tokens from messages.
        
        This is a rough estimate using character count / 4 (common approximation).
        For more accurate counting, use tiktoken or model-specific tokenizers.
        
        Args:
            messages: List of message dictionaries
            model_name: Model name for model-specific estimation
            
        Returns:
            Estimated token count
        """
        total_chars = 0
        
        for msg in messages:
            # Count role
            role = msg.get("role", "")
            total_chars += len(role)
            
            # Count content
            content = msg.get("content", "")
            if isinstance(content, str):
                total_chars += len(content)
            elif isinstance(content, list):
                # Handle multi-modal content (text + images)
                for item in content:
                    if isinstance(item, dict):
                        text = item.get("text", "")
                        total_chars += len(text)
            
            # Count tool calls
            tool_calls = msg.get("tool_calls", [])
            if tool_calls:
                for tc in tool_calls:
                    if isinstance(tc, dict):
                        func = tc.get("function", {})
                        total_chars += len(str(func))
        
        # Rough approximation: 1 token ≈ 4 characters
        estimated_tokens = total_chars // 4
        
        logger.debug(
            f"Estimated context tokens: {estimated_tokens} "
            f"(from {total_chars} chars, {len(messages)} messages)"
        )
        
        return estimated_tokens
    
    @classmethod
    def get_timeout_for_request(
        cls,
        messages: list[dict],
        model_name: str,
        base_timeout: Optional[int] = None
    ) -> int:
        """Get timeout for a specific request.
        
        Convenience method that estimates context and calculates timeout.
        
        Args:
            messages: List of message dictionaries
            model_name: Model name
            base_timeout: Optional base timeout override
            
        Returns:
            Calculated timeout in seconds
        """
        # Estimate context tokens
        context_tokens = cls.estimate_context_tokens(messages, model_name)
        
        # Calculate timeout
        timeout = cls.calculate_timeout(
            context_tokens=context_tokens,
            base_timeout=base_timeout,
            model_name=model_name
        )
        
        return timeout


def get_context_aware_timeout(
    messages: list[dict],
    model_name: str,
    base_timeout: Optional[int] = None
) -> int:
    """Get context-aware timeout for a request.
    
    Convenience function for easy integration.
    
    Args:
        messages: List of message dictionaries
        model_name: Model name
        base_timeout: Optional base timeout override
        
    Returns:
        Calculated timeout in seconds
    """
    return ContextAwareTimeout.get_timeout_for_request(
        messages=messages,
        model_name=model_name,
        base_timeout=base_timeout
    )


# Example usage:
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.DEBUG)
    
    # Test with different context sizes
    test_cases = [
        (5_000, "small context"),
        (25_000, "medium context"),
        (75_000, "large context"),
        (150_000, "xlarge context"),
        (250_000, "xxlarge context"),
    ]
    
    print("\nContext-Aware Timeout Calculator")
    print("=" * 60)
    
    for tokens, description in test_cases:
        timeout = ContextAwareTimeout.calculate_timeout(tokens)
        print(f"{description:20s} ({tokens:>7,} tokens) → {timeout:>2}s timeout")
    
    print("\nWith custom base timeout (40s):")
    print("=" * 60)
    
    for tokens, description in test_cases:
        timeout = ContextAwareTimeout.calculate_timeout(tokens, base_timeout=40)
        print(f"{description:20s} ({tokens:>7,} tokens) → {timeout:>2}s timeout")

