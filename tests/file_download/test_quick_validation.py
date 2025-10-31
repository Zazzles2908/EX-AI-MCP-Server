"""
Quick validation tests for SmartFileDownloadTool - Fast execution for rapid feedback.
"""

import pytest
import os
from tools.smart_file_download import SmartFileDownloadTool


class TestQuickValidation:
    """Quick validation tests."""
    
    def test_tool_initialization(self):
        """Test tool initializes without errors."""
        tool = SmartFileDownloadTool()
        assert tool is not None
        assert tool.storage_manager is not None
        assert tool.dedup_manager is not None
    
    def test_path_validation_rejects_invalid_paths(self):
        """Test path validation rejects paths outside /mnt/project/."""
        tool = SmartFileDownloadTool()
        
        invalid_paths = [
            "/etc/passwd",
            "/tmp/test",
            "../../../etc/passwd",
            "c:\\Windows\\System32",
            "/root/.ssh/id_rsa"
        ]
        
        for path in invalid_paths:
            with pytest.raises(ValueError, match="must be within /mnt/project/"):
                tool._validate_destination(path)
    
    def test_path_validation_accepts_valid_paths(self):
        """Test path validation accepts valid paths."""
        tool = SmartFileDownloadTool()
        
        valid_paths = [
            "/mnt/project/downloads/",
            "/mnt/project/EX-AI-MCP-Server/downloads/",
            "/mnt/project/test/"
        ]
        
        for path in valid_paths:
            validated = tool._validate_destination(path)
            assert validated is not None
            assert "/mnt/project/" in validated
    
    @pytest.mark.asyncio
    async def test_provider_determination_kimi_pattern(self):
        """Test provider determination recognizes Kimi patterns."""
        tool = SmartFileDownloadTool()
        tool.storage_manager.enabled = False  # Skip database lookup
        
        # Kimi patterns
        kimi_ids = [
            "file_abc123xyz",
            "d40qan21ol7h6f177pt0",
            "file_test_12345"
        ]
        
        for file_id in kimi_ids:
            provider = await tool._determine_provider(file_id)
            assert provider == "kimi", f"Failed for {file_id}"
    
    @pytest.mark.asyncio
    async def test_sha256_calculation(self):
        """Test SHA256 calculation works."""
        tool = SmartFileDownloadTool()
        
        # Create temp file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("test content for hashing")
            temp_file = f.name
        
        try:
            hash_value = tool.dedup_manager.calculate_sha256(temp_file)
            assert hash_value is not None
            assert len(hash_value) == 64  # SHA256 is 64 hex characters
            assert isinstance(hash_value, str)
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

