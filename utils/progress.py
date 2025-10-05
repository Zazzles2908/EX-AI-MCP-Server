"""
Progress notification helper for EX MCP Server.

- Centralizes progress emission for tools
- Controlled via STREAM_PROGRESS env var (default: true)
- Logs to the "mcp_activity" logger
- Best-effort MCP notification hook (can be wired by server if supported)
"""
from __future__ import annotations

import asyncio
import logging
import os
from typing import Any, Callable, Optional
from contextvars import ContextVar

# Type for a notifier function; may be sync or async
Notifier = Callable[[str, str], Any]

_logger = logging.getLogger("mcp_activity")
_mcp_notifier: Optional[Notifier] = None

# Per-call progress capture via ContextVar (safe for async concurrency)
_progress_log_var: ContextVar[Optional[list[str]]] = ContextVar("progress_log", default=None)


def _stream_enabled() -> bool:
    return os.getenv("STREAM_PROGRESS", "true").strip().lower() == "true"


def start_progress_capture() -> None:
    """Begin capturing progress messages for the current call."""
    _progress_log_var.set([])


def get_progress_log() -> list[str]:
    """Return captured progress messages for the current call (if any)."""
    buf = _progress_log_var.get()
    return list(buf) if isinstance(buf, list) else []


def set_mcp_notifier(notifier: Notifier) -> None:
    """
    Register a notifier callback capable of sending MCP-compatible notifications.
    The callback should accept (message: str, level: str) and may be sync or async.
    """
    global _mcp_notifier
    _mcp_notifier = notifier


def clear_mcp_notifier() -> None:
    """Clear any registered MCP notifier."""
    global _mcp_notifier
    _mcp_notifier = None


def send_progress(message: str, level: str = "info") -> None:
    """
    Emit a progress signal if STREAM_PROGRESS is enabled.
    - Logs via mcp_activity (picked up by stderr/file handlers)
    - Captures message into per-call buffer (ContextVar)
    - Best-effort call to a registered MCP notifier (if any)
    """
    if not _stream_enabled():
        return

    # Log first so users always see breadcrumbs in stderr/logs
    level_lower = (level or "info").lower()
    if level_lower == "debug":
        _logger.debug(f"[PROGRESS] {message}")
    elif level_lower in ("warn", "warning"):
        _logger.warning(f"[PROGRESS] {message}")
    elif level_lower == "error":
        _logger.error(f"[PROGRESS] {message}")
    else:
        _logger.info(f"[PROGRESS] {message}")

    # Capture in per-call buffer
    try:
        buf = _progress_log_var.get()
        if isinstance(buf, list):
            buf.append(message)
    except Exception:
        pass

    # Best-effort MCP notification
    try:
        if _mcp_notifier is None:
            return
        result = _mcp_notifier(message, level_lower)
        if asyncio.iscoroutine(result):
            # Fire and forget; do not await within tool critical paths
            asyncio.create_task(result)  # type: ignore[arg-type]
    except Exception:
        # Never allow progress emission to break tool execution
        _logger.debug("[PROGRESS] MCP notifier unavailable or failed; continuing")


# ============================================================================
# Progress Heartbeat System (Added for Day 3-4 Implementation)
# ============================================================================

import time
from typing import Dict

_heartbeat_logger = logging.getLogger(__name__)


class ProgressHeartbeat:
    """Manages progress heartbeat for long-running operations.

    Sends periodic progress updates at configured intervals to prevent users
    from thinking the system is frozen during long operations.

    Usage:
        async with ProgressHeartbeat(interval_secs=6.0) as heartbeat:
            heartbeat.set_total_steps(5)
            for i in range(5):
                heartbeat.set_current_step(i + 1)
                await heartbeat.send_heartbeat(f"Processing step {i+1}...")
                # Do work here
    """

    def __init__(
        self,
        interval_secs: float = 6.0,
        callback: Optional[Callable[[Dict[str, Any]], Any]] = None
    ):
        """
        Initialize progress heartbeat.

        Args:
            interval_secs: Seconds between heartbeats (default 6s)
            callback: Optional async callback function for progress updates
                     Signature: async def callback(data: dict) -> None
        """
        self.interval = interval_secs
        self.callback = callback
        self.last_heartbeat = time.time()
        self.enabled = True
        self.start_time = time.time()
        self.current_step = 0
        self.total_steps = 0
        self._task = None

    async def __aenter__(self):
        """Context manager entry."""
        self.start_time = time.time()
        self.last_heartbeat = time.time()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
        return False

    def stop(self):
        """Stop heartbeat."""
        self.enabled = False
        if self._task and not self._task.done():
            self._task.cancel()

    def set_total_steps(self, total: int):
        """Set total number of steps for progress calculation."""
        self.total_steps = total

    def set_current_step(self, step: int):
        """Set current step number for progress calculation."""
        self.current_step = step

    async def send_heartbeat(
        self,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Send progress heartbeat if interval elapsed.

        Args:
            message: Progress message
            metadata: Optional metadata dict
        """
        if not self.enabled:
            return

        now = time.time()
        if now - self.last_heartbeat >= self.interval:
            await self._emit_progress(message, metadata)
            self.last_heartbeat = now

    async def force_heartbeat(
        self,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Force send heartbeat immediately, ignoring interval.

        Args:
            message: Progress message
            metadata: Optional metadata dict
        """
        if not self.enabled:
            return

        await self._emit_progress(message, metadata)
        self.last_heartbeat = time.time()

    async def _emit_progress(self, message: str, metadata: Optional[Dict[str, Any]]):
        """
        Emit progress message to client.

        Args:
            message: Progress message
            metadata: Optional metadata dict
        """
        now = time.time()
        elapsed = now - self.start_time

        # Calculate progress percentage
        progress_pct = 0.0
        if self.total_steps > 0 and self.current_step > 0:
            progress_pct = (self.current_step / self.total_steps) * 100

        # Estimate remaining time
        estimated_remaining = None
        if self.total_steps > 0 and self.current_step > 0:
            avg_time_per_step = elapsed / self.current_step
            remaining_steps = self.total_steps - self.current_step
            estimated_remaining = avg_time_per_step * remaining_steps

        # Build progress data
        progress_data = {
            "message": message,
            "elapsed_secs": round(elapsed, 2),
            "progress_pct": round(progress_pct, 1),
            "step": self.current_step,
            "total_steps": self.total_steps,
            "timestamp": now
        }

        if estimated_remaining is not None:
            progress_data["estimated_remaining_secs"] = round(estimated_remaining, 2)

        if metadata:
            progress_data["metadata"] = metadata

        # Log progress
        _heartbeat_logger.debug(f"Progress: {message} ({progress_pct:.1f}% complete, {elapsed:.1f}s elapsed)")

        # Also use existing send_progress for backward compatibility
        send_progress(message, "info")

        # Call callback if provided
        if self.callback:
            try:
                if asyncio.iscoroutinefunction(self.callback):
                    await self.callback(progress_data)
                else:
                    self.callback(progress_data)
            except Exception as e:
                _heartbeat_logger.warning(f"Progress callback failed: {e}", exc_info=True)
                # Don't let callback failures break the heartbeat


class ProgressHeartbeatManager:
    """Manages multiple progress heartbeats for concurrent operations."""

    def __init__(self):
        """Initialize progress heartbeat manager."""
        self.operations: Dict[str, ProgressHeartbeat] = {}

    def create_heartbeat(
        self,
        operation_id: str,
        interval_secs: float = 6.0,
        callback: Optional[Callable] = None
    ) -> ProgressHeartbeat:
        """
        Create new progress heartbeat for operation.

        Args:
            operation_id: Unique operation identifier
            interval_secs: Seconds between heartbeats
            callback: Optional callback function

        Returns:
            ProgressHeartbeat instance
        """
        heartbeat = ProgressHeartbeat(interval_secs, callback)
        self.operations[operation_id] = heartbeat
        return heartbeat

    def get_heartbeat(self, operation_id: str) -> Optional[ProgressHeartbeat]:
        """
        Get existing heartbeat for operation.

        Args:
            operation_id: Operation identifier

        Returns:
            ProgressHeartbeat instance or None
        """
        return self.operations.get(operation_id)

    def remove_heartbeat(self, operation_id: str):
        """
        Remove heartbeat for completed operation.

        Args:
            operation_id: Operation identifier
        """
        if operation_id in self.operations:
            self.operations[operation_id].stop()
            del self.operations[operation_id]

    def stop_all(self):
        """Stop all active heartbeats."""
        for heartbeat in self.operations.values():
            heartbeat.stop()
        self.operations.clear()


# Global heartbeat manager instance
_heartbeat_manager = ProgressHeartbeatManager()


def get_heartbeat_manager() -> ProgressHeartbeatManager:
    """
    Get global heartbeat manager instance.

    Returns:
        ProgressHeartbeatManager instance
    """
    return _heartbeat_manager
