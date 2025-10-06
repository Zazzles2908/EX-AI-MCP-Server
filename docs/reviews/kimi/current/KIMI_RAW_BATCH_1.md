# Batch 1 Code Review

## Files Reviewed
- `__init__.py` (src package)
- `cache_store.py`
- `history_store.py`
- `__init__.py` (conversation package)
- `KIMI_DESIGN_CONTEXT.md`

## Findings

### CRITICAL: Missing error handling in critical paths
**File:** `cache_store.py`
**Lines:** 25-32
**Category:** reliability
**Issue:** The `record()` and `load()` methods lack proper error handling for edge cases. If an exception occurs during dictionary operations, it could corrupt the cache state or cause the entire cache to become unusable.
**Recommendation:** Add try-except blocks around critical operations and implement proper error recovery:

```python
def record(self, continuation_id: str, data: Dict[str, Any]) -> None:
    if not continuation_id:
        return
    try:
        with self._lock:
            cur = dict(self._mem.get(continuation_id) or {})
            cur.update(data or {})
            self._mem[continuation_id] = cur
    except Exception as e:
        logger.error(f"Cache record failed for {continuation_id}: {e}")
        # Consider implementing fallback or cleanup
```

### HIGH: Inconsistent singleton pattern implementation
**File:** `cache_store.py` and `history_store.py`
**Lines:** 34-40 (cache), 85-91 (history)
**Category:** architecture
**Issue:** Both files implement singleton patterns but use different approaches. The cache store uses a simple global variable check, while the history store has more complex initialization. This inconsistency could lead to race conditions during server startup.
**Recommendation:** Standardize the singleton pattern across both stores. Use a thread-safe implementation with proper locking:

```python
_singleton_lock = threading.Lock()
_store: Optional[_CacheStore] = None

def get_cache_store() -> _CacheStore:
    global _store
    if _store is None:
        with _singleton_lock:
            if _store is None:
                _store = _CacheStore()
    return _store
```

### HIGH: Potential memory leak in history store
**File:** `history_store.py`
**Lines:** 18-25, 65-72
**Category:** performance
**Issue:** The in-memory history (`_mem` dict) grows indefinitely without any cleanup mechanism. For long-running servers with many unique `continuation_id` values, this could lead to memory exhaustion.
**Recommendation:** Implement a cleanup strategy:
1. Add a maximum history size per continuation_id (e.g., keep only last 100 messages)
2. Implement LRU eviction for old continuation_ids
3. Add configurable TTL for conversation history

```python
MAX_HISTORY_PER_CONTINUATION = 100
MAX_CONTINUATIONS_IN_MEMORY = 1000

def record_turn(self, continuation_id: str, role: str, content: str) -> None:
    # ... existing code ...
    with self._lock:
        history = self._mem.setdefault(continuation_id, [])
        history.append(item)
        # Enforce max history per continuation
        if len(history) > MAX_HISTORY_PER_CONTINUATION:
            history.pop(0)
        # Enforce max continuations in memory
        if len(self._mem) > MAX_CONTINUATIONS_IN_MEMORY:
            # Remove oldest continuation
            oldest = min(self._mem.keys(), key=lambda k: self._mem[k][0]['ts'] if self._mem[k] else '')
            del self._mem[oldest]
```

### MEDIUM: Missing type hints in public API
**File:** `conversation/__init__.py`
**Lines:** 8-14
**Category:** code_quality
**Issue:** The public API exports lack proper type hints, making it harder for IDEs and type checkers to provide accurate assistance.
**Recommendation:** Add return type hints:

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .cache_store import _CacheStore
    from .history_store import _HistoryStore

__all__ = [
    "get_cache_store",
    "get_history_store", 
    "assemble_context_block",
]
```

### MEDIUM: Inefficient JSONL parsing
**File:** `history_store.py`
**Lines:** 55-65
**Category:** performance
**Issue:** Loading conversation history from JSONL files reads the entire file into memory, then processes line by line. This is inefficient for large conversation files.
**Recommendation:** Use a more efficient approach:

```python
def load_recent(self, continuation_id: str, n: int = 6) -> List[Dict[str, Any]]:
    if not continuation_id:
        return []
    
    # Check memory first
    with self._lock:
        if continuation_id in self._mem:
            return self._mem[continuation_id][-n:]
    
    # Efficient file reading
    try:
        fpath = self._base / f"{continuation_id}.json