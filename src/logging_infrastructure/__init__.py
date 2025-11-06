"""
EXAI-MCP Centralized Logging Infrastructure
============================================

Provides structured logging with automatic context enrichment.

Quick Start:
    from src.logging import get_logger, LoggingContext
    
    logger = get_logger(__name__)
    
    with LoggingContext.request_context(request_id="123"):
        logger.info("Processing request", user="john")

Date: 2025-10-22
"""

from .logging_manager import (
    LoggingManager,
    get_logging_manager,
    get_logger,
)

from .logging_context import LoggingContext

from .file_operations_logger import (
    FileOperationsLogger,
    get_file_logger,
)

__all__ = [
    # Logging Manager
    "LoggingManager",
    "get_logging_manager",
    "get_logger",
    
    # Context Management
    "LoggingContext",
    
    # File Operations Logger
    "FileOperationsLogger",
    "get_file_logger",
]

