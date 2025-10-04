"""
Bootstrap Module

Provides common initialization utilities for EX-AI MCP Server entry points.
Consolidates environment loading, path setup, and logging configuration.
"""

from .env_loader import load_env, get_repo_root
from .logging_setup import setup_logging

__all__ = [
    "load_env",
    "get_repo_root",
    "setup_logging",
]

