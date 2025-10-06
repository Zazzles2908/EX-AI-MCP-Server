from __future__ import annotations

import os


def is_streaming_enabled(provider_type: str | None, tool_name: str | None) -> bool:
    """Centralized streaming enablement logic.

    - Currently only enables streaming for GLM provider when GLM_STREAM_ENABLED is truthy
      AND the tool name is exactly 'chat'.
    - Gate remains environment-driven to preserve existing behavior.
    - Safe defaults: return False on any error.
    """
    try:
        p = (provider_type or "").strip().lower()
        t = (tool_name or "").strip().lower()
        enabled = os.getenv("GLM_STREAM_ENABLED", "false").strip().lower() in ("1", "true", "yes")
        if p == "glm" and t == "chat":
            return bool(enabled)
        return False
    except (AttributeError, TypeError, ValueError) as e:
        import logging
        logging.getLogger(__name__).debug(f"Streaming flag check failed: {e}")
        return False

