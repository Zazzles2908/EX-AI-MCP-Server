"""
Model context management for dynamic token allocation.

This module provides a clean abstraction for model-specific token management,
ensuring that token limits are properly calculated based on the current model
being used, not global constants.

CONVERSATION MEMORY INTEGRATION:
This module works closely with the conversation memory system to provide
optimal token allocation for multi-turn conversations:

1. DUAL PRIORITIZATION STRATEGY SUPPORT:
   - Provides separate token budgets for conversation history vs. files
   - Enables the conversation memory system to apply newest-first prioritization
   - Ensures optimal balance between context preservation and new content

2. MODEL-SPECIFIC ALLOCATION:
   - Dynamic allocation based on model capabilities (context window size)
   - Conservative allocation for smaller models (O3: 200K context)
   - Generous allocation for larger models (Gemini: 1M+ context)
   - Adapts token distribution ratios based on model capacity

3. CROSS-TOOL CONSISTENCY:
   - Provides consistent token budgets across different tools
   - Enables seamless conversation continuation between tools
   - Supports conversation reconstruction with proper budget management
"""

import logging
from dataclasses import dataclass
from typing import Any, Optional, TYPE_CHECKING

from config import DEFAULT_MODEL

# REFACTORED: Removed get_registry_instance import - now using instance-based registry
# Avoid circular import: src.providers imports utils, utils.model.context imports src.providers
# Move imports inside methods where they're actually used
if TYPE_CHECKING:
    from src.providers import ModelCapabilities, ModelProviderRegistry

logger = logging.getLogger(__name__)


@dataclass
class TokenAllocation:
    """Token allocation strategy for a model."""

    total_tokens: int
    content_tokens: int
    response_tokens: int
    file_tokens: int
    history_tokens: int

    @property
    def available_for_prompt(self) -> int:
        """Tokens available for the actual prompt after allocations."""
        return self.content_tokens - self.file_tokens - self.history_tokens


class ModelContext:
    """
    Encapsulates model-specific information and token calculations.

    This class provides a single source of truth for all model-related
    token calculations, ensuring consistency across the system.
    """

    def __init__(self, model_name: str, model_option: Optional[str] = None):
        self.model_name = model_name
        self.model_option = model_option  # Store optional model option (e.g., "for", "against", etc.)
        self._provider = None
        self._capabilities = None
        self._token_allocation = None

    @property
    def provider(self):
        """Get the model provider lazily."""
        if self._provider is None:
            import logging
            logging.info(f"MODEL_CONTEXT_DEBUG: Getting provider for model '{self.model_name}'")
            from src.providers.registry_core import get_registry_instance  # Import here to avoid circular import
            registry = get_registry_instance()  # Use singleton to see initialized providers
            self._provider = registry.get_provider_for_model(self.model_name)
            logging.info(f"MODEL_CONTEXT_DEBUG: get_provider_for_model returned: {self._provider}")
            if not self._provider:
                available_models = registry.get_available_models()
                logging.info(f"MODEL_CONTEXT_DEBUG: Available models: {available_models}")
                raise ValueError(f"Model '{self.model_name}' is not available. Available models: {available_models}")
        return self._provider

    @property
    def capabilities(self):  # Remove type hint to avoid circular import at module level
        """Get model capabilities lazily."""
        if self._capabilities is None:
            from src.providers import ModelCapabilities  # Import here to avoid circular import
            self._capabilities = self.provider.get_capabilities(self.model_name)
        return self._capabilities

    def calculate_token_allocation(self, reserved_for_response: Optional[int] = None) -> TokenAllocation:
        """
        Calculate token allocation based on model capacity and conversation requirements.

        This method implements the core token budget calculation that supports the
        dual prioritization strategy used in conversation memory and file processing:

        TOKEN ALLOCATION STRATEGY:
        1. CONTENT vs RESPONSE SPLIT:
           - Smaller models (< 300K): 60% content, 40% response (conservative)
           - Larger models (≥ 300K): 80% content, 20% response (generous)

        2. CONTENT SUB-ALLOCATION:
           - File tokens: 30-40% of content budget for newest file versions
           - History tokens: 40-50% of content budget for conversation context
           - Remaining: Available for tool-specific prompt content

        3. CONVERSATION MEMORY INTEGRATION:
           - History allocation enables conversation reconstruction in reconstruct_thread_context()
           - File allocation supports newest-first file prioritization in tools
           - Remaining budget passed to tools via _remaining_tokens parameter

        Args:
            reserved_for_response: Override response token reservation

        Returns:
            TokenAllocation with calculated budgets for dual prioritization strategy
        """
        total_tokens = self.capabilities.context_window

        # SECURITY FIX: Add bounds checking for very large contexts
        # Prevent memory exhaustion with extremely large contexts
        import os
        max_context = int(os.getenv("MAX_MODEL_CONTEXT_TOKENS", str(2_000_000)))  # Default: 2M tokens max

        if total_tokens > max_context:
            logger.warning(
                f"Model context window ({total_tokens:,} tokens) exceeds maximum allowed "
                f"({max_context:,} tokens). Clamping to prevent memory exhaustion. "
                f"Set MAX_MODEL_CONTEXT_TOKENS env var to increase if needed."
            )
            total_tokens = max_context

        # Also enforce minimum context size
        min_context = int(os.getenv("MIN_MODEL_CONTEXT_TOKENS", "1000"))  # Default: 1K tokens minimum
        if total_tokens < min_context:
            logger.warning(
                f"Model context window ({total_tokens:,} tokens) is below minimum "
                f"({min_context:,} tokens). This may cause functionality issues."
            )
            total_tokens = min_context

        # Dynamic allocation based on model capacity
        if total_tokens < 300_000:
            # Smaller context models (O3): Conservative allocation
            content_ratio = 0.6  # 60% for content
            response_ratio = 0.4  # 40% for response
            file_ratio = 0.3  # 30% of content for files
            history_ratio = 0.5  # 50% of content for history
        else:
            # Larger context models (Gemini): More generous allocation
            content_ratio = 0.8  # 80% for content
            response_ratio = 0.2  # 20% for response
            file_ratio = 0.4  # 40% of content for files
            history_ratio = 0.4  # 40% of content for history

        # Calculate allocations
        content_tokens = int(total_tokens * content_ratio)
        response_tokens = reserved_for_response or int(total_tokens * response_ratio)

        # Sub-allocations within content budget
        file_tokens = int(content_tokens * file_ratio)
        history_tokens = int(content_tokens * history_ratio)

        # Additional validation: ensure allocations don't exceed total
        total_allocated = content_tokens + response_tokens
        if total_allocated > total_tokens:
            logger.warning(
                f"Token allocations ({total_allocated:,}) exceed total context "
                f"({total_tokens:,}). Scaling down proportionally."
            )
            # Scale down proportionally
            scale_factor = total_tokens / total_allocated
            content_tokens = int(content_tokens * scale_factor)
            response_tokens = int(response_tokens * scale_factor)
            file_tokens = int(file_tokens * scale_factor)
            history_tokens = int(history_tokens * scale_factor)

        allocation = TokenAllocation(
            total_tokens=total_tokens,
            content_tokens=content_tokens,
            response_tokens=response_tokens,
            file_tokens=file_tokens,
            history_tokens=history_tokens,
        )

        logger.debug(f"Token allocation for {self.model_name}:")
        logger.debug(f"  Total: {allocation.total_tokens:,}")
        logger.debug(f"  Content: {allocation.content_tokens:,} ({content_ratio:.0%})")
        logger.debug(f"  Response: {allocation.response_tokens:,} ({response_ratio:.0%})")
        logger.debug(f"  Files: {allocation.file_tokens:,} ({file_ratio:.0%} of content)")
        logger.debug(f"  History: {allocation.history_tokens:,} ({history_ratio:.0%} of content)")

        return allocation

    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text using model-specific tokenizer.

        For now, uses simple estimation. Can be enhanced with model-specific
        tokenizers (tiktoken for OpenAI, etc.) in the future.
        """
        # TODO: Integrate model-specific tokenizers
        # For now, use conservative estimation
        return len(text) // 3  # Conservative estimate

    @classmethod
    def from_arguments(cls, arguments: dict[str, Any]) -> "ModelContext":
        """Create ModelContext from tool arguments."""
        model_name = arguments.get("model") or DEFAULT_MODEL
        return cls(model_name)
