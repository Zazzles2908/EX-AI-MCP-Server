from __future__ import annotations
from typing import List, Dict

from .history_store import get_history_store


def assemble_context_block(continuation_id: str, max_turns: int = 6) -> str:
    """
    Build a textual preface from recent conversation turns for models that accept
    a single string prompt. Keeps it compact and clear.

    BUG FIX #12 (2025-10-20): Now uses Supabase-based storage with context pruning
    instead of in-memory history_store. This prevents context bloat and enables
    intelligent message limiting.
    """
    if not continuation_id:
        return ""

    # BUG FIX #12: Use new Supabase-based storage with context pruning
    from utils.conversation.storage_factory import build_conversation_history

    # build_conversation_history returns (history_string, token_count)
    # We only need the history_string for the preface
    history_string, _ = build_conversation_history(continuation_id, model_context=None)

    if not history_string:
        return ""

    # The history_string already includes formatting from build_conversation_history()
    # Just return it directly
    return history_string

