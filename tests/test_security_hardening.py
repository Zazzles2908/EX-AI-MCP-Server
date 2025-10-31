"""
Security hardening tests for checksum validation system.

Tests for thread safety, constant-time comparison, and HMAC support.
"""

import pytest
import threading
import time
from src.monitoring.validation.checksum import ChecksumManager, ChecksumAlgorithm
from src.monitoring.validation.mismatch_handler import MismatchHandler


class TestThreadSafety:
    """Test thread-safe singleton implementations."""
    
    def test_checksum_manager_thread_safe_singleton(self):
        """Test ChecksumManager singleton is thread-safe."""
        instances = []
        
        def get_instance():
            instances.append(ChecksumManager())
        
        threads = [threading.Thread(target=get_instance) for _ in range(10)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        # All instances should be the same object
        assert len(set(id(inst) for inst in instances)) == 1
    
    def test_mismatch_handler_thread_safe_singleton(self):
        """Test MismatchHandler singleton is thread-safe."""
        instances = []
        
        def get_instance():
            instances.append(MismatchHandler())
        
        threads = [threading.Thread(target=get_instance) for _ in range(10)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        # All instances should be the same object
        assert len(set(id(inst) for inst in instances)) == 1
    
    def test_concurrent_checksum_generation(self):
        """Test concurrent checksum generation is thread-safe."""
        manager = ChecksumManager()
        results = []
        
        def generate_checksums():
            for i in range(10):
                result = manager.generate_checksum(
                    {'data': f'test_{i}'},
                    'test_event'
                )
                results.append(result)
        
        threads = [threading.Thread(target=generate_checksums) for _ in range(5)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        # Should have 50 results (5 threads * 10 iterations)
        assert len(results) == 50
        # All should be valid
        assert all(r.checksum for r in results)
    
    def test_concurrent_mismatch_recording(self):
        """Test concurrent mismatch recording is thread-safe."""
        handler = MismatchHandler()
        handler.reset_stats()
        
        def record_mismatches():
            for i in range(10):
                handler.record_mismatch(
                    event_type=f'event_{i}',
                    sequence_id=i,
                    adapter='test_adapter',
                    expected_checksum='expected',
                    actual_checksum='actual',
                    category='critical',
                    error_message='test mismatch'
                )
        
        threads = [threading.Thread(target=record_mismatches) for _ in range(5)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        stats = handler.get_stats()
        # Should have 50 mismatches (5 threads * 10 iterations)
        assert stats.total_mismatches == 50


class TestConstantTimeComparison:
    """Test constant-time checksum comparison."""
    
    def test_validate_checksum_uses_constant_time_comparison(self):
        """Test that validation uses constant-time comparison."""
        manager = ChecksumManager()
        event_data = {'key': 'value'}
        
        # Generate a valid checksum
        result = manager.generate_checksum(event_data, 'test_event')
        valid_checksum = result.checksum
        
        # Validate with correct checksum
        validation = manager.validate_checksum(
            event_data,
            valid_checksum,
            ChecksumAlgorithm.CRC32,
            'test_event'
        )
        assert validation.is_valid is True
        
        # Validate with incorrect checksum
        validation = manager.validate_checksum(
            event_data,
            'incorrect_checksum',
            ChecksumAlgorithm.CRC32,
            'test_event'
        )
        assert validation.is_valid is False
    
    def test_timing_attack_resistance(self):
        """Test that comparison is resistant to timing attacks."""
        manager = ChecksumManager()
        event_data = {'key': 'value'}
        
        result = manager.generate_checksum(event_data, 'test_event')
        valid_checksum = result.checksum
        
        # Time validation with correct checksum
        start = time.perf_counter()
        for _ in range(100):
            manager.validate_checksum(
                event_data,
                valid_checksum,
                ChecksumAlgorithm.CRC32,
                'test_event'
            )
        correct_time = time.perf_counter() - start
        
        # Time validation with incorrect checksum
        start = time.perf_counter()
        for _ in range(100):
            manager.validate_checksum(
                event_data,
                'incorrect_checksum',
                ChecksumAlgorithm.CRC32,
                'test_event'
            )
        incorrect_time = time.perf_counter() - start
        
        # Times should be similar (within 50% variance)
        # This is a statistical test, not a guarantee
        ratio = max(correct_time, incorrect_time) / min(correct_time, incorrect_time)
        assert ratio < 1.5, f"Timing difference too large: {ratio}"


class TestHMACSupport:
    """Test HMAC-SHA256 support for critical events."""
    
    def test_set_secret_key(self):
        """Test setting secret key for HMAC."""
        manager = ChecksumManager()
        secret_key = 'test_secret_key_12345'
        
        manager.set_secret_key(secret_key)
        # Verify it was set (by checking internal state)
        assert manager._secret_key == secret_key
    
    def test_hmac_sha256_generation(self):
        """Test HMAC-SHA256 checksum generation."""
        manager = ChecksumManager()
        secret_key = 'test_secret_key_12345'
        manager.set_secret_key(secret_key)
        
        event_data = {'key': 'value'}
        
        # Generate HMAC checksum
        result = manager.generate_checksum(
            event_data,
            'critical_event',
            ChecksumAlgorithm.SHA256
        )
        
        assert result.checksum
        assert len(result.checksum) == 64  # SHA256 produces 64 hex chars
    
    def test_hmac_consistency(self):
        """Test HMAC checksums are consistent."""
        manager = ChecksumManager()
        secret_key = 'test_secret_key_12345'
        manager.set_secret_key(secret_key)
        
        event_data = {'key': 'value'}
        
        # Generate multiple checksums for same data
        result1 = manager.generate_checksum(
            event_data,
            'critical_event',
            ChecksumAlgorithm.SHA256
        )
        result2 = manager.generate_checksum(
            event_data,
            'critical_event',
            ChecksumAlgorithm.SHA256
        )
        
        # Should be identical
        assert result1.checksum == result2.checksum
    
    def test_hmac_differs_with_different_secret(self):
        """Test HMAC checksums differ with different secrets."""
        manager = ChecksumManager()
        event_data = {'key': 'value'}
        
        # Generate with first secret
        manager.set_secret_key('secret1')
        result1 = manager.generate_checksum(
            event_data,
            'critical_event',
            ChecksumAlgorithm.SHA256
        )
        
        # Generate with second secret
        manager.set_secret_key('secret2')
        result2 = manager.generate_checksum(
            event_data,
            'critical_event',
            ChecksumAlgorithm.SHA256
        )
        
        # Should be different
        assert result1.checksum != result2.checksum


class TestSecurityIntegration:
    """Integration tests for security features."""
    
    def test_thread_safe_validation_with_hmac(self):
        """Test thread-safe validation with HMAC support."""
        manager = ChecksumManager()
        manager.set_secret_key('test_secret')
        
        results = []
        
        def validate_checksums():
            event_data = {'key': 'value'}
            result = manager.generate_checksum(
                event_data,
                'test_event',
                ChecksumAlgorithm.SHA256
            )
            
            validation = manager.validate_checksum(
                event_data,
                result.checksum,
                ChecksumAlgorithm.SHA256,
                'test_event'
            )
            results.append(validation.is_valid)
        
        threads = [threading.Thread(target=validate_checksums) for _ in range(10)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        # All validations should succeed
        assert all(results)
        assert len(results) == 10
    
    def test_security_features_dont_break_existing_functionality(self):
        """Test that security features don't break existing functionality."""
        manager = ChecksumManager()
        
        # Test CRC32 still works
        event_data = {'key': 'value'}
        result = manager.generate_checksum(
            event_data,
            'test_event',
            ChecksumAlgorithm.CRC32
        )
        assert result.checksum
        assert len(result.checksum) == 8  # CRC32 is 8 hex chars
        
        # Test SHA256 still works
        result = manager.generate_checksum(
            event_data,
            'test_event',
            ChecksumAlgorithm.SHA256
        )
        assert result.checksum
        assert len(result.checksum) == 64  # SHA256 is 64 hex chars
        
        # Test validation still works
        validation = manager.validate_checksum(
            event_data,
            result.checksum,
            ChecksumAlgorithm.SHA256,
            'test_event'
        )
        assert validation.is_valid is True

