"""
Performance Tests: Load Testing & Resource Validation

Tests system performance under load, memory leak detection,
CPU usage profiling, and response time validation.

Created: 2025-10-05
Week: 3, Day 14
"""

import pytest
import asyncio
import time
import psutil
import os
from src.daemon.session_manager import SessionManager
from utils.error_handling import GracefulDegradation
from utils.progress import ProgressHeartbeat


class TestLoadTesting:
    """Test system performance under load."""
    
    @pytest.mark.asyncio
    async def test_concurrent_session_creation(self):
        """Test creating multiple concurrent sessions."""
        manager = SessionManager(max_concurrent_sessions=100)
        
        # Create 50 concurrent sessions
        session_ids = [f"load-test-session-{i}" for i in range(50)]
        
        start_time = time.time()
        tasks = [manager.ensure(sid) for sid in session_ids]
        sessions = await asyncio.gather(*tasks)
        duration = time.time() - start_time
        
        # All sessions should be created
        assert len(sessions) == 50
        assert all(s is not None for s in sessions)
        
        # Should complete in reasonable time (< 5 seconds)
        assert duration < 5.0
        
        # Cleanup
        for sid in session_ids:
            await manager.remove(sid)
    
    @pytest.mark.asyncio
    async def test_concurrent_session_operations(self):
        """Test concurrent operations on multiple sessions."""
        manager = SessionManager()
        
        # Create sessions
        session_ids = [f"ops-test-session-{i}" for i in range(20)]
        for sid in session_ids:
            await manager.ensure(sid)
        
        # Perform concurrent operations
        start_time = time.time()
        tasks = []
        for sid in session_ids:
            tasks.append(manager.update_activity(sid))
            tasks.append(manager.get(sid))
        
        await asyncio.gather(*tasks)
        duration = time.time() - start_time
        
        # Should complete quickly (< 2 seconds)
        assert duration < 2.0
        
        # Cleanup
        for sid in session_ids:
            await manager.remove(sid)
    
    @pytest.mark.asyncio
    async def test_session_cleanup_performance(self):
        """Test performance of session cleanup with many sessions."""
        manager = SessionManager(session_timeout_secs=1)
        
        # Create many sessions
        session_ids = [f"cleanup-test-session-{i}" for i in range(100)]
        for sid in session_ids:
            await manager.ensure(sid)
        
        # Wait for timeout
        await asyncio.sleep(1.5)
        
        # Cleanup should be fast
        start_time = time.time()
        cleaned = await manager.cleanup_stale_sessions()
        duration = time.time() - start_time
        
        # Should cleanup all sessions
        assert cleaned == 100
        
        # Should complete quickly (< 1 second)
        assert duration < 1.0
    
    @pytest.mark.asyncio
    async def test_graceful_degradation_under_load(self):
        """Test graceful degradation with many concurrent operations."""
        degradation = GracefulDegradation()
        
        call_count = 0
        
        async def test_fn():
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.01)  # Simulate work
            return f"result_{call_count}"
        
        # Execute many concurrent operations
        start_time = time.time()
        tasks = [
            degradation.execute_with_fallback(test_fn, timeout_secs=5.0, max_retries=0)
            for _ in range(50)
        ]
        results = await asyncio.gather(*tasks)
        duration = time.time() - start_time
        
        # All should succeed
        assert len(results) == 50
        assert all(r.startswith("result_") for r in results)
        
        # Should complete in reasonable time (< 10 seconds)
        assert duration < 10.0
    
    @pytest.mark.asyncio
    async def test_progress_heartbeat_under_load(self):
        """Test progress heartbeat with many concurrent operations."""
        messages = []

        async def callback(data):
            messages.append(data)

        # Create multiple concurrent heartbeats
        async def run_heartbeat(index):
            async with ProgressHeartbeat(interval_secs=0.3, callback=callback) as hb:
                hb.set_total_steps(5)
                for step in range(1, 6):
                    hb.set_current_step(step)
                    await hb.send_heartbeat(f"Task {index} - Step {step}")
                    await asyncio.sleep(0.2)  # Longer than interval to trigger heartbeats

        start_time = time.time()
        tasks = [run_heartbeat(i) for i in range(10)]
        await asyncio.gather(*tasks)
        duration = time.time() - start_time

        # Should receive heartbeat messages (at least some)
        # Note: Exact count depends on timing, so we just verify we got some
        assert len(messages) >= 5  # At least some heartbeats

        # Should complete in reasonable time (< 20 seconds)
        assert duration < 20.0


class TestMemoryLeakDetection:
    """Test for memory leaks."""
    
    @pytest.mark.asyncio
    async def test_session_creation_no_memory_leak(self):
        """Test that repeated session creation doesn't leak memory."""
        manager = SessionManager()
        
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create and destroy many sessions
        for i in range(100):
            session_id = f"leak-test-{i}"
            await manager.ensure(session_id)
            await manager.remove(session_id)
        
        # Get final memory usage
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be minimal (< 10 MB)
        assert memory_increase < 10.0
    
    @pytest.mark.asyncio
    async def test_graceful_degradation_no_memory_leak(self):
        """Test that repeated graceful degradation doesn't leak memory."""
        degradation = GracefulDegradation()
        
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        async def test_fn():
            return "result"
        
        # Execute many operations
        for _ in range(100):
            await degradation.execute_with_fallback(test_fn, timeout_secs=1.0, max_retries=0)
        
        # Get final memory usage
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be minimal (< 10 MB)
        assert memory_increase < 10.0


class TestCPUUsage:
    """Test CPU usage under load."""
    
    @pytest.mark.asyncio
    async def test_session_operations_cpu_usage(self):
        """Test that session operations don't consume excessive CPU."""
        manager = SessionManager()
        
        # Create sessions
        session_ids = [f"cpu-test-{i}" for i in range(50)]
        for sid in session_ids:
            await manager.ensure(sid)
        
        # Get initial CPU usage
        process = psutil.Process(os.getpid())
        initial_cpu = process.cpu_percent(interval=0.1)
        
        # Perform many operations
        for _ in range(100):
            for sid in session_ids:
                await manager.update_activity(sid)
        
        # Get final CPU usage
        final_cpu = process.cpu_percent(interval=0.1)
        
        # CPU usage should be reasonable (< 80%)
        assert final_cpu < 80.0
        
        # Cleanup
        for sid in session_ids:
            await manager.remove(sid)


class TestResponseTime:
    """Test response time validation."""
    
    @pytest.mark.asyncio
    async def test_session_creation_response_time(self):
        """Test that session creation is fast."""
        manager = SessionManager()
        
        # Measure response time for single session creation
        start_time = time.time()
        await manager.ensure("response-test-1")
        duration = time.time() - start_time
        
        # Should be very fast (< 0.1 seconds)
        assert duration < 0.1
        
        # Cleanup
        await manager.remove("response-test-1")
    
    @pytest.mark.asyncio
    async def test_session_activity_update_response_time(self):
        """Test that activity update is fast."""
        manager = SessionManager()
        
        # Create session
        await manager.ensure("response-test-2")
        
        # Measure response time for activity update
        start_time = time.time()
        await manager.update_activity("response-test-2")
        duration = time.time() - start_time
        
        # Should be very fast (< 0.05 seconds)
        assert duration < 0.05
        
        # Cleanup
        await manager.remove("response-test-2")
    
    @pytest.mark.asyncio
    async def test_graceful_degradation_response_time(self):
        """Test that graceful degradation adds minimal overhead."""
        degradation = GracefulDegradation()
        
        async def fast_fn():
            return "result"
        
        # Measure response time with graceful degradation
        start_time = time.time()
        result = await degradation.execute_with_fallback(fast_fn, timeout_secs=1.0, max_retries=0)
        duration = time.time() - start_time
        
        # Should add minimal overhead (< 0.1 seconds)
        assert duration < 0.1
        assert result == "result"
    
    @pytest.mark.asyncio
    async def test_progress_heartbeat_response_time(self):
        """Test that progress heartbeat adds minimal overhead."""
        messages = []
        
        async def callback(data):
            messages.append(data)
        
        # Measure response time with progress heartbeat
        start_time = time.time()
        async with ProgressHeartbeat(interval_secs=1.0, callback=callback) as hb:
            hb.set_total_steps(3)
            for step in range(1, 4):
                hb.set_current_step(step)
                await hb.send_heartbeat(f"Step {step}")
                await asyncio.sleep(0.05)
        duration = time.time() - start_time
        
        # Should complete quickly (< 1 second)
        assert duration < 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

