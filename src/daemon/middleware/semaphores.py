"""
Semaphore Management Middleware

This module provides semaphore management utilities for the EX-AI MCP Server.
Extracted from ws_server.py as part of code refactoring (2025-10-21).

Components:
    SemaphoreGuard: Context manager for safe semaphore operations
    recover_semaphore_leaks: Attempt to recover from semaphore leaks
    check_semaphore_health: Check for semaphore leaks and attempt recovery
"""

import asyncio
import logging
from typing import Dict

logger = logging.getLogger(__name__)


# PHASE 3 FIX (2025-10-25): Port-based semaphore isolation (EXAI validated)
# Implements Option B: Port-Based Semaphore Dictionary for clean separation
class PortSemaphoreManager:
    """
    Manages semaphores per WebSocket server port for isolation.

    This ensures that different MCP server instances (e.g., VSCode1 on port 8079,
    VSCode2 on port 8080) don't compete for the same semaphore slots.
    """

    def __init__(self):
        self._semaphores: Dict[int, asyncio.BoundedSemaphore] = {}
        self._locks: Dict[int, asyncio.Lock] = {}
        self._limits: Dict[int, int] = {}
        # EXAI FIX (2025-10-25): Add provider semaphore support for port isolation
        self._provider_semaphores: Dict[str, asyncio.BoundedSemaphore] = {}
        self._provider_limits: Dict[str, int] = {}
        logger.info("[PORT_SEM] PortSemaphoreManager initialized")

    def get_semaphore(self, port: int, limit: int = 5) -> asyncio.BoundedSemaphore:
        """
        Get or create a semaphore for the specified port.

        Args:
            port: WebSocket server port number
            limit: Maximum concurrent operations for this port

        Returns:
            BoundedSemaphore instance for this port
        """
        if port not in self._semaphores:
            self._semaphores[port] = asyncio.BoundedSemaphore(limit)
            self._limits[port] = limit
            logger.info(f"[PORT_SEM] Created semaphore for port {port} with limit {limit}")
        return self._semaphores[port]

    def get_lock(self, port: int) -> asyncio.Lock:
        """
        Get or create a lock for the specified port.

        Args:
            port: WebSocket server port number

        Returns:
            Lock instance for this port
        """
        if port not in self._locks:
            self._locks[port] = asyncio.Lock()
            logger.debug(f"[PORT_SEM] Created lock for port {port}")
        return self._locks[port]

    def get_limit(self, port: int) -> int:
        """Get the configured limit for a port's semaphore."""
        return self._limits.get(port, 5)

    def get_provider_semaphore(self, port: int, provider: str, limit: int) -> asyncio.BoundedSemaphore:
        """
        Get or create a provider-specific semaphore for the specified port.

        EXAI FIX (2025-10-25): Provider semaphores are now port-specific to prevent
        cross-port blocking. Each port+provider combination gets its own semaphore.

        Args:
            port: WebSocket server port number
            provider: Provider name (e.g., "KIMI", "GLM")
            limit: Maximum concurrent operations for this provider on this port

        Returns:
            BoundedSemaphore instance for this port+provider combination
        """
        key = f"{port}_{provider}"
        if key not in self._provider_semaphores:
            self._provider_semaphores[key] = asyncio.BoundedSemaphore(limit)
            self._provider_limits[key] = limit
            logger.info(f"[PORT_SEM] Created provider semaphore for port {port}, provider {provider} with limit {limit}")
        return self._provider_semaphores[key]

    def get_provider_limit(self, port: int, provider: str) -> int:
        """Get the configured limit for a port+provider semaphore."""
        key = f"{port}_{provider}"
        return self._provider_limits.get(key, 5)

    def get_metrics(self) -> dict:
        """
        Get semaphore metrics for monitoring dashboard.

        PHASE 2.4 ENHANCEMENT (2025-10-26): EXAI-recommended semaphore monitoring

        Returns:
            Dictionary with semaphore metrics:
            {
                'ports': {
                    8079: {'current': 8, 'limit': 10, 'available': 2},
                    8080: {'current': 6, 'limit': 10, 'available': 4}
                },
                'providers': {
                    '8079_KIMI': {'current': 3, 'limit': 3, 'available': 0},
                    '8079_GLM': {'current': 2, 'limit': 2, 'available': 0},
                    '8080_KIMI': {'current': 1, 'limit': 3, 'available': 2},
                    '8080_GLM': {'current': 0, 'limit': 2, 'available': 2}
                },
                'total_leaks_detected': 0,
                'health_status': 'healthy'  # 'healthy', 'warning', 'critical'
            }
        """
        metrics = {
            'ports': {},
            'providers': {},
            'total_leaks_detected': 0,
            'health_status': 'healthy'
        }

        # Port semaphores
        for port, semaphore in self._semaphores.items():
            limit = self._limits.get(port, 5)
            current = limit - semaphore._value  # Number of acquired slots
            available = semaphore._value

            metrics['ports'][port] = {
                'current': current,
                'limit': limit,
                'available': available,
                'usage_percent': int((current / limit) * 100) if limit > 0 else 0
            }

            # Check for leaks (current > limit indicates leak)
            if current > limit:
                metrics['total_leaks_detected'] += (current - limit)
                metrics['health_status'] = 'critical'

        # Provider semaphores
        for key, semaphore in self._provider_semaphores.items():
            limit = self._provider_limits.get(key, 5)
            current = limit - semaphore._value
            available = semaphore._value

            metrics['providers'][key] = {
                'current': current,
                'limit': limit,
                'available': available,
                'usage_percent': int((current / limit) * 100) if limit > 0 else 0
            }

            # Check for leaks
            if current > limit:
                metrics['total_leaks_detected'] += (current - limit)
                metrics['health_status'] = 'critical'

        # Set warning status if usage is high but no leaks
        if metrics['health_status'] == 'healthy':
            for port_metrics in metrics['ports'].values():
                if port_metrics['usage_percent'] > 80:
                    metrics['health_status'] = 'warning'
                    break

        return metrics


# Global instance
_port_semaphore_manager = PortSemaphoreManager()


def get_port_semaphore_manager() -> PortSemaphoreManager:
    """Get the global PortSemaphoreManager instance."""
    return _port_semaphore_manager


def get_global_semaphore(limit: int = 5) -> asyncio.BoundedSemaphore:
    """
    Legacy function for backward compatibility.

    Uses port 8079 as default for existing single-port deployments.
    """
    return _port_semaphore_manager.get_semaphore(8079, limit)


class SemaphoreGuard:
    """
    Context manager for safe semaphore operations with guaranteed release.

    Prevents semaphore leaks by ensuring release happens even if exceptions occur.
    Tracks acquisition state and handles edge cases like double-release.

    Example:
        >>> async with SemaphoreGuard(my_semaphore, "my_sem"):
        ...     # Semaphore is acquired
        ...     await do_work()
        ...     # Semaphore is automatically released, even if exception occurs
    """

    def __init__(self, semaphore, name="unknown"):
        """
        Initialize the semaphore guard.

        Args:
            semaphore: asyncio.BoundedSemaphore to manage
            name: Human-readable name for logging
        """
        self.semaphore = semaphore
        self.name = name
        self.acquired = False

    async def __aenter__(self):
        """Acquire the semaphore with error handling and tracking."""
        try:
            # PHASE 2.4 FIX (2025-10-26): EXAI COMPREHENSIVE FIX - Explicit acquire check
            # Root cause: Double-release or missing-acquire pattern causing semaphore leaks
            # EXAI recommended: Add explicit check to prevent acquiring already-acquired semaphore
            if self.acquired:
                logger.warning(f"Semaphore {self.name} already acquired, skipping duplicate acquire")
                return self

            await self.semaphore.acquire()
            self.acquired = True
            logger.debug(f"Acquired semaphore: {self.name} (value: {self.semaphore._value})")
            return self
        except Exception as e:
            logger.error(f"Failed to acquire semaphore {self.name}: {e}")
            self.acquired = False
            raise

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Release the semaphore with error handling and state tracking."""
        if self.acquired:
            try:
                # CRITICAL FIX (2025-10-31): Check if semaphore is already at max before releasing
                # Prevents "BoundedSemaphore released too many times" error when recovery system
                # has already released this semaphore
                if hasattr(self.semaphore, '_value') and hasattr(self.semaphore, '_bound_value'):
                    if self.semaphore._value >= self.semaphore._bound_value:
                        logger.warning(f"Semaphore {self.name} already at max value ({self.semaphore._value}/{self.semaphore._bound_value}), skipping release (likely recovered by recovery system)")
                        self.acquired = False  # CRITICAL: Update state
                        return True  # FIXED: Return True to suppress exception propagation

                self.semaphore.release()
                self.acquired = False  # CRITICAL: Update state
                logger.debug(f"Released semaphore: {self.name} (value: {self.semaphore._value})")
            except ValueError as e:
                # This happens when semaphore is already at max (recovery system released it)
                logger.warning(f"Semaphore {self.name} already released (likely by recovery system): {e}")
                self.acquired = False  # CRITICAL: Update state
                return True  # FIXED: Suppress the exception
            except Exception as e:
                logger.error(f"Failed to release semaphore {self.name}: {e}", exc_info=True)
                self.acquired = False  # CRITICAL: Update state even on error
                # This is a critical error that could lead to deadlocks
                logger.critical(f"CRITICAL: Semaphore leak detected for {self.name}!")
                return True  # FIXED: Suppress exception to prevent cascading failures
        else:
            logger.warning(f"Attempted to release non-acquired semaphore: {self.name}")

        return False  # Don't suppress exceptions from user code


async def recover_semaphore_leaks(
    global_sem: asyncio.BoundedSemaphore,
    global_max: int,
    provider_sems: Dict[str, asyncio.BoundedSemaphore],
    provider_limits: Dict[str, int]
) -> bool:
    """
    Attempt to recover from semaphore leaks by resetting to expected values.

    Args:
        global_sem: Global semaphore instance
        global_max: Expected maximum value for global semaphore
        provider_sems: Dictionary of provider semaphores
        provider_limits: Dictionary of expected maximum values per provider

    Returns:
        True if any leaks were recovered, False otherwise

    Example:
        >>> recovered = await recover_semaphore_leaks(
        ...     _global_sem, GLOBAL_MAX_INFLIGHT,
        ...     _provider_sems, {"KIMI": 5, "GLM": 5}
        ... )
    """
    from src.monitoring.metrics import (
        record_semaphore_recovery,
        update_semaphore_values
    )

    recovered = []
    recovery_status = "success"

    # Recover global semaphore
    if global_sem._value < global_max:
        leaked = global_max - global_sem._value
        recovered_count = 0
        for _ in range(leaked):
            try:
                global_sem.release()
                recovered_count += 1
            except ValueError:
                recovery_status = "partial"
                break  # Can't release more than acquired

        if recovered_count > 0:
            recovered.append(f"Global: +{recovered_count}")
            record_semaphore_recovery("global", recovery_status, recovered_count)

        # Update metrics
        update_semaphore_values("global", "global", global_sem._value, global_max)

    # Recover provider semaphores
    for provider, sem in provider_sems.items():
        expected = provider_limits.get(provider, 0)
        if sem._value < expected:
            leaked = expected - sem._value
            recovered_count = 0
            for _ in range(leaked):
                try:
                    sem.release()
                    recovered_count += 1
                except ValueError:
                    recovery_status = "partial"
                    break

            if recovered_count > 0:
                recovered.append(f"{provider}: +{recovered_count}")
                record_semaphore_recovery(f"provider_{provider.lower()}", recovery_status, recovered_count)

            # Update metrics
            update_semaphore_values("provider", provider.lower(), sem._value, expected)

    if recovered:
        logger.warning(f"SEMAPHORE RECOVERY: Recovered leaks: {', '.join(recovered)}")
        return True
    return False


async def check_semaphore_health(
    global_sem: asyncio.BoundedSemaphore,
    global_max: int,
    provider_sems: Dict[str, asyncio.BoundedSemaphore],
    provider_limits: Dict[str, int]
) -> None:
    """
    Check for semaphore leaks and attempt recovery.
    Enhanced with threshold-based alerting per EXAI recommendations (2025-10-21).

    Args:
        global_sem: Global semaphore instance
        global_max: Expected maximum value for global semaphore
        provider_sems: Dictionary of provider semaphores
        provider_limits: Dictionary of expected maximum values per provider

    Example:
        >>> await check_semaphore_health(
        ...     _global_sem, GLOBAL_MAX_INFLIGHT,
        ...     _provider_sems, {"KIMI": 5, "GLM": 5}
        ... )
    """
    from src.monitoring.metrics import (
        record_semaphore_leak,
        update_semaphore_values,
        record_semaphore_exhaustion
    )

    issues = []
    alerts = []

    # Check global semaphore
    global_current = global_sem._value
    global_expected = global_max

    # Leak detection
    if global_current != global_expected:
        issues.append(f"Global semaphore leak: expected {global_expected}, got {global_current}")
        record_semaphore_leak("global", global_expected, global_current)

    # Exhaustion alerting (CRITICAL)
    if global_current <= 0:
        alerts.append(f"CRITICAL: Global semaphore exhausted! (0/{global_expected} permits available)")
        record_semaphore_exhaustion("global", "global")
    # High utilization warning
    elif global_current <= global_expected * 0.1:  # 10% or less available
        alerts.append(f"WARNING: Global semaphore high utilization ({global_current}/{global_expected} permits available)")

    # Always update current values for monitoring
    update_semaphore_values("global", "global", global_current, global_expected)

    # Check provider semaphores
    for provider, sem in provider_sems.items():
        expected = provider_limits.get(provider, 0)
        current = sem._value

        # Leak detection
        if current != expected:
            issues.append(f"Provider {provider} semaphore leak: expected {expected}, got {current}")
            record_semaphore_leak(f"provider_{provider.lower()}", expected, current)

        # Exhaustion alerting (CRITICAL)
        if current <= 0:
            alerts.append(f"CRITICAL: {provider} semaphore exhausted! (0/{expected} permits available)")
            record_semaphore_exhaustion("provider", provider.lower())
        # High utilization warning
        elif current <= expected * 0.1:  # 10% or less available
            alerts.append(f"WARNING: {provider} semaphore high utilization ({current}/{expected} permits available)")

        # Always update current values for monitoring
        update_semaphore_values("provider", provider.lower(), current, expected)

    # Log alerts (highest priority)
    if alerts:
        for alert in alerts:
            if "CRITICAL" in alert:
                logger.critical(f"SEMAPHORE ALERT: {alert}")
            else:
                logger.warning(f"SEMAPHORE ALERT: {alert}")

    # Log issues
    if issues:
        for issue in issues:
            logger.warning(f"SEMAPHORE HEALTH: {issue}")

        # Attempt automatic recovery
        recovered = await recover_semaphore_leaks(
            global_sem, global_max,
            provider_sems, provider_limits
        )
        if recovered:
            logger.info("SEMAPHORE HEALTH: Automatic recovery successful")
    else:
        logger.debug("Semaphore health check passed")

