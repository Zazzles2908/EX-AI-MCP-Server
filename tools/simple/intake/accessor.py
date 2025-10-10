"""
Request Accessor for SimpleTool

This module provides safe request field access for SimpleTool.
Extracted from tools/simple/base.py as part of Phase 2 Cleanup refactoring.

All methods use try/except to safely handle missing attributes,
returning sensible defaults when fields don't exist on the request object.
"""

from typing import Optional


class RequestAccessor:
    """
    Safe request field access for SimpleTool.
    
    This class provides static methods for extracting fields from request objects
    with proper error handling and default values. All methods follow the pattern:
    1. Try to access the attribute
    2. Return a sensible default if attribute doesn't exist
    3. Never raise exceptions for missing fields
    """
    
    @staticmethod
    def get_model_name(request) -> Optional[str]:
        """
        Get model name from request.
        
        Args:
            request: The request object
            
        Returns:
            Model name if present, None otherwise
        """
        try:
            return request.model
        except AttributeError:
            return None
    
    @staticmethod
    def get_images(request) -> list:
        """
        Get images from request.
        
        Args:
            request: The request object
            
        Returns:
            List of image paths/URLs, empty list if not present
        """
        try:
            return request.images if request.images is not None else []
        except AttributeError:
            return []
    
    @staticmethod
    def get_continuation_id(request) -> Optional[str]:
        """
        Get continuation_id from request.
        
        Args:
            request: The request object
            
        Returns:
            Continuation ID if present, None otherwise
        """
        try:
            return request.continuation_id
        except AttributeError:
            return None
    
    @staticmethod
    def get_prompt(request) -> str:
        """
        Get prompt from request.
        
        Args:
            request: The request object
            
        Returns:
            Prompt string, empty string if not present
        """
        try:
            return request.prompt
        except AttributeError:
            return ""
    
    @staticmethod
    def get_temperature(request) -> Optional[float]:
        """
        Get temperature from request.
        
        Args:
            request: The request object
            
        Returns:
            Temperature value if present, None otherwise
        """
        try:
            return request.temperature
        except AttributeError:
            return None
    
    @staticmethod
    def get_thinking_mode(request) -> Optional[str]:
        """
        Get thinking_mode from request.
        
        Args:
            request: The request object
            
        Returns:
            Thinking mode if present, None otherwise
        """
        try:
            return request.thinking_mode
        except AttributeError:
            return None
    
    @staticmethod
    def get_files(request) -> list:
        """
        Get files from request.
        
        Args:
            request: The request object
            
        Returns:
            List of file paths, empty list if not present
        """
        try:
            return request.files if request.files is not None else []
        except AttributeError:
            return []
    
    @staticmethod
    def get_use_websearch(request) -> bool:
        """
        Get use_websearch from request, falling back to env default.
        
        EX_WEBSEARCH_DEFAULT_ON controls default when request doesn't specify.
        
        Args:
            request: The request object
            
        Returns:
            True if websearch should be used, False otherwise
        """
        try:
            val = getattr(request, "use_websearch", None)
            if val is not None:
                return bool(val)
            import os as __os
            return __os.getenv("EX_WEBSEARCH_DEFAULT_ON", "true").strip().lower() == "true"
        except AttributeError:
            return True
    
    @staticmethod
    def get_as_dict(request) -> dict:
        """
        Convert request to dictionary.
        
        Tries Pydantic v2 model_dump(), falls back to v1 dict(),
        and finally creates a minimal dict with just the prompt.
        
        Args:
            request: The request object
            
        Returns:
            Dictionary representation of the request
        """
        try:
            # Try Pydantic v2 method first
            return request.model_dump()
        except AttributeError:
            try:
                # Fall back to Pydantic v1 method
                return request.dict()
            except AttributeError:
                # Last resort - convert to dict manually
                # Use the static method to get prompt safely
                return {"prompt": RequestAccessor.get_prompt(request)}

    @staticmethod
    def set_files(request, files: list) -> None:
        """
        Set files on request.

        Args:
            request: The request object
            files: List of file paths to set
        """
        try:
            request.files = files
        except AttributeError:
            # If request doesn't support file setting, ignore silently
            pass

