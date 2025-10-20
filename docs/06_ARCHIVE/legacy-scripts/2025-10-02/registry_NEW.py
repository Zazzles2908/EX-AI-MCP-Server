"""
Model Provider Registry - Public API

This module provides the public API for the provider registry system.
It re-exports all components from the specialized modules for backward compatibility.

Architecture:
- registry_config.py: Configuration, feature flags, and health monitoring
- registry_core.py: Core registry functionality (registration, initialization, discovery)
- registry_selection.py: Model selection, fallback chains, and diagnostics

For implementation details, see the individual modules.
"""

# ================================================================================
# Configuration and Health Monitoring
# ================================================================================

from src.providers.registry_config import (
    # Feature flag functions
    _health_enabled,
    _cb_enabled,
    _health_log_only,
    _retry_attempts,
    _backoff_base,
    _backoff_max,
    _free_tier_enabled,
    _free_model_list,
    _apply_free_first,
    _cost_aware_enabled,
    _load_model_costs,
    _max_cost_per_request,
    _apply_cost_aware,
    _get_health_manager,
    # Health wrapper
    HealthWrappedProvider,
)

# ================================================================================
# Core Registry
# ================================================================================

from src.providers.registry_core import ModelProviderRegistry

# ================================================================================
# Selection and Diagnostics
# ================================================================================

from src.providers.registry_selection import ProviderDiagnostics

# ================================================================================
# Public API
# ================================================================================

__all__ = [
    # Core registry
    "ModelProviderRegistry",
    # Health monitoring
    "HealthWrappedProvider",
    # Diagnostics
    "ProviderDiagnostics",
    # Feature flags (internal use)
    "_health_enabled",
    "_cb_enabled",
    "_health_log_only",
    "_retry_attempts",
    "_backoff_base",
    "_backoff_max",
    "_free_tier_enabled",
    "_free_model_list",
    "_apply_free_first",
    "_cost_aware_enabled",
    "_load_model_costs",
    "_max_cost_per_request",
    "_apply_cost_aware",
    "_get_health_manager",
]

