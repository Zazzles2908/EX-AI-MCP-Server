"""
Response Formatting Mixin for EXAI MCP Tools

This module provides response formatting and instruction generation for tools.

RESPONSIBILITY:
===============

ResponseFormattingMixin handles the OUTPUT side of tool execution:
- Generating standardized instructions for AI models
- Formatting responses for consistency
- Post-processing hooks for response customization
- Web search and language instruction generation

This mixin is INDEPENDENT of the core interface and model management,
allowing response formatting logic to evolve without affecting other concerns.

DESIGN RATIONALE:
=================

**Why Separate from base_tool_core.py?**
- Different concern: Response formatting vs. core interface
- Independent evolution: Formatting logic changes frequently
- Size: 168 lines is substantial enough for its own module
- Testability: Response formatting can be tested independently
- Decision: MAINTAIN SEPARATION (Phase 6.3 - 2025-11-01)

**Why Not Merge with base_tool.py?**
- Keeps composition orchestrator (base_tool.py) focused
- Response formatting is an implementation detail, not composition logic
- Allows future tools to override formatting without touching core

INSTRUCTION GENERATION:
=======================

**Web Search Instructions:**
- Standardized instructions for when web search is enabled
- Tool-specific guidance can be added via tool_specific parameter
- Consistent format across all tools for AI model clarity

**Language Instructions:**
- Generates language-specific instructions for code generation
- Supports multiple programming languages
- Extensible for new languages without modifying core logic

RESPONSE FORMATTING HOOKS:
==========================

**format_response():**
- Default implementation returns response as-is
- Tools can override to customize response formatting
- Useful for adding metadata, formatting code blocks, etc.

**parse_response():**
- Hook for parsing AI model responses
- Default implementation returns response unchanged
- Tools can override for custom parsing logic

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

WEB SEARCH CAPABILITY: You have access to native web search tools that you can use autonomously to enhance your analysis with current information!

IMPORTANT: When you identify areas where web searches would significantly improve your response (such as checking current documentation, finding recent solutions, verifying best practices, or gathering community insights), you should AUTONOMOUSLY use your web search tool to gather this information and incorporate it directly into your response.

How to use web search:
1. Identify what information would improve your analysis
2. Use your web search tool with specific, targeted queries
3. Incorporate the search results directly into your comprehensive response
4. Cite sources when referencing search results

When web search is valuable:
- Checking current documentation and API references
- Finding recent best practices and patterns
- Verifying known issues and community solutions
- Checking framework updates and compatibility
- Looking up security advisories and patches
- Finding performance benchmarks and optimizations

You should use web search proactively when it will provide more accurate, current, or comprehensive information. Do not ask permission - just search and integrate the results into your response."""

        if tool_specific:
            return f"""{base_instruction}

{tool_specific}

Use web search autonomously whenever it will improve the quality and accuracy of your analysis."""

        # Default instruction for all tools
        return base_instruction
    
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

