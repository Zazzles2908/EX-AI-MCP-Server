"""Streaming adapter for OpenAI-compatible providers with thinking mode support.

Supports:
- Standard content streaming
- Kimi thinking mode (reasoning_content extraction)
- GLM thinking mode (thinking field extraction)
"""

from __future__ import annotations

import logging
import os
from typing import Any, Callable, List, Optional, Tuple

# Import httpx for RemoteProtocolError handling
try:
    import httpx
except ImportError:
    httpx = None

logger = logging.getLogger(__name__)


def _safe_call_chunk_callback(callback: Callable[[str], None], chunk: str) -> None:
    """
    Safely call a chunk callback, handling both sync and async callbacks.

    NEW (2025-10-24): Helper function for progressive streaming support.
    FIX (2025-11-07): Proper async/sync pattern - create event loop in thread if needed.

    Args:
        callback: Sync or async callback function
        chunk: Text chunk to forward

    Note:
        For async callbacks, creates a task in the running event loop.
        Falls back to new event loop if no loop is running.
    """
    import asyncio
    import inspect

    try:
        if inspect.iscoroutinefunction(callback):
            # Async callback - need to run in event loop
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Create task in running loop (don't await - fire and forget)
                    asyncio.create_task(callback(chunk))
                else:
                    # Run in new loop
                    loop.run_until_complete(callback(chunk))
            except RuntimeError:
                # No event loop - create one properly
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(callback(chunk))
                finally:
                    loop.close()
        else:
            # Sync callback
            callback(chunk)
    except Exception as e:
        # Log but don't propagate - streaming is best-effort
        logger.debug(f"Chunk callback error: {e}")


def stream_openai_chat_events(
    *,
    client: Any,
    create_kwargs: dict[str, Any],
    on_delta: Optional[Callable[[str], None]] = None,
    on_chunk: Optional[Callable[[str], None]] = None,  # NEW (2025-10-24): For WebSocket progressive forwarding
    extract_reasoning: Optional[bool] = None,
) -> Tuple[str, List[Any]]:
    """
    Stream OpenAI-compatible chat events with optional progressive chunk forwarding.

    Args:
        client: OpenAI-compatible client instance
        create_kwargs: Arguments for client.chat.completions.create()
        on_delta: Optional callback for each content delta (legacy)
        on_chunk: Optional async callback for progressive WebSocket streaming (NEW)
        extract_reasoning: Whether to extract reasoning tokens

    Returns:
        Tuple of (complete_content, reasoning_events)

    Note:
        on_chunk callback can be sync or async. If async, it will be awaited.
        This enables real-time progressive streaming to WebSocket clients.
    """
    """Iterate OpenAI-compatible chat.completions.create(stream=True) events.

    Supports both standard content streaming and thinking mode (reasoning_content).

    Args:
        client: OpenAI-compatible client instance
        create_kwargs: Kwargs for client.chat.completions.create()
        on_delta: Optional callback for each content delta
        extract_reasoning: Whether to extract reasoning_content (for kimi-thinking-preview)
                          If None, reads from KIMI_EXTRACT_REASONING env var (default: true)

    Returns:
        Tuple of (content_text, raw_items)
        - content_text: Concatenated content (reasoning + regular content)
        - raw_items: List of raw streaming events
    """
    # Read extract_reasoning from env if not explicitly provided
    if extract_reasoning is None:
        extract_reasoning = os.getenv("KIMI_EXTRACT_REASONING", "true").strip().lower() in ("1", "true", "yes")

    # SECURITY FIX: Add buffer size limits to prevent memory exhaustion
    # Max chunks to prevent unbounded list growth
    MAX_CHUNKS = int(os.getenv("STREAM_MAX_CHUNKS", "10000"))
    MAX_CONTENT_SIZE = int(os.getenv("STREAM_MAX_CONTENT_SIZE", str(10 * 1024 * 1024)))  # 10MB default

    content_parts: List[str] = []
    reasoning_parts: List[str] = []
    raw_items: List[Any] = []

    # Track if we're in thinking mode
    in_thinking = False

    # CRITICAL FIX (2025-10-15): Add streaming timeout to prevent 6+ hour hangs
    # Get timeout from env (default 10 minutes for Kimi - can be slower than GLM)
    import time
    stream_timeout = int(os.getenv("KIMI_STREAM_TIMEOUT", "600"))  # 10 minutes default
    stream_start = time.time()

    try:
        for evt in client.chat.completions.create(stream=True, **create_kwargs):
            # Check if streaming has exceeded timeout
            elapsed = time.time() - stream_start
            if elapsed > stream_timeout:
                raise TimeoutError(
                    f"Kimi streaming exceeded timeout of {stream_timeout}s (elapsed: {int(elapsed)}s). "
                    "This prevents indefinite hangs. Increase KIMI_STREAM_TIMEOUT if needed."
                )

            # SECURITY FIX: Check buffer size before appending to raw_items
            if len(raw_items) >= MAX_CHUNKS:
                logger.warning(f"Raw items buffer overflow: max {MAX_CHUNKS} items reached")
                raise RuntimeError(
                    f"Stream buffer overflow: raw items exceeded limit of {MAX_CHUNKS}. "
                    f"Increase STREAM_MAX_CHUNKS if needed."
                )

            raw_items.append(evt)
            try:
                ch = getattr(evt, "choices", None) or []
                if ch:
                    delta = getattr(ch[0], "delta", None)
                    if delta:
                        # Extract reasoning_content for Kimi thinking mode
                        # Source: https://platform.moonshot.ai/docs/guide/use-kimi-thinking-preview-model
                        if extract_reasoning and hasattr(delta, "reasoning_content"):
                            reasoning_piece = getattr(delta, "reasoning_content")
                            if reasoning_piece:
                                if not in_thinking:
                                    in_thinking = True
                                    logger.debug("=============thinking start=============")

                                # SECURITY FIX: Check buffer size before appending
                                reasoning_str = str(reasoning_piece)
                                total_size = sum(len(p) for p in reasoning_parts) + len(reasoning_str)
                                if len(reasoning_parts) >= MAX_CHUNKS:
                                    logger.warning(f"Reasoning buffer overflow: max {MAX_CHUNKS} chunks reached")
                                    raise RuntimeError(
                                        f"Stream buffer overflow: reasoning chunks exceeded limit of {MAX_CHUNKS}. "
                                        f"Increase STREAM_MAX_CHUNKS if needed."
                                    )
                                if total_size > MAX_CONTENT_SIZE:
                                    logger.warning(f"Reasoning buffer overflow: max {MAX_CONTENT_SIZE} bytes reached")
                                    raise RuntimeError(
                                        f"Stream buffer overflow: reasoning content exceeded {MAX_CONTENT_SIZE} bytes. "
                                        f"Increase STREAM_MAX_CONTENT_SIZE if needed."
                                    )

                                reasoning_parts.append(reasoning_str)
                                # Optionally call on_delta for reasoning too
                                if on_delta:
                                    on_delta(reasoning_str)
                                if on_chunk:  # NEW (2025-10-24): Forward reasoning chunks too
                                    _safe_call_chunk_callback(on_chunk, reasoning_str)

                        # Extract regular content
                        piece = getattr(delta, "content", None)
                        if piece:
                            if in_thinking:
                                in_thinking = False
                                logger.debug("=============thinking end=============")
                            s = str(piece)

                            # SECURITY FIX: Check buffer size before appending
                            total_size = sum(len(p) for p in content_parts) + len(s)
                            if len(content_parts) >= MAX_CHUNKS:
                                logger.warning(f"Content buffer overflow: max {MAX_CHUNKS} chunks reached")
                                raise RuntimeError(
                                    f"Stream buffer overflow: content chunks exceeded limit of {MAX_CHUNKS}. "
                                    f"Increase STREAM_MAX_CHUNKS if needed."
                                )
                            if total_size > MAX_CONTENT_SIZE:
                                logger.warning(f"Content buffer overflow: max {MAX_CONTENT_SIZE} bytes reached")
                                raise RuntimeError(
                                    f"Stream buffer overflow: content exceeded {MAX_CONTENT_SIZE} bytes. "
                                    f"Increase STREAM_MAX_CONTENT_SIZE if needed."
                                )

                            content_parts.append(s)
                            if on_delta:
                                on_delta(s)
                            if on_chunk:  # NEW (2025-10-24): Forward chunk for WebSocket streaming
                                _safe_call_chunk_callback(on_chunk, s)
            except Exception as e:
                # Continue on best-effort parsing
                logger.debug(f"Failed to parse streaming chunk: {e}")
                pass
    except TimeoutError as timeout_err:
        logger.error(f"Kimi streaming timeout: {timeout_err}")
        raise RuntimeError(f"Kimi streaming timeout: {timeout_err}") from timeout_err
    except Exception as e:
        # Check if this is a RemoteProtocolError (connection closed prematurely)
        if httpx and isinstance(e, (httpx.RemoteProtocolError, getattr(httpx, '_exceptions', {}).get('RemoteProtocolError'))):
            logger.warning(
                f"Kimi API closed connection prematurely during streaming. "
                f"Returning partial response (elapsed: {int(time.time() - stream_start)}s). "
                f"Error: {e}"
            )
            # Return partial data - we've accumulated content_parts and reasoning_parts
            final_text = ""
            if reasoning_parts:
                reasoning_text = "".join(reasoning_parts)
                final_text = f"[Reasoning]\n{reasoning_text}\n\n[Response]\n"
            final_text += "".join(content_parts)
            return (final_text, raw_items)
        else:
            logger.error(f"Streaming error: {e}")
            raise
    
    # Combine reasoning and content
    # Format: [Reasoning]\n{reasoning}\n\n[Response]\n{content}
    final_text = ""
    if reasoning_parts:
        reasoning_text = "".join(reasoning_parts)
        final_text = f"[Reasoning]\n{reasoning_text}\n\n[Response]\n"
    final_text += "".join(content_parts)
    
    return (final_text, raw_items)

