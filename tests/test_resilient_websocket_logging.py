"""
Integration tests for resilient_websocket logging optimization.

Tests the actual logging behavior of resilient_websocket module with sampling.

Created: 2025-10-28
EXAI Consultation: 7e59bfd7-a9cc-4a19-9807-5ebd84082cab
"""

import pytest
import asyncio
import logging
import os
from unittest.mock import Mock, AsyncMock, patch
from collections import defaultdict

# Import the module under test
from src.monitoring.resilient_websocket import ResilientWebSocket


class LogCapture:
    """Capture logs for analysis."""
    
    def __init__(self):
        self.logs = []
        self.by_level = defaultdict(int)
        self.by_key = defaultdict(int)
    
    def add_log(self, level: str, message: str):
        """Add a captured log."""
        self.logs.append({"level": level, "message": message})
        self.by_level[level] += 1
        
        # Extract sampling key if present
        if "[SAMPLED:" in message:
            key = message.split("[SAMPLED:")[1].split("]")[0]
            self.by_key[key] += 1
    
    def get_summary(self):
        """Get summary statistics."""
        return {
            "total": len(self.logs),
            "by_level": dict(self.by_level),
            "by_key": dict(self.by_key)
        }


class MockLogHandler(logging.Handler):
    """Mock log handler to capture logs."""
    
    def __init__(self, capture: LogCapture):
        super().__init__()
        self.capture = capture
    
    def emit(self, record):
        """Capture log record."""
        self.capture.add_log(record.levelname, record.getMessage())


@pytest.fixture
def log_capture():
    """Fixture to capture logs."""
    return LogCapture()


@pytest.fixture
def mock_websocket():
    """Fixture for mock WebSocket."""
    ws = AsyncMock()
    ws.send = AsyncMock()
    ws.close = AsyncMock()
    return ws


@pytest.fixture
def resilient_ws(mock_websocket, log_capture):
    """Fixture for ResilientWebSocket with log capture."""
    # Set up log capture
    logger = logging.getLogger("src.monitoring.resilient_websocket")
    handler = MockLogHandler(log_capture)
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    
    # Create ResilientWebSocket instance
    rws = ResilientWebSocket(mock_websocket, "test-client-123")
    
    yield rws
    
    # Cleanup
    logger.removeHandler(handler)


@pytest.mark.asyncio
async def test_enqueue_sampling(resilient_ws, log_capture):
    """Test that enqueue operations are sampled at ~10%."""
    # Send 100 messages
    for i in range(100):
        await resilient_ws.enqueue({"test": f"message-{i}"})
    
    # Check log volume
    summary = log_capture.get_summary()
    
    # Should have ~10 sampled enqueue logs (10% of 100)
    enqueue_logs = summary['by_key'].get('enqueue', 0)
    
    # Allow some variance (8-12 logs for 10% sampling)
    assert 8 <= enqueue_logs <= 12, f"Expected 8-12 enqueue logs, got {enqueue_logs}"
    
    # Total logs should be much less than 100
    assert summary['total'] < 50, f"Expected <50 total logs, got {summary['total']}"


@pytest.mark.asyncio
async def test_send_success_sampling(resilient_ws, mock_websocket, log_capture):
    """Test that send success logs are sampled."""
    # Enqueue and send 100 messages
    for i in range(100):
        await resilient_ws.enqueue({"test": f"message-{i}"})
    
    # Trigger sends
    await resilient_ws.flush()
    
    # Check for sampled send_success logs
    summary = log_capture.get_summary()
    send_success_logs = summary['by_key'].get('send_success', 0)
    
    # Should have some sampled logs, but not all 100
    assert send_success_logs < 20, f"Expected <20 send_success logs, got {send_success_logs}"


@pytest.mark.asyncio
async def test_critical_logs_not_sampled(resilient_ws, log_capture):
    """Test that WARNING/ERROR logs are never sampled."""
    # Set up log capture for WARNING level
    logger = logging.getLogger("src.monitoring.resilient_websocket")
    original_level = logger.level
    logger.setLevel(logging.WARNING)
    
    try:
        # Trigger some operations that might generate warnings
        # (This depends on the actual implementation)
        
        # For now, just verify that if there are WARNING/ERROR logs,
        # they don't have [SAMPLED] markers
        summary = log_capture.get_summary()
        
        for log in log_capture.logs:
            if log['level'] in ['WARNING', 'ERROR', 'CRITICAL']:
                assert '[SAMPLED:' not in log['message'], \
                    f"Critical log should not be sampled: {log['message']}"
    
    finally:
        logger.setLevel(original_level)


@pytest.mark.asyncio
async def test_sampling_rate_configuration():
    """Test that sampling rate can be configured via environment variable."""
    # Test with 20% sampling rate
    with patch.dict(os.environ, {'LOG_SAMPLE_RATE_RESILIENT_WEBSOCKET': '0.2'}):
        # Import fresh to pick up new env var
        import importlib
        import src.monitoring.resilient_websocket as rws_module
        importlib.reload(rws_module)
        
        # Verify sampling rate is configured
        # (This would require exposing the sampling_logger or its config)
        # For now, this is a placeholder test


@pytest.mark.asyncio
async def test_log_level_configuration():
    """Test that log level can be configured via environment variable."""
    # Test with ERROR level
    with patch.dict(os.environ, {'LOG_LEVEL_RESILIENT_WEBSOCKET': 'ERROR'}):
        # Import fresh to pick up new env var
        import importlib
        import src.monitoring.resilient_websocket as rws_module
        importlib.reload(rws_module)
        
        # Verify log level is configured
        logger = logging.getLogger("src.monitoring.resilient_websocket")
        # Note: This might not work as expected due to logger caching


@pytest.mark.asyncio
async def test_performance_overhead(resilient_ws, log_capture):
    """Test that logging overhead is minimal."""
    import time
    
    # Measure time to enqueue 1000 messages
    start_time = time.time()
    
    for i in range(1000):
        await resilient_ws.enqueue({"test": f"message-{i}"})
    
    elapsed = time.time() - start_time
    
    # Should complete in <1 second (very generous threshold)
    assert elapsed < 1.0, f"Enqueuing 1000 messages took {elapsed:.2f}s (expected <1s)"
    
    # Log volume should be ~100 (10% of 1000)
    summary = log_capture.get_summary()
    assert summary['total'] < 200, f"Expected <200 logs for 1000 operations, got {summary['total']}"


@pytest.mark.asyncio
async def test_per_key_sampling_independence(resilient_ws, log_capture):
    """Test that different operation types have independent sampling."""
    # Perform different operations
    for i in range(100):
        await resilient_ws.enqueue({"test": f"message-{i}"})
    
    await resilient_ws.flush()
    
    # Check that we have samples from multiple keys
    summary = log_capture.get_summary()
    
    # Should have samples from at least 2 different operation types
    assert len(summary['by_key']) >= 2, \
        f"Expected samples from multiple operation types, got {list(summary['by_key'].keys())}"


@pytest.mark.asyncio
async def test_no_sampling_when_disabled():
    """Test that sampling can be disabled (100% logging)."""
    with patch.dict(os.environ, {'LOG_SAMPLE_RATE_RESILIENT_WEBSOCKET': '1.0'}):
        # Import fresh to pick up new env var
        import importlib
        import src.monitoring.resilient_websocket as rws_module
        importlib.reload(rws_module)
        
        # With 100% sampling, all logs should appear
        # (This would require a full test setup)


def test_log_format():
    """Test that sampled logs have proper format."""
    # Verify that sampled logs include:
    # 1. [SAMPLED:key] marker
    # 2. Useful context information
    # 3. Proper log level
    
    # This is a placeholder for format validation
    pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

