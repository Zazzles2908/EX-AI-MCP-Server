"""
Semaphore Lifecycle Tracking

Diagnostic tool for tracking semaphore acquisition/release patterns to detect leaks.
Implements EXAI recommendation from 2025-10-21 investigation.

Usage:
    tracker = SemaphoreTracker()
    
    # Track acquisition
    sem_id = tracker.track_acquire("global_sem")
    
    # Track release
    tracker.track_release(sem_id, "global_sem")
    
    # Get diagnostics
    report = tracker.get_diagnostic_report()
"""

import asyncio
import logging
import time
import traceback
import threading
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class SemaphoreAcquisition:
    """Record of a semaphore acquisition."""
    sem_id: str
    name: str
    timestamp: float
    thread_id: int
    stack_trace: List[str] = field(default_factory=list)
    released: bool = False
    release_timestamp: Optional[float] = None
    
    @property
    def duration(self) -> Optional[float]:
        """Get duration if released, None otherwise."""
        if self.release_timestamp:
            return self.release_timestamp - self.timestamp
        return None
    
    @property
    def age(self) -> float:
        """Get age of acquisition (time since acquired)."""
        return time.time() - self.timestamp


class SemaphoreTracker:
    """
    Track semaphore acquisition/release lifecycle for leak detection.
    
    Features:
    - Full stack trace capture on acquisition
    - Thread ID tracking
    - Duration measurement
    - Leak detection (unreleased acquisitions)
    - Diagnostic reporting
    
    Thread-safe for use in async contexts.
    """
    
    def __init__(self, leak_threshold_seconds: float = 60.0):
        """
        Initialize semaphore tracker.
        
        Args:
            leak_threshold_seconds: Time after which unreleased acquisition is considered a leak
        """
        self.leak_threshold = leak_threshold_seconds
        self.acquisitions: Dict[str, SemaphoreAcquisition] = {}
        self._lock = asyncio.Lock()
        self._next_id = 0
        
    def _generate_id(self) -> str:
        """Generate unique ID for tracking."""
        self._next_id += 1
        return f"sem_{self._next_id}_{int(time.time() * 1000)}"
    
    async def track_acquire(self, name: str, capture_stack: bool = True) -> str:
        """
        Track semaphore acquisition.
        
        Args:
            name: Human-readable semaphore name
            capture_stack: Whether to capture full stack trace (expensive)
            
        Returns:
            Unique ID for this acquisition (use for track_release)
        """
        sem_id = self._generate_id()
        thread_id = threading.get_ident()
        
        # Capture stack trace if requested
        stack = []
        if capture_stack:
            try:
                stack = traceback.format_stack()[:-1]  # Exclude this frame
            except Exception as e:
                logger.debug(f"Failed to capture stack trace: {e}")
        
        acquisition = SemaphoreAcquisition(
            sem_id=sem_id,
            name=name,
            timestamp=time.time(),
            thread_id=thread_id,
            stack_trace=stack
        )
        
        async with self._lock:
            self.acquisitions[sem_id] = acquisition
        
        logger.debug(
            f"[SEM_TRACK] Acquired {name} "
            f"(id={sem_id}, thread={thread_id}, total_active={len(self.acquisitions)})"
        )
        
        return sem_id
    
    async def track_release(self, sem_id: str, name: str) -> None:
        """
        Track semaphore release.
        
        Args:
            sem_id: ID returned from track_acquire
            name: Semaphore name (for validation)
        """
        async with self._lock:
            if sem_id not in self.acquisitions:
                logger.error(
                    f"[SEM_TRACK] LEAK DETECTED: Release without acquire for {name} (id={sem_id})"
                )
                return
            
            acquisition = self.acquisitions[sem_id]
            
            # Validate name matches
            if acquisition.name != name:
                logger.warning(
                    f"[SEM_TRACK] Name mismatch: acquired as '{acquisition.name}', "
                    f"released as '{name}' (id={sem_id})"
                )
            
            # Mark as released
            acquisition.released = True
            acquisition.release_timestamp = time.time()
            
            duration = acquisition.duration
            logger.debug(
                f"[SEM_TRACK] Released {name} after {duration:.2f}s "
                f"(id={sem_id}, total_active={len([a for a in self.acquisitions.values() if not a.released])})"
            )
            
            # Remove from tracking (keep only unreleased)
            del self.acquisitions[sem_id]
    
    async def get_active_acquisitions(self) -> List[SemaphoreAcquisition]:
        """Get list of currently unreleased acquisitions."""
        async with self._lock:
            return [acq for acq in self.acquisitions.values() if not acq.released]
    
    async def get_potential_leaks(self) -> List[SemaphoreAcquisition]:
        """Get acquisitions that exceed leak threshold."""
        active = await self.get_active_acquisitions()
        return [acq for acq in active if acq.age > self.leak_threshold]
    
    async def get_diagnostic_report(self) -> Dict[str, Any]:
        """
        Generate diagnostic report.
        
        Returns:
            Dictionary with:
            - total_active: Number of unreleased acquisitions
            - potential_leaks: Number of acquisitions exceeding threshold
            - by_name: Breakdown by semaphore name
            - oldest: Oldest unreleased acquisition
        """
        active = await self.get_active_acquisitions()
        leaks = await self.get_potential_leaks()
        
        # Group by name
        by_name: Dict[str, int] = {}
        for acq in active:
            by_name[acq.name] = by_name.get(acq.name, 0) + 1
        
        # Find oldest
        oldest = None
        if active:
            oldest = max(active, key=lambda a: a.age)
        
        return {
            "total_active": len(active),
            "potential_leaks": len(leaks),
            "by_name": by_name,
            "oldest": {
                "name": oldest.name,
                "age_seconds": oldest.age,
                "thread_id": oldest.thread_id,
                "timestamp": datetime.fromtimestamp(oldest.timestamp).isoformat()
            } if oldest else None,
            "leak_threshold_seconds": self.leak_threshold
        }
    
    async def log_diagnostic_report(self) -> None:
        """Log diagnostic report at INFO level."""
        report = await self.get_diagnostic_report()
        
        if report["total_active"] == 0:
            logger.debug("[SEM_TRACK] No active acquisitions")
            return
        
        logger.info(
            f"[SEM_TRACK] Diagnostic Report: "
            f"{report['total_active']} active, "
            f"{report['potential_leaks']} potential leaks, "
            f"by_name={report['by_name']}"
        )
        
        if report["oldest"]:
            logger.info(
                f"[SEM_TRACK] Oldest acquisition: "
                f"{report['oldest']['name']} "
                f"({report['oldest']['age_seconds']:.1f}s old, "
                f"thread={report['oldest']['thread_id']})"
            )
        
        # Log potential leaks at WARNING level
        if report["potential_leaks"] > 0:
            leaks = await self.get_potential_leaks()
            for leak in leaks:
                logger.warning(
                    f"[SEM_TRACK] POTENTIAL LEAK: {leak.name} "
                    f"held for {leak.age:.1f}s (threshold: {self.leak_threshold}s)"
                )
                
                # Log stack trace for leaks
                if leak.stack_trace:
                    logger.warning(
                        f"[SEM_TRACK] Stack trace for {leak.name}:\n" +
                        "".join(leak.stack_trace[-10:])  # Last 10 frames
                    )


# Global tracker instance (optional - can also create per-component)
_global_tracker: Optional[SemaphoreTracker] = None


def get_global_tracker(leak_threshold: float = 60.0) -> SemaphoreTracker:
    """Get or create global semaphore tracker instance."""
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = SemaphoreTracker(leak_threshold_seconds=leak_threshold)
    return _global_tracker


async def start_periodic_diagnostics(
    tracker: SemaphoreTracker,
    interval_seconds: float = 30.0,
    stop_event: Optional[asyncio.Event] = None
) -> None:
    """
    Run periodic diagnostic logging.
    
    Args:
        tracker: SemaphoreTracker instance
        interval_seconds: How often to log diagnostics
        stop_event: Event to signal stop (optional)
    """
    logger.info(f"[SEM_TRACK] Starting periodic diagnostics (interval={interval_seconds}s)")
    
    while True:
        if stop_event and stop_event.is_set():
            logger.info("[SEM_TRACK] Stopping periodic diagnostics")
            break
        
        try:
            await tracker.log_diagnostic_report()
        except Exception as e:
            logger.error(f"[SEM_TRACK] Error in periodic diagnostics: {e}", exc_info=True)
        
        await asyncio.sleep(interval_seconds)

