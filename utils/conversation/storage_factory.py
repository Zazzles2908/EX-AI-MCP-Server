"""
Conversation Storage Factory

Provides factory function to get appropriate conversation storage backend.
Supports in-memory, Supabase, and dual storage modes with configuration.

CRITICAL FIX (2025-10-16): Implemented singleton pattern to prevent lazy initialization
on every call. Storage is now initialized ONCE at startup and reused across all calls.

CONTEXT ENGINEERING (Phase 1 - 2025-10-19): Added history stripping to DualStorageConversation
to ensure consistent behavior across all storage backends.
"""

import os
import logging
import threading
from typing import Literal, Optional, Dict, Any, List

# Context Engineering imports
from utils.conversation.history_detection import HistoryDetector, DetectionMode
from utils.conversation.token_utils import TokenCounter
from config import CONTEXT_ENGINEERING

logger = logging.getLogger(__name__)

# Global singleton instance and lock for thread-safe initialization
_storage_instance = None
_storage_lock = threading.Lock()


def get_conversation_storage(
    backend: Optional[Literal["memory", "supabase", "dual"]] = None,
    fallback: bool = True,
    force_new: bool = False
):
    """
    Factory function to get appropriate conversation storage (SINGLETON PATTERN)

    CRITICAL FIX (2025-10-16): This now returns a SINGLETON instance to prevent
    lazy initialization on every call. Storage is initialized ONCE and reused.

    Args:
        backend: Storage backend type (memory, supabase, dual)
                If None, reads from CONVERSATION_STORAGE_BACKEND env var
        fallback: Enable fallback to in-memory storage on errors
        force_new: Force creation of new instance (for testing only)

    Returns:
        Conversation storage instance (singleton)
    """
    global _storage_instance

    # Return existing instance unless force_new is True
    if _storage_instance is not None and not force_new:
        return _storage_instance

    # Thread-safe initialization
    with _storage_lock:
        # Double-check pattern
        if _storage_instance is not None and not force_new:
            return _storage_instance

        if backend is None:
            backend = os.getenv("CONVERSATION_STORAGE_BACKEND", "memory")

        # DEBUG: Log storage backend selection
        logger.info(f"[STORAGE_FACTORY] Creating conversation storage: backend={backend}, fallback={fallback}")

        if backend == "memory":
            from .memory import InMemoryConversation
            _storage_instance = InMemoryConversation()

        elif backend == "supabase":
            from .supabase_memory import get_supabase_memory
            _storage_instance = get_supabase_memory(fallback_to_memory=fallback)

        elif backend == "dual":
            _storage_instance = DualStorageConversation(fallback=fallback)

        else:
            logger.warning(f"Unknown backend '{backend}', defaulting to memory")
            from .memory import InMemoryConversation
            _storage_instance = InMemoryConversation()

        logger.info(f"[STORAGE_FACTORY] Singleton storage instance created: {type(_storage_instance).__name__}")
        return _storage_instance


class DualStorageConversation:
    """
    Dual storage: Write to both Supabase and in-memory, read from Supabase with fallback.
    
    This provides the safest migration path:
    - All conversations are persisted to Supabase
    - In-memory storage provides immediate fallback
    - Gradual migration without downtime
    """
    
    def __init__(self, fallback: bool = True):
        """
        Initialize dual storage with context engineering

        Args:
            fallback: Enable fallback to in-memory on Supabase errors
        """
        from .supabase_memory import get_supabase_memory
        from .memory import InMemoryConversation

        self.supabase = get_supabase_memory(fallback_to_memory=False)
        self.memory = InMemoryConversation()
        self.fallback = fallback

        # Initialize context engineering components
        self.config = CONTEXT_ENGINEERING
        self.strip_history = self.config.get("strip_embedded_history", True)

        # Initialize history detector with configured mode
        detection_mode = self.config.get("detection_mode", "conservative")
        mode = DetectionMode.AGGRESSIVE if detection_mode == "aggressive" else DetectionMode.CONSERVATIVE
        self.history_detector = HistoryDetector(mode)

        # Initialize token counter for logging
        self.token_counter = TokenCounter()

        logger.info("Initialized dual storage (Supabase + in-memory) with context engineering")
    
    def get_thread(self, continuation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get thread from Supabase with fallback to in-memory
        
        Args:
            continuation_id: Unique conversation identifier
        
        Returns:
            Thread context dict or None
        """
        # Try Supabase first
        try:
            thread = self.supabase.get_thread(continuation_id)
            if thread:
                logger.debug(f"Retrieved thread {continuation_id} from Supabase")
                return thread
        except Exception as e:
            logger.warning(f"Supabase get_thread failed: {e}")
        
        # Fallback to in-memory
        if self.fallback:
            logger.debug(f"Falling back to in-memory for thread {continuation_id}")
            return self.memory.get_thread(continuation_id)
        
        return None
    
    def add_turn(
        self,
        continuation_id: str,
        role: str,
        content: str,
        files: Optional[List[str]] = None,
        images: Optional[List[str]] = None,
        metadata: Optional[Dict] = None,
        tool_name: Optional[str] = None
    ) -> bool:
        """
        Add turn to both Supabase and in-memory storage with history stripping.

        Implements Context Engineering Phase 1: Defense-in-depth history stripping
        to prevent recursive embedding of conversation history.

        Args:
            continuation_id: Unique conversation identifier
            role: Message role (user, assistant, system)
            content: Message content
            files: Optional list of file paths
            images: Optional list of image paths
            metadata: Optional metadata
            tool_name: Optional tool name

        Returns:
            True if at least one storage succeeded
        """
        # Apply context engineering: Strip embedded history BEFORE storage
        original_content = content
        if self.strip_history and role == "user":
            content = self._strip_embedded_history(content)

            # Log stripping if content changed
            if content != original_content and self.config.get("log_stripping", True):
                tokens_before = self.token_counter.count_tokens(original_content)
                tokens_after = self.token_counter.count_tokens(content)
                reduction = ((tokens_before - tokens_after) / tokens_before * 100) if tokens_before > 0 else 0
                logger.info(
                    f"[DUAL_STORAGE] History stripped: {tokens_before} → {tokens_after} tokens "
                    f"({reduction:.1f}% reduction)"
                )

            # In dry run mode, don't actually save the stripped content
            if self.config.get("dry_run", False):
                logger.info("[DUAL_STORAGE] DRY RUN: Would have stripped history from turn")
                content = original_content  # Restore original for dry run

        supabase_success = False
        memory_success = False

        # Try Supabase (with cleaned content)
        try:
            supabase_success = self.supabase.add_turn(
                continuation_id, role, content, files, images, metadata, tool_name
            )
            if supabase_success:
                logger.debug(f"Saved turn to Supabase: {continuation_id}")
        except Exception as e:
            logger.warning(f"Supabase add_turn failed: {e}")

        # Always write to in-memory (for fallback, with cleaned content)
        try:
            memory_success = self.memory.add_turn(
                continuation_id, role, content, files, images, metadata, tool_name
            )
            if memory_success:
                logger.debug(f"Saved turn to in-memory: {continuation_id}")
        except Exception as e:
            logger.warning(f"In-memory add_turn failed: {e}")

        # Success if either succeeded
        success = supabase_success or memory_success
        
        if not success:
            logger.error(f"Failed to save turn to both storages: {continuation_id}")

        return success

    def _strip_embedded_history(self, content: str) -> str:
        """
        Strip embedded history from content using defense-in-depth approach.

        This method implements Context Engineering Phase 1 to prevent recursive
        embedding of conversation history that causes token explosion.

        Args:
            content: Content to strip history from

        Returns:
            Content with history sections removed
        """
        if not content:
            return content

        # Check token threshold - only strip if content exceeds minimum
        min_threshold = self.config.get("min_token_threshold", 100)
        token_count = self.token_counter.count_tokens(content)
        if token_count < min_threshold:
            return content

        try:
            # Detect history sections
            sections = self.history_detector.extract_history_sections(content)
            if not sections:
                return content

            # Remove history sections
            clean_parts = []
            last_end = 0

            for start, end in sections:
                # Add content before this history section
                clean_parts.append(content[last_end:start])
                last_end = end

            # Add remaining content after last history section
            clean_parts.append(content[last_end:])

            clean_content = "".join(clean_parts)

            # Recursively check for nested history
            # This ensures we get all levels of embedded history
            if self.history_detector.has_embedded_history(clean_content):
                return self._strip_embedded_history(clean_content)

            return clean_content

        except Exception as e:
            logger.error(f"History stripping failed: {e}")
            # Return original content if stripping fails (graceful degradation)
            return content

    # BUG FIX #14 (2025-10-20): DELETED build_conversation_history
    # Legacy text-based history building is no longer used.
    # Modern approach: Use get_messages_array() for SDK-native message format.

    # PHASE 2 FIX (2025-11-01): Removed clear_request_cache() method
    # Request-scoped cache has been eliminated as part of cache layer reduction


# ============================================================================
# Startup Initialization
# ============================================================================

def initialize_conversation_storage(
    backend: Optional[Literal["memory", "supabase", "dual"]] = None,
    fallback: bool = True
) -> None:
    """
    Initialize conversation storage at startup (EAGER INITIALIZATION)

    CRITICAL FIX (2025-10-16): Call this at daemon startup to initialize
    storage ONCE instead of lazy initialization on every call.

    This prevents:
    - 300-700ms latency on every call
    - Multiple Supabase/Redis connections
    - Repeated HTTP calls to Supabase

    Args:
        backend: Storage backend type (memory, supabase, dual)
        fallback: Enable fallback to in-memory storage on errors
    """
    logger.info("[STORAGE_FACTORY] Initializing conversation storage at startup...")
    storage = get_conversation_storage(backend=backend, fallback=fallback)
    logger.info(f"[STORAGE_FACTORY] Startup initialization complete: {type(storage).__name__}")


# ============================================================================
# Convenience functions for backward compatibility
# ============================================================================

def get_thread(continuation_id: str) -> Optional[Dict[str, Any]]:
    """Get thread using configured storage backend"""
    storage = get_conversation_storage()
    return storage.get_thread(continuation_id)


def add_turn(
    continuation_id: str,
    role: str,
    content: str,
    files: Optional[List[str]] = None,
    images: Optional[List[str]] = None,
    metadata: Optional[Dict] = None,
    tool_name: Optional[str] = None
) -> bool:
    """Add turn using configured storage backend"""
    storage = get_conversation_storage()
    return storage.add_turn(
        continuation_id, role, content, files, images, metadata, tool_name
    )


# BUG FIX #14 (2025-10-20): DELETED build_conversation_history
# Legacy text-based history building is no longer used.
# Modern approach: Use get_messages_array() for SDK-native message format.

