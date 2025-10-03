from __future__ import annotations

from typing import Any, Dict, Optional


# Common error suggestions for better UX
ERROR_SUGGESTIONS = {
    "missing_required_parameter": {
        "chat": "The 'prompt' parameter is required. Example: {\"prompt\": \"Your question here\"}",
        "thinkdeep": "The 'step' parameter is required. Example: {\"step\": \"Describe what you're investigating\", \"step_number\": 1, \"total_steps\": 3, \"next_step_required\": true, \"findings\": \"Initial observations\"}",
        "debug": "The 'step' parameter is required. Example: {\"step\": \"Describe the issue to debug\", \"step_number\": 1, \"total_steps\": 3, \"next_step_required\": true, \"findings\": \"Initial investigation\"}",
        "analyze": "The 'step' parameter is required. Example: {\"step\": \"What to analyze\", \"step_number\": 1, \"total_steps\": 2, \"next_step_required\": true, \"findings\": \"Initial assessment\"}",
    },
    "invalid_parameter": {
        "thinkdeep": "Did you mean 'step' instead of 'prompt'? Thinkdeep uses 'step' for investigation steps.",
        "debug": "Did you mean 'step' instead of 'prompt'? Debug uses 'step' for investigation steps.",
        "chat": "Did you mean 'prompt' instead of 'step'? Chat uses 'prompt' for questions.",
    },
    "model_not_found": "The specified model is not available. Use 'listmodels_EXAI-WS' to see available models, or use 'auto' to let the system choose the best model.",
    "web_search_failed": "Web search failed. This might be due to: 1) Network issues, 2) Search backend unavailable, 3) Invalid query. Try rephrasing your query or disable web search with use_websearch=false.",
    "file_not_found": "File not found. Make sure to use absolute paths (e.g., 'c:\\\\Project\\\\file.py') and verify the file exists.",
    "continuation_not_found": "Continuation ID not found or expired. Start a new conversation without continuation_id.",
}


def get_helpful_suggestion(error_type: str, tool: str, error_msg: str) -> Optional[str]:
    """
    Generate helpful suggestions based on error type and context.

    Args:
        error_type: Type of error (e.g., 'missing_required_parameter')
        tool: Tool name where error occurred
        error_msg: Original error message

    Returns:
        Helpful suggestion string or None
    """
    # Check for specific tool suggestions
    if error_type in ERROR_SUGGESTIONS:
        suggestions = ERROR_SUGGESTIONS[error_type]
        if isinstance(suggestions, dict) and tool in suggestions:
            return suggestions[tool]
        elif isinstance(suggestions, str):
            return suggestions

    # Check for parameter confusion
    if "prompt" in error_msg.lower() and tool in ["thinkdeep", "debug", "analyze"]:
        return ERROR_SUGGESTIONS["invalid_parameter"].get(tool)
    elif "step" in error_msg.lower() and tool == "chat":
        return ERROR_SUGGESTIONS["invalid_parameter"].get("chat")

    # Check for common error patterns
    if "model" in error_msg.lower() and "not found" in error_msg.lower():
        return ERROR_SUGGESTIONS["model_not_found"]
    elif "file" in error_msg.lower() and "not found" in error_msg.lower():
        return ERROR_SUGGESTIONS["file_not_found"]
    elif "continuation" in error_msg.lower():
        return ERROR_SUGGESTIONS["continuation_not_found"]

    return None


def make_error_envelope(provider: str, tool: str, error: BaseException | str, detail: str | None = None, error_type: str | None = None) -> Dict[str, Any]:
    """Create a standardized error envelope for tool failures with helpful suggestions.

    Shape:
      {
        "status": "execution_error",
        "error_class": "<exception-lower>" | "error",
        "provider": "KIMI|GLM|unknown",
        "tool": "<tool_name>",
        "detail": "<string>",
        "suggestion": "<helpful guidance>" (optional)
      }

    Args:
        provider: Provider name (KIMI, GLM, etc.)
        tool: Tool name where error occurred
        error: Exception or error message
        detail: Additional detail (optional)
        error_type: Type of error for suggestion lookup (optional)
    """
    if isinstance(error, BaseException):
        cls = type(error).__name__.lower()
        msg = str(error)
    else:
        cls = "error"
        msg = str(error)
    if detail:
        msg = f"{msg}"

    # Generate helpful suggestion
    suggestion = get_helpful_suggestion(error_type or cls, tool, msg)

    envelope = {
        "status": "execution_error",
        "error_class": cls,
        "provider": provider or "unknown",
        "tool": tool or "unknown",
        # Provide both keys for backward/forward compatibility across tools
        "error": msg,
        "detail": msg,
    }

    # Add suggestion if available
    if suggestion:
        envelope["suggestion"] = suggestion
        envelope["detail"] = f"{msg}\n\n💡 Suggestion: {suggestion}"

    return envelope

