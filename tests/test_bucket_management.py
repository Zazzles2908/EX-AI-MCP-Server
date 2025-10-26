"""
Unit tests for bucket management operations in HybridSupabaseManager.

Phase C Step 3: Tests for autonomous bucket operations via Python Supabase client.

Date: 2025-10-22
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from src.storage.hybrid_supabase_manager import HybridSupabaseManager, HybridOperationResult


class TestBucketManagement:
    """Test suite for bucket management operations."""
    
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
    # LIST BUCKETS TESTS
    # ========================================================================
    
    def test_list_buckets_success(self, manager, mock_client):
        """Test successful bucket listing."""
        # Arrange
        expected_buckets = [
            {"id": "bucket1", "name": "uploads", "public": False},
            {"id": "bucket2", "name": "public-files", "public": True}
        ]
        mock_client.storage.list_buckets.return_value = expected_buckets
        
        # Act
        result = manager.list_buckets()
        
        # Assert
        assert result.success is True
        assert result.data == expected_buckets
        assert result.metadata["count"] == 2
        assert result.metadata["operation"] == "list_buckets"
        assert result.layer_used == "python"
        mock_client.storage.list_buckets.assert_called_once()
    
    def test_list_buckets_empty(self, manager, mock_client):
        """Test listing buckets when none exist."""
        # Arrange
        mock_client.storage.list_buckets.return_value = []
        
        # Act
        result = manager.list_buckets()
        
        # Assert
        assert result.success is True
        assert result.data == []
        assert result.metadata["count"] == 0
        assert result.layer_used == "python"
    
    def test_list_buckets_error(self, manager, mock_client):
        """Test bucket listing error handling."""
        # Arrange
        mock_client.storage.list_buckets.side_effect = Exception("Connection failed")
        
        # Act
        result = manager.list_buckets()
        
        # Assert
        assert result.success is False
        assert "Connection failed" in result.error
        assert result.metadata["operation"] == "list_buckets"
        assert result.layer_used == "python"
    
    # ========================================================================
    # CREATE BUCKET TESTS
    # ========================================================================
    
    def test_create_bucket_success(self, manager, mock_client):
        """Test successful bucket creation."""
        # Arrange
        bucket_name = "test-bucket"
        expected_result = {"id": "bucket-id", "name": bucket_name}
        mock_client.storage.create_bucket.return_value = expected_result
        
        # Act
        result = manager.create_bucket(bucket_name, public=False)
        
        # Assert
        assert result.success is True
        assert result.data == expected_result
        assert result.metadata["bucket_name"] == bucket_name
        assert result.metadata["public"] is False
        assert result.metadata["operation"] == "create_bucket"
        assert result.layer_used == "python"
        mock_client.storage.create_bucket.assert_called_once_with(
            bucket_name, 
            {"public": False}
        )
    
    def test_create_bucket_public(self, manager, mock_client):
        """Test creating a public bucket."""
        # Arrange
        bucket_name = "public-bucket"
        mock_client.storage.create_bucket.return_value = {"name": bucket_name}
        
        # Act
        result = manager.create_bucket(bucket_name, public=True)
        
        # Assert
        assert result.success is True
        assert result.metadata["public"] is True
        mock_client.storage.create_bucket.assert_called_once_with(
            bucket_name,
            {"public": True}
        )
    
    def test_create_bucket_with_options(self, manager, mock_client):
        """Test creating bucket with file size limit and MIME types."""
        # Arrange
        bucket_name = "restricted-bucket"
        file_size_limit = 5242880  # 5MB
        allowed_mime_types = ["image/jpeg", "image/png"]
        mock_client.storage.create_bucket.return_value = {"name": bucket_name}
        
        # Act
        result = manager.create_bucket(
            bucket_name,
            public=False,
            file_size_limit=file_size_limit,
            allowed_mime_types=allowed_mime_types
        )
        
        # Assert
        assert result.success is True
        mock_client.storage.create_bucket.assert_called_once_with(
            bucket_name,
            {
                "public": False,
                "file_size_limit": file_size_limit,
                "allowed_mime_types": allowed_mime_types
            }
        )
    
    def test_create_bucket_duplicate_error(self, manager, mock_client):
        """Test error when creating duplicate bucket."""
        # Arrange
        bucket_name = "existing-bucket"
        mock_client.storage.create_bucket.side_effect = Exception("Bucket already exists")
        
        # Act
        result = manager.create_bucket(bucket_name)
        
        # Assert
        assert result.success is False
        assert "already exists" in result.error
        assert result.metadata["bucket_name"] == bucket_name
        assert result.layer_used == "python"
    
    # ========================================================================
    # DELETE BUCKET TESTS
    # ========================================================================
    
    def test_delete_bucket_success(self, manager, mock_client):
        """Test successful bucket deletion."""
        # Arrange
        bucket_name = "old-bucket"
        mock_client.storage.delete_bucket.return_value = {"message": "Bucket deleted"}
        
        # Act
        result = manager.delete_bucket(bucket_name)
        
        # Assert
        assert result.success is True
        assert result.metadata["bucket_name"] == bucket_name
        assert result.metadata["operation"] == "delete_bucket"
        assert result.layer_used == "python"
        mock_client.storage.delete_bucket.assert_called_once_with(bucket_name)
    
    def test_delete_bucket_not_found(self, manager, mock_client):
        """Test error when deleting non-existent bucket."""
        # Arrange
        bucket_name = "nonexistent-bucket"
        mock_client.storage.delete_bucket.side_effect = Exception("Bucket not found")
        
        # Act
        result = manager.delete_bucket(bucket_name)
        
        # Assert
        assert result.success is False
        assert "not found" in result.error
        assert result.metadata["bucket_name"] == bucket_name
        assert result.layer_used == "python"
    
    # ========================================================================
    # EMPTY BUCKET TESTS
    # ========================================================================
    
    def test_empty_bucket_success(self, manager, mock_client):
        """Test successful bucket emptying."""
        # Arrange
        bucket_name = "full-bucket"
        mock_client.storage.empty_bucket.return_value = {"message": "Bucket emptied"}
        
        # Act
        result = manager.empty_bucket(bucket_name)
        
        # Assert
        assert result.success is True
        assert result.metadata["bucket_name"] == bucket_name
        assert result.metadata["operation"] == "empty_bucket"
        assert result.layer_used == "python"
        mock_client.storage.empty_bucket.assert_called_once_with(bucket_name)
    
    def test_empty_bucket_error(self, manager, mock_client):
        """Test error when emptying bucket."""
        # Arrange
        bucket_name = "protected-bucket"
        mock_client.storage.empty_bucket.side_effect = Exception("Permission denied")
        
        # Act
        result = manager.empty_bucket(bucket_name)
        
        # Assert
        assert result.success is False
        assert "Permission denied" in result.error
        assert result.metadata["bucket_name"] == bucket_name
        assert result.layer_used == "python"
    
    # ========================================================================
    # GET BUCKET TESTS
    # ========================================================================
    
    def test_get_bucket_success(self, manager, mock_client):
        """Test successful bucket info retrieval."""
        # Arrange
        bucket_name = "info-bucket"
        expected_info = {
            "id": "bucket-id",
            "name": bucket_name,
            "public": True,
            "file_size_limit": 1048576,
            "allowed_mime_types": ["image/*"]
        }
        mock_client.storage.get_bucket.return_value = expected_info
        
        # Act
        result = manager.get_bucket(bucket_name)
        
        # Assert
        assert result.success is True
        assert result.data == expected_info
        assert result.metadata["bucket_name"] == bucket_name
        assert result.metadata["operation"] == "get_bucket"
        assert result.layer_used == "python"
        mock_client.storage.get_bucket.assert_called_once_with(bucket_name)
    
    def test_get_bucket_not_found(self, manager, mock_client):
        """Test error when getting non-existent bucket."""
        # Arrange
        bucket_name = "missing-bucket"
        mock_client.storage.get_bucket.side_effect = Exception("Bucket not found")
        
        # Act
        result = manager.get_bucket(bucket_name)
        
        # Assert
        assert result.success is False
        assert "not found" in result.error
        assert result.metadata["bucket_name"] == bucket_name
        assert result.layer_used == "python"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

