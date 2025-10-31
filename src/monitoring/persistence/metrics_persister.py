"""
Metrics Persister

Persists validation metrics to Supabase database with periodic flushing.
Includes resilience patterns (circuit breaker, retry logic) and DLQ support.

EXAI Consultation: ac40c717-09db-4b0a-b943-6e38730a1300
Date: 2025-11-01
Phase: Phase 2.4.6 - MetricsPersister Resilience
"""

import logging
import threading
import time
import os
from typing import Any, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class MetricsPersister:
    """
    Persists validation metrics to database.

    Features:
    - Periodic flush of metrics
    - Aggregation by event type
    - Error handling and retry logic
    - Thread-safe operations
    - Resilience patterns (circuit breaker, retry logic)
    - Dead Letter Queue (DLQ) for failed operations
    - Graceful shutdown support
    """

    def __init__(self, supabase_client: Any, flush_interval: int = 300):
        """
        Initialize metrics persister.

        Args:
            supabase_client: Supabase client instance
            flush_interval: Flush interval in seconds (default: 300)
        """
        self.supabase = supabase_client
        self.flush_interval = flush_interval
        self._lock = threading.Lock()
        self._flush_thread: Optional[threading.Thread] = None
        self._running = False
        self._last_flush = datetime.now()

        # PHASE 2.4.6: Initialize resilience patterns
        self._init_resilience_patterns()

        # PHASE 2.4.6: Initialize DLQ and graceful shutdown
        self._init_dlq_and_shutdown()

    def _init_resilience_patterns(self) -> None:
        """Initialize circuit breaker and retry logic"""
        try:
            from src.monitoring.resilience import ResilienceWrapperFactory, RetryConfig

            # Get configuration from environment
            cb_threshold = int(os.getenv('METRICS_PERSISTER_CIRCUIT_BREAKER_THRESHOLD', '5'))
            cb_timeout = int(os.getenv('METRICS_PERSISTER_CIRCUIT_BREAKER_TIMEOUT', '60'))
            retry_attempts = int(os.getenv('METRICS_PERSISTER_RETRY_MAX_ATTEMPTS', '3'))
            retry_backoff = float(os.getenv('METRICS_PERSISTER_RETRY_BACKOFF_FACTOR', '2.0'))

            # Create resilience wrapper
            self._resilience_wrapper = ResilienceWrapperFactory.create(
                'metrics_persister_db',
                circuit_breaker_config={
                    'failure_threshold': cb_threshold,
                    'recovery_timeout': cb_timeout,
                },
                retry_config=RetryConfig(
                    max_attempts=retry_attempts,
                    initial_delay=1.0,
                    exponential_base=retry_backoff,
                )
            )
            logger.info("Resilience patterns initialized for MetricsPersister")

        except Exception as e:
            logger.warning(f"Failed to initialize resilience patterns: {e}")
            self._resilience_wrapper = None

    def _init_dlq_and_shutdown(self) -> None:
        """Initialize DLQ and graceful shutdown"""
        try:
            from src.monitoring.persistence.dead_letter_queue import get_dlq
            from src.monitoring.persistence.graceful_shutdown import (
                get_shutdown_handler,
                register_metrics_flush_handler
            )

            # Initialize DLQ
            self._dlq = get_dlq(self.supabase)

            # Register metrics flush handler for graceful shutdown
            shutdown_handler = get_shutdown_handler()
            register_metrics_flush_handler(self.flush)

            logger.info("DLQ and graceful shutdown initialized for MetricsPersister")

        except Exception as e:
            logger.warning(f"Failed to initialize DLQ and shutdown: {e}")
            self._dlq = None
    
    def start(self) -> None:
        """Start periodic flush background thread"""
        if self._running:
            logger.warning("MetricsPersister already running")
            return
        
        self._running = True
        self._flush_thread = threading.Thread(
            target=self._flush_loop,
            daemon=True,
            name='MetricsPersisterFlushThread'
        )
        self._flush_thread.start()
        logger.info(f"MetricsPersister started (flush interval: {self.flush_interval}s)")
    
    def stop(self) -> None:
        """Stop periodic flush background thread"""
        self._running = False
        if self._flush_thread:
            self._flush_thread.join(timeout=5)
        logger.info("MetricsPersister stopped")
    
    def _flush_loop(self) -> None:
        """Background thread for periodic flushing"""
        while self._running:
            try:
                time.sleep(self.flush_interval)
                if self._running:
                    self.flush()
            except Exception as e:
                logger.error(f"Error in flush loop: {e}")
    
    def flush(self, metrics_data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Flush metrics to database with resilience protection.

        Args:
            metrics_data: Metrics data to flush (from ValidationMetrics.get_flush_data())

        Returns:
            True if flush successful, False otherwise
        """
        if not metrics_data:
            logger.debug("No metrics data to flush")
            return True

        # PHASE 2.4.6: Use resilience wrapper if available
        if self._resilience_wrapper:
            try:
                result = self._resilience_wrapper.execute(
                    self._flush_with_lock,
                    metrics_data
                )
                return result
            except Exception as e:
                logger.error(f"Resilience wrapper failed: {e}")
                # Fall through to store in DLQ
                if self._dlq:
                    self._dlq.store_failed_operation(
                        {'metrics_data': metrics_data},
                        f"Flush failed: {str(e)}"
                    )
                return False
        else:
            # Fallback: direct flush without resilience
            return self._flush_with_lock(metrics_data)

    def _flush_with_lock(self, metrics_data: Dict[str, Any]) -> bool:
        """
        Internal flush method with lock.

        Args:
            metrics_data: Metrics data to flush

        Returns:
            True if successful, False otherwise
        """
        try:
            with self._lock:
                for event_type, metrics in metrics_data.items():
                    self._persist_metrics(event_type, metrics)

                self._last_flush = datetime.now()
                logger.info(
                    f"Flushed metrics for {len(metrics_data)} event types "
                    f"at {self._last_flush.isoformat()}"
                )
                return True

        except Exception as e:
            logger.error(f"Error flushing metrics: {e}")
            return False
    
    def _persist_metrics(self, event_type: str, metrics: Dict[str, Any]) -> None:
        """
        Persist metrics for a single event type.
        
        Args:
            event_type: Type of event
            metrics: Metrics dictionary
        """
        try:
            # Calculate pass rate
            total = metrics.get('total_events', 0)
            passed = metrics.get('passed_events', 0)
            pass_rate = (passed / total * 100) if total > 0 else 0.0
            
            # Calculate average validation time
            validation_count = metrics.get('validation_count', 0)
            total_time = metrics.get('total_validation_time_ms', 0)
            avg_time = (total_time / validation_count) if validation_count > 0 else 0.0
            
            # Prepare data for insertion
            data = {
                'event_type': event_type,
                'total_events': total,
                'passed_events': passed,
                'failed_events': metrics.get('failed_events', 0),
                'pass_rate': pass_rate,
                'avg_validation_time_ms': avg_time,
                'total_errors': metrics.get('error_count', 0),
                'total_warnings': metrics.get('warning_count', 0),
                'flush_timestamp': datetime.now().isoformat(),
            }
            
            # Try to insert via RPC first (if available)
            try:
                self.supabase.rpc(
                    'insert_validation_metrics',
                    data
                ).execute()
                logger.debug(f"Persisted metrics for {event_type} via RPC")
                return
            except Exception as rpc_error:
                logger.debug(f"RPC insert failed: {rpc_error}, trying direct insert")
            
            # Fallback: Try direct insert to public schema
            try:
                self.supabase.table('validation_metrics').insert(data).execute()
                logger.debug(f"Persisted metrics for {event_type} via direct insert")
                return
            except Exception as direct_error:
                logger.debug(f"Direct insert failed: {direct_error}")
            
            # Fallback: Try insert to monitoring schema via view
            try:
                self.supabase.table('validation_metrics_insert').insert(data).execute()
                logger.debug(f"Persisted metrics for {event_type} via view")
                return
            except Exception as view_error:
                logger.warning(
                    f"All persistence methods failed for {event_type}: "
                    f"RPC={rpc_error}, Direct={direct_error}, View={view_error}"
                )
        
        except Exception as e:
            logger.error(f"Error persisting metrics for {event_type}: {e}")
    
    def get_last_flush_time(self) -> datetime:
        """Get timestamp of last flush"""
        return self._last_flush
    
    def get_flush_interval(self) -> int:
        """Get flush interval in seconds"""
        return self.flush_interval
    
    def set_flush_interval(self, interval: int) -> None:
        """Set flush interval in seconds"""
        if interval <= 0:
            logger.warning(f"Invalid flush interval: {interval}, ignoring")
            return

        self.flush_interval = interval
        logger.info(f"Flush interval updated to {interval}s")

    def get_resilience_metrics(self) -> Dict[str, Any]:
        """
        Get resilience pattern metrics.

        Returns:
            Dictionary with circuit breaker and retry metrics
        """
        if not self._resilience_wrapper:
            return {}

        try:
            return self._resilience_wrapper.get_metrics()
        except Exception as e:
            logger.error(f"Failed to get resilience metrics: {e}")
            return {}

    def get_dlq_status(self) -> Dict[str, Any]:
        """
        Get Dead Letter Queue status.

        Returns:
            Dictionary with DLQ statistics
        """
        if not self._dlq:
            return {}

        try:
            return {
                'stats': self._dlq.get_stats(),
                'size': self._dlq.get_size(),
            }
        except Exception as e:
            logger.error(f"Failed to get DLQ status: {e}")
            return {}

