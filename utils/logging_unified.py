"""Unified logging infrastructure for all tools.

This module provides a centralized logging system that:
1. Logs all tool executions to structured JSONL format
2. Integrates with existing logging infrastructure (tool_events.py, observability.py)
3. Provides consistent logging interface for simple and workflow tools
4. Tracks request_id for correlation across tool calls
5. Integrates with ProgressHeartbeat for long-running operations

Usage:
    from utils.logging_unified import get_unified_logger
    
    logger = get_unified_logger()
    logger.log_tool_start("chat", "req-123", {"prompt": "Hello"})
    logger.log_tool_complete("chat", "req-123", {"status": "success"})
"""

import json
import time
import logging
import traceback
import uuid
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timezone

# Standard logger for this module
_module_logger = logging.getLogger(__name__)


class UnifiedLogger:
    """Unified logging for all tools with structured output."""
    
    def __init__(self, log_file: str = ".logs/toolcalls.jsonl"):
        """
        Initialize unified logger.
        
        Args:
            log_file: Path to log file (JSONL format)
        """
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.buffer = []
        self.buffer_size = 10  # Flush after 10 entries
        
    def _write_log(self, entry: Dict[str, Any]):
        """
        Write log entry to file.
        
        Args:
            entry: Log entry dictionary
        """
        try:
            # Add to buffer
            self.buffer.append(entry)
            
            # Flush if buffer is full
            if len(self.buffer) >= self.buffer_size:
                self._flush()
        except Exception as e:
            _module_logger.warning(f"Failed to write log entry: {e}")
            
    def _flush(self):
        """Flush buffered log entries to file."""
        if not self.buffer:
            return
            
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                for entry in self.buffer:
                    f.write(json.dumps(entry, ensure_ascii=False) + '\n')
            self.buffer.clear()
        except Exception as e:
            _module_logger.warning(f"Failed to flush log buffer: {e}")
            
    def log_tool_start(
        self,
        tool_name: str,
        request_id: str,
        params: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log tool execution start.
        
        Args:
            tool_name: Name of the tool
            request_id: Unique request identifier
            params: Tool parameters
            metadata: Optional metadata
        """
        entry = {
            "timestamp": time.time(),
            "datetime": datetime.now(timezone.utc).isoformat(),
            "event": "tool_start",
            "tool": tool_name,
            "request_id": request_id,
            "params": self._sanitize_params(params),
        }
        if metadata:
            entry["metadata"] = metadata
            
        self._write_log(entry)
        _module_logger.info(f"[{tool_name}] Started (request_id={request_id})")
        
    def log_tool_progress(
        self,
        tool_name: str,
        request_id: str,
        step: int,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log tool execution progress.
        
        Args:
            tool_name: Name of the tool
            request_id: Unique request identifier
            step: Current step number
            message: Progress message
            metadata: Optional metadata
        """
        entry = {
            "timestamp": time.time(),
            "datetime": datetime.now(timezone.utc).isoformat(),
            "event": "tool_progress",
            "tool": tool_name,
            "request_id": request_id,
            "step": step,
            "message": message,
        }
        if metadata:
            entry["metadata"] = metadata
            
        self._write_log(entry)
        _module_logger.debug(f"[{tool_name}] Progress: {message} (step={step})")
        
    def log_tool_complete(
        self,
        tool_name: str,
        request_id: str,
        result: Dict[str, Any],
        duration_secs: float,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log tool execution completion.
        
        Args:
            tool_name: Name of the tool
            request_id: Unique request identifier
            result: Tool result
            duration_secs: Execution duration in seconds
            metadata: Optional metadata
        """
        entry = {
            "timestamp": time.time(),
            "datetime": datetime.now(timezone.utc).isoformat(),
            "event": "tool_complete",
            "tool": tool_name,
            "request_id": request_id,
            "duration_secs": round(duration_secs, 3),
            "result": self._sanitize_result(result),
        }
        if metadata:
            entry["metadata"] = metadata
            
        self._write_log(entry)
        _module_logger.info(f"[{tool_name}] Completed in {duration_secs:.2f}s (request_id={request_id})")
        
    def log_tool_error(
        self,
        tool_name: str,
        request_id: str,
        error: str,
        error_traceback: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log tool execution error.
        
        Args:
            tool_name: Name of the tool
            request_id: Unique request identifier
            error: Error message
            error_traceback: Optional error traceback
            metadata: Optional metadata
        """
        entry = {
            "timestamp": time.time(),
            "datetime": datetime.now(timezone.utc).isoformat(),
            "event": "tool_error",
            "tool": tool_name,
            "request_id": request_id,
            "error": error,
        }
        if error_traceback:
            entry["traceback"] = error_traceback
        if metadata:
            entry["metadata"] = metadata
            
        self._write_log(entry)
        _module_logger.error(f"[{tool_name}] Error: {error} (request_id={request_id})")
        
    def log_expert_validation_start(
        self,
        tool_name: str,
        request_id: str,
        expert_model: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log expert validation start.
        
        Args:
            tool_name: Name of the tool
            request_id: Unique request identifier
            expert_model: Expert model name
            metadata: Optional metadata
        """
        entry = {
            "timestamp": time.time(),
            "datetime": datetime.now(timezone.utc).isoformat(),
            "event": "expert_validation_start",
            "tool": tool_name,
            "request_id": request_id,
            "expert_model": expert_model,
        }
        if metadata:
            entry["metadata"] = metadata
            
        self._write_log(entry)
        _module_logger.info(f"[{tool_name}] Expert validation started with {expert_model} (request_id={request_id})")
        
    def log_expert_validation_complete(
        self,
        tool_name: str,
        request_id: str,
        expert_model: str,
        validation_result: Dict[str, Any],
        duration_secs: float,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log expert validation completion.
        
        Args:
            tool_name: Name of the tool
            request_id: Unique request identifier
            expert_model: Expert model name
            validation_result: Validation result
            duration_secs: Validation duration in seconds
            metadata: Optional metadata
        """
        entry = {
            "timestamp": time.time(),
            "datetime": datetime.now(timezone.utc).isoformat(),
            "event": "expert_validation_complete",
            "tool": tool_name,
            "request_id": request_id,
            "expert_model": expert_model,
            "duration_secs": round(duration_secs, 3),
            "validation_result": validation_result,
        }
        if metadata:
            entry["metadata"] = metadata
            
        self._write_log(entry)
        _module_logger.info(f"[{tool_name}] Expert validation completed in {duration_secs:.2f}s (request_id={request_id})")
        
    def _sanitize_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize parameters for logging (remove sensitive data, truncate large values).
        
        Args:
            params: Parameters dictionary
            
        Returns:
            Sanitized parameters
        """
        sanitized = {}
        for key, value in params.items():
            # Skip internal/private parameters
            if key.startswith('_'):
                continue
                
            # Truncate long strings
            if isinstance(value, str) and len(value) > 500:
                sanitized[key] = value[:500] + "... (truncated)"
            else:
                sanitized[key] = value
                
        return sanitized
        
    def _sanitize_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize result for logging (truncate large values).
        
        Args:
            result: Result dictionary
            
        Returns:
            Sanitized result
        """
        sanitized = {}
        for key, value in result.items():
            # Truncate long strings
            if isinstance(value, str) and len(value) > 1000:
                sanitized[key] = value[:1000] + "... (truncated)"
            else:
                sanitized[key] = value
                
        return sanitized


# Global unified logger instance
_unified_logger = None


def get_unified_logger() -> UnifiedLogger:
    """
    Get global unified logger instance.
    
    Returns:
        UnifiedLogger instance
    """
    global _unified_logger
    if _unified_logger is None:
        _unified_logger = UnifiedLogger()
    return _unified_logger

