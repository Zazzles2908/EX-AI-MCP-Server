from __future__ import annotations
import json
import logging
import os
import threading
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class _HistoryStore:
    """
    Minimal in-memory + JSONL-append conversation history store keyed by continuation_id.
    - In-memory for quick recent retrieval
    - JSONL persisted under logs/conversation/<continuation_id>.jsonl for audit
    """
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._mem: Dict[str, List[Dict[str, Any]]] = {}
        self._base = Path("logs/conversation")
        try:
            self._base.mkdir(parents=True, exist_ok=True)
        except (OSError, PermissionError) as e:
            logger.warning(f"Failed to create conversation history directory: {e}")
        except Exception as e:
            logger.error(f"Unexpected error creating conversation history directory: {e}")

    def record_turn(self, continuation_id: str, role: str, content: str) -> None:
        if not continuation_id:
            return
        item = {
            "ts": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "role": role,
            "content": content,
        }
        with self._lock:
            self._mem.setdefault(continuation_id, []).append(item)
        # append to JSONL on disk (best-effort)
        try:
            fpath = self._base / f"{continuation_id}.jsonl"
            with fpath.open("a", encoding="utf-8") as f:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
        except (OSError, IOError, PermissionError) as e:
            logger.warning(f"Failed to persist conversation turn for {continuation_id}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error persisting conversation turn for {continuation_id}: {e}")

    def load_recent(self, continuation_id: str, n: int = 6) -> List[Dict[str, Any]]:
        if not continuation_id:
            return []
        with self._lock:
            arr = list(self._mem.get(continuation_id) or [])
        if arr:
            return arr[-n:]
        # If no in-memory history yet, try loading from disk (last n lines)
        try:
            fpath = self._base / f"{continuation_id}.jsonl"
            if fpath.exists():
                lines = fpath.read_text(encoding="utf-8", errors="ignore").splitlines()[-n:]
                out: List[Dict[str, Any]] = []
                for ln in lines:
                    try:
                        out.append(json.loads(ln))
                    except json.JSONDecodeError as e:
                        logger.debug(f"Skipping malformed JSON line in {continuation_id}.jsonl: {e}")
                        continue
                    except Exception as e:
                        logger.warning(f"Unexpected error parsing JSON line in {continuation_id}.jsonl: {e}")
                        continue
                # cache into memory
                with self._lock:
                    self._mem[continuation_id] = out
                return out
        except (OSError, IOError, PermissionError) as e:
            logger.warning(f"Failed to load conversation history for {continuation_id}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error loading conversation history for {continuation_id}: {e}")
        return []


# Singleton accessor
_store: Optional[_HistoryStore] = None

def get_history_store() -> _HistoryStore:
    global _store
    if _store is None:
        _store = _HistoryStore()
    return _store

