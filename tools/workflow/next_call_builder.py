"""
Next Call Builder Module

This module handles building the next_call structure for workflow tool responses.
Separated from orchestration.py to keep components focused and maintainable.

Purpose:
- Build complete next_call.arguments with ALL required fields
- Prevent validation errors when post-processing auto-continues workflows
- Make it easy to extend or customize next_call building logic

Design:
- Single responsibility: build next_call structures
- Easy to test in isolation
- Easy to extend for tool-specific customization
"""

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class NextCallBuilder:
    """
    Builds next_call structures for workflow tool responses.
    
    The next_call structure tells clients and post-processing handlers
    how to continue the workflow with the next step.
    """
    
    @staticmethod
    def build_next_call(
        tool_name: str,
        request: Any,
        continuation_id: Optional[str] = None,
        include_all_fields: bool = True
    ) -> Dict[str, Any]:
        """
        Build a complete next_call structure with all required fields.
        
        Args:
            tool_name: Name of the workflow tool
            request: The workflow request object (validated Pydantic model)
            continuation_id: Optional continuation ID for multi-turn workflows
            include_all_fields: If True, include ALL fields from request (recommended)
                               If False, only include minimal fields (legacy behavior)
        
        Returns:
            Dictionary with 'tool' and 'arguments' keys
        
        Example:
            {
                "tool": "analyze",
                "arguments": {
                    "step": "Continue analysis...",
                    "step_number": 2,
                    "total_steps": 3,
                    "next_step_required": True,
                    "findings": "Previous findings...",
                    "relevant_files": [...],
                    "continuation_id": "abc123",
                    "model": "glm-4.5-flash"
                }
            }
        """
        if include_all_fields:
            # Build complete arguments with ALL fields from request
            # This prevents validation errors when post-processing auto-continues
            next_args = NextCallBuilder._build_complete_arguments(request, continuation_id)
        else:
            # Legacy behavior: only include minimal fields
            # WARNING: This can cause validation errors if required fields are missing
            next_args = NextCallBuilder._build_minimal_arguments(request, continuation_id)
        
        return {
            "tool": tool_name,
            "arguments": next_args
        }
    
    @staticmethod
    def _build_complete_arguments(request: Any, continuation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Build complete arguments including ALL fields from the request.
        
        This ensures that when post-processing auto-continues the workflow,
        all required fields are present and validation succeeds.
        
        Args:
            request: The workflow request object
            continuation_id: Optional continuation ID
        
        Returns:
            Complete arguments dictionary
        """
        # Start with all fields from the request
        # Use model_dump() if available (Pydantic v2), otherwise dict()
        if hasattr(request, 'model_dump'):
            next_args = request.model_dump(exclude_none=True, exclude_unset=False)
        elif hasattr(request, 'dict'):
            next_args = request.dict(exclude_none=True, exclude_unset=False)
        else:
            # Fallback: manually extract fields
            next_args = {}
            for field_name in dir(request):
                if not field_name.startswith('_') and not callable(getattr(request, field_name, None)):
                    try:
                        value = getattr(request, field_name, None)
                        if value is not None:
                            next_args[field_name] = value
                    except Exception:
                        pass
        
        # Filter out internal/private fields that shouldn't be in next_call
        internal_fields = {
            '_model_context', '_resolved_model_name', '_session_id', 
            '_call_key', '_today', '_remaining_tokens', '_original_user_prompt',
            '_cached_summary', '_cached_files'
        }
        next_args = {k: v for k, v in next_args.items() if k not in internal_fields}
        
        # Add/override continuation_id if provided
        if continuation_id:
            next_args['continuation_id'] = continuation_id
        
        # Ensure model is present (required for execution)
        if 'model' not in next_args or not next_args['model']:
            next_args['model'] = 'auto'
        
        logger.debug(f"Built complete next_call arguments with {len(next_args)} fields: {list(next_args.keys())}")
        
        return next_args
    
    @staticmethod
    def _build_minimal_arguments(request: Any, continuation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Build minimal arguments (legacy behavior).
        
        WARNING: This only includes 4 core fields and can cause validation errors
        if the workflow tool requires additional fields like 'findings'.
        
        This is kept for backward compatibility but is NOT recommended.
        
        Args:
            request: The workflow request object
            continuation_id: Optional continuation ID
        
        Returns:
            Minimal arguments dictionary
        """
        next_args = {
            "step": getattr(request, "step", None),
            "step_number": getattr(request, "step_number", None),
            "total_steps": getattr(request, "total_steps", None),
            "next_step_required": getattr(request, "next_step_required", None),
        }
        
        if continuation_id:
            next_args["continuation_id"] = continuation_id
        
        logger.warning(
            "Using minimal next_call arguments (legacy mode). "
            "This may cause validation errors. Consider using include_all_fields=True."
        )
        
        return next_args
    
    @staticmethod
    def build_pause_next_call(
        tool_name: str,
        request: Any,
        next_step_number: int,
        continuation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Build next_call for pause_for_* responses.
        
        This is used when the workflow needs to pause and wait for the user
        to complete required actions before continuing.
        
        Args:
            tool_name: Name of the workflow tool
            request: The workflow request object
            next_step_number: The step number for the next call
            continuation_id: Optional continuation ID
        
        Returns:
            Dictionary with 'tool' and 'arguments' keys
        """
        # Build complete arguments first
        next_args = NextCallBuilder._build_complete_arguments(request, continuation_id)
        
        # Override step-related fields for the next step
        next_args['step'] = f"Continue with step {next_step_number} as per required actions."
        next_args['step_number'] = next_step_number
        
        # Ensure findings is present (required field for most workflow tools)
        if 'findings' not in next_args or not next_args['findings']:
            next_args['findings'] = "Summarize new insights and evidence from the required actions."
        
        return {
            "tool": tool_name,
            "arguments": next_args
        }


# Export public API
__all__ = ['NextCallBuilder']

