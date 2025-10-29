"""
Unit tests for logging utilities.

Tests async logging, sampling, and performance characteristics.

Created: 2025-10-28
EXAI Consultation: 7e59bfd7-a9cc-4a19-9807-5ebd84082cab
"""

import unittest
import logging
import time
import threading
from io import StringIO
from src.utils.logging_utils import (
    AsyncLogHandler,
    SamplingLogger,
    log_sampled,
    get_async_logger,
    get_sampling_logger,
    get_logger
)


class TestAsyncLogHandler(unittest.TestCase):
    """Test async log handler functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.stream = StringIO()
        self.target_handler = logging.StreamHandler(self.stream)
        self.target_handler.setFormatter(logging.Formatter('%(message)s'))
    
    def test_async_handler_processes_logs(self):
        """Test that async handler processes logs in background."""
        handler = AsyncLogHandler(max_queue_size=100, target_handler=self.target_handler)
        logger = logging.getLogger("test_async")
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        
        # Send logs
        for i in range(10):
            logger.info(f"Test message {i}")
        
        # Wait for processing
        time.sleep(0.5)
        
        # Verify logs were processed
        output = self.stream.getvalue()
        self.assertIn("Test message 0", output)
        self.assertIn("Test message 9", output)
        
        # Check stats
        stats = handler.get_stats()
        self.assertEqual(stats["processed"], 10)
        self.assertEqual(stats["dropped"], 0)
    
    def test_async_handler_drops_when_full(self):
        """Test that async handler drops logs when queue is full."""
        handler = AsyncLogHandler(max_queue_size=5, target_handler=self.target_handler)
        logger = logging.getLogger("test_async_full")
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        
        # Flood with logs
        for i in range(100):
            logger.info(f"Test message {i}")
        
        # Wait for processing
        time.sleep(0.5)
        
        # Check that some were dropped
        stats = handler.get_stats()
        self.assertGreater(stats["dropped"], 0)
        self.assertLess(stats["processed"], 100)
    
    def test_async_handler_thread_safety(self):
        """Test that async handler is thread-safe."""
        handler = AsyncLogHandler(max_queue_size=1000, target_handler=self.target_handler)
        logger = logging.getLogger("test_async_threaded")
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        
        def log_worker(worker_id: int):
            for i in range(50):
                logger.info(f"Worker {worker_id} message {i}")
        
        # Create multiple threads
        threads = [threading.Thread(target=log_worker, args=(i,)) for i in range(5)]
        
        # Start all threads
        for t in threads:
            t.start()
        
        # Wait for completion
        for t in threads:
            t.join()
        
        # Wait for processing
        time.sleep(1.0)
        
        # Verify all logs processed
        stats = handler.get_stats()
        self.assertEqual(stats["processed"], 250)  # 5 workers * 50 messages


class TestSamplingLogger(unittest.TestCase):
    """Test sampling logger functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.stream = StringIO()
        handler = logging.StreamHandler(self.stream)
        handler.setFormatter(logging.Formatter('%(message)s'))
        
        self.logger = logging.getLogger("test_sampling")
        self.logger.handlers = []  # Clear existing handlers
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG)
    
    def test_sampling_rate_10_percent(self):
        """Test 10% sampling rate."""
        sampler = SamplingLogger(self.logger, sample_rate=0.1)
        
        # Log 100 messages
        for i in range(100):
            sampler.debug(f"Message {i}")
        
        # Count logged messages
        output = self.stream.getvalue()
        logged_count = output.count("[SAMPLED]")
        
        # Should be approximately 10 (within tolerance)
        self.assertGreater(logged_count, 5)
        self.assertLess(logged_count, 20)
    
    def test_sampling_rate_100_percent(self):
        """Test 100% sampling (no sampling)."""
        sampler = SamplingLogger(self.logger, sample_rate=1.0)
        
        # Log 50 messages
        for i in range(50):
            sampler.debug(f"Message {i}")
        
        # Count logged messages
        output = self.stream.getvalue()
        logged_count = output.count("[SAMPLED]")
        
        # Should log all 50
        self.assertEqual(logged_count, 50)
    
    def test_sampling_rate_0_percent(self):
        """Test 0% sampling (no logs)."""
        sampler = SamplingLogger(self.logger, sample_rate=0.0)
        
        # Log 50 messages
        for i in range(50):
            sampler.debug(f"Message {i}")
        
        # Count logged messages
        output = self.stream.getvalue()
        logged_count = output.count("[SAMPLED]")
        
        # Should log none
        self.assertEqual(logged_count, 0)
    
    def test_warnings_not_sampled(self):
        """Test that warnings are never sampled."""
        sampler = SamplingLogger(self.logger, sample_rate=0.01)  # 1% sampling
        
        # Log 100 warnings
        for i in range(100):
            sampler.warning(f"Warning {i}")
        
        # Count logged warnings
        output = self.stream.getvalue()
        warning_count = output.count("Warning")
        
        # Should log all 100 (no sampling for warnings)
        self.assertEqual(warning_count, 100)
    
    def test_errors_not_sampled(self):
        """Test that errors are never sampled."""
        sampler = SamplingLogger(self.logger, sample_rate=0.01)  # 1% sampling
        
        # Log 100 errors
        for i in range(100):
            sampler.error(f"Error {i}")
        
        # Count logged errors
        output = self.stream.getvalue()
        error_count = output.count("Error")
        
        # Should log all 100 (no sampling for errors)
        self.assertEqual(error_count, 100)


class TestLogSampledDecorator(unittest.TestCase):
    """Test log_sampled decorator."""
    
    def test_decorator_samples_function_calls(self):
        """Test that decorator samples function calls."""
        call_count = 0
        
        @log_sampled(sample_rate=0.1)
        def test_function():
            nonlocal call_count
            call_count += 1
        
        # Call function 100 times
        for _ in range(100):
            test_function()
        
        # All calls should execute
        self.assertEqual(call_count, 100)


class TestGetLogger(unittest.TestCase):
    """Test get_logger factory function."""
    
    def test_get_standard_logger(self):
        """Test getting standard logger."""
        logger = get_logger("test_standard")
        self.assertIsInstance(logger, logging.Logger)
    
    def test_get_async_logger(self):
        """Test getting async logger."""
        logger = get_async_logger("test_async_get")
        self.assertIsInstance(logger, logging.Logger)
        
        # Check for async handler
        has_async_handler = any(isinstance(h, AsyncLogHandler) for h in logger.handlers)
        self.assertTrue(has_async_handler)
    
    def test_get_sampling_logger(self):
        """Test getting sampling logger."""
        logger = get_sampling_logger("test_sampling_get", sample_rate=0.1)
        self.assertIsInstance(logger, SamplingLogger)


class TestPerformance(unittest.TestCase):
    """Performance tests for logging utilities."""
    
    def test_async_handler_throughput(self):
        """Test async handler can process >10K logs/second."""
        handler = AsyncLogHandler(max_queue_size=20000)
        logger = logging.getLogger("test_perf")
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        
        # Send 10K logs
        start_time = time.time()
        for i in range(10000):
            logger.debug(f"Performance test {i}")
        elapsed = time.time() - start_time
        
        # Should complete in <1 second (non-blocking)
        self.assertLess(elapsed, 1.0)
        
        # Wait for processing
        time.sleep(2.0)
        
        # Check stats
        stats = handler.get_stats()
        self.assertEqual(stats["processed"], 10000)
    
    def test_sampling_overhead(self):
        """Test that sampling has minimal overhead."""
        logger = logging.getLogger("test_sampling_perf")
        logger.setLevel(logging.CRITICAL)  # Disable actual logging
        
        sampler = SamplingLogger(logger, sample_rate=0.01)
        
        # Measure time for 10K sampled calls
        start_time = time.time()
        for i in range(10000):
            sampler.debug(f"Performance test {i}")
        elapsed = time.time() - start_time
        
        # Should complete very quickly (<0.1s)
        self.assertLess(elapsed, 0.1)


if __name__ == '__main__':
    unittest.main()

