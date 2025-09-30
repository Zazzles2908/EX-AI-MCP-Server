"""
Request Accessor Mixin for Workflow Tools

This module provides request field extraction and validation methods for workflow tools.
These are pure getter methods with minimal dependencies, providing a foundation for
other workflow modules.

Key Features:
- Request field extraction with safe fallbacks
- Temperature and model settings validation
- Confidence and status accessors
- File context accessors
- Completion message generation
"""

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


class RequestAccessorMixin:
    """
    Mixin providing request field accessors for workflow tools.
    
    This class contains pure getter methods that extract fields from request objects
    with safe fallbacks. These methods can be overridden by subclasses for custom
    field mapping.
    """
    
    # ================================================================================
    # Temperature and Model Settings
    # ================================================================================
    
    def get_request_temperature(self, request) -> float:
        """Get temperature from request. Override for custom temperature handling."""
        try:
            return request.temperature if request.temperature is not None else self.get_default_temperature()
        except AttributeError:
            return self.get_default_temperature()
    
    def get_validated_temperature(self, request, model_context: Any) -> tuple[float, list[str]]:
        """
        Get temperature from request and validate it against model constraints.
        
        This is a convenience method that combines temperature extraction and validation
        for workflow tools. It ensures temperature is within valid range for the model.
        
        Args:
            request: The request object containing temperature
            model_context: Model context object containing model info
        
        Returns:
            Tuple of (validated_temperature, warning_messages)
        """
        temperature = self.get_request_temperature(request)
        return self.validate_and_correct_temperature(temperature, model_context)
    
    def get_request_thinking_mode(self, request) -> str:
        """Get thinking mode from request. Override for custom thinking mode handling."""
        try:
            return request.thinking_mode if request.thinking_mode is not None else self.get_expert_thinking_mode()
        except AttributeError:
            return self.get_expert_thinking_mode()
    
    def get_request_use_websearch(self, request) -> bool:
        """Get use_websearch from request. Override for custom websearch handling."""
        try:
            return request.use_websearch if request.use_websearch is not None else True
        except AttributeError:
            return True
    
    def get_request_use_assistant_model(self, request) -> bool:
        """
        Get use_assistant_model from request. Override for custom assistant model handling.
        
        Args:
            request: Current request object
        
        Returns:
            True if assistant model should be used, False otherwise
        """
        try:
            if request.use_assistant_model is not None:
                return request.use_assistant_model
        except AttributeError:
            pass
        # Allow environment default override to make tools fast-by-default when desired
        import os as _os
        env = (_os.getenv("DEFAULT_USE_ASSISTANT_MODEL") or "").strip().lower()
        if env in ("false", "0", "no", "off"):
            return False
        return True
    
    def get_request_model_name(self, request: Any) -> str:
        """Get model name from request. Avoid misleading defaults like 'flash'."""
        try:
            m = getattr(request, "model", None)
            if m and isinstance(m, str) and m.strip():
                return m
        except Exception:
            pass
        # Fall back to configured DEFAULT_MODEL; let callers handle 'auto' if needed
        from config import DEFAULT_MODEL
        return DEFAULT_MODEL
    
    # ================================================================================
    # Request Data Extraction
    # ================================================================================
    
    def get_request_confidence(self, request: Any) -> str:
        """Get confidence from request. Override for custom confidence handling."""
        try:
            return request.confidence or "low"
        except AttributeError:
            return "low"
    
    def get_request_relevant_context(self, request: Any) -> list[str]:
        """Get relevant context from request. Override for custom field mapping."""
        try:
            return request.relevant_context or []
        except AttributeError:
            return []
    
    def get_request_issues_found(self, request: Any) -> list[str]:
        """Get issues found from request. Override for custom field mapping."""
        try:
            return request.issues_found or []
        except AttributeError:
            return []
    
    def get_request_hypothesis(self, request: Any) -> Optional[str]:
        """Get hypothesis from request. Override for custom field mapping."""
        try:
            return request.hypothesis
        except AttributeError:
            return None
    
    def get_request_images(self, request: Any) -> list[str]:
        """Get images from request. Override for custom field mapping."""
        try:
            return request.images or []
        except AttributeError:
            return []
    
    # ================================================================================
    # Workflow Step Accessors
    # ================================================================================
    
    def get_request_continuation_id(self, request: Any) -> Optional[str]:
        """Get continuation ID from request. Override for custom continuation handling."""
        try:
            return request.continuation_id
        except AttributeError:
            return None
    
    def get_request_next_step_required(self, request: Any) -> bool:
        """Get next step required from request. Override for custom step handling."""
        try:
            return request.next_step_required
        except AttributeError:
            return True
    
    def get_request_step_number(self, request: Any) -> int:
        """Get step number from request. Override for custom step handling."""
        try:
            return request.step_number or 1
        except AttributeError:
            return 1
    
    def get_request_relevant_files(self, request: Any) -> list[str]:
        """Get relevant files from request. Override for custom file handling."""
        try:
            return request.relevant_files or []
        except AttributeError:
            return []
    
    def get_request_files_checked(self, request: Any) -> list[str]:
        """Get files checked from request. Override for custom file handling."""
        try:
            return request.files_checked or []
        except AttributeError:
            return []
    
    def get_backtrack_step(self, request) -> Optional[int]:
        """Get backtrack step from request. Override for custom backtrack handling."""
        try:
            return request.backtrack_from_step
        except AttributeError:
            return None
    
    # ================================================================================
    # File Context Accessors
    # ================================================================================
    
    def get_embedded_file_content(self) -> str:
        """Get embedded file content. Returns empty string if not available."""
        try:
            return self._embedded_file_content or ""  # type: ignore
        except AttributeError:
            return ""
    
    def get_file_reference_note(self) -> str:
        """Get file reference note. Returns empty string if not available."""
        try:
            return self._file_reference_note or ""  # type: ignore
        except AttributeError:
            return ""
    
    def get_actually_processed_files(self) -> list[str]:
        """Get list of actually processed files. Returns empty list if not available."""
        try:
            return self._actually_processed_files or []  # type: ignore
        except AttributeError:
            return []
    
    def get_current_model_context(self):
        """Get current model context. Returns None if not available."""
        try:
            return self._model_context  # type: ignore
        except AttributeError:
            return None
    
    def get_current_arguments(self) -> dict[str, Any]:
        """Get current arguments. Returns empty dict if not available."""
        try:
            return self._current_arguments or {}  # type: ignore
        except AttributeError:
            return {}
    
    # ================================================================================
    # Initial Request Handling
    # ================================================================================
    
    def store_initial_issue(self, step_description: str):
        """Store initial issue description. Override for custom storage."""
        # Default implementation - tools can override to store differently
        self.initial_issue = step_description  # type: ignore
    
    def get_initial_request(self, fallback_step: str) -> str:
        """Get initial request description. Override for custom retrieval."""
        try:
            return self.initial_request or fallback_step  # type: ignore
        except AttributeError:
            return fallback_step
    
    # ================================================================================
    # Completion and Status Methods
    # ================================================================================
    
    def prepare_work_summary(self) -> str:
        """Prepare work summary. Override for custom implementation."""
        try:
            return f"Completed {len(self.consolidated_findings.findings)} work steps"  # type: ignore
        except AttributeError:
            return "Work completed"
    
    def get_completion_status(self) -> str:
        """Get completion status. Override for tool-specific status."""
        return "high_confidence_completion"
    
    def get_final_analysis_from_request(self, request):
        """Extract final analysis from request. Override for tool-specific fields."""
        return self.get_request_hypothesis(request)
    
    def get_confidence_level(self, request) -> str:
        """Get confidence level. Override for tool-specific confidence handling."""
        return self.get_request_confidence(request) or "high"
    
    def get_completion_message(self) -> str:
        """Get completion message. Override for tool-specific messaging."""
        return (
            f"{self.get_name().capitalize()} complete with high confidence. Present results "
            "and proceed with implementation without requiring further consultation."
        )
    
    def get_skip_reason(self) -> str:
        """Get reason for skipping expert analysis. Override for tool-specific reasons."""
        return f"{self.get_name()} completed with sufficient confidence"
    
    def get_skip_expert_analysis_status(self) -> str:
        """Get status for skipped expert analysis. Override for tool-specific status."""
        return "skipped_by_tool_design"
    
    def get_step_guidance_message(self, request) -> str:
        """
        Get step guidance message. Override for tool-specific guidance.
        Default implementation uses required actions.
        """
        required_actions = self.get_required_actions(
            request.step_number, self.get_request_confidence(request), request.findings, request.total_steps
        )

        next_step_number = request.step_number + 1
        return (
            f"MANDATORY: DO NOT call the {self.get_name()} tool again immediately. "
            f"You MUST first work using appropriate tools. "
            f"REQUIRED ACTIONS before calling {self.get_name()} step {next_step_number}:\n"
            + "\n".join(f"{i + 1}. {action}" for i, action in enumerate(required_actions))
            + f"\n\nOnly call {self.get_name()} again with step_number: {next_step_number} "
            f"AFTER completing this work."
        )

    def get_completion_next_steps_message(self, expert_analysis_used: bool = False) -> str:
        """
        Get the message to show when work is complete.
        Tools can override for custom messaging.

        Args:
            expert_analysis_used: True if expert analysis was successfully executed
        """
        base_message = (
            f"{self.get_name().upper()} IS COMPLETE. You MUST now summarize and present ALL key findings, confirmed "
            "hypotheses, and exact recommended solutions. Clearly identify the most likely root cause and "
            "provide concrete, actionable implementation guidance. Highlight affected code paths and display "
            "reasoning that led to this conclusion—make it easy for a developer to understand exactly where "
            "the problem lies."
        )

        # Add expert analysis guidance only when expert analysis was actually used
        if expert_analysis_used:
            expert_guidance = self.get_expert_analysis_guidance()
            if expert_guidance:
                return f"{base_message}\n\n{expert_guidance}"

        return base_message

    def get_expert_analysis_guidance(self) -> str:
        """
        Get additional guidance for handling expert analysis results.

        Subclasses can override this to provide specific instructions about how
        to validate and use expert analysis findings. Returns empty string by default.

        When expert analysis is called, this guidance will be:
        1. Appended to the completion next steps message
        2. Added as "important_considerations" field in the response data

        Example implementation:
        ```python
        def get_expert_analysis_guidance(self) -> str:
            return (
                "IMPORTANT: Expert analysis provided above. You MUST validate "
                "the expert findings rather than accepting them blindly. "
                "Cross-reference with your own investigation and ensure "
                "recommendations align with the codebase context."
            )
        ```

        Returns:
            Additional guidance text or empty string if no guidance needed
        """
        return ""

    # ================================================================================
    # Response Customization
    # ================================================================================

    def customize_workflow_response(self, response_data: dict, request) -> dict:
        """
        Allow tools to customize the workflow response before returning.

        Tools can override this to add tool-specific fields, modify status names,
        customize field mapping, etc. Default implementation returns unchanged.
        """
        # Ensure file context information is preserved in all response paths
        if not response_data.get("file_context"):
            embedded_content = self.get_embedded_file_content()
            reference_note = self.get_file_reference_note()
            processed_files = self.get_actually_processed_files()

            # Prioritize embedded content over references for final steps
            if embedded_content:
                response_data["file_context"] = {
                    "type": "fully_embedded",
                    "files_embedded": len(processed_files),
                    "context_optimization": "Full file content embedded for expert analysis",
                }
            elif reference_note:
                response_data["file_context"] = {
                    "type": "reference_only",
                    "note": reference_note,
                    "context_optimization": "Files referenced but not embedded to preserve Claude's context window",
                }

        return response_data

