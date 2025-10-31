"""
Shared test configuration and fixtures for file download system tests.
"""

import pytest
import asyncio
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
import logging

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)

# Test data directory
TEST_DATA_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_download_dir():
    """Create temporary download directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def mock_storage_manager():
    """Mock HybridSupabaseManager."""
    manager = AsyncMock()
    manager.enabled = True
    manager.get_client = Mock(return_value=Mock())
    return manager


@pytest.fixture
def mock_dedup_manager():
    """Mock FileDeduplicationManager."""
    manager = AsyncMock()
    manager.calculate_sha256 = Mock(return_value="abc123def456")
    return manager


@pytest.fixture
def mock_kimi_client():
    """Mock Kimi/Moonshot OpenAI client."""
    client = Mock()
    
    # Mock file metadata
    metadata = Mock()
    metadata.filename = "test_file.pdf"
    metadata.bytes = 1024 * 100  # 100KB
    client.files.retrieve = Mock(return_value=metadata)
    
    # Mock file content with streaming
    content_response = Mock()
    content_response.iter_content = Mock(return_value=[b"chunk1", b"chunk2"])
    client.files.content = Mock(return_value=content_response)
    
    return client


@pytest.fixture
def test_file_small():
    """Create small test file (< 10MB)."""
    test_file = TEST_DATA_DIR / "small_test.txt"
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.write_text("Small test file content")
    return test_file


@pytest.fixture
def test_file_medium():
    """Create medium test file (10-100MB)."""
    test_file = TEST_DATA_DIR / "medium_test.bin"
    test_file.parent.mkdir(parents=True, exist_ok=True)
    # Create 50MB file
    with open(test_file, 'wb') as f:
        f.write(b'x' * (50 * 1024 * 1024))
    return test_file


@pytest.fixture
def malicious_filenames():
    """Test cases for path traversal and injection attacks."""
    return [
        "../../../etc/passwd",
        "..\\..\\..\\windows\\system32",
        "file|rm -rf /",
        "file`whoami`",
        "file$(whoami)",
        "file;rm -rf /",
        "file\x00.txt",
        "file<script>alert('xss')</script>.txt",
        "con.txt",  # Reserved on Windows
        "prn.txt",  # Reserved on Windows
        "",  # Empty
        "   ",  # Whitespace only
        "." * 300,  # Very long
    ]


@pytest.fixture
def valid_filenames():
    """Test cases for valid filenames."""
    return [
        "document.pdf",
        "image.png",
        "data.json",
        "archive.zip",
        "file-with-dashes.txt",
        "file_with_underscores.txt",
        "file123.txt",
        "UPPERCASE.PDF",
        "mixed_Case-File.txt",
    ]

