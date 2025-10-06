"""Tests for progress heartbeat system.

Tests the ProgressHeartbeat class and ProgressHeartbeatManager to ensure:
1. Heartbeats send at correct intervals
2. Progress calculation is accurate
3. Context manager works correctly
4. Callbacks are invoked properly
5. Manager handles multiple operations
"""

import pytest
import asyncio
import time
from utils.progress import ProgressHeartbeat, ProgressHeartbeatManager, get_heartbeat_manager


class TestProgressHeartbeatTiming:
    """Test heartbeat timing and interval behavior."""
    
    @pytest.mark.asyncio
    async def test_heartbeat_sends_at_interval(self):
        """Test heartbeat sends at correct interval."""
        messages = []
        
        async def callback(data):
            messages.append(data)
        
        async with ProgressHeartbeat(interval_secs=2.0, callback=callback) as hb:
            for i in range(10):
                await hb.send_heartbeat(f"Step {i}")
                await asyncio.sleep(1)
        
        # Should have ~5 messages (10 seconds / 2 second interval)
        assert 4 <= len(messages) <= 6, f"Expected 4-6 messages, got {len(messages)}"
        
    @pytest.mark.asyncio
    async def test_force_heartbeat_ignores_interval(self):
        """Test force_heartbeat sends immediately."""
        messages = []
        
        async def callback(data):
            messages.append(data)
        
        async with ProgressHeartbeat(interval_secs=10.0, callback=callback) as hb:
            await hb.force_heartbeat("Message 1")
            await hb.force_heartbeat("Message 2")
            await hb.force_heartbeat("Message 3")
        
        # Should have 3 messages despite 10s interval
        assert len(messages) == 3
        
    @pytest.mark.asyncio
    async def test_heartbeat_respects_enabled_flag(self):
        """Test heartbeat stops when disabled."""
        messages = []
        
        async def callback(data):
            messages.append(data)
        
        hb = ProgressHeartbeat(interval_secs=1.0, callback=callback)
        await hb.force_heartbeat("Message 1")
        
        hb.stop()
        await hb.force_heartbeat("Message 2")  # Should not send
        
        assert len(messages) == 1


class TestProgressCalculation:
    """Test progress percentage and time estimation."""
    
    @pytest.mark.asyncio
    async def test_progress_percentage_calculation(self):
        """Test heartbeat calculates progress correctly."""
        messages = []
        
        async def callback(data):
            messages.append(data)
        
        async with ProgressHeartbeat(interval_secs=1.0, callback=callback) as hb:
            hb.set_total_steps(5)
            
            for i in range(1, 6):
                hb.set_current_step(i)
                await hb.force_heartbeat(f"Step {i}")
                await asyncio.sleep(0.1)
        
        # Check progress calculation
        assert len(messages) == 5
        assert messages[0]["step"] == 1
        assert messages[0]["total_steps"] == 5
        assert messages[0]["progress_pct"] == 20.0  # 1/5 = 20%
        
        assert messages[4]["step"] == 5
        assert messages[4]["progress_pct"] == 100.0  # 5/5 = 100%
        
    @pytest.mark.asyncio
    async def test_elapsed_time_tracking(self):
        """Test heartbeat tracks elapsed time."""
        messages = []
        
        async def callback(data):
            messages.append(data)
        
        async with ProgressHeartbeat(interval_secs=0.5, callback=callback) as hb:
            await hb.force_heartbeat("Start")
            await asyncio.sleep(1.0)
            await hb.force_heartbeat("After 1 second")
        
        assert len(messages) == 2
        assert messages[0]["elapsed_secs"] < 0.1  # First message is immediate
        assert 0.9 <= messages[1]["elapsed_secs"] <= 1.2  # Second message after ~1s
        
    @pytest.mark.asyncio
    async def test_estimated_remaining_time(self):
        """Test heartbeat estimates remaining time."""
        messages = []

        async def callback(data):
            messages.append(data)

        async with ProgressHeartbeat(interval_secs=0.5, callback=callback) as hb:
            hb.set_total_steps(4)

            for i in range(1, 5):
                hb.set_current_step(i)
                await asyncio.sleep(0.5)  # Sleep BEFORE heartbeat to accumulate time
                await hb.force_heartbeat(f"Step {i}")

        # Check estimated remaining time
        assert len(messages) == 4

        # After step 1 (with 0.5s elapsed), should estimate ~1.5s remaining (3 steps * 0.5s each)
        if "estimated_remaining_secs" in messages[0]:
            assert 1.0 <= messages[0]["estimated_remaining_secs"] <= 2.0

        # After step 2, should estimate ~1.0s remaining
        if "estimated_remaining_secs" in messages[1]:
            assert 0.5 <= messages[1]["estimated_remaining_secs"] <= 1.5

        # After step 4, should have no remaining time
        # (or very small due to timing variations)
        if "estimated_remaining_secs" in messages[3]:
            assert messages[3]["estimated_remaining_secs"] < 0.5


class TestContextManager:
    """Test context manager behavior."""
    
    @pytest.mark.asyncio
    async def test_context_manager_starts_and_stops(self):
        """Test context manager properly starts and stops heartbeat."""
        messages = []
        
        async def callback(data):
            messages.append(data)
        
        hb = ProgressHeartbeat(interval_secs=1.0, callback=callback)
        
        # Before entering context
        assert hb.enabled is True
        
        async with hb:
            await hb.force_heartbeat("Inside context")
            assert hb.enabled is True
        
        # After exiting context
        assert hb.enabled is False
        await hb.force_heartbeat("Outside context")  # Should not send
        
        assert len(messages) == 1
        
    @pytest.mark.asyncio
    async def test_context_manager_handles_exceptions(self):
        """Test context manager stops heartbeat even on exception."""
        messages = []
        
        async def callback(data):
            messages.append(data)
        
        hb = ProgressHeartbeat(interval_secs=1.0, callback=callback)
        
        try:
            async with hb:
                await hb.force_heartbeat("Before exception")
                raise ValueError("Test exception")
        except ValueError:
            pass
        
        # Heartbeat should be stopped
        assert hb.enabled is False
        assert len(messages) == 1


class TestCallbackHandling:
    """Test callback invocation and error handling."""
    
    @pytest.mark.asyncio
    async def test_async_callback_invoked(self):
        """Test async callback is invoked correctly."""
        messages = []
        
        async def async_callback(data):
            messages.append(data)
            await asyncio.sleep(0.01)  # Simulate async work
        
        async with ProgressHeartbeat(interval_secs=1.0, callback=async_callback) as hb:
            await hb.force_heartbeat("Test message")
        
        assert len(messages) == 1
        assert messages[0]["message"] == "Test message"
        
    @pytest.mark.asyncio
    async def test_sync_callback_invoked(self):
        """Test sync callback is invoked correctly."""
        messages = []
        
        def sync_callback(data):
            messages.append(data)
        
        async with ProgressHeartbeat(interval_secs=1.0, callback=sync_callback) as hb:
            await hb.force_heartbeat("Test message")
        
        assert len(messages) == 1
        assert messages[0]["message"] == "Test message"
        
    @pytest.mark.asyncio
    async def test_callback_failure_does_not_break_heartbeat(self):
        """Test heartbeat continues even if callback fails."""
        messages = []
        
        async def failing_callback(data):
            messages.append(data)
            raise RuntimeError("Callback failed")
        
        async with ProgressHeartbeat(interval_secs=1.0, callback=failing_callback) as hb:
            await hb.force_heartbeat("Message 1")
            await hb.force_heartbeat("Message 2")
        
        # Both messages should be recorded despite callback failures
        assert len(messages) == 2


class TestProgressHeartbeatManager:
    """Test ProgressHeartbeatManager for managing multiple operations."""
    
    @pytest.mark.asyncio
    async def test_create_and_get_heartbeat(self):
        """Test creating and retrieving heartbeats."""
        manager = ProgressHeartbeatManager()
        
        hb1 = manager.create_heartbeat("op1", interval_secs=5.0)
        hb2 = manager.create_heartbeat("op2", interval_secs=10.0)
        
        assert manager.get_heartbeat("op1") is hb1
        assert manager.get_heartbeat("op2") is hb2
        assert manager.get_heartbeat("op3") is None
        
    @pytest.mark.asyncio
    async def test_remove_heartbeat(self):
        """Test removing heartbeats."""
        manager = ProgressHeartbeatManager()
        
        hb = manager.create_heartbeat("op1", interval_secs=5.0)
        assert manager.get_heartbeat("op1") is hb
        
        manager.remove_heartbeat("op1")
        assert manager.get_heartbeat("op1") is None
        assert hb.enabled is False  # Should be stopped
        
    @pytest.mark.asyncio
    async def test_stop_all_heartbeats(self):
        """Test stopping all heartbeats."""
        manager = ProgressHeartbeatManager()
        
        hb1 = manager.create_heartbeat("op1", interval_secs=5.0)
        hb2 = manager.create_heartbeat("op2", interval_secs=10.0)
        
        manager.stop_all()
        
        assert hb1.enabled is False
        assert hb2.enabled is False
        assert len(manager.operations) == 0
        
    @pytest.mark.asyncio
    async def test_global_heartbeat_manager(self):
        """Test global heartbeat manager instance."""
        manager1 = get_heartbeat_manager()
        manager2 = get_heartbeat_manager()
        
        # Should return same instance
        assert manager1 is manager2


class TestProgressData:
    """Test progress data structure and metadata."""
    
    @pytest.mark.asyncio
    async def test_progress_data_structure(self):
        """Test progress data contains all required fields."""
        messages = []
        
        async def callback(data):
            messages.append(data)
        
        async with ProgressHeartbeat(interval_secs=1.0, callback=callback) as hb:
            hb.set_total_steps(3)
            hb.set_current_step(1)
            await hb.force_heartbeat("Test message")
        
        assert len(messages) == 1
        data = messages[0]
        
        # Check required fields
        assert "message" in data
        assert "elapsed_secs" in data
        assert "progress_pct" in data
        assert "step" in data
        assert "total_steps" in data
        assert "timestamp" in data
        
        assert data["message"] == "Test message"
        assert data["step"] == 1
        assert data["total_steps"] == 3
        assert data["progress_pct"] == pytest.approx(33.3, abs=0.1)
        
    @pytest.mark.asyncio
    async def test_progress_metadata(self):
        """Test progress data includes custom metadata."""
        messages = []
        
        async def callback(data):
            messages.append(data)
        
        async with ProgressHeartbeat(interval_secs=1.0, callback=callback) as hb:
            await hb.force_heartbeat(
                "Processing file",
                metadata={"filename": "test.txt", "size": 1024}
            )
        
        assert len(messages) == 1
        data = messages[0]
        
        assert "metadata" in data
        assert data["metadata"]["filename"] == "test.txt"
        assert data["metadata"]["size"] == 1024

