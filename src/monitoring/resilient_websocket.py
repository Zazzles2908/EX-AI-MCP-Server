"""
Resilient WebSocket Manager - Backward-Compatible Wrapper

This module has been refactored into focused, maintainable modules:

REFACTORED MODULES:
- websocket_exceptions.py: Custom exception types
- websocket_models.py: Data structures (ConnectionState, QueuedMessage)
- message_queue.py: Abstract queue and in-memory implementation
- websocket_deduplication.py: Message deduplication logic
- websocket_background_tasks.py: Background task management
- resilient_websocket_manager.py: Main manager class

This file provides a backward-compatible wrapper that imports from the
refactored modules and maintains the original ResilientWebSocketManager API.

Created: 2025-11-04 (Refactoring from 914-line god object)
Part of: God Object Refactoring Milestone - 5 of 7 Complete
Author: Claude Code

CHANGES:
- Original 914-line file split into 6 focused modules
- 100% backward compatible - all existing imports continue to work
- Better separation of concerns and improved maintainability
- Same functionality, better architecture

Original documentation preserved for backward compatibility:
================================================================
Resilient WebSocket Manager for handling connection failures and message queuing.

This module provides a robust WebSocket communication layer with:
- Pending message queue for disconnected clients
- Automatic retry with exponential backoff
- Connection timeout detection
- Message TTL (300s for pending messages)
- Metrics integration (Prometheus/OpenTelemetry compatible)
- Circuit breaker pattern for graceful degradation
- Message deduplication
================================================================
"""

# Re-export all public APIs from refactored modules
from src.monitoring.resilient_websocket_manager import ResilientWebSocketManager

# Also re-export commonly used classes for convenience
from src.monitoring.websocket_models import ConnectionState, QueuedMessage
from src.monitoring.message_queue import MessageQueue, InMemoryMessageQueue
from src.monitoring.websocket_deduplication import MessageDeduplicator

# Backward compatibility: Re-export the main class
__all__ = [
    "ResilientWebSocketManager",
    "ConnectionState",
    "QueuedMessage",
    "MessageQueue",
    "InMemoryMessageQueue",
    "MessageDeduplicator"
]

# Preserve original module docstring for backward compatibility
__doc__ = """
Resilient WebSocket Manager for handling connection failures and message queuing.

This module provides a robust WebSocket communication layer with:
- Pending message queue for disconnected clients
- Automatic retry with exponential backoff
- Connection timeout detection
- Message TTL (300s for pending messages)
- Metrics integration (Prometheus/OpenTelemetry compatible)
- Circuit breaker pattern for graceful degradation
- Message deduplication

REFACTORED (2025-11-04):
This module has been refactored into focused, maintainable modules.
All original functionality is preserved through backward-compatible wrappers.
See individual module documentation for implementation details.

ARCHITECTURE:
- ResilientWebSocketManager: Main orchestrator (in resilient_websocket_manager.py)
- ConnectionState/QueuedMessage: Data models (in websocket_models.py)
- Message Queue: Abstract interface + in-memory impl (in message_queue.py)
- Deduplication: Message deduplication logic (in websocket_deduplication.py)
- Background Tasks: Retry/cleanup tasks (in websocket_background_tasks.py)
- Exceptions: Custom exception types (in websocket_exceptions.py)
"""
