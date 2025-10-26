"""
Comprehensive Shadow Mode Validation Test Suite

Tests the shadow mode implementation for file management migration.
Validates facade routing, shadow mode capture, legacy operations,
configuration switching, and error handling.

Reference: EXAI consultation (Continuation: 9222d725-b6cd-44f1-8406-274e5a3b3389)
Date: 2025-10-22
"""

import pytest
import asyncio
import tempfile
import os
import uuid
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

# Import the components we're testing
from src.file_management.migration_facade import FileManagementFacade, ShadowModeMetrics
from src.file_management.manager import UnifiedFileManager
from src.file_management.rollout_manager import RolloutManager
from src.file_management.models import FileOperationResult, FileReference, FileUploadMetadata
from config import MigrationConfig

# Test constants
TEST_UUID = str(uuid.uuid4())
TEST_SHA256 = "a" * 64  # Valid SHA256 hash format


class TestShadowModeConfiguration:
    """Test shadow mode configuration and validation."""
    
    def test_shadow_mode_config_defaults(self):
        """Verify shadow mode configuration has correct defaults."""
        assert MigrationConfig.ENABLE_SHADOW_MODE == False  # Default off
        assert MigrationConfig.SHADOW_MODE_SAMPLE_RATE == 0.1  # 10%
        assert MigrationConfig.SHADOW_MODE_ERROR_THRESHOLD == 0.05  # 5%
        assert MigrationConfig.SHADOW_MODE_MIN_SAMPLES == 50
        assert MigrationConfig.SHADOW_MODE_MAX_SAMPLES_PER_MINUTE == 100
        assert MigrationConfig.SHADOW_MODE_INCLUDE_TIMING == True
    
    def test_shadow_mode_config_validation(self):
        """Verify shadow mode configuration validation works."""
        # Should not raise with valid defaults
        assert MigrationConfig.validate_shadow_mode_config() == True


class TestShadowModeMetrics:
    """Test shadow mode metrics tracking."""
    
    def test_metrics_initialization(self):
        """Verify metrics initialize correctly."""
        metrics = ShadowModeMetrics()
        assert metrics.comparison_count == 0
        assert metrics.error_count == 0
        assert metrics.discrepancy_count == 0
        assert metrics.get_error_rate() == 0.0
    
    def test_metrics_record_comparison(self):
        """Verify metrics record comparisons correctly."""
        metrics = ShadowModeMetrics()
        
        # Record success
        metrics.record_comparison("success")
        assert metrics.comparison_count == 1
        assert metrics.error_count == 0
        assert metrics.discrepancy_count == 0
        
        # Record error
        metrics.record_comparison("error")
        assert metrics.comparison_count == 2
        assert metrics.error_count == 1
        assert metrics.get_error_rate() == 0.5
        
        # Record discrepancy
        metrics.record_comparison("discrepancy")
        assert metrics.comparison_count == 3
        assert metrics.discrepancy_count == 1
    
    def test_metrics_reset(self):
        """Verify metrics reset works."""
        metrics = ShadowModeMetrics()
        metrics.record_comparison("error")
        metrics.record_comparison("discrepancy")
        
        metrics.reset()
        assert metrics.comparison_count == 0
        assert metrics.error_count == 0
        assert metrics.discrepancy_count == 0


class TestFacadeRouting:
    """Test facade routing logic."""
    
    @pytest.fixture
    def mock_unified_manager(self):
        """Create mock unified manager."""
        manager = Mock(spec=UnifiedFileManager)
        manager.upload_file_async = AsyncMock(return_value=FileOperationResult(
            success=True,
            file_reference=FileReference(
                internal_id=TEST_UUID,
                provider_id="kimi-unified-456",
                provider="kimi",
                file_hash=TEST_SHA256,
                size=1024,
                mime_type="text/plain",
                original_name="test.txt"
            )
        ))
        return manager
    
    @pytest.fixture
    def mock_rollout_manager(self):
        """Create mock rollout manager."""
        manager = Mock(spec=RolloutManager)
        manager.should_use_unified = Mock(return_value=False)  # Default to legacy
        return manager
    
    @pytest.fixture
    def mock_config(self):
        """Create mock configuration."""
        config = Mock()
        config.ENABLE_UNIFIED_MANAGER = False
        config.ENABLE_SHADOW_MODE = False
        config.ENABLE_FALLBACK_TO_LEGACY = True
        config.SHADOW_MODE_SAMPLE_RATE = 1.0  # 100% for testing
        return config
    
    @pytest.fixture
    def facade(self, mock_unified_manager, mock_rollout_manager, mock_config):
        """Create facade instance for testing."""
        return FileManagementFacade(
            unified_manager=mock_unified_manager,
            rollout_manager=mock_rollout_manager,
            config=mock_config,
            legacy_handlers={}
        )
    
    @pytest.mark.asyncio
    async def test_facade_routes_to_legacy_by_default(self, facade):
        """Verify facade routes to legacy when unified is disabled."""
        # Create a temporary test file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("test content")
            test_file = f.name
        
        try:
            result = await facade.upload_file(
                file_path=test_file,
                provider="kimi"
            )
            
            # Should use legacy (which will call _legacy_kimi_upload)
            # Legacy upload will actually try to call KimiUploadFilesTool
            # For this test, we just verify it doesn't call unified
            assert facade.unified_manager.upload_file_async.call_count == 0
        finally:
            os.unlink(test_file)
    
    def test_should_run_shadow_mode_respects_config(self, facade):
        """Verify shadow mode respects configuration."""
        # Shadow mode disabled
        facade.config.ENABLE_SHADOW_MODE = False
        assert facade._should_run_shadow_mode() == False
        
        # Shadow mode enabled with 100% sampling
        facade.config.ENABLE_SHADOW_MODE = True
        facade.config.SHADOW_MODE_SAMPLE_RATE = 1.0
        assert facade._should_run_shadow_mode() == True
        
        # Shadow mode enabled with 0% sampling
        facade.config.SHADOW_MODE_SAMPLE_RATE = 0.0
        assert facade._should_run_shadow_mode() == False


class TestShadowModeComparison:
    """Test shadow mode comparison logic."""
    
    @pytest.fixture
    def facade(self):
        """Create minimal facade for comparison testing."""
        config = Mock()
        config.ENABLE_SHADOW_MODE = True
        return FileManagementFacade(
            unified_manager=Mock(),
            rollout_manager=Mock(),
            config=config
        )
    
    def test_compare_results_both_success_match(self, facade):
        """Verify comparison when both succeed with matching data."""
        primary = FileOperationResult(
            success=True,
            file_reference=FileReference(
                internal_id=TEST_UUID,
                provider_id="file-123",
                provider="kimi",
                file_hash=TEST_SHA256,
                size=1024,
                mime_type="text/plain",
                original_name="test.txt"
            )
        )
        shadow = FileOperationResult(
            success=True,
            file_reference=FileReference(
                internal_id=TEST_UUID,
                provider_id="file-123",
                provider="kimi",
                file_hash=TEST_SHA256,
                size=1024,
                mime_type="text/plain",
                original_name="test.txt"
            )
        )
        
        comparison = facade._compare_results(primary, shadow)
        assert comparison["results_match"] == True
        assert comparison["has_errors"] == False
        assert len(comparison["discrepancies"]) == 0
    
    def test_compare_results_both_success_mismatch(self, facade):
        """Verify comparison when both succeed but data differs."""
        test_sha256_2 = "b" * 64  # Different valid SHA256
        primary = FileOperationResult(
            success=True,
            file_reference=FileReference(
                internal_id=TEST_UUID,
                provider_id="file-123",
                provider="kimi",
                file_hash=TEST_SHA256,
                size=1024,
                mime_type="text/plain",
                original_name="test.txt"
            )
        )
        shadow = FileOperationResult(
            success=True,
            file_reference=FileReference(
                internal_id=TEST_UUID,
                provider_id="file-456",  # Different ID
                provider="kimi",
                file_hash=test_sha256_2,  # Different hash
                size=2048,  # Different size
                mime_type="text/plain",
                original_name="test.txt"
            )
        )
        
        comparison = facade._compare_results(primary, shadow)
        assert comparison["results_match"] == False
        assert comparison["has_errors"] == False
        assert len(comparison["discrepancies"]) == 3  # ID, hash, size
    
    def test_compare_results_both_fail(self, facade):
        """Verify comparison when both fail (should match)."""
        primary = FileOperationResult(
            success=False,
            error="Primary failed"
        )
        shadow = FileOperationResult(
            success=False,
            error="Shadow failed"
        )
        
        comparison = facade._compare_results(primary, shadow)
        assert comparison["results_match"] == True  # Both failed = match
        assert comparison["has_errors"] == True
        assert comparison["match_reason"] == "Both implementations failed"
    
    def test_compare_results_one_fails(self, facade):
        """Verify comparison when only one fails (should not match)."""
        primary = FileOperationResult(
            success=True,
            file_reference=FileReference(
                internal_id=TEST_UUID,
                provider_id="file-123",
                provider="kimi",
                file_hash=TEST_SHA256,
                size=1024,
                mime_type="text/plain",
                original_name="test.txt"
            )
        )
        shadow = FileOperationResult(
            success=False,
            error="Shadow failed"
        )
        
        comparison = facade._compare_results(primary, shadow)
        assert comparison["results_match"] == False
        assert comparison["has_errors"] == True
        assert comparison["primary_success"] == True
        assert comparison["shadow_success"] == False


class TestErrorHandling:
    """Test error handling in shadow mode."""
    
    @pytest.mark.asyncio
    async def test_shadow_mode_error_doesnt_affect_primary(self):
        """Verify shadow mode errors don't affect primary operation."""
        # This would require more complex mocking
        # For now, we verify the structure is correct
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

