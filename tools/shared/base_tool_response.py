"""
Response Formatting Mixin for Zen MCP Tools

This module provides response formatting and instruction generation for tools.

Key Components:
- ResponseFormattingMixin: Handles response formatting and instruction generation
- Web search instruction generation
- Language instruction generation
- Response formatting hooks
"""

import logging
import os
from abc import abstractmethod
from typing import Any, Optional

logger = logging.getLogger(__name__)


class ResponseFormattingMixin:
    """
    Mixin providing response formatting functionality for tools.
    
    This class handles:
    - Response formatting and post-processing
    - Web search instruction generation
    - Language instruction generation
    - Response parsing hooks
    """
    
    # ================================================================================
    # Instruction Generation
    # ================================================================================
    
    def get_websearch_instruction(self, use_websearch: bool, tool_specific: Optional[str] = None) -> str:
        """
        Generate standardized web search instruction based on the use_websearch parameter.
        
        Args:
            use_websearch: Whether web search is enabled
            tool_specific: Optional tool-specific search guidance
        
        Returns:
            str: Web search instruction to append to prompt, or empty string
        """
        if not use_websearch:
            return ""
        
        base_instruction = """

WEB SEARCH CAPABILITY: You can request Claude to perform web searches to enhance your analysis with current information!

IMPORTANT: When you identify areas where web searches would significantly improve your response (such as checking current documentation, finding recent solutions, verifying best practices, or gathering community insights), you MUST explicitly instruct Claude to perform specific web searches and then respond back using the continuation_id from this response to continue the analysis.

Use clear, direct language based on the value of the search:

For valuable supplementary information: "Please perform a web search on '[specific topic/query]' and then continue this analysis using the continuation_id from this response if you find relevant information."

For important missing information: "Please search for '[specific topic/query]' and respond back with the findings using the continuation_id from this response - this information is needed to provide a complete analysis."

For critical/essential information: "SEARCH REQUIRED: Please immediately perform a web search on '[specific topic/query]' and respond back with the results using the continuation_id from this response. Cannot provide accurate analysis without this current information."

This ensures you get the most current and comprehensive information while maintaining conversation context through the continuation_id."""
        
        if tool_specific:
            return f"""{base_instruction}

{tool_specific}

When recommending searches, be specific about what information you need and why it would improve your analysis."""
        
        # Default instruction for all tools
        return f"""{base_instruction}

Consider requesting searches for:
- Current documentation and API references
- Recent best practices and patterns
- Known issues and community solutions
- Framework updates and compatibility
- Security advisories and patches
- Performance benchmarks and optimizations

When recommending searches, be specific about what information you need and why it would improve your analysis. Always remember to instruct Claude to use the continuation_id from this response when providing search results."""
    
    def get_language_instruction(self) -> str:
        """
        Generate language instruction based on LOCALE configuration.
        
        Returns:
            str: Language instruction to prepend to prompt, or empty string if
                 no locale set
        """
        # Read LOCALE directly from environment to support dynamic changes
        # This allows tests to modify os.environ["LOCALE"] and see the changes
        locale = os.getenv("LOCALE", "").strip()
        
        if not locale:
            return ""
        
        # Simple language instruction
        return f"Always respond in {locale}.\n\n"
    
    # ================================================================================
    # Response Formatting
    # ================================================================================
    
    def format_response(self, response: str, request, model_info: dict = None) -> str:
        """
        Format the AI model's response for the user.
        
        This method allows tools to post-process the model's response,
        adding structure, validation, or additional context.
        
        The default implementation returns the response unchanged.
        Tools can override this method to add custom formatting.
        
        Args:
            response: Raw response from the AI model
            request: The original request object
            model_info: Optional model information and metadata
        
        Returns:
            str: Formatted response ready for the user
        """
        return response
    
    # ================================================================================
    # Abstract Methods - Must be implemented by tools
    # ================================================================================
    
    @abstractmethod
    async def prepare_prompt(self, request) -> str:
        """
        Prepare the complete prompt for the AI model.
        
        This method should construct the full prompt by combining:
        - System prompt from get_system_prompt()
        - File content from _prepare_file_content_for_prompt()
        - Conversation history from reconstruct_thread_context()
        - User's request and any tool-specific context
        
        Args:
            request: The validated request object
        
        Returns:
            str: Complete prompt ready for the AI model
        """
        pass
    
    def _parse_response(self, raw_text: str, request, model_info: Optional[dict] = None):
        """
        Parse and validate the AI model's response.
        
        This method allows tools to parse structured responses, validate output,
        or extract specific information from the model's response.
        
        The default implementation returns the raw text unchanged.
        Tools can override this method to add custom parsing logic.
        
        Args:
            raw_text: Raw text response from the AI model
            request: The original request object
            model_info: Optional model information and metadata
        
        Returns:
            Parsed response (type depends on tool implementation)
        """
        # Default implementation: return raw text
        return raw_text

