"""
Phase 1 Tests: Feature Flag Integration

Tests for:
- Feature flag configuration
- Rollout percentage logic
- Async wrapper decorator
- Metrics collection
- Fallback behavior
"""

import pytest
import os
import asyncio
from unittest.mock import patch, MagicMock
from tools.config.async_upload_config import AsyncUploadConfig, get_config, reset_config
from tools.monitoring.async_upload_metrics import (
    UploadMetrics, MetricsCollector, get_metrics_collector, reset_metrics
)
from tools.decorators.async_upload_wrapper import async_upload_wrapper


class TestAsyncUploadConfig:
    """Test feature flag configuration"""
    
    def setup_method(self):
        """Reset config before each test"""
        reset_config()
    
    def test_default_config_disabled(self):
        """Test that async is disabled by default"""
        config = AsyncUploadConfig.from_env()
        assert not config.enabled
        assert config.rollout_percentage == 0
        assert config.fallback_on_error is True
    
    @patch.dict(os.environ, {
        'ASYNC_UPLOAD_ENABLED': 'true',
        'ASYNC_UPLOAD_ROLLOUT': '50'
    })
    def test_config_from_env(self):
        """Test loading config from environment variables"""
        reset_config()
        config = AsyncUploadConfig.from_env()
        assert config.enabled is True
        assert config.rollout_percentage == 50
    
    @patch.dict(os.environ, {
        'ASYNC_UPLOAD_ENABLED': 'false',
        'ASYNC_UPLOAD_ROLLOUT': '0'
    })
    def test_config_disabled_via_env(self):
        """Test disabling async via environment"""
        reset_config()
        config = AsyncUploadConfig.from_env()
        assert config.enabled is False
        assert config.rollout_percentage == 0


class TestRolloutLogic:
    """Test rollout percentage logic"""
    
    def test_rollout_zero_percent(self):
        """Test that 0% rollout never uses async"""
        config = AsyncUploadConfig(enabled=True, rollout_percentage=0)
        assert not config.should_use_async("test-request-1")
        assert not config.should_use_async("test-request-2")
    
    def test_rollout_hundred_percent(self):
        """Test that 100% rollout always uses async"""
        config = AsyncUploadConfig(enabled=True, rollout_percentage=100)
        assert config.should_use_async("test-request-1")
        assert config.should_use_async("test-request-2")
    
    def test_rollout_disabled(self):
        """Test that disabled config never uses async"""
        config = AsyncUploadConfig(enabled=False, rollout_percentage=100)
        assert not config.should_use_async("test-request-1")
    
    def test_rollout_consistency(self):
        """Test that same request ID always gets same result"""
        config = AsyncUploadConfig(enabled=True, rollout_percentage=50)
        
        result1 = config.should_use_async("consistent-id")
        result2 = config.should_use_async("consistent-id")
        
        assert result1 == result2
    
    def test_rollout_distribution(self):
        """Test that rollout percentage is roughly distributed"""
        config = AsyncUploadConfig(enabled=True, rollout_percentage=50)
        
        # Test with 1000 different request IDs
        async_count = sum(
            1 for i in range(1000)
            if config.should_use_async(f"request-{i}")
        )
        
        # Should be roughly 50% (allow 40-60% variance)
        assert 400 < async_count < 600


class TestMetricsCollection:
    """Test metrics collection"""
    
    def setup_method(self):
        """Reset metrics before each test"""
        reset_metrics()
    
    def test_record_successful_upload(self):
        """Test recording successful upload"""
        collector = get_metrics_collector()
        
        metrics = UploadMetrics(
            execution_type="async",
            success=True,
            duration_ms=100.5,
            file_size_mb=5.0,
            provider="kimi"
        )
        
        collector.record_upload(metrics)
        
        assert len(collector.metrics) == 1
        assert collector.metrics[0].success is True
    
    def test_record_failed_upload(self):
        """Test recording failed upload"""
        collector = get_metrics_collector()
        
        metrics = UploadMetrics(
            execution_type="async",
            success=False,
            duration_ms=50.0,
            error_type="TimeoutError",
            provider="kimi"
        )
        
        collector.record_upload(metrics)
        
        assert len(collector.metrics) == 1
        assert collector.metrics[0].success is False
        assert collector.metrics[0].error_type == "TimeoutError"
    
    def test_get_summary(self):
        """Test metrics summary"""
        collector = get_metrics_collector()
        
        # Record some metrics
        collector.record_upload(UploadMetrics(
            execution_type="async",
            success=True,
            duration_ms=100.0,
            provider="kimi"
        ))
        collector.record_upload(UploadMetrics(
            execution_type="async",
            success=False,
            duration_ms=50.0,
            error_type="TimeoutError",
            provider="kimi"
        ))
        collector.record_upload(UploadMetrics(
            execution_type="sync",
            success=True,
            duration_ms=200.0,
            provider="kimi"
        ))
        
        summary = collector.get_summary()
        
        assert summary["total_uploads"] == 3
        assert summary["successful"] == 2
        assert summary["failed"] == 1
        assert summary["success_rate"] == pytest.approx(66.67, rel=1)
    
    def test_async_vs_sync_comparison(self):
        """Test async vs sync performance comparison"""
        collector = get_metrics_collector()
        
        # Record async metrics
        for i in range(5):
            collector.record_upload(UploadMetrics(
                execution_type="async",
                success=True,
                duration_ms=100.0 + i,
                provider="kimi"
            ))
        
        # Record sync metrics
        for i in range(5):
            collector.record_upload(UploadMetrics(
                execution_type="sync",
                success=True,
                duration_ms=200.0 + i,
                provider="kimi"
            ))
        
        comparison = collector.get_async_vs_sync_comparison()
        
        assert comparison["async"]["count"] == 5
        assert comparison["sync"]["count"] == 5
        assert comparison["improvement"]["latency_improvement_percent"] > 0


class TestAsyncWrapper:
    """Test async wrapper decorator"""
    
    def setup_method(self):
        """Reset config and metrics before each test"""
        reset_config()
        reset_metrics()
    
    def test_sync_execution_when_disabled(self):
        """Test that sync is used when async is disabled"""
        @async_upload_wrapper
        def sync_func(x):
            return x * 2
        
        with patch('tools.decorators.async_upload_wrapper.get_config') as mock_config:
            mock_config.return_value = AsyncUploadConfig(enabled=False)
            result = sync_func(5)
            assert result == 10
    
    def test_sync_execution_when_rollout_zero(self):
        """Test that sync is used when rollout is 0%"""
        @async_upload_wrapper
        def sync_func(x):
            return x * 2
        
        with patch('tools.decorators.async_upload_wrapper.get_config') as mock_config:
            mock_config.return_value = AsyncUploadConfig(
                enabled=True,
                rollout_percentage=0
            )
            result = sync_func(5)
            assert result == 10
    
    def test_fallback_on_error(self):
        """Test fallback to sync on async error"""
        @async_upload_wrapper
        def sync_func(x):
            return x * 2

        with patch('tools.decorators.async_upload_wrapper.get_config') as mock_config:
            mock_config.return_value = AsyncUploadConfig(
                enabled=True,
                rollout_percentage=100,
                fallback_on_error=True
            )

            with patch('tools.decorators.async_upload_wrapper._async_execute') as mock_async:
                mock_async.side_effect = Exception("Async failed")

                result = sync_func(5)
                assert result == 10

                # Verify fallback was used by checking metrics
                collector = get_metrics_collector()
                assert len(collector.metrics) == 1
                assert collector.metrics[0].fallback_used is True
    
    def test_metrics_recorded(self):
        """Test that metrics are recorded"""
        @async_upload_wrapper
        def sync_func(x):
            return x * 2
        
        with patch('tools.decorators.async_upload_wrapper.get_config') as mock_config:
            mock_config.return_value = AsyncUploadConfig(enabled=False)
            
            result = sync_func(5)
            
            collector = get_metrics_collector()
            assert len(collector.metrics) == 1
            assert collector.metrics[0].success is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

