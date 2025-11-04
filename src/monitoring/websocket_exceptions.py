"""
WebSocket Exceptions - Custom exception types for WebSocket operations.

This module defines custom exceptions used throughout the WebSocket
resilience system for better error handling and debugging.

Created: 2025-11-04 (Refactoring from resilient_websocket.py)
Part of: God Object Refactoring Milestone
"""


class WebSocketError(Exception):
    """Base exception for all WebSocket-related errors."""
    pass


class MessageQueueError(WebSocketError):
    """Exception raised for message queue operations."""
    pass


class QueueOverflowError(MessageQueueError):
    """Exception raised when message queue exceeds capacity."""
    pass


class DeduplicationError(WebSocketError):
    """Exception raised for message deduplication errors."""
    pass


class CircuitBreakerError(WebSocketError):
    """Exception raised for circuit breaker operations."""
    pass


class ConnectionTimeoutError(WebSocketError):
    """Exception raised when WebSocket connection times out."""
    pass


class ShutdownError(WebSocketError):
    """Exception raised during graceful shutdown operations."""
    pass


__all__ = [
    "WebSocketError",
    "MessageQueueError",
    "QueueOverflowError",
    "DeduplicationError",
    "CircuitBreakerError",
    "ConnectionTimeoutError",
    "ShutdownError"
]
