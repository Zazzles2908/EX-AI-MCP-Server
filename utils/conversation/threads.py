"""
Conversation Thread Management

This module provides thread lifecycle management for conversation persistence.
It handles creating, retrieving, and updating conversation threads, as well as
collecting files and images from conversation history.

Key Functions:
- create_thread: Initialize new conversation thread
- get_thread: Retrieve thread by ID
- add_turn: Add turn to existing thread
- get_thread_chain: Traverse parent chain
- get_conversation_file_list: Extract files with newest-first priority
- get_conversation_image_list: Extract images with newest-first priority

For detailed architectural documentation, see utils/conversation_memory.py
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from utils.conversation.models import (
    CONVERSATION_TIMEOUT_SECONDS,
    MAX_CONVERSATION_TURNS,
    ConversationTurn,
    ThreadContext,
    _is_valid_uuid,
    get_storage,
)

# Storage factory will be imported lazily to avoid circular imports
# (storage_factory imports from memory, which imports from threads)
STORAGE_FACTORY_AVAILABLE = None  # Will be set on first use
_storage_factory_cache = None  # Cache the imported function
_storage_backend_instance = None  # CACHE the storage backend instance to avoid creating 60+ instances per request

logger = logging.getLogger(__name__)


def _get_storage_factory():
    """
    Lazy import of storage factory to avoid circular imports.

    Returns:
        get_conversation_storage function or None if import fails
    """
    global STORAGE_FACTORY_AVAILABLE, _storage_factory_cache

    if STORAGE_FACTORY_AVAILABLE is None:
        try:
            from utils.conversation.storage_factory import get_conversation_storage
            _storage_factory_cache = get_conversation_storage
            STORAGE_FACTORY_AVAILABLE = True
            logger.info("[STORAGE_INTEGRATION] Storage factory available - will use configured backend")
        except ImportError as e:
            STORAGE_FACTORY_AVAILABLE = False
            logger.warning(f"[STORAGE_INTEGRATION] Storage factory not available: {e}")

    return _storage_factory_cache if STORAGE_FACTORY_AVAILABLE else None


def _get_storage_backend():
    """
    Get cached storage backend instance to avoid creating multiple instances.

    CRITICAL: This prevents creating 60+ storage instances per request!
    The storage factory was being created for EVERY get_thread() call,
    causing massive performance overhead and Supabase query spam.

    Returns:
        Cached storage backend instance or None if not available
    """
    global _storage_backend_instance

    if _storage_backend_instance is None:
        get_conversation_storage = _get_storage_factory()
        if get_conversation_storage:
            _storage_backend_instance = get_conversation_storage()
            logger.info("[STORAGE_INTEGRATION] Created cached storage backend instance")

    return _storage_backend_instance


# ================================================================================
# Thread Lifecycle Management
# ================================================================================


def create_thread(
    tool_name: str,
    initial_request: dict[str, Any],
    parent_thread_id: Optional[str] = None,
    session_fingerprint: Optional[str] = None,
    client_friendly_name: Optional[str] = None,
) -> str:
    """
    Create new conversation thread and return thread ID

    Initializes a new conversation thread for AI-to-AI discussions.
    This is called when a tool wants to enable follow-up conversations
    or when Claude explicitly starts a multi-turn interaction.

    Args:
        tool_name: Name of the tool creating this thread (e.g., "analyze", "chat")
        initial_request: Original request parameters (will be filtered for serialization)
        parent_thread_id: Optional parent thread ID for conversation chains
        session_fingerprint: Optional session fingerprint to scope this thread
        client_friendly_name: Optional friendly client label for logging/UX

    Returns:
        str: UUID thread identifier that can be used for continuation

    Note:
        - Thread expires after the configured timeout (default: 3 hours)
        - Non-serializable parameters are filtered out automatically
        - Thread can be continued by any tool using the returned UUID
        - Parent thread creates a chain for conversation history traversal
    """
    thread_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    # Filter out non-serializable parameters to avoid JSON encoding issues
    filtered_context = {
        k: v
        for k, v in initial_request.items()
        if k not in ["temperature", "thinking_mode", "model", "continuation_id"]
    }

    context = ThreadContext(
        thread_id=thread_id,
        parent_thread_id=parent_thread_id,  # Link to parent for conversation chains
        created_at=now,
        last_updated_at=now,
        tool_name=tool_name,  # Track which tool initiated this conversation
        turns=[],  # Empty initially, turns added via add_turn()
        initial_context=filtered_context,
        session_fingerprint=session_fingerprint,
        client_friendly_name=client_friendly_name,
    )

    # Store using configured storage backend (dual storage if CONVERSATION_STORAGE_BACKEND=dual)
    # Use CACHED instance to avoid creating multiple instances!
    storage_backend = _get_storage_backend()
    if storage_backend:
        try:
            # Use storage factory for Supabase integration
            logger.info(f"[STORAGE_INTEGRATION] Creating thread {thread_id} using storage factory")

            # Storage factory expects add_turn interface, so we'll use the old method for now
            # and add the thread creation to storage factory in next iteration
            # For now, use dual approach: Redis + storage factory
            storage = get_storage()
            key = f"thread:{thread_id}"
            storage.setex(key, CONVERSATION_TIMEOUT_SECONDS, context.model_dump_json())

            logger.debug(f"[THREAD] Created new thread {thread_id} with parent {parent_thread_id} (Redis)")
        except Exception as e:
            logger.error(f"[STORAGE_INTEGRATION] Failed to use storage factory: {e}, falling back to Redis")
            storage = get_storage()
            key = f"thread:{thread_id}"
            storage.setex(key, CONVERSATION_TIMEOUT_SECONDS, context.model_dump_json())
            logger.debug(f"[THREAD] Created new thread {thread_id} with parent {parent_thread_id} (Redis fallback)")
    else:
        # Fallback to original Redis storage
        storage = get_storage()
        key = f"thread:{thread_id}"
        storage.setex(key, CONVERSATION_TIMEOUT_SECONDS, context.model_dump_json())
        logger.debug(f"[THREAD] Created new thread {thread_id} with parent {parent_thread_id} (Redis only)")

    return thread_id


def get_thread(thread_id: str) -> Optional[ThreadContext]:
    """
    Retrieve thread context from configured storage backend

    Fetches complete conversation context for cross-tool continuation.
    This is the core function that enables tools to access conversation
    history from previous interactions.

    When CONVERSATION_STORAGE_BACKEND=dual, this will:
    1. Try to retrieve from Supabase first
    2. Fall back to Redis/in-memory if Supabase fails
    3. Enable conversation persistence across container restarts

    Args:
        thread_id: UUID of the conversation thread

    Returns:
        ThreadContext: Complete conversation context if found
        None: If thread doesn't exist, expired, or invalid UUID

    Security:
        - Validates UUID format to prevent injection attacks
        - Handles storage connection failures gracefully
        - No error information leakage on failure
    """
    if not thread_id or not _is_valid_uuid(thread_id):
        return None

    try:
        # Try storage factory first (Supabase integration)
        # Use CACHED instance to avoid creating 60+ instances per request!
        storage_backend = _get_storage_backend()
        if storage_backend:
            try:
                thread_data = storage_backend.get_thread(thread_id)

                if thread_data:
                    # Storage factory returns dict, convert to ThreadContext
                    if isinstance(thread_data, ThreadContext):
                        logger.debug(f"[STORAGE_INTEGRATION] Retrieved thread {thread_id} from storage factory (ThreadContext)")
                        return thread_data
                    elif isinstance(thread_data, dict):
                        logger.debug(f"[STORAGE_INTEGRATION] Retrieved thread {thread_id} from storage factory (dict)")
                        # For now, fall through to Redis since dict format needs conversion
                        # TODO: Implement dict to ThreadContext conversion
                    else:
                        logger.warning(f"[STORAGE_INTEGRATION] Unexpected thread data type: {type(thread_data)}")
            except Exception as e:
                logger.debug(f"[STORAGE_INTEGRATION] Storage factory failed: {e}, falling back to Redis")

        # Fallback to Redis storage (original behavior)
        storage = get_storage()
        key = f"thread:{thread_id}"
        data = storage.get(key)

        if data:
            logger.debug(f"[STORAGE_INTEGRATION] Retrieved thread {thread_id} from Redis")
            return ThreadContext.model_validate_json(data)
        return None
    except Exception as e:
        # Silently handle errors to avoid exposing storage details
        logger.debug(f"[STORAGE_INTEGRATION] Error retrieving thread {thread_id}: {e}")
        return None


def add_turn(
    thread_id: str,
    role: str,
    content: str,
    files: Optional[list[str]] = None,
    images: Optional[list[str]] = None,
    tool_name: Optional[str] = None,
    model_provider: Optional[str] = None,
    model_name: Optional[str] = None,
    model_metadata: Optional[dict[str, Any]] = None,
) -> bool:
    """
    Add turn to existing thread with atomic file ordering.

    Appends a new conversation turn to an existing thread. This is the core
    function for building conversation history and enabling cross-tool
    continuation. Each turn preserves the tool and model that generated it.

    Args:
        thread_id: UUID of the conversation thread
        role: "user" (from MCP client) or "assistant" (from AI model)
        content: The actual message/response content
        files: Optional list of files referenced in this turn
        images: Optional list of images referenced in this turn
        tool_name: Name of the tool adding this turn (for attribution)
        model_provider: Provider used (e.g., "glm", "kimi")
        model_name: Specific model used (e.g., "glm-4.6", "kimi-k2-0905-preview")
        model_metadata: Additional model info (e.g., thinking mode, token usage)

    Returns:
        bool: True if turn was successfully added, False otherwise

    Failure cases:
        - Thread doesn't exist or expired
        - Maximum turn limit reached
        - Storage connection failure

    Note:
        - Refreshes thread TTL to configured timeout on successful update
        - Turn limits prevent runaway conversations
        - File references are preserved for cross-tool access with atomic ordering
        - Image references are preserved for cross-tool visual context
        - Model information enables cross-provider conversations
    """
    logger.debug(f"[FLOW] Adding {role} turn to {thread_id} ({tool_name})")

    context = get_thread(thread_id)
    if not context:
        logger.debug(f"[FLOW] Thread {thread_id} not found for turn addition")
        return False

    # Check turn limit to prevent runaway conversations
    if len(context.turns) >= MAX_CONVERSATION_TURNS:
        logger.debug(f"[FLOW] Thread {thread_id} at max turns ({MAX_CONVERSATION_TURNS})")
        return False

    # Create new turn with complete metadata
    turn = ConversationTurn(
        role=role,
        content=content,
        timestamp=datetime.now(timezone.utc).isoformat(),
        files=files,  # Preserved for cross-tool file context
        images=images,  # Preserved for cross-tool visual context
        tool_name=tool_name,  # Track which tool generated this turn
        model_provider=model_provider,  # Track model provider
        model_name=model_name,  # Track specific model
        model_metadata=model_metadata,  # Additional model info
    )

    context.turns.append(turn)
    context.last_updated_at = datetime.now(timezone.utc).isoformat()

    # Save back to storage and refresh TTL
    # Use dual storage if available (Supabase + Redis)
    try:
        # Try storage factory first (Supabase integration)
        # Use CACHED instance to avoid creating multiple instances!
        storage_backend = _get_storage_backend()
        if storage_backend:
            try:
                success = storage_backend.add_turn(
                    thread_id,
                    role,
                    content,
                    files=files,
                    images=images,
                    metadata=model_metadata,
                    tool_name=tool_name
                )
                if success:
                    logger.debug(f"[STORAGE_INTEGRATION] Saved turn to storage factory for thread {thread_id}")
            except Exception as e:
                logger.debug(f"[STORAGE_INTEGRATION] Storage factory add_turn failed: {e}")

        # Always save to Redis (for backward compatibility and fallback)
        storage = get_storage()
        key = f"thread:{thread_id}"
        storage.setex(key, CONVERSATION_TIMEOUT_SECONDS, context.model_dump_json())  # Refresh TTL to configured timeout
        logger.debug(f"[STORAGE_INTEGRATION] Saved turn to Redis for thread {thread_id}")
        return True
    except Exception as e:
        logger.debug(f"[FLOW] Failed to save turn to storage: {type(e).__name__}")
        return False


def get_thread_chain(thread_id: str, max_depth: int = 20) -> list[ThreadContext]:
    """
    Traverse the parent chain to get all threads in conversation sequence.

    Retrieves the complete conversation chain by following parent_thread_id
    links. Returns threads in chronological order (oldest first).

    Args:
        thread_id: Starting thread ID
        max_depth: Maximum chain depth to prevent infinite loops

    Returns:
        list[ThreadContext]: All threads in chain, oldest first
    """
    chain = []
    current_id = thread_id
    seen_ids = set()

    # Build chain from current to oldest
    while current_id and len(chain) < max_depth:
        # Prevent circular references
        if current_id in seen_ids:
            logger.warning(f"[THREAD] Circular reference detected in thread chain at {current_id}")
            break

        seen_ids.add(current_id)

        context = get_thread(current_id)
        if not context:
            logger.debug(f"[THREAD] Thread {current_id} not found in chain traversal")
            break

        chain.append(context)
        current_id = context.parent_thread_id

    # Reverse to get chronological order (oldest first)
    chain.reverse()

    logger.debug(f"[THREAD] Retrieved chain of {len(chain)} threads for {thread_id}")
    return chain


# ================================================================================
# File and Image Collection (Newest-First Prioritization)
# ================================================================================


def get_conversation_file_list(context: ThreadContext) -> list[str]:
    """
    Extract all unique files from conversation turns with newest-first prioritization.

    This function implements the core file prioritization logic used throughout the
    conversation memory system. It walks backwards through conversation turns
    (from newest to oldest) and collects unique file references, ensuring that
    when the same file appears in multiple turns, the reference from the NEWEST
    turn takes precedence.

    PRIORITIZATION ALGORITHM:
    1. Iterate through turns in REVERSE order (index len-1 down to 0)
    2. For each turn, process files in the order they appear in turn.files
    3. Add file to result list only if not already seen (newest reference wins)
    4. Skip duplicate files that were already added from newer turns

    This ensures that:
    - Files from newer conversation turns appear first in the result
    - When the same file is referenced multiple times, only the newest reference is kept
    - The order reflects the most recent conversation context

    Example:
        Turn 1: files = ["main.py", "utils.py"]
        Turn 2: files = ["test.py"]
        Turn 3: files = ["main.py", "config.py"]  # main.py appears again

        Result: ["main.py", "config.py", "test.py", "utils.py"]
        (main.py from Turn 3 takes precedence over Turn 1)

    Args:
        context: ThreadContext containing all conversation turns to process

    Returns:
        list[str]: Unique file paths ordered by newest reference first.
                   Empty list if no turns exist or no files are referenced.

    Performance:
        - Time Complexity: O(n*m) where n=turns, m=avg files per turn
        - Space Complexity: O(f) where f=total unique files
        - Uses set for O(1) duplicate detection
    """
    if not context.turns:
        logger.debug("[FILES] No turns found, returning empty file list")
        return []

    # Collect files by walking backwards (newest to oldest turns)
    seen_files = set()
    file_list = []

    logger.debug(f"[FILES] Collecting files from {len(context.turns)} turns (newest first)")

    # Process turns in reverse order (newest first) - this is the CORE of newest-first prioritization
    # By iterating from len-1 down to 0, we encounter newer turns before older turns
    # When we find a duplicate file, we skip it because the newer version is already in our list
    for i in range(len(context.turns) - 1, -1, -1):  # REVERSE: newest turn first
        turn = context.turns[i]
        if turn.files:
            logger.debug(f"[FILES] Turn {i + 1} has {len(turn.files)} files: {turn.files}")
            for file_path in turn.files:
                if file_path not in seen_files:
                    # First time seeing this file - add it (this is the NEWEST reference)
                    seen_files.add(file_path)
                    file_list.append(file_path)
                    logger.debug(f"[FILES] Added new file: {file_path} (from turn {i + 1})")
                else:
                    # File already seen from a NEWER turn - skip this older reference
                    logger.debug(f"[FILES] Skipping duplicate file: {file_path} (newer version already included)")

    logger.debug(f"[FILES] Final file list ({len(file_list)}): {file_list}")
    return file_list


def get_conversation_image_list(context: ThreadContext) -> list[str]:
    """
    Extract all unique images from conversation turns with newest-first prioritization.

    This function implements the identical prioritization logic as get_conversation_file_list()
    to ensure consistency in how images are handled across conversation turns. It walks
    backwards through conversation turns (from newest to oldest) and collects unique image
    references, ensuring that when the same image appears in multiple turns, the reference
    from the NEWEST turn takes precedence.

    PRIORITIZATION ALGORITHM:
    1. Iterate through turns in REVERSE order (index len-1 down to 0)
    2. For each turn, process images in the order they appear in turn.images
    3. Add image to result list only if not already seen (newest reference wins)
    4. Skip duplicate images that were already added from newer turns

    This ensures that:
    - Images from newer conversation turns appear first in the result
    - When the same image is referenced multiple times, only the newest reference is kept
    - The order reflects the most recent conversation context

    Example:
        Turn 1: images = ["diagram.png", "flow.jpg"]
        Turn 2: images = ["error.png"]
        Turn 3: images = ["diagram.png", "updated.png"]  # diagram.png appears again

        Result: ["diagram.png", "updated.png", "error.png", "flow.jpg"]
        (diagram.png from Turn 3 takes precedence over Turn 1)

    Args:
        context: ThreadContext containing all conversation turns to process

    Returns:
        list[str]: Unique image paths ordered by newest reference first.
                   Empty list if no turns exist or no images are referenced.

    Performance:
        - Time Complexity: O(n*m) where n=turns, m=avg images per turn
        - Space Complexity: O(i) where i=total unique images
        - Uses set for O(1) duplicate detection
    """
    if not context.turns:
        logger.debug("[IMAGES] No turns found, returning empty image list")
        return []

    # Collect images by walking backwards (newest to oldest turns)
    seen_images = set()
    image_list = []

    logger.debug(f"[IMAGES] Collecting images from {len(context.turns)} turns (newest first)")

    # Process turns in reverse order (newest first) - this is the CORE of newest-first prioritization
    # By iterating from len-1 down to 0, we encounter newer turns before older turns
    # When we find a duplicate image, we skip it because the newer version is already in our list
    for i in range(len(context.turns) - 1, -1, -1):  # REVERSE: newest turn first
        turn = context.turns[i]
        if turn.images:
            logger.debug(f"[IMAGES] Turn {i + 1} has {len(turn.images)} images: {turn.images}")
            for image_path in turn.images:
                if image_path not in seen_images:
                    # First time seeing this image - add it (this is the NEWEST reference)
                    seen_images.add(image_path)
                    image_list.append(image_path)
                    logger.debug(f"[IMAGES] Added new image: {image_path} (from turn {i + 1})")
                else:
                    # Image already seen from a NEWER turn - skip this older reference
                    logger.debug(f"[IMAGES] Skipping duplicate image: {image_path} (newer version already included)")

    logger.debug(f"[IMAGES] Final image list ({len(image_list)}): {image_list}")
    return image_list

