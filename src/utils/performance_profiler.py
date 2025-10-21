"""
Performance Profiling Utilities

Diagnostic tools for profiling execution time and identifying bottlenecks.
Implements EXAI recommendation from 2025-10-21 investigation.

Usage:
    profiler = PerformanceProfiler("expert_analysis")
    
    profiler.checkpoint("start")
    # ... do work ...
    profiler.checkpoint("prompt_built")
    # ... do more work ...
    profiler.checkpoint("api_complete")
    
    profiler.log_report()
"""

import time
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class Checkpoint:
    """Record of a performance checkpoint."""
    name: str
    timestamp: float
    metadata: Dict = field(default_factory=dict)
    
    def elapsed_since(self, other: 'Checkpoint') -> float:
        """Get elapsed time since another checkpoint."""
        return self.timestamp - other.timestamp


class PerformanceProfiler:
    """
    Track execution time with named checkpoints.
    
    Features:
    - Named checkpoints for different execution phases
    - Automatic duration calculation between checkpoints
    - Metadata attachment (e.g., prompt size, API response size)
    - Diagnostic reporting
    
    Example:
        profiler = PerformanceProfiler("my_operation")
        profiler.checkpoint("start")
        # ... work ...
        profiler.checkpoint("phase1_complete", metadata={"items_processed": 100})
        # ... more work ...
        profiler.checkpoint("phase2_complete")
        profiler.log_report()  # Logs timing breakdown
    """
    
    def __init__(self, operation_name: str):
        """
        Initialize profiler.
        
        Args:
            operation_name: Name of operation being profiled
        """
        self.operation_name = operation_name
        self.checkpoints: List[Checkpoint] = []
        self.start_time = time.time()
        
    def checkpoint(self, name: str, metadata: Optional[Dict] = None) -> None:
        """
        Record a checkpoint.
        
        Args:
            name: Checkpoint name (e.g., "prompt_built", "api_complete")
            metadata: Optional metadata to attach (e.g., {"size": 1024})
        """
        checkpoint = Checkpoint(
            name=name,
            timestamp=time.time(),
            metadata=metadata or {}
        )
        self.checkpoints.append(checkpoint)
        
        logger.debug(
            f"[PROFILE] {self.operation_name}.{name} "
            f"(+{checkpoint.timestamp - self.start_time:.2f}s)"
        )
    
    def get_duration(self, start_checkpoint: str, end_checkpoint: str) -> Optional[float]:
        """
        Get duration between two checkpoints.
        
        Args:
            start_checkpoint: Name of start checkpoint
            end_checkpoint: Name of end checkpoint
            
        Returns:
            Duration in seconds, or None if checkpoints not found
        """
        start = next((c for c in self.checkpoints if c.name == start_checkpoint), None)
        end = next((c for c in self.checkpoints if c.name == end_checkpoint), None)
        
        if start and end:
            return end.elapsed_since(start)
        return None
    
    def get_total_duration(self) -> float:
        """Get total duration from start to last checkpoint."""
        if not self.checkpoints:
            return 0.0
        return self.checkpoints[-1].timestamp - self.start_time
    
    def get_report(self) -> Dict:
        """
        Generate performance report.
        
        Returns:
            Dictionary with:
            - operation: Operation name
            - total_duration: Total time
            - checkpoints: List of checkpoint details
            - phases: Duration breakdown between consecutive checkpoints
        """
        if not self.checkpoints:
            return {
                "operation": self.operation_name,
                "total_duration": 0.0,
                "checkpoints": [],
                "phases": []
            }
        
        # Build checkpoint details
        checkpoint_details = []
        for i, cp in enumerate(self.checkpoints):
            checkpoint_details.append({
                "name": cp.name,
                "elapsed_from_start": cp.timestamp - self.start_time,
                "metadata": cp.metadata
            })
        
        # Build phase durations (time between consecutive checkpoints)
        phases = []
        for i in range(len(self.checkpoints) - 1):
            current = self.checkpoints[i]
            next_cp = self.checkpoints[i + 1]
            phases.append({
                "from": current.name,
                "to": next_cp.name,
                "duration": next_cp.elapsed_since(current)
            })
        
        return {
            "operation": self.operation_name,
            "total_duration": self.get_total_duration(),
            "checkpoints": checkpoint_details,
            "phases": phases
        }
    
    def log_report(self, level: int = logging.INFO) -> None:
        """
        Log performance report.
        
        Args:
            level: Logging level (default: INFO)
        """
        report = self.get_report()
        
        if not report["checkpoints"]:
            logger.log(level, f"[PROFILE] {self.operation_name}: No checkpoints recorded")
            return
        
        # Log summary
        logger.log(
            level,
            f"[PROFILE] {self.operation_name} completed in {report['total_duration']:.2f}s"
        )
        
        # Log phase breakdown
        if report["phases"]:
            phase_summary = ", ".join([
                f"{p['from']}→{p['to']}: {p['duration']:.2f}s"
                for p in report["phases"]
            ])
            logger.log(level, f"[PROFILE] Phase breakdown: {phase_summary}")
        
        # Log metadata if present
        for cp in report["checkpoints"]:
            if cp["metadata"]:
                logger.log(
                    level,
                    f"[PROFILE] {cp['name']} metadata: {cp['metadata']}"
                )
    
    def get_slowest_phase(self) -> Optional[Dict]:
        """
        Get the slowest phase (longest duration between checkpoints).
        
        Returns:
            Dictionary with from, to, duration, or None if no phases
        """
        report = self.get_report()
        if not report["phases"]:
            return None
        
        return max(report["phases"], key=lambda p: p["duration"])


# Context manager for automatic profiling
class ProfiledOperation:
    """
    Context manager for automatic profiling.
    
    Example:
        with ProfiledOperation("my_operation") as profiler:
            profiler.checkpoint("phase1_start")
            # ... work ...
            profiler.checkpoint("phase1_complete")
        # Report is automatically logged on exit
    """
    
    def __init__(self, operation_name: str, auto_log: bool = True):
        """
        Initialize profiled operation.
        
        Args:
            operation_name: Name of operation
            auto_log: Whether to automatically log report on exit
        """
        self.profiler = PerformanceProfiler(operation_name)
        self.auto_log = auto_log
        
    def __enter__(self) -> PerformanceProfiler:
        """Enter context - return profiler."""
        self.profiler.checkpoint("start")
        return self.profiler
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context - log report if enabled."""
        self.profiler.checkpoint("end")
        
        if self.auto_log:
            if exc_type:
                logger.error(
                    f"[PROFILE] {self.profiler.operation_name} failed after "
                    f"{self.profiler.get_total_duration():.2f}s: {exc_val}"
                )
            else:
                self.profiler.log_report()
        
        return False  # Don't suppress exceptions


# Decorator for automatic function profiling
def profile_function(operation_name: Optional[str] = None):
    """
    Decorator to automatically profile a function.
    
    Args:
        operation_name: Optional custom name (defaults to function name)
    
    Example:
        @profile_function()
        async def my_slow_function():
            # ... work ...
            pass
    """
    def decorator(func):
        import functools
        import asyncio
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            name = operation_name or func.__name__
            with ProfiledOperation(name) as profiler:
                result = await func(*args, **kwargs)
                return result
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            name = operation_name or func.__name__
            with ProfiledOperation(name) as profiler:
                result = func(*args, **kwargs)
                return result
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

