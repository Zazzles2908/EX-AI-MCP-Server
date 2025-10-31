"""
Graceful Shutdown Handler for Monitoring System

Handles graceful shutdown of background threads and pending operations.
Ensures no data loss during shutdown.

EXAI Consultation: ac40c717-09db-4b0a-b943-6e38730a1300
Date: 2025-11-01
Phase: Phase 2.4.6 - MetricsPersister Resilience
"""

import logging
import signal
import threading
import time
from typing import Callable, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class GracefulShutdownHandler:
    """
    Handles graceful shutdown of the monitoring system.
    
    Features:
    - Signal handling (SIGTERM, SIGINT)
    - Pending operation completion
    - Resource cleanup
    - Shutdown timeout enforcement
    - Metrics flushing before shutdown
    """
    
    def __init__(self, timeout_seconds: int = 30):
        """
        Initialize graceful shutdown handler.
        
        Args:
            timeout_seconds: Maximum time to wait for shutdown (default: 30)
        """
        self.timeout_seconds = timeout_seconds
        self._shutdown_event = threading.Event()
        self._shutdown_handlers: List[Callable] = []
        self._is_shutting_down = False
        self._shutdown_start_time: Optional[datetime] = None
        self._pending_operations = 0
        self._lock = threading.Lock()
    
    def register_shutdown_handler(self, handler: Callable) -> None:
        """
        Register a handler to be called during shutdown.
        
        Args:
            handler: Callable to execute during shutdown
        """
        with self._lock:
            self._shutdown_handlers.append(handler)
            logger.debug(f"Registered shutdown handler: {handler.__name__}")
    
    def register_signal_handlers(self) -> None:
        """
        Register signal handlers for SIGTERM and SIGINT.
        """
        def signal_handler(signum, frame):
            signal_name = signal.Signals(signum).name
            logger.info(f"Received signal {signal_name}, initiating graceful shutdown")
            self.initiate_shutdown()
        
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
        logger.info("Signal handlers registered (SIGTERM, SIGINT)")
    
    def initiate_shutdown(self) -> None:
        """
        Initiate graceful shutdown sequence.
        """
        with self._lock:
            if self._is_shutting_down:
                logger.warning("Shutdown already in progress")
                return
            
            self._is_shutting_down = True
            self._shutdown_start_time = datetime.now()
        
        logger.info(f"Initiating graceful shutdown (timeout: {self.timeout_seconds}s)")
        self._shutdown_event.set()
    
    def is_shutting_down(self) -> bool:
        """Check if shutdown is in progress"""
        return self._is_shutting_down
    
    def wait_for_shutdown(self) -> bool:
        """
        Wait for shutdown signal.
        
        Returns:
            True if shutdown signal received, False if timeout
        """
        return self._shutdown_event.wait(timeout=self.timeout_seconds)
    
    def increment_pending_operations(self) -> None:
        """Increment count of pending operations"""
        with self._lock:
            self._pending_operations += 1
    
    def decrement_pending_operations(self) -> None:
        """Decrement count of pending operations"""
        with self._lock:
            self._pending_operations = max(0, self._pending_operations - 1)
    
    def get_pending_operations(self) -> int:
        """Get count of pending operations"""
        with self._lock:
            return self._pending_operations
    
    def get_shutdown_time_remaining(self) -> float:
        """
        Get remaining time for shutdown.
        
        Returns:
            Seconds remaining, or 0 if timeout exceeded
        """
        if not self._shutdown_start_time:
            return self.timeout_seconds
        
        elapsed = (datetime.now() - self._shutdown_start_time).total_seconds()
        remaining = max(0, self.timeout_seconds - elapsed)
        return remaining
    
    def execute_shutdown(self) -> bool:
        """
        Execute shutdown sequence.
        
        Returns:
            True if shutdown completed successfully, False if timeout
        """
        logger.info("Executing shutdown handlers...")
        
        # Execute all registered handlers
        for handler in self._shutdown_handlers:
            try:
                remaining_time = self.get_shutdown_time_remaining()
                if remaining_time <= 0:
                    logger.warning("Shutdown timeout exceeded, stopping handler execution")
                    return False
                
                logger.debug(f"Executing shutdown handler: {handler.__name__}")
                handler()
                
            except Exception as e:
                logger.error(f"Error in shutdown handler {handler.__name__}: {e}")
        
        # Wait for pending operations to complete
        logger.info("Waiting for pending operations to complete...")
        start_time = time.time()
        
        while self.get_pending_operations() > 0:
            remaining_time = self.get_shutdown_time_remaining()
            if remaining_time <= 0:
                logger.warning(
                    f"Shutdown timeout exceeded with {self.get_pending_operations()} "
                    f"pending operations still running"
                )
                return False
            
            pending = self.get_pending_operations()
            logger.debug(f"Waiting for {pending} pending operations (timeout: {remaining_time:.1f}s)")
            time.sleep(0.1)
        
        elapsed = time.time() - start_time
        logger.info(f"Graceful shutdown completed successfully ({elapsed:.2f}s)")
        return True


# Global shutdown handler instance
_shutdown_handler: Optional[GracefulShutdownHandler] = None


def get_shutdown_handler(timeout_seconds: int = 30) -> GracefulShutdownHandler:
    """
    Get or create global shutdown handler instance.
    
    Args:
        timeout_seconds: Timeout for shutdown (default: 30)
        
    Returns:
        GracefulShutdownHandler instance
    """
    global _shutdown_handler
    
    if _shutdown_handler is None:
        _shutdown_handler = GracefulShutdownHandler(timeout_seconds)
        _shutdown_handler.register_signal_handlers()
    
    return _shutdown_handler


class ShutdownContext:
    """
    Context manager for tracking pending operations during shutdown.
    
    Usage:
        with ShutdownContext():
            # Perform operation
            pass
    """
    
    def __init__(self, handler: Optional[GracefulShutdownHandler] = None):
        """
        Initialize shutdown context.
        
        Args:
            handler: GracefulShutdownHandler instance (uses global if None)
        """
        self.handler = handler or get_shutdown_handler()
    
    def __enter__(self):
        """Enter context - increment pending operations"""
        self.handler.increment_pending_operations()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context - decrement pending operations"""
        self.handler.decrement_pending_operations()
        return False


def register_metrics_flush_handler(flush_callback: Callable) -> None:
    """
    Register metrics flush callback to be called during shutdown.
    
    Args:
        flush_callback: Callable that flushes metrics
    """
    handler = get_shutdown_handler()
    handler.register_shutdown_handler(flush_callback)
    logger.info("Registered metrics flush handler for shutdown")


def register_adapter_cleanup_handler(cleanup_callback: Callable) -> None:
    """
    Register adapter cleanup callback to be called during shutdown.
    
    Args:
        cleanup_callback: Callable that cleans up adapters
    """
    handler = get_shutdown_handler()
    handler.register_shutdown_handler(cleanup_callback)
    logger.info("Registered adapter cleanup handler for shutdown")

