"""
Request Handler Monitoring Module

This module provides execution monitoring and progress tracking including:
- Watchdog and heartbeat implementation
- Timeout handling
- Progress capture integration
- Cancellation support
- JSONL event recording
"""

import asyncio
import logging
import time
import os
from typing import Any, Callable, Dict

logger = logging.getLogger(__name__)


def load_monitoring_config() -> Dict[str, float]:
    """
    Load watchdog and timeout configuration from environment.
    
    Returns:
        Dictionary with timeout and heartbeat configuration
    """
    try:
        tool_timeout_s = float(os.getenv("EX_TOOL_TIMEOUT_SECONDS", "120"))
        hb_every_s = float(os.getenv("EX_HEARTBEAT_SECONDS", "10"))
        warn_after_s = float(os.getenv("EX_WATCHDOG_WARN_SECONDS", "30"))
        err_after_s = float(os.getenv("EX_WATCHDOG_ERROR_SECONDS", "90"))
    except Exception:
        tool_timeout_s, hb_every_s, warn_after_s, err_after_s = 120.0, 10.0, 30.0, 90.0
    
    return {
        'tool_timeout_s': tool_timeout_s,
        'hb_every_s': hb_every_s,
        'warn_after_s': warn_after_s,
        'err_after_s': err_after_s,
    }


async def execute_with_monitor(
    coro_factory: Callable,
    name: str,
    req_id: str,
    config: Dict[str, Any]
) -> Any:
    """
    Execute tool with monitoring, heartbeat, and timeout.
    
    This function wraps tool execution with:
    - Background heartbeat task for progress tracking
    - Timeout enforcement
    - Watchdog warnings and errors
    - Cancellation handling
    - JSONL event recording
    
    Args:
        coro_factory: Coroutine factory function that returns the tool execution coroutine
        name: Tool name
        req_id: Request ID
        config: Monitoring configuration including timeouts and event tracking
        
    Returns:
        Tool execution result
        
    Raises:
        asyncio.TimeoutError: If execution exceeds timeout
        asyncio.CancelledError: If execution is cancelled
    """
    start = time.time()
    
    # Extract configuration
    tool_timeout_s = config.get('tool_timeout_s', 120.0)
    hb_every_s = config.get('hb_every_s', 10.0)
    warn_after_s = config.get('warn_after_s', 30.0)
    err_after_s = config.get('err_after_s', 90.0)
    
    # Event tracking
    ex_mirror = config.get('ex_mirror', False)
    evt = config.get('event')
    sink = config.get('sink')
    
    # Background heartbeat
    mcp_logger = logging.getLogger("mcp_activity")
    _stop = False
    
    async def _heartbeat():
        """Background heartbeat task for progress tracking."""
        last_warned = False
        while not _stop:
            elapsed = time.time() - start
            try:
                if elapsed >= err_after_s:
                    mcp_logger.error(f"[WATCHDOG] tool={name} req_id={req_id} elapsed={elapsed:.1f}s — escalating")
                elif elapsed >= warn_after_s and not last_warned:
                    mcp_logger.warning(f"[WATCHDOG] tool={name} req_id={req_id} elapsed={elapsed:.1f}s — still running")
                    last_warned = True
                else:
                    mcp_logger.info(f"[PROGRESS] tool={name} req_id={req_id} elapsed={elapsed:.1f}s — heartbeat")
            except Exception:
                pass
            try:
                await asyncio.sleep(hb_every_s)
            except Exception:
                break
    
    hb_task = asyncio.create_task(_heartbeat())
    try:
        main_task = asyncio.create_task(coro_factory())
        result = await asyncio.wait_for(main_task, timeout=tool_timeout_s)
        
        # Record success
        try:
            if ex_mirror and evt and sink:
                evt.end(ok=True)
                sink.record(evt)
        except Exception:
            pass
        
        return result
    
    except asyncio.CancelledError:
        # Propagate cancellation (e.g., client disconnect) but record structured end
        try:
            mcp_logger.info(f"TOOL_CANCELLED: {name} req_id={req_id}")
        except Exception:
            pass
        try:
            main_task.cancel()
        except Exception:
            pass
        try:
            if ex_mirror and evt and sink:
                evt.end(ok=False, error="cancelled")
                sink.record(evt)
        except Exception:
            pass
        raise
    
    finally:
        _stop = True
        try:
            hb_task.cancel()
        except Exception:
            pass


# Export public API
__all__ = [
    'load_monitoring_config',
    'execute_with_monitor',
]

