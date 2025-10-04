"""
Web Search Mixin for SimpleTool

Provides web search instruction generation and guidance functionality.
Extracted from tools/simple/base.py to improve maintainability.
"""

from typing import Optional


class WebSearchMixin:
    """
    Mixin providing web search instruction generation and guidance.

    This mixin handles:
    - Web search instruction formatting
    - Tool-specific web search guidance
    - Chat-style web search guidance

    Dependencies:
    - Requires TOOL_NAME attribute from BaseTool
    - Requires TOOL_DESCRIPTION attribute from BaseTool
    - Requires TOOL_SCHEMA attribute from BaseTool
    """

    def get_websearch_instruction(self, use_websearch: bool, guidance: Optional[str]) -> str:
        """
        Generate web search instruction text.
        
        Args:
            use_websearch: Whether web search is enabled
            guidance: Optional tool-specific guidance text
            
        Returns:
            Formatted web search instruction or empty string
        """
        if not use_websearch:
            return ""
            
        instruction = "\n\n=== WEB SEARCH GUIDANCE ===\n"
        
        if guidance:
            instruction += f"{guidance}\n"
        else:
            instruction += (
                "Consider using web search for:\n"
                "- Current information and recent developments\n"
                "- Documentation and technical specifications\n"
                "- Best practices and community solutions\n"
            )
            
        instruction += "=== END GUIDANCE ===\n"
        return instruction

    def get_websearch_guidance(self) -> Optional[str]:
        """
        Return tool-specific web search guidance.

        Override this to provide tool-specific guidance for when web searches
        would be helpful. Return None to use the default guidance.

        Returns:
            Tool-specific web search guidance or None for default
        """
        return None

    def get_chat_style_websearch_guidance(self) -> str:
        """
        Get Chat tool-style web search guidance.

        Returns web search guidance that matches the original Chat tool pattern.
        This is useful for tools that want to maintain the same search behavior.

        Returns:
            Web search guidance text
        """
        return """When discussing topics, consider if searches for these would help:
- Documentation for any technologies or concepts mentioned
- Current best practices and patterns
- Recent developments or updates
- Community discussions and solutions"""

