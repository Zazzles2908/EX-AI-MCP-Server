"""
Request Handler Execution Module

This module handles tool execution orchestration including:
- Tool execution with model context
- Kimi multi-file chat with GLM fallback
- Result normalization
- File size validation
- Model context creation
- Optional features (date injection, smart websearch, client defaults)
"""

import logging
import os
import datetime
import re
from typing import Any, Dict, Callable, Optional
from mcp.types import TextContent

logger = logging.getLogger(__name__)


def create_model_context(model_name: str, model_option: Optional[str] = None):
    """
    Create model context with resolved model and option.
    
    Args:
        model_name: Resolved model name
        model_option: Optional model option (e.g., "web_search")
        
    Returns:
        ModelContext object
    """
    from utils.model_context import ModelContext
    
    model_context = ModelContext(model_name, model_option)
    logger.debug(
        f"Model context created for {model_name} with {model_context.capabilities.context_window} token capacity"
    )
    if model_option:
        logger.debug(f"Model option stored in context: '{model_option}'")
    
    return model_context


def validate_file_sizes(arguments: Dict[str, Any], model_name: str, env_true_func) -> Optional[Dict]:
    """
    Validate file sizes before tool execution.
    
    Args:
        arguments: Tool arguments (may contain files)
        model_name: Resolved model name
        env_true_func: Function to check environment variables
        
    Returns:
        Error dict if validation fails, None if successful
    """
    if "files" not in arguments or not arguments["files"]:
        return None
    
    logger.debug(f"Checking file sizes for {len(arguments['files'])} files with model {model_name}")
    
    if env_true_func("STRICT_FILE_SIZE_REJECTION", "false"):
        from utils.file_utils import check_total_file_size
        file_size_check = check_total_file_size(arguments["files"], model_name)
        if file_size_check:
            logger.warning(f"File size check failed with model {model_name}")
            return file_size_check
    
    return None


def inject_optional_features(arguments: Dict[str, Any], tool_name: str, env_true_func, os_module=os) -> Dict[str, Any]:
    """
    Inject optional features like date, websearch, and client-aware defaults.
    
    Args:
        arguments: Tool arguments
        tool_name: Tool name
        env_true_func: Function to check environment variables
        os_module: OS module (for testing)
        
    Returns:
        Updated arguments
    """
    # Optional date injection for temporal awareness
    try:
        if env_true_func("INJECT_CURRENT_DATE", "true"):
            fmt = os_module.getenv("DATE_FORMAT", "%Y-%m-%d")
            today = datetime.datetime.now().strftime(fmt)
            arguments["_today"] = today
    except Exception:
        pass
    
    # Smart websearch (thinkdeep) - conservative, default off
    try:
        if tool_name == "thinkdeep":
            if "use_websearch" not in arguments:
                if env_true_func("ENABLE_SMART_WEBSEARCH", "false"):
                    prompt_text = (arguments.get("prompt") or arguments.get("_original_user_prompt") or "")
                    lowered = prompt_text.lower()
                    recent_date = re.search(r"\b20\d{2}-\d{2}-\d{2}\b", lowered)  # YYYY-MM-DD
                    triggers = [
                        "today", "now", "this week", "as of", "release notes", "changelog",
                    ]
                    if (
                        any(t in lowered for t in triggers)
                        or recent_date
                        or re.search(r"cve-\d{4}-\d+", lowered)
                    ):
                        arguments["use_websearch"] = True
                        logger.debug("[SMART_WEBSEARCH] enabled for thinkdeep due to time-sensitive cues")
    except Exception:
        pass
    
    # Client-aware defaults (generic profile with legacy Claude fallback)
    try:
        from utils.client_info import get_client_info_from_context
        try:
            import server as _srv  # lazy import to avoid circulars during module import
        except Exception:
            _srv = None  # type: ignore
        ci = get_client_info_from_context(_srv) or {}
        # Generic env first, then legacy Claude-specific variables
        if env_true_func("CLIENT_DEFAULTS_USE_WEBSEARCH", os_module.getenv("CLAUDE_DEFAULTS_USE_WEBSEARCH", "false")):
            if "use_websearch" not in arguments:
                arguments["use_websearch"] = True
        if tool_name == "thinkdeep" and "thinking_mode" not in arguments:
            default_thinking = (os_module.getenv("CLIENT_DEFAULT_THINKING_MODE") or os_module.getenv("CLAUDE_DEFAULT_THINKING_MODE", "medium")).strip().lower()
            arguments["thinking_mode"] = default_thinking
    except Exception:
        pass
    
    return arguments


async def execute_tool_with_fallback(
    tool,
    tool_name: str,
    arguments: Dict[str, Any],
    tool_map: Dict[str, Any],
    execute_with_monitor_func: Callable,
    req_id: str
) -> list:
    """
    Execute Kimi tool with GLM fallback on structured failure.
    
    Args:
        tool: Tool object to execute
        tool_name: Tool name
        arguments: Tool arguments
        tool_map: Dictionary of available tools
        execute_with_monitor_func: Function to execute with monitoring
        req_id: Request ID for logging
        
    Returns:
        List of TextContent results
    """
    if tool_name == "kimi_multi_file_chat":
        # Safety-net: try Kimi first, then fallback to GLM multi-file chat on structured failure
        try:
            logging.getLogger("mcp_activity").info({
                "event": "route_diagnostics",
                "tool": tool_name,
                "req_id": req_id,
                "path": "non_model_dispatch",
                "note": "manager dispatcher engaged; invoking safety-net orchestrator"
            })
        except Exception:
            pass
        
        # Attempt 1: Kimi
        result = await execute_with_monitor_func(lambda: tool.execute(arguments))
        
        # Inspect result for structured execution_error to trigger fallback
        try:
            import json as _json
            last = result[-1] if isinstance(result, list) and result else None
            payload = None
            if isinstance(last, TextContent) and last.type == "text" and last.text:
                try:
                    payload = _json.loads(last.text)
                except Exception:
                    payload = None
            if isinstance(payload, dict) and str(payload.get("status", "")).lower() == "execution_error":
                # Attempt 2: GLM multi-file chat
                try:
                    logging.getLogger("mcp_activity").info("[FALLBACK] switching to glm_multi_file_chat after kimi failure")
                except Exception:
                    pass
                glm_tool = tool_map.get("glm_multi_file_chat")
                if glm_tool is not None:
                    alt = await execute_with_monitor_func(lambda: glm_tool.execute(arguments))
                    return alt
        except Exception:
            pass
        
        return result
    else:
        # Standard execution
        result = await execute_with_monitor_func(lambda: tool.execute(arguments))
        return result


def normalize_result(result: Any) -> list:
    """
    Normalize result shape to list[TextContent].
    
    Args:
        result: Raw result from tool execution
        
    Returns:
        Normalized list of TextContent
    """
    if isinstance(result, TextContent):
        return [result]
    elif not isinstance(result, list):
        return [TextContent(type="text", text=str(result))]
    return result


async def execute_tool_without_model(
    tool,
    tool_name: str,
    arguments: Dict[str, Any],
    execute_with_monitor_func: Callable,
    req_id: str,
    evt: Any = None
) -> list:
    """
    Execute tool directly without model context (for tools that don't require models).
    
    Args:
        tool: Tool object to execute
        tool_name: Tool name
        arguments: Tool arguments
        execute_with_monitor_func: Function to execute with monitoring
        req_id: Request ID for logging
        evt: Optional event object for telemetry
        
    Returns:
        List of TextContent results
    """
    logger.debug(f"Tool {tool_name} doesn't require model resolution - skipping model validation")
    
    # Update route_plan path for non-model-dispatch tools
    try:
        if evt:
            _rp = dict(evt.args.get("route_plan") or {})
            _rp["path"] = "non_model_dispatch"
            evt.args["route_plan"] = _rp
    except Exception:
        pass
    
    try:
        if tool_name == "kimi_multi_file_chat":
            # All file_chat requests must pass through fallback orchestrator
            try:
                logging.getLogger("mcp_activity").info({
                    "event": "route_diagnostics",
                    "tool": tool_name,
                    "req_id": req_id,
                    "path": "non_model_dispatch",
                    "note": "manager dispatcher engaged; invoking safety-net orchestrator"
                })
            except Exception:
                pass
            try:
                logging.getLogger("mcp_activity").info("[FALLBACK] orchestrator route engaged for multi-file chat")
            except Exception:
                pass
            return await execute_with_monitor_func(lambda: tool.execute(arguments))
        else:
            return await execute_with_monitor_func(lambda: tool.execute(arguments))
    except Exception as e:
        # Graceful error normalization for invalid arguments and runtime errors
        try:
            from pydantic import ValidationError as _ValidationError
        except Exception:
            _ValidationError = None  # type: ignore
        import json as _json
        if _ValidationError and isinstance(e, _ValidationError):
            err = {
                "status": "invalid_request",
                "error": "Invalid arguments for tool",
                "details": str(e),
                "tool": tool_name,
            }
            logger.warning("Tool %s argument validation failed: %s", tool_name, e)
            return [TextContent(type="text", text=_json.dumps(err))]
        logger.error("Tool %s execution failed: %s", tool_name, e, exc_info=True)
        err = {
            "status": "execution_error",
            "error": str(e),
            "tool": tool_name,
        }
        return [TextContent(type="text", text=_json.dumps(err))]


# Export public API
__all__ = [
    'create_model_context',
    'validate_file_sizes',
    'inject_optional_features',
    'execute_tool_with_fallback',
    'normalize_result',
    'execute_tool_without_model',
]

