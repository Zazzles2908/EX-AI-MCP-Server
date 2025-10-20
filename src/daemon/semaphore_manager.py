"""
Semaphore Manager for EXAI MCP Server

Provides proper semaphore management with context managers to prevent leaks.
Fixes Bug #11 (semaphore leaks causing "BoundedSemaphore released too many times" errors).

Created: 2025-10-20
Author: EXAI Agent (with EXAI consultation)
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class SemaphoreManager:
    """
    Manages semaphores with proper context management to prevent leaks.
    
    Features:
    - Context manager for safe acquisition/release
    - Automatic leak detection and logging
    - Usage statistics and monitoring
    - Thread-safe operation tracking
    
    Usage:
        semaphore_manager = SemaphoreManager(max_concurrent=5)
        async with semaphore_manager.acquire():
            # Your code here
            pass
    """
    
    def __init__(self, max_concurrent: int = 5, name: str = "unnamed"):
        """
        Initialize semaphore manager.
        
        Args:
            max_concurrent: Maximum number of concurrent operations
            name: Name for logging and identification
        """
        self.semaphore = asyncio.BoundedSemaphore(max_concurrent)
        self.max_concurrent = max_concurrent
        self.name = name
        
        # Tracking
        self.active_requests = 0
        self.total_acquired = 0
        self.total_released = 0
        self.total_errors = 0
        
        # Timestamps
        self.created_at = datetime.now()
        self.last_acquire_at: Optional[datetime] = None
        self.last_release_at: Optional[datetime] = None
        
        logger.info(f"[SEMAPHORE_MANAGER] Created '{self.name}' with max_concurrent={max_concurrent}")
    
    @asynccontextmanager
    async def acquire(self, timeout: Optional[float] = None):
        """
        Context manager for safe semaphore acquisition and release.
        
        Args:
            timeout: Optional timeout in seconds for acquisition
            
        Yields:
            None
            
        Raises:
            asyncio.TimeoutError: If timeout is exceeded
            Exception: Any exception from the wrapped code
        """
        acquired = False
        acquire_start = datetime.now()
        
        try:
            # Acquire with optional timeout
            if timeout:
                await asyncio.wait_for(self.semaphore.acquire(), timeout=timeout)
            else:
                await self.semaphore.acquire()
            
            acquired = True
            self.active_requests += 1
            self.total_acquired += 1
            self.last_acquire_at = datetime.now()
            
            acquire_duration = (self.last_acquire_at - acquire_start).total_seconds()
            
            logger.debug(
                f"[SEMAPHORE_MANAGER] '{self.name}' acquired "
                f"(active: {self.active_requests}/{self.max_concurrent}, "
                f"wait: {acquire_duration:.3f}s)"
            )
            
            yield
            
        except asyncio.TimeoutError:
            logger.error(
                f"[SEMAPHORE_MANAGER] '{self.name}' acquisition timeout "
                f"after {timeout}s (active: {self.active_requests}/{self.max_concurrent})"
            )
            self.total_errors += 1
            raise
            
        except Exception as e:
            logger.error(
                f"[SEMAPHORE_MANAGER] '{self.name}' error in context: {e}"
            )
            self.total_errors += 1
            raise
            
        finally:
            # Only release if we successfully acquired
            if acquired:
                try:
                    self.semaphore.release()
                    self.active_requests -= 1
                    self.total_released += 1
                    self.last_release_at = datetime.now()
                    
                    logger.debug(
                        f"[SEMAPHORE_MANAGER] '{self.name}' released "
                        f"(active: {self.active_requests}/{self.max_concurrent})"
                    )
                    
                except ValueError as e:
                    # This catches "BoundedSemaphore released too many times"
                    logger.critical(
                        f"[SEMAPHORE_MANAGER] '{self.name}' CRITICAL: "
                        f"Attempted to release more times than acquired! "
                        f"Error: {e} "
                        f"(acquired: {self.total_acquired}, released: {self.total_released})"
                    )
                    self.total_errors += 1
                    # Don't re-raise - we want to continue execution
    
    def get_stats(self) -> Dict:
        """
        Get semaphore statistics for monitoring.
        
        Returns:
            Dictionary with semaphore statistics
        """
        now = datetime.now()
        uptime = (now - self.created_at).total_seconds()
        
        stats = {
            "name": self.name,
            "active_requests": self.active_requests,
            "max_concurrent": self.max_concurrent,
            "total_acquired": self.total_acquired,
            "total_released": self.total_released,
            "total_errors": self.total_errors,
            "leak_detected": self.total_acquired != self.total_released,
            "leak_count": self.total_acquired - self.total_released,
            "utilization": self.active_requests / self.max_concurrent if self.max_concurrent > 0 else 0,
            "uptime_seconds": uptime,
        }
        
        if self.last_acquire_at:
            stats["last_acquire_at"] = self.last_acquire_at.isoformat()
            stats["seconds_since_last_acquire"] = (now - self.last_acquire_at).total_seconds()
        
        if self.last_release_at:
            stats["last_release_at"] = self.last_release_at.isoformat()
            stats["seconds_since_last_release"] = (now - self.last_release_at).total_seconds()
        
        return stats
    
    def log_stats(self, level: str = "info"):
        """
        Log current semaphore statistics.
        
        Args:
            level: Log level (debug, info, warning, error)
        """
        stats = self.get_stats()
        
        log_func = getattr(logger, level, logger.info)
        log_func(
            f"[SEMAPHORE_MANAGER] '{self.name}' stats: "
            f"active={stats['active_requests']}/{stats['max_concurrent']}, "
            f"acquired={stats['total_acquired']}, "
            f"released={stats['total_released']}, "
            f"errors={stats['total_errors']}, "
            f"leak={'YES' if stats['leak_detected'] else 'NO'}"
        )
        
        if stats["leak_detected"]:
            logger.warning(
                f"[SEMAPHORE_MANAGER] '{self.name}' LEAK DETECTED: "
                f"{stats['leak_count']} unreleased semaphores!"
            )
    
    async def health_check(self) -> bool:
        """
        Perform health check on semaphore.
        
        Returns:
            True if healthy, False if issues detected
        """
        stats = self.get_stats()
        healthy = True
        
        # Check for leaks
        if stats["leak_detected"]:
            logger.warning(
                f"[SEMAPHORE_HEALTH] '{self.name}' leak detected: "
                f"acquired={stats['total_acquired']}, released={stats['total_released']}"
            )
            healthy = False
        
        # Check for high utilization
        if stats["utilization"] >= 0.9:
            logger.warning(
                f"[SEMAPHORE_HEALTH] '{self.name}' high utilization: "
                f"{stats['active_requests']}/{stats['max_concurrent']} ({stats['utilization']:.1%})"
            )
        
        # Check for errors
        if stats["total_errors"] > 0:
            logger.warning(
                f"[SEMAPHORE_HEALTH] '{self.name}' has {stats['total_errors']} errors"
            )
        
        return healthy


# Global semaphore managers
_global_semaphore_manager: Optional[SemaphoreManager] = None
_provider_semaphore_managers: Dict[str, SemaphoreManager] = {}


def get_global_semaphore_manager(max_concurrent: int = 5) -> SemaphoreManager:
    """
    Get or create the global semaphore manager.
    
    Args:
        max_concurrent: Maximum concurrent operations (only used on first call)
        
    Returns:
        Global SemaphoreManager instance
    """
    global _global_semaphore_manager
    if _global_semaphore_manager is None:
        _global_semaphore_manager = SemaphoreManager(
            max_concurrent=max_concurrent,
            name="global"
        )
    return _global_semaphore_manager


def get_provider_semaphore_manager(provider: str, max_concurrent: int = 3) -> SemaphoreManager:
    """
    Get or create a provider-specific semaphore manager.
    
    Args:
        provider: Provider name (e.g., "KIMI", "GLM")
        max_concurrent: Maximum concurrent operations for this provider
        
    Returns:
        Provider-specific SemaphoreManager instance
    """
    global _provider_semaphore_managers
    if provider not in _provider_semaphore_managers:
        _provider_semaphore_managers[provider] = SemaphoreManager(
            max_concurrent=max_concurrent,
            name=f"provider-{provider}"
        )
    return _provider_semaphore_managers[provider]


async def health_check_all() -> Dict[str, bool]:
    """
    Perform health check on all semaphore managers.
    
    Returns:
        Dictionary mapping semaphore names to health status
    """
    results = {}
    
    # Check global semaphore
    if _global_semaphore_manager:
        results["global"] = await _global_semaphore_manager.health_check()
    
    # Check provider semaphores
    for provider, manager in _provider_semaphore_managers.items():
        results[f"provider-{provider}"] = await manager.health_check()
    
    return results


def log_stats_all(level: str = "info"):
    """
    Log statistics for all semaphore managers.
    
    Args:
        level: Log level (debug, info, warning, error)
    """
    # Log global semaphore
    if _global_semaphore_manager:
        _global_semaphore_manager.log_stats(level)
    
    # Log provider semaphores
    for manager in _provider_semaphore_managers.values():
        manager.log_stats(level)

