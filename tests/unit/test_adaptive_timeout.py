"""
Unit tests for Adaptive Timeout Engine.

Tests cover:
- Empty history fallback
- Outlier handling (clipped P95)
- Cold start scenarios
- Model version normalization
- Burst protection
- Emergency overrides
- Error handling
- Concurrent access protection

Author: EX-AI MCP Server Team
Date: 2025-11-03
"""

import pytest
import numpy as np
from src.core.adaptive_timeout import AdaptiveTimeoutEngine, EMERGENCY_TIMEOUT_OVERRIDE


class TestAdaptiveTimeoutEngine:
    """Test suite for AdaptiveTimeoutEngine."""
    
    def test_empty_history_uses_base_timeout(self):
        """Test that empty history falls back to base timeout."""
        engine = AdaptiveTimeoutEngine()
        timeout, metadata = engine.get_adaptive_timeout_safe("new-model", base_timeout=60)
        
        assert timeout == 60
        assert metadata["source"] == "static"
        assert metadata["confidence"] == 0.0
        assert metadata["samples_used"] == 0
    
    def test_insufficient_samples_uses_base_timeout(self):
        """Test that <5 samples falls back to base timeout."""
        engine = AdaptiveTimeoutEngine(min_samples_for_adaptive=5)
        
        # Add only 3 samples
        for duration in [10, 20, 30]:
            engine.record_duration("test-model", duration)
        
        timeout, metadata = engine.get_adaptive_timeout_safe("test-model", base_timeout=60)
        
        assert timeout == 60
        assert metadata["source"] == "static"
        assert metadata["samples_used"] == 3
    
    def test_clipped_p95_discards_outliers(self):
        """Test that clipped P95 discards top 1% outliers."""
        engine = AdaptiveTimeoutEngine()
        
        # Add 100 samples: 99 normal (10-20s) + 1 outlier (1000s)
        for i in range(99):
            engine.record_duration("test-model", 10 + (i % 10))
        engine.record_duration("test-model", 1000)  # Outlier
        
        timeout, metadata = engine.get_adaptive_timeout_safe("test-model", base_timeout=30)
        
        # Timeout should be based on P95 of normal samples (~20s), not outlier (1000s)
        # P95 of 10-20 ≈ 19s, buffer = max(30, 19*0.2) = 30s, total ≈ 49s
        assert timeout < 100  # Should not be influenced by 1000s outlier
        assert metadata["source"] == "adaptive"
        assert metadata["samples_used"] == 100
    
    def test_model_version_normalization(self):
        """Test that model versions are normalized correctly."""
        engine = AdaptiveTimeoutEngine()
        
        # Record durations for versioned model
        engine.record_duration("k2-2025-11-03", 100)
        engine.record_duration("k2-2025-11-04", 110)
        engine.record_duration("k2", 120)
        
        # All should be normalized to "k2"
        assert engine.normalize_model_name("k2-2025-11-03") == "k2"
        assert engine.normalize_model_name("k2-2025-11-04") == "k2"
        assert engine.normalize_model_name("k2") == "k2"
        
        # Should have 3 samples under "k2"
        assert len(engine.historical_durations["k2"]) == 3
    
    def test_burst_protection_limits_increases(self):
        """Test that burst protection prevents sudden timeout spikes."""
        engine = AdaptiveTimeoutEngine(burst_protection_multiplier=2.0)
        
        # Set initial timeout
        engine.last_timeout["test-model"] = 100
        
        # Try to increase to 300s (3x increase)
        protected = engine.apply_burst_protection("test-model", new_timeout=300)
        
        # Should be limited to 2x = 200s
        assert protected == 200
        assert engine.last_timeout["test-model"] == 200
    
    def test_burst_protection_allows_decreases(self):
        """Test that burst protection allows timeout decreases."""
        engine = AdaptiveTimeoutEngine(burst_protection_multiplier=2.0)
        
        # Set initial timeout
        engine.last_timeout["test-model"] = 100
        
        # Decrease to 50s
        protected = engine.apply_burst_protection("test-model", new_timeout=50)
        
        # Should allow decrease
        assert protected == 50
        assert engine.last_timeout["test-model"] == 50
    
    def test_emergency_override_takes_precedence(self):
        """Test that emergency overrides take precedence over adaptive."""
        engine = AdaptiveTimeoutEngine()
        
        # Add samples for k2
        for _ in range(10):
            engine.record_duration("kimi-k2-0905-preview", 50)
        
        # Emergency override should take precedence
        timeout, metadata = engine.get_adaptive_timeout_safe("kimi-k2-0905-preview", base_timeout=60)
        
        assert timeout == EMERGENCY_TIMEOUT_OVERRIDE["kimi-k2-0905-preview"]
        assert metadata["source"] == "emergency"
        assert metadata["confidence"] == 1.0
    
    def test_error_handling_falls_back_to_base(self):
        """Test that errors fall back to base timeout gracefully."""
        engine = AdaptiveTimeoutEngine()
        
        # Force an error by corrupting internal state
        engine.historical_durations["bad-model"] = "not-a-deque"
        
        timeout, metadata = engine.get_adaptive_timeout_safe("bad-model", base_timeout=60)
        
        assert timeout == 60
        assert metadata["source"] == "fallback"
        assert "error" in metadata
    
    def test_model_retirement_cleans_up_memory(self):
        """Test that model retirement removes historical data."""
        engine = AdaptiveTimeoutEngine()
        
        # Add samples
        for _ in range(10):
            engine.record_duration("old-model", 50)
        
        assert "old-model" in engine.historical_durations
        
        # Retire model
        engine.retire_model("old-model")
        
        assert "old-model" not in engine.historical_durations
        assert "old-model" not in engine.last_timeout
    
    def test_circular_buffer_limits_memory(self):
        """Test that circular buffer limits memory to max_samples."""
        engine = AdaptiveTimeoutEngine(max_samples_per_model=100)
        
        # Add 150 samples
        for i in range(150):
            engine.record_duration("test-model", i)
        
        # Should only retain last 100
        assert len(engine.historical_durations["test-model"]) == 100
        
        # Should contain samples 50-149 (last 100)
        durations = list(engine.historical_durations["test-model"])
        assert min(durations) == 50
        assert max(durations) == 149
    
    def test_confidence_increases_with_samples(self):
        """Test that confidence increases as more samples are collected."""
        engine = AdaptiveTimeoutEngine(max_samples_per_model=100)
        
        # Add 10 samples
        for _ in range(10):
            engine.record_duration("test-model", 50)
        
        _, metadata_10 = engine.get_adaptive_timeout_safe("test-model", base_timeout=60)
        
        # Add 90 more samples (total 100)
        for _ in range(90):
            engine.record_duration("test-model", 50)
        
        _, metadata_100 = engine.get_adaptive_timeout_safe("test-model", base_timeout=60)
        
        # Confidence should increase
        assert metadata_100["confidence"] > metadata_10["confidence"]
        assert metadata_100["confidence"] == 1.0  # 100/100 = 1.0
    
    def test_get_stats_returns_correct_data(self):
        """Test that get_stats returns accurate statistics."""
        engine = AdaptiveTimeoutEngine()
        
        # Add samples for two models
        for _ in range(10):
            engine.record_duration("model-a", 50)
        for _ in range(20):
            engine.record_duration("model-b", 100)
        
        stats = engine.get_stats()
        
        assert stats["models_tracked"] == 2
        assert stats["total_samples"] == 30
        assert stats["models"]["model-a"]["samples"] == 10
        assert stats["models"]["model-b"]["samples"] == 20
        assert stats["models"]["model-a"]["mean"] == 50
        assert stats["models"]["model-b"]["mean"] == 100
    
    def test_never_goes_below_base_timeout(self):
        """Test that adaptive timeout never goes below base timeout."""
        engine = AdaptiveTimeoutEngine()
        
        # Add very fast samples (1-5s)
        for i in range(10):
            engine.record_duration("fast-model", 1 + i % 5)
        
        # Even with fast samples, should respect base timeout
        timeout, _ = engine.get_adaptive_timeout_safe("fast-model", base_timeout=60)
        
        assert timeout >= 60


class TestConcurrentAccess:
    """Test concurrent access to adaptive timeout engine."""
    
    def test_concurrent_record_duration(self):
        """Test that concurrent record_duration calls don't corrupt data."""
        import threading
        
        engine = AdaptiveTimeoutEngine()
        
        def record_many(model, count):
            for i in range(count):
                # Use i+1 to avoid recording duration of 0 (invalid)
                engine.record_duration(model, i + 1)

        # Create 10 threads, each recording 100 samples
        threads = []
        for i in range(10):
            t = threading.Thread(target=record_many, args=(f"model-{i}", 100))
            threads.append(t)
            t.start()

        # Wait for all threads
        for t in threads:
            t.join()

        # Should have 10 models, each with 100 samples
        stats = engine.get_stats()
        assert stats["models_tracked"] == 10
        assert stats["total_samples"] == 1000

    # K2 Enhancement Tests (2025-11-03)

    def test_provider_specific_kimi_defaults(self):
        """Test provider-specific defaults for Kimi models."""
        engine = AdaptiveTimeoutEngine()
        config = engine.get_provider_specific_config("kimi-k2")

        assert config["base_timeout"] == 300
        assert config["percentile"] == 95

    def test_provider_specific_glm_defaults(self):
        """Test provider-specific defaults for GLM models."""
        engine = AdaptiveTimeoutEngine()
        config = engine.get_provider_specific_config("glm-4.6")

        assert config["base_timeout"] == 120
        assert config["percentile"] == 90

    def test_provider_detection_kimi(self):
        """Test provider detection for Kimi models."""
        engine = AdaptiveTimeoutEngine()

        assert engine.detect_provider("kimi-k2") == "kimi"
        assert engine.detect_provider("k2-2025-11-03") == "kimi"
        assert engine.detect_provider("kimi-thinking-preview") == "kimi"

    def test_provider_detection_glm(self):
        """Test provider detection for GLM models."""
        engine = AdaptiveTimeoutEngine()

        assert engine.detect_provider("glm-4.6") == "glm"
        assert engine.detect_provider("glm-4.5-flash") == "glm"
        assert engine.detect_provider("zai-model") == "glm"

    def test_duration_validation_boundary_conditions(self):
        """Test duration validation edge cases."""
        engine = AdaptiveTimeoutEngine()

        assert not engine.validate_duration(0)  # Zero duration
        assert not engine.validate_duration(-1)  # Negative duration
        assert not engine.validate_duration(3601)  # Just over 1 hour
        assert engine.validate_duration(0.001)  # Very small positive
        assert engine.validate_duration(3600)  # Exactly 1 hour
        assert engine.validate_duration(100)  # Normal duration

    def test_duration_validation_prevents_recording(self):
        """Test that invalid durations are not recorded."""
        engine = AdaptiveTimeoutEngine()

        # Try to record invalid durations
        engine.record_duration("test-model", -10)
        engine.record_duration("test-model", 0)
        engine.record_duration("test-model", 5000)

        # Should have no samples
        stats = engine.get_stats()
        assert stats["total_samples"] == 0

        # Record valid duration
        engine.record_duration("test-model", 100)
        stats = engine.get_stats()
        assert stats["total_samples"] == 1

    def test_health_check_healthy_state(self):
        """Test health check in healthy state."""
        engine = AdaptiveTimeoutEngine()

        # Add enough samples for high confidence
        for i in range(80):
            engine.record_duration("model-1", 10.0 + i * 0.1)

        health = engine.health_check()

        assert health["status"] == "healthy"
        assert health["models_tracked"] == 1
        assert health["total_samples"] == 80
        assert health["avg_confidence"] > 0.7
        assert health["low_confidence_models"] == 0

    def test_health_check_degraded_state(self):
        """Test health check in degraded state."""
        engine = AdaptiveTimeoutEngine()

        # Add many models with low samples
        for i in range(150):
            engine.record_duration(f"model-{i}", 10.0)

        health = engine.health_check()

        assert health["status"] in ["degraded", "unhealthy"]
        assert health["models_tracked"] == 150
        assert health["low_confidence_models"] > 0

    def test_emergency_override_partial_matching(self):
        """Test emergency override with partial matching."""
        engine = AdaptiveTimeoutEngine()

        # Test exact match
        timeout, key = engine.get_emergency_override("kimi-k2")
        assert timeout == 300
        assert key == "kimi-k2"

        # Test partial match with version
        timeout, key = engine.get_emergency_override("kimi-k2-2025-11-03")
        assert timeout == 300
        assert key == "kimi-k2"

        # Test case insensitivity
        timeout, key = engine.get_emergency_override("KIMI-K2")
        assert timeout == 300
        assert key == "kimi-k2"

        # Test no match
        timeout, key = engine.get_emergency_override("unknown-model")
        assert timeout is None
        assert key is None

    def test_emergency_override_in_safe_wrapper(self):
        """Test emergency override integration in get_adaptive_timeout_safe."""
        engine = AdaptiveTimeoutEngine()

        # Test with versioned model name
        timeout, metadata = engine.get_adaptive_timeout_safe("kimi-k2-2025-11-03", base_timeout=60)

        assert timeout == 300
        assert metadata["source"] == "emergency"
        assert metadata["confidence"] == 1.0
        assert "override_key" in metadata


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

