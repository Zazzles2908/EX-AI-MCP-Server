"""
Supabase Conversation Memory

Provides persistent conversation storage using Supabase with fallback to in-memory storage.
Compatible with existing conversation memory interface for seamless integration.

PERFORMANCE FIX (2025-10-16): Added multi-layer caching to reduce Supabase HTTP calls
from 7 per request to 0 (cache hit) or 2 (cache miss).
Issue: 926e2c85-98d0-4163-a0c3-7299ee05416c

EMERGENCY HOTFIX (2025-10-19): Context pruning to fix 108K token issue
- Limit messages to 15 most recent (was unlimited)
- Remove file contents from messages older than 3 turns
- Add token counting and logging
Target: 90% token reduction (108K → <10K)
"""

import logging
import time
from typing import Optional, Dict, Any, List
from src.storage.supabase_client import get_storage_manager
from src.storage.conversation_mapper import get_conversation_mapper
from src.storage.file_handler import get_file_handler
from .cache_manager import get_cache_manager
from utils.performance.timing import timing_decorator, log_operation_time
from config import USE_ASYNC_SUPABASE

logger = logging.getLogger(__name__)

# EMERGENCY HOTFIX: Context pruning configuration
# BUG FIX #12 (2025-10-20): Aggressive pruning to fix context bloat issue
# EXAI Assessment (2025-10-20): Previous pruning too gentle (0.5% reduction)
# Target: 60-70% reduction with hard token limit of 4000 tokens
# External AI confirmed: Token growth pattern (1,279 → 29,818) indicates incomplete pruning
MAX_MESSAGES_TO_LOAD = 5  # Limit to 5 most recent messages (was 8, originally 15)
KEEP_FILE_CONTENT_TURNS = 1  # Keep file contents for 1 most recent turn only (was 2)
HARD_TOKEN_LIMIT = 4000  # Hard limit: prune aggressively if exceeded (EXAI recommendation)


class SupabaseConversationMemory:
    """
    Persistent conversation memory using Supabase.

    Features:
    - Conversation persistence
    - Message history storage
    - File upload integration
    - Fallback to in-memory storage
    - Compatible with existing memory interface
    """

    def __init__(self, fallback_to_memory: bool = True):
        """
        Initialize Supabase conversation memory

        Args:
            fallback_to_memory: Enable fallback to in-memory storage on errors
        """
        self.storage = get_storage_manager()
        self.mapper = get_conversation_mapper()
        self.file_handler = get_file_handler()
        self.fallback_to_memory = fallback_to_memory

        # PERFORMANCE FIX: Initialize cache manager
        self.cache = get_cache_manager()

        # BUG FIX #11 (2025-10-19): Add in-memory thread cache to eliminate redundant get_thread() calls
        # This prevents multiple get_thread() calls within the same request from hitting Supabase
        # Expected improvement: 0.905s → 0.3s (eliminates 3x redundant calls)
        # BUG FIX #13 (2025-10-20): This is a REQUEST-SCOPED cache that MUST be cleared after each request
        # Without clearing, it becomes a memory leak and serves stale data across requests
        self._thread_cache = {}
        self._request_cache_enabled = True  # Can be disabled for debugging

        # BUG FIX #11 (Phase 1b - 2025-10-20): Use async queue instead of ThreadPoolExecutor
        # When USE_ASYNC_SUPABASE=true, writes are submitted to async queue
        # This prevents blocking the response while saving to Supabase
        # Expected improvement: Eliminates write blocking (~0.13s per request) + avoids ThreadPoolExecutor resource exhaustion
        if USE_ASYNC_SUPABASE:
            self._write_executor = None  # Signal to use async queue
            self._use_async_queue = True
            logger.info("[ASYNC_SUPABASE] Will use async queue for writes")
        else:
            self._write_executor = None  # Synchronous writes
            self._use_async_queue = False
            logger.info("[ASYNC_SUPABASE] Synchronous writes enabled")

        # Import in-memory functions for fallback
        if fallback_to_memory:
            try:
                from .memory import get_thread as memory_get_thread
                from .memory import add_turn as memory_add_turn
                self._memory_get_thread = memory_get_thread
                self._memory_add_turn = memory_add_turn
            except ImportError:
                logger.warning("In-memory fallback not available")
                self.fallback_to_memory = False

    @timing_decorator("SupabaseMemory.get_thread")
    def get_thread(self, continuation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get conversation thread from Supabase with multi-layer caching

        PERFORMANCE FIX: Check L1/L2 cache before hitting Supabase
        TIMING INSTRUMENTATION (2025-10-19): Added timing to identify bottlenecks
        BUG FIX #11 (2025-10-19): Added in-memory thread cache to eliminate redundant calls

        Args:
            continuation_id: Unique conversation identifier

        Returns:
            Thread context dict or None if not found
        """
        if not self.storage.enabled:
            if self.fallback_to_memory:
                logger.debug("Supabase not enabled, using in-memory fallback")
                return self._memory_get_thread(continuation_id)
            return None

        try:
            # BUG FIX #11 & #13: Check in-memory thread cache first (L0 - request-level cache)
            # This eliminates redundant Supabase queries WITHIN a single request
            # Cache is cleared after each request completes (see request_handler.py)
            if self._request_cache_enabled and continuation_id in self._thread_cache:
                logger.info(f"[REQUEST_CACHE HIT] Thread {continuation_id} from request cache (0ms, no Supabase query)")
                return self._thread_cache[continuation_id]

            # PERFORMANCE FIX: Check cache first (L1 → L2)
            cached_conv = self.cache.get_conversation(continuation_id)
            cached_messages = self.cache.get_messages(continuation_id)

            if cached_conv and cached_messages is not None:
                # Cache hit - no Supabase calls needed!
                thread = {
                    'id': continuation_id,
                    'conversation_id': cached_conv['id'],
                    'messages': cached_messages,
                    'metadata': cached_conv.get('metadata', {}),
                    'storage': 'supabase',
                    'created_at': cached_conv.get('created_at'),
                    'updated_at': cached_conv.get('updated_at')
                }
                logger.debug(f"[CACHE HIT] Retrieved thread {continuation_id} from cache ({len(cached_messages)} messages)")

                # BUG FIX #11 & #13: Store in request cache for subsequent calls in same request
                if self._request_cache_enabled:
                    self._thread_cache[continuation_id] = thread
                    logger.debug(f"[REQUEST_CACHE STORE] Cached thread {continuation_id} for this request")

                return thread

            # Cache miss - load from Supabase (L3)
            logger.debug(f"[CACHE MISS] Loading thread {continuation_id} from Supabase")

            # Get conversation from Supabase (TIMED)
            start_time = time.time()
            conv = self.storage.get_conversation_by_continuation_id(continuation_id)
            log_operation_time("SupabaseMemory.get_conversation_by_continuation_id", start_time)

            if not conv:
                logger.debug(f"No conversation found for {continuation_id}")
                if self.fallback_to_memory:
                    return self._memory_get_thread(continuation_id)
                return None

            # EMERGENCY HOTFIX: Get messages with limit to prevent 108K token issue (TIMED)
            start_time = time.time()
            messages = self.storage.get_conversation_messages(conv['id'], limit=MAX_MESSAGES_TO_LOAD)
            log_operation_time("SupabaseMemory.get_conversation_messages", start_time)

            # Log message count for monitoring
            logger.info(f"[CONTEXT_PRUNING] Loaded {len(messages)} messages for {continuation_id} (limit={MAX_MESSAGES_TO_LOAD})")

            # PERFORMANCE FIX: Populate cache for next request
            self.cache.set_conversation(continuation_id, conv)
            self.cache.set_messages(continuation_id, messages)

            # Convert to thread format
            thread = {
                'id': continuation_id,
                'conversation_id': conv['id'],
                'messages': messages,
                'metadata': conv.get('metadata', {}),
                'storage': 'supabase',
                'created_at': conv.get('created_at'),
                'updated_at': conv.get('updated_at')
            }

            # BUG FIX #11 & #13: Store in request cache for subsequent calls in same request
            if self._request_cache_enabled:
                self._thread_cache[continuation_id] = thread
                logger.info(f"[REQUEST_CACHE STORE] Cached thread {continuation_id} for this request (loaded from Supabase)")

            logger.debug(f"Retrieved thread {continuation_id} with {len(messages)} messages (cached for next request)")
            return thread

        except Exception as e:
            logger.error(f"Error getting thread {continuation_id}: {e}")
            if self.fallback_to_memory:
                logger.debug("Falling back to in-memory storage")
                return self._memory_get_thread(continuation_id)
            return None

    def _write_message_background(
        self,
        continuation_id: str,
        role: str,
        content: str,
        files: Optional[List[str]],
        images: Optional[List[str]],
        metadata: Optional[Dict],
        tool_name: Optional[str]
    ):
        """
        Background thread for writing to Supabase (fire-and-forget pattern).

        BUG FIX #11 (2025-10-19): This method runs in a background thread to avoid
        blocking the response while saving to Supabase.

        Args:
            continuation_id: Unique conversation identifier
            role: Message role (user, assistant, system)
            content: Message content
            files: Optional list of file paths
            images: Optional list of image paths
            metadata: Optional metadata
            tool_name: Optional tool name
        """
        try:
            # Get or create conversation
            conv_id = self.mapper.get_or_create_conversation(
                continuation_id=continuation_id,
                title=f"Conversation {continuation_id[:8]}",
                metadata={'tool_name': tool_name} if tool_name else None
            )

            if not conv_id:
                logger.error(f"[BACKGROUND_WRITE] Failed to get/create conversation for {continuation_id}")
                return

            # Process files if provided
            file_ids = []
            all_files = (files or []) + (images or [])

            if all_files:
                processed_files = self.file_handler.process_files(
                    file_paths=all_files,
                    context_id=continuation_id,
                    upload_immediately=True
                )

                # Extract file IDs and link to conversation
                for file_info in processed_files:
                    file_id = file_info.get('file_id')
                    if file_id:
                        file_ids.append(file_id)
                        self.storage.link_file_to_conversation(conv_id, file_id)

            # Prepare message metadata
            msg_metadata = metadata or {}
            msg_metadata['file_ids'] = file_ids
            msg_metadata['tool_name'] = tool_name

            # Save message
            msg_id = self.storage.save_message(
                conversation_id=conv_id,
                role=role,
                content=content,
                metadata=msg_metadata
            )

            if msg_id:
                # Invalidate cache after write
                self.cache.invalidate(continuation_id)

                # Invalidate thread cache after write
                if continuation_id in self._thread_cache:
                    del self._thread_cache[continuation_id]

                logger.debug(f"[BACKGROUND_WRITE] Saved turn for {continuation_id}: {role} message")
            else:
                logger.error(f"[BACKGROUND_WRITE] Failed to save message for {continuation_id}")

        except Exception as e:
            logger.error(f"[BACKGROUND_WRITE] Error adding turn to {continuation_id}: {e}")

    @timing_decorator("SupabaseMemory.add_turn")
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
        Add a conversation turn to Supabase

        TIMING INSTRUMENTATION (2025-10-19): Added timing to identify bottlenecks
        BUG FIX #11 (2025-10-19): Added fire-and-forget pattern for async writes

        Args:
            continuation_id: Unique conversation identifier
            role: Message role (user, assistant, system)
            content: Message content
            files: Optional list of file paths
            images: Optional list of image paths
            metadata: Optional metadata
            tool_name: Optional tool name

        Returns:
            True if successful, False otherwise
        """
        if not self.storage.enabled:
            if self.fallback_to_memory:
                logger.debug("Supabase not enabled, using in-memory fallback")
                return self._memory_add_turn(
                    continuation_id, role, content, files, images, metadata, tool_name
                )
            return False

        # BUG FIX #11 (Phase 1b - 2025-10-20): If async writes are enabled, submit to async queue and return immediately
        # This prevents blocking the response while saving to Supabase
        # Expected improvement: Eliminates write blocking (~0.13s per request) + avoids ThreadPoolExecutor resource exhaustion
        if self._use_async_queue:
            logger.info(f"[ASYNC_SUPABASE] Submitting write to async queue for {continuation_id}")

            # Prepare the data for the queue
            update_data = {
                'role': role,
                'content': content,
                'files': files,
                'images': images,
                'metadata': metadata,
                'tool_name': tool_name
            }

            # Submit to queue without blocking (synchronous call to async queue)
            try:
                import time
                from src.daemon.conversation_queue import get_conversation_queue_sync, QueueItem

                # Create a queue item with timestamp
                item = QueueItem(
                    conversation_id=continuation_id,
                    update_data=update_data,
                    timestamp=time.time()
                )

                # Get the queue and submit the item (synchronous version)
                queue = get_conversation_queue_sync()
                if queue is None:
                    # Fallback to synchronous write if queue not available
                    logger.warning("[ASYNC_SUPABASE] Async queue not available, falling back to sync write")
                    # Continue to synchronous path below
                else:
                    queue.put_sync(item)
                    logger.info(f"[ASYNC_SUPABASE] Queued write for {continuation_id}")
                    # Return immediately without blocking
                    return True
            except Exception as e:
                logger.error(f"[ASYNC_SUPABASE] Error submitting to async queue: {e}, falling back to sync write")
                # Continue to synchronous path below

        # Synchronous path (original implementation)
        try:
            # Get or create conversation (TIMED)
            start_time = time.time()
            conv_id = self.mapper.get_or_create_conversation(
                continuation_id=continuation_id,
                title=f"Conversation {continuation_id[:8]}",
                metadata={'tool_name': tool_name} if tool_name else None
            )
            log_operation_time("SupabaseMemory.get_or_create_conversation", start_time)

            if not conv_id:
                logger.error(f"Failed to get/create conversation for {continuation_id}")
                if self.fallback_to_memory:
                    return self._memory_add_turn(
                        continuation_id, role, content, files, images, metadata, tool_name
                    )
                return False

            # Process files if provided
            file_ids = []
            all_files = (files or []) + (images or [])

            if all_files:
                start_time = time.time()
                processed_files = self.file_handler.process_files(
                    file_paths=all_files,
                    context_id=continuation_id,
                    upload_immediately=True
                )
                log_operation_time("SupabaseMemory.process_files", start_time)

                # Extract file IDs and link to conversation
                for file_info in processed_files:
                    file_id = file_info.get('file_id')
                    if file_id:
                        file_ids.append(file_id)
                        self.storage.link_file_to_conversation(conv_id, file_id)

            # Prepare message metadata
            msg_metadata = metadata or {}
            msg_metadata['file_ids'] = file_ids
            msg_metadata['tool_name'] = tool_name

            # Save message (TIMED)
            start_time = time.time()
            msg_id = self.storage.save_message(
                conversation_id=conv_id,
                role=role,
                content=content,
                metadata=msg_metadata
            )
            log_operation_time("SupabaseMemory.save_message", start_time)

            if msg_id:
                # PERFORMANCE FIX: Invalidate cache after write
                self.cache.invalidate(continuation_id)

                # BUG FIX #11: Invalidate thread cache after write to force reload on next get_thread()
                if continuation_id in self._thread_cache:
                    del self._thread_cache[continuation_id]

                logger.debug(f"Saved turn for {continuation_id}: {role} message (cache invalidated)")
                return True
            else:
                logger.error(f"Failed to save message for {continuation_id}")
                if self.fallback_to_memory:
                    return self._memory_add_turn(
                        continuation_id, role, content, files, images, metadata, tool_name
                    )
                return False

        except Exception as e:
            logger.error(f"Error adding turn to {continuation_id}: {e}")
            if self.fallback_to_memory:
                logger.debug("Falling back to in-memory storage")
                return self._memory_add_turn(
                    continuation_id, role, content, files, images, metadata, tool_name
                )
            return False

    # BUG FIX #14 (2025-10-20): DELETED build_conversation_history
    # Legacy text-based history building is no longer used.
    # Modern approach: Use get_messages_array() for SDK-native message format.
    # SDKs (Kimi/GLM) receive message arrays directly, not text strings.

    def clear_request_cache(self):
        """
        Clear the request-scoped thread cache.

        BUG FIX #13 (2025-10-20): This MUST be called after each request completes
        to prevent memory leaks and stale data being served across requests.

        The thread cache is designed to eliminate redundant Supabase queries WITHIN
        a single request, but it must be cleared BETWEEN requests.
        """
        if not self._request_cache_enabled:
            return

        cache_size = len(self._thread_cache)
        if cache_size > 0:
            logger.debug(f"[REQUEST_CACHE] Clearing {cache_size} cached threads")
            self._thread_cache.clear()
        else:
            logger.debug("[REQUEST_CACHE] No cached threads to clear")


# Global instance
_supabase_memory: Optional[SupabaseConversationMemory] = None


def get_supabase_memory(fallback_to_memory: bool = True) -> SupabaseConversationMemory:
    """Get global Supabase conversation memory instance"""
    global _supabase_memory
    if _supabase_memory is None:
        _supabase_memory = SupabaseConversationMemory(fallback_to_memory=fallback_to_memory)
    return _supabase_memory


# BUG FIX #11 (2025-10-20): Async queue processing function
async def process_conversation_update(queue_item):
    """
    Process a conversation update from the async queue.

    This function is called by the ConversationQueue consumer to process
    queued conversation updates. It replaces the ThreadPoolExecutor pattern.

    Args:
        queue_item: QueueItem with conversation_id and update_data
    """
    try:
        memory = get_supabase_memory()

        # Extract data from queue item
        continuation_id = queue_item.conversation_id
        data = queue_item.update_data

        # Call the background write function (synchronous)
        # This runs in the async event loop but the actual Supabase call is sync
        memory._write_message_background(
            continuation_id=continuation_id,
            role=data['role'],
            content=data['content'],
            files=data.get('files'),
            images=data.get('images'),
            metadata=data.get('metadata'),
            tool_name=data.get('tool_name')
        )

        logger.info(f"[CONV_QUEUE] Processed update for {continuation_id}")

    except Exception as e:
        logger.error(f"[CONV_QUEUE] Error processing conversation update: {e}", exc_info=True)
