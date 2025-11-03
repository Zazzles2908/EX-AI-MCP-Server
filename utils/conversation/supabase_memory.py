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
        # PHASE 2 FIX (2025-11-01): Removed request-scoped cache (L0)
        # Consolidating to 2 cache layers: Supabase (L3) + Redis (L2 via BaseCacheManager)
        # Request-scoped cache was causing complexity without significant performance benefit

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
            # PHASE 2 FIX (2025-11-01): Removed request-scoped cache
            # Now using only L2 (Redis via BaseCacheManager) → L3 (Supabase)
            # PERFORMANCE FIX: Check cache first (L2 → L3)
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

                # PHASE 1 FIX (2025-11-01): Batch link files to reduce HTTP calls
                for file_info in processed_files:
                    file_id = file_info.get('file_id')
                    if file_id:
                        file_ids.append(file_id)

                # Batch link all files at once
                if file_ids:
                    self.storage.link_files_to_conversation_batch(conv_id, file_ids)

            # Prepare message metadata
            msg_metadata = metadata or {}
            msg_metadata['file_ids'] = file_ids
            msg_metadata['tool_name'] = tool_name

            # Save message with timestamp for unique idempotency key
            # CRITICAL FIX (2025-10-23): Include microsecond-precision timestamp
            # to ensure each message gets a unique idempotency key, preventing
            # race conditions where duplicate messages are created simultaneously
            #
            # ARCHITECTURAL FIX (2025-10-23): Use guaranteed microsecond precision
            # and rely entirely on database constraints for duplicate prevention
            from datetime import datetime
            client_timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')

            msg_id = self.storage.save_message(
                conversation_id=conv_id,
                role=role,
                content=content,
                metadata=msg_metadata,
                client_timestamp=client_timestamp
            )

            if msg_id:
                # Invalidate cache after write
                self.cache.invalidate(continuation_id)
                logger.debug(f"[BACKGROUND_WRITE] Saved turn for {continuation_id}: {role} message")
            else:
                logger.error(f"[BACKGROUND_WRITE] Failed to save message for {continuation_id}")

        except Exception as e:
            logger.error(f"[BACKGROUND_WRITE] Error adding turn to {continuation_id}: {e}")

    def _is_duplicate_message(self, conversation_id: str, content: str, role: str, limit: int = 10) -> bool:
        # CRITICAL FIX (2025-11-02): Only check for duplicates on assistant messages, never user messages
        # User messages were being incorrectly flagged as duplicates, causing message imbalance in Supabase
        if role != 'assistant':
            return False
        """
        Check if this message was recently saved to prevent duplicates.

        CRITICAL FIX (2025-10-23): Prevents duplicate messages caused by race conditions
        during slow API responses (9+ minute Kimi responses triggering retries).

        BUG FIX (2025-10-23): Fixed incorrect method call - use get_or_create_conversation()
        instead of non-existent get_conversation_id() method.

        Args:
            conversation_id: Conversation identifier (continuation_id)
            content: Message content to check
            role: Message role (user, assistant, system)
            limit: Number of recent messages to check (default: 10)

        Returns:
            True if duplicate found, False otherwise
        """
        try:
            # Get the database conversation UUID from the continuation_id
            # BUG FIX: Use get_or_create_conversation() instead of get_conversation_id()
            conv_id = self.mapper.get_or_create_conversation(conversation_id)
            if not conv_id:
                logger.debug(f"[DEDUP] No conversation found for {conversation_id[:8]}")
                return False

            # Get recent messages using the correct method name
            # BUG FIX: Use get_conversation_messages() instead of get_messages()
            recent_messages = self.storage.get_conversation_messages(conv_id, limit=limit)
            if not recent_messages:
                logger.debug(f"[DEDUP] No recent messages found for {conversation_id[:8]}")
                return False

            # Check for exact content match within last 60 seconds
            from datetime import datetime, timezone
            now = datetime.now(timezone.utc)

            for msg in recent_messages:
                if msg.get('role') == role and msg.get('content') == content:
                    # Check timestamp - only consider duplicates within 60 seconds
                    created_at = msg.get('created_at')
                    if created_at:
                        if isinstance(created_at, str):
                            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))

                        time_diff = (now - created_at).total_seconds()
                        if time_diff < 60:
                            logger.warning(f"[DEDUP] Found duplicate message from {time_diff:.1f}s ago in {conversation_id[:8]}")
                            return True

            logger.debug(f"[DEDUP] No duplicates found for {role} message in {conversation_id[:8]}")
            return False

        except Exception as e:
            logger.error(f"[DEDUP] Error checking for duplicates: {e}", exc_info=True)
            # On error, allow the message through (fail open)
            return False

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

        # CRITICAL FIX (2025-10-23): Prevent duplicate messages from race conditions
        # Check if this exact message was recently saved (within last 60 seconds)
        # This prevents duplicates caused by slow responses triggering retries
        if self._is_duplicate_message(continuation_id, content, role):
            logger.warning(f"[DEDUP] Preventing duplicate message: {role} in {continuation_id[:8]}")
            return True

        # PHASE 1 (2025-10-24): Standardize metadata before storage
        # Extract and standardize metadata fields to match Supabase schema
        # DEBUG: Log incoming metadata
        logger.info(f"[PHASE1_DEBUG] add_turn called with metadata={metadata}, type={type(metadata)}")

        storage_metadata = {}
        if metadata:
            if isinstance(metadata, dict):
                # Direct field mapping
                if 'model_used' in metadata:
                    storage_metadata['model_used'] = metadata['model_used']
                if 'provider_used' in metadata:
                    storage_metadata['provider_used'] = metadata['provider_used']
                if 'response_time_ms' in metadata:
                    storage_metadata['response_time_ms'] = metadata['response_time_ms']
                if 'token_usage' in metadata:
                    storage_metadata['token_usage'] = metadata['token_usage']
                if 'thinking_mode' in metadata:
                    storage_metadata['thinking_mode'] = metadata['thinking_mode']
                # Preserve full metadata for backward compatibility
                storage_metadata['model_metadata'] = metadata

        # PHASE 1 DEBUG (2025-10-24): Log metadata being passed to storage
        logger.info(f"[PHASE1_METADATA] continuation_id={continuation_id}, storage_metadata={storage_metadata}")

        # BUG FIX #11 (Phase 1b - 2025-10-20): If async writes are enabled, submit to async queue and return immediately
        # This prevents blocking the response while saving to Supabase
        # Expected improvement: Eliminates write blocking (~0.13s per request) + avoids ThreadPoolExecutor resource exhaustion
        if self._use_async_queue:
            logger.info(f"[ASYNC_SUPABASE] Submitting write to async queue for {continuation_id}")

            # Prepare the data for the queue (use standardized metadata)
            update_data = {
                'role': role,
                'content': content,
                'files': files,
                'images': images,
                'metadata': storage_metadata,  # Use standardized metadata
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

                # PHASE 1 FIX (2025-11-01): Batch link files to reduce HTTP calls
                for file_info in processed_files:
                    file_id = file_info.get('file_id')
                    if file_id:
                        file_ids.append(file_id)

                # Batch link all files at once
                if file_ids:
                    self.storage.link_files_to_conversation_batch(conv_id, file_ids)

            # Prepare message metadata (use standardized metadata from Phase 1)
            msg_metadata = storage_metadata or {}
            msg_metadata['file_ids'] = file_ids
            msg_metadata['tool_name'] = tool_name

            # Save message (TIMED)
            # CRITICAL FIX (2025-10-23): Include microsecond-precision timestamp
            # to ensure each message gets a unique idempotency key, preventing
            # race conditions where duplicate messages are created simultaneously
            #
            # ARCHITECTURAL FIX (2025-10-23): Use guaranteed microsecond precision
            # and rely entirely on database constraints for duplicate prevention
            from datetime import datetime
            client_timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')

            start_time = time.time()
            msg_id = self.storage.save_message(
                conversation_id=conv_id,
                role=role,
                content=content,
                metadata=msg_metadata,
                client_timestamp=client_timestamp
            )
            log_operation_time("SupabaseMemory.save_message", start_time)

            if msg_id:
                # PERFORMANCE FIX: Invalidate cache after write
                self.cache.invalidate(continuation_id)
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

    # PHASE 2 FIX (2025-11-01): Removed clear_request_cache() method
    # Request-scoped cache has been eliminated as part of cache layer reduction


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
