"""
Registry shim module for backward compatibility.

This module provides backward compatibility for imports that expect
src.providers.registry to exist, redirecting to the actual registry module.
"""

# Re-export the actual registry from registry_core
from .registry_core import ModelProviderRegistry as registry

# For imports that expect to import registry directly
__all__ = ['registry']