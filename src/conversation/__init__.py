"""
EX-AI-MCP-Server conversation management package.

Provides session management, caching, history tracking, and memory policies
for the EX-AI-MCP-Server WebSocket daemon.

This package implements:
- CacheStore: In-memory cache for provider context reuse (session_id, call_key, tokens)
- HistoryStore: In-memory + JSONL-persisted conversation history keyed by continuation_id
- MemoryPolicy: Context assembly and token budget management for conversation continuity
- SessionManager: Async session lifecycle management with bounded semaphores

All stores use thread-safe singleton patterns for consistent state within the server process.
"""

__version__ = "1.0.0"

from .cache_store import get_cache_store
from .history_store import get_history_store
from .memory_policy import assemble_context_block

__all__ = [
    "get_cache_store",
    "get_history_store",
    "assemble_context_block",
]

