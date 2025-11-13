"""
Provider Registry Configuration and Health Monitoring

This module provides configuration management, feature flags, and health monitoring
for the provider registry system.

Key Components:
- Environment variable loading (.env support)
- Feature flag functions (health checks, circuit breakers, retries, cost awareness)
- HealthWrappedProvider class for health monitoring and retry logic
- Health manager singleton

For the main registry functionality, see registry_core.py
"""

import asyncio
import logging
import os
import time
from typing import Any, Optional, TYPE_CHECKING

# Ensure environment variables from project .env are available even when server.py
# is not the entrypoint (e.g., direct tool/EX-AI invocations)
try:
    from pathlib import Path
    from dotenv import load_dotenv  # type: ignore

    # Compute repository root (three levels up from this file: src/providers/registry_config.py)
    repo_root = Path(__file__).resolve().parents[2]
    env_path = repo_root / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=str(env_path))
    else:
        logging.warning(".env file not found at %s", env_path)
except Exception as e:
    # If dotenv is not installed or any error occurs, proceed with system env only
    logging.warning("dotenv load failed: %s; proceeding with system environment only", e)

from src.providers.base import ModelProvider, ProviderType

if TYPE_CHECKING:
    from tools.models import ToolModelCategory

from utils.infrastructure.health import HealthManager


# ================================================================================
# Feature Flag Functions
# ================================================================================

# Helper for env var access
_DEF = lambda k, d: os.getenv(k, d).lower()


def _health_enabled() -> bool:
    """Check if health checks are enabled."""
    return _DEF("HEALTH_CHECKS_ENABLED", "false") == "true"


def _cb_enabled() -> bool:
    """Check if circuit breaker is enabled."""
    return _DEF("CIRCUIT_BREAKER_ENABLED", "false") == "true"


def _health_log_only() -> bool:
    """Check if health checks are in log-only mode (no gating)."""
    return _DEF("HEALTH_LOG_ONLY", "true") == "true"


def _retry_attempts() -> int:
    """Get number of retry attempts for failed requests."""
    try:
        return int(os.getenv("RETRY_ATTEMPTS", "2"))
    except Exception:
        return 2


def _backoff_base() -> float:
    """Get base backoff delay in seconds."""
    try:
        return float(os.getenv("RETRY_BACKOFF_BASE", "0.5"))
    except Exception:
        return 0.5


def _backoff_max() -> float:
    """Get maximum backoff delay in seconds."""
    try:
        return float(os.getenv("RETRY_BACKOFF_MAX", "4.0"))
    except Exception:
        return 4.0


def _free_tier_enabled() -> bool:
    """Check if free tier preference is enabled."""
    return os.getenv("FREE_TIER_PREFERENCE_ENABLED", "false").lower() == "true"


def _free_model_list() -> set[str]:
    """Get set of free tier model names."""
    raw = os.getenv("FREE_MODEL_LIST", "")
    return set([m.strip().lower() for m in raw.split(",") if m.strip()])


def _apply_free_first(models: list[str]) -> list[str]:
    """Reorder models to prioritize free tier models."""
    if not _free_tier_enabled():
        return models
    free = _free_model_list()
    if not free:
        return models
    free_models = [m for m in models if m.lower() in free]
    paid_models = [m for m in models if m.lower() not in free]
    return free_models + paid_models


def _cost_aware_enabled() -> bool:
    """Check if cost-aware routing is enabled."""
    return os.getenv("COST_AWARE_ROUTING_ENABLED", "false").lower() == "true"


def _load_model_costs() -> dict[str, float]:
    """Load model cost configuration from environment."""
    import json

    raw = os.getenv("MODEL_COSTS_JSON", "{}")
    try:
        data = json.loads(raw)
        if isinstance(data, dict):
            return {str(k): float(v) for k, v in data.items()}
    except Exception:
        pass
    return {}


def _max_cost_per_request() -> float | None:
    """Get maximum cost per request limit."""
    try:
        val = os.getenv("MAX_COST_PER_REQUEST")
        return float(val) if val else None
    except Exception:
        return None


def _apply_cost_aware(models: list[str], tool_category: Any) -> list[str]:
    """Filter and sort models by cost constraints."""
    if not _cost_aware_enabled():
        return models
    costs = _load_model_costs()
    if not costs:
        return models
    max_cost = _max_cost_per_request()

    # Filter and sort by configured cost if present; unknown costs retain original order at end
    def model_key(m: str):
        return (0, costs[m]) if m in costs else (1, float("inf"))

    filtered = [
        m
        for m in models
        if (max_cost is None or (m in costs and costs[m] <= max_cost)) or (m not in costs)
    ]
    filtered.sort(key=model_key)
    return filtered


# ================================================================================
# Health Manager Singleton
# ================================================================================

_HEALTH_MANAGER: HealthManager | None = None


def _get_health_manager() -> HealthManager:
    """Get or create the global health manager instance."""
    global _HEALTH_MANAGER
    if _HEALTH_MANAGER is None:
        _HEALTH_MANAGER = HealthManager()
    return _HEALTH_MANAGER


# ================================================================================
# Health Wrapped Provider
# ================================================================================


class HealthWrappedProvider(ModelProvider):
    """
    Wrapper that records provider health and applies simple retry/backoff.

    Only active when HEALTH_CHECKS_ENABLED=true. Selection gating happens in registry.
    This wrapper provides:
    - Health monitoring and metrics recording
    - Automatic retry with exponential backoff
    - Circuit breaker integration
    - Latency tracking
    """

    def __init__(self, inner: ModelProvider):
        self._inner = inner
        self._ptype = inner.get_provider_type()
        self._health = _get_health_manager().get(self._ptype.value)

    # Pass-throughs to satisfy abstract interface
    def get_provider_type(self) -> ProviderType:
        return self._ptype

    # Ensure restriction validation sees real model lists/capabilities
    def get_model_configurations(self) -> dict[str, Any]:
        return self._inner.get_model_configurations()

    def get_all_model_aliases(self) -> dict[str, list[str]]:
        return self._inner.get_all_model_aliases()

    def list_all_known_models(self) -> list[str]:
        return self._inner.list_all_known_models()

    def get_preferred_model(self, category: "ToolModelCategory", allowed_models: list[str]) -> str | None:
        # Delegate if inner provider implements preference; else no preference
        try:
            return self._inner.get_preferred_model(category, allowed_models)  # type: ignore[attr-defined]
        except Exception:
            return None

    # Legacy compatibility: alias to inner when callers expect raw provider type
    def get_provider_type_raw(self):
        return self._inner.get_provider_type()

    @staticmethod
    def _schedule(coro) -> None:
        """Schedule async health recording without blocking."""
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(coro)
        except Exception:
            # If no loop or running in a threadpool, skip recording instead of crashing
            pass

    # Forwarding methods
    def get_capabilities(self, model_name: str):
        return self._inner.get_capabilities(model_name)

    def validate_model_name(self, model_name: str) -> bool:
        return self._inner.validate_model_name(model_name)

    def list_models(self, respect_restrictions: bool = True):
        fn = getattr(self._inner, "list_models", None)
        if callable(fn):
            return fn(respect_restrictions=respect_restrictions)
        # Return empty list if inner provider doesn't implement list_models
        return []

    def supports_thinking_mode(self, model_name: str) -> bool:
        fn = getattr(self._inner, "supports_thinking_mode", None)
        if callable(fn):
            try:
                return bool(fn(model_name))
            except Exception:
                return False
        return False

    def count_tokens(self, text: str, model_name: str) -> int:
        # Token count is fast; treat errors as failure but no retries
        try:
            val = self._inner.count_tokens(text, model_name)
            if _health_enabled() and not _health_log_only():
                HealthWrappedProvider._schedule(self._health.record_result(True))
            return val
        except Exception:
            if _health_enabled():
                # log-only still records but does not gate selection here
                HealthWrappedProvider._schedule(self._health.record_result(False))
            raise

    def generate_content(
        self,
        prompt: str,
        model_name: str,
        system_prompt: str | None = None,
        temperature: float = 0.3,
        max_output_tokens: int | None = None,
        **kwargs,
    ):
        """Generate content with retry logic and health monitoring."""
        attempts = max(1, _retry_attempts())
        delay = _backoff_base()
        last_exc = None
        for i in range(attempts):
            try:
                t0 = time.perf_counter()
                result = self._inner.generate_content(
                    prompt=prompt,
                    model_name=model_name,
                    system_prompt=system_prompt,
                    temperature=temperature,
                    max_output_tokens=max_output_tokens,
                    **kwargs,
                )
                latency_ms = (time.perf_counter() - t0) * 1000.0
                if _health_enabled() and not _health_log_only():
                    HealthWrappedProvider._schedule(self._health.record_result(True))
                try:
                    from utils.infrastructure.metrics import record_provider_call

                    record_provider_call(self._ptype.value, model_name, True, latency_ms)
                except Exception:
                    pass
                return result
            except Exception as e:
                last_exc = e
                if _health_enabled():
                    HealthWrappedProvider._schedule(self._health.record_result(False))
                try:
                    from utils.infrastructure.metrics import record_provider_call

                    record_provider_call(self._ptype.value, model_name, False, None)
                except Exception:
                    pass
                # Simple backoff before retrying (EXAI Fix #5 - 2025-10-21: Add retry logging)
                if i < attempts - 1:
                    backoff_time = min(delay, _backoff_max())
                    logger.warning(
                        f"🔄 [PROVIDER_RETRY] Provider: {self._ptype.value}, "
                        f"Attempt: {i + 1}/{attempts}, "
                        f"Error: {str(e)[:100]}, "
                        f"Retrying in {backoff_time:.1f}s..."
                    )
                    time.sleep(backoff_time)
                    delay *= 2
                else:
                    logger.error(
                        f"❌ [PROVIDER_RETRY_EXHAUSTED] Provider: {self._ptype.value}, "
                        f"Failed after {attempts} attempts, "
                        f"Final error: {str(e)[:100]}"
                    )
        # Exceeded retries
        raise last_exc

