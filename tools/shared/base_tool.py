"""
Core Tool Infrastructure for EXAI MCP Tools

This module provides the fundamental base class for all tools by composing
specialized mixins that handle different aspects of tool functionality.

The BaseTool class is composed from:
- BaseToolCore: Core interface and abstract methods
- ModelManagementMixin: Model provider integration and selection
- FileHandlingMixin: File processing and conversation-aware handling
- ResponseFormattingMixin: Response formatting and instruction generation

This modular architecture keeps each component focused and maintainable while
providing the full functionality needed by all tools.
"""

import logging
from abc import ABC
from typing import TYPE_CHECKING, Any, Optional

from mcp.types import TextContent

if TYPE_CHECKING:
    from tools.models import ToolModelCategory

from tools.shared.base_tool_core import BaseToolCore
from tools.shared.base_tool_file_handling import FileHandlingMixin
from tools.shared.base_tool_model_management import ModelManagementMixin
from tools.shared.base_tool_response import ResponseFormattingMixin

# Import models from tools.models for compatibility
try:
    from tools.models import SPECIAL_STATUS_MODELS, ContinuationOffer, ToolOutput
except ImportError:
    # Fallback in case models haven't been set up yet
    SPECIAL_STATUS_MODELS = {}
    ContinuationOffer = None
    ToolOutput = None

logger = logging.getLogger(__name__)


class BaseTool(
    BaseToolCore,
    ModelManagementMixin,
    FileHandlingMixin,
    ResponseFormattingMixin,
    ABC
):
    """
    Abstract base class for all Zen MCP tools.
    
    This class defines the interface that all tools must implement and provides
    common functionality for request handling, model creation, and response formatting.
    
    CONVERSATION-AWARE FILE PROCESSING:
    This base class implements the sophisticated dual prioritization strategy for
    conversation-aware file handling across all tools:
    
    1. FILE DEDUPLICATION WITH NEWEST-FIRST PRIORITY:
       - When same file appears in multiple conversation turns, newest reference wins
       - Prevents redundant file embedding while preserving most recent file state
       - Cross-tool file tracking ensures consistent behavior across analyze → codereview → debug
    
    2. CONVERSATION CONTEXT INTEGRATION:
       - All tools receive enhanced prompts with conversation history via reconstruct_thread_context()
       - File references from previous turns are preserved and accessible
       - Cross-tool knowledge transfer maintains full context without manual file re-specification
    
    3. TOKEN-AWARE FILE EMBEDDING:
       - Respects model-specific token allocation budgets from ModelContext
       - Prioritizes conversation history, then newest files, then remaining content
       - Graceful degradation when token limits are approached
    
    4. STATELESS-TO-STATEFUL BRIDGING:
       - Tools operate on stateless MCP requests but access full conversation state
       - Conversation memory automatically injected via continuation_id parameter
       - Enables natural AI-to-AI collaboration across tool boundaries
    
    To create a new tool:
    1. Create a new class that inherits from BaseTool
    2. Implement all abstract methods
    3. Define a request model that inherits from ToolRequest
    4. Register the tool in server.py's TOOLS dictionary
    
    Architecture:
    - BaseToolCore: Core interface, abstract methods, configuration
    - ModelManagementMixin: Model provider integration, selection, validation
    - FileHandlingMixin: File processing, conversation-aware deduplication
    - ResponseFormattingMixin: Response formatting, instruction generation
    """
    
    # ================================================================================
    # Implementation Methods - Must be implemented by subclasses
    # ================================================================================
    
    async def execute(
        self,
        arguments: dict[str, Any],
        on_chunk: Optional[Any] = None  # NEW: Streaming callback for progressive chunk delivery
    ) -> list[TextContent]:
        """
        Execute the tool with the given arguments.

        Args:
            arguments: Tool arguments dictionary
            on_chunk: Optional async callback for streaming chunks (signature: async def on_chunk(chunk: str))

        This is the main entry point for tool execution. It should:
        1. Validate and parse the arguments into a request object
        2. Resolve the model context
        3. Prepare the prompt using prepare_prompt()
        4. Call the AI model
        5. Format and return the response
        
        Args:
            arguments: Dictionary of arguments from the MCP client
        
        Returns:
            list[TextContent]: List of text content responses
        
        Raises:
            ValueError: If validation fails or required parameters are missing
        """
        raise NotImplementedError("Subclasses must implement execute method")

