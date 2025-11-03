"""
Adaptive Timeout Engine - Data-driven, model-aware timeout management.

This module implements an adaptive timeout system that learns from actual model
performance and adjusts timeouts dynamically, replacing hardcoded timeout assumptions.

Key Features:
- Clipped P95 algorithm (discards top 1% outliers)
- Model version normalization
- Burst protection (prevents sudden timeout spikes)
- Emergency override mechanism
- Graceful error handling with fallback
- Memory-efficient circular buffer (100 samples per model)

Author: EX-AI MCP Server Team
Date: 2025-11-03
"""

import os
import re
import logging
from collections import defaultdict, deque
from typing import Dict, List, Optional, Tuple
import numpy as np

logger = logging.getLogger(__name__)

# Emergency timeout overrides (seconds)
EMERGENCY_TIMEOUT_OVERRIDE = {
    "kimi-k2-0905-preview": 300,
    "kimi-k2": 300,
    "kimi-thinking-preview": 180,
    "glm-4.6": 120,
}

# Maximum duration to accept (configurable via environment)
MAX_DURATION_SECONDS = int(os.getenv('ADAPTIVE_TIMEOUT_MAX_DURATION', '3600'))


class AdaptiveTimeoutEngine:
    """
    Learns from actual model performance and adjusts timeouts dynamically.
    
    Uses clipped P95 algorithm to handle outliers and provides burst protection
    to prevent sudden timeout spikes.
    """
    
    def __init__(
        self,
        percentile_threshold: int = 95,
        max_samples_per_model: int = 100,
        burst_protection_multiplier: float = 2.0,
        min_samples_for_adaptive: int = 5
    ):
        """
        Initialize the adaptive timeout engine.
        
        Args:
            percentile_threshold: Percentile to use for timeout calculation (default: 95)
            max_samples_per_model: Maximum samples to retain per model (default: 100)
            burst_protection_multiplier: Maximum allowed timeout increase (default: 2.0x)
            min_samples_for_adaptive: Minimum samples needed before using adaptive (default: 5)
        """
        self.historical_durations: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=max_samples_per_model)
        )
        self.percentile_threshold = percentile_threshold
        self.max_samples_per_model = max_samples_per_model
        self.burst_protection_multiplier = burst_protection_multiplier
        self.min_samples_for_adaptive = min_samples_for_adaptive
        self.last_timeout: Dict[str, int] = {}  # Track last timeout for burst protection

        # Provider-specific defaults (K2 Enhancement 1 - 2025-11-03)
        self.provider_defaults = {
            "kimi": {"base_timeout": 300, "percentile": 95},
            "glm": {"base_timeout": 120, "percentile": 90},
            "openai": {"base_timeout": 180, "percentile": 95},
            "default": {"base_timeout": 180, "percentile": 95}
        }

        logger.info(
            f"AdaptiveTimeoutEngine initialized: "
            f"P{percentile_threshold}, "
            f"max_samples={max_samples_per_model}, "
            f"burst_protection={burst_protection_multiplier}x"
        )
    
    def detect_provider(self, model: str) -> str:
        """
        Detect provider from model name with fallback logic.

        K2 Enhancement 1 (2025-11-03): Explicit provider detection

        Args:
            model: Model name

        Returns:
            Provider name ('kimi', 'glm', 'openai', 'default')
        """
        model_lower = model.lower()

        # Kimi models
        if any(pattern in model_lower for pattern in ['kimi', 'k2']):
            return 'kimi'

        # GLM models
        if any(pattern in model_lower for pattern in ['glm', 'zai']):
            return 'glm'

        # OpenAI models
        if any(pattern in model_lower for pattern in ['gpt', 'davinci', 'curie']):
            return 'openai'

        return 'default'

    def get_provider_specific_config(self, model: str) -> Dict:
        """
        Get provider-specific configuration.

        K2 Enhancement 1 (2025-11-03): Provider-specific defaults

        Args:
            model: Model name

        Returns:
            Dict with 'base_timeout' and 'percentile' keys
        """
        provider = self.detect_provider(model)
        return self.provider_defaults.get(provider, self.provider_defaults["default"])

    def normalize_model_name(self, model: str) -> str:
        """
        Normalize model name by stripping version suffixes.

        Examples:
            k2-2025-11-03 → k2
            gpt-4-turbo-2025-04 → gpt-4-turbo
            kimi-k2-0905-preview → kimi-k2-0905-preview (no change)

        Args:
            model: Raw model name

        Returns:
            Normalized model name
        """
        # Strip date suffixes (YYYY-MM-DD)
        normalized = re.sub(r'-\d{4}-\d{2}-\d{2}$', '', model)
        return normalized
    
    def validate_duration(self, duration: float) -> bool:
        """
        Validate duration before recording.

        K2 Enhancement 2 (2025-11-03): Duration validation

        Args:
            duration: Duration in seconds

        Returns:
            True if valid, False otherwise
        """
        if duration <= 0:
            logger.warning(f"Invalid duration: {duration}s (must be positive)")
            return False
        if duration > MAX_DURATION_SECONDS:
            logger.warning(f"Suspicious duration: {duration}s (>{MAX_DURATION_SECONDS}s)")
            return False
        return True

    def record_duration(self, model: str, duration: float) -> None:
        """
        Record actual duration for a model call.

        K2 Enhancement 2 (2025-11-03): Added duration validation

        Args:
            model: Model name (will be normalized)
            duration: Actual duration in seconds
        """
        # Validate duration before recording
        if not self.validate_duration(duration):
            return  # Skip invalid durations

        normalized_model = self.normalize_model_name(model)
        self.historical_durations[normalized_model].append(duration)

        logger.debug(
            f"Recorded duration for {normalized_model}: {duration:.2f}s "
            f"(total samples: {len(self.historical_durations[normalized_model])})"
        )
    
    def get_adaptive_timeout(self, model: str, base_timeout: int) -> int:
        """
        Calculate adaptive timeout based on historical performance.
        
        Uses clipped P95 algorithm:
        1. Discard top 1% outliers
        2. Calculate P95 of remaining samples
        3. Add 20% buffer (minimum 30s)
        4. Never go below base_timeout
        
        Args:
            model: Model name (will be normalized)
            base_timeout: Fallback timeout if no history available
            
        Returns:
            Adaptive timeout in seconds
        """
        normalized_model = self.normalize_model_name(model)
        durations = list(self.historical_durations.get(normalized_model, []))
        
        # Not enough samples - use base timeout
        if len(durations) < self.min_samples_for_adaptive:
            logger.debug(
                f"Insufficient samples for {normalized_model} "
                f"({len(durations)}/{self.min_samples_for_adaptive}), "
                f"using base timeout: {base_timeout}s"
            )
            return base_timeout
        
        # Clipped P95 - discard top 1% outliers before percentile calc
        sorted_durations = sorted(durations)
        clip_index = max(1, int(len(sorted_durations) * 0.99))  # At least 1 sample
        clipped = sorted_durations[:clip_index]
        
        # Calculate P95 of clipped data
        p95 = np.percentile(clipped, self.percentile_threshold)
        
        # Add buffer: 20% or 30s minimum
        buffer = max(30, p95 * 0.2)
        adaptive = int(p95 + buffer)
        
        # Never go below base timeout (safety floor)
        final_timeout = max(base_timeout, adaptive)
        
        logger.debug(
            f"Adaptive timeout for {normalized_model}: "
            f"P95={p95:.2f}s, buffer={buffer:.2f}s, "
            f"adaptive={adaptive}s, final={final_timeout}s "
            f"(samples={len(durations)}, clipped={len(clipped)})"
        )
        
        return final_timeout
    
    def apply_burst_protection(self, model: str, new_timeout: int, old_timeout: Optional[int] = None) -> int:
        """
        Apply burst protection to prevent sudden timeout spikes.
        
        Limits timeout increases to burst_protection_multiplier (default 2.0x).
        
        Args:
            model: Model name (will be normalized)
            new_timeout: Newly calculated timeout
            old_timeout: Previous timeout (optional, uses last_timeout if not provided)
            
        Returns:
            Protected timeout
        """
        normalized_model = self.normalize_model_name(model)
        
        if old_timeout is None:
            old_timeout = self.last_timeout.get(normalized_model)
        
        if old_timeout is None:
            # No previous timeout - allow new timeout
            self.last_timeout[normalized_model] = new_timeout
            return new_timeout
        
        # Apply burst protection
        max_allowed = int(old_timeout * self.burst_protection_multiplier)
        protected_timeout = min(new_timeout, max_allowed)
        
        if protected_timeout < new_timeout:
            logger.warning(
                f"Burst protection applied for {normalized_model}: "
                f"new={new_timeout}s limited to {protected_timeout}s "
                f"(old={old_timeout}s, max_change={self.burst_protection_multiplier}x)"
            )
        
        self.last_timeout[normalized_model] = protected_timeout
        return protected_timeout
    
    def get_emergency_override(self, model: str) -> Tuple[Optional[int], Optional[str]]:
        """
        Get emergency override with case-insensitive partial matching.

        K2 Enhancement 4 (2025-11-03): Partial matching for version flexibility

        Args:
            model: Model name

        Returns:
            Tuple of (timeout, override_key) or (None, None)
        """
        model_lower = model.lower()

        for override_key, timeout in EMERGENCY_TIMEOUT_OVERRIDE.items():
            if override_key.lower() in model_lower:
                return timeout, override_key

        return None, None

    def get_adaptive_timeout_safe(self, model: str, base_timeout: int, apply_burst: bool = True) -> Tuple[int, Dict]:
        """
        Safe wrapper for get_adaptive_timeout with error handling and metadata.

        K2 Enhancement 4 (2025-11-03): Enhanced emergency override with partial matching

        Args:
            model: Model name
            base_timeout: Fallback timeout
            apply_burst: Whether to apply burst protection (default: True)

        Returns:
            Tuple of (timeout_seconds, metadata_dict)
        """
        normalized_model = self.normalize_model_name(model)

        # Check emergency override with partial matching
        override_timeout, override_key = self.get_emergency_override(normalized_model)
        if override_timeout is not None:
            logger.info(f"Using emergency override for {normalized_model} (matched: {override_key}): {override_timeout}s")
            return override_timeout, {
                "source": "emergency",
                "confidence": 1.0,
                "samples_used": 0,
                "override_key": override_key
            }
        
        try:
            # Calculate adaptive timeout
            adaptive_timeout = self.get_adaptive_timeout(normalized_model, base_timeout)
            
            # Apply burst protection if requested
            if apply_burst:
                adaptive_timeout = self.apply_burst_protection(normalized_model, adaptive_timeout)
            
            # Determine source and confidence
            sample_count = len(self.historical_durations.get(normalized_model, []))
            if sample_count < self.min_samples_for_adaptive:
                source = "static"
                confidence = 0.0
            else:
                source = "adaptive"
                confidence = min(1.0, sample_count / self.max_samples_per_model)
            
            metadata = {
                "source": source,
                "confidence": confidence,
                "samples_used": sample_count
            }
            
            return adaptive_timeout, metadata
            
        except Exception as e:
            logger.error(f"Adaptive timeout calculation failed for {normalized_model}: {e}", exc_info=True)
            return base_timeout, {
                "source": "fallback",
                "confidence": 0.0,
                "samples_used": 0,
                "error": str(e)
            }
    
    def retire_model(self, model: str) -> None:
        """
        Remove historical data for a retired model.
        
        Args:
            model: Model name to retire (will be normalized)
        """
        normalized_model = self.normalize_model_name(model)
        
        if normalized_model in self.historical_durations:
            sample_count = len(self.historical_durations[normalized_model])
            del self.historical_durations[normalized_model]
            logger.info(f"Retired model {normalized_model} ({sample_count} samples removed)")
        
        if normalized_model in self.last_timeout:
            del self.last_timeout[normalized_model]
    
    def get_stats(self) -> Dict:
        """
        Get statistics about the adaptive timeout engine.

        Returns:
            Dictionary with engine statistics
        """
        total_samples = sum(len(durations) for durations in self.historical_durations.values())

        # Calculate confidence by model
        confidence_by_model = {}
        provider_distribution = defaultdict(int)

        for model, durations in self.historical_durations.items():
            sample_count = len(durations)
            confidence_by_model[model] = min(1.0, sample_count / self.max_samples_per_model)

            # Track provider distribution
            provider = self.detect_provider(model)
            provider_distribution[provider] += 1

        return {
            "models_tracked": len(self.historical_durations),
            "total_samples": total_samples,
            "confidence_by_model": confidence_by_model,
            "provider_distribution": dict(provider_distribution),
            "models": {
                model: {
                    "samples": len(durations),
                    "min": min(durations) if durations else None,
                    "max": max(durations) if durations else None,
                    "mean": np.mean(durations) if durations else None,
                    "p95": np.percentile(durations, 95) if durations else None
                }
                for model, durations in self.historical_durations.items()
            }
        }

    def health_check(self) -> Dict:
        """
        Quick health check for monitoring.

        K2 Enhancement 3 (2025-11-03): Health check endpoint

        Returns:
            Dictionary with health status and key metrics
        """
        stats = self.get_stats()

        # Calculate average confidence
        confidence_values = list(stats['confidence_by_model'].values())
        avg_confidence = sum(confidence_values) / max(len(confidence_values), 1) if confidence_values else 0.0

        # Count low confidence models
        low_confidence_models = len([c for c in confidence_values if c < 0.5])

        # Determine health status
        if avg_confidence > 0.7:
            status = "healthy"
        elif avg_confidence > 0.4:
            status = "degraded"
        else:
            status = "unhealthy"

        return {
            "status": status,
            "models_tracked": stats["models_tracked"],
            "total_samples": stats["total_samples"],
            "memory_usage_kb": round(stats["models_tracked"] * 0.4, 2),  # ~400 bytes per model
            "avg_confidence": round(avg_confidence, 3),
            "low_confidence_models": low_confidence_models,
            "provider_distribution": stats.get('provider_distribution', {})
        }


# Global singleton instance
_engine: Optional[AdaptiveTimeoutEngine] = None


def get_engine() -> AdaptiveTimeoutEngine:
    """Get or create the global adaptive timeout engine instance."""
    global _engine
    if _engine is None:
        _engine = AdaptiveTimeoutEngine()
    return _engine


def is_adaptive_timeout_enabled() -> bool:
    """Check if adaptive timeout is enabled via environment variable."""
    return os.getenv("ADAPTIVE_TIMEOUT_ENABLED", "false").lower() in ("true", "1", "yes")

