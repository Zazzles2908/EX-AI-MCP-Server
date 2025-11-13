"""
Async Conversation Queue

BUG FIX #11 (2025-10-20): Replace ThreadPoolExecutor with async queue pattern
Based on EXAI guidance from Phase 1 implementation plan.

This module provides an async queue for fire-and-forget conversation updates
to Supabase, replacing the ThreadPoolExecutor pattern which can cause resource
exhaustion.

Benefits:
- Lightweight coroutines instead of threads
- Natural backpressure when queue fills
- Better monitoring and control
- No thread context switching overhead

Expected improvements:
- Reduced memory usage (no thread stacks)
- Better handling of high-throughput scenarios
- Clearer queue depth monitoring
"""

import asyncio
import logging
from typing import Callable, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class QueueItem:
    """Item to be processed by the queue."""
    conversation_id: str
    update_data: dict
    timestamp: float


class ConversationQueue:
    """
    Async queue for conversation updates with bounded size and backpressure.
    
    Features:
    - Bounded queue with configurable max size
    - Dedicated consumer task for processing
    - Queue depth monitoring
    - Graceful shutdown handling
    - Error handling with logging
    """
    
    def __init__(
        self,
        max_size: int = 1000,
        consumer_func: Optional[Callable] = None,
        warning_threshold: int = 500
    ):
        """
        Initialize conversation queue.
        
        Args:
            max_size: Maximum queue size (default 1000)
            consumer_func: Async function to process queue items
            warning_threshold: Log warning when queue exceeds this size
        """
        self.queue = asyncio.Queue(maxsize=max_size)
        self.consumer_func = consumer_func
        self.consumer_task = None
        self.running = False
        self.warning_threshold = warning_threshold
        self.max_size = max_size
        
        # Metrics
        self.total_processed = 0
        self.total_errors = 0
        self.total_dropped = 0
        
    async def start(self):
        """Start the consumer task."""
        if self.running:
            logger.warning("[CONV_QUEUE] Consumer already running")
            return
            
        self.running = True
        self.consumer_task = asyncio.create_task(self._consume())
        logger.info(f"[CONV_QUEUE] Consumer started (max_size={self.max_size}, warning_threshold={self.warning_threshold})")
        
    async def stop(self):
        """Stop the consumer task gracefully."""
        logger.info("[CONV_QUEUE] Stopping consumer...")
        self.running = False
        
        if self.consumer_task:
            self.consumer_task.cancel()
            try:
                await self.consumer_task
            except asyncio.CancelledError:
                pass
                
        # Log final metrics
        logger.info(
            f"[CONV_QUEUE] Consumer stopped | "
            f"Processed: {self.total_processed}, "
            f"Errors: {self.total_errors}, "
            f"Dropped: {self.total_dropped}"
        )
        
    async def _consume(self):
        """Consume items from the queue."""
        logger.info("[CONV_QUEUE] Consumer loop started")
        
        while self.running:
            try:
                # Get item from queue with timeout to allow checking running flag
                item = await asyncio.wait_for(self.queue.get(), timeout=1.0)
                
                try:
                    # Process the item
                    await self.consumer_func(item)
                    self.total_processed += 1
                    
                except Exception as e:
                    self.total_errors += 1
                    logger.error(f"[CONV_QUEUE] Error processing item: {e}", exc_info=True)
                    
                finally:
                    self.queue.task_done()
                    
            except asyncio.TimeoutError:
                # Timeout is expected, just continue the loop
                continue
            except Exception as e:
                logger.error(f"[CONV_QUEUE] Unexpected error in consumer loop: {e}", exc_info=True)
                
        logger.info("[CONV_QUEUE] Consumer loop exited")
        
    async def put(self, item: QueueItem):
        """
        Add an item to the queue.
        
        Args:
            item: QueueItem to process
            
        Note:
            If queue is full, item will be dropped and logged
        """
        try:
            # Try to put without blocking
            self.queue.put_nowait(item)
            
            # Check if we should warn about queue depth
            current_size = self.queue.qsize()
            if current_size > self.warning_threshold:
                logger.warning(
                    f"[CONV_QUEUE] Queue depth high: {current_size}/{self.max_size} "
                    f"({current_size/self.max_size*100:.1f}%)"
                )
                
        except asyncio.QueueFull:
            self.total_dropped += 1
            logger.error(
                f"[CONV_QUEUE] Queue full ({self.max_size}), dropping item for conversation {item.conversation_id} | "
                f"Total dropped: {self.total_dropped}"
            )
            # Alternative strategies could be implemented here:
            # 1. Block until space is available: await self.queue.put(item)
            # 2. Drop oldest item and add new one
            # 3. Store to disk as fallback

    def put_sync(self, item: QueueItem):
        """
        Add an item to the queue (synchronous version for use from sync code).

        BUG FIX #11 (Phase 1b): Allows synchronous code to submit to async queue
        without requiring an event loop.

        Args:
            item: QueueItem to process

        Note:
            If queue is full, item will be dropped and logged
        """
        try:
            # Try to put without blocking
            self.queue.put_nowait(item)

            # Check if we should warn about queue depth
            current_size = self.queue.qsize()
            if current_size > self.warning_threshold:
                logger.warning(
                    f"[CONV_QUEUE] Queue depth high: {current_size}/{self.max_size} "
                    f"({current_size/self.max_size*100:.1f}%)"
                )

        except asyncio.QueueFull:
            self.total_dropped += 1
            logger.error(
                f"[CONV_QUEUE] Queue full ({self.max_size}), dropping item for conversation {item.conversation_id} | "
                f"Total dropped: {self.total_dropped}"
            )

    def size(self) -> int:
        """Get current queue size."""
        return self.queue.qsize()
        
    def get_metrics(self) -> dict:
        """
        Get queue metrics.
        
        Returns:
            Dictionary with queue metrics
        """
        return {
            "queue_size": self.queue.qsize(),
            "max_size": self.max_size,
            "utilization": self.queue.qsize() / self.max_size * 100,
            "total_processed": self.total_processed,
            "total_errors": self.total_errors,
            "total_dropped": self.total_dropped,
            "running": self.running
        }


# Global queue instance
_conversation_queue: Optional[ConversationQueue] = None


async def get_conversation_queue() -> ConversationQueue:
    """
    Get or create the global conversation queue.
    
    Returns:
        ConversationQueue instance
    """
    global _conversation_queue
    
    if _conversation_queue is None:
        try:
            # Import here to avoid circular dependency
            from config import CONVERSATION_QUEUE_SIZE, CONVERSATION_QUEUE_WARNING_THRESHOLD
            from utils.conversation.supabase_memory import process_conversation_update

            _conversation_queue = ConversationQueue(
                max_size=CONVERSATION_QUEUE_SIZE,
                consumer_func=process_conversation_update,
                warning_threshold=CONVERSATION_QUEUE_WARNING_THRESHOLD
            )
            await _conversation_queue.start()
            logger.info("[CONV_QUEUE] Global queue initialized")
        except Exception as e:
            logger.warning(f"[CONV_QUEUE] Failed to initialize conversation queue: {e}. Daemon will continue without it.")
            # Return a minimal no-op queue
            _conversation_queue = None
        
    return _conversation_queue


def get_conversation_queue_sync() -> Optional[ConversationQueue]:
    """
    Get the global conversation queue (synchronous version).

    BUG FIX #11 (Phase 1b): Allows synchronous code to access the queue
    without requiring async/await.

    Returns:
        ConversationQueue instance if initialized, None otherwise

    Note:
        This function does NOT create the queue if it doesn't exist.
        The queue must be initialized during server startup via get_conversation_queue().
    """
    global _conversation_queue
    return _conversation_queue


async def shutdown_conversation_queue():
    """Shutdown the global conversation queue."""
    global _conversation_queue

    if _conversation_queue:
        await _conversation_queue.stop()
        _conversation_queue = None

