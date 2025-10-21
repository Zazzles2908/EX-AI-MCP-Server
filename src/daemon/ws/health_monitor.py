"""
WebSocket Health Monitor

Handles health monitoring, semaphore health checks, and health file writing.
Extracted from ws_server.py as part of Week 3 Fix #15 (2025-10-21).

This module contains:
- HealthMonitor class - Health monitoring and reporting
- Periodic health file writing
- Semaphore health checking and leak recovery
"""

import asyncio
import json
import logging
import os
import time
from datetime import timedelta
from pathlib import Path
from typing import Any, Dict, Optional

# Import semaphore management
from src.daemon.middleware.semaphores import (
    recover_semaphore_leaks as _recover_semaphore_leaks_impl,
    check_semaphore_health as _check_semaphore_health_impl,
)

logger = logging.getLogger(__name__)


class HealthMonitor:
    """
    Handles health monitoring and reporting.
    
    Provides:
    - Periodic health file writing
    - Semaphore health checking
    - Semaphore leak recovery
    - Health snapshot generation
    """
    
    def __init__(
        self,
        health_path: Path,
        global_sem: asyncio.Semaphore,
        provider_sems: Dict[str, asyncio.Semaphore],
        session_handler,
        server_tools: Dict[str, Any],
        host: str,
        port: int,
        started_at: float,
        global_max_inflight: int,
        provider_max_inflight: Dict[str, int]
    ):
        """
        Initialize health monitor.
        
        Args:
            health_path: Path to health file
            global_sem: Global semaphore
            provider_sems: Provider-specific semaphores
            session_handler: SessionHandler instance
            server_tools: Dictionary of available tools
            host: WebSocket host
            port: WebSocket port
            started_at: Server start timestamp
            global_max_inflight: Global max inflight requests
            provider_max_inflight: Provider-specific max inflight requests
        """
        self.health_path = health_path
        self.global_sem = global_sem
        self.provider_sems = provider_sems
        self.session_handler = session_handler
        self.server_tools = server_tools
        self.host = host
        self.port = port
        self.started_at = started_at
        self.global_max_inflight = global_max_inflight
        self.provider_max_inflight = provider_max_inflight
        
        # Tasks
        self.health_writer_task: Optional[asyncio.Task] = None
        self.semaphore_health_task: Optional[asyncio.Task] = None
    
    async def recover_semaphore_leaks(self) -> int:
        """
        Recover leaked semaphores.
        
        Returns:
            Number of leaks recovered
        """
        return await _recover_semaphore_leaks_impl(
            self.global_sem,
            self.global_max_inflight,
            self.provider_sems,
            self.provider_max_inflight
        )
    
    async def check_semaphore_health(self) -> None:
        """Check semaphore health and log warnings if needed."""
        await _check_semaphore_health_impl(
            self.global_sem,
            self.global_max_inflight,
            self.provider_sems,
            self.provider_max_inflight
        )
    
    async def start_periodic_semaphore_health(self, stop_event: asyncio.Event) -> None:
        """
        Start periodic semaphore health monitoring.
        
        Week 2 Fix #6 (2025-10-21): Centralized timeout configuration.
        
        Args:
            stop_event: Event to signal task shutdown
        """
        interval = float(os.getenv("EXAI_SEMAPHORE_HEALTH_CHECK_INTERVAL", "30"))
        
        logger.info(f"[HEALTH] Starting periodic semaphore health check (interval: {interval}s)")
        
        while not stop_event.is_set():
            await self.check_semaphore_health()
            try:
                await asyncio.wait_for(stop_event.wait(), timeout=interval)
            except asyncio.TimeoutError:
                continue
        
        logger.info("[HEALTH] Periodic semaphore health check stopped")
    
    async def start_health_writer(self, stop_event: asyncio.Event) -> None:
        """
        Start health writer task that updates health file periodically.
        
        CRITICAL FIX (P0): Added timeout to prevent indefinite blocking on session list.
        If session manager lock is held for >2s, use empty list to keep health file fresh.
        
        Args:
            stop_event: Event to signal task shutdown
        """
        last_successful_write = time.time()
        health_interval = float(os.getenv("EXAI_HEALTH_WRITER_INTERVAL", "10"))
        session_lock_timeout = float(os.getenv("EXAI_HEALTH_WRITER_SESSION_LOCK_TIMEOUT", "2.0"))
        
        logger.info(f"[HEALTH] Starting health writer (interval: {health_interval}s)")
        
        while not stop_event.is_set():
            try:
                # Get session IDs with timeout
                try:
                    sess_ids = await asyncio.wait_for(
                        self.session_handler.list_session_ids(),
                        timeout=session_lock_timeout
                    )
                except asyncio.TimeoutError:
                    logger.warning(
                        f"Health writer timeout getting session IDs (lock held >{session_lock_timeout}s), "
                        "using empty list"
                    )
                    sess_ids = []
                except Exception as e:
                    logger.debug(f"Failed to list session IDs for health writer: {e}")
                    sess_ids = []
                
                # Get global inflight count
                try:
                    inflight_global = self.global_max_inflight - self.global_sem._value  # type: ignore[attr-defined]
                except Exception as e:
                    logger.debug(f"Failed to get global semaphore value for health writer: {e}")
                    inflight_global = None
                
                # Calculate uptime
                uptime_seconds = int(time.time() - self.started_at) if self.started_at else 0
                
                # Create health snapshot
                snapshot = {
                    "t": time.time(),
                    "pid": os.getpid(),
                    "host": self.host,
                    "port": self.port,
                    "started_at": self.started_at,
                    "uptime_human": str(timedelta(seconds=uptime_seconds)),
                    "sessions": len(sess_ids),
                    "global_capacity": self.global_max_inflight,
                    "global_inflight": inflight_global,
                    "tool_count": len(self.server_tools),
                }
                
                # Write health file
                try:
                    self.health_path.write_text(
                        json.dumps(snapshot, sort_keys=True, indent=2),
                        encoding="utf-8"
                    )
                    last_successful_write = time.time()
                except Exception as e:
                    logger.warning(f"Failed to write health file: {e}")
                
                # Monitor health writer staleness
                time_since_write = time.time() - last_successful_write
                if time_since_write > 30:
                    logger.critical(
                        f"Health writer failed for {int(time_since_write)}s - daemon may be stuck. "
                        "This indicates a serious issue with the event loop or blocking operations."
                    )
            
            except Exception as e:
                logger.error(f"Health writer error: {e}", exc_info=True)
            
            # Wait for next interval
            try:
                await asyncio.wait_for(stop_event.wait(), timeout=health_interval)
            except asyncio.TimeoutError:
                continue
        
        logger.info("[HEALTH] Health writer stopped")
    
    def start_monitoring_tasks(self, stop_event: asyncio.Event) -> tuple[asyncio.Task, asyncio.Task]:
        """
        Start all health monitoring tasks.
        
        Args:
            stop_event: Event to signal task shutdown
            
        Returns:
            Tuple of (health_writer_task, semaphore_health_task)
        """
        self.health_writer_task = asyncio.create_task(self.start_health_writer(stop_event))
        self.semaphore_health_task = asyncio.create_task(self.start_periodic_semaphore_health(stop_event))
        
        return self.health_writer_task, self.semaphore_health_task
    
    async def stop_monitoring_tasks(self) -> None:
        """Stop all health monitoring tasks."""
        tasks = []
        
        if self.health_writer_task and not self.health_writer_task.done():
            self.health_writer_task.cancel()
            tasks.append(self.health_writer_task)
        
        if self.semaphore_health_task and not self.semaphore_health_task.done():
            self.semaphore_health_task.cancel()
            tasks.append(self.semaphore_health_task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

