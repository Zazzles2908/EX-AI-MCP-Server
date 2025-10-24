"""
Unit tests for optimized file operations in HybridSupabaseManager.

Phase C Step 4: Tests for parallel uploads and progress tracking.

Date: 2025-10-22
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from src.storage.hybrid_supabase_manager import HybridSupabaseManager, HybridOperationResult


class TestFileOperationsOptimization:
    """Test suite for optimized file operations."""
    
    @pytest.fixture
    def manager(self):
        """Create HybridSupabaseManager instance for testing."""
        with patch('src.storage.hybrid_supabase_manager.SupabaseStorageManager'):
            manager = HybridSupabaseManager()
            return manager
    
    @pytest.fixture
    def mock_client(self, manager):
        """Create mock Supabase client."""
        mock = MagicMock()
        manager.python_client.get_client = Mock(return_value=mock)
        return mock
    
    # ========================================================================
    # UPLOAD WITH PROGRESS TRACKING TESTS
    # ========================================================================
    
    def test_upload_small_file_with_progress(self, manager, mock_client):
        """Test small file upload with progress callback."""
        # Arrange
        bucket = "test-bucket"
        path = "test/file.txt"
        file_data = b"Small file content"
        progress_calls = []
        
        def progress_callback(bytes_transferred, total_bytes, percentage):
            progress_calls.append((bytes_transferred, total_bytes, percentage))
        
        mock_client.storage.from_.return_value.upload.return_value = {"path": path}
        
        # Act
        result = manager.upload_file(
            bucket, path, file_data,
            progress_callback=progress_callback,
            use_parallel=False  # Force standard upload
        )
        
        # Assert
        assert result.success is True
        assert result.metadata["parallel"] is False
        assert len(progress_calls) == 2  # Initial + completion
        assert progress_calls[0] == (0, len(file_data), 0.0)
        assert progress_calls[1] == (len(file_data), len(file_data), 100.0)
    
    def test_upload_without_progress_callback(self, manager, mock_client):
        """Test upload without progress callback."""
        # Arrange
        bucket = "test-bucket"
        path = "test/file.txt"
        file_data = b"File content"
        
        mock_client.storage.from_.return_value.upload.return_value = {"path": path}
        
        # Act
        result = manager.upload_file(bucket, path, file_data, use_parallel=False)
        
        # Assert
        assert result.success is True
        assert result.metadata["size"] == len(file_data)
        assert result.metadata["parallel"] is False
    
    # ========================================================================
    # PARALLEL UPLOAD TESTS
    # ========================================================================
    
    def test_parallel_upload_large_file(self, manager, mock_client):
        """Test parallel upload for large file."""
        # Arrange
        bucket = "test-bucket"
        path = "test/large-file.bin"
        file_data = b"X" * (15 * 1024 * 1024)  # 15MB file
        progress_calls = []
        
        def progress_callback(bytes_transferred, total_bytes, percentage):
            progress_calls.append((bytes_transferred, total_bytes, percentage))
        
        mock_client.storage.from_.return_value.upload.return_value = {"path": path}
        mock_client.storage.from_.return_value.remove.return_value = None
        
        # Act
        result = manager.upload_file(
            bucket, path, file_data,
            progress_callback=progress_callback,
            use_parallel=True,
            chunk_size=5 * 1024 * 1024,  # 5MB chunks
            max_workers=2
        )
        
        # Assert
        assert result.success is True
        assert result.metadata["parallel"] is True
        assert result.metadata["num_chunks"] == 3  # 15MB / 5MB = 3 chunks
        assert result.metadata["workers"] == 2
        assert len(progress_calls) > 0  # Should have progress updates
    
    def test_parallel_upload_disabled_for_small_file(self, manager, mock_client):
        """Test that parallel upload is disabled for small files."""
        # Arrange
        bucket = "test-bucket"
        path = "test/small-file.txt"
        file_data = b"X" * (5 * 1024 * 1024)  # 5MB file (below 10MB threshold)
        
        mock_client.storage.from_.return_value.upload.return_value = {"path": path}
        
        # Act
        result = manager.upload_file(
            bucket, path, file_data,
            use_parallel=True  # Requested but won't be used
        )
        
        # Assert
        assert result.success is True
        assert result.metadata["parallel"] is False  # Falls back to standard upload
    
    def test_parallel_upload_progress_tracking(self, manager, mock_client):
        """Test progress tracking during parallel upload."""
        # Arrange
        bucket = "test-bucket"
        path = "test/large-file.bin"
        file_data = b"X" * (12 * 1024 * 1024)  # 12MB file
        progress_calls = []
        
        def progress_callback(bytes_transferred, total_bytes, percentage):
            progress_calls.append({
                "bytes": bytes_transferred,
                "total": total_bytes,
                "percent": percentage
            })
        
        mock_client.storage.from_.return_value.upload.return_value = {"path": path}
        mock_client.storage.from_.return_value.remove.return_value = None
        
        # Act
        result = manager.upload_file(
            bucket, path, file_data,
            progress_callback=progress_callback,
            use_parallel=True,
            chunk_size=4 * 1024 * 1024,  # 4MB chunks
            max_workers=3
        )
        
        # Assert
        assert result.success is True
        assert len(progress_calls) > 0
        # First call should be initial progress
        assert progress_calls[0]["bytes"] == 0
        assert progress_calls[0]["percent"] == 0.0
        # Progress should increase
        assert any(call["percent"] > 0 for call in progress_calls)
    
    # ========================================================================
    # DOWNLOAD WITH PROGRESS TRACKING TESTS
    # ========================================================================
    
    def test_download_with_progress(self, manager):
        """Test file download with progress callback."""
        # Arrange
        file_id = "test-file-id"
        file_data = b"Downloaded file content"
        progress_calls = []
        
        def progress_callback(bytes_transferred, total_bytes, percentage):
            progress_calls.append((bytes_transferred, total_bytes, percentage))
        
        manager.python_client.download_file = Mock(return_value=file_data)
        
        # Act
        result = manager.download_file(file_id, progress_callback=progress_callback)
        
        # Assert
        assert result.success is True
        assert result.data == file_data
        assert len(progress_calls) == 2  # Initial + completion
        assert progress_calls[0] == (0, 0, 0.0)
        assert progress_calls[1] == (len(file_data), len(file_data), 100.0)
    
    def test_download_without_progress_callback(self, manager):
        """Test download without progress callback."""
        # Arrange
        file_id = "test-file-id"
        file_data = b"File content"
        
        manager.python_client.download_file = Mock(return_value=file_data)
        
        # Act
        result = manager.download_file(file_id)
        
        # Assert
        assert result.success is True
        assert result.data == file_data
        assert result.metadata["size"] == len(file_data)
    
    def test_download_file_not_found(self, manager):
        """Test download when file doesn't exist."""
        # Arrange
        file_id = "nonexistent-file"
        manager.python_client.download_file = Mock(return_value=None)
        
        # Act
        result = manager.download_file(file_id)
        
        # Assert
        assert result.success is False
        assert "not found" in result.error
        assert result.metadata["file_id"] == file_id
    
    def test_download_error_handling(self, manager):
        """Test download error handling."""
        # Arrange
        file_id = "error-file"
        manager.python_client.download_file = Mock(
            side_effect=Exception("Network error")
        )
        
        # Act
        result = manager.download_file(file_id)
        
        # Assert
        assert result.success is False
        assert "Network error" in result.error
        assert result.metadata["file_id"] == file_id
    
    # ========================================================================
    # UPLOAD ERROR HANDLING TESTS
    # ========================================================================
    
    def test_upload_error_handling(self, manager, mock_client):
        """Test upload error handling."""
        # Arrange
        bucket = "test-bucket"
        path = "test/file.txt"
        file_data = b"File content"
        
        mock_client.storage.from_.return_value.upload.side_effect = Exception(
            "Upload failed"
        )
        
        # Act
        result = manager.upload_file(bucket, path, file_data, use_parallel=False)
        
        # Assert
        assert result.success is False
        assert "Upload failed" in result.error
        assert result.metadata["bucket"] == bucket
        assert result.metadata["path"] == path
    
    def test_parallel_upload_error_handling(self, manager, mock_client):
        """Test parallel upload error handling."""
        # Arrange
        bucket = "test-bucket"
        path = "test/large-file.bin"
        file_data = b"X" * (15 * 1024 * 1024)  # 15MB file
        
        mock_client.storage.from_.return_value.upload.side_effect = Exception(
            "Chunk upload failed"
        )
        
        # Act
        result = manager.upload_file(
            bucket, path, file_data,
            use_parallel=True
        )
        
        # Assert
        assert result.success is False
        assert "failed" in result.error.lower()
        assert result.metadata["bucket"] == bucket


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

