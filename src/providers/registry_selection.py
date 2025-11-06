"""
Provider Registry Selection and Fallback Logic

This module provides model selection, fallback chains, and diagnostics for the provider registry.

Key Components:
- Model selection methods (get_preferred_fallback_model, get_best_provider_for_category)
- Fallback chain logic (_auggie_fallback_chain, call_with_fallback)
- Helper methods for model filtering (_get_allowed_models_for_provider)
- ProviderDiagnostics class for troubleshooting provider availability

For core registry functionality, see registry_core.py
For configuration and health monitoring, see registry_config.py
"""

import logging
import os
import time as _t
from typing import Any, Optional, TYPE_CHECKING

from src.providers.base import ModelProvider, ProviderType

# Import error handling framework
from src.daemon.error_handling import ProviderError, ErrorCode, log_error

logger = logging.getLogger(__name__)
from src.providers.registry_config import _apply_cost_aware, _apply_free_first
from src.router.routing_cache import get_routing_cache

if TYPE_CHECKING:
    from tools.models import ToolModelCategory


# ================================================================================
# Model Selection Methods (Mixin for ModelProviderRegistry)
# ================================================================================
# These methods will be added to ModelProviderRegistry via composition


def get_preferred_fallback_model(
    registry_instance, tool_category: Optional["ToolModelCategory"] = None
) -> str:
    """
    Select a reasonable fallback model across providers.

    Strategy:
    1) For each provider in priority order, get allowed models
    2) Apply cost-aware + free-tier ordering
    3) Ask provider for preference; else take first allowed
    4) If nothing available, default to a safe GLM/Kimi model present in stack
    """
    # Try cache first (3min TTL)
    routing_cache = get_routing_cache()
    cache_context = {"tool_category": str(tool_category) if tool_category else "BALANCED"}
    cached_model = routing_cache.get_model_selection(cache_context)
    if cached_model:
        logger.debug(f"[ROUTING_CACHE] Fallback model cache HIT: {cached_model}")
        return cached_model

    try:
        from tools.models import ToolModelCategory as _Cat
    except Exception:

        class _Cat:  # minimal stub
            FAST_RESPONSE = object()
            EXTENDED_REASONING = object()
            BALANCED = object()

    effective_cat = tool_category or getattr(_Cat, "BALANCED")

    first_available: Optional[str] = None

    # Import registry class to access class methods
    from src.providers.registry_core import ModelProviderRegistry as cls

    for ptype in cls.PROVIDER_PRIORITY_ORDER:
        prov = cls.get_provider(ptype)
        if not prov:
            continue
        try:
            allowed = _get_allowed_models_for_provider(prov, ptype)
        except Exception:
            # Fallback to provider list when helper is not available
            try:
                allowed = prov.list_models(respect_restrictions=True)
            except Exception:
                allowed = []
        if not allowed:
            continue
        # Track first available
        if not first_available:
            first_available = sorted(allowed)[0]
        # Intra-provider ordering
        ordered = _apply_free_first(_apply_cost_aware(list(allowed), effective_cat))
        # Ask provider for preference
        try:
            chosen = prov.get_preferred_model(effective_cat, ordered)  # type: ignore[attr-defined]
        except Exception:
            chosen = None
        if chosen:
            # Cache the selection (3min TTL)
            routing_cache.set_model_selection(cache_context, chosen)
            logger.debug(f"[ROUTING_CACHE] Cached fallback model: {chosen}")
            return chosen
        # Otherwise pick first ordered
        if ordered:
            # Cache the selection (3min TTL)
            routing_cache.set_model_selection(cache_context, ordered[0])
            logger.debug(f"[ROUTING_CACHE] Cached fallback model: {ordered[0]}")
            return ordered[0]

    # Cross-provider default if nothing chosen
    default_model = os.getenv("DEFAULT_MODEL", "glm-4.5-flash") or "glm-4.5-flash"
    try:
        if cls.get_provider(ProviderType.GLM):
            default_model = "glm-4.5-flash"
        elif cls.get_provider(ProviderType.KIMI):
            default_model = "kimi-k2-0711-preview"
    except Exception:
        pass

    # Cache the default (3min TTL)
    routing_cache.set_model_selection(cache_context, default_model)
    logger.debug(f"[ROUTING_CACHE] Cached fallback model (default): {default_model}")
    return default_model


def get_best_provider_for_category(
    registry_instance,
    category: "ToolModelCategory",
    allowed_models: list[str],
) -> Optional[tuple[ModelProvider, str]]:
    """
    Select best provider and model for a functional category.

    This implements environment preferences and cost-aware routing.
    """
    # Import registry class to access class methods
    from src.providers.registry_core import ModelProviderRegistry as cls

    # 1) Aggregate allowed by provider while preserving priority order
    available = cls.get_available_models(respect_restrictions=True)
    by_provider: dict[ProviderType, list[str]] = {}
    for name, ptype in available.items():
        if name in allowed_models:
            by_provider.setdefault(ptype, []).append(name)

    # Apply free-tier preference then cost-aware ordering within each provider
    for ptype, names in list(by_provider.items()):
        names = _apply_free_first(names)
        names = _apply_cost_aware(names, category)
        by_provider[ptype] = names

    # 2) Provider priority selection
    for ptype in cls.PROVIDER_PRIORITY_ORDER:
        if ptype not in by_provider or not by_provider[ptype]:
            continue
        provider = cls.get_provider(ptype)
        if not provider:
            continue

        # Provider-specific preference env var
        preferred = provider.get_preferred_model(category, by_provider[ptype])
        chosen = preferred or (by_provider[ptype][0] if by_provider[ptype] else None)
        if chosen:
            return provider, chosen

    return None


def _get_allowed_models_for_provider(provider: ModelProvider, provider_type: ProviderType) -> list[str]:
    """
    Return canonical model names supported by a provider after restriction filtering.
    Uses provider.list_models(respect_restrictions=False) when available, otherwise
    falls back to the provider's SUPPORTED_MODELS keys.
    """
    try:
        from utils.model.restrictions import get_restriction_service
    except Exception:
        get_restriction_service = None  # type: ignore

    restriction_service = get_restriction_service() if get_restriction_service else None

    # Gather supported models without double-filtering
    try:
        supported = provider.list_models(respect_restrictions=False)
    except (NotImplementedError, AttributeError):
        try:
            supported = list(getattr(provider, "SUPPORTED_MODELS", {}).keys())
        except Exception:
            supported = []

    allowed: list[str] = []
    for name in supported:
        try:
            if restriction_service is None or restriction_service.is_allowed(provider_type, name, name):
                allowed.append(name)
        except Exception:
            # Be permissive under diagnostics/transient failures
            allowed.append(name)
    return allowed


# ================================================================================
# Fallback Chain Logic
# ================================================================================


def _auggie_fallback_chain(
    registry_instance,
    category: Optional["ToolModelCategory"],
    hints: Optional[list[str]] = None,
) -> list[str]:
    """
    Return a prioritized list of candidate models for a category.

    SIMPLIFIED FALLBACK STRATEGY (2025-10-16):
    - FAST_RESPONSE: Only GLM-4.6 (no fallback to Kimi models)
    - EXTENDED_REASONING: Kimi K2 models only
    - BALANCED: GLM-4.5 series

    This prevents cascading timeouts through multiple providers.
    """
    # Import registry class to access class methods
    from src.providers.registry_core import ModelProviderRegistry as cls

    # Import category enum
    try:
        from tools.models import ToolModelCategory as _Cat
    except Exception:
        class _Cat:  # minimal stub
            FAST_RESPONSE = object()
            EXTENDED_REASONING = object()
            BALANCED = object()

    # 1) Try explicit chains from auggie settings
    try:
        from auggie.config import get_auggie_settings  # type: ignore[import-not-found]

        settings = get_auggie_settings() or {}
        fb = settings.get("fallback") or {}
        key = None
        if category is not None:
            try:
                # Map commonly used aliases
                key = {
                    "FAST_RESPONSE": "chat",
                    "EXTENDED_REASONING": "reasoning",
                }.get(category.name, category.name.lower())
            except Exception:
                key = None
        chain = fb.get(key or "", [])
        if chain:
            # If hints provided, lightly bias order
            if hints:
                low_map = {m.lower(): m for m in chain}
                priorities: list[str] = []
                for h in [s.lower() for s in hints if isinstance(s, str)]:
                    if any(k in h for k in ("vision", "image", "diagram")):
                        for cand in ("glm-4.5v",):
                            m = low_map.get(cand)
                            if m and m not in priorities:
                                priorities.append(m)
                    if any(k in h for k in ("think", "reason", "chain of thought", "cot", "deep")):
                        for cand in ("kimi-k2-thinking", "kimi-k2-0711-preview", "glm-4.5-airx"):
                            m = low_map.get(cand)
                            if m and m not in priorities:
                                priorities.append(m)
                rest = [m for m in chain if m not in priorities]
                return priorities + rest
            return chain
    except Exception:
        pass

    # 2) SIMPLIFIED: Category-specific fallback chains (NO cross-provider fallback)
    order: list[str] = []

    if category is not None:
        try:
            cat_name = category.name
        except Exception:
            cat_name = None

        if cat_name == "FAST_RESPONSE":
            # FAST_RESPONSE: Only GLM models (no Kimi fallback)
            order = ["glm-4.6", "glm-4.5-flash", "glm-4.5"]
        elif cat_name == "EXTENDED_REASONING":
            # EXTENDED_REASONING: Only Kimi K2 models
            order = ["kimi-k2-0905-preview", "kimi-k2-0711-preview", "kimi-thinking-preview"]
        elif cat_name == "BALANCED":
            # BALANCED: GLM-4.5 series
            order = ["glm-4.5", "glm-4.5-air", "glm-4.6"]
        else:
            # Unknown category: use GLM-4.6 as safe default
            order = ["glm-4.6"]
    else:
        # No category: use GLM-4.6 as safe default
        order = ["glm-4.6"]

    # 3) Hint-based biasing (vision/thinking)
    if hints:
        low_map = {m.lower(): m for m in order}
        priorities = []
        for h in [s.lower() for s in hints if isinstance(s, str)]:
            if any(k in h for k in ("vision", "image", "diagram")):
                for cand in ("glm-4.5v",):
                    m = low_map.get(cand)
                    if m and m not in priorities:
                        priorities.append(m)
            if any(k in h for k in ("think", "reason", "chain of thought", "cot", "deep")):
                for cand in ("kimi-k2-thinking", "kimi-k2-0711-preview", "glm-4.5-airx"):
                    m = low_map.get(cand)
                    if m and m not in priorities:
                        priorities.append(m)
        rest = [m for m in order if m not in priorities]
        order = priorities + rest

    return order


def call_with_fallback(
    registry_instance,
    category: Optional["ToolModelCategory"],
    call_fn,
    hints: Optional[list[str]] = None,
    max_attempts: int = 2,  # CHANGED 2025-10-16: Limit to 2 attempts to prevent cascading timeouts
):
    """
    Execute call_fn(model_name) over a category-aware fallback chain.
    Records lightweight telemetry for each attempt and returns the first
    successful response. Raises the last exception if all attempts fail.

    Args:
        registry_instance: Registry instance
        category: Tool model category for fallback selection
        call_fn: Function to call with model_name parameter
        hints: Optional hints for model selection
        max_attempts: Maximum number of fallback attempts (default: 2)
    """
    # Import registry class to access class methods
    from src.providers.registry_core import ModelProviderRegistry as cls

    chain = _auggie_fallback_chain(registry_instance, category, hints)

    # LIMIT ATTEMPTS: Prevent cascading timeouts through multiple providers
    chain = chain[:max_attempts]

    last_exc: Exception | None = None
    for attempt_num, model in enumerate(chain, 1):
        t0 = _t.perf_counter()
        try:
            logging.info(f"Fallback attempt {attempt_num}/{len(chain)}: trying model '{model}'")
            resp = call_fn(model)
            dt_ms = (_t.perf_counter() - t0) * 1000.0
            if resp is None:
                # Record failure with no usage
                cls.record_telemetry(model, False, latency_ms=dt_ms)
                # JSONL error logging for None response
                try:
                    from utils.observability import record_error

                    prov = cls.get_provider_for_model(model)
                    ptype = prov.get_provider_type() if prov else None
                    provider = (
                        getattr(ptype, "value", getattr(ptype, "name", "unknown")) if ptype else "unknown"
                    )
                    record_error(str(provider), model, "call_failed_none", "Provider returned None")
                except Exception:
                    pass
                log_error(ErrorCode.PROVIDER_ERROR, f"Provider returned None for model '{model}'")
                raise ProviderError(provider, Exception(f"Provider returned None for model '{model}'"))
            # Best-effort usage capture for success telemetry
            usage = getattr(resp, "usage", {}) or {}
            cls.record_telemetry(
                model,
                True,
                input_tokens=int(usage.get("input_tokens", 0) or 0),
                output_tokens=int(usage.get("output_tokens", 0) or 0),
                latency_ms=dt_ms,
            )
            logging.info(f"Fallback attempt {attempt_num}/{len(chain)}: SUCCESS with model '{model}' ({dt_ms:.0f}ms)")
            return resp
        except Exception as e:
            # Calculate duration even if call_fn failed before dt_ms was set
            try:
                dt_ms = (_t.perf_counter() - t0) * 1000.0
            except Exception:
                dt_ms = 0.0  # Fallback if perf_counter fails
            cls.record_telemetry(model, False, latency_ms=dt_ms)
            # JSONL error logging for exception
            try:
                from utils.observability import record_error

                prov = cls.get_provider_for_model(model)
                ptype = prov.get_provider_type() if prov else None
                provider = getattr(ptype, "value", getattr(ptype, "name", "unknown")) if ptype else "unknown"
                record_error(str(provider), model, "call_failed", str(e))
            except Exception:
                pass
            logging.warning(f"Fallback attempt {attempt_num}/{len(chain)}: FAILED with model '{model}' ({dt_ms:.0f}ms): {e}")
            last_exc = e
            continue
    if last_exc:
        raise last_exc
    log_error(ErrorCode.PROVIDER_ERROR, "No models available for fallback execution")
    raise ProviderError("Registry", Exception("No models available for fallback execution"))


# ================================================================================
# Provider Diagnostics
# ================================================================================


class ProviderDiagnostics:
    """
    Lightweight diagnostics for provider availability without importing server modules.

    Provides structured insights into why a provider may be unavailable, focusing on
    environment variables and registry state. Avoids circular imports by design.
    """

    _API_KEY_VARS = {
        ProviderType.KIMI: ["KIMI_API_KEY", "MOONSHOT_API_KEY"],
        ProviderType.GLM: ["GLM_API_KEY", "ZHIPUAI_API_KEY"],
        ProviderType.CUSTOM: ["CUSTOM_API_KEY"],
        ProviderType.OPENROUTER: ["OPENROUTER_API_KEY"],
    }

    _BASE_URL_VARS = {
        ProviderType.KIMI: ["KIMI_API_URL", "MOONSHOT_API_URL"],
        ProviderType.GLM: ["GLM_API_URL", "ZHIPUAI_API_URL"],
        ProviderType.CUSTOM: ["CUSTOM_API_URL"],
        # OPENROUTER typically does not require a base URL override
    }

    @classmethod
    def _first_present(cls, names: list[str]) -> tuple[str | None, str | None]:
        for n in names or []:
            v = os.getenv(n)
            if v:
                return n, v
        return None, None

    @classmethod
    def _is_placeholder(cls, val: str | None) -> bool:
        if not val:
            return False
        s = val.strip().lower()
        return s.startswith("your_") or s in {"changeme", "placeholder"}

    @classmethod
    def diagnose_provider(cls, provider_type: ProviderType) -> dict[str, Any]:
        """
        Return structured diagnostics for a single provider type.

        This does not import server modules and does not force provider initialization.
        """
        # Import registry class
        from src.providers.registry_core import ModelProviderRegistry

        info: dict[str, Any] = {
            "provider": getattr(provider_type, "name", str(provider_type)),
            "registered": False,
            "initialized": False,
            "api_key_present": False,
            "api_key_var": None,
            "api_key_is_placeholder": False,
            "base_url_present": False,
            "base_url_var": None,
            "reason_unavailable": None,
            "suggestions": [],
        }
        reg = ModelProviderRegistry()
        info["registered"] = provider_type in getattr(reg, "_providers", {})

        # API key check
        key_vars = cls._API_KEY_VARS.get(provider_type, [])
        key_var, key_val = cls._first_present(key_vars)
        info["api_key_present"] = bool(key_val)
        info["api_key_var"] = key_var
        info["api_key_is_placeholder"] = cls._is_placeholder(key_val)

        # Base URL (optional)
        url_vars = cls._BASE_URL_VARS.get(provider_type, [])
        url_var, url_val = cls._first_present(url_vars)
        info["base_url_present"] = bool(url_val)
        info["base_url_var"] = url_var

        # Initialized (without forcing a new instance)
        info["initialized"] = provider_type in getattr(reg, "_initialized_providers", {})

        # Reasoning and suggestions
        if not info["registered"]:
            info["reason_unavailable"] = "Provider class not registered in registry"
            info["suggestions"].append("Ensure provider_config.configure_providers() ran in the daemon")
        elif not info["api_key_present"] and provider_type != ProviderType.CUSTOM:
            info["reason_unavailable"] = "Missing API key"
            if key_vars:
                info["suggestions"].append(f"Set one of: {', '.join(key_vars)} in .env")
        elif info["api_key_is_placeholder"]:
            info["reason_unavailable"] = "API key appears to be a placeholder"
            info["suggestions"].append(f"Replace {key_var} with a valid key in .env")
        elif provider_type == ProviderType.CUSTOM and not info["base_url_present"]:
            info["reason_unavailable"] = "CUSTOM_API_URL is required for Custom provider"
            info["suggestions"].append("Set CUSTOM_API_URL (and optionally CUSTOM_API_KEY) in .env")
        elif not info["initialized"]:
            info["reason_unavailable"] = "Provider not initialized yet"
            info["suggestions"].append("Restart or ping the daemon so providers initialize")

        return info

    @classmethod
    def diagnose_all(cls) -> list[dict[str, Any]]:
        """Diagnose all known provider types present in the registry or with env keys."""
        # Import registry class
        from src.providers.registry_core import ModelProviderRegistry

        reg = ModelProviderRegistry()
        ptypes = set(getattr(reg, "_providers", {}).keys()) | {
            ProviderType.KIMI,
            ProviderType.GLM,
            ProviderType.CUSTOM,
            ProviderType.OPENROUTER,
        }
        return [cls.diagnose_provider(pt) for pt in ptypes]

    @classmethod
    def diagnose_all_daemon_first(cls) -> list[dict[str, Any]]:
        """
        Prefer daemon snapshot if present; fallback to local process diagnostics.

        The daemon writes logs/provider_registry_snapshot.json at startup. Reading it avoids
        cross-process registry confusion and more accurately reflects the MCP server state.
        """
        try:
            import json
            from pathlib import Path

            p = Path("logs") / "provider_registry_snapshot.json"
            if p.exists():
                data = json.loads(p.read_text(encoding="utf-8")) or {}
                registered = set(data.get("registered_providers") or [])
                initialized = set(data.get("initialized_providers") or [])
                results: list[dict[str, Any]] = []
                for pt in [ProviderType.KIMI, ProviderType.GLM, ProviderType.CUSTOM, ProviderType.OPENROUTER]:
                    base = cls.diagnose_provider(pt)
                    name = getattr(pt, "name", str(pt))
                    base["registered"] = name in registered
                    base["initialized"] = name in initialized
                    if base["registered"] and base["initialized"]:
                        base["reason_unavailable"] = None
                    results.append(base)
                return results
        except Exception:
            pass
        # Fallback to process-local view
        return cls.diagnose_all()

