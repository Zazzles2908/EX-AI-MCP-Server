"""
Metrics Persistence Service

Handles persistence of validation metrics to Supabase database.
Provides periodic flush and aggregation capabilities.

EXAI Consultation: ac40c717-09db-4b0a-b943-6e38730a1300
Date: 2025-11-01
Phase: Phase 2.4.6 - MetricsPersister Resilience
"""

from .metrics_persister import MetricsPersister
from .dead_letter_queue import DeadLetterQueue, DLQItem, get_dlq
from .graceful_shutdown import (
    GracefulShutdownHandler,
    ShutdownContext,
    get_shutdown_handler,
    register_metrics_flush_handler,
    register_adapter_cleanup_handler,
)

__all__ = [
    'MetricsPersister',
    'DeadLetterQueue',
    'DLQItem',
    'get_dlq',
    'GracefulShutdownHandler',
    'ShutdownContext',
    'get_shutdown_handler',
    'register_metrics_flush_handler',
    'register_adapter_cleanup_handler',
]

