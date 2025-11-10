"""
Tool Performance Metrics

Comprehensive performance tracking and analytics for AI tools.
Provides insights into usage patterns, performance trends, and optimization opportunities.

Universal Design - Works with any project or AI provider.

Features:
- Real-time metric collection
- Performance aggregation
- Trend analysis
- Optimization recommendations
- Cost tracking
- Quality assessment
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
import statistics

from .universal_config import get_config, get_storage_path

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """Individual performance metric."""
    timestamp: datetime
    tool_name: str
    model_name: str
    provider: str
    duration: float
    token_count: int
    cost: float
    success: bool
    quality_score: Optional[float] = None
    user_satisfaction: Optional[float] = None


@dataclass
class ToolMetrics:
    """Aggregated metrics for a tool."""
    tool_name: str
    total_requests: int
    successful_requests: int
    success_rate: float
    avg_duration: float
    p95_duration: float
    p99_duration: float
    avg_tokens: float
    total_cost: float
    avg_cost: float
    throughput_per_hour: float
    error_rate: float
    last_updated: datetime


@dataclass
class ModelMetrics:
    """Aggregated metrics for a model."""
    model_name: str
    provider: str
    total_requests: int
    total_cost: float
    avg_duration: float
    avg_tokens: float
    cost_efficiency: float  # tokens per dollar
    performance_score: float  # composite score
    error_rate: float
    last_updated: datetime


class PerformanceMetricsCollector:
    """
    Collects and analyzes performance metrics across all EXAI tools.

    Features:
    - Real-time metric collection
    - Performance aggregation
    - Trend analysis
    - Optimization recommendations
    - Cost tracking
    - Quality assessment
    """

    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize performance metrics collector.

        Args:
            storage_path: Optional path to store metrics.
                         If not provided, uses configuration or environment variable.
        """
        # Get storage path from config or parameter
        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            try:
                self.storage_path = Path(get_storage_path("performance_metrics"))
            except Exception:
                # Fallback to default
                self.storage_path = Path("~/.exai-prompts/data/performance_metrics.json")

        # Ensure parent directory exists
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        self.metrics: List[PerformanceMetric] = []
        self.tool_cache: Dict[str, ToolMetrics] = {}
        self.model_cache: Dict[str, ModelMetrics] = {}

        # Load existing metrics
        self._load_metrics()

        # Load configuration
        config = get_config()
        global_config = config.get_global_config()

        # Configuration (can be overridden by environment variables)
        self.aggregation_window = 100  # Number of metrics to aggregate
        self.quality_threshold = global_config.quality_threshold
        self.cost_alert_threshold = global_config.cost_alert_threshold

    def record_metric(self,
                     tool_name: str,
                     model_name: str,
                     provider: str,
                     duration: float,
                     token_count: int,
                     cost: float,
                     success: bool,
                     quality_score: Optional[float] = None,
                     user_satisfaction: Optional[float] = None) -> None:
        """
        Record a performance metric.

        Args:
            tool_name: Name of the tool
            model_name: Name of the model
            provider: Provider (kimi, glm)
            duration: Request duration in seconds
            token_count: Number of tokens processed
            cost: Cost in USD
            success: Whether request succeeded
            quality_score: Quality score (0-1)
            user_satisfaction: User satisfaction score (0-1)
        """
        metric = PerformanceMetric(
            timestamp=datetime.now(),
            tool_name=tool_name,
            model_name=model_name,
            provider=provider,
            duration=duration,
            token_count=token_count,
            cost=cost,
            success=success,
            quality_score=quality_score,
            user_satisfaction=user_satisfaction
        )

        self.metrics.append(metric)

        # Keep only recent metrics (last 10,000)
        if len(self.metrics) > 10000:
            self.metrics = self.metrics[-10000:]

        # Save metrics
        self._save_metrics()

        logger.debug(
            f"Metric recorded: {tool_name}/{model_name} - "
            f"Duration: {duration:.2f}s, Tokens: {token_count}, Cost: ${cost:.4f}"
        )

    def get_tool_metrics(self, tool_name: str) -> Optional[ToolMetrics]:
        """
        Get aggregated metrics for a tool.

        Args:
            tool_name: Name of the tool

        Returns:
            ToolMetrics object or None if not enough data
        """
        # Get recent metrics for this tool
        tool_metrics = [
            m for m in self.metrics
            if m.tool_name == tool_name
        ][-self.aggregation_window:]

        if len(tool_metrics) < 10:  # Minimum samples
            return None

        # Calculate statistics
        total_requests = len(tool_metrics)
        successful_requests = sum(1 for m in tool_metrics if m.success)
        success_rate = successful_requests / total_requests

        # Duration statistics
        durations = [m.duration for m in tool_metrics]
        avg_duration = statistics.mean(durations)
        p95_duration = statistics.quantiles(durations, n=20)[18]  # 95th percentile
        p99_duration = statistics.quantiles(durations, n=100)[98]  # 99th percentile

        # Token statistics
        tokens = [m.token_count for m in tool_metrics]
        avg_tokens = statistics.mean(tokens)

        # Cost statistics
        costs = [m.cost for m in tool_metrics]
        total_cost = sum(costs)
        avg_cost = statistics.mean(costs)

        # Throughput (requests per hour)
        time_span = (tool_metrics[-1].timestamp - tool_metrics[0].timestamp).total_seconds()
        throughput_per_hour = (total_requests / time_span * 3600) if time_span > 0 else 0

        # Error rate
        error_rate = 1 - success_rate

        tool_metrics_obj = ToolMetrics(
            tool_name=tool_name,
            total_requests=total_requests,
            successful_requests=successful_requests,
            success_rate=success_rate,
            avg_duration=avg_duration,
            p95_duration=p95_duration,
            p99_duration=p99_duration,
            avg_tokens=avg_tokens,
            total_cost=total_cost,
            avg_cost=avg_cost,
            throughput_per_hour=throughput_per_hour,
            error_rate=error_rate,
            last_updated=datetime.now()
        )

        self.tool_cache[tool_name] = tool_metrics_obj
        return tool_metrics_obj

    def get_model_metrics(self, model_name: str) -> Optional[ModelMetrics]:
        """
        Get aggregated metrics for a model.

        Args:
            model_name: Name of the model

        Returns:
            ModelMetrics object or None if not enough data
        """
        # Get recent metrics for this model
        model_metrics = [
            m for m in self.metrics
            if m.model_name == model_name
        ][-self.aggregation_window:]

        if len(model_metrics) < 10:
            return None

        # Calculate statistics
        total_requests = len(model_metrics)
        total_cost = sum(m.cost for m in model_metrics)

        # Duration statistics
        durations = [m.duration for m in model_metrics]
        avg_duration = statistics.mean(durations)

        # Token statistics
        tokens = [m.token_count for m in model_metrics]
        total_tokens = sum(tokens)
        avg_tokens = statistics.mean(tokens)

        # Cost efficiency (tokens per dollar)
        cost_efficiency = total_tokens / total_cost if total_cost > 0 else 0

        # Performance score (composite of speed, success rate, and cost efficiency)
        success_rate = sum(1 for m in model_metrics if m.success) / total_requests
        avg_speed_score = 1 / avg_duration if avg_duration > 0 else 0
        performance_score = (success_rate * 0.4) + (avg_speed_score * 0.3) + (cost_efficiency * 0.3)

        # Error rate
        error_rate = 1 - success_rate

        # Get provider
        provider = model_metrics[0].provider if model_metrics else "unknown"

        model_metrics_obj = ModelMetrics(
            model_name=model_name,
            provider=provider,
            total_requests=total_requests,
            total_cost=total_cost,
            avg_duration=avg_duration,
            avg_tokens=avg_tokens,
            cost_efficiency=cost_efficiency,
            performance_score=performance_score,
            error_rate=error_rate,
            last_updated=datetime.now()
        )

        self.model_cache[model_name] = model_metrics_obj
        return model_metrics_obj

    def get_provider_metrics(self, provider: str) -> Dict[str, Any]:
        """
        Get aggregated metrics for a provider.

        Args:
            provider: Provider name (kimi, glm)

        Returns:
            Dictionary with provider-level metrics
        """
        provider_metrics = [m for m in self.metrics if m.provider == provider]

        if not provider_metrics:
            return {"message": "No metrics available for this provider"}

        total_requests = len(provider_metrics)
        total_cost = sum(m.cost for m in provider_metrics)
        success_rate = sum(1 for m in provider_metrics if m.success) / total_requests

        # Model breakdown
        model_breakdown = {}
        unique_models = set(m.model_name for m in provider_metrics)
        for model in unique_models:
            model_metrics = self.get_model_metrics(model)
            if model_metrics:
                model_breakdown[model] = {
                    "requests": model_metrics.total_requests,
                    "avg_duration": model_metrics.avg_duration,
                    "cost_efficiency": model_metrics.cost_efficiency,
                    "performance_score": model_metrics.performance_score
                }

        return {
            "provider": provider,
            "total_requests": total_requests,
            "total_cost": total_cost,
            "success_rate": success_rate,
            "avg_cost": total_cost / total_requests,
            "models": model_breakdown
        }

    def get_performance_leaderboard(self, metric: str = "performance_score") -> List[Dict[str, Any]]:
        """
        Get performance leaderboard for models.

        Args:
            metric: Metric to rank by (performance_score, cost_efficiency, success_rate, etc.)

        Returns:
            List of models ranked by metric
        """
        leaderboard = []

        unique_models = set(m.model_name for m in self.metrics)
        for model in unique_models:
            model_metrics = self.get_model_metrics(model)
            if model_metrics:
                leaderboard.append({
                    "model": model,
                    "provider": model_metrics.provider,
                    "requests": model_metrics.total_requests,
                    "avg_duration": model_metrics.avg_duration,
                    "cost_efficiency": model_metrics.cost_efficiency,
                    "performance_score": model_metrics.performance_score,
                    "error_rate": model_metrics.error_rate
                })

        # Sort by metric
        if metric in ["cost_efficiency", "performance_score"]:
            leaderboard.sort(key=lambda x: x[metric], reverse=True)
        else:
            leaderboard.sort(key=lambda x: x[metric])

        return leaderboard

    def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """
        Generate optimization recommendations based on metrics.

        Returns:
            List of optimization recommendations
        """
        recommendations = []

        # Analyze each tool
        unique_tools = set(m.tool_name for m in self.metrics)
        for tool in unique_tools:
            tool_metrics = self.get_tool_metrics(tool)
            if not tool_metrics:
                continue

            # Check success rate
            if tool_metrics.success_rate < 0.9:
                recommendations.append({
                    "type": "success_rate",
                    "severity": "high",
                    "tool": tool,
                    "message": f"Success rate is {tool_metrics.success_rate*100:.1f}% (target: >90%)",
                    "action": "Review error logs and improve error handling"
                })

            # Check duration
            if tool_metrics.avg_duration > 30:
                recommendations.append({
                    "type": "performance",
                    "severity": "medium",
                    "tool": tool,
                    "message": f"Average duration is {tool_metrics.avg_duration:.1f}s (target: <30s)",
                    "action": "Consider optimizing prompts or using faster models"
                })

            # Check cost
            if tool_metrics.avg_cost > 0.5:
                recommendations.append({
                    "type": "cost",
                    "severity": "medium",
                    "tool": tool,
                    "message": f"Average cost is ${tool_metrics.avg_cost:.2f} (target: <$0.50)",
                    "action": "Optimize token usage or switch to more cost-efficient models"
                })

        # Analyze models
        unique_models = set(m.model_name for m in self.metrics)
        for model in unique_models:
            model_metrics = self.get_model_metrics(model)
            if not model_metrics:
                continue

            # Check cost efficiency
            if model_metrics.cost_efficiency < 1000:
                recommendations.append({
                    "type": "cost_efficiency",
                    "severity": "low",
                    "model": model,
                    "message": f"Cost efficiency is {model_metrics.cost_efficiency:.0f} tokens/$ (low)",
                    "action": "Consider using more cost-efficient models for this workload"
                })

        return recommendations

    def get_trend_analysis(self, metric_name: str, hours: int = 24) -> Dict[str, Any]:
        """
        Analyze trends for a specific metric.

        Args:
            metric_name: Name of the metric to analyze
            hours: Number of hours to analyze

        Returns:
            Dictionary with trend analysis
        """
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_metrics = [m for m in self.metrics if m.timestamp >= cutoff]

        if not recent_metrics:
            return {
                "period": f"{hours} hours",
                "message": "No data in specified period"
            }

        # Group by hour
        hourly_data = defaultdict(list)
        for metric in recent_metrics:
            hour_key = metric.timestamp.strftime("%Y-%m-%d %H:00")
            hourly_data[hour_key].append(metric)

        # Calculate hourly aggregates
        hourly_stats = []
        for hour, metrics in sorted(hourly_data.items()):
            if metric_name == "duration":
                values = [m.duration for m in metrics]
            elif metric_name == "cost":
                values = [m.cost for m in metrics]
            elif metric_name == "tokens":
                values = [m.token_count for m in metrics]
            else:
                values = [getattr(m, metric_name, 0) for m in metrics if hasattr(m, metric_name)]

            if values:
                hourly_stats.append({
                    "hour": hour,
                    "count": len(values),
                    "avg": statistics.mean(values),
                    "min": min(values),
                    "max": max(values)
                })

        # Calculate trend
        if len(hourly_stats) >= 2:
            first_avg = hourly_stats[0]["avg"]
            last_avg = hourly_stats[-1]["avg"]
            change = (last_avg - first_avg) / first_avg * 100 if first_avg > 0 else 0
            trend = "improving" if change < 0 else "degrading" if change > 0 else "stable"
        else:
            trend = "insufficient_data"
            change = 0

        return {
            "metric": metric_name,
            "period": f"{hours} hours",
            "trend": trend,
            "change_percent": change,
            "data_points": len(hourly_stats),
            "hourly_breakdown": hourly_stats
        }

    def _save_metrics(self) -> None:
        """Save metrics to storage."""
        try:
            data = {
                "metrics": [asdict(m) for m in self.metrics],
                "last_updated": datetime.now().isoformat()
            }
            # Convert datetime objects to ISO format strings
            for metric_data in data["metrics"]:
                metric_data["timestamp"] = metric_data["timestamp"].isoformat()

            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save performance metrics: {e}")

    def _load_metrics(self) -> None:
        """Load metrics from storage."""
        try:
            if self.storage_path.exists():
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)

                for metric_data in data.get("metrics", []):
                    metric_data["timestamp"] = datetime.fromisoformat(metric_data["timestamp"])
                    metric = PerformanceMetric(**metric_data)
                    self.metrics.append(metric)
        except Exception as e:
            logger.error(f"Failed to load performance metrics: {e}")
            self.metrics = []

    def generate_report(self) -> str:
        """
        Generate comprehensive performance report.

        Returns:
            Formatted report string
        """
        report = []
        report.append("="*70)
        report.append("TOOL PERFORMANCE METRICS REPORT")
        report.append("="*70)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        # Overview
        total_metrics = len(self.metrics)
        if total_metrics == 0:
            report.append("No metrics available yet.")
            return "\n".join(report)

        overall_success_rate = sum(1 for m in self.metrics if m.success) / total_metrics
        total_cost = sum(m.cost for m in self.metrics)
        avg_duration = statistics.mean(m.duration for m in self.metrics)

        report.append("OVERVIEW")
        report.append("-"*70)
        report.append(f"Total Requests: {total_metrics}")
        report.append(f"Overall Success Rate: {overall_success_rate*100:.2f}%")
        report.append(f"Total Cost: ${total_cost:.2f}")
        report.append(f"Average Duration: {avg_duration:.2f}s")
        report.append("")

        # Tool leaderboard
        report.append("TOOL PERFORMANCE LEADERBOARD")
        report.append("-"*70)
        tool_leaderboard = []
        unique_tools = set(m.tool_name for m in self.metrics)
        for tool in unique_tools:
            metrics = self.get_tool_metrics(tool)
            if metrics:
                tool_leaderboard.append(metrics)

        tool_leaderboard.sort(key=lambda x: x.success_rate, reverse=True)

        for i, tool in enumerate(tool_leaderboard[:10], 1):
            report.append(
                f"{i:2}. {tool.tool_name:20} | "
                f"Success: {tool.success_rate*100:5.1f}% | "
                f"Duration: {tool.avg_duration:6.2f}s | "
                f"Cost: ${tool.avg_cost:6.3f}"
            )
        report.append("")

        # Model leaderboard
        report.append("MODEL PERFORMANCE LEADERBOARD")
        report.append("-"*70)
        model_leaderboard = self.get_performance_leaderboard("performance_score")

        for i, model in enumerate(model_leaderboard[:10], 1):
            report.append(
                f"{i:2}. {model['model']:30} | "
                f"Score: {model['performance_score']:6.3f} | "
                f"Cost Eff: {model['cost_efficiency']:8.0f} | "
                f"Errors: {model['error_rate']*100:5.1f}%"
            )
        report.append("")

        # Optimization recommendations
        recommendations = self.get_optimization_recommendations()
        if recommendations:
            report.append("OPTIMIZATION RECOMMENDATIONS")
            report.append("-"*70)
            for rec in recommendations:
                severity_mark = {"high": "!!!", "medium": "!!", "low": "!"}[rec["severity"]]
                report.append(f"{severity_mark} [{rec['type']}] {rec.get('tool', rec.get('model', 'N/A'))}")
                report.append(f"    {rec['message']}")
                report.append(f"    Action: {rec['action']}")
                report.append("")
        else:
            report.append("OPTIMIZATION RECOMMENDATIONS")
            report.append("-"*70)
            report.append("No optimization recommendations at this time.")
            report.append("")

        return "\n".join(report)


# Global metrics collector instance
_metrics_collector: Optional[PerformanceMetricsCollector] = None


def get_metrics_collector() -> PerformanceMetricsCollector:
    """Get or create global metrics collector instance."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = PerformanceMetricsCollector()
    return _metrics_collector


# Decorator for automatic metrics collection
def collect_metrics(tool_name: str):
    """
    Decorator to automatically collect performance metrics.

    Args:
        tool_name: Name of the tool
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            collector = get_metrics_collector()
            model = kwargs.get("model", "unknown")
            provider = "kimi" if "kimi" in model else "glm"

            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time

                # Estimate tokens and cost (would be provided by actual implementation)
                token_count = len(str(result)) // 4  # Rough estimate
                cost = duration * 0.01  # Rough estimate

                collector.record_metric(
                    tool_name=tool_name,
                    model_name=model,
                    provider=provider,
                    duration=duration,
                    token_count=token_count,
                    cost=cost,
                    success=True
                )

                return result
            except Exception as e:
                duration = time.time() - start_time

                collector.record_metric(
                    tool_name=tool_name,
                    model_name=model,
                    provider=provider,
                    duration=duration,
                    token_count=0,
                    cost=0,
                    success=False
                )

                raise

        return wrapper
    return decorator


if __name__ == "__main__":
    # Generate report
    collector = get_metrics_collector()
    report = collector.generate_report()
    print(report)

    # Save report
    Path("docs/reports/tool_performance_metrics_report.md").write_text(report)
    print("\nReport saved to docs/reports/tool_performance_metrics_report.md")
