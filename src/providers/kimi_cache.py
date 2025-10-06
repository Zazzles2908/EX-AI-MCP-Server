"""Kimi cache token management (LRU + TTL)."""

import logging
import os
import time
from typing import Optional

logger = logging.getLogger(__name__)


# Simple in-process LRU for Kimi context tokens per session/tool/prefix
_cache_tokens: dict[str, tuple[str, float]] = {}
_cache_tokens_order: list[str] = []
_cache_tokens_ttl: float = float(os.getenv("KIMI_CACHE_TOKEN_TTL_SECS", "1800"))
_cache_tokens_max: int = int(os.getenv("KIMI_CACHE_TOKEN_LRU_MAX", "256"))


def lru_key(session_id: str, tool_name: str, prefix_hash: str) -> str:
    """Generate cache key from session, tool, and prefix hash.
    
    Args:
        session_id: Session identifier
        tool_name: Tool name
        prefix_hash: Hash of message prefix
        
    Returns:
        Cache key string
    """
    return f"{session_id}:{tool_name}:{prefix_hash}"


def save_cache_token(session_id: str, tool_name: str, prefix_hash: str, token: str) -> None:
    """Save cache token with TTL.

    Args:
        session_id: Session identifier
        tool_name: Tool name
        prefix_hash: Hash of message prefix
        token: Cache token to save
    """
    try:
        k = lru_key(session_id, tool_name, prefix_hash)
        _cache_tokens[k] = (token, time.time())
        _cache_tokens_order.append(k)
        # Purge expired and over-capacity entries
        purge_cache_tokens()
        logger.info("Kimi cache token saved key=%s suffix=%s", k[-24:], token[-6:])
    except (TypeError, ValueError, KeyError) as e:
        logger.warning("Failed to save cache token: %s", e)
    except Exception as e:
        logger.error("Unexpected error saving cache token: %s", e)


def get_cache_token(session_id: str, tool_name: str, prefix_hash: str) -> Optional[str]:
    """Retrieve cached token if not expired.

    Args:
        session_id: Session identifier
        tool_name: Tool name
        prefix_hash: Hash of message prefix

    Returns:
        Cache token if found and not expired, None otherwise
    """
    try:
        k = lru_key(session_id, tool_name, prefix_hash)
        v = _cache_tokens.get(k)
        if not v:
            return None
        token, ts = v
        if time.time() - ts > _cache_tokens_ttl:
            _cache_tokens.pop(k, None)
            return None
        return token
    except (TypeError, ValueError, KeyError) as e:
        logger.warning("Failed to get cache token: %s", e)
        return None
    except Exception as e:
        logger.error("Unexpected error getting cache token: %s", e)
        return None


def purge_cache_tokens() -> None:
    """Purge expired and over-capacity cache tokens (LRU + TTL).

    Removes tokens that have exceeded TTL and enforces LRU max size limit.
    """
    global _cache_tokens, _cache_tokens_order
    try:
        # TTL-based cleanup
        now = time.time()
        ttl = _cache_tokens_ttl
        _cache_tokens = {k: v for k, v in _cache_tokens.items() if now - v[1] <= ttl}
        # LRU size limit
        if len(_cache_tokens) > _cache_tokens_max:
            # remove oldest keys
            to_remove = len(_cache_tokens) - _cache_tokens_max
            removed = 0
            for k in list(_cache_tokens_order):
                if k in _cache_tokens:
                    _cache_tokens.pop(k, None)
                    removed += 1
                    if removed >= to_remove:
                        break
    except (TypeError, ValueError, KeyError) as e:
        logger.warning("Failed to purge cache tokens: %s", e)
    except Exception as e:
        logger.error("Unexpected error purging cache tokens: %s", e)


__all__ = [
    "lru_key",
    "save_cache_token",
    "get_cache_token",
    "purge_cache_tokens",
]

