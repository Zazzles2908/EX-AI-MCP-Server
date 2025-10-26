"""
Test Missing Handlers Implementation

Tests for the newly implemented delete_file() method in SupabaseStorageManager
and the _legacy_download() and _legacy_delete() methods in FileManagementFacade.

Phase 2.4.1 - Task 1: Implement Missing Handlers
Date: 2025-10-22
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
from src.storage.supabase_client import SupabaseStorageManager
from src.file_management.migration_facade import FileManagementFacade
from src.file_management.models import FileOperationResult


class TestSupabaseStorageManagerDeleteFile:
    """Test delete_file() method in SupabaseStorageManager"""
    
    def test_delete_file_disabled(self):
        """Test delete_file when Supabase is disabled"""
        with patch.object(SupabaseStorageManager, '_enabled', False):
            manager = SupabaseStorageManager()
            result = manager.delete_file("test-file-id")
            assert result is False
    
    @patch('src.storage.supabase_client.SupabaseStorageManager.get_client')
    def test_delete_file_not_found(self, mock_get_client):
        """Test delete_file when file not found in database"""
        # Mock client
        mock_client = MagicMock()
        mock_client.table().select().eq().execute.return_value = MagicMock(data=[])
        mock_get_client.return_value = mock_client
        
        manager = SupabaseStorageManager()
        result = manager.delete_file("nonexistent-file-id")
        
        # Should return True (consider already deleted as success)
        assert result is True
    
    @patch('src.storage.supabase_client.SupabaseStorageManager.get_client')
    def test_delete_file_success(self, mock_get_client):
        """Test successful file deletion"""
        # Mock client
        mock_client = MagicMock()
        
        # Mock file record
        file_data = {
            "id": "test-file-id",
            "storage_path": "test/path/file.txt",
            "file_type": "user_upload"
        }
        mock_client.table().select().eq().execute.return_value = MagicMock(data=[file_data])
        
        # Mock storage deletion
        mock_client.storage.from_().remove.return_value = None
        
        # Mock database deletion
        mock_client.table().delete().eq().execute.return_value = MagicMock(data=[file_data])
        
        mock_get_client.return_value = mock_client
        
        manager = SupabaseStorageManager()
        result = manager.delete_file("test-file-id")
        
        assert result is True
    
    @patch('src.storage.supabase_client.SupabaseStorageManager.get_client')
    def test_delete_file_storage_failure_continues(self, mock_get_client):
        """Test that database deletion continues even if storage deletion fails"""
        # Mock client
        mock_client = MagicMock()
        
        # Mock file record
        file_data = {
            "id": "test-file-id",
            "storage_path": "test/path/file.txt",
            "file_type": "user_upload"
        }
        mock_client.table().select().eq().execute.return_value = MagicMock(data=[file_data])
        
        # Mock storage deletion failure (non-retryable)
        mock_client.storage.from_().remove.side_effect = Exception("Storage error")
        
        # Mock database deletion success
        mock_client.table().delete().eq().execute.return_value = MagicMock(data=[file_data])
        
        mock_get_client.return_value = mock_client
        
        manager = SupabaseStorageManager()
        
        # Mock _classify_error to return non-retryable
        with patch.object(manager, '_classify_error', return_value=(False, "storage_error")):
            result = manager.delete_file("test-file-id")
        
        # Should still succeed (database deletion succeeded)
        assert result is True


class TestFileManagementFacadeLegacyHandlers:
    """Test _legacy_download() and _legacy_delete() methods in FileManagementFacade"""
    
    @pytest.mark.asyncio
    async def test_legacy_download_file_not_found(self):
        """Test _legacy_download when file not found"""
        facade = FileManagementFacade()
        
        with patch('src.storage.supabase_client.SupabaseStorageManager.get_client') as mock_get_client:
            mock_client = MagicMock()
            mock_client.table().select().eq().execute.return_value = MagicMock(data=[])
            mock_get_client.return_value = mock_client
            
            result = await facade._legacy_download("nonexistent-file-id", None)
            
            assert result.success is False
            assert "not found" in result.error.lower()
    
    @pytest.mark.asyncio
    async def test_legacy_download_success(self):
        """Test successful _legacy_download"""
        facade = FileManagementFacade()
        
        with patch('src.storage.supabase_client.SupabaseStorageManager.get_client') as mock_get_client:
            with patch('src.storage.supabase_client.SupabaseStorageManager.download_file') as mock_download:
                # Mock file metadata
                file_data = {
                    "id": "test-file-id",
                    "storage_path": "test/path/file.txt",
                    "original_name": "file.txt",
                    "size_bytes": 1024
                }
                
                mock_client = MagicMock()
                mock_client.table().select().eq().execute.return_value = MagicMock(data=[file_data])
                mock_get_client.return_value = mock_client
                
                # Mock download
                mock_download.return_value = b"test file content"
                
                result = await facade._legacy_download("test-file-id", None)
                
                assert result.success is True
                assert result.metadata["file_id"] == "test-file-id"
    
    @pytest.mark.asyncio
    async def test_legacy_delete_file_not_found(self):
        """Test _legacy_delete when file not found"""
        facade = FileManagementFacade()
        
        with patch('src.storage.supabase_client.SupabaseStorageManager.get_client') as mock_get_client:
            mock_client = MagicMock()
            mock_client.table().select().eq().execute.return_value = MagicMock(data=[])
            mock_get_client.return_value = mock_client
            
            result = await facade._legacy_delete("nonexistent-file-id")
            
            assert result.success is False
            assert "not found" in result.error.lower()
    
    @pytest.mark.asyncio
    async def test_legacy_delete_success(self):
        """Test successful _legacy_delete"""
        facade = FileManagementFacade()
        
        with patch('src.storage.supabase_client.SupabaseStorageManager.get_client') as mock_get_client:
            with patch('src.storage.supabase_client.SupabaseStorageManager.delete_file') as mock_delete:
                # Mock file metadata
                file_data = {
                    "id": "test-file-id",
                    "storage_path": "test/path/file.txt"
                }
                
                mock_client = MagicMock()
                mock_client.table().select().eq().execute.return_value = MagicMock(data=[file_data])
                mock_get_client.return_value = mock_client
                
                # Mock delete
                mock_delete.return_value = True
                
                result = await facade._legacy_delete("test-file-id")
                
                assert result.success is True
                assert result.metadata["file_id"] == "test-file-id"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

