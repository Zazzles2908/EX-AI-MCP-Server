"""
Performance Monitor - Monitor CPU, memory, and response times

Tracks:
- CPU usage
- Memory usage
- Response times
- Resource alerts

Created: 2025-10-05
"""

import logging
import os
import psutil
import time
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """
    Monitor performance metrics during test execution.
    
    Tracks:
    - CPU usage
    - Memory usage
    - Response times
    - Resource alerts
    """
    
    def __init__(self):
        """Initialize the performance monitor."""
        self.monitor_memory = os.getenv("MONITOR_MEMORY", "true").lower() == "true"
        self.monitor_cpu = os.getenv("MONITOR_CPU", "true").lower() == "true"
        
        self.memory_alert_mb = int(os.getenv("MEMORY_ALERT_MB", "500"))
        self.cpu_alert_percent = int(os.getenv("CPU_ALERT_PERCENT", "80"))
        
        self.process = psutil.Process(os.getpid())
        
        # Metrics storage
        self.metrics = {}
        
        logger.info("Performance monitor initialized")
    
    def start_monitoring(self, test_id: str) -> Dict[str, Any]:
        """
        Start monitoring for a test.
        
        Args:
            test_id: Test identifier
        
        Returns:
            Initial metrics
        """
        initial_metrics = {
            "test_id": test_id,
            "start_time": time.time(),
            "start_memory_mb": self._get_memory_mb() if self.monitor_memory else 0,
            "start_cpu_percent": self._get_cpu_percent() if self.monitor_cpu else 0
        }
        
        self.metrics[test_id] = initial_metrics
        
        return initial_metrics
    
    def stop_monitoring(self, test_id: str) -> Dict[str, Any]:
        """
        Stop monitoring for a test.
        
        Args:
            test_id: Test identifier
        
        Returns:
            Final metrics with duration and resource usage
        """
        if test_id not in self.metrics:
            logger.warning(f"Test {test_id} not found in metrics")
            return {}
        
        initial = self.metrics[test_id]
        
        # Calculate final metrics
        end_time = time.time()
        duration_secs = end_time - initial["start_time"]
        
        final_metrics = {
            **initial,
            "end_time": end_time,
            "duration_secs": duration_secs,
            "end_memory_mb": self._get_memory_mb() if self.monitor_memory else 0,
            "end_cpu_percent": self._get_cpu_percent() if self.monitor_cpu else 0
        }
        
        # Calculate deltas
        if self.monitor_memory:
            final_metrics["memory_delta_mb"] = final_metrics["end_memory_mb"] - final_metrics["start_memory_mb"]
        
        # Check alerts
        alerts = []
        
        if self.monitor_memory and final_metrics["end_memory_mb"] > self.memory_alert_mb:
            alerts.append(f"Memory usage ({final_metrics['end_memory_mb']:.1f} MB) exceeds alert threshold ({self.memory_alert_mb} MB)")
        
        if self.monitor_cpu and final_metrics["end_cpu_percent"] > self.cpu_alert_percent:
            alerts.append(f"CPU usage ({final_metrics['end_cpu_percent']:.1f}%) exceeds alert threshold ({self.cpu_alert_percent}%)")
        
        final_metrics["alerts"] = alerts
        
        # Update stored metrics
        self.metrics[test_id] = final_metrics
        
        return final_metrics
    
    def get_metrics(self, test_id: str) -> Optional[Dict[str, Any]]:
        """Get metrics for a test."""
        return self.metrics.get(test_id)
    
    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get all metrics."""
        return self.metrics
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics."""
        if not self.metrics:
            return {
                "total_tests": 0,
                "avg_duration_secs": 0,
                "avg_memory_mb": 0,
                "avg_cpu_percent": 0,
                "total_alerts": 0
            }
        
        durations = [m.get("duration_secs", 0) for m in self.metrics.values() if "duration_secs" in m]
        memories = [m.get("end_memory_mb", 0) for m in self.metrics.values() if "end_memory_mb" in m]
        cpus = [m.get("end_cpu_percent", 0) for m in self.metrics.values() if "end_cpu_percent" in m]
        alerts = [a for m in self.metrics.values() for a in m.get("alerts", [])]
        
        return {
            "total_tests": len(self.metrics),
            "avg_duration_secs": sum(durations) / len(durations) if durations else 0,
            "max_duration_secs": max(durations) if durations else 0,
            "min_duration_secs": min(durations) if durations else 0,
            "avg_memory_mb": sum(memories) / len(memories) if memories else 0,
            "max_memory_mb": max(memories) if memories else 0,
            "avg_cpu_percent": sum(cpus) / len(cpus) if cpus else 0,
            "max_cpu_percent": max(cpus) if cpus else 0,
            "total_alerts": len(alerts),
            "alerts": alerts
        }
    
    def _get_memory_mb(self) -> float:
        """Get current memory usage in MB."""
        try:
            return self.process.memory_info().rss / 1024 / 1024
        except Exception as e:
            logger.error(f"Failed to get memory usage: {e}")
            return 0.0
    
    def _get_cpu_percent(self) -> float:
        """Get current CPU usage percentage."""
        try:
            return self.process.cpu_percent(interval=0.1)
        except Exception as e:
            logger.error(f"Failed to get CPU usage: {e}")
            return 0.0


# Example usage
if __name__ == "__main__":
    monitor = PerformanceMonitor()
    
    # Start monitoring
    test_id = "test_chat_basic"
    monitor.start_monitoring(test_id)
    
    # Simulate work
    time.sleep(2)
    
    # Stop monitoring
    metrics = monitor.stop_monitoring(test_id)
    
    print(f"Duration: {metrics['duration_secs']:.2f}s")
    print(f"Memory: {metrics.get('end_memory_mb', 0):.1f} MB")
    print(f"CPU: {metrics.get('end_cpu_percent', 0):.1f}%")
    print(f"Alerts: {metrics.get('alerts', [])}")
    
    # Get summary
    summary = monitor.get_summary()
    print(f"\nSummary: {summary}")

