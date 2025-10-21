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
                self.semaphore.release()
                self.acquired = False
                logger.debug(f"Released semaphore: {self.name} (value: {self.semaphore._value})")
            except Exception as e:
                logger.error(f"Failed to release semaphore {self.name}: {e}")
                # This is a critical error that could lead to deadlocks
                logger.critical(f"CRITICAL: Semaphore leak detected for {self.name}!")
        else:
            logger.warning(f"Attempted to release non-acquired semaphore: {self.name}")


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

