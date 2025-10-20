from __future__ import annotations

from typing import Any, Dict, Tuple, Optional


def build_websearch_provider_kwargs(
    *,
    provider_type: Any,
    use_websearch: bool,
    model_name: str = "",
    include_event: bool = False,
) -> Tuple[Dict[str, Any], Optional[object]]:
    """Build provider kwargs for provider-native websearch injection.

    Returns (provider_kwargs, web_event_or_None).
    - provider_kwargs may include keys: tools, tool_choice
    - When include_event is True and a web tool is injected, returns a ToolCallEvent instance.

    Notes:
    - No fallback logic is introduced; this only assembles the primary provider inputs.
    - Best-effort: if capabilities lookup fails, returns empty kwargs and None event.
    - model_name is required for GLM to check if model supports websearch
    """
    import logging
    logger = logging.getLogger(__name__)

    provider_kwargs: Dict[str, Any] = {}
    web_event = None
    try:
        from src.providers.capabilities import get_capabilities_for_provider
        caps = get_capabilities_for_provider(provider_type)

        logger.info(f"[WEBSEARCH_DEBUG] provider_type={provider_type}, use_websearch={use_websearch}, model_name={model_name}")

        ws = caps.get_websearch_tool_schema({
            "use_websearch": bool(use_websearch),
            "model_name": model_name
        })

        logger.info(f"[WEBSEARCH_DEBUG] ws.tools={ws.tools}, ws.tool_choice={ws.tool_choice}")

        if ws.tools:
            provider_kwargs["tools"] = ws.tools
            logger.info(f"[WEBSEARCH_DEBUG] Added tools to provider_kwargs: {ws.tools}")
        if ws.tool_choice is not None:
            provider_kwargs["tool_choice"] = ws.tool_choice
            logger.info(f"[WEBSEARCH_DEBUG] Added tool_choice to provider_kwargs: {ws.tool_choice}")
        if include_event and ws.tools:
            try:
                from utils.tool_events import ToolCallEvent
                web_event = ToolCallEvent(
                    provider=getattr(provider_type, "value", str(provider_type)),
                    tool_name="web_search",
                    args={},
                )
            except Exception:
                web_event = None
    except Exception as e:
        # Capabilities lookup failed; proceed without web tool
        logger.warning(f"[WEBSEARCH_DEBUG] Capabilities lookup failed: {e}")
        return provider_kwargs, None

    logger.info(f"[WEBSEARCH_DEBUG] Final provider_kwargs keys: {list(provider_kwargs.keys())}")
    return provider_kwargs, web_event

