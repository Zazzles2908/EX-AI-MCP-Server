"""
Conversation Memory Data Models

This module provides the core data structures for conversation persistence
in the EX-AI MCP Server. It enables multi-turn AI-to-AI conversations by
defining the models used to store conversation state across request cycles.

Key Components:
- ConversationTurn: Single exchange in a conversation
- ThreadContext: Complete conversation context for a thread
- Configuration constants for conversation limits
- Storage backend access
- UUID validation utilities

For detailed architectural documentation, see utils/conversation_memory.py
"""

import logging
import os
import uuid
from typing import Any, Optional

from pydantic import BaseModel

logger = logging.getLogger(__name__)

# ================================================================================
# Configuration Constants
# ================================================================================

# Get max conversation turns from environment, default to 20 turns (10 exchanges)
try:
    MAX_CONVERSATION_TURNS = int(os.getenv("MAX_CONVERSATION_TURNS", "20"))
    if MAX_CONVERSATION_TURNS <= 0:
        logger.warning(f"Invalid MAX_CONVERSATION_TURNS value ({MAX_CONVERSATION_TURNS}), using default of 20 turns")
        MAX_CONVERSATION_TURNS = 20
except ValueError:
    logger.warning(
        f"Invalid MAX_CONVERSATION_TURNS value ('{os.getenv('MAX_CONVERSATION_TURNS')}'), using default of 20 turns"
    )
    MAX_CONVERSATION_TURNS = 20

# Get conversation timeout from environment (in hours), default to 3 hours
try:
    CONVERSATION_TIMEOUT_HOURS = int(os.getenv("CONVERSATION_TIMEOUT_HOURS", "3"))
    if CONVERSATION_TIMEOUT_HOURS <= 0:
        logger.warning(
            f"Invalid CONVERSATION_TIMEOUT_HOURS value ({CONVERSATION_TIMEOUT_HOURS}), using default of 3 hours"
        )
        CONVERSATION_TIMEOUT_HOURS = 3
except ValueError:
    logger.warning(
        f"Invalid CONVERSATION_TIMEOUT_HOURS value ('{os.getenv('CONVERSATION_TIMEOUT_HOURS')}'), using default of 3 hours"
    )
    CONVERSATION_TIMEOUT_HOURS = 3

CONVERSATION_TIMEOUT_SECONDS = CONVERSATION_TIMEOUT_HOURS * 3600


# ================================================================================
# Data Models
# ================================================================================


class ConversationTurn(BaseModel):
    """
    Single turn in a conversation

    Represents one exchange in the AI-to-AI conversation, tracking both
    the content and metadata needed for cross-tool continuation.

    Attributes:
        role: "user" (Claude) or "assistant" (Gemini/O3/etc)
        content: The actual message content/response
        timestamp: ISO timestamp when this turn was created
        files: List of file paths referenced in this specific turn
        images: List of image paths referenced in this specific turn
        tool_name: Which tool generated this turn (for cross-tool tracking)
        model_provider: Provider used (e.g., "google", "openai")
        model_name: Specific model used (e.g., "gemini-2.5-flash", "o3-mini")
        model_metadata: Additional model-specific metadata (e.g., thinking mode, token usage)
    """

    role: str  # "user" or "assistant"
    content: str
    timestamp: str
    files: Optional[list[str]] = None  # Files referenced in this turn
    images: Optional[list[str]] = None  # Images referenced in this turn
    tool_name: Optional[str] = None  # Tool used for this turn
    model_provider: Optional[str] = None  # Model provider (google, openai, etc)
    model_name: Optional[str] = None  # Specific model used
    model_metadata: Optional[dict[str, Any]] = None  # Additional model info


class ThreadContext(BaseModel):
    """
    Complete conversation context for a thread

    Contains all information needed to reconstruct a conversation state
    across different tools and request cycles. This is the core data
    structure that enables cross-tool continuation.

    Attributes:
        thread_id: UUID identifying this conversation thread
        parent_thread_id: UUID of parent thread (for conversation chains)
        created_at: ISO timestamp when thread was created
        last_updated_at: ISO timestamp of last modification
        tool_name: Name of the tool that initiated this thread
        turns: List of all conversation turns in chronological order
        initial_context: Original request data that started the conversation
        session_fingerprint: Optional session fingerprint to scope this thread
        client_friendly_name: Optional friendly client name (e.g., "Claude", "VS Code")
    """

    thread_id: str
    parent_thread_id: Optional[str] = None  # Parent thread for conversation chains
    created_at: str
    last_updated_at: str
    tool_name: str  # Tool that created this thread (preserved for attribution)
    turns: list[ConversationTurn]
    initial_context: dict[str, Any]  # Original request parameters
    session_fingerprint: Optional[str] = None
    client_friendly_name: Optional[str] = None


# ================================================================================
# Storage Backend Access
# ================================================================================


def get_storage():
    """
    Get in-memory storage backend for conversation persistence.

    Returns:
        InMemoryStorage: Thread-safe in-memory storage backend
    """
    from utils.infrastructure.storage_backend import get_storage_backend

    return get_storage_backend()


# ================================================================================
# Utility Functions
# ================================================================================


def _is_valid_uuid(val: str) -> bool:
    """
    Validate UUID format for security

    Ensures thread IDs are valid UUIDs to prevent injection attacks
    and malformed requests.

    Args:
        val: String to validate as UUID

    Returns:
        bool: True if valid UUID format, False otherwise
    """
    try:
        uuid.UUID(val)
        return True
    except ValueError:
        return False

