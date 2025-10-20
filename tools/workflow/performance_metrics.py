"""
Performance metrics tracking for workflow tools.

Day 3.5: Implements comprehensive performance monitoring and diagnostics.
Provides insights into execution time, memory usage, and optimization effectiveness.

Based on EXAI recommendations from continuation_id: 8b5fce66-a561-45ec-b412-68992147882c
"""

import logging
import time
from typing import Dict, List, Optional
import psutil
import os

logger = logging.getLogger(__name__)


class PerformanceMetrics:
    """
    Performance metrics tracking for workflow tools.
    
    Features:
    - Step execution time tracking
    - File read time tracking
    - Consolidation time tracking
    - Memory usage monitoring
    - Cache hit rate tracking
    - Performance summary generation
    
    Usage:
        metrics = get_performance_metrics()
        metrics.start_step(1)
        # ... do work ...
        metrics.end_step(1)
        summary = metrics.get_summary()
    """
    
    def __init__(self):
        """Initialize performance metrics."""
        self.step_times: Dict[int, Dict] = {}
        self.file_read_times: List[float] = []
        self.consolidation_times: List[float] = []
        self.memory_snapshots: List[Dict] = []
        
        self._step_start_times: Dict[int, float] = {}
        self._workflow_start_time: Optional[float] = None
        
        # Get process for memory monitoring
        self._process = psutil.Process(os.getpid())
        
        logger.info("PerformanceMetrics initialized")
    
    def start_workflow(self):
        """Mark the start of a workflow execution."""
        self._workflow_start_time = time.time()
        self._take_memory_snapshot("workflow_start")
        logger.debug("Workflow execution started")
    
    def end_workflow(self) -> float:
        """
        Mark the end of a workflow execution.
        
        Returns:
            Total workflow execution time in seconds
        """
        if self._workflow_start_time is None:
            logger.warning("end_workflow called without start_workflow")
            return 0.0
        
        elapsed = time.time() - self._workflow_start_time
        self._take_memory_snapshot("workflow_end")
        logger.debug(f"Workflow execution completed in {elapsed:.2f}s")
        return elapsed
    
    def start_step(self, step_number: int):
        """
        Mark the start of a step execution.
        
        Args:
            step_number: Step number being executed
        """
        self._step_start_times[step_number] = time.time()
        self._take_memory_snapshot(f"step_{step_number}_start")
        logger.debug(f"Step {step_number} started")
    
    def end_step(self, step_number: int):
        """
        Mark the end of a step execution.
        
        Args:
            step_number: Step number that completed
        """
        if step_number not in self._step_start_times:
            logger.warning(f"end_step called for step {step_number} without start_step")
            return
        
        elapsed = time.time() - self._step_start_times[step_number]
        self.step_times[step_number] = {
            'duration': elapsed,
            'timestamp': time.time(),
        }
        
        self._take_memory_snapshot(f"step_{step_number}_end")
        logger.debug(f"Step {step_number} completed in {elapsed:.2f}s")
    
    def record_file_read(self, duration: float):
        """
        Record a file read operation time.
        
        Args:
            duration: Time taken to read file in seconds
        """
        self.file_read_times.append(duration)
    
    def record_consolidation(self, duration: float):
        """
        Record a consolidation operation time.
        
        Args:
            duration: Time taken to consolidate in seconds
        """
        self.consolidation_times.append(duration)
    
    def _take_memory_snapshot(self, label: str):
        """
        Take a memory usage snapshot.
        
        Args:
            label: Label for this snapshot
        """
        try:
            mem_info = self._process.memory_info()
            self.memory_snapshots.append({
                'label': label,
                'timestamp': time.time(),
                'rss_mb': mem_info.rss / 1024 / 1024,  # Resident Set Size in MB
                'vms_mb': mem_info.vms / 1024 / 1024,  # Virtual Memory Size in MB
            })
        except Exception as e:
            logger.warning(f"Failed to take memory snapshot: {e}")
    
    def get_summary(self) -> Dict:
        """
        Get comprehensive performance summary.
        
        Returns:
            Dictionary with performance metrics:
            - total_steps: Number of steps executed
            - total_step_time: Total time spent in steps (seconds)
            - avg_step_time: Average time per step (seconds)
            - min_step_time: Minimum step time (seconds)
            - max_step_time: Maximum step time (seconds)
            - total_file_reads: Number of file read operations
            - total_file_read_time: Total time spent reading files (seconds)
            - avg_file_read_time: Average time per file read (seconds)
            - total_consolidations: Number of consolidation operations
            - total_consolidation_time: Total time spent consolidating (seconds)
            - avg_consolidation_time: Average time per consolidation (seconds)
            - memory_start_mb: Memory usage at workflow start (MB)
            - memory_end_mb: Memory usage at workflow end (MB)
            - memory_delta_mb: Change in memory usage (MB)
            - memory_peak_mb: Peak memory usage (MB)
        """
        summary = {}
        
        # Step timing metrics
        if self.step_times:
            step_durations = [s['duration'] for s in self.step_times.values()]
            summary['total_steps'] = len(self.step_times)
            summary['total_step_time'] = sum(step_durations)
            summary['avg_step_time'] = sum(step_durations) / len(step_durations)
            summary['min_step_time'] = min(step_durations)
            summary['max_step_time'] = max(step_durations)
        else:
            summary['total_steps'] = 0
            summary['total_step_time'] = 0
            summary['avg_step_time'] = 0
            summary['min_step_time'] = 0
            summary['max_step_time'] = 0
        
        # File read metrics
        if self.file_read_times:
            summary['total_file_reads'] = len(self.file_read_times)
            summary['total_file_read_time'] = sum(self.file_read_times)
            summary['avg_file_read_time'] = sum(self.file_read_times) / len(self.file_read_times)
        else:
            summary['total_file_reads'] = 0
            summary['total_file_read_time'] = 0
            summary['avg_file_read_time'] = 0
        
        # Consolidation metrics
        if self.consolidation_times:
            summary['total_consolidations'] = len(self.consolidation_times)
            summary['total_consolidation_time'] = sum(self.consolidation_times)
            summary['avg_consolidation_time'] = sum(self.consolidation_times) / len(self.consolidation_times)
        else:
            summary['total_consolidations'] = 0
            summary['total_consolidation_time'] = 0
            summary['avg_consolidation_time'] = 0
        
        # Memory metrics
        if self.memory_snapshots:
            start_snapshot = next((s for s in self.memory_snapshots if 'start' in s['label']), None)
            end_snapshot = next((s for s in reversed(self.memory_snapshots) if 'end' in s['label']), None)
            
            if start_snapshot:
                summary['memory_start_mb'] = start_snapshot['rss_mb']
            else:
                summary['memory_start_mb'] = 0
            
            if end_snapshot:
                summary['memory_end_mb'] = end_snapshot['rss_mb']
            else:
                summary['memory_end_mb'] = 0
            
            summary['memory_delta_mb'] = summary['memory_end_mb'] - summary['memory_start_mb']
            summary['memory_peak_mb'] = max(s['rss_mb'] for s in self.memory_snapshots)
        else:
            summary['memory_start_mb'] = 0
            summary['memory_end_mb'] = 0
            summary['memory_delta_mb'] = 0
            summary['memory_peak_mb'] = 0
        
        return summary
    
    def get_formatted_summary(self) -> str:
        """
        Get formatted performance summary as text.
        
        Returns:
            Formatted summary string
        """
        summary = self.get_summary()
        
        output = "\n=== Performance Summary ===\n\n"
        
        output += f"Steps:\n"
        output += f"  Total: {summary['total_steps']}\n"
        output += f"  Total Time: {summary['total_step_time']:.2f}s\n"
        output += f"  Avg Time: {summary['avg_step_time']:.2f}s\n"
        output += f"  Min Time: {summary['min_step_time']:.2f}s\n"
        output += f"  Max Time: {summary['max_step_time']:.2f}s\n\n"
        
        output += f"File Reads:\n"
        output += f"  Total: {summary['total_file_reads']}\n"
        output += f"  Total Time: {summary['total_file_read_time']:.2f}s\n"
        output += f"  Avg Time: {summary['avg_file_read_time']:.3f}s\n\n"
        
        output += f"Consolidations:\n"
        output += f"  Total: {summary['total_consolidations']}\n"
        output += f"  Total Time: {summary['total_consolidation_time']:.2f}s\n"
        output += f"  Avg Time: {summary['avg_consolidation_time']:.2f}s\n\n"
        
        output += f"Memory:\n"
        output += f"  Start: {summary['memory_start_mb']:.1f} MB\n"
        output += f"  End: {summary['memory_end_mb']:.1f} MB\n"
        output += f"  Delta: {summary['memory_delta_mb']:+.1f} MB\n"
        output += f"  Peak: {summary['memory_peak_mb']:.1f} MB\n"
        
        output += "\n=========================="
        
        return output
    
    def clear(self):
        """Clear all metrics."""
        self.step_times.clear()
        self.file_read_times.clear()
        self.consolidation_times.clear()
        self.memory_snapshots.clear()
        self._step_start_times.clear()
        self._workflow_start_time = None
        logger.info("Performance metrics cleared")


# Singleton instance for shared metrics across workflow tools
_performance_metrics: Optional[PerformanceMetrics] = None


def get_performance_metrics() -> PerformanceMetrics:
    """
    Get singleton performance metrics instance.
    
    Returns:
        Shared PerformanceMetrics instance
    """
    global _performance_metrics
    if _performance_metrics is None:
        _performance_metrics = PerformanceMetrics()
    return _performance_metrics


def reset_performance_metrics():
    """Reset the performance metrics (useful for testing)."""
    global _performance_metrics
    if _performance_metrics is not None:
        _performance_metrics.clear()
    _performance_metrics = None

