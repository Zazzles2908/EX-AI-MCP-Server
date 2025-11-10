"""
Capability-Aware Routing

Dynamically routes requests based on provider capabilities and tool requirements.
Optimizes execution paths by matching tool needs with provider features.

Phase 1.5 Implementation - Capability-Aware Routing
"""

import logging
from typing import Dict, Any, Optional, List
from enum import Enum

from src.prompts.prompt_registry import ProviderType

logger = logging.getLogger(__name__)


class ExecutionPath(Enum):
    """Execution path types based on capabilities."""
    DIRECT = "direct_execution"  # Utility tools, no model needed
    STANDARD = "standard_execution"  # Basic model execution
    STREAMING = "streaming_execution"  # Streaming response
    THINKING = "thinking_mode"  # Deep reasoning mode
    VISION = "vision_enabled"  # Image processing
    FILE_UPLOAD = "file_upload_enabled"  # File handling
    TOOL_CALLING = "tool_calling_enabled"  # Function calling


class CapabilityMatrix:
    """
    Capability matrix defining what each provider supports.
    
    This matrix is the source of truth for provider capabilities and is used
    to make routing decisions.
    """
    
    # Kimi (Moonshot) capabilities
    KIMI_CAPABILITIES = {
        "streaming": True,
        "thinking_mode": True,  # kimi-thinking-preview model
        "file_uploads": True,  # Moonshot file API
        "vision": True,  # moonshot-v1-*-vision-preview models
        "tool_calling": True,  # OpenAI-compatible function calling
        "web_search": False,  # BUG FIX (2025-11-09): Kimi does NOT support web_search tool type
        "max_tokens": 128000,  # Context window
        "max_output_tokens": 4096,
        "supports_chinese": True,
        "supports_english": True,
        "sdk_type": "openai_compatible"
    }
    
    # GLM (ZhipuAI) capabilities
    GLM_CAPABILITIES = {
        "streaming": True,
        "thinking_mode": True,  # Custom thinking.type parameter
        "file_uploads": True,  # GLM file API
        "vision": True,  # glm-4.5v model
        "tool_calling": True,  # Native tool calling
        "web_search": True,  # Native web search via search_prime
        "max_tokens": 128000,  # Context window
        "max_output_tokens": 4096,
        "supports_chinese": True,  # Primary language
        "supports_english": True,
        "sdk_type": "zhipuai_native"
    }
    
    @classmethod
    def get_capabilities(cls, provider: ProviderType) -> Dict[str, Any]:
        """
        Get capability dictionary for a provider.
        
        Args:
            provider: Provider type (KIMI or GLM)
        
        Returns:
            Dictionary of capabilities
        """
        if provider == ProviderType.KIMI:
            return cls.KIMI_CAPABILITIES.copy()
        elif provider == ProviderType.GLM:
            return cls.GLM_CAPABILITIES.copy()
        else:
            return {}
    
    @classmethod
    def supports_feature(cls, provider: ProviderType, feature: str) -> bool:
        """
        Check if provider supports a specific feature.
        
        Args:
            provider: Provider type
            feature: Feature name (e.g., "streaming", "vision")
        
        Returns:
            True if feature is supported
        """
        capabilities = cls.get_capabilities(provider)
        return capabilities.get(feature, False)
    
    @classmethod
    def get_max_tokens(cls, provider: ProviderType) -> int:
        """Get maximum token limit for provider."""
        capabilities = cls.get_capabilities(provider)
        return capabilities.get("max_tokens", 4096)
    
    @classmethod
    def get_sdk_type(cls, provider: ProviderType) -> str:
        """Get SDK type for provider."""
        capabilities = cls.get_capabilities(provider)
        return capabilities.get("sdk_type", "unknown")


class ToolRequirements:
    """
    Tool requirements specification.
    
    Defines what capabilities a tool needs from the provider.
    """
    
    def __init__(
        self,
        requires_model: bool = True,
        supports_streaming: bool = False,
        needs_reasoning: bool = False,
        needs_vision: bool = False,
        needs_file_upload: bool = False,
        needs_tool_calling: bool = False,
        needs_web_search: bool = False,
        min_tokens: int = 4096
    ):
        """
        Initialize tool requirements.
        
        Args:
            requires_model: Whether tool needs AI model (False for utility tools)
            supports_streaming: Whether tool can use streaming responses
            needs_reasoning: Whether tool benefits from thinking mode
            needs_vision: Whether tool processes images
            needs_file_upload: Whether tool handles file uploads
            needs_tool_calling: Whether tool uses function calling
            needs_web_search: Whether tool needs web search
            min_tokens: Minimum token requirement
        """
        self.requires_model = requires_model
        self.supports_streaming = supports_streaming
        self.needs_reasoning = needs_reasoning
        self.needs_vision = needs_vision
        self.needs_file_upload = needs_file_upload
        self.needs_tool_calling = needs_tool_calling
        self.needs_web_search = needs_web_search
        self.min_tokens = min_tokens


# Tool requirement definitions
TOOL_REQUIREMENTS = {
    # Workflow tools - complex analysis
    "debug": ToolRequirements(
        requires_model=True,
        supports_streaming=True,
        needs_reasoning=True,
        min_tokens=8192
    ),
    "analyze": ToolRequirements(
        requires_model=True,
        supports_streaming=True,
        needs_reasoning=True,
        min_tokens=8192
    ),
    "codereview": ToolRequirements(
        requires_model=True,
        supports_streaming=True,
        needs_reasoning=True,
        min_tokens=8192
    ),
    "refactor": ToolRequirements(
        requires_model=True,
        supports_streaming=True,
        needs_reasoning=True,
        min_tokens=8192
    ),
    "secaudit": ToolRequirements(
        requires_model=True,
        supports_streaming=True,
        needs_reasoning=True,
        min_tokens=8192
    ),
    "precommit": ToolRequirements(
        requires_model=True,
        supports_streaming=True,
        needs_reasoning=True,
        min_tokens=8192
    ),
    "testgen": ToolRequirements(
        requires_model=True,
        supports_streaming=True,
        needs_reasoning=True,
        min_tokens=8192
    ),
    "thinkdeep": ToolRequirements(
        requires_model=True,
        supports_streaming=True,
        needs_reasoning=True,
        min_tokens=16384
    ),
    "tracer": ToolRequirements(
        requires_model=True,
        supports_streaming=True,
        needs_reasoning=True,
        min_tokens=8192
    ),
    "planner": ToolRequirements(
        requires_model=True,
        supports_streaming=True,
        needs_reasoning=True,
        min_tokens=8192
    ),
    "docgen": ToolRequirements(
        requires_model=True,
        supports_streaming=True,
        needs_reasoning=False,
        min_tokens=8192
    ),
    "consensus": ToolRequirements(
        requires_model=True,
        supports_streaming=True,
        needs_reasoning=True,
        min_tokens=16384
    ),
    
    # Simple tools
    "chat": ToolRequirements(
        requires_model=True,
        supports_streaming=True,
        needs_reasoning=False,
        needs_file_upload=True,
        needs_web_search=True,
        min_tokens=4096
    ),
    
    # Utility tools - no model needed
    "activity": ToolRequirements(requires_model=False),
    "health": ToolRequirements(requires_model=False),
    "listmodels": ToolRequirements(requires_model=False),
    "version": ToolRequirements(requires_model=False),
}


class CapabilityRouter:
    """
    Routes requests based on provider capabilities and tool requirements.
    
    Determines optimal execution path by matching tool needs with provider features.
    
    Usage:
        router = CapabilityRouter()
        path = router.route_request("debug", ProviderType.KIMI, streaming=True)
        # Returns: ExecutionPath.THINKING
    """
    
    def __init__(self):
        """Initialize capability router."""
        self.capability_matrix = CapabilityMatrix()
        logger.info("CapabilityRouter initialized")
    
    def route_request(
        self,
        tool_name: str,
        provider: ProviderType,
        streaming: bool = False,
        thinking_mode: bool = False,
        has_images: bool = False,
        has_files: bool = False
    ) -> ExecutionPath:
        """
        Determine optimal execution path for request.
        
        Args:
            tool_name: Name of the tool being invoked
            provider: Provider to use
            streaming: Whether streaming is requested
            thinking_mode: Whether thinking mode is requested
            has_images: Whether request includes images
            has_files: Whether request includes file uploads
        
        Returns:
            ExecutionPath enum indicating routing decision
        """
        # Get tool requirements
        requirements = TOOL_REQUIREMENTS.get(tool_name)
        if not requirements:
            logger.warning(f"Unknown tool: {tool_name}, using standard execution")
            return ExecutionPath.STANDARD
        
        # Utility tools bypass model entirely
        if not requirements.requires_model:
            logger.debug(f"Tool {tool_name} is utility tool, using direct execution")
            return ExecutionPath.DIRECT
        
        # Get provider capabilities
        capabilities = self.capability_matrix.get_capabilities(provider)
        
        # Check token requirements
        if requirements.min_tokens > capabilities.get("max_tokens", 0):
            logger.warning(
                f"Tool {tool_name} requires {requirements.min_tokens} tokens, "
                f"but {provider.value} only supports {capabilities.get('max_tokens')}"
            )
        
        # Route based on features (priority order)
        
        # 1. Vision takes precedence if images present
        if has_images and requirements.needs_vision:
            if capabilities.get("vision"):
                logger.info(f"Routing {tool_name} to vision-enabled path")
                return ExecutionPath.VISION
            else:
                logger.warning(f"Provider {provider.value} doesn't support vision")
        
        # 2. File upload path
        if has_files and requirements.needs_file_upload:
            if capabilities.get("file_uploads"):
                logger.info(f"Routing {tool_name} to file-upload path")
                return ExecutionPath.FILE_UPLOAD
            else:
                logger.warning(f"Provider {provider.value} doesn't support file uploads")
        
        # 3. Thinking mode for complex reasoning
        if (thinking_mode or requirements.needs_reasoning) and capabilities.get("thinking_mode"):
            logger.info(f"Routing {tool_name} to thinking mode path")
            return ExecutionPath.THINKING
        
        # 4. Streaming for supported tools
        if streaming and requirements.supports_streaming and capabilities.get("streaming"):
            logger.info(f"Routing {tool_name} to streaming path")
            return ExecutionPath.STREAMING
        
        # 5. Default to standard execution
        logger.debug(f"Routing {tool_name} to standard execution path")
        return ExecutionPath.STANDARD
    
    def get_optimal_provider(
        self,
        tool_name: str,
        required_features: Optional[List[str]] = None
    ) -> ProviderType:
        """
        Suggest optimal provider for a tool based on requirements.

        Args:
            tool_name: Name of the tool
            required_features: List of required features

        Returns:
            Recommended provider type
        """
        requirements = TOOL_REQUIREMENTS.get(tool_name)
        if not requirements:
            return ProviderType.AUTO

        # BUG FIX (2025-11-09): Smart routing for web_search
        # Kimi does not support web_search tool type - must route to GLM
        if requirements.needs_web_search:
            logger.info("[SMART_ROUTING] Tool requires web_search, routing to GLM")
            return ProviderType.GLM

        # If no specific features required, default to KIMI
        if not required_features:
            return ProviderType.KIMI

        # Check which providers support all required features
        for provider in [ProviderType.KIMI, ProviderType.GLM]:
            capabilities = self.capability_matrix.get_capabilities(provider)
            if all(capabilities.get(feature, False) for feature in required_features):
                logger.info(f"Provider {provider.value} supports all required features")
                return provider

        # Fallback to AUTO if no provider supports all features
        logger.warning("No provider supports all required features, using AUTO")
        return ProviderType.AUTO
    
    def validate_request(
        self,
        tool_name: str,
        provider: ProviderType,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Validate that provider can handle the request.
        
        Args:
            tool_name: Name of the tool
            provider: Provider to validate
            **kwargs: Request parameters
        
        Returns:
            Validation result with warnings/errors
        """
        result = {
            "valid": True,
            "warnings": [],
            "errors": []
        }
        
        requirements = TOOL_REQUIREMENTS.get(tool_name)
        if not requirements:
            result["warnings"].append(f"Unknown tool: {tool_name}")
            return result
        
        capabilities = self.capability_matrix.get_capabilities(provider)
        
        # Check each requirement
        if kwargs.get("has_images") and not capabilities.get("vision"):
            result["errors"].append(f"Provider {provider.value} doesn't support vision")
            result["valid"] = False
        
        if kwargs.get("has_files") and not capabilities.get("file_uploads"):
            result["errors"].append(f"Provider {provider.value} doesn't support file uploads")
            result["valid"] = False
        
        if requirements.min_tokens > capabilities.get("max_tokens", 0):
            result["warnings"].append(
                f"Tool requires {requirements.min_tokens} tokens, "
                f"provider supports {capabilities.get('max_tokens')}"
            )
        
        return result


# Global router instance
_router_instance = None


def get_router() -> CapabilityRouter:
    """Get global CapabilityRouter instance (singleton pattern)."""
    global _router_instance
    if _router_instance is None:
        _router_instance = CapabilityRouter()
    return _router_instance

