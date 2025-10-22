"""
Concurrent Request Diagnostic Tests

Tests to expose and diagnose concurrent request hanging issues.
Tests with varying concurrency levels (5, 10, 20, 50) and identifies blocking points.

Created: 2025-10-21
Phase: 2.2 - Concurrent Request Handling
"""

import pytest
import asyncio
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
import logging

from src.utils.request_lifecycle_logger import (
    get_lifecycle_logger,
    log_request_received,
    log_request_completed,
    log_request_timeout,
    log_request_error
)

logger = logging.getLogger(__name__)


class ConcurrentRequestDiagnostics:
    """Diagnostic tests for concurrent request handling."""
    
    @staticmethod
    def simple_request(request_id: str, provider: str, model: str, delay: float = 0.1) -> Dict[str, Any]:
        """
        Simulate a simple request with configurable delay.
        
        Args:
            request_id: Unique request identifier
            provider: Provider name
            model: Model name
            delay: Simulated processing delay in seconds
        
        Returns:
            Result dictionary with timing information
        """
        start_time = time.time()
        log_request_received(request_id, provider, model)
        
        try:
            # Simulate processing
            time.sleep(delay)
            
            duration = time.time() - start_time
            log_request_completed(request_id, duration_seconds=duration)
            
            return {
                'request_id': request_id,
                'status': 'success',
                'duration': duration,
                'provider': provider,
                'model': model
            }
        except Exception as e:
            log_request_error(request_id, str(e))
            return {
                'request_id': request_id,
                'status': 'error',
                'error': str(e),
                'provider': provider,
                'model': model
            }
    
    @staticmethod
    def test_concurrent_requests(num_requests: int, delay: float = 0.1, max_workers: int = 10) -> Dict[str, Any]:
        """
        Test concurrent requests and measure performance.
        
        Args:
            num_requests: Number of concurrent requests to spawn
            delay: Simulated processing delay per request
            max_workers: Maximum number of worker threads
        
        Returns:
            Dictionary with test results and statistics
        """
        logger.info(f"Starting concurrent request test: {num_requests} requests, {delay}s delay, {max_workers} workers")
        
        start_time = time.time()
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for i in range(num_requests):
                request_id = f"test_req_{i}_{int(time.time() * 1000)}"
                provider = 'kimi' if i % 2 == 0 else 'glm'
                model = 'moonshot-v1-8k' if provider == 'kimi' else 'glm-4.5-flash'
                
                future = executor.submit(
                    ConcurrentRequestDiagnostics.simple_request,
                    request_id,
                    provider,
                    model,
                    delay
                )
                futures.append(future)
            
            # Collect results
            for future in as_completed(futures):
                try:
                    result = future.result(timeout=30)
                    results.append(result)
                except Exception as e:
                    logger.error(f"Request failed: {e}")
                    results.append({'status': 'error', 'error': str(e)})
        
        total_duration = time.time() - start_time
        
        # Calculate statistics
        successful = [r for r in results if r.get('status') == 'success']
        failed = [r for r in results if r.get('status') == 'error']
        
        durations = [r['duration'] for r in successful]
        avg_duration = sum(durations) / len(durations) if durations else 0
        min_duration = min(durations) if durations else 0
        max_duration = max(durations) if durations else 0
        
        # Get lifecycle logger statistics
        lifecycle_stats = get_lifecycle_logger().get_statistics()
        
        return {
            'num_requests': num_requests,
            'successful': len(successful),
            'failed': len(failed),
            'total_duration': total_duration,
            'avg_request_duration': avg_duration,
            'min_request_duration': min_duration,
            'max_request_duration': max_duration,
            'requests_per_second': num_requests / total_duration if total_duration > 0 else 0,
            'lifecycle_stats': lifecycle_stats
        }


class TestConcurrentRequestDiagnostics:
    """Pytest test cases for concurrent request diagnostics."""
    
    def test_5_concurrent_requests(self):
        """Test with 5 concurrent requests."""
        result = ConcurrentRequestDiagnostics.test_concurrent_requests(
            num_requests=5,
            delay=0.1,
            max_workers=5
        )
        
        logger.info(f"5 concurrent requests result: {result}")
        
        assert result['successful'] == 5
        assert result['failed'] == 0
        assert result['total_duration'] < 2.0  # Should complete in under 2 seconds
    
    def test_10_concurrent_requests(self):
        """Test with 10 concurrent requests."""
        result = ConcurrentRequestDiagnostics.test_concurrent_requests(
            num_requests=10,
            delay=0.1,
            max_workers=10
        )
        
        logger.info(f"10 concurrent requests result: {result}")
        
        assert result['successful'] == 10
        assert result['failed'] == 0
        assert result['total_duration'] < 3.0  # Should complete in under 3 seconds
    
    def test_20_concurrent_requests(self):
        """Test with 20 concurrent requests."""
        result = ConcurrentRequestDiagnostics.test_concurrent_requests(
            num_requests=20,
            delay=0.1,
            max_workers=10
        )
        
        logger.info(f"20 concurrent requests result: {result}")
        
        assert result['successful'] == 20
        assert result['failed'] == 0
        assert result['total_duration'] < 5.0  # Should complete in under 5 seconds
    
    def test_50_concurrent_requests(self):
        """Test with 50 concurrent requests."""
        result = ConcurrentRequestDiagnostics.test_concurrent_requests(
            num_requests=50,
            delay=0.1,
            max_workers=10
        )
        
        logger.info(f"50 concurrent requests result: {result}")
        
        assert result['successful'] == 50
        assert result['failed'] == 0
        assert result['total_duration'] < 10.0  # Should complete in under 10 seconds
    
    def test_concurrent_requests_with_varying_delays(self):
        """Test concurrent requests with varying processing delays."""
        start_time = time.time()
        results = []
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for i in range(10):
                request_id = f"varying_delay_req_{i}"
                provider = 'kimi' if i % 2 == 0 else 'glm'
                model = 'moonshot-v1-8k' if provider == 'kimi' else 'glm-4.5-flash'
                delay = 0.1 * (i + 1)  # Varying delays: 0.1s, 0.2s, ..., 1.0s
                
                future = executor.submit(
                    ConcurrentRequestDiagnostics.simple_request,
                    request_id,
                    provider,
                    model,
                    delay
                )
                futures.append(future)
            
            for future in as_completed(futures):
                result = future.result(timeout=30)
                results.append(result)
        
        total_duration = time.time() - start_time
        
        # All requests should complete successfully
        assert len(results) == 10
        assert all(r['status'] == 'success' for r in results)
        
        # Total duration should be close to max delay (1.0s) since they run concurrently
        assert total_duration < 2.0
    
    def test_lifecycle_logger_tracking(self):
        """Test that lifecycle logger correctly tracks concurrent requests."""
        lifecycle_logger = get_lifecycle_logger()
        
        # Run concurrent requests
        result = ConcurrentRequestDiagnostics.test_concurrent_requests(
            num_requests=5,
            delay=0.1,
            max_workers=5
        )
        
        # Verify lifecycle logger captured events
        stats = lifecycle_logger.get_statistics()
        
        assert stats['total_requests'] >= 5
        assert stats['completed_requests'] >= 5
        assert stats['avg_duration_ms'] > 0
    
    def test_request_timeout_detection(self):
        """Test detection of requests that exceed timeout."""
        request_id = "timeout_test_req"

        def slow_request():
            log_request_received(request_id, 'kimi', 'moonshot-v1-8k')
            time.sleep(5)  # Deliberately slow
            log_request_completed(request_id)

        start_time = time.time()
        thread = threading.Thread(target=slow_request, daemon=True)  # Make daemon to prevent hanging
        thread.start()
        thread.join(timeout=1.0)  # Wait max 1 second

        duration = time.time() - start_time

        if thread.is_alive():
            # Request is still running - this is a timeout scenario
            log_request_timeout(request_id, timeout_seconds=1.0)
            assert duration >= 1.0
            assert duration < 1.5
            # Thread will be cleaned up automatically as daemon
        else:
            pytest.fail("Request completed too quickly - should have timed out")


class TestBlockingPointIdentification:
    """Tests to identify specific blocking points in the system."""
    
    def test_identify_blocking_operations(self):
        """Identify operations that block concurrent execution."""
        # This test will be expanded as we identify actual blocking points
        # For now, it serves as a placeholder for blocking point analysis
        
        lifecycle_logger = get_lifecycle_logger()
        
        # Run concurrent requests
        result = ConcurrentRequestDiagnostics.test_concurrent_requests(
            num_requests=10,
            delay=0.1,
            max_workers=10
        )
        
        # Analyze phase durations to identify bottlenecks
        active_requests = lifecycle_logger.get_active_requests()
        
        # If there are stuck requests, they indicate blocking points
        assert len(active_requests) == 0, f"Found {len(active_requests)} stuck requests"
    
    def test_auto_model_selection_impact(self):
        """Test impact of 'auto' model selection on concurrent requests."""
        # This test will be implemented once we integrate with actual providers
        # For now, it's a placeholder for testing 'auto' model selection
        pass


if __name__ == '__main__':
    # Run diagnostic tests manually
    print("Running concurrent request diagnostics...")
    
    for num_requests in [5, 10, 20, 50]:
        print(f"\nTesting {num_requests} concurrent requests...")
        result = ConcurrentRequestDiagnostics.test_concurrent_requests(num_requests)
        print(f"Results: {result}")

