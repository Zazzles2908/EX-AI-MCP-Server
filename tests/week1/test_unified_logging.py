"""Tests for unified logging system.

Tests the UnifiedLogger class to ensure:
1. Log entries are written correctly
2. Buffering works as expected
3. Sanitization removes sensitive data
4. All log methods work correctly
5. Integration with existing logging infrastructure
"""

import pytest
import json
import tempfile
import time
from pathlib import Path
from utils.logging_unified import UnifiedLogger, get_unified_logger


class TestUnifiedLoggerBasics:
    """Test basic unified logger functionality."""
    
    def test_logger_initialization(self):
        """Test logger initializes correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.jsonl"
            logger = UnifiedLogger(str(log_file))
            
            assert logger.log_file == log_file
            assert logger.buffer == []
            assert logger.buffer_size == 10
            
    def test_log_file_created(self):
        """Test log file is created on first write."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.jsonl"
            logger = UnifiedLogger(str(log_file))
            
            # Write enough entries to trigger flush
            for i in range(10):
                logger.log_tool_start(
                    tool_name="test_tool",
                    request_id=f"req-{i}",
                    params={"test": "value"}
                )
            
            assert log_file.exists()
            
    def test_buffer_flush_on_size(self):
        """Test buffer flushes when size limit reached."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.jsonl"
            logger = UnifiedLogger(str(log_file))
            
            # Write 9 entries (should not flush)
            for i in range(9):
                logger.log_tool_start(
                    tool_name="test_tool",
                    request_id=f"req-{i}",
                    params={"test": "value"}
                )
            
            assert len(logger.buffer) == 9
            assert not log_file.exists()
            
            # Write 10th entry (should trigger flush)
            logger.log_tool_start(
                tool_name="test_tool",
                request_id="req-9",
                params={"test": "value"}
            )
            
            assert len(logger.buffer) == 0
            assert log_file.exists()


class TestLogMethods:
    """Test all log methods."""
    
    def test_log_tool_start(self):
        """Test log_tool_start writes correct entry."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.jsonl"
            logger = UnifiedLogger(str(log_file))
            
            logger.log_tool_start(
                tool_name="chat",
                request_id="req-123",
                params={"prompt": "Hello"},
                metadata={"user": "test"}
            )
            logger._flush()
            
            # Read log file
            with open(log_file, 'r') as f:
                entry = json.loads(f.readline())
            
            assert entry["event"] == "tool_start"
            assert entry["tool"] == "chat"
            assert entry["request_id"] == "req-123"
            assert entry["params"]["prompt"] == "Hello"
            assert entry["metadata"]["user"] == "test"
            assert "timestamp" in entry
            assert "datetime" in entry
            
    def test_log_tool_progress(self):
        """Test log_tool_progress writes correct entry."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.jsonl"
            logger = UnifiedLogger(str(log_file))
            
            logger.log_tool_progress(
                tool_name="analyze",
                request_id="req-456",
                step=3,
                message="Processing step 3 of 5",
                metadata={"progress_pct": 60.0}
            )
            logger._flush()
            
            # Read log file
            with open(log_file, 'r') as f:
                entry = json.loads(f.readline())
            
            assert entry["event"] == "tool_progress"
            assert entry["tool"] == "analyze"
            assert entry["request_id"] == "req-456"
            assert entry["step"] == 3
            assert entry["message"] == "Processing step 3 of 5"
            assert entry["metadata"]["progress_pct"] == 60.0
            
    def test_log_tool_complete(self):
        """Test log_tool_complete writes correct entry."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.jsonl"
            logger = UnifiedLogger(str(log_file))
            
            logger.log_tool_complete(
                tool_name="chat",
                request_id="req-789",
                result={"status": "success", "content": "Response"},
                duration_secs=2.5,
                metadata={"tokens": 150}
            )
            logger._flush()
            
            # Read log file
            with open(log_file, 'r') as f:
                entry = json.loads(f.readline())
            
            assert entry["event"] == "tool_complete"
            assert entry["tool"] == "chat"
            assert entry["request_id"] == "req-789"
            assert entry["duration_secs"] == 2.5
            assert entry["result"]["status"] == "success"
            assert entry["metadata"]["tokens"] == 150
            
    def test_log_tool_error(self):
        """Test log_tool_error writes correct entry."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.jsonl"
            logger = UnifiedLogger(str(log_file))
            
            logger.log_tool_error(
                tool_name="chat",
                request_id="req-error",
                error="Connection timeout",
                error_traceback="Traceback...",
                metadata={"retry_count": 3}
            )
            logger._flush()
            
            # Read log file
            with open(log_file, 'r') as f:
                entry = json.loads(f.readline())
            
            assert entry["event"] == "tool_error"
            assert entry["tool"] == "chat"
            assert entry["request_id"] == "req-error"
            assert entry["error"] == "Connection timeout"
            assert entry["traceback"] == "Traceback..."
            assert entry["metadata"]["retry_count"] == 3
            
    def test_log_expert_validation_start(self):
        """Test log_expert_validation_start writes correct entry."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.jsonl"
            logger = UnifiedLogger(str(log_file))
            
            logger.log_expert_validation_start(
                tool_name="analyze",
                request_id="req-expert",
                expert_model="kimi-k2-0905-preview",
                metadata={"validation_type": "quality"}
            )
            logger._flush()
            
            # Read log file
            with open(log_file, 'r') as f:
                entry = json.loads(f.readline())
            
            assert entry["event"] == "expert_validation_start"
            assert entry["tool"] == "analyze"
            assert entry["request_id"] == "req-expert"
            assert entry["expert_model"] == "kimi-k2-0905-preview"
            assert entry["metadata"]["validation_type"] == "quality"
            
    def test_log_expert_validation_complete(self):
        """Test log_expert_validation_complete writes correct entry."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.jsonl"
            logger = UnifiedLogger(str(log_file))
            
            logger.log_expert_validation_complete(
                tool_name="analyze",
                request_id="req-expert",
                expert_model="kimi-k2-0905-preview",
                validation_result={"approved": True, "score": 0.95},
                duration_secs=5.2,
                metadata={"validation_type": "quality"}
            )
            logger._flush()
            
            # Read log file
            with open(log_file, 'r') as f:
                entry = json.loads(f.readline())
            
            assert entry["event"] == "expert_validation_complete"
            assert entry["tool"] == "analyze"
            assert entry["request_id"] == "req-expert"
            assert entry["expert_model"] == "kimi-k2-0905-preview"
            assert entry["duration_secs"] == 5.2
            assert entry["validation_result"]["approved"] is True
            assert entry["validation_result"]["score"] == 0.95


class TestSanitization:
    """Test parameter and result sanitization."""
    
    def test_sanitize_params_truncates_long_strings(self):
        """Test long parameter strings are truncated."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.jsonl"
            logger = UnifiedLogger(str(log_file))
            
            long_string = "x" * 1000
            logger.log_tool_start(
                tool_name="test",
                request_id="req-1",
                params={"long_param": long_string}
            )
            logger._flush()
            
            # Read log file
            with open(log_file, 'r') as f:
                entry = json.loads(f.readline())
            
            assert len(entry["params"]["long_param"]) < 600
            assert "truncated" in entry["params"]["long_param"]
            
    def test_sanitize_params_skips_private_params(self):
        """Test private parameters are skipped."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.jsonl"
            logger = UnifiedLogger(str(log_file))
            
            logger.log_tool_start(
                tool_name="test",
                request_id="req-1",
                params={"public": "value", "_private": "secret"}
            )
            logger._flush()
            
            # Read log file
            with open(log_file, 'r') as f:
                entry = json.loads(f.readline())
            
            assert "public" in entry["params"]
            assert "_private" not in entry["params"]
            
    def test_sanitize_result_truncates_long_strings(self):
        """Test long result strings are truncated."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.jsonl"
            logger = UnifiedLogger(str(log_file))
            
            long_string = "y" * 2000
            logger.log_tool_complete(
                tool_name="test",
                request_id="req-1",
                result={"long_result": long_string},
                duration_secs=1.0
            )
            logger._flush()
            
            # Read log file
            with open(log_file, 'r') as f:
                entry = json.loads(f.readline())
            
            assert len(entry["result"]["long_result"]) < 1100
            assert "truncated" in entry["result"]["long_result"]


class TestGlobalLogger:
    """Test global logger instance."""
    
    def test_get_unified_logger_returns_singleton(self):
        """Test get_unified_logger returns same instance."""
        logger1 = get_unified_logger()
        logger2 = get_unified_logger()
        
        assert logger1 is logger2
        
    def test_global_logger_works(self):
        """Test global logger can log entries."""
        logger = get_unified_logger()
        
        # Should not raise exception
        logger.log_tool_start(
            tool_name="test",
            request_id="req-global",
            params={"test": "value"}
        )


class TestFullWorkflow:
    """Test complete logging workflow."""
    
    def test_complete_tool_execution_workflow(self):
        """Test logging a complete tool execution."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.jsonl"
            logger = UnifiedLogger(str(log_file))
            
            request_id = "req-workflow"
            
            # Log start
            logger.log_tool_start(
                tool_name="analyze",
                request_id=request_id,
                params={"query": "test query"}
            )
            
            # Log progress
            for i in range(1, 4):
                logger.log_tool_progress(
                    tool_name="analyze",
                    request_id=request_id,
                    step=i,
                    message=f"Step {i} of 3"
                )
            
            # Log completion
            logger.log_tool_complete(
                tool_name="analyze",
                request_id=request_id,
                result={"status": "success"},
                duration_secs=3.5
            )
            
            logger._flush()
            
            # Read all entries
            entries = []
            with open(log_file, 'r') as f:
                for line in f:
                    entries.append(json.loads(line))
            
            # Verify workflow
            assert len(entries) == 5  # 1 start + 3 progress + 1 complete
            assert entries[0]["event"] == "tool_start"
            assert entries[1]["event"] == "tool_progress"
            assert entries[2]["event"] == "tool_progress"
            assert entries[3]["event"] == "tool_progress"
            assert entries[4]["event"] == "tool_complete"
            
            # All should have same request_id
            for entry in entries:
                assert entry["request_id"] == request_id

