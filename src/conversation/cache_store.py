from __future__ import annotations
import threading
from typing import Dict, Any, Optional


class _CacheStore:
    """
    Minimal in-memory cache token/session store keyed by continuation_id.
    Intended for provider context reuse (e.g., session_id, call_key, token).
    """
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._mem: Dict[str, Dict[str, Any]] = {}

    def record(self, continuation_id: str, data: Dict[str, Any]) -> None:
        if not continuation_id:
            return
        with self._lock:
            cur = dict(self._mem.get(continuation_id) or {})
            cur.update(data or {})
            self._mem[continuation_id] = cur

    def load(self, continuation_id: str) -> Dict[str, Any]:
        if not continuation_id:
            return {}
        with self._lock:
            return dict(self._mem.get(continuation_id) or {})


_store: Optional[_CacheStore] = None

def get_cache_store() -> _CacheStore:
    global _store
    if _store is None:
        _store = _CacheStore()
    return _store

