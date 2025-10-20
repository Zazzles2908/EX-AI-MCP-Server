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

logger = logging.getLogger(__name__)


def stream_openai_chat_events(
    *,
    client: Any,
    create_kwargs: dict[str, Any],
    on_delta: Optional[Callable[[str], None]] = None,
    extract_reasoning: Optional[bool] = None,
) -> Tuple[str, List[Any]]:
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
                                reasoning_parts.append(str(reasoning_piece))
                                # Optionally call on_delta for reasoning too
                                if on_delta:
                                    on_delta(str(reasoning_piece))

                        # Extract regular content
                        piece = getattr(delta, "content", None)
                        if piece:
                            if in_thinking:
                                in_thinking = False
                                logger.debug("=============thinking end=============")
                            s = str(piece)
                            content_parts.append(s)
                            if on_delta:
                                on_delta(s)
            except Exception as e:
                # Continue on best-effort parsing
                logger.debug(f"Failed to parse streaming chunk: {e}")
                pass
    except TimeoutError as timeout_err:
        logger.error(f"Kimi streaming timeout: {timeout_err}")
        raise RuntimeError(f"Kimi streaming timeout: {timeout_err}") from timeout_err
    except Exception as e:
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

