"""
Logging Setup Module

Consolidates logging configuration for EX-AI MCP Server components.
Replaces duplicate implementations in:
- scripts/run_ws_shim.py lines 34-50
- src/daemon/ws_server.py lines 20-54
- server.py lines 125-180
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


def setup_logging(
    component_name: str,
    log_file: Optional[str] = None,
    log_level: Optional[str] = None,
    file_logging: bool = True,
    console_logging: bool = True,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
) -> logging.Logger:
    """
    Setup logging for a component with both file and console handlers.
    
    Args:
        component_name: Name of the component (used for logger name)
        log_file: Optional explicit log file path
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        file_logging: Enable file logging
        console_logging: Enable console logging
        max_bytes: Maximum log file size before rotation
        backup_count: Number of backup log files to keep
        
    Returns:
        Configured logger instance
    """
    # Determine log level
    if log_level is None:
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    else:
        log_level = log_level.upper()
    
    # Get or create logger
    logger = logging.getLogger(component_name)
    logger.setLevel(log_level)

    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()

    # Prevent propagation to root logger to avoid duplicate messages
    # (root logger may have its own handlers from async_logging setup)
    logger.propagate = False
    
    # CRITICAL FIX (2025-11-01): Use Melbourne timezone for all timestamps
    # EXAI Consultation: 63c00b70-364b-4351-bf6c-5a105e553dce
    # Import timezone helper for Melbourne/AEDT timestamps
    timezone_loaded = False
    try:
        from utils.timezone_helper import MELBOURNE_TZ
        from datetime import datetime

        class MelbourneFormatter(logging.Formatter):
            """Custom formatter that uses Melbourne timezone"""
            def formatTime(self, record, datefmt=None):
                dt = datetime.fromtimestamp(record.created, tz=MELBOURNE_TZ)
                if datefmt:
                    return dt.strftime(datefmt)
                else:
                    return dt.strftime("%Y-%m-%d %H:%M:%S %Z")

        formatter = MelbourneFormatter(
            "%(asctime)s %(levelname)s %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S %Z"
        )
        timezone_loaded = True
    except ImportError as e:
        # Fallback to standard formatter if timezone_helper not available
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        # Log warning about timezone fallback (will use logger after it's configured)
        logger.info(f"WARNING: Failed to load Melbourne timezone - falling back to UTC: {e}", file=sys.stderr)
    
    # Add console handler
    if console_logging:
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # Add file handler
    if file_logging:
        try:
            # Determine log file path
            if log_file is None:
                # Default to logs/{component_name}.log
                from .env_loader import get_repo_root
                repo_root = get_repo_root()
                logs_dir = repo_root / "logs"
                logs_dir.mkdir(parents=True, exist_ok=True)
                log_file = str(logs_dir / f"{component_name}.log")
            
            # Create rotating file handler
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding="utf-8"
            )
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            
        except Exception as e:
            # Never let logging setup break the application
            logger.warning(f"Failed to setup file logging: {e}")

    # PHASE 1 FIX (2025-11-01): Re-log timezone warning if helper failed to load
    # EXAI Consultation: 63c00b70-364b-4351-bf6c-5a105e553dce
    if not timezone_loaded:
        logger.warning("Melbourne timezone unavailable - using UTC timestamps")

    return logger


def setup_basic_logging(log_level: Optional[str] = None) -> None:
    """
    Setup basic logging configuration (fallback for simple cases).
    
    Args:
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    if log_level is None:
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    else:
        log_level = log_level.upper()
    
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stderr
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance by name.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def configure_websockets_logging() -> None:
    """
    Configure websockets library logging to suppress handshake noise.

    The websockets library logs handshake failures at ERROR level, which creates
    noise from port scanners, health checks, and clients that connect without
    completing the HTTP upgrade handshake. These errors are unavoidable and
    expected for any public-facing WebSocket server.

    This function suppresses these errors by setting the websockets library
    loggers to WARNING level, which only shows actual problems (not noise).

    Call this once during application startup, typically in the daemon entry point.
    """
    # Suppress handshake failure noise from port scanners and health checks
    # Set to CRITICAL to suppress ERROR-level handshake failures
    logging.getLogger('websockets.server').setLevel(logging.CRITICAL)
    logging.getLogger('websockets.protocol').setLevel(logging.CRITICAL)
    logging.getLogger('websockets.client').setLevel(logging.CRITICAL)

    # Log that we've configured this (at INFO level so we can verify it's working)
    logging.info("[LOGGING] Configured websockets library logging to suppress handshake noise")

