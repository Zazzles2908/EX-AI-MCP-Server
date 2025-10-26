"""
Memory monitoring and alerting for EX-AI MCP Server.

Provides comprehensive memory tracking, leak detection, and alerting capabilities.
"""

import os
import gc
import time
import logging
import psutil
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """Memory alert severity levels."""
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"
    LEAK_DETECTED = "leak_detected"


@dataclass
class MemoryMetrics:
    """Memory usage metrics snapshot."""
    timestamp: datetime
    
    # Process memory (bytes)
    rss: int  # Resident Set Size (physical memory)
    vms: int  # Virtual Memory Size
    shared: int  # Shared memory
    
    # Python-specific
    heap_size: int  # Python heap size
    gc_collections: Dict[int, int]  # GC collections by generation
    gc_objects: int  # Total tracked objects
    
    # Container memory (if available)
    container_limit: Optional[int] = None
    container_usage: Optional[int] = None
    
    # Calculated metrics
    rss_percent: float = 0.0  # RSS as % of available memory
    growth_rate_mb_per_hour: float = 0.0  # Memory growth rate
    
    def to_dict(self) -> Dict:
        """Convert metrics to dictionary for JSON serialization."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "process_memory": {
                "rss_bytes": self.rss,
                "rss_mb": round(self.rss / (1024 * 1024), 2),
                "vms_bytes": self.vms,
                "vms_mb": round(self.vms / (1024 * 1024), 2),
                "shared_bytes": self.shared,
                "shared_mb": round(self.shared / (1024 * 1024), 2),
                "rss_percent": round(self.rss_percent, 2),
            },
            "python_memory": {
                "heap_bytes": self.heap_size,
                "heap_mb": round(self.heap_size / (1024 * 1024), 2),
                "gc_collections": self.gc_collections,
                "gc_objects": self.gc_objects,
            },
            "container_memory": {
                "limit_bytes": self.container_limit,
                "limit_mb": round(self.container_limit / (1024 * 1024), 2) if self.container_limit else None,
                "usage_bytes": self.container_usage,
                "usage_mb": round(self.container_usage / (1024 * 1024), 2) if self.container_usage else None,
            } if self.container_limit or self.container_usage else None,
            "analysis": {
                "growth_rate_mb_per_hour": round(self.growth_rate_mb_per_hour, 2),
            }
        }


@dataclass
class MemoryAlert:
    """Memory alert information."""
    level: AlertLevel
    message: str
    timestamp: datetime
    metrics: MemoryMetrics
    threshold_exceeded: Optional[str] = None


class MemoryMonitor:
    """
    Comprehensive memory monitoring with alerting and leak detection.
    
    Features:
    - Process and container memory tracking
    - Configurable alerting thresholds
    - Memory leak detection via growth rate analysis
    - GC statistics monitoring
    """
    
    def __init__(
        self,
        warning_threshold_percent: float = 80.0,
        critical_threshold_percent: float = 90.0,
        leak_detection_mb_per_hour: float = 100.0,
        collection_interval_seconds: int = 60,
        history_size: int = 100,
    ):
        """
        Initialize memory monitor.
        
        Args:
            warning_threshold_percent: Warning threshold (% of available memory)
            critical_threshold_percent: Critical threshold (% of available memory)
            leak_detection_mb_per_hour: Memory growth rate indicating leak (MB/hour)
            collection_interval_seconds: Metrics collection interval
            history_size: Number of historical metrics to retain
        """
        self.warning_threshold = warning_threshold_percent
        self.critical_threshold = critical_threshold_percent
        self.leak_threshold = leak_detection_mb_per_hour
        self.collection_interval = collection_interval_seconds
        self.history_size = history_size
        
        # Process handle
        self.process = psutil.Process()
        
        # Metrics history
        self.metrics_history: List[MemoryMetrics] = []
        self.baseline_metrics: Optional[MemoryMetrics] = None
        
        # Alert state
        self.current_alert_level = AlertLevel.NORMAL
        self.last_alert: Optional[MemoryAlert] = None
        
        # Timing
        self.last_collection_time = 0.0
        
        logger.info(
            f"Memory monitor initialized: warning={warning_threshold_percent}%, "
            f"critical={critical_threshold_percent}%, leak_threshold={leak_detection_mb_per_hour}MB/h"
        )
    
    def collect_metrics(self) -> MemoryMetrics:
        """Collect current memory metrics."""
        now = datetime.now()
        
        # Process memory info
        mem_info = self.process.memory_info()
        
        # GC statistics
        gc_stats = gc.get_stats()
        gc_collections = {i: gc.get_count()[i] for i in range(3)}
        gc_objects = len(gc.get_objects())
        
        # Python heap size (approximate)
        heap_size = sum(stat.get('collected', 0) for stat in gc_stats)
        
        # Container memory (read from cgroup if available)
        container_limit, container_usage = self._get_container_memory()
        
        # Calculate RSS percentage
        total_memory = psutil.virtual_memory().total
        rss_percent = (mem_info.rss / total_memory) * 100 if total_memory > 0 else 0.0
        
        # Calculate growth rate
        growth_rate = self._calculate_growth_rate(mem_info.rss)
        
        metrics = MemoryMetrics(
            timestamp=now,
            rss=mem_info.rss,
            vms=mem_info.vms,
            shared=getattr(mem_info, 'shared', 0),
            heap_size=heap_size,
            gc_collections=gc_collections,
            gc_objects=gc_objects,
            container_limit=container_limit,
            container_usage=container_usage,
            rss_percent=rss_percent,
            growth_rate_mb_per_hour=growth_rate,
        )
        
        # Update history
        self.metrics_history.append(metrics)
        if len(self.metrics_history) > self.history_size:
            self.metrics_history.pop(0)
        
        # Set baseline if not set
        if self.baseline_metrics is None:
            self.baseline_metrics = metrics
            logger.info(f"Memory baseline set: RSS={metrics.rss / (1024*1024):.2f}MB")
        
        return metrics
    
    def _get_container_memory(self) -> tuple[Optional[int], Optional[int]]:
        """Read container memory limits and usage from cgroup."""
        try:
            # Try cgroup v2 first
            limit_path = "/sys/fs/cgroup/memory.max"
            usage_path = "/sys/fs/cgroup/memory.current"
            
            if not os.path.exists(limit_path):
                # Fall back to cgroup v1
                limit_path = "/sys/fs/cgroup/memory/memory.limit_in_bytes"
                usage_path = "/sys/fs/cgroup/memory/memory.usage_in_bytes"
            
            limit = None
            usage = None
            
            if os.path.exists(limit_path):
                with open(limit_path, 'r') as f:
                    limit_str = f.read().strip()
                    if limit_str != "max":
                        limit = int(limit_str)
            
            if os.path.exists(usage_path):
                with open(usage_path, 'r') as f:
                    usage = int(f.read().strip())
            
            return limit, usage
        except Exception as e:
            logger.debug(f"Could not read container memory: {e}")
            return None, None
    
    def _calculate_growth_rate(self, current_rss: int) -> float:
        """Calculate memory growth rate in MB/hour."""
        if len(self.metrics_history) < 2:
            return 0.0
        
        # Use metrics from 1 hour ago (or oldest available)
        target_time = datetime.now() - timedelta(hours=1)
        reference_metrics = None
        
        for metrics in self.metrics_history:
            if metrics.timestamp <= target_time:
                reference_metrics = metrics
            else:
                break
        
        if reference_metrics is None:
            reference_metrics = self.metrics_history[0]
        
        # Calculate growth
        time_diff_hours = (datetime.now() - reference_metrics.timestamp).total_seconds() / 3600
        if time_diff_hours == 0:
            return 0.0
        
        rss_diff_mb = (current_rss - reference_metrics.rss) / (1024 * 1024)
        growth_rate = rss_diff_mb / time_diff_hours
        
        return growth_rate
    
    def check_alerts(self, metrics: MemoryMetrics) -> Optional[MemoryAlert]:
        """Check if metrics exceed alert thresholds."""
        alert = None

        # Require minimum history for leak detection (at least 10 minutes of data)
        # This prevents false positives during startup
        min_history_for_leak_detection = 10
        has_sufficient_history = len(self.metrics_history) >= min_history_for_leak_detection

        # Check for memory leak (only if we have sufficient history)
        if has_sufficient_history and metrics.growth_rate_mb_per_hour > self.leak_threshold:
            alert = MemoryAlert(
                level=AlertLevel.LEAK_DETECTED,
                message=f"Memory leak detected: growing at {metrics.growth_rate_mb_per_hour:.2f}MB/hour",
                timestamp=metrics.timestamp,
                metrics=metrics,
                threshold_exceeded=f"leak_threshold={self.leak_threshold}MB/h"
            )
        # Check critical threshold
        elif metrics.rss_percent >= self.critical_threshold:
            alert = MemoryAlert(
                level=AlertLevel.CRITICAL,
                message=f"Critical memory usage: {metrics.rss_percent:.1f}% of available memory",
                timestamp=metrics.timestamp,
                metrics=metrics,
                threshold_exceeded=f"critical_threshold={self.critical_threshold}%"
            )
        # Check warning threshold
        elif metrics.rss_percent >= self.warning_threshold:
            alert = MemoryAlert(
                level=AlertLevel.WARNING,
                message=f"High memory usage: {metrics.rss_percent:.1f}% of available memory",
                timestamp=metrics.timestamp,
                metrics=metrics,
                threshold_exceeded=f"warning_threshold={self.warning_threshold}%"
            )
        else:
            # Normal state
            if self.current_alert_level != AlertLevel.NORMAL:
                logger.info(f"Memory usage returned to normal: {metrics.rss_percent:.1f}%")
            self.current_alert_level = AlertLevel.NORMAL
            return None

        # Log alert if level changed
        if alert and alert.level != self.current_alert_level:
            logger.warning(f"Memory alert: {alert.message} ({alert.threshold_exceeded})")
            self.current_alert_level = alert.level
            self.last_alert = alert

        return alert


# Global singleton instance
_memory_monitor: Optional[MemoryMonitor] = None


def get_memory_monitor() -> MemoryMonitor:
    """Get or create the global memory monitor instance."""
    global _memory_monitor
    
    if _memory_monitor is None:
        # Read configuration from environment
        warning_threshold = float(os.getenv("EXAI_MEMORY_WARNING_THRESHOLD", "80.0"))
        critical_threshold = float(os.getenv("EXAI_MEMORY_CRITICAL_THRESHOLD", "90.0"))
        leak_threshold = float(os.getenv("EXAI_MEMORY_LEAK_THRESHOLD_MB_PER_HOUR", "100.0"))
        collection_interval = int(os.getenv("EXAI_MEMORY_COLLECTION_INTERVAL", "60"))
        history_size = int(os.getenv("EXAI_MEMORY_HISTORY_SIZE", "100"))
        
        _memory_monitor = MemoryMonitor(
            warning_threshold_percent=warning_threshold,
            critical_threshold_percent=critical_threshold,
            leak_detection_mb_per_hour=leak_threshold,
            collection_interval_seconds=collection_interval,
            history_size=history_size,
        )
    
    return _memory_monitor

