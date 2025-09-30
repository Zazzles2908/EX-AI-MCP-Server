from __future__ import annotations

from typing import Any, Dict, Tuple, Optional


def build_websearch_provider_kwargs(
    *,
    provider_type: Any,
    use_websearch: bool,
    include_event: bool = False,
) -> Tuple[Dict[str, Any], Optional[object]]:
    """Build provider kwargs for provider-native websearch injection.

    Returns (provider_kwargs, web_event_or_None).
    - provider_kwargs may include keys: tools, tool_choice
    - When include_event is True and a web tool is injected, returns a ToolCallEvent instance.

    Notes:
    - No fallback logic is introduced; this only assembles the primary provider inputs.
    - Best-effort: if capabilities lookup fails, returns empty kwargs and None event.
    """
    provider_kwargs: Dict[str, Any] = {}
    web_event = None
    try:
        from src.providers.capabilities import get_capabilities_for_provider
        caps = get_capabilities_for_provider(provider_type)
        ws = caps.get_websearch_tool_schema({"use_websearch": bool(use_websearch)})
        if ws.tools:
            provider_kwargs["tools"] = ws.tools
        if ws.tool_choice is not None:
            provider_kwargs["tool_choice"] = ws.tool_choice
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
    except Exception:
        # Capabilities lookup failed; proceed without web tool
        return provider_kwargs, None
    return provider_kwargs, web_event

