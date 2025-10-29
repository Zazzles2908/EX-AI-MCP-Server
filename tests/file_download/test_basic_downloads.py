"""
Basic download functionality tests for SmartFileDownloadTool.
Tests Kimi provider downloads, fallback mechanisms, and concurrent protection.
"""

import pytest
import asyncio
import os
import time
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

# Import the tool
from tools.smart_file_download import SmartFileDownloadTool, _active_downloads


class TestBasicDownloads:
    """Test basic download functionality."""
    
    @pytest.mark.asyncio
    async def test_download_tool_initialization(self):
        """Test that SmartFileDownloadTool initializes correctly."""
        tool = SmartFileDownloadTool()
        
        assert tool is not None
        assert hasattr(tool, 'storage_manager')
        assert hasattr(tool, 'dedup_manager')
        assert hasattr(tool, 'moonshot_api_key')
        assert hasattr(tool, 'glm_api_key')
    
    @pytest.mark.asyncio
    async def test_path_validation_success(self):
        """Test path validation accepts valid paths."""
        tool = SmartFileDownloadTool()
        
        # Valid paths within /mnt/project/
        valid_paths = [
            "/mnt/project/downloads/",
            "/mnt/project/EX-AI-MCP-Server/downloads/",
            "/mnt/project/test/"
        ]
        
        for path in valid_paths:
            try:
                validated = tool._validate_destination(path)
                assert validated is not None
                assert "/mnt/project/" in validated
            except ValueError as e:
                pytest.fail(f"Valid path rejected: {path} - {e}")
    
    @pytest.mark.asyncio
    async def test_path_validation_failure(self):
        """Test path validation rejects invalid paths."""
        tool = SmartFileDownloadTool()
        
        # Invalid paths outside /mnt/project/
        invalid_paths = [
            "/etc/passwd",
            "/tmp/test",
            "../../../etc/passwd",
            "c:\\Windows\\System32"
        ]
        
        for path in invalid_paths:
            with pytest.raises(ValueError, match="must be within /mnt/project/"):
                tool._validate_destination(path)
    
    @pytest.mark.asyncio
    async def test_provider_determination_from_database(self):
        """Test provider determination from database."""
        tool = SmartFileDownloadTool()
        
        # Mock Supabase client
        mock_client = Mock()
        mock_client.table = Mock(return_value=mock_client)
        mock_client.select = Mock(return_value=mock_client)
        mock_client.eq = Mock(return_value=mock_client)
        mock_client.execute = Mock(return_value=Mock(data=[{
            "provider": "kimi"
        }]))
        
        tool.storage_manager.enabled = True
        tool.storage_manager.get_client = Mock(return_value=mock_client)
        
        provider = await tool._determine_provider("file_test_12345")
        assert provider == "kimi"
    
    @pytest.mark.asyncio
    async def test_provider_determination_from_pattern(self):
        """Test provider determination from file_id pattern."""
        tool = SmartFileDownloadTool()
        tool.storage_manager.enabled = False
        
        # Kimi pattern (starts with "file_" or long ID)
        provider = await tool._determine_provider("file_abc123xyz")
        assert provider == "kimi"
        
        # Long ID pattern
        provider = await tool._determine_provider("d40qan21ol7h6f177pt0")
        assert provider == "kimi"
    
    @pytest.mark.asyncio
    async def test_provider_fallback_for_glm(self):
        """Test fallback to Supabase for GLM files."""
        tool = SmartFileDownloadTool()
        
        # Mock database returning GLM provider
        mock_client = Mock()
        mock_client.table = Mock(return_value=mock_client)
        mock_client.select = Mock(return_value=mock_client)
        mock_client.eq = Mock(return_value=mock_client)
        mock_client.execute = Mock(return_value=Mock(data=[{
            "provider": "glm"
        }]))
        
        tool.storage_manager.enabled = True
        tool.storage_manager.get_client = Mock(return_value=mock_client)
        
        provider = await tool._determine_provider("glm_file_12345")
        assert provider == "supabase"  # Should fallback to Supabase
    
    @pytest.mark.asyncio
    async def test_concurrent_download_protection(self):
        """Test that concurrent downloads of same file are protected."""
        tool = SmartFileDownloadTool()
        
        # Clear active downloads
        _active_downloads.clear()
        
        # Mock the download process to take some time
        async def slow_download(*args, **kwargs):
            await asyncio.sleep(0.5)
            return "/mnt/project/downloads/test.txt"
        
        # Mock dependencies
        tool._validate_destination = Mock(return_value="/mnt/project/downloads/")
        tool._check_cache = AsyncMock(return_value=None)
        tool._determine_provider = AsyncMock(return_value="kimi")
        tool._download_from_kimi = AsyncMock(side_effect=slow_download)
        tool._verify_integrity = AsyncMock()
        tool._update_download_tracking = AsyncMock()
        
        # Start two concurrent downloads
        file_id = "file_concurrent_test"
        task1 = asyncio.create_task(tool.execute(file_id))
        await asyncio.sleep(0.1)  # Let first download start
        task2 = asyncio.create_task(tool.execute(file_id))
        
        # Wait for both to complete
        results = await asyncio.gather(task1, task2)
        
        # Both should succeed
        assert len(results) == 2
        assert all(r is not None for r in results)
        
        # But only one actual download should have occurred
        assert tool._download_from_kimi.call_count == 1
    
    @pytest.mark.asyncio
    async def test_integrity_verification_success(self):
        """Test successful integrity verification."""
        tool = SmartFileDownloadTool()
        
        # Create temp file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("test content")
            temp_file = f.name
        
        try:
            # Mock database to return expected hash
            expected_hash = tool.dedup_manager.calculate_sha256(temp_file)
            
            mock_client = Mock()
            mock_client.table = Mock(return_value=mock_client)
            mock_client.select = Mock(return_value=mock_client)
            mock_client.eq = Mock(return_value=mock_client)
            mock_client.execute = Mock(return_value=Mock(data=[{
                "sha256_hash": expected_hash
            }]))
            
            tool.storage_manager.enabled = True
            tool.storage_manager.get_client = Mock(return_value=mock_client)
            
            # Should not raise exception
            await tool._verify_integrity("file_test", temp_file)
            
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    @pytest.mark.asyncio
    async def test_integrity_verification_failure(self):
        """Test integrity verification detects corruption."""
        tool = SmartFileDownloadTool()
        
        # Create temp file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("test content")
            temp_file = f.name
        
        try:
            # Mock database to return different hash
            mock_client = Mock()
            mock_client.table = Mock(return_value=mock_client)
            mock_client.select = Mock(return_value=mock_client)
            mock_client.eq = Mock(return_value=mock_client)
            mock_client.execute = Mock(return_value=Mock(data=[{
                "sha256_hash": "wrong_hash_12345"
            }]))
            
            tool.storage_manager.enabled = True
            tool.storage_manager.get_client = Mock(return_value=mock_client)
            
            # Should raise ValueError
            with pytest.raises(ValueError, match="Hash mismatch"):
                await tool._verify_integrity("file_test", temp_file)
            
            # File should be deleted
            assert not os.path.exists(temp_file)
            
        except AssertionError:
            # Cleanup if test fails
            if os.path.exists(temp_file):
                os.unlink(temp_file)
            raise


class TestPerformanceMetrics:
    """Test performance tracking and metrics."""
    
    @pytest.mark.asyncio
    async def test_download_duration_tracking(self):
        """Test that download duration is tracked."""
        tool = SmartFileDownloadTool()
        
        # Mock dependencies
        tool._validate_destination = Mock(return_value="/mnt/project/downloads/")
        tool._check_cache = AsyncMock(return_value=None)
        tool._determine_provider = AsyncMock(return_value="kimi")
        
        # Mock download with known duration
        async def timed_download(*args, **kwargs):
            await asyncio.sleep(0.2)  # 200ms
            return "/mnt/project/downloads/test.txt"
        
        tool._download_from_kimi = AsyncMock(side_effect=timed_download)
        tool._verify_integrity = AsyncMock()
        
        # Track if tracking was called with duration
        tracking_called = False
        tracking_duration = None
        
        async def mock_tracking(*args, **kwargs):
            nonlocal tracking_called, tracking_duration
            tracking_called = True
            tracking_duration = kwargs.get('download_duration_ms', args[5] if len(args) > 5 else None)
        
        tool._update_download_tracking = AsyncMock(side_effect=mock_tracking)
        
        # Execute download
        start = time.time()
        await tool.execute("file_test")
        duration = (time.time() - start) * 1000
        
        # Verify tracking was called
        assert tracking_called
        assert tracking_duration is not None
        assert tracking_duration >= 200  # At least 200ms
        assert tracking_duration <= duration + 100  # Within reasonable range


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

