"""
EX-AI-MCP-Server conversation management package.

Provides session management and caching for the EX-AI-MCP-Server WebSocket daemon.

BUG FIX #14 (2025-10-20): Removed legacy conversation systems
- DELETED: HistoryStore (in-memory JSONL history) - replaced by Supabase
- DELETED: MemoryPolicy (text-based context assembly) - replaced by message arrays
- KEPT: CacheStore (provider context reuse) - still needed for session management

Modern conversation management uses:
- Supabase for persistent storage (utils/conversation/supabase_memory.py)
- Message arrays for SDK-native format (no text-based history building)
- Request handler provides _messages parameter to all tools
"""

__version__ = "2.0.0"

from .cache_store import get_cache_store

__all__ = [
    "get_cache_store",
]

