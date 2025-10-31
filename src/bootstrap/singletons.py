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
- WEEK 1 FIX #3 (2025-10-21): Corrected misleading GIL documentation
- The GIL prevents corruption of individual Python objects (like booleans)
- The import lock ensures this module is initialized only once per process
- IMPORTANT: The GIL does NOT prevent race conditions in check-then-act patterns
  within functions called after module import
- Current implementation relies on import lock for safety during module initialization
- For thread-safe post-import calls, proper locking (threading.Lock) would be required
- In practice, these functions are called during startup before concurrent access begins
"""

import logging
import os
import threading
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

# WEEK 1 FIX #4 (2025-10-21): Add locks to prevent check-then-act race conditions
# Double-checked locking pattern: fast path without lock, slow path with lock + double-check
_providers_lock = threading.Lock()
_tools_lock = threading.Lock()
_provider_tools_lock = threading.Lock()

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

    WEEK 1 FIX #4 (2025-10-21): Added double-checked locking to prevent race conditions

    Raises:
        ValueError: If no valid API keys are found
    """
    global _providers_configured

    # Fast path: no lock needed if already configured
    if _providers_configured:
        logger.debug("Providers already configured, skipping")
        return

    # Slow path: acquire lock and double-check
    with _providers_lock:
        # Double-check inside lock (another thread may have initialized while we waited)
        if _providers_configured:
            logger.debug("Providers already configured (confirmed in lock), skipping")
            return

        try:
            # NOTE: This imports from src/server/providers/provider_config.py
            # which is a thin orchestrator that delegates to helper modules
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

    WEEK 1 FIX #4 (2025-10-21): Added double-checked locking to prevent race conditions

    Returns:
        Dict[str, Any]: The unified tool dictionary (same object reference)
    """
    global _tools_built, _tool_registry, _tools_dict

    # Fast path: no lock needed if already built
    if _tools_built and _tools_dict is not None:
        logger.debug("Tools already built, returning existing dict")
        return _tools_dict

    # Slow path: acquire lock and double-check
    with _tools_lock:
        # Double-check inside lock (another thread may have built while we waited)
        if _tools_built and _tools_dict is not None:
            logger.debug("Tools already built (confirmed in lock), returning existing dict")
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

    WEEK 1 FIX #4 (2025-10-21): Added double-checked locking to prevent race conditions

    Args:
        tools_dict: The tool dictionary to mutate with provider-specific tools
    """
    global _provider_tools_registered

    # Fast path: no lock needed if already registered
    if _provider_tools_registered:
        logger.debug("Provider-specific tools already registered, skipping")
        return

    # Early exit if providers not configured (no lock needed for read-only check)
    if not _providers_configured:
        logger.info("Provider tools will be registered after providers are configured")
        return

    # Slow path: acquire lock and double-check
    with _provider_tools_lock:
        # Double-check inside lock (another thread may have registered while we waited)
        if _provider_tools_registered:
            logger.debug("Provider-specific tools already registered (confirmed in lock), skipping")
            return

        try:
            import importlib

            prov_tools: Dict[str, Any] = {}

            # Kimi provider tools (lenient registration)
            # Phase A2 Cleanup: Removed kimi_upload_files and kimi_chat_with_files (use smart_file_query)
            kimi_tools = [
                ("kimi_manage_files", ("tools.providers.kimi.kimi_files", "KimiManageFilesTool")),
                ("kimi_intent_analysis", ("tools.providers.kimi.kimi_intent", "KimiIntentAnalysisTool")),
            ]

            for name, (module_path, class_name) in kimi_tools:
                try:
                    logger.info(f"[PROVIDER_TOOLS] Attempting to import {name} from {module_path}.{class_name}")
                    mod = importlib.import_module(module_path)
                    cls = getattr(mod, class_name)
                    if name not in tools_dict:
                        prov_tools[name] = cls()
                        logger.info(f"[PROVIDER_TOOLS] Successfully registered {name}")
                    else:
                        logger.info(f"[PROVIDER_TOOLS] Skipping {name} - already in registry")
                except Exception as e:
                    logger.error(f"[PROVIDER_TOOLS] Provider tool import failed: {name} from {module_path} ({e})")
                    import traceback
                    logger.error(f"[PROVIDER_TOOLS] Traceback: {traceback.format_exc()}")

            # GLM provider tools (lenient registration)
            # NOTE: glm_web_search is INTERNAL ONLY - auto-injected via build_websearch_provider_kwargs()
            # Phase A2 Cleanup: Removed glm_upload_file and glm_multi_file_chat (use smart_file_query)
            glm_tools = [
                # All file operations now handled by smart_file_query
            ]

            for name, (module_path, class_name) in glm_tools:
                try:
                    logger.info(f"[PROVIDER_TOOLS] Attempting to import {name} from {module_path}.{class_name}")
                    mod = importlib.import_module(module_path)
                    cls = getattr(mod, class_name)
                    if name not in tools_dict:
                        prov_tools[name] = cls()
                        logger.info(f"[PROVIDER_TOOLS] Successfully registered {name}")
                    else:
                        logger.info(f"[PROVIDER_TOOLS] Skipping {name} - already in registry")
                except Exception as e:
                    logger.error(f"[PROVIDER_TOOLS] Provider tool import failed: {name} from {module_path} ({e})")
                    import traceback
                    logger.error(f"[PROVIDER_TOOLS] Traceback: {traceback.format_exc()}")

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

