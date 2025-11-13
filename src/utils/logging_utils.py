"""
Advanced Logging Utilities for EXAI-MCP-Server

Provides async logging, sampling, and performance-optimized logging patterns.

Created: 2025-10-28
EXAI Consultation: 7e59bfd7-a9cc-4a19-9807-5ebd84082cab
Phase 2: Advanced Logging Optimization
"""

import asyncio
import logging
import time
from functools import wraps
from typing import Callable, Any, Optional, Literal
from collections import deque, OrderedDict
import threading
from queue import Queue, Full, Empty
import os


class AsyncLogHandler(logging.Handler):
    """
    Async logging handler that processes logs in a background thread.

    This prevents logging from blocking the main event loop, which is critical
    for high-frequency operations in async WebSocket systems.

    Features:
    - Queue-based log processing
    - Configurable queue size and overflow behavior
    - Backpressure mechanism with multiple strategies
    - Thread-safe operation
    - Performance monitoring

    PHASE 2 FIX (2025-10-28): Added backpressure mechanism per EXAI QA review
    EXAI Consultation: 7e59bfd7-a9cc-4a19-9807-5ebd84082cab

    Usage:
        handler = AsyncLogHandler(
            max_queue_size=1000,
            overflow_strategy='drop_oldest'
        )
        logger = logging.getLogger(__name__)
        logger.addHandler(handler)
    """

    def __init__(
        self,
        max_queue_size: int = 1000,
        target_handler: Optional[logging.Handler] = None,
        overflow_strategy: Literal['drop_oldest', 'drop_newest', 'block'] = 'drop_oldest',
        block_timeout: float = 0.1
    ):
        """
        Initialize async log handler.

        Args:
            max_queue_size: Maximum number of logs to queue before applying overflow strategy
            target_handler: Handler to forward logs to (defaults to StreamHandler)
            overflow_strategy: How to handle queue overflow:
                - 'drop_oldest': Remove oldest log to make room (FIFO)
                - 'drop_newest': Drop the new log (preserve history)
                - 'block': Block briefly with timeout (may impact performance)
            block_timeout: Timeout in seconds when using 'block' strategy (default: 0.1s)
        """
        super().__init__()
        self.log_queue = Queue(maxsize=max_queue_size)
        self.target_handler = target_handler or logging.StreamHandler()
        self.overflow_strategy = overflow_strategy
        self.block_timeout = block_timeout
        self.worker_thread = threading.Thread(target=self._process_logs, daemon=True, name="AsyncLogWorker")
        self.worker_thread.start()
        self._dropped_count = 0
        self._processed_count = 0
        self._blocked_count = 0
    
    def _process_logs(self):
        """Background thread that processes queued log records."""
        while True:
            try:
                log_record = self.log_queue.get(timeout=1)
                if log_record:
                    self.target_handler.emit(log_record)
                    self._processed_count += 1
                self.log_queue.task_done()
            except Empty:
                continue
            except Exception as e:
                # Avoid infinite loop if target handler fails
                logger.info(f"AsyncLogHandler error: {e}")
    
    def emit(self, record: logging.LogRecord):
        """
        Queue a log record for async processing.

        Applies overflow strategy if queue is full:
        - drop_oldest: Remove oldest log to make room
        - drop_newest: Drop this log (preserve history)
        - block: Block briefly with timeout
        """
        try:
            self.log_queue.put_nowait(record)
        except Full:
            # Apply overflow strategy
            if self.overflow_strategy == 'drop_oldest':
                # Remove oldest log to make room for new one
                try:
                    self.log_queue.get_nowait()
                    self._dropped_count += 1
                    self.log_queue.put_nowait(record)
                except (Empty, Full):
                    # Race condition - queue state changed
                    self._dropped_count += 1
            elif self.overflow_strategy == 'drop_newest':
                # Drop the new log (preserve history)
                self._dropped_count += 1
            elif self.overflow_strategy == 'block':
                # Block briefly with timeout
                try:
                    self.log_queue.put(record, timeout=self.block_timeout)
                    self._blocked_count += 1
                except Full:
                    # Still full after timeout - drop it
                    self._dropped_count += 1

            # Only log drops occasionally to avoid spam
            if self._dropped_count % 100 == 0:
                logger.info(f"AsyncLogHandler: Dropped {self._dropped_count} logs (strategy={self.overflow_strategy})")
    
    def get_stats(self) -> dict:
        """Get handler statistics."""
        queue_size = self.log_queue.qsize()
        queue_max = self.log_queue.maxsize
        return {
            "processed": self._processed_count,
            "dropped": self._dropped_count,
            "blocked": self._blocked_count,
            "queue_size": queue_size,
            "queue_max": queue_max,
            "overflow_strategy": self.overflow_strategy,
            "utilization_percent": (queue_size / queue_max * 100) if queue_max > 0 else 0,
            "drop_rate": (self._dropped_count / max(self._processed_count, 1) * 100)
        }

    def reset_stats(self):
        """Reset statistics counters."""
        self._dropped_count = 0
        self._blocked_count = 0
        self._processed_count = 0


class SamplingLogger:
    """
    Logger wrapper that samples high-frequency operations.

    Instead of logging every operation, samples at a configurable rate.
    This dramatically reduces log volume while maintaining visibility.

    Features:
    - Counter-based sampling (log every Nth operation)
    - Per-key independent sampling with LRU cache
    - Automatic counter reset to prevent overflow
    - Bounded memory usage
    - Automatic sample count tracking

    PHASE 2 FIX (2025-10-28): Added LRU cache and counter reset per EXAI QA review
    EXAI Consultation: 7e59bfd7-a9cc-4a19-9807-5ebd84082cab

    Usage:
        sampler = SamplingLogger(logger, sample_rate=0.1, max_keys=1000)
        sampler.debug("High-frequency operation", key="operation_type")

    Note:
        Uses counter-based sampling for predictable statistical sampling.
        For 10% sampling, logs every 10th operation regardless of timing.
        This ensures representative sampling across variable traffic patterns.
    """

    def __init__(
        self,
        logger: logging.Logger,
        sample_rate: float = 0.1,
        max_keys: int = 1000,
        counter_reset_threshold: int = 1_000_000
    ):
        """
        Initialize sampling logger.

        Args:
            logger: Base logger to wrap
            sample_rate: Fraction of operations to log (0.0-1.0)
            max_keys: Maximum number of unique keys to track (LRU eviction)
            counter_reset_threshold: Reset counter after this many operations
        """
        self.logger = logger
        self.sample_rate = max(0.0, min(1.0, sample_rate))
        self.max_keys = max_keys
        self.counter_reset_threshold = counter_reset_threshold

        # Use OrderedDict for LRU behavior
        self.counters = OrderedDict()
        self._total_samples = 0
        self._active_keys = 0

        # Calculate sample interval (log every Nth operation)
        if sample_rate >= 1.0:
            self.sample_interval = 1  # Log every operation
        elif sample_rate <= 0.0:
            self.sample_interval = float('inf')  # Never log
        else:
            self.sample_interval = int(1.0 / sample_rate)

    def _should_log(self, key: str = "default") -> bool:
        """
        Determine if this operation should be logged using counter-based sampling.

        Implements LRU cache for bounded memory and periodic counter reset.

        Args:
            key: Sampling key for independent tracking

        Returns:
            True if this operation should be logged
        """
        # Always log if sample_rate is 1.0
        if self.sample_rate >= 1.0:
            return True

        # Never log if sample_rate is 0.0
        if self.sample_rate <= 0.0:
            return False

        # Get or create counter for this key
        if key in self.counters:
            # Move to end (most recently used)
            self.counters.move_to_end(key)
            counter = self.counters[key]
        else:
            # New key - check if we need to evict oldest
            if len(self.counters) >= self.max_keys:
                # Remove least recently used key
                self.counters.popitem(last=False)
            counter = 0
            self._active_keys = len(self.counters) + 1

        # Increment counter with periodic reset
        counter += 1
        if counter >= self.counter_reset_threshold:
            counter = 0  # Reset to prevent overflow

        self.counters[key] = counter

        # Log every Nth operation where N = sample_interval
        should_log = counter % self.sample_interval == 0
        if should_log:
            self._total_samples += 1

        return should_log
    
    def debug(self, msg: str, *args, key: str = "default", **kwargs):
        """Log at DEBUG level with sampling."""
        if self._should_log(key):
            self.logger.debug(f"[SAMPLED] {msg}", *args, **kwargs)
    
    def info(self, msg: str, *args, key: str = "default", **kwargs):
        """Log at INFO level with sampling."""
        if self._should_log(key):
            self.logger.info(f"[SAMPLED] {msg}", *args, **kwargs)
    
    def warning(self, msg: str, *args, **kwargs):
        """Log at WARNING level (no sampling for warnings)."""
        self.logger.warning(msg, *args, **kwargs)
    
    def error(self, msg: str, *args, **kwargs):
        """Log at ERROR level (no sampling for errors)."""
        self.logger.error(msg, *args, **kwargs)
    
    def critical(self, msg: str, *args, **kwargs):
        """Log at CRITICAL level (no sampling for critical)."""
        self.logger.critical(msg, *args, **kwargs)

    def get_stats(self) -> dict:
        """Get sampling statistics."""
        total_operations = sum(self.counters.values())
        return {
            "sample_rate": self.sample_rate,
            "sample_interval": self.sample_interval,
            "active_keys": len(self.counters),
            "max_keys": self.max_keys,
            "total_samples": self._total_samples,
            "total_operations": total_operations,
            "counter_reset_threshold": self.counter_reset_threshold,
            "effective_sample_rate": (self._total_samples / max(total_operations, 1) * 100),
            "memory_utilization": (len(self.counters) / self.max_keys * 100)
        }

    def get_detailed_stats(self) -> dict:
        """Get detailed per-key statistics."""
        return {
            "global_stats": self.get_stats(),
            "per_key_counters": dict(self.counters),
            "top_keys": sorted(self.counters.items(), key=lambda x: x[1], reverse=True)[:10]
        }

    def reset_stats(self):
        """Reset statistics counters."""
        self._total_samples = 0
        self.counters.clear()
        self._active_keys = 0


def log_sampled(sample_rate: float = 0.1, key: Optional[str] = None):
    """
    Decorator to sample high-frequency function calls.
    
    Logs function execution at the specified sample rate.
    
    Args:
        sample_rate: Fraction of calls to log (0.0-1.0)
        key: Optional key for independent sampling tracking
    
    Usage:
        @log_sampled(sample_rate=0.01)  # 1% sampling
        def process_message(msg):
            # ... processing logic
    """
    def decorator(func: Callable) -> Callable:
        logger = logging.getLogger(func.__module__)
        sampler = SamplingLogger(logger, sample_rate=sample_rate)
        sample_key = key or func.__name__
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            sampler.debug(f"Executing {func.__name__}", key=sample_key)
            result = func(*args, **kwargs)
            return wrapper
        
        return wrapper
    return decorator


def get_async_logger(name: str, max_queue_size: int = 1000) -> logging.Logger:
    """
    Get a logger with async handler attached.
    
    Args:
        name: Logger name (typically __name__)
        max_queue_size: Maximum async queue size
    
    Returns:
        Logger with async handler
    
    Usage:
        logger = get_async_logger(__name__)
        logger.info("This will be logged asynchronously")
    """
    logger = logging.getLogger(name)
    
    # Check if async handler already attached
    for handler in logger.handlers:
        if isinstance(handler, AsyncLogHandler):
            return logger
    
    # Add async handler
    async_handler = AsyncLogHandler(max_queue_size=max_queue_size)
    async_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s %(name)s: %(message)s'
    ))
    logger.addHandler(async_handler)
    
    return logger


def get_sampling_logger(name: str, sample_rate: float = 0.1) -> SamplingLogger:
    """
    Get a sampling logger for high-frequency operations.
    
    Args:
        name: Logger name (typically __name__)
        sample_rate: Fraction of operations to log (0.0-1.0)
    
    Returns:
        SamplingLogger instance
    
    Usage:
        logger = get_sampling_logger(__name__, sample_rate=0.01)
        logger.debug("High-frequency operation")  # Only logs 1% of calls
    """
    base_logger = logging.getLogger(name)
    return SamplingLogger(base_logger, sample_rate=sample_rate)


# Feature flag for async logging (from environment)
ASYNC_LOGGING_ENABLED = os.getenv("ASYNC_LOGGING_ENABLED", "false").lower() == "true"


def get_logger(name: str, use_async: Optional[bool] = None, sample_rate: Optional[float] = None) -> logging.Logger:
    """
    Get a logger with optional async and sampling features.
    
    This is the main entry point for getting loggers in the application.
    
    Args:
        name: Logger name (typically __name__)
        use_async: Enable async logging (defaults to ASYNC_LOGGING_ENABLED env var)
        sample_rate: If provided, returns SamplingLogger instead
    
    Returns:
        Logger or SamplingLogger instance
    
    Usage:
        # Standard logger
        logger = get_logger(__name__)
        
        # Async logger
        logger = get_logger(__name__, use_async=True)
        
        # Sampling logger
        logger = get_logger(__name__, sample_rate=0.1)
    """
    if sample_rate is not None:
        return get_sampling_logger(name, sample_rate=sample_rate)
    
    if use_async is None:
        use_async = ASYNC_LOGGING_ENABLED
    
    if use_async:
        return get_async_logger(name)
    
    return logging.getLogger(name)

