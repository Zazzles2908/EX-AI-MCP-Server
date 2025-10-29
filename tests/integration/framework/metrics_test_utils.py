"""
Metrics Test Utilities for WebSocket Metrics Validation.

Provides helpers for collecting, asserting, and validating metrics during tests.

Created: 2025-10-28
Phase: 2.4 Week 1.5 - Integration Tests
EXAI Consultation: b5ba9ff3-a1b2-4dab-af19-c3cc4ce1d8aa
"""

import logging
import time
from typing import Optional, Any, Dict, List
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class MetricsSnapshot:
    """Snapshot of metrics at a point in time."""
    
    timestamp: float
    metrics: Dict[str, Any]
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get metric value by key (supports nested keys with dot notation)."""
        keys = key.split('.')
        value = self.metrics
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def compare_to(self, other: 'MetricsSnapshot') -> Dict[str, Any]:
        """Compare this snapshot to another and return differences."""
        differences = {}
        
        def compare_dicts(d1: dict, d2: dict, prefix: str = ""):
            for key in set(list(d1.keys()) + list(d2.keys())):
                full_key = f"{prefix}.{key}" if prefix else key
                
                if key not in d1:
                    differences[full_key] = {"added": d2[key]}
                elif key not in d2:
                    differences[full_key] = {"removed": d1[key]}
                elif isinstance(d1[key], dict) and isinstance(d2[key], dict):
                    compare_dicts(d1[key], d2[key], full_key)
                elif d1[key] != d2[key]:
                    differences[full_key] = {
                        "before": d1[key],
                        "after": d2[key],
                        "delta": d2[key] - d1[key] if isinstance(d1[key], (int, float)) else None
                    }
        
        compare_dicts(self.metrics, other.metrics)
        return differences


@dataclass
class MetricsCollector:
    """
    Collects and validates metrics during tests.
    
    Provides utilities for:
    - Taking metric snapshots
    - Comparing snapshots
    - Asserting metric values
    - Tracking metric changes over time
    """
    
    metrics_source: Any
    snapshots: List[MetricsSnapshot] = field(default_factory=list)
    
    def take_snapshot(self, label: Optional[str] = None) -> MetricsSnapshot:
        """
        Take a snapshot of current metrics.
        
        Args:
            label: Optional label for this snapshot
        
        Returns:
            MetricsSnapshot instance
        """
        if hasattr(self.metrics_source, 'to_dict'):
            metrics_dict = self.metrics_source.to_dict()
        elif hasattr(self.metrics_source, 'get_stats'):
            metrics_dict = self.metrics_source.get_stats()
        elif isinstance(self.metrics_source, dict):
            metrics_dict = self.metrics_source.copy()
        else:
            raise ValueError(f"Unsupported metrics source type: {type(self.metrics_source)}")
        
        snapshot = MetricsSnapshot(
            timestamp=time.time(),
            metrics=metrics_dict
        )
        
        self.snapshots.append(snapshot)
        
        if label:
            logger.debug(f"Took metrics snapshot: {label}")
        
        return snapshot
    
    def get_latest_snapshot(self) -> Optional[MetricsSnapshot]:
        """Get the most recent snapshot."""
        return self.snapshots[-1] if self.snapshots else None
    
    def get_snapshot_at_index(self, index: int) -> Optional[MetricsSnapshot]:
        """Get snapshot at specific index."""
        if 0 <= index < len(self.snapshots):
            return self.snapshots[index]
        return None
    
    def compare_snapshots(
        self,
        before_index: int = 0,
        after_index: int = -1
    ) -> Dict[str, Any]:
        """
        Compare two snapshots and return differences.
        
        Args:
            before_index: Index of "before" snapshot
            after_index: Index of "after" snapshot
        
        Returns:
            Dictionary of differences
        """
        before = self.get_snapshot_at_index(before_index)
        after = self.get_snapshot_at_index(after_index)
        
        if not before or not after:
            raise ValueError("Invalid snapshot indices")
        
        return before.compare_to(after)
    
    def assert_metric_increased(
        self,
        metric_key: str,
        min_increase: Optional[int] = None,
        before_index: int = 0,
        after_index: int = -1
    ) -> bool:
        """
        Assert that a metric increased between snapshots.
        
        Args:
            metric_key: Metric key (supports dot notation)
            min_increase: Minimum expected increase
            before_index: Index of "before" snapshot
            after_index: Index of "after" snapshot
        
        Returns:
            True if assertion passed
        
        Raises:
            AssertionError if metric did not increase
        """
        before = self.get_snapshot_at_index(before_index)
        after = self.get_snapshot_at_index(after_index)
        
        before_value = before.get(metric_key, 0)
        after_value = after.get(metric_key, 0)
        
        increase = after_value - before_value
        
        if min_increase is not None:
            assert increase >= min_increase, (
                f"Metric '{metric_key}' increased by {increase}, "
                f"expected at least {min_increase}"
            )
        else:
            assert increase > 0, (
                f"Metric '{metric_key}' did not increase "
                f"(before={before_value}, after={after_value})"
            )
        
        logger.debug(f"Metric '{metric_key}' increased by {increase}")
        return True
    
    def assert_metric_equals(
        self,
        metric_key: str,
        expected_value: Any,
        snapshot_index: int = -1
    ) -> bool:
        """
        Assert that a metric equals expected value.
        
        Args:
            metric_key: Metric key (supports dot notation)
            expected_value: Expected value
            snapshot_index: Snapshot index to check
        
        Returns:
            True if assertion passed
        
        Raises:
            AssertionError if metric does not equal expected value
        """
        snapshot = self.get_snapshot_at_index(snapshot_index)
        actual_value = snapshot.get(metric_key)
        
        assert actual_value == expected_value, (
            f"Metric '{metric_key}' = {actual_value}, expected {expected_value}"
        )
        
        logger.debug(f"Metric '{metric_key}' equals {expected_value}")
        return True
    
    def clear_snapshots(self) -> None:
        """Clear all snapshots."""
        self.snapshots.clear()
        logger.debug("Cleared all metric snapshots")


def assert_metrics_recorded(
    metrics: Any,
    expected_metrics: Dict[str, Any],
    tolerance: float = 0.0
) -> bool:
    """
    Assert that expected metrics were recorded.
    
    Args:
        metrics: Metrics source (WebSocketMetrics instance or dict)
        expected_metrics: Dictionary of expected metric values
        tolerance: Acceptable deviation for numeric values (0.0-1.0)
    
    Returns:
        True if all assertions passed
    
    Raises:
        AssertionError if any metric doesn't match
    
    Example:
        >>> assert_metrics_recorded(metrics, {
        ...     "connections.total": 10,
        ...     "messages.sent": 100
        ... })
    """
    collector = MetricsCollector(metrics)
    snapshot = collector.take_snapshot()
    
    for key, expected_value in expected_metrics.items():
        actual_value = snapshot.get(key)
        
        if isinstance(expected_value, (int, float)) and tolerance > 0:
            # Allow tolerance for numeric values
            deviation = abs(actual_value - expected_value) / expected_value if expected_value != 0 else 0
            assert deviation <= tolerance, (
                f"Metric '{key}' = {actual_value}, expected {expected_value} "
                f"(deviation: {deviation:.2%}, tolerance: {tolerance:.2%})"
            )
        else:
            assert actual_value == expected_value, (
                f"Metric '{key}' = {actual_value}, expected {expected_value}"
            )
    
    logger.info(f"All {len(expected_metrics)} metrics matched expected values")
    return True


def assert_metric_value(
    metrics: Any,
    metric_key: str,
    expected_value: Any,
    tolerance: float = 0.0
) -> bool:
    """
    Assert that a single metric has expected value.
    
    Args:
        metrics: Metrics source
        metric_key: Metric key (supports dot notation)
        expected_value: Expected value
        tolerance: Acceptable deviation for numeric values
    
    Returns:
        True if assertion passed
    
    Example:
        >>> assert_metric_value(metrics, "connections.active", 5)
    """
    return assert_metrics_recorded(metrics, {metric_key: expected_value}, tolerance)


def get_metric_snapshot(metrics: Any) -> MetricsSnapshot:
    """
    Get a snapshot of current metrics.
    
    Args:
        metrics: Metrics source
    
    Returns:
        MetricsSnapshot instance
    
    Example:
        >>> snapshot = get_metric_snapshot(metrics)
        >>> print(snapshot.get("connections.total"))
    """
    collector = MetricsCollector(metrics)
    return collector.take_snapshot()

