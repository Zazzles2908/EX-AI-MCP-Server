from __future__ import annotations
from typing import List, Dict

from .history_store import get_history_store


def assemble_context_block(continuation_id: str, max_turns: int = 6) -> str:
    """
    Build a textual preface from recent conversation turns for models that accept
    a single string prompt. Keeps it compact and clear.
    """
    if not continuation_id:
        return ""
    hist = get_history_store().load_recent(continuation_id, n=max_turns)
    if not hist:
        return ""
    lines: List[str] = ["Previous conversation (most recent first):"]
    for item in hist[-max_turns:]:
        role = (item.get("role") or "").strip() or "user"
        content = (item.get("content") or "").strip()
        if content:
            lines.append(f"- {role.title()}: {content}")
    lines.append("")
    return "\n".join(lines)

