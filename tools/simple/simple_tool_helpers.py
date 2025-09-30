"""
Request Accessor and Convenience Methods for Simple Tools

This module provides helper methods for SimpleTool that handle:
- Request field extraction (hook pattern for safe attribute access)
- Convenience methods for prompt building
- File validation and processing
- Websearch guidance generation
"""

import logging
import os
from typing import Any, Optional

logger = logging.getLogger(__name__)


class SimpleToolHelpersMixin:
    """
    Mixin providing request accessor and convenience methods for simple tools.
    
    This class handles:
    - Safe request field extraction using hook pattern
    - Prompt building utilities
    - File validation
    - Websearch guidance generation
    """
    
    # ================================================================================
    # Request Accessor Methods (Hook Pattern)
    # ================================================================================
    
    def get_request_model_name(self, request) -> Optional[str]:
        """Get model name from request. Override for custom model name handling."""
        try:
            return request.model
        except AttributeError:
            return None
    
    def get_request_images(self, request) -> list:
        """Get images from request. Override for custom image handling."""
        try:
            return request.images if request.images is not None else []
        except AttributeError:
            return []
    
    def get_request_continuation_id(self, request) -> Optional[str]:
        """Get continuation_id from request. Override for custom continuation handling."""
        try:
            return request.continuation_id
        except AttributeError:
            return None
    
    def get_request_prompt(self, request) -> str:
        """Get prompt from request. Override for custom prompt handling."""
        try:
            return request.prompt
        except AttributeError:
            return ""
    
    def get_request_temperature(self, request) -> Optional[float]:
        """Get temperature from request. Override for custom temperature handling."""
        try:
            return request.temperature
        except AttributeError:
            return None
    
    def get_validated_temperature(self, request, model_context: Any) -> tuple[float, list[str]]:
        """
        Get temperature from request and validate it against model constraints.
        
        This is a convenience method that combines temperature extraction and validation
        for simple tools. It ensures temperature is within valid range for the model.
        
        Args:
            request: The request object containing temperature
            model_context: Model context object containing model info
        
        Returns:
            Tuple of (validated_temperature, warning_messages)
        """
        temperature = self.get_request_temperature(request)
        if temperature is None:
            temperature = self.get_default_temperature()
        return self.validate_and_correct_temperature(temperature, model_context)
    
    def get_request_thinking_mode(self, request) -> Optional[str]:
        """Get thinking_mode from request. Override for custom thinking mode handling."""
        try:
            return request.thinking_mode
        except AttributeError:
            return None
    
    def get_request_files(self, request) -> list:
        """Get files from request. Override for custom file handling."""
        try:
            return request.files if request.files is not None else []
        except AttributeError:
            return []
    
    def get_request_use_websearch(self, request) -> bool:
        """Get use_websearch from request, falling back to env default.
        EX_WEBSEARCH_DEFAULT_ON controls default when request doesn't specify.
        """
        try:
            val = getattr(request, "use_websearch", None)
            if val is not None:
                return bool(val)
            return os.getenv("EX_WEBSEARCH_DEFAULT_ON", "true").strip().lower() == "true"
        except AttributeError:
            return True
    
    def get_request_as_dict(self, request) -> dict:
        """Convert request to dictionary. Override for custom serialization."""
        try:
            # Try Pydantic v2 method first
            return request.model_dump()
        except AttributeError:
            try:
                # Fall back to Pydantic v1 method
                return request.dict()
            except AttributeError:
                # Last resort - convert to dict manually
                return {"prompt": self.get_request_prompt(request)}
    
    def set_request_files(self, request, files: list) -> None:
        """Set files on request. Override for custom file setting."""
        try:
            request.files = files
        except AttributeError:
            # If request doesn't support file setting, ignore silently
            pass
    
    def get_actually_processed_files(self) -> list:
        """Get actually processed files. Override for custom file tracking."""
        try:
            return self._actually_processed_files
        except AttributeError:
            return []
    
    # ================================================================================
    # Convenience Methods for Prompt Building
    # ================================================================================
    
    def build_standard_prompt(
        self, system_prompt: str, user_content: str, request, file_context_title: str = "CONTEXT FILES"
    ) -> str:
        """
        Build a standard prompt with system prompt, file context, and user content.
        
        This is a convenience method that combines common prompt building patterns.
        It handles file embedding, conversation history, and proper formatting.
        
        Args:
            system_prompt: The system prompt for the AI
            user_content: The user's input content
            request: The request object
            file_context_title: Title for the file context section
        
        Returns:
            Complete formatted prompt
        """
        # Get files from request
        files = self.get_request_files(request)
        
        # Build file context if files are present
        file_context = ""
        if files:
            try:
                from utils.file_utils import embed_files_in_prompt
                file_context = embed_files_in_prompt(files, title=file_context_title)
            except Exception as e:
                logger.warning(f"Failed to embed files: {e}")
        
        # Combine system prompt, file context, and user content
        if file_context:
            return f"{system_prompt}\n\n{file_context}\n\n{user_content}"
        else:
            return f"{system_prompt}\n\n{user_content}"
    
    def get_prompt_content_for_size_validation(self, user_content: str) -> str:
        """
        Get the prompt content that should be validated for size limits.
        
        This method allows tools to specify which part of the prompt should be
        checked against MCP transport size limits. By default, returns the user
        content as-is.
        
        Override this if your tool needs custom size validation logic.
        
        Args:
            user_content: The user's input content
        
        Returns:
            Content to validate for size limits
        """
        return user_content
    
    def get_websearch_guidance(self) -> Optional[str]:
        """
        Get tool-specific websearch guidance.
        
        Override this to provide custom websearch instructions for your tool.
        Returns None by default (uses base tool's generic guidance).
        
        Returns:
            Tool-specific websearch guidance or None
        """
        return None
    
    def handle_prompt_file_with_fallback(self, request) -> str:
        """
        Handle prompt.txt file with fallback to request prompt.
        
        This method checks for a prompt.txt file in the request's files list
        and uses it as the prompt if found. Otherwise, falls back to the
        request's prompt field.
        
        Args:
            request: The request object
        
        Returns:
            Prompt content from file or request
        """
        try:
            files = self.get_request_files(request)
            if files:
                for file_path in files:
                    if file_path.endswith("prompt.txt"):
                        try:
                            with open(file_path, "r", encoding="utf-8") as f:
                                return f.read()
                        except Exception as e:
                            logger.warning(f"Failed to read prompt.txt: {e}")
        except Exception:
            pass
        
        # Fallback to request prompt
        return self.get_request_prompt(request)
    
    def get_chat_style_websearch_guidance(self) -> str:
        """
        Get chat-style websearch guidance for simple tools.
        
        This provides user-friendly websearch instructions for chat-like tools.
        
        Returns:
            Chat-style websearch guidance
        """
        return """
If you need current information or want to verify facts, you can request a web search.
Just ask me to search for specific information, and I'll help you find it."""
    
    def supports_custom_request_model(self) -> bool:
        """
        Check if this tool supports custom request models.
        
        Simple tools use the base ToolRequest by default, but can override
        get_request_model() to use custom models.
        
        Returns:
            True if tool uses custom request model
        """
        from tools.shared.base_models import ToolRequest
        return self.get_request_model() != ToolRequest
    
    def _validate_file_paths(self, request) -> Optional[str]:
        """
        Validate file paths for security.
        
        This prevents path traversal attacks and ensures proper access control.
        
        Args:
            request: The request object containing files
        
        Returns:
            Error message if validation fails, None otherwise
        """
        files = self.get_request_files(request)
        if not files:
            return None
        
        try:
            # Use base tool's file validation
            self.validate_file_paths(files)
            return None
        except ValueError as e:
            return str(e)
        except Exception as e:
            logger.error(f"File validation error: {e}")
            return f"File validation failed: {str(e)}"
    
    def prepare_chat_style_prompt(self, request, system_prompt: str = None) -> str:
        """
        Prepare a chat-style prompt with conversation-aware formatting.
        
        This method builds prompts suitable for chat-like interactions,
        handling file context and conversation history appropriately.
        
        Args:
            request: The request object
            system_prompt: Optional system prompt override
        
        Returns:
            Formatted chat-style prompt
        """
        if system_prompt is None:
            system_prompt = self.get_system_prompt()
        
        user_content = self.get_request_prompt(request)
        
        return self.build_standard_prompt(
            system_prompt=system_prompt,
            user_content=user_content,
            request=request,
            file_context_title="REFERENCE FILES"
        )

