"""
Bootstrap Module

Provides common initialization utilities for EX-AI MCP Server entry points.
Consolidates environment loading, path setup, logging configuration, and
singleton initialization for providers and tools.
"""

from .env_loader import load_env, get_repo_root
from .logging_setup import setup_logging, configure_websockets_logging
from .singletons import (
    ensure_providers_configured,
    ensure_tools_built,
    ensure_provider_tools_registered,
    bootstrap_all,
    is_providers_configured,
    is_tools_built,
    is_provider_tools_registered,
    get_tools,
)

__all__ = [
    "load_env",
    "get_repo_root",
    "setup_logging",
    "configure_websockets_logging",
    "ensure_providers_configured",
    "ensure_tools_built",
    "ensure_provider_tools_registered",
    "bootstrap_all",
    "is_providers_configured",
    "is_tools_built",
    "is_provider_tools_registered",
    "get_tools",
]

