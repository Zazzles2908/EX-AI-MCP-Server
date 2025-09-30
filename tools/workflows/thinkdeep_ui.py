"""
ThinkDeep Workflow UI Helpers

UI summary generation functions for the ThinkDeep workflow tool.
These functions format workflow data for client rendering.
"""

from typing import Any, Optional


def ui_summarize_text(txt: str, max_items: int = 5) -> list[str]:
    """
    Summarize text into bullet points for UI display.
    
    Args:
        txt: Text to summarize
        max_items: Maximum number of items to return
        
    Returns:
        List of summary bullet points
    """
    try:
        if not txt:
            return []
        lines = [l.strip(" \t-•") for l in txt.splitlines() if l.strip()]
        bullets = [l for l in lines if l.startswith(('-', '*')) or (len(l) > 1 and l[:2].isdigit())]
        if not bullets:
            import re
            sentences = re.split(r"(?<=[.!?])\s+", txt)
            bullets = [s.strip() for s in sentences if s.strip()][:max_items]
        return bullets[:max_items]
    except Exception:
        return []


def ui_build_summary(
    request: Any,
    assistant_response: str,
    continuation_id_val: Optional[str] = None,
    extra: dict | None = None,
    tool_instance: Any = None,
) -> dict:
    """
    Build a comprehensive UI summary for the ThinkDeep workflow.
    
    Args:
        request: The workflow request object
        assistant_response: Response from the assistant model
        continuation_id_val: Optional continuation ID
        extra: Optional extra metadata (duration, tokens, etc.)
        tool_instance: Optional tool instance for accessing methods
        
    Returns:
        Dictionary containing UI summary data
    """
    try:
        # Get thinking mode
        thinking_mode_res = None
        if tool_instance and hasattr(tool_instance, 'get_request_thinking_mode'):
            try:
                thinking_mode_res = tool_instance.get_request_thinking_mode(request)
            except Exception:
                thinking_mode_res = getattr(request, 'thinking_mode', None)
        else:
            thinking_mode_res = getattr(request, 'thinking_mode', None)
            
        # Get websearch setting
        use_ws_res = False
        if tool_instance and hasattr(tool_instance, 'get_request_use_websearch'):
            try:
                use_ws_res = bool(tool_instance.get_request_use_websearch(request))
            except Exception:
                use_ws_res = bool(getattr(request, 'use_websearch', False))
        else:
            use_ws_res = bool(getattr(request, 'use_websearch', False))
            
        # Get model name
        model_name = None
        if tool_instance:
            try:
                if isinstance(getattr(tool_instance, 'stored_request_params', None), dict):
                    model_name = tool_instance.stored_request_params.get('model')
            except Exception:
                pass
        if not model_name:
            model_name = getattr(request, 'model', None)
            
        # Get expert mode setting
        expert_mode = None
        if tool_instance and hasattr(tool_instance, 'get_request_use_assistant_model') and request is not None:
            try:
                expert_mode = bool(tool_instance.get_request_use_assistant_model(request))
            except Exception:
                pass
                
        return {
            "step": getattr(request, 'step', ''),
            "step_number": getattr(request, 'step_number', 1),
            "total_steps": getattr(request, 'total_steps', 1),
            "findings": getattr(request, 'findings', ''),
            "thinking_mode": thinking_mode_res,
            "use_websearch": use_ws_res,
            "focus_areas": getattr(request, 'focus_areas', None) or ["general"],
            "prompt": getattr(request, 'step', ''),
            "output": {
                "summary_bullets": ui_summarize_text(assistant_response),
                "raw": assistant_response or "",
            },
            "tool": tool_instance.get_name() if tool_instance and hasattr(tool_instance, 'get_name') else "thinkdeep",
            "duration_secs": (extra or {}).get("duration_secs"),
            "model": model_name or (extra or {}).get("model_name"),
            "tokens": (extra or {}).get("tokens"),
            "conversation_id": (extra or {}).get("conversation_id") or continuation_id_val,
            "expert_mode": expert_mode,
        }
    except Exception:
        return {}


__all__ = ["ui_summarize_text", "ui_build_summary"]

