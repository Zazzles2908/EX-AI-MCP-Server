"""
Resilience module for EX-AI MCP Server

This module provides resilience patterns for external service calls:
- Circuit breakers for cascading failure prevention
- Rate limiting for resource protection
- Connection management for WebSocket stability

Phase 1 Implementation (2025-10-18)
"""

from .circuit_breaker_manager import circuit_breaker_manager

__all__ = ['circuit_breaker_manager']

