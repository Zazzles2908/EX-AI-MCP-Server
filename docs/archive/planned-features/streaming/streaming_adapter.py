from __future__ import annotations

from typing import AsyncIterator, Dict, Any, List, Tuple, Callable, Optional


class StreamingAdapter:
    """Minimal streaming adapter interface (Phase E MVP).

    Concrete adapters should wrap provider streaming APIs and yield token/text chunks.
    """

    async def iter_stream(self, request: Dict[str, Any]) -> AsyncIterator[str]:  # pragma: no cover
        yield ""


class MoonshotStreamingAdapter(StreamingAdapter):
    async def iter_stream(self, request: Dict[str, Any]) -> AsyncIterator[str]:
        # Placeholder: yield a single chunk for now
        yield request.get("prompt", "")[:50]


class ZaiStreamingAdapter(StreamingAdapter):
    async def iter_stream(self, request: Dict[str, Any]) -> AsyncIterator[str]:
        # Placeholder: yield a single chunk for now
        yield request.get("prompt", "")[:50]


# --- Provider-agnostic helpers for OpenAI-compatible streaming (SSE/text-event-stream) ---

def stream_openai_chat_events(
    *,
    client: Any,
    create_kwargs: Dict[str, Any],
    on_delta: Optional[Callable[[str], None]] = None,
) -> Tuple[str, List[Any]]:
    """Iterate OpenAI-compatible chat.completions.create(stream=True) events.

    Returns tuple (content_text, raw_items).
    """
    content_parts: List[str] = []
    raw_items: List[Any] = []
    for evt in client.chat.completions.create(stream=True, **create_kwargs):
        raw_items.append(evt)
        try:
            ch = getattr(evt, "choices", None) or []
            if ch:
                delta = getattr(ch[0], "delta", None)
                if delta:
                    piece = getattr(delta, "content", None)
                    if piece:
                        s = str(piece)
                        content_parts.append(s)
                        if on_delta:
                            on_delta(s)
        except Exception:
            # Continue on best-effort parsing
            pass
    return ("".join(content_parts), raw_items)

