"""
Provider Detection Module

Handles detection and validation of available AI model providers.
Checks API keys, validates configurations, and performs lazy imports.
"""

import logging
import os
from typing import Any, Optional, Tuple

logger = logging.getLogger(__name__)


def _check_api_key(key_name: str, alias_name: Optional[str] = None) -> Optional[str]:
    """
    Check for API key in environment, supporting vendor aliases.
    
    Args:
        key_name: Primary environment variable name
        alias_name: Optional alias environment variable name
        
    Returns:
        API key if found and valid, None otherwise
    """
    key = os.getenv(key_name)
    if alias_name:
        key = key or os.getenv(alias_name)
    
    # Check if key exists and is not a placeholder
    if key and key not in ("your_kimi_api_key_here", "your_glm_api_key_here", "your_openrouter_api_key_here"):
        return key
    return None


def _is_provider_allowed(provider_name: str, disabled_providers: set, allowed_providers: set) -> bool:
    """
    Check if provider is allowed based on gating configuration.
    
    Args:
        provider_name: Provider name (uppercase)
        disabled_providers: Set of disabled provider names
        allowed_providers: Set of allowed provider names (empty = all allowed)
        
    Returns:
        True if provider is allowed, False otherwise
    """
    if provider_name in disabled_providers:
        return False
    if allowed_providers and provider_name not in allowed_providers:
        return False
    return True


def detect_kimi_provider(disabled_providers: set, allowed_providers: set) -> Tuple[bool, Optional[Any], Optional[str]]:
    """
    Detect Kimi provider availability.
    
    Args:
        disabled_providers: Set of disabled provider names
        allowed_providers: Set of allowed provider names
        
    Returns:
        Tuple of (is_available, provider_class, api_key)
    """
    # Check API key (accept vendor alias)
    kimi_key = _check_api_key("KIMI_API_KEY", "MOONSHOT_API_KEY")
    
    if not kimi_key:
        return False, None, None
    
    if not _is_provider_allowed("KIMI", disabled_providers, allowed_providers):
        return False, None, None
    
    # Try to import provider class
    try:
        from src.providers.kimi import KimiModelProvider
        logger.info("Kimi API key found - Moonshot AI models available")
        return True, KimiModelProvider, kimi_key
    except Exception as e:
        logger.warning(f"Kimi provider import failed: {e}; continuing without Kimi")
        return False, None, None


def detect_glm_provider(disabled_providers: set, allowed_providers: set) -> Tuple[bool, Optional[Any], Optional[str]]:
    """
    Detect GLM provider availability.
    
    Args:
        disabled_providers: Set of disabled provider names
        allowed_providers: Set of allowed provider names
        
    Returns:
        Tuple of (is_available, provider_class, api_key)
    """
    # Check API key (accept vendor alias)
    glm_key = _check_api_key("GLM_API_KEY", "ZHIPUAI_API_KEY")
    
    if not glm_key:
        return False, None, None
    
    if not _is_provider_allowed("GLM", disabled_providers, allowed_providers):
        return False, None, None
    
    # Try to import provider class
    try:
        from src.providers.glm import GLMModelProvider
        logger.info("GLM API key found - ZhipuAI models available")
        return True, GLMModelProvider, glm_key
    except Exception as e:
        logger.warning(f"GLM provider import failed: {e}; continuing without GLM")
        return False, None, None


def detect_openrouter_provider() -> Tuple[bool, Optional[str]]:
    """
    Detect OpenRouter provider availability.
    
    Returns:
        Tuple of (is_available, api_key)
    """
    # Check if OpenRouter is enabled
    enable_openrouter = os.getenv("ENABLE_OPENROUTER", "false").strip().lower() in ("1", "true", "yes")
    
    if not enable_openrouter:
        logger.debug("OpenRouter disabled by ENABLE_OPENROUTER=false (default)")
        return False, None
    
    # Check API key
    openrouter_key = _check_api_key("OPENROUTER_API_KEY")
    
    if not openrouter_key:
        logger.debug("OpenRouter API key not found in environment")
        return False, None
    
    logger.info("OpenRouter enabled and API key found - Multiple models available via OpenRouter")
    return True, openrouter_key


def detect_custom_provider() -> Tuple[bool, Optional[Any], Optional[str], Optional[str]]:
    """
    Detect custom provider availability (Ollama, vLLM, etc.).
    
    Returns:
        Tuple of (is_available, provider_class, api_key, base_url)
    """
    # Check if custom provider is enabled
    enable_custom = os.getenv("ENABLE_CUSTOM", "false").strip().lower() in ("1", "true", "yes")
    
    if not enable_custom:
        logger.debug("Custom provider disabled by ENABLE_CUSTOM=false (default)")
        return False, None, None, None
    
    # Check for custom API URL
    custom_url = os.getenv("CUSTOM_API_URL")
    
    if not custom_url:
        logger.debug("Custom API URL not found in environment")
        return False, None, None, None
    
    # Try to import custom provider
    try:
        from src.providers.custom import CustomProvider
        
        # Get API key (can be empty for Ollama)
        custom_key = os.getenv("CUSTOM_API_KEY", "")
        custom_model = os.getenv("CUSTOM_MODEL_NAME", "llama3.2")
        
        logger.info(f"Custom API enabled; endpoint: {custom_url} with model {custom_model}")
        if custom_key:
            logger.debug("Custom API key provided for authentication")
        else:
            logger.debug("No custom API key provided (using unauthenticated access)")
        
        return True, CustomProvider, custom_key, custom_url
    except Exception as e:
        logger.warning(f"Custom provider module not available: {e}; skipping custom provider registration")
        return False, None, None, None


def detect_all_providers() -> dict:
    """
    Detect all available providers.
    
    Returns:
        Dict with provider configuration:
        {
            'disabled_providers': set,
            'allowed_providers': set,
            'kimi': {'available': bool, 'class': class, 'key': str},
            'glm': {'available': bool, 'class': class, 'key': str},
            'openrouter': {'available': bool, 'key': str},
            'custom': {'available': bool, 'class': class, 'key': str, 'url': str},
            'valid_providers': list[str],
            'has_native_apis': bool,
            'has_openrouter': bool,
            'has_custom': bool
        }
    """
    # Log environment variable status
    logger.debug("Checking environment variables for API keys...")
    api_keys_to_check = ["KIMI_API_KEY", "GLM_API_KEY", "OPENROUTER_API_KEY", "CUSTOM_API_URL"]
    for key in api_keys_to_check:
        value = os.getenv(key)
        logger.debug(f"  {key}: {'[PRESENT]' if value else '[MISSING]'}")
    
    # Parse provider gating configuration
    disabled_providers = {p.strip().upper() for p in os.getenv("DISABLED_PROVIDERS", "").split(",") if p.strip()}
    allowed_providers = {p.strip().upper() for p in os.getenv("ALLOWED_PROVIDERS", "").split(",") if p.strip()}
    
    # Force-disable providers we don't support in this deployment
    disabled_providers.update({"GOOGLE", "OPENAI", "XAI", "DIAL"})
    
    # Detect each provider
    kimi_available, kimi_class, kimi_key = detect_kimi_provider(disabled_providers, allowed_providers)
    glm_available, glm_class, glm_key = detect_glm_provider(disabled_providers, allowed_providers)
    openrouter_available, openrouter_key = detect_openrouter_provider()
    custom_available, custom_class, custom_key, custom_url = detect_custom_provider()
    
    # Build valid providers list
    valid_providers = []
    if kimi_available:
        valid_providers.append("Kimi")
    if glm_available:
        valid_providers.append("GLM")
    if openrouter_available:
        valid_providers.append("OpenRouter")
    if custom_available:
        valid_providers.append(f"Custom API ({custom_url})")
    
    # Determine provider categories
    has_native_apis = kimi_available or glm_available
    has_openrouter = openrouter_available
    has_custom = custom_available
    
    return {
        'disabled_providers': disabled_providers,
        'allowed_providers': allowed_providers,
        'kimi': {
            'available': kimi_available,
            'class': kimi_class,
            'key': kimi_key
        },
        'glm': {
            'available': glm_available,
            'class': glm_class,
            'key': glm_key
        },
        'openrouter': {
            'available': openrouter_available,
            'key': openrouter_key
        },
        'custom': {
            'available': custom_available,
            'class': custom_class,
            'key': custom_key,
            'url': custom_url
        },
        'valid_providers': valid_providers,
        'has_native_apis': has_native_apis,
        'has_openrouter': has_openrouter,
        'has_custom': has_custom
    }

