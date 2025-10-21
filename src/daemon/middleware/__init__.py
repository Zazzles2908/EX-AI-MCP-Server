"""
Middleware Components

This package contains middleware components for the EX-AI MCP WebSocket server.
Extracted from ws_server.py as part of code refactoring (2025-10-21).

Modules:
    semaphores: Semaphore management utilities (guard, recovery, monitoring)
"""

from .semaphores import (
    SemaphoreGuard,
    recover_semaphore_leaks,
    check_semaphore_health,
)

__all__ = [
    "SemaphoreGuard",
    "recover_semaphore_leaks",
    "check_semaphore_health",
]

