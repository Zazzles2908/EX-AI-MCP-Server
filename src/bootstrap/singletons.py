"""
Singleton Initialization Module

This module provides idempotent initialization of providers and tools that must
happen exactly once per process, regardless of how many entry points import it.

CRITICAL: This module should be imported at top-level by both server.py and ws_server.py
to ensure singleton initialization happens before any tool execution.

Architecture:
- Providers are configured once via configure_providers()
- Tool registry is built once via ToolRegistry.build_tools()
- Provider-specific tools are registered once after providers are ready
- All initialization is guarded by module-level flags to prevent re-execution

Thread Safety:
- This module uses module-level state which is inherently thread-safe in CPython
  due to the GIL and import lock
- No additional locking is needed for initialization guards
"""

import logging
import os
from typing import Dict, Any, Optional

# Setup logging early
logger = logging.getLogger(__name__)

# ============================================================================
# INITIALIZATION STATE FLAGS
# ============================================================================
# These flags ensure idempotent initialization across multiple imports

_providers_configured = False
_tools_built = False
_provider_tools_registered = False

# Shared references to initialized objects
_tool_registry: Optional[Any] = None
_tools_dict: Optional[Dict[str, Any]] = None


# ============================================================================
# PROVIDER INITIALIZATION
# ============================================================================

def ensure_providers_configured() -> None:
    """
    Idempotently configure AI model providers.
    
    This function can be called multiple times safely - it will only
    configure providers on the first call.
    
    Raises:
        ValueError: If no valid API keys are found
    """
    global _providers_configured
    
    if _providers_configured:
        logger.debug("Providers already configured, skipping")
        return
    
    try:
        from src.server.providers import configure_providers
        
        logger.info("Configuring providers (first-time initialization)")
        configure_providers()
        _providers_configured = True
        logger.info("Providers configured successfully")
        
    except Exception as e:
        logger.error(f"Failed to configure providers: {e}")
        raise


# ============================================================================
# TOOL REGISTRY INITIALIZATION
# ============================================================================

def ensure_tools_built() -> Dict[str, Any]:
    """
    Idempotently build the tool registry.
    
    This function can be called multiple times safely - it will only
    build tools on the first call and return the same dict reference
    on subsequent calls.
    
    Returns:
        Dict[str, Any]: The unified tool dictionary (same object reference)
    """
    global _tools_built, _tool_registry, _tools_dict
    
    if _tools_built and _tools_dict is not None:
        logger.debug("Tools already built, returning existing dict")
        return _tools_dict
    
    try:
        from tools.registry import ToolRegistry
        
        logger.info("Building tool registry (first-time initialization)")
        _tool_registry = ToolRegistry()
        _tool_registry.build_tools()
        _tools_dict = _tool_registry.list_tools()
        _tools_built = True
        
        logger.info(f"Tool registry built successfully with {len(_tools_dict)} tools")
        return _tools_dict
        
    except Exception as e:
        logger.error(f"Failed to build tool registry: {e}")
        raise


# ============================================================================
# PROVIDER-SPECIFIC TOOL REGISTRATION
# ============================================================================

def ensure_provider_tools_registered(tools_dict: Dict[str, Any]) -> None:
    """
    Idempotently register provider-specific tools.
    
    This function can be called multiple times safely - it will only
    register provider tools on the first call after providers are configured.
    
    Args:
        tools_dict: The tool dictionary to mutate with provider-specific tools
    """
    global _provider_tools_registered
    
    if _provider_tools_registered:
        logger.debug("Provider-specific tools already registered, skipping")
        return
    
    if not _providers_configured:
        logger.info("Provider tools will be registered after providers are configured")
        return
    
    try:
        import importlib
        
        prov_tools: Dict[str, Any] = {}
        
        # Kimi provider tools (lenient registration)
        # NOTE: kimi_upload_and_extract and kimi_chat_with_tools are INTERNAL ONLY
        kimi_tools = [
            ("kimi_multi_file_chat", ("tools.providers.kimi.kimi_upload", "KimiMultiFileChatTool")),
            ("kimi_intent_analysis", ("tools.providers.kimi.kimi_intent", "KimiIntentAnalysisTool")),
        ]
        
        for name, (module_path, class_name) in kimi_tools:
            try:
                mod = importlib.import_module(module_path)
                cls = getattr(mod, class_name)
                if name not in tools_dict:
                    prov_tools[name] = cls()
            except Exception as e:
                logger.debug(f"Provider tool import failed: {name} from {module_path} ({e})")
        
        # GLM provider tools (lenient registration)
        # NOTE: glm_web_search is INTERNAL ONLY - auto-injected via build_websearch_provider_kwargs()
        glm_tools = [
            ("glm_upload_file", ("tools.providers.glm.glm_files", "GLMUploadFileTool")),
        ]
        
        for name, (module_path, class_name) in glm_tools:
            try:
                mod = importlib.import_module(module_path)
                cls = getattr(mod, class_name)
                if name not in tools_dict:
                    prov_tools[name] = cls()
            except Exception as e:
                logger.debug(f"Provider tool import failed: {name} from {module_path} ({e})")
        
        if prov_tools:
            logger.info(f"Registering provider-specific tools: {sorted(prov_tools.keys())}")
            tools_dict.update(prov_tools)
            _provider_tools_registered = True
        else:
            logger.debug("No provider-specific tools to register")
            _provider_tools_registered = True
            
    except Exception as e:
        logger.error(f"Failed to register provider-specific tools: {e}")
        # Don't raise - provider tools are optional, core tools still work


# ============================================================================
# UNIFIED BOOTSTRAP FUNCTION
# ============================================================================

def bootstrap_all() -> Dict[str, Any]:
    """
    Perform complete bootstrap: providers + tools + provider tools.
    
    This is the main entry point that should be called by both server.py
    and ws_server.py at module level.
    
    Returns:
        Dict[str, Any]: The unified tool dictionary
    """
    # Step 1: Configure providers
    ensure_providers_configured()
    
    # Step 2: Build tool registry
    tools = ensure_tools_built()
    
    # Step 3: Register provider-specific tools
    ensure_provider_tools_registered(tools)
    
    return tools


# ============================================================================
# QUERY FUNCTIONS
# ============================================================================

def is_providers_configured() -> bool:
    """Check if providers have been configured."""
    return _providers_configured


def is_tools_built() -> bool:
    """Check if tools have been built."""
    return _tools_built


def is_provider_tools_registered() -> bool:
    """Check if provider-specific tools have been registered."""
    return _provider_tools_registered


def get_tools() -> Optional[Dict[str, Any]]:
    """
    Get the tools dictionary if it has been built.
    
    Returns:
        The tools dictionary or None if not yet built
    """
    return _tools_dict


__all__ = [
    "ensure_providers_configured",
    "ensure_tools_built",
    "ensure_provider_tools_registered",
    "bootstrap_all",
    "is_providers_configured",
    "is_tools_built",
    "is_provider_tools_registered",
    "get_tools",
]

