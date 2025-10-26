"""
Unit tests for Supabase Storage Manager upload optimization.

Phase C Step 4: Tests for retry logic, progress tracking, and error handling.

Date: 2025-10-22
"""

import pytest
import io
import time
from unittest.mock import Mock, patch, MagicMock, call
from src.storage.supabase_client import (
    SupabaseStorageManager,
    RetryableError,
    NonRetryableError,
    ProgressTracker
)


class TestProgressTracker:
    """Test suite for ProgressTracker class."""
    
    def test_progress_tracker_with_callback(self):
        """Test progress tracking with callback"""
        progress_updates = []
        
        def callback(transferred, total, percentage):
            progress_updates.append((transferred, total, percentage))
        
        tracker = ProgressTracker(callback, throttle_interval=0.1)
        
        # First update should go through
        tracker.update(100, 1000)
        assert len(progress_updates) == 1
        assert progress_updates[0] == (100, 1000, 10.0)
        
        # Immediate second update should be throttled
        tracker.update(200, 1000)
        assert len(progress_updates) == 1  # Still 1, throttled
        
        # Wait for throttle interval
        time.sleep(0.15)
        tracker.update(300, 1000)
        assert len(progress_updates) == 2
        assert progress_updates[1] == (300, 1000, 30.0)
    
    def test_progress_tracker_without_callback(self):
        """Test progress tracking without callback (should not error)"""
        tracker = ProgressTracker(None)
        tracker.update(100, 1000)  # Should not raise exception
    
    def test_progress_tracker_callback_exception(self):
        """Test progress tracking handles callback exceptions"""
        def failing_callback(transferred, total, percentage):
            raise Exception("Callback failed")
        
        tracker = ProgressTracker(failing_callback)
        tracker.update(100, 1000)  # Should not raise exception


class TestErrorClassification:
    """Test suite for error classification."""
    
    @pytest.fixture
    def storage_manager(self):
        with patch('src.storage.supabase_client.create_client'):
            manager = SupabaseStorageManager()
            return manager
    
    def test_classify_network_errors(self, storage_manager):
        """Test classification of network errors as retryable"""
        network_errors = [
            Exception("Connection timeout"),
            Exception("Network error occurred"),
            Exception("HTTP 500 Internal Server Error"),
            Exception("Service unavailable"),
        ]
        
        for error in network_errors:
            is_retryable, category = storage_manager._classify_error(error)
            assert is_retryable is True
            assert category == "network"
    
    def test_classify_auth_errors(self, storage_manager):
        """Test classification of auth errors as non-retryable"""
        auth_errors = [
            Exception("Unauthorized access"),
            Exception("Invalid API key"),
            Exception("JWT token expired"),
        ]
        
        for error in auth_errors:
            is_retryable, category = storage_manager._classify_error(error)
            assert is_retryable is False
            assert category == "authentication"
    
    def test_classify_quota_errors(self, storage_manager):
        """Test classification of quota errors as non-retryable"""
        quota_errors = [
            Exception("Storage quota exceeded"),
            Exception("File size limit reached"),
        ]
        
        for error in quota_errors:
            is_retryable, category = storage_manager._classify_error(error)
            assert is_retryable is False
            assert category == "quota"
    
    def test_classify_unknown_errors(self, storage_manager):
        """Test classification of unknown errors as retryable (default)"""
        unknown_error = Exception("Something went wrong")
        is_retryable, category = storage_manager._classify_error(unknown_error)
        assert is_retryable is True
        assert category == "unknown"


class TestRetryLogic:
    """Test suite for retry logic."""
    
    @pytest.fixture
    def storage_manager(self):
        with patch('src.storage.supabase_client.create_client'):
            manager = SupabaseStorageManager()
            return manager
    
    def test_retry_success_on_first_attempt(self, storage_manager):
        """Test successful execution on first attempt"""
        mock_func = Mock(return_value="success")
        
        result = storage_manager._retry_with_backoff(mock_func, max_retries=3)
        
        assert result == "success"
        assert mock_func.call_count == 1
    
    def test_retry_success_after_failures(self, storage_manager):
        """Test successful execution after retries"""
        mock_func = Mock(side_effect=[
            Exception("Network timeout"),
            Exception("Connection error"),
            "success"
        ])
        
        result = storage_manager._retry_with_backoff(mock_func, max_retries=3)
        
        assert result == "success"
        assert mock_func.call_count == 3
    
    def test_retry_max_retries_exceeded(self, storage_manager):
        """Test max retries exceeded"""
        mock_func = Mock(side_effect=Exception("Network timeout"))
        
        with pytest.raises(RetryableError):
            storage_manager._retry_with_backoff(mock_func, max_retries=2)
        
        assert mock_func.call_count == 3  # Initial + 2 retries
    
    def test_retry_non_retryable_error(self, storage_manager):
        """Test non-retryable error stops retries"""
        mock_func = Mock(side_effect=Exception("Invalid API key"))
        
        with pytest.raises(NonRetryableError):
            storage_manager._retry_with_backoff(mock_func, max_retries=3)
        
        assert mock_func.call_count == 1  # No retries for non-retryable errors


class TestUploadFileOptimization:
    """Test suite for optimized upload_file method."""
    
    @pytest.fixture
    def storage_manager(self):
        with patch('src.storage.supabase_client.create_client'):
            manager = SupabaseStorageManager()
            manager._enabled = True
            return manager
    
    @pytest.fixture
    def mock_client(self, storage_manager):
        mock = MagicMock()
        storage_manager.get_client = Mock(return_value=mock)
        return mock
    
    def test_upload_with_bytes(self, storage_manager, mock_client):
        """Test upload using bytes (backward compatibility)"""
        file_data = b"test content"
        
        with patch.object(storage_manager, '_check_file_exists') as mock_check:
            mock_check.return_value = None
            mock_client.storage.from_.return_value.upload.return_value = {"path": "test.txt"}
            mock_client.table.return_value.insert.return_value.execute.return_value.data = [{"id": "test-id"}]
            
            result = storage_manager.upload_file(
                file_path="test.txt",
                file_data=file_data,
                original_name="test.txt"
            )
            
            assert result == "test-id"
            mock_client.storage.from_.return_value.upload.assert_called_once()
    
    def test_upload_with_file_object(self, storage_manager, mock_client):
        """Test upload using file object"""
        file_obj = io.BytesIO(b"test content")
        
        with patch.object(storage_manager, '_check_file_exists') as mock_check:
            mock_check.return_value = None
            mock_client.storage.from_.return_value.upload.return_value = {"path": "test.txt"}
            mock_client.table.return_value.insert.return_value.execute.return_value.data = [{"id": "test-id"}]
            
            result = storage_manager.upload_file(
                file_path="test.txt",
                file_obj=file_obj,
                original_name="test.txt"
            )
            
            assert result == "test-id"
    
    def test_upload_with_progress_callback(self, storage_manager, mock_client):
        """Test upload with progress callback"""
        progress_updates = []
        
        def progress_callback(transferred, total, percentage):
            progress_updates.append((transferred, total, percentage))
        
        file_data = b"test content"
        
        with patch.object(storage_manager, '_check_file_exists') as mock_check:
            mock_check.return_value = None
            mock_client.storage.from_.return_value.upload.return_value = {"path": "test.txt"}
            mock_client.table.return_value.insert.return_value.execute.return_value.data = [{"id": "test-id"}]
            
            result = storage_manager.upload_file(
                file_path="test.txt",
                file_data=file_data,
                original_name="test.txt",
                progress_callback=progress_callback
            )
            
            assert result == "test-id"
            # Should have at least initial and final progress updates
            assert len(progress_updates) >= 1
    
    def test_upload_existing_file(self, storage_manager, mock_client):
        """Test upload of existing file (deduplication)"""
        file_data = b"test content"
        
        with patch.object(storage_manager, '_check_file_exists') as mock_check:
            mock_check.return_value = "existing-id"
            
            result = storage_manager.upload_file(
                file_path="test.txt",
                file_data=file_data,
                original_name="test.txt"
            )
            
            assert result == "existing-id"
            # Should not call upload if file exists
            mock_client.storage.from_.return_value.upload.assert_not_called()
    
    def test_upload_race_condition(self, storage_manager, mock_client):
        """Test handling of upload race condition"""
        file_data = b"test content"
        
        with patch.object(storage_manager, '_check_file_exists') as mock_check:
            # First check: file doesn't exist
            # Second check (after race condition): file exists
            mock_check.side_effect = [None, "race-condition-id"]
            
            # Simulate duplicate error
            mock_client.storage.from_.return_value.upload.side_effect = Exception("Duplicate file")
            
            result = storage_manager.upload_file(
                file_path="test.txt",
                file_data=file_data,
                original_name="test.txt"
            )
            
            assert result == "race-condition-id"
            assert mock_check.call_count == 2
    
    def test_upload_validation_errors(self, storage_manager):
        """Test input validation"""
        # No file_data or file_obj
        result = storage_manager.upload_file(
            file_path="test.txt",
            original_name="test.txt"
        )
        assert result is None
        
        # Both file_data and file_obj
        result = storage_manager.upload_file(
            file_path="test.txt",
            file_data=b"test",
            file_obj=io.BytesIO(b"test"),
            original_name="test.txt"
        )
        assert result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

