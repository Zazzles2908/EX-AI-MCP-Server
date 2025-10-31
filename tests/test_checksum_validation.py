"""
Tests for Checksum Validation System

Tests for ChecksumManager, ChecksumAlgorithm, and checksum generation/validation.
"""

import pytest
from src.monitoring.validation.checksum import (
    ChecksumManager,
    ChecksumAlgorithm,
    ChecksumResult,
    get_checksum_manager,
)


class TestChecksumAlgorithm:
    """Test ChecksumAlgorithm enum."""

    def test_crc32_algorithm(self):
        """Test CRC32 algorithm enum value."""
        assert ChecksumAlgorithm.CRC32.value == "crc32"

    def test_sha256_algorithm(self):
        """Test SHA256 algorithm enum value."""
        assert ChecksumAlgorithm.SHA256.value == "sha256"


class TestChecksumManager:
    """Test ChecksumManager functionality."""

    def setup_method(self):
        """Setup for each test."""
        ChecksumManager._instance = None
        ChecksumManager.reset_metrics()

    def test_singleton_pattern(self):
        """Test ChecksumManager singleton pattern."""
        manager1 = ChecksumManager()
        manager2 = ChecksumManager()
        assert manager1 is manager2

    def test_get_checksum_manager(self):
        """Test get_checksum_manager function."""
        manager = get_checksum_manager()
        assert isinstance(manager, ChecksumManager)

    def test_generate_crc32_checksum(self):
        """Test CRC32 checksum generation."""
        manager = ChecksumManager()
        event_data = {'key': 'value', 'number': 42}
        
        result = manager.generate_checksum(
            event_data,
            'test_event',
            ChecksumAlgorithm.CRC32,
        )
        
        assert result.algorithm == ChecksumAlgorithm.CRC32
        assert result.checksum is not None
        assert len(result.checksum) == 8  # CRC32 is 8 hex characters
        assert result.event_type == 'test_event'
        assert result.is_valid is None

    def test_generate_sha256_checksum(self):
        """Test SHA256 checksum generation."""
        manager = ChecksumManager()
        event_data = {'key': 'value', 'number': 42}
        
        result = manager.generate_checksum(
            event_data,
            'test_event',
            ChecksumAlgorithm.SHA256,
        )
        
        assert result.algorithm == ChecksumAlgorithm.SHA256
        assert result.checksum is not None
        assert len(result.checksum) == 64  # SHA256 is 64 hex characters
        assert result.event_type == 'test_event'

    def test_generate_checksum_default_algorithm(self):
        """Test checksum generation with default algorithm."""
        manager = ChecksumManager()
        event_data = {'key': 'value'}
        
        result = manager.generate_checksum(event_data, 'test_event')
        
        assert result.algorithm == ChecksumAlgorithm.CRC32

    def test_generate_checksum_with_sequence_id(self):
        """Test checksum generation with sequence ID."""
        manager = ChecksumManager()
        event_data = {'key': 'value'}
        
        result = manager.generate_checksum(
            event_data,
            'test_event',
            sequence_id=123,
        )
        
        assert result.sequence_id == 123

    def test_checksum_consistency(self):
        """Test that same data produces same checksum."""
        manager = ChecksumManager()
        event_data = {'key': 'value', 'number': 42}
        
        result1 = manager.generate_checksum(event_data, 'test_event')
        result2 = manager.generate_checksum(event_data, 'test_event')
        
        assert result1.checksum == result2.checksum

    def test_checksum_differs_for_different_data(self):
        """Test that different data produces different checksums."""
        manager = ChecksumManager()
        data1 = {'key': 'value1'}
        data2 = {'key': 'value2'}
        
        result1 = manager.generate_checksum(data1, 'test_event')
        result2 = manager.generate_checksum(data2, 'test_event')
        
        assert result1.checksum != result2.checksum

    def test_validate_checksum_success(self):
        """Test successful checksum validation."""
        manager = ChecksumManager()
        event_data = {'key': 'value'}
        
        # Generate checksum
        gen_result = manager.generate_checksum(
            event_data,
            'test_event',
            ChecksumAlgorithm.CRC32,
        )
        
        # Validate checksum
        val_result = manager.validate_checksum(
            event_data,
            gen_result.checksum,
            ChecksumAlgorithm.CRC32,
            'test_event',
        )
        
        assert val_result.is_valid is True
        assert val_result.error_message is None

    def test_validate_checksum_failure(self):
        """Test failed checksum validation."""
        manager = ChecksumManager()
        event_data = {'key': 'value'}
        
        # Validate with wrong checksum
        result = manager.validate_checksum(
            event_data,
            'wrongchecksum',
            ChecksumAlgorithm.CRC32,
            'test_event',
        )
        
        assert result.is_valid is False
        assert 'mismatch' in result.error_message.lower()

    def test_validate_checksum_with_sequence_id(self):
        """Test checksum validation with sequence ID."""
        manager = ChecksumManager()
        event_data = {'key': 'value'}
        
        gen_result = manager.generate_checksum(
            event_data,
            'test_event',
            sequence_id=456,
        )
        
        val_result = manager.validate_checksum(
            event_data,
            gen_result.checksum,
            ChecksumAlgorithm.CRC32,
            'test_event',
            sequence_id=456,
        )
        
        assert val_result.is_valid is True
        assert val_result.sequence_id == 456

    def test_get_algorithm_for_critical_category(self):
        """Test algorithm selection for critical category."""
        manager = ChecksumManager()
        algorithm = manager.get_algorithm_for_category('critical')
        assert algorithm == ChecksumAlgorithm.SHA256

    def test_get_algorithm_for_performance_category(self):
        """Test algorithm selection for performance category."""
        manager = ChecksumManager()
        algorithm = manager.get_algorithm_for_category('performance')
        assert algorithm == ChecksumAlgorithm.CRC32

    def test_get_algorithm_for_other_categories(self):
        """Test algorithm selection for other categories."""
        manager = ChecksumManager()
        
        for category in ['user_activity', 'system', 'debug']:
            algorithm = manager.get_algorithm_for_category(category)
            assert algorithm == ChecksumAlgorithm.CRC32

    def test_get_metrics(self):
        """Test getting checksum metrics."""
        manager = ChecksumManager()
        event_data = {'key': 'value'}
        
        # Generate some checksums
        manager.generate_checksum(event_data, 'test_event', ChecksumAlgorithm.CRC32)
        manager.generate_checksum(event_data, 'test_event', ChecksumAlgorithm.SHA256)
        
        metrics = manager.get_metrics()
        
        assert metrics['checksums_generated'] == 2
        assert metrics['algorithm_distribution']['crc32'] == 1
        assert metrics['algorithm_distribution']['sha256'] == 1

    def test_metrics_validation_failures(self):
        """Test metrics tracking validation failures."""
        manager = ChecksumManager()
        event_data = {'key': 'value'}
        
        # Generate and validate
        gen_result = manager.generate_checksum(event_data, 'test_event')
        manager.validate_checksum(
            event_data,
            'wrongchecksum',
            ChecksumAlgorithm.CRC32,
            'test_event',
        )
        
        metrics = manager.get_metrics()
        
        assert metrics['checksums_validated'] == 1
        assert metrics['validation_failures'] == 1
        assert metrics['validation_failure_rate'] == 1.0

    def test_flush_metrics(self):
        """Test flushing metrics returns current metrics."""
        manager = ChecksumManager()
        event_data = {'key': 'value'}

        manager.generate_checksum(event_data, 'test_event')

        metrics = manager.flush_metrics()

        assert metrics['checksums_generated'] >= 1
        assert 'algorithm_distribution' in metrics

    def test_checksum_result_to_dict(self):
        """Test ChecksumResult to_dict conversion."""
        manager = ChecksumManager()
        event_data = {'key': 'value'}
        
        result = manager.generate_checksum(
            event_data,
            'test_event',
            sequence_id=789,
        )
        
        result_dict = result.to_dict()
        
        assert result_dict['algorithm'] == 'crc32'
        assert result_dict['event_type'] == 'test_event'
        assert result_dict['sequence_id'] == 789
        assert 'timestamp' in result_dict
        assert 'checksum' in result_dict

    def test_invalid_event_data_serialization(self):
        """Test handling of non-serializable event data."""
        manager = ChecksumManager()
        
        # Create non-serializable object
        class NonSerializable:
            pass
        
        event_data = {'key': NonSerializable()}
        
        with pytest.raises(ValueError):
            manager.generate_checksum(event_data, 'test_event')

    def test_complex_nested_data(self):
        """Test checksum generation with complex nested data."""
        manager = ChecksumManager()
        event_data = {
            'level1': {
                'level2': {
                    'level3': [1, 2, 3, {'nested': 'value'}]
                }
            }
        }
        
        result = manager.generate_checksum(event_data, 'test_event')
        
        assert result.checksum is not None
        assert result.is_valid is None

    def test_empty_event_data(self):
        """Test checksum generation with empty event data."""
        manager = ChecksumManager()
        event_data = {}
        
        result = manager.generate_checksum(event_data, 'test_event')
        
        assert result.checksum is not None
        assert len(result.checksum) > 0

    def test_large_event_data(self):
        """Test checksum generation with large event data."""
        manager = ChecksumManager()
        event_data = {f'key_{i}': f'value_{i}' for i in range(1000)}
        
        result = manager.generate_checksum(event_data, 'test_event')
        
        assert result.checksum is not None
        assert result.is_valid is None

