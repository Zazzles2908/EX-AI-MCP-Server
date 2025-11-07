"""
Handler Model Resolution Module

This module centralizes all model resolution logic including:
- Centralized auto routing policy
- Step-aware heuristics for workflow tools
- CJK content detection
- Intelligent selection by tool category
- Hidden sentinel handling
- Provider validation and fallback

Phase 6.4 (2025-11-01): Renamed from request_handler_model_resolution.py to model_resolution.py
"""

import logging
from src.providers.registry_core import get_registry_instance
import os
from src.providers.registry_core import get_registry_instance
from typing import Any, Dict, Optional

from src.router.routing_cache import get_routing_cache

logger = logging.getLogger(__name__)


def _has_cjk(text: str) -> bool:
    """
    Detect CJK (Chinese, Japanese, Korean) characters in text.
    
    Args:
        text: Text to check
        
    Returns:
        True if CJK characters found, False otherwise
    """
    try:
        if not text:
            return False
        # Quick CJK block detection
        return any(
            ("\u4e00" <= ch <= "\u9fff") or  # CJK Unified Ideographs
            ("\u3040" <= ch <= "\u30ff") or  # Hiragana and Katakana
            ("\u3400" <= ch <= "\u4dbf")     # CJK Extension A
            for ch in text
        )
    except Exception:
        return False


def _route_auto_model(tool_name: str, requested: str | None, args: Dict[str, Any]) -> str | None:
    """
    Centralized model:auto routing policy with step-aware heuristics.

    This function implements intelligent model selection based on:
    - Tool type (simple vs workflow)
    - Step number and continuation status
    - Depth parameter
    - Tool-specific requirements

    Args:
        tool_name: Name of the tool being executed
        requested: Requested model name (may be "auto")
        args: Tool arguments including step_number, next_step_required, depth

    Returns:
        Resolved model name or None to use requested
    """
    try:
        # CRITICAL FIX (Bug #4): Respect model lock from continuation
        # When a conversation is continued, preserve the model from previous turn
        if args.get("_model_locked_by_continuation"):
            logger.debug(f"[MODEL_ROUTING] Model locked by continuation - skipping auto-routing")
            return requested  # Skip routing, use continuation model

        # CRITICAL: Kimi file operations routing MUST happen BEFORE early return
        # These tools have model defaults in their schemas, so we need to override
        if tool_name in {"kimi_upload_files", "kimi_chat_with_files", "kimi_manage_files"}:
            selected_model = os.getenv("KIMI_DEFAULT_MODEL", "kimi-k2-0905-preview")
            routing_cache = get_routing_cache()
            cache_context = {
                "tool_name": tool_name,
                "step_number": args.get("step_number"),
                "next_step_required": args.get("next_step_required"),
                "depth": str(args.get("depth") or "").strip().lower()
            }
            routing_cache.set_model_selection(cache_context, selected_model)
            logger.debug(f"[ROUTING_CACHE] Cached auto-routing: {tool_name} → {selected_model}")
            return selected_model

        req = (requested or "").strip().lower()
        if req and req != "auto":
            return requested  # explicit model respected

        # Try cache for auto routing (3min TTL)
        routing_cache = get_routing_cache()
        cache_context = {
            "tool_name": tool_name,
            "step_number": args.get("step_number"),
            "next_step_required": args.get("next_step_required"),
            "depth": str(args.get("depth") or "").strip().lower()
        }
        cached_model = routing_cache.get_model_selection(cache_context)
        if cached_model:
            logger.debug(f"[ROUTING_CACHE] Auto-routing cache HIT: {tool_name} → {cached_model}")
            return cached_model
        
        # Route Kimi-specific tools to Kimi by default
        kimi_tools = {"kimi_chat_with_tools", "kimi_upload_and_extract"}
        if tool_name in kimi_tools:
            selected_model = os.getenv("KIMI_SPEED_MODEL", "kimi-k2-0905-preview")
            routing_cache.set_model_selection(cache_context, selected_model)
            logger.debug(f"[ROUTING_CACHE] Cached auto-routing: {tool_name} → {selected_model}")
            return selected_model

        # Simple tools use fast model (AI Manager)
        simple_tools = {"chat", "status", "provider_capabilities", "listmodels", "activity", "version"}
        if tool_name in simple_tools:
            selected_model = os.getenv("GLM_SPEED_MODEL", "glm-4.5-flash")
            routing_cache.set_model_selection(cache_context, selected_model)
            logger.debug(f"[ROUTING_CACHE] Cached auto-routing: {tool_name} → {selected_model}")
            return selected_model

        # Step-aware heuristics for workflows (Option B)
        step_number = args.get("step_number")
        next_step_required = args.get("next_step_required")
        depth = str(args.get("depth") or "").strip().lower()

        # thinkdeep: always deep
        if tool_name == "thinkdeep":
            selected_model = os.getenv("KIMI_QUALITY_MODEL", "kimi-thinking-preview")
            routing_cache.set_model_selection(cache_context, selected_model)
            logger.debug(f"[ROUTING_CACHE] Cached auto-routing: {tool_name} → {selected_model}")
            return selected_model

        # analyze
        if tool_name == "analyze":
            if (step_number == 1 and (next_step_required is True)):
                selected_model = os.getenv("GLM_SPEED_MODEL", "glm-4.5-flash")
            else:
                # final step or unknown -> deep by default
                selected_model = os.getenv("KIMI_QUALITY_MODEL", "kimi-thinking-preview")
            routing_cache.set_model_selection(cache_context, selected_model)
            logger.debug(f"[ROUTING_CACHE] Cached auto-routing: {tool_name} → {selected_model}")
            return selected_model

        # codereview/refactor/debug/testgen/planner
        if tool_name in {"codereview", "refactor", "debug", "testgen", "planner"}:
            if depth == "deep" or (next_step_required is False):
                selected_model = os.getenv("KIMI_QUALITY_MODEL", "kimi-thinking-preview")
            elif step_number == 1:
                selected_model = os.getenv("GLM_SPEED_MODEL", "glm-4.5-flash")
            else:
                # Default lean toward flash unless final/deep
                selected_model = os.getenv("GLM_SPEED_MODEL", "glm-4.5-flash")
            routing_cache.set_model_selection(cache_context, selected_model)
            logger.debug(f"[ROUTING_CACHE] Cached auto-routing: {tool_name} → {selected_model}")
            return selected_model

        # consensus/docgen/secaudit: deep
        if tool_name in {"consensus", "docgen", "secaudit"}:
            selected_model = os.getenv("KIMI_QUALITY_MODEL", "kimi-thinking-preview")
            routing_cache.set_model_selection(cache_context, selected_model)
            logger.debug(f"[ROUTING_CACHE] Cached auto-routing: {tool_name} → {selected_model}")
            return selected_model

        # Default: prefer GLM flash (AI Manager)
        selected_model = os.getenv("GLM_SPEED_MODEL", "glm-4.5-flash")
        routing_cache.set_model_selection(cache_context, selected_model)
        logger.debug(f"[ROUTING_CACHE] Cached auto-routing: {tool_name} → {selected_model}")
        return selected_model
    except Exception:
        # BUG FIX: Never return 'auto' - always return a concrete model
        # If there's an exception, fall back to the default speed model
        return os.getenv("GLM_SPEED_MODEL", "glm-4.5-flash")


def resolve_auto_model_legacy(args: Dict[str, Any], tool_obj, os_module=os) -> str:
    """
    Backward-compatible auto model selection.
    
    This function implements the legacy auto-selection logic based on:
    - Locale and CJK content detection
    - Tool category (extended reasoning, balanced, fast)
    - Provider availability
    - Local-only requirements
    
    Args:
        args: Tool arguments
        tool_obj: Tool object with get_model_category method
        os_module: OS module (for testing)
        
    Returns:
        Selected model name
    """
    from src.providers.registry import ModelProviderRegistry
    from src.providers.base import ProviderType
    
    # Inspect providers
    available = ModelProviderRegistry.get_available_models(respect_restrictions=True)
    has_glm = any(pt == ProviderType.GLM for pt in available.values())
    has_kimi = any(pt == ProviderType.KIMI for pt in available.values())
    has_custom = any(pt == ProviderType.CUSTOM for pt in available.values())
    
    locale = os_module.getenv("LOCALE", "").lower()
    prompt = args.get("prompt", "") or args.get("_original_user_prompt", "") or ""
    local_only = bool(args.get("local_only"))
    chosen = None
    reason = None
    
    # Intelligent selection by tool category (env-gated)
    try:
        if os.getenv("ENABLE_INTELLIGENT_SELECTION", "true").strip().lower() == "true":
            cat_obj = tool_obj.get_model_category() if hasattr(tool_obj, "get_model_category") else None
            cat_name = getattr(cat_obj, "name", None)
            if cat_name:
                # Choose quality-tier for extended reasoning; speed-tier for fast/balanced
                if cat_name == "EXTENDED_REASONING":
                    if (locale.startswith("zh") or _has_cjk(prompt)) and has_kimi:
                        chosen = os.getenv("KIMI_QUALITY_MODEL", os.getenv("KIMI_DEFAULT_MODEL", "kimi-k2-0711-preview"))
                        reason = "intelligent_ext_reasoning_kimi"
                    elif has_glm:
                        chosen = os.getenv("GLM_QUALITY_MODEL", "glm-4.5")
                        reason = "intelligent_ext_reasoning_glm"
                elif cat_name in ("BALANCED", "FAST_RESPONSE"):
                    if has_glm:
                        chosen = os.getenv("GLM_SPEED_MODEL", "glm-4.5-flash")
                        reason = "intelligent_speed_glm"
                    elif has_kimi:
                        chosen = os.getenv("KIMI_SPEED_MODEL", "kimi-k2-turbo-preview")
                        reason = "intelligent_speed_kimi"
                # If still not chosen, fall through to legacy logic below
    except Exception as e:
        logger.debug(f"Intelligent routing failed, falling back to legacy logic: {e}")
    
    # 1) Locale or content indicates CJK → prefer Kimi
    if not chosen and (locale.startswith("zh") or _has_cjk(prompt)) and has_kimi:
        chosen = os.getenv("KIMI_DEFAULT_MODEL", "kimi-k2-0711-preview")
        reason = "cjk_locale_or_content"
    # 2) Local-only tasks → prefer Custom
    elif not chosen and local_only and has_custom:
        chosen = os.getenv("CUSTOM_MODEL_NAME", "llama3.2")
        reason = "local_only"
    # 3) Default GLM fast model if present
    elif not chosen and has_glm:
        chosen = "glm-4.5-flash"
        reason = "default_glm"
    # 4) Provider-registry fallback by tool category
    else:
        if not chosen:
            cat = tool_obj.get_model_category() if hasattr(tool_obj, "get_model_category") else None
            chosen = ModelProviderRegistry.get_preferred_fallback_model(cat)
            reason = "provider_fallback"
    
    # Log structured selection
    try:
        sel_log = {
            "event": "auto_model_selected",
            "tool": getattr(tool_obj, "__class__", type(tool_obj)).__name__,
            "model": chosen,
            "reason": reason,
            "locale": locale,
            "has_cjk": _has_cjk(prompt),
            "local_only": local_only,
        }
        logger.info(sel_log)
    except Exception:
        pass
    
    return chosen


def validate_and_fallback_model(model_name: str, tool_name: str, tool_obj, req_id: str, configure_providers_func) -> tuple[str, Optional[str]]:
    """
    Validate model availability and apply graceful fallback.
    
    Args:
        model_name: Model name to validate
        tool_name: Tool name for logging
        tool_obj: Tool object
        req_id: Request ID for logging
        configure_providers_func: Function to configure providers
        
    Returns:
        Tuple of (validated_model_name, error_message)
        error_message is None if validation successful
    """
    from src.providers.registry import ModelProviderRegistry
    
    provider = get_registry_instance().get_provider_for_model(model_name)
    if not provider:
        # Try to recover gracefully before failing
        available_models = list(ModelProviderRegistry.get_available_models(respect_restrictions=True).keys())
        if not available_models:
            # Providers may not be initialized in this process yet; try again
            try:
                configure_providers_func()
                available_models = list(ModelProviderRegistry.get_available_models(respect_restrictions=True).keys())
                provider = get_registry_instance().get_provider_for_model(model_name)
            except Exception as _e:
                logger.debug(f"configure_providers() retry failed: {_e}")
        
        if not provider:
            tool_category = tool_obj.get_model_category()
            suggested_model = ModelProviderRegistry.get_preferred_fallback_model(tool_category)
            # If we have a suggested model, auto-fallback instead of erroring
            if suggested_model and suggested_model != model_name:
                # CRITICAL FIX (Bug #8): Warn user about invalid model and fallback
                # Previously this was silent, which confused users about which model was actually used
                logger.warning(
                    f"[MODEL_VALIDATION] Invalid model '{model_name}' requested for tool '{tool_name}'. "
                    f"Falling back to '{suggested_model}'. "
                    f"Available models: {', '.join(available_models[:5])}{'...' if len(available_models) > 5 else ''}"
                )
                logger.info(f"[BOUNDARY] Auto-fallback: '{model_name}' -> '{suggested_model}' for tool {tool_name}")
                return suggested_model, None
            else:
                error_message = (
                    f"Model '{model_name}' is not available with current API keys. "
                    f"Available models: {', '.join(available_models)}. "
                    f"Suggested model for {tool_name}: '{suggested_model}' "
                    f"(category: {tool_category.value})"
                )
                return model_name, error_message
    
    return model_name, None


# Export public API
__all__ = [
    '_has_cjk',
    '_route_auto_model',
    'resolve_auto_model_legacy',
    'validate_and_fallback_model',
]

