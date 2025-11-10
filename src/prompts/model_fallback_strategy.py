"""
Model Fallback Strategy System

Automatic failover system for AI models with:
- Multi-tier fallback hierarchy
- Health monitoring and circuit breakers
- Intelligent model selection based on failure patterns
- Graceful degradation with user notification
- Performance-based routing

Created: 2025-11-09
Medium-Term Task 4
"""

import asyncio
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field
import json
import statistics
from pathlib import Path

from .universal_config import get_config, get_storage_path

logger = logging.getLogger(__name__)


class FallbackTrigger(Enum):
    """Triggers for fallback activation."""
    TIMEOUT = "timeout"
    ERROR = "error"
    RATE_LIMIT = "rate_limit"
    QUALITY_THRESHOLD = "quality_threshold"
    CIRCUIT_BREAKER = "circuit_breaker"
    MANUAL = "manual"


class ModelHealth(Enum):
    """Health status of a model."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CIRCUIT_OPEN = "circuit_open"
    RECOVERING = "recovering"


@dataclass
class FallbackAttempt:
    """Record of a fallback attempt."""
    timestamp: datetime
    primary_model: str
    fallback_model: str
    trigger: FallbackTrigger
    success: bool
    duration: float
    error_message: Optional[str] = None
    quality_score: Optional[float] = None


@dataclass
class ModelFailureStats:
    """Statistics for model failures."""
    model_name: str
    provider: str
    total_attempts: int = 0
    successes: int = 0
    failures: int = 0
    timeouts: int = 0
    errors: int = 0
    rate_limits: int = 0
    quality_failures: int = 0
    avg_duration: float = 0.0
    success_rate: float = 0.0
    last_failure: Optional[datetime] = None
    consecutive_failures: int = 0
    health_status: ModelHealth = ModelHealth.HEALTHY
    circuit_breaker_trips: int = 0
    fallback_attempts: int = 0
    successful_fallbacks: int = 0


@dataclass
class FallbackStrategy:
    """Configuration for fallback strategy."""
    model_name: str
    provider: str
    fallback_models: List[str] = field(default_factory=list)
    timeout_threshold: float = 60.0
    quality_threshold: float = 0.7
    max_retries: int = 2
    circuit_breaker_failure_threshold: int = 5
    circuit_breaker_recovery_time: int = 300  # 5 minutes
    cooldown_period: int = 60  # 1 minute
    priority_order: bool = True


class ModelFallbackStrategy:
    """
    Comprehensive model fallback system with intelligent routing.

    Features:
    - Multi-tier fallback hierarchy
    - Circuit breaker pattern
    - Health monitoring
    - Performance-based routing
    - Automatic recovery
    """

    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize fallback strategy.

        Args:
            storage_path: Optional custom storage path
        """
        # Load configuration
        try:
            if storage_path:
                self.storage_path = Path(storage_path)
            else:
                self.storage_path = Path(get_storage_path("model_fallback"))
        except Exception:
            self.storage_path = Path("~/.exai-prompts/data/model_fallback.json")

        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        # Load existing data
        self.failure_stats: Dict[str, ModelFailureStats] = {}
        self.fallback_strategies: Dict[str, FallbackStrategy] = {}
        self.fallback_history: List[FallbackAttempt] = []

        # Load persisted data
        self._load_data()

        # Default fallback strategies for known models
        self._init_default_strategies()

    def _load_data(self) -> None:
        """Load persisted data from storage."""
        try:
            if self.storage_path.exists():
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)

                    # Load failure stats
                    for model_name, stats_data in data.get('failure_stats', {}).items():
                        stats = ModelFailureStats(**stats_data)
                        # Convert string timestamps back to datetime
                        if stats.last_failure:
                            stats.last_failure = datetime.fromisoformat(stats.last_failure)
                        self.failure_stats[model_name] = stats

                    # Load fallback strategies
                    for model_name, strategy_data in data.get('fallback_strategies', {}).items():
                        self.fallback_strategies[model_name] = FallbackStrategy(**strategy_data)

                    # Load fallback history
                    for attempt_data in data.get('fallback_history', []):
                        attempt_data['timestamp'] = datetime.fromisoformat(attempt_data['timestamp'])
                        attempt_data['trigger'] = FallbackTrigger(attempt_data['trigger'])
                        self.fallback_history.append(FallbackAttempt(**attempt_data))
        except Exception as e:
            logger.warning(f"Failed to load fallback data: {e}")

    def _save_data(self) -> None:
        """Persist data to storage."""
        try:
            # Convert to JSON-serializable format
            data = {
                'failure_stats': {
                    name: {
                        **stats.__dict__,
                        'last_failure': stats.last_failure.isoformat() if stats.last_failure else None
                    }
                    for name, stats in self.failure_stats.items()
                },
                'fallback_strategies': {
                    name: strategy.__dict__
                    for name, strategy in self.fallback_strategies.items()
                },
                'fallback_history': [
                    {
                        **attempt.__dict__,
                        'timestamp': attempt.timestamp.isoformat(),
                        'trigger': attempt.trigger.value
                    }
                    for attempt in self.fallback_history[-1000:]  # Keep last 1000
                ]
            }

            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save fallback data: {e}")

    def _init_default_strategies(self) -> None:
        """Initialize default fallback strategies."""
        defaults = {
            "glm-4.6": FallbackStrategy(
                model_name="glm-4.6",
                provider="GLM",
                fallback_models=["glm-4.5-flash", "kimi-k2-0905-preview"],
                timeout_threshold=60.0,
                quality_threshold=0.7,
                circuit_breaker_failure_threshold=5
            ),
            "glm-4.5-flash": FallbackStrategy(
                model_name="glm-4.5-flash",
                provider="GLM",
                fallback_models=["kimi-k2-0905-preview", "glm-4.6"],
                timeout_threshold=45.0,
                quality_threshold=0.6,
                circuit_breaker_failure_threshold=7
            ),
            "kimi-k2-0905-preview": FallbackStrategy(
                model_name="kimi-k2-0905-preview",
                provider="Kimi",
                fallback_models=["kimi-latest", "glm-4.6"],
                timeout_threshold=60.0,
                quality_threshold=0.75,
                circuit_breaker_failure_threshold=5
            ),
            "kimi-k2-turbo-preview": FallbackStrategy(
                model_name="kimi-k2-turbo-preview",
                provider="Kimi",
                fallback_models=["kimi-latest", "glm-4.6"],
                timeout_threshold=60.0,
                quality_threshold=0.8,
                circuit_breaker_failure_threshold=3
            ),
            "kimi-latest": FallbackStrategy(
                model_name="kimi-latest",
                provider="Kimi",
                fallback_models=["glm-4.6", "glm-4.5-flash"],
                timeout_threshold=60.0,
                quality_threshold=0.75,
                circuit_breaker_failure_threshold=5
            )
        }

        for model_name, strategy in defaults.items():
            if model_name not in self.fallback_strategies:
                self.fallback_strategies[model_name] = strategy

    def register_model(
        self,
        model_name: str,
        provider: str,
        fallback_models: Optional[List[str]] = None,
        **kwargs
    ) -> None:
        """
        Register a model with its fallback strategy.

        Args:
            model_name: Name of the model
            provider: Provider name
            fallback_models: List of fallback models
            **kwargs: Additional strategy parameters
        """
        strategy = FallbackStrategy(
            model_name=model_name,
            provider=provider,
            fallback_models=fallback_models or [],
            **kwargs
        )

        self.fallback_strategies[model_name] = strategy
        self._save_data()
        logger.info(f"Registered model fallback strategy: {model_name}")

    async def execute_with_fallback(
        self,
        primary_model: str,
        execute_func: Callable,
        fallback_func: Optional[Callable] = None,
        *args,
        **kwargs
    ) -> Tuple[Any, bool]:
        """
        Execute a function with automatic fallback.

        Args:
            primary_model: Primary model to try
            execute_func: Function to execute
            fallback_func: Optional custom fallback function
            *args: Arguments for execute_func
            **kwargs: Keyword arguments for execute_func

        Returns:
            Tuple of (result, fallback_used)
        """
        strategy = self.fallback_strategies.get(primary_model)

        if not strategy:
            # No fallback strategy, execute directly
            result = await execute_func(*args, **kwargs)
            return result, False

        # Get initial failure stats
        if primary_model not in self.failure_stats:
            self.failure_stats[primary_model] = ModelFailureStats(
                model_name=primary_model,
                provider=strategy.provider
            )

        # Try primary model
        try:
            result = await self._execute_with_monitoring(
                primary_model,
                execute_func,
                *args,
                **kwargs
            )

            # Check quality if available
            if isinstance(result, dict) and 'quality_score' in result:
                quality_score = result.get('quality_score')
                if quality_score < strategy.quality_threshold:
                    await self._record_failure(
                        primary_model,
                        FallbackTrigger.QUALITY_THRESHOLD,
                        f"Quality score {quality_score} below threshold {strategy.quality_threshold}"
                    )
                    return await self._try_fallbacks(
                        primary_model,
                        strategy,
                        execute_func,
                        *args,
                        **kwargs
                    )

            # Success - update stats
            await self._record_success(primary_model)
            return result, False

        except asyncio.TimeoutError:
            await self._record_failure(
                primary_model,
                FallbackTrigger.TIMEOUT,
                "Request timed out"
            )
            return await self._try_fallbacks(
                primary_model,
                strategy,
                execute_func,
                *args,
                **kwargs
            )

        except Exception as e:
            error_msg = str(e)
            trigger = FallbackTrigger.ERROR

            # Determine trigger type
            if "rate limit" in error_msg.lower():
                trigger = FallbackTrigger.RATE_LIMIT

            await self._record_failure(
                primary_model,
                trigger,
                error_msg
            )
            return await self._try_fallbacks(
                primary_model,
                strategy,
                execute_func,
                *args,
                **kwargs
            )

    async def _execute_with_monitoring(
        self,
        model_name: str,
        execute_func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """Execute function with monitoring."""
        start_time = datetime.now()
        result = await execute_func(*args, **kwargs)
        duration = (datetime.now() - start_time).total_seconds()

        # Update stats
        if model_name in self.failure_stats:
            stats = self.failure_stats[model_name]
            if stats.avg_duration == 0:
                stats.avg_duration = duration
            else:
                stats.avg_duration = (stats.avg_duration + duration) / 2

        return result

    async def _try_fallbacks(
        self,
        primary_model: str,
        strategy: FallbackStrategy,
        execute_func: Callable,
        *args,
        **kwargs
    ) -> Tuple[Any, bool]:
        """Try fallback models."""
        for fallback_model in strategy.fallback_models:
            # Check if fallback is healthy
            if not self._is_model_healthy(fallback_model):
                logger.warning(f"Fallback model {fallback_model} is not healthy, skipping")
                continue

            try:
                logger.info(f"Trying fallback model: {fallback_model}")

                # Update stats
                if fallback_model not in self.failure_stats:
                    fallback_strategy = self.fallback_strategies.get(fallback_model)
                    provider = fallback_strategy.provider if fallback_strategy else "Unknown"
                    self.failure_stats[fallback_model] = ModelFailureStats(
                        model_name=fallback_model,
                        provider=provider
                    )

                # Execute with fallback
                result = await self._execute_with_monitoring(
                    fallback_model,
                    execute_func,
                    *args,
                    **kwargs
                )

                # Record successful fallback
                attempt = FallbackAttempt(
                    timestamp=datetime.now(),
                    primary_model=primary_model,
                    fallback_model=fallback_model,
                    trigger=FallbackTrigger.MANUAL,
                    success=True,
                    duration=0.0
                )
                self.fallback_history.append(attempt)

                # Update stats
                if primary_model in self.failure_stats:
                    self.failure_stats[primary_model].successful_fallbacks += 1

                logger.info(f"Fallback to {fallback_model} successful")
                self._save_data()
                return result, True

            except Exception as e:
                logger.error(f"Fallback model {fallback_model} failed: {e}")
                continue

        # All fallbacks failed
        logger.error(f"All fallbacks failed for {primary_model}")
        raise RuntimeError(f"All fallback models failed for {primary_model}")

    async def _record_success(self, model_name: str) -> None:
        """Record successful execution."""
        if model_name in self.failure_stats:
            stats = self.failure_stats[model_name]
            stats.successes += 1
            stats.total_attempts += 1
            stats.consecutive_failures = 0
            stats.success_rate = stats.successes / stats.total_attempts
            stats.health_status = ModelHealth.HEALTHY

            self._save_data()

    async def _record_failure(
        self,
        model_name: str,
        trigger: FallbackTrigger,
        error_message: str
    ) -> None:
        """Record failed execution."""
        if model_name in self.failure_stats:
            stats = self.failure_stats[model_name]
            stats.failures += 1
            stats.total_attempts += 1
            stats.consecutive_failures += 1
            stats.last_failure = datetime.now()
            stats.success_rate = stats.successes / stats.total_attempts

            # Update failure type counts
            if trigger == FallbackTrigger.TIMEOUT:
                stats.timeouts += 1
            elif trigger == FallbackTrigger.ERROR:
                stats.errors += 1
            elif trigger == FallbackTrigger.RATE_LIMIT:
                stats.rate_limits += 1
            elif trigger == FallbackTrigger.QUALITY_THRESHOLD:
                stats.quality_failures += 1

            # Check circuit breaker
            if stats.consecutive_failures >= stats.circuit_breaker_failure_threshold:
                stats.circuit_breaker_trips += 1
                stats.health_status = ModelHealth.CIRCUIT_OPEN
                logger.warning(f"Circuit breaker opened for {model_name}")

            # Update health status
            if stats.success_rate < 0.5:
                stats.health_status = ModelHealth.UNHEALTHY
            elif stats.success_rate < 0.8:
                stats.health_status = ModelHealth.DEGRADED

            self._save_data()

    def _is_model_healthy(self, model_name: str) -> bool:
        """Check if a model is healthy and can be used."""
        if model_name not in self.failure_stats:
            return True

        stats = self.failure_stats[model_name]

        # Check circuit breaker
        if stats.health_status == ModelHealth.CIRCUIT_OPEN:
            # Check if recovery time has passed
            if stats.last_failure:
                time_since_failure = (datetime.now() - stats.last_failure).total_seconds()
                if time_since_failure < 60:  # 1 minute cooldown
                    return False
                else:
                    # Mark as recovering
                    stats.health_status = ModelHealth.RECOVERING
                    self._save_data()

        return stats.health_status in [
            ModelHealth.HEALTHY,
            ModelHealth.RECOVERING
        ]

    def get_healthy_models(
        self,
        provider: Optional[str] = None
    ) -> List[str]:
        """
        Get list of healthy models.

        Args:
            provider: Optional provider filter

        Returns:
            List of healthy model names
        """
        models = []

        for model_name, stats in self.failure_stats.items():
            if self._is_model_healthy(model_name):
                strategy = self.fallback_strategies.get(model_name)
                if strategy and (not provider or strategy.provider == provider):
                    models.append(model_name)

        return sorted(models)

    def get_fallback_recommendations(
        self,
        model_name: str,
        task_type: Optional[str] = None
    ) -> List[str]:
        """
        Get fallback model recommendations.

        Args:
            model_name: Primary model
            task_type: Optional task type for better selection

        Returns:
            List of recommended fallback models
        """
        strategy = self.fallback_strategies.get(model_name)
        if not strategy:
            return []

        # Filter healthy models
        healthy_fallbacks = [
            m for m in strategy.fallback_models
            if self._is_model_healthy(m)
        ]

        # Sort by success rate if stats available
        def sort_key(model):
            if model in self.failure_stats:
                return self.failure_stats[model].success_rate
            return 0.5  # Default for unknown

        return sorted(healthy_fallbacks, key=sort_key, reverse=True)

    def get_model_health_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive health report.

        Returns:
            Health report dictionary
        """
        report = {
            'generated_at': datetime.now().isoformat(),
            'total_models': len(self.failure_stats),
            'healthy_models': len(self.get_healthy_models()),
            'models': {}
        }

        for model_name, stats in self.failure_stats.items():
            report['models'][model_name] = {
                'health_status': stats.health_status.value,
                'success_rate': stats.success_rate,
                'total_attempts': stats.total_attempts,
                'consecutive_failures': stats.consecutive_failures,
                'last_failure': stats.last_failure.isoformat() if stats.last_failure else None,
                'fallback_attempts': stats.fallback_attempts,
                'successful_fallbacks': stats.successful_fallbacks,
                'fallback_success_rate': (
                    stats.successful_fallbacks / stats.fallback_attempts
                    if stats.fallback_attempts > 0 else 0
                ),
                'provider': stats.provider
            }

        return report

    def reset_model_stats(self, model_name: str) -> None:
        """
        Reset statistics for a model.

        Args:
            model_name: Model to reset
        """
        if model_name in self.failure_stats:
            provider = self.failure_stats[model_name].provider
            self.failure_stats[model_name] = ModelFailureStats(
                model_name=model_name,
                provider=provider
            )
            self._save_data()
            logger.info(f"Reset statistics for model: {model_name}")

    def get_recent_fallbacks(
        self,
        hours: int = 24
    ) -> List[FallbackAttempt]:
        """
        Get recent fallback attempts.

        Args:
            hours: Number of hours to look back

        Returns:
            List of fallback attempts
        """
        cutoff = datetime.now() - timedelta(hours=hours)
        return [
            attempt for attempt in self.fallback_history
            if attempt.timestamp >= cutoff
        ]

    def generate_fallback_report(self) -> str:
        """
        Generate comprehensive fallback report.

        Returns:
            Formatted report string
        """
        report = []
        report.append("# Model Fallback Strategy Report")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        # Health summary
        healthy_count = len(self.get_healthy_models())
        total_count = len(self.failure_stats)
        report.append("## Health Summary")
        report.append(f"- Total Models: {total_count}")
        report.append(f"- Healthy Models: {healthy_count}")
        report.append(f"- Unhealthy Models: {total_count - healthy_count}")
        report.append("")

        # Model health details
        report.append("## Model Health Details")
        for model_name, stats in sorted(self.failure_stats.items()):
            health_icon = {
                ModelHealth.HEALTHY: "✅",
                ModelHealth.DEGRADED: "⚠️",
                ModelHealth.UNHEALTHY: "❌",
                ModelHealth.CIRCUIT_OPEN: "🔴",
                ModelHealth.RECOVERING: "🟡"
            }[stats.health_status]

            report.append(f"### {health_icon} {model_name}")
            report.append(f"- Status: {stats.health_status.value}")
            report.append(f"- Success Rate: {stats.success_rate*100:.1f}%")
            report.append(f"- Total Attempts: {stats.total_attempts}")
            report.append(f"- Consecutive Failures: {stats.consecutive_failures}")
            report.append(f"- Provider: {stats.provider}")

            if stats.last_failure:
                report.append(f"- Last Failure: {stats.last_failure.strftime('%Y-%m-%d %H:%M:%S')}")

            if stats.fallback_attempts > 0:
                report.append(f"- Fallback Success Rate: {stats.successful_fallbacks/stats.fallback_attempts*100:.1f}%")

            report.append("")

        # Recent fallbacks
        recent_fallbacks = self.get_recent_fallbacks(24)
        if recent_fallbacks:
            report.append("## Recent Fallbacks (Last 24 Hours)")
            for attempt in recent_fallbacks[-10:]:  # Last 10
                success_icon = "✅" if attempt.success else "❌"
                report.append(f"- {success_icon} {attempt.primary_model} → {attempt.fallback_model}")
                report.append(f"  Trigger: {attempt.trigger.value}, Time: {attempt.timestamp.strftime('%H:%M:%S')}")
                if attempt.error_message:
                    report.append(f"  Error: {attempt.error_message}")
            report.append("")

        return "\n".join(report)


# Global instance
_fallback_strategy: Optional[ModelFallbackStrategy] = None


def get_fallback_strategy(storage_path: Optional[str] = None) -> ModelFallbackStrategy:
    """
    Get global fallback strategy instance.

    Args:
        storage_path: Optional custom storage path

    Returns:
        ModelFallbackStrategy instance
    """
    global _fallback_strategy
    if _fallback_strategy is None:
        _fallback_strategy = ModelFallbackStrategy(storage_path)
    return _fallback_strategy


def with_fallback(
    primary_model: str,
    fallback_models: Optional[List[str]] = None
):
    """
    Decorator for automatic fallback.

    Args:
        primary_model: Primary model to use
        fallback_models: List of fallback models

    Usage:
        @with_fallback("glm-4.6", ["glm-4.5-flash", "kimi-k2-0905-preview"])
        async def my_function():
            pass
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            strategy = get_fallback_strategy()
            strategy.register_model(
                primary_model,
                "Unknown",
                fallback_models or []
            )

            result, _ = await strategy.execute_with_fallback(
                primary_model,
                func,
                *args,
                **kwargs
            )
            return result
        return wrapper
    return decorator


if __name__ == "__main__":
    # Demo usage
    async def main():
        strategy = get_fallback_strategy()

        # Register a custom model
        strategy.register_model(
            "my-model",
            "MyProvider",
            ["glm-4.6", "kimi-k2-0905-preview"],
            quality_threshold=0.8
        )

        # Get health report
        report = strategy.generate_fallback_report()
        print(report)

        # Get healthy models
        healthy = strategy.get_healthy_models()
        print(f"\nHealthy models: {healthy}")

    asyncio.run(main())
