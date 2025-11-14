"""
Audit logger for tracking file operations.
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime


class AuditLogger:
    """Simple audit logger for file operations."""

    def __init__(self, name: str = "file_audit"):
        """Initialize audit logger.

        Args:
            name: Logger name
        """
        self.logger = logging.getLogger(name)

    def log_operation(
        self,
        operation: str,
        path: str,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log a file operation.

        Args:
            operation: Operation type (read, write, delete, etc.)
            path: File path
            user_id: Optional user ID
            metadata: Optional additional metadata
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "operation": operation,
            "path": path,
        }

        if user_id:
            log_data["user_id"] = user_id

        if metadata:
            log_data.update(metadata)

        self.logger.info(f"Audit: {log_data}")

    def log_error(self, operation: str, path: str, error: str, metadata: Optional[Dict[str, Any]] = None):
        """Log an error.

        Args:
            operation: Operation type
            path: File path
            error: Error message
            metadata: Optional additional metadata
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "operation": operation,
            "path": path,
            "error": error,
        }

        if metadata:
            log_data.update(metadata)

        self.logger.error(f"Audit Error: {log_data}")
