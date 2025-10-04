"""
Core Tool Interface for EXAI MCP Tools

This module provides the fundamental base class interface and abstract methods
that all tools must implement.

Key Components:
- BaseToolCore: Abstract base class defining the core tool interface
- Abstract methods for tool metadata and configuration
- Core configuration methods with default implementations
"""

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from tools.models import ToolModelCategory

logger = logging.getLogger(__name__)


class BaseToolCore(ABC):
    """
    Abstract base class defining the core interface for all EXAI MCP tools.

    This class defines the fundamental contract that all tools must implement,
    including tool metadata, configuration, and basic behavior.

    To create a new tool:
    1. Inherit from BaseTool (which composes this and other mixins)
    2. Implement all abstract methods
    3. Define a request model that inherits from ToolRequest
    4. Register the tool in server.py's TOOLS dictionary
    """
    
    # Class-level cache for OpenRouter registry to avoid multiple loads
    _openrouter_registry_cache = None
    
    @classmethod
    def _get_openrouter_registry(cls):
        """Get cached OpenRouter registry instance, creating if needed."""
        # Use BaseToolCore class directly to ensure cache is shared across all subclasses
        if BaseToolCore._openrouter_registry_cache is None:
            from src.providers.openrouter_registry import OpenRouterModelRegistry
            
            BaseToolCore._openrouter_registry_cache = OpenRouterModelRegistry()
            logger.debug("Created cached OpenRouter registry instance")
        return BaseToolCore._openrouter_registry_cache
    
    def __init__(self):
        # Cache tool metadata at initialization to avoid repeated calls
        self.name = self.get_name()
        self.description = self.get_description()
        self.default_temperature = self.get_default_temperature()
        # Tool initialization complete
    
    # ================================================================================
    # Abstract Methods - Must be implemented by all tools
    # ================================================================================
    
    @abstractmethod
    def get_name(self) -> str:
        """
        Return the unique name identifier for this tool.
        
        This name is used by MCP clients to invoke the tool and must be
        unique across all registered tools.
        
        Returns:
            str: The tool's unique name (e.g., "review_code", "analyze")
        """
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """
        Return a detailed description of what this tool does.
        
        This description is shown to MCP clients to help them
        understand when and how to use the tool. It should be comprehensive
        and include trigger phrases.
        
        Returns:
            str: Detailed tool description with usage examples
        """
        pass
    
    @abstractmethod
    def get_input_schema(self) -> dict[str, Any]:
        """
        Return the JSON Schema that defines this tool's parameters.
        
        This schema is used by MCP clients to validate inputs before
        sending requests. It should match the tool's request model.
        
        Returns:
            dict[str, Any]: JSON Schema object defining required and optional parameters
        """
        pass
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Return the system prompt that configures the AI model's behavior.
        
        This prompt sets the context and instructions for how the model
        should approach the task. It's prepended to the user's request.
        
        Returns:
            str: System prompt with role definition and instructions
        """
        pass
    
    # ================================================================================
    # Tool Descriptor - Default Implementation
    # ================================================================================
    
    def get_descriptor(self) -> dict[str, Any]:
        """Return a machine-readable descriptor for this tool (MVP).
        
        Non-breaking default that harvests existing metadata so planners/orchestrators
        can reason about tools without hardcoding. WorkflowTool will override to add
        workflow-specific semantics.
        """
        # Basic fields
        name = self.get_name()
        try:
            description = self.get_description()
        except Exception:
            description = ""
        try:
            annotations = self.get_annotations() or {}
        except Exception:
            annotations = {}
        try:
            schema = self.get_input_schema()
        except Exception:
            schema = {}
        
        # Some tool variants (e.g., WorkflowTool) may expose get_required_fields.
        req_fields: list[str] = []
        try:
            rf = getattr(self, "get_required_fields", None)
            if callable(rf):
                req_fields = rf() or []
        except Exception:
            req_fields = []
        
        # Optional: model category for cost/latency hints
        model_category = None
        try:
            get_mc = getattr(self, "get_model_category", None)
            if callable(get_mc):
                mc = get_mc()
                model_category = getattr(mc, "value", getattr(mc, "name", str(mc)))
        except Exception:
            model_category = None
        
        # Optional: whether tool requires a model
        requires_model = None
        try:
            requires_model = bool(self.requires_model())
        except Exception:
            requires_model = None
        
        return {
            "id": name,
            "display_name": name,
            "description": description,
            "category": "core",
            "type": "simple",
            "capabilities": [],
            "supports_workflow": False,
            "required_fields": req_fields,
            "input_schema": schema,
            "annotations": annotations,
            **({"model_category": model_category} if model_category else {}),
            **({"requires_model": requires_model} if requires_model is not None else {}),
        }
    
    def get_annotations(self) -> Optional[dict[str, Any]]:
        """
        Return optional annotations for this tool.
        
        Annotations provide hints about tool behavior without being security-critical.
        They help MCP clients make better decisions about tool usage.
        
        Returns:
            Optional[dict]: Dictionary with annotation fields like readOnlyHint, destructiveHint, etc.
                           Returns None if no annotations are needed.
        """
        return None
    
    # ================================================================================
    # Tool Configuration - Default Implementations
    # ================================================================================
    
    def requires_model(self) -> bool:
        """
        Return whether this tool requires AI model access.
        
        Tools that override execute() to do pure data processing (like planner)
        should return False to skip model resolution at the MCP boundary.
        
        Returns:
            bool: True if tool needs AI model access (default), False for data-only tools
        """
        return True
    
    def get_default_temperature(self) -> float:
        """
        Return the default temperature for this tool's AI model calls.
        
        Temperature controls randomness in model outputs:
        - Lower values (0.0-0.3): More focused and deterministic
        - Medium values (0.4-0.7): Balanced creativity and consistency
        - Higher values (0.8-1.0): More creative and varied
        
        Returns:
            float: Default temperature value (typically 0.3-0.7)
        """
        return 0.5
    
    def wants_line_numbers_by_default(self) -> bool:
        """
        Return whether this tool wants line numbers in file content by default.
        
        Line numbers help with precise code references but add token overhead.
        Tools focused on code analysis typically want them, while general tools may not.
        
        Returns:
            bool: True if line numbers should be included by default
        """
        return False
    
    def get_default_thinking_mode(self) -> str:
        """
        Return the default thinking mode for this tool.
        
        Thinking modes control the depth of reasoning:
        - "minimal": Quick, surface-level responses
        - "low": Basic reasoning
        - "medium": Standard analytical depth
        - "high": Deep, thorough analysis
        - "max": Maximum reasoning depth
        
        Returns:
            str: Default thinking mode (typically "medium" or "high")
        """
        return "medium"
    
    def get_model_category(self) -> "ToolModelCategory":
        """
        Return the model category for this tool.
        
        Model categories help with cost optimization and capability matching:
        - FAST: Quick, lightweight models for simple tasks
        - SMART: Balanced models for general use
        - ADVANCED: Powerful models for complex reasoning
        
        Returns:
            ToolModelCategory: The tool's model category
        """
        from tools.models import ToolModelCategory
        return ToolModelCategory.SMART
    
    def get_request_model(self):
        """
        Return the request model class for this tool.
        
        The request model defines and validates the tool's input parameters.
        This is used for runtime validation and schema generation.
        
        Returns:
            Type: The Pydantic model class for this tool's requests
        """
        # Default implementation - tools should override if they have a specific request model
        return None

