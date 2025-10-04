"""
Streaming Mixin for SimpleTool

Provides streaming support configuration functionality.
Extracted from tools/simple/base.py to improve maintainability.
"""

from typing import Dict, Any


class StreamingMixin:
    """
    Mixin providing streaming support configuration.

    This mixin handles:
    - Streaming enablement checks
    - Provider kwargs for streaming
    - Centralized streaming logic

    Dependencies:
    - No direct dependencies on BaseTool attributes
    - Self-contained functionality
    """

    def _build_streaming_kwargs(self, provider, tool_name: str) -> Dict[str, Any]:
        """
        Build provider kwargs for streaming if enabled.
        
        Args:
            provider: The provider instance
            tool_name: Name of the tool being executed
            
        Returns:
            Dictionary with streaming kwargs (may include 'stream': True)
        """
        kwargs = {}
        
        try:
            from src.providers.orchestration.streaming_flags import is_streaming_enabled
            
            provider_type = getattr(provider.get_provider_type(), "value", "")
            
            if is_streaming_enabled(provider_type, tool_name):
                kwargs["stream"] = True
                
        except Exception:
            # Silently fail if streaming check fails
            pass
            
        return kwargs

    def _is_streaming_enabled(self, provider_type: str, tool_name: str) -> bool:
        """
        Check if streaming is enabled for this provider and tool.
        
        Args:
            provider_type: Type of provider (e.g., 'kimi', 'glm')
            tool_name: Name of the tool being executed
            
        Returns:
            True if streaming is enabled, False otherwise
        """
        try:
            from src.providers.orchestration.streaming_flags import is_streaming_enabled
            return is_streaming_enabled(provider_type, tool_name)
        except Exception:
            return False

