"""
Timeout Monitoring System

Monitors and analyzes timeout events across AI tools and models.
Provides intelligent timeout configuration recommendations and alerting.

Universal Design - Works with any project or AI provider.

Features:
- Real-time timeout tracking
- Statistical analysis
- Dynamic timeout recommendations
- Alerting for timeout issues
- Performance trend analysis
- Environment variable configuration
- Custom model support
- Provider-agnostic design
"""

import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from pathlib import Path

from .universal_config import get_config, get_storage_path

logger = logging.getLogger(__name__)


@dataclass
class TimeoutEvent:
    """Record of a timeout event."""
    timestamp: datetime
    tool_name: str
    model_name: str
    provider: str
    timeout_value: float
    actual_duration: float
    task_type: str
    context_size: str
    complexity: str
    success: bool
    error_message: Optional[str] = None


@dataclass
class TimeoutStats:
    """Timeout statistics for a tool/model combination."""
    tool_name: str
    model_name: str
    total_requests: int
    timeouts: int
    timeout_rate: float
    avg_duration: float
    p95_duration: float
    p99_duration: float
    recommended_timeout: float
    last_updated: datetime


class TimeoutMonitor:
    """
    Monitors and analyzes timeout events across all tools and models.

    Features:
    - Real-time timeout tracking
    - Statistical analysis
    - Dynamic timeout recommendations
    - Alerting for timeout issues
    - Performance trend analysis
    """

    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize timeout monitor.

        Args:
            storage_path: Optional path to store timeout events.
                         If not provided, uses configuration or environment variable.
        """
        # Get storage path from config or parameter
        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            try:
                self.storage_path = Path(get_storage_path("timeout_monitor"))
            except Exception:
                # Fallback to default
                self.storage_path = Path("~/.exai-prompts/data/timeout_monitor.json")

        # Ensure parent directory exists
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        self.events: List[TimeoutEvent] = []
        self.stats_cache: Dict[str, TimeoutStats] = {}

        # Load existing events
        self._load_events()

        # Load configuration
        config = get_config()
        global_config = config.get_global_config()

        # Configuration (can be overridden by environment variables)
        self.alert_threshold = global_config.alert_threshold
        self.window_size = 100  # Number of events to analyze
        self.min_samples = global_config.min_samples

    def record_timeout(self,
                      tool_name: str,
                      model_name: str,
                      provider: str,
                      timeout_value: float,
                      actual_duration: float,
                      task_type: str,
                      context_size: str = "medium",
                      complexity: str = "moderate",
                      success: bool = False,
                      error_message: Optional[str] = None) -> None:
        """
        Record a timeout event.

        Args:
            tool_name: Name of the tool
            model_name: Name of the model
            provider: Provider (kimi, glm)
            timeout_value: Configured timeout value
            actual_duration: Actual duration before timeout
            task_type: Type of task
            context_size: Size of context (small, medium, large)
            complexity: Task complexity (simple, moderate, complex)
            success: Whether operation succeeded
            error_message: Optional error message
        """
        event = TimeoutEvent(
            timestamp=datetime.now(),
            tool_name=tool_name,
            model_name=model_name,
            provider=provider,
            timeout_value=timeout_value,
            actual_duration=actual_duration,
            task_type=task_type,
            context_size=context_size,
            complexity=complexity,
            success=success,
            error_message=error_message
        )

        self.events.append(event)

        # Keep only recent events (last 1000)
        if len(self.events) > 1000:
            self.events = self.events[-1000:]

        # Save events
        self._save_events()

        # Check for alert conditions
        self._check_alerts(event)

        logger.info(
            f"Timeout event recorded: {tool_name}/{model_name} - "
            f"Timeout: {timeout_value}s, Actual: {actual_duration}s, "
            f"Success: {success}"
        )

    def get_stats(self, tool_name: str, model_name: str) -> Optional[TimeoutStats]:
        """
        Get timeout statistics for a tool/model.

        Args:
            tool_name: Name of the tool
            model_name: Name of the model

        Returns:
            TimeoutStats object or None if not enough data
        """
        key = f"{tool_name}/{model_name}"

        # Get recent events for this tool/model
        events = [
            e for e in self.events
            if e.tool_name == tool_name and e.model_name == model_name
        ][-self.window_size:]

        if len(events) < self.min_samples:
            return None

        # Calculate statistics
        total_requests = len(events)
        timeouts = sum(1 for e in events if not e.success)
        timeout_rate = timeouts / total_requests if total_requests > 0 else 0

        # Duration statistics
        durations = [e.actual_duration for e in events]
        avg_duration = sum(durations) / len(durations)
        p95_duration = self._percentile(durations, 95)
        p99_duration = self._percentile(durations, 99)

        # Recommended timeout (P99 + 20% buffer)
        recommended_timeout = p99_duration * 1.2

        stats = TimeoutStats(
            tool_name=tool_name,
            model_name=model_name,
            total_requests=total_requests,
            timeouts=timeouts,
            timeout_rate=timeout_rate,
            avg_duration=avg_duration,
            p95_duration=p95_duration,
            p99_duration=p99_duration,
            recommended_timeout=recommended_timeout,
            last_updated=datetime.now()
        )

        self.stats_cache[key] = stats
        return stats

    def get_model_recommendations(self, model_name: str) -> Dict[str, Any]:
        """
        Get timeout recommendations for a model.

        Args:
            model_name: Name of the model

        Returns:
            Dictionary with recommendations
        """
        # Get all tools using this model
        model_events = [e for e in self.events if e.model_name == model_name]
        unique_tools = list(set(e.tool_name for e in model_events))

        if not unique_tools:
            return {
                "model": model_name,
                "recommendation": "insufficient_data",
                "message": "No data available for this model"
            }

        # Get stats for each tool
        tool_stats = []
        for tool in unique_tools:
            stats = self.get_stats(tool, model_name)
            if stats:
                tool_stats.append(stats)

        if not tool_stats:
            return {
                "model": model_name,
                "recommendation": "insufficient_data",
                "message": "Not enough data for recommendations"
            }

        # Calculate aggregate statistics
        avg_timeout_rate = sum(s.timeout_rate for s in tool_stats) / len(tool_stats)
        max_p99 = max(s.p99_duration for s in tool_stats)

        # Determine recommendation
        if avg_timeout_rate > self.alert_threshold:
            recommendation = "increase_timeout"
            message = f"High timeout rate ({avg_timeout_rate*100:.1f}%) detected. Consider increasing timeout."
        elif max_p99 > 0:
            recommendation = "set_timeout"
            message = f"Recommended timeout: {max_p99 * 1.2:.1f}s (P99 + 20% buffer)"
        else:
            recommendation = "use_default"
            message = "Using default timeout configuration"

        return {
            "model": model_name,
            "recommendation": recommendation,
            "message": message,
            "stats": {
                "tools_analyzed": len(tool_stats),
                "avg_timeout_rate": avg_timeout_rate,
                "max_p99_duration": max_p99,
                "recommended_timeout": max_p99 * 1.2 if max_p99 > 0 else None
            },
            "per_tool": [
                {
                    "tool": s.tool_name,
                    "timeout_rate": s.timeout_rate,
                    "p99_duration": s.p99_duration,
                    "recommended": s.recommended_timeout
                }
                for s in tool_stats
            ]
        }

    def get_provider_recommendations(self, provider: str) -> Dict[str, Any]:
        """
        Get timeout recommendations for a provider.

        Args:
            provider: Provider name (kimi, glm)

        Returns:
            Dictionary with provider-level recommendations
        """
        provider_events = [e for e in self.events if e.provider == provider]
        unique_models = list(set(e.model_name for e in provider_events))

        recommendations = []
        for model in unique_models:
            rec = self.get_model_recommendations(model)
            recommendations.append(rec)

        return {
            "provider": provider,
            "models": recommendations,
            "summary": {
                "total_models": len(unique_models),
                "models_needing_attention": sum(
                    1 for r in recommendations
                    if r["recommendation"] in ["increase_timeout", "set_timeout"]
                )
            }
        }

    def get_trend_analysis(self, hours: int = 24) -> Dict[str, Any]:
        """
        Analyze timeout trends over time.

        Args:
            hours: Number of hours to analyze

        Returns:
            Dictionary with trend analysis
        """
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_events = [e for e in self.events if e.timestamp >= cutoff]

        if not recent_events:
            return {
                "period": f"{hours} hours",
                "message": "No events in specified period"
            }

        # Group by hour
        hourly_stats = defaultdict(lambda: {
            "total": 0,
            "timeouts": 0,
            "avg_duration": 0
        })

        for event in recent_events:
            hour_key = event.timestamp.strftime("%Y-%m-%d %H:00")
            hourly_stats[hour_key]["total"] += 1
            if not event.success:
                hourly_stats[hour_key]["timeouts"] += 1
            hourly_stats[hour_key]["avg_duration"] += event.actual_duration

        # Calculate rates
        for hour, stats in hourly_stats.items():
            if stats["total"] > 0:
                stats["timeout_rate"] = stats["timeouts"] / stats["total"]
                stats["avg_duration"] = stats["avg_duration"] / stats["total"]

        # Calculate trend
        hours_list = sorted(hourly_stats.keys())
        if len(hours_list) >= 2:
            first_rate = hourly_stats[hours_list[0]]["timeout_rate"]
            last_rate = hourly_stats[hours_list[-1]]["timeout_rate"]
            trend = "improving" if last_rate < first_rate else "degrading"
            change = (last_rate - first_rate) / first_rate * 100 if first_rate > 0 else 0
        else:
            trend = "stable"
            change = 0

        return {
            "period": f"{hours} hours",
            "total_events": len(recent_events),
            "total_timeouts": sum(1 for e in recent_events if not e.success),
            "overall_timeout_rate": sum(1 for e in recent_events if not e.success) / len(recent_events),
            "trend": trend,
            "change_percent": change,
            "hourly_breakdown": dict(hourly_stats)
        }

    def _percentile(self, data: List[float], p: int) -> float:
        """Calculate percentile."""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * p / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]

    def _check_alerts(self, event: TimeoutEvent) -> None:
        """Check if event triggers alert conditions."""
        if not event.success:
            # Check recent timeout rate for this tool/model
            recent_events = [
                e for e in self.events[-20:]  # Last 20 events
                if e.tool_name == event.tool_name and e.model_name == event.model_name
            ]
            if len(recent_events) >= 5:
                timeout_rate = sum(1 for e in recent_events if not e.success) / len(recent_events)
                if timeout_rate > self.alert_threshold:
                    logger.warning(
                        f"TIMEOUT ALERT: {event.tool_name}/{event.model_name} - "
                        f"Timeout rate exceeded threshold ({timeout_rate*100:.1f}%)"
                    )

    def _save_events(self) -> None:
        """Save events to storage."""
        try:
            data = {
                "events": [asdict(e) for e in self.events],
                "last_updated": datetime.now().isoformat()
            }
            # Convert datetime objects to ISO format strings
            for event_data in data["events"]:
                event_data["timestamp"] = event_data["timestamp"].isoformat()

            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save timeout events: {e}")

    def _load_events(self) -> None:
        """Load events from storage."""
        try:
            if self.storage_path.exists():
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)

                for event_data in data.get("events", []):
                    event_data["timestamp"] = datetime.fromisoformat(event_data["timestamp"])
                    event = TimeoutEvent(**event_data)
                    self.events.append(event)
        except Exception as e:
            logger.error(f"Failed to load timeout events: {e}")
            self.events = []

    def generate_report(self) -> str:
        """
        Generate comprehensive timeout monitoring report.

        Returns:
            Formatted report
        """
        report = []
        report.append("="*70)
        report.append("TIMEOUT MONITORING REPORT")
        report.append("="*70)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        # Overview
        total_events = len(self.events)
        total_timeouts = sum(1 for e in self.events if not e.success)
        overall_rate = (total_timeouts / total_events * 100) if total_events > 0 else 0

        report.append("OVERVIEW")
        report.append("-"*70)
        report.append(f"Total Events: {total_events}")
        report.append(f"Total Timeouts: {total_timeouts}")
        report.append(f"Overall Timeout Rate: {overall_rate:.2f}%")
        report.append("")

        # Trend analysis
        trend = self.get_trend_analysis(24)
        report.append("24-HOUR TREND")
        report.append("-"*70)
        report.append(f"Trend: {trend.get('trend', 'N/A')}")
        report.append(f"Change: {trend.get('change_percent', 0):.2f}%")
        report.append(f"Events in period: {trend.get('total_events', 0)}")
        report.append("")

        # Provider recommendations
        for provider in ["kimi", "glm"]:
            provider_rec = self.get_provider_recommendations(provider)
            if provider_rec["models"]:
                report.append(f"{provider.upper()} PROVIDER RECOMMENDATIONS")
                report.append("-"*70)
                for model_rec in provider_rec["models"]:
                    report.append(f"\nModel: {model_rec['model']}")
                    report.append(f"  Recommendation: {model_rec['recommendation']}")
                    report.append(f"  Message: {model_rec['message']}")
                    if "stats" in model_rec:
                        stats = model_rec["stats"]
                        report.append(f"  Tools analyzed: {stats.get('tools_analyzed', 0)}")
                        if stats.get('recommended_timeout'):
                            report.append(f"  Recommended timeout: {stats['recommended_timeout']:.1f}s")
                report.append("")

        # Detailed tool stats
        report.append("TOOL-SPECIFIC STATISTICS")
        report.append("-"*70)

        unique_combinations = set((e.tool_name, e.model_name) for e in self.events)
        for tool, model in sorted(unique_combinations):
            stats = self.get_stats(tool, model)
            if stats:
                report.append(f"\n{tool} / {model}")
                report.append(f"  Requests: {stats.total_requests}")
                report.append(f"  Timeouts: {stats.timeouts}")
                report.append(f"  Timeout rate: {stats.timeout_rate*100:.2f}%")
                report.append(f"  Avg duration: {stats.avg_duration:.2f}s")
                report.append(f"  P95 duration: {stats.p95_duration:.2f}s")
                report.append(f"  P99 duration: {stats.p99_duration:.2f}s")
                report.append(f"  Recommended timeout: {stats.recommended_timeout:.2f}s")

        return "\n".join(report)


# Global timeout monitor instance
_timeout_monitor: Optional[TimeoutMonitor] = None


def get_timeout_monitor() -> TimeoutMonitor:
    """Get or create global timeout monitor instance."""
    global _timeout_monitor
    if _timeout_monitor is None:
        _timeout_monitor = TimeoutMonitor()
    return _timeout_monitor


# Decorator for automatic timeout monitoring
def monitor_timeout(tool_name: str, model_param: str = "model"):
    """
    Decorator to automatically monitor timeouts for tool functions.

    Args:
        tool_name: Name of the tool
        model_param: Name of the parameter containing model name
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Extract parameters
            model_name = kwargs.get(model_param, "unknown")
            provider = "kimi" if "kimi" in model_name else "glm"

            # Get timeout monitor
            monitor = get_timeout_monitor()

            # Record start
            start_time = time.time()
            timeout_value = kwargs.get("timeout", 30.0)  # Default timeout

            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time

                # Record success
                monitor.record_timeout(
                    tool_name=tool_name,
                    model_name=model_name,
                    provider=provider,
                    timeout_value=timeout_value,
                    actual_duration=duration,
                    task_type="unknown",
                    success=True
                )

                return result
            except Exception as e:
                duration = time.time() - start_time

                # Record timeout/failure
                monitor.record_timeout(
                    tool_name=tool_name,
                    model_name=model_name,
                    provider=provider,
                    timeout_value=timeout_value,
                    actual_duration=duration,
                    task_type="unknown",
                    success=False,
                    error_message=str(e)
                )

                raise

        return wrapper
    return decorator


if __name__ == "__main__":
    # Generate report
    monitor = get_timeout_monitor()
    report = monitor.generate_report()
    print(report)

    # Save report
    Path("docs/reports/timeout_monitoring_report.md").write_text(report)
    print("\nReport saved to docs/reports/timeout_monitoring_report.md")
