"""
Core Tool Infrastructure for EXAI MCP Tools

This module provides the fundamental base class for all tools by composing
specialized mixins that handle different aspects of tool functionality.

ARCHITECTURE OVERVIEW:
=====================

The BaseTool class uses a mixin-based composition pattern to separate concerns
and maintain modularity. This design was chosen over a monolithic class to:

1. **Separation of Concerns**: Each mixin handles a distinct responsibility
2. **Independent Testing**: Mixins can be unit tested in isolation
3. **Selective Inheritance**: Future tools can compose only needed functionality
4. **Maintainability**: Changes to one concern don't affect others
5. **Extensibility**: New mixins can be added without modifying existing code

MIXIN COMPOSITION:
==================

The BaseTool class is composed from these mixins (in MRO order):

1. **BaseToolCore** (base_tool_core.py - 381 lines)
   - Core interface and abstract methods
   - Tool metadata (name, description, category)
   - Configuration methods with default implementations
   - OpenRouter registry caching for model lookups

2. **ModelManagementMixin** (base_tool_model_management.py)
   - Model provider integration and selection
   - Model context resolution and validation
   - Provider-specific configuration handling
   - Model capability checking

3. **FileHandlingMixin** (base_tool_file_handling.py)
   - File processing and conversation-aware handling
   - Dual prioritization strategy for file deduplication
   - Token-aware file embedding with graceful degradation
   - Cross-tool file tracking and context integration

4. **ResponseFormattingMixin** (base_tool_response.py - 168 lines)
   - Response formatting and post-processing
   - Web search instruction generation
   - Language instruction generation
   - Response parsing hooks

ARCHITECTURAL DECISIONS:
========================

**Why Mixins Instead of Single File?**
- Considered consolidating base_tool_core.py and base_tool_response.py
- Decision: MAINTAIN SEPARATION (Phase 6.3 - 2025-11-01)
- Rationale: Combined file would be ~576 lines, approaching unwieldy size
- Benefits: Clear boundaries, independent evolution, better testability

**Why Only base_tool.py Imports Mixins?**
- Mixins are implementation details, not public interfaces
- Tools inherit from BaseTool, never from mixins directly
- This encapsulation allows internal refactoring without breaking tools

**Import Dependencies:**
- Only base_tool.py imports from base_tool_core.py and base_tool_response.py
- No other files in codebase import these modules directly
- Clean dependency graph prevents circular imports

USAGE PATTERN:
==============

To create a new tool:
1. Inherit from BaseTool (not from individual mixins)
2. Implement all abstract methods from BaseToolCore
3. Define a request model that inherits from ToolRequest
4. Register the tool in tools/registry.py

Example:
    class MyTool(BaseTool):
        def get_name(self) -> str:
            return "my_tool"

        async def execute(self, arguments: dict, on_chunk=None):
            # Implementation here
            pass

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

