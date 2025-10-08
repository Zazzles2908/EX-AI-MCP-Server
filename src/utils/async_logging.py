"""
Async-safe logging configuration for the EX-AI MCP Server.

This module provides non-blocking logging using QueueHandler and QueueListener
to prevent deadlocks in async contexts.

CRITICAL: Python's standard logging module uses thread locks internally,
which can cause deadlocks when used in async code. This module solves that
by offloading all logging I/O to a separate thread via a queue.
"""

import logging
import logging.handlers
import queue
import sys
from typing import Optional

# Global listener instance
_log_listener: Optional[logging.handlers.QueueListener] = None


def setup_async_safe_logging(level: int = logging.INFO) -> logging.handlers.QueueListener:
    """
    Configure async-safe logging using QueueHandler and QueueListener.
    
    This prevents logging deadlocks in async code by:
    1. Using a QueueHandler that never blocks (just puts messages in a queue)
    2. Using a QueueListener in a separate thread to actually write logs
    3. Ensuring the event loop is never blocked by logging I/O
    
    Args:
        level: Logging level (default: INFO)
        
    Returns:
        QueueListener instance (must be stopped on shutdown)
    """
    global _log_listener
    
    # If already configured, return existing listener
    if _log_listener is not None:
        return _log_listener
    
    # Create a queue for log messages (no size limit)
    log_queue: queue.Queue = queue.Queue(-1)
    
    # Create the actual handlers that will write logs
    # These run in a separate thread, so they won't block the event loop
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Format for log messages
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # Create listener that processes messages from the queue
    # This runs in a separate thread and handles all I/O
    _log_listener = logging.handlers.QueueListener(
        log_queue,
        console_handler,
        respect_handler_level=True
    )
    
    # Start the listener thread
    _log_listener.start()
    
    # Create queue handler for the root logger
    # This handler just puts messages in the queue (non-blocking)
    queue_handler = logging.handlers.QueueHandler(log_queue)
    
    # Configure root logger
    root_logger = logging.getLogger()
    
    # Remove existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add the queue handler
    root_logger.addHandler(queue_handler)
    root_logger.setLevel(level)
    
    logging.info("[ASYNC_LOGGING] Async-safe logging configured successfully")
    
    return _log_listener


def shutdown_async_logging():
    """
    Shutdown the async logging listener.
    
    Call this on application shutdown to ensure all log messages are flushed.
    """
    global _log_listener
    
    if _log_listener is not None:
        logging.info("[ASYNC_LOGGING] Shutting down async logging listener")
        _log_listener.stop()
        _log_listener = None


def get_async_safe_logger(name: str) -> logging.Logger:
    """
    Get a logger that's safe to use in async contexts.
    
    This returns a standard Python logger, but because we've configured
    the root logger with a QueueHandler, all logging calls are non-blocking.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)

