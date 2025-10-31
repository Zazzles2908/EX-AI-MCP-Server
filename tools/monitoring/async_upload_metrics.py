"""
Async Upload Metrics Collection

Tracks performance metrics for async vs sync file uploads.
Supports integration with monitoring systems (Prometheus, CloudWatch, etc.)

Metrics Tracked:
- execution_type: "sync", "async", or "sync_fallback"
- success: True/False
- duration_ms: Execution time in milliseconds
- error_type: Exception type if failed
- fallback_used: Whether fallback to sync was used
- file_size_mb: Size of uploaded file
- provider: Upload provider (kimi, glm)
"""

import time
import logging
import json
from dataclasses import dataclass, asdict, field
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class UploadMetrics:
    """Metrics for a single upload operation"""
    
    execution_type: str  # "sync", "async", or "sync_fallback"
    success: bool
    duration_ms: float
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    error_type: Optional[str] = None
    fallback_used: bool = False
    file_size_mb: float = 0.0
    provider: str = "unknown"
    request_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict())


class MetricsCollector:
    """Collects and aggregates upload metrics"""
    
    def __init__(self, log_file: Optional[str] = None):
        """
        Initialize metrics collector
        
        Args:
            log_file: Optional file path to write metrics to
        """
        self.metrics: List[UploadMetrics] = []
        self.log_file = log_file
        
        if log_file:
            # Create log file if it doesn't exist
            Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    
    def record_upload(self, metrics: UploadMetrics):
        """Record an upload operation"""
        self.metrics.append(metrics)
        
        # Log to file if configured
        if self.log_file:
            self._write_to_file(metrics)
        
        # Log to logger
        logger.info(
            f"Upload: type={metrics.execution_type}, "
            f"success={metrics.success}, "
            f"duration={metrics.duration_ms:.2f}ms, "
            f"size={metrics.file_size_mb:.2f}MB, "
            f"provider={metrics.provider}"
        )
    
    def _write_to_file(self, metrics: UploadMetrics):
        """Write metrics to log file"""
        try:
            with open(self.log_file, 'a') as f:
                f.write(metrics.to_json() + '\n')
        except Exception as e:
            logger.error(f"Failed to write metrics to file: {e}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics"""
        if not self.metrics:
            return {
                "total_uploads": 0,
                "successful": 0,
                "failed": 0,
                "success_rate": 0.0,
                "avg_duration_ms": 0.0,
                "by_type": {}
            }
        
        total = len(self.metrics)
        successful = sum(1 for m in self.metrics if m.success)
        failed = total - successful
        
        # Group by execution type
        by_type = {}
        for metric in self.metrics:
            if metric.execution_type not in by_type:
                by_type[metric.execution_type] = {
                    "count": 0,
                    "successful": 0,
                    "failed": 0,
                    "avg_duration_ms": 0.0,
                    "total_duration_ms": 0.0
                }
            
            by_type[metric.execution_type]["count"] += 1
            if metric.success:
                by_type[metric.execution_type]["successful"] += 1
            else:
                by_type[metric.execution_type]["failed"] += 1
            by_type[metric.execution_type]["total_duration_ms"] += metric.duration_ms
        
        # Calculate averages
        for type_stats in by_type.values():
            if type_stats["count"] > 0:
                type_stats["avg_duration_ms"] = type_stats["total_duration_ms"] / type_stats["count"]
        
        avg_duration = sum(m.duration_ms for m in self.metrics) / total if total > 0 else 0
        
        return {
            "total_uploads": total,
            "successful": successful,
            "failed": failed,
            "success_rate": (successful / total * 100) if total > 0 else 0.0,
            "avg_duration_ms": avg_duration,
            "by_type": by_type
        }
    
    def get_async_vs_sync_comparison(self) -> Dict[str, Any]:
        """Compare async vs sync performance"""
        async_metrics = [m for m in self.metrics if m.execution_type == "async"]
        sync_metrics = [m for m in self.metrics if m.execution_type == "sync"]
        
        def calc_stats(metrics_list):
            if not metrics_list:
                return None
            
            successful = sum(1 for m in metrics_list if m.success)
            avg_duration = sum(m.duration_ms for m in metrics_list) / len(metrics_list)
            
            return {
                "count": len(metrics_list),
                "successful": successful,
                "success_rate": (successful / len(metrics_list) * 100),
                "avg_duration_ms": avg_duration,
                "min_duration_ms": min(m.duration_ms for m in metrics_list),
                "max_duration_ms": max(m.duration_ms for m in metrics_list)
            }
        
        async_stats = calc_stats(async_metrics)
        sync_stats = calc_stats(sync_metrics)
        
        improvement = None
        if async_stats and sync_stats and sync_stats["avg_duration_ms"] > 0:
            improvement = {
                "latency_improvement_percent": (
                    (sync_stats["avg_duration_ms"] - async_stats["avg_duration_ms"]) / 
                    sync_stats["avg_duration_ms"] * 100
                ),
                "success_rate_improvement_percent": (
                    async_stats["success_rate"] - sync_stats["success_rate"]
                )
            }
        
        return {
            "async": async_stats,
            "sync": sync_stats,
            "improvement": improvement
        }
    
    def clear(self):
        """Clear all metrics (useful for testing)"""
        self.metrics.clear()


# Global metrics collector instance
_collector: Optional[MetricsCollector] = None


def get_metrics_collector(log_file: Optional[str] = None) -> MetricsCollector:
    """Get or create global metrics collector"""
    global _collector
    if _collector is None:
        _collector = MetricsCollector(log_file=log_file)
    return _collector


def reset_metrics():
    """Reset global metrics collector (useful for testing)"""
    global _collector
    _collector = None

