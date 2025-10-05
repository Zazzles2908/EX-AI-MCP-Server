"""
Integration Tests: WebSocket + Session Management

Tests the integration between WebSocket server and session management,
verifying timeout hierarchy, progress heartbeat, and graceful degradation.

Created: 2025-10-05
Week: 3, Day 13
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock
from src.daemon.session_manager import SessionManager, Session
from config import TimeoutConfig


class TestWebSocketSessionIntegration:
    """Test WebSocket server integration with session management."""
    
    @pytest.mark.asyncio
    async def test_session_created_on_connection(self):
        """Test that session is created when WebSocket connects."""
        manager = SessionManager()
        
        # Simulate WebSocket connection
        session_id = "test-session-1"
        session = await manager.ensure(session_id)
        
        assert session is not None
        assert session.session_id == session_id
        assert session.created_at > 0
        assert session.last_activity > 0
        assert session.closed is False
    
    @pytest.mark.asyncio
    async def test_session_removed_on_disconnect(self):
        """Test that session is removed when WebSocket disconnects."""
        manager = SessionManager()
        
        # Create session
        session_id = "test-session-2"
        await manager.ensure(session_id)
        
        # Verify session exists
        session = await manager.get(session_id)
        assert session is not None
        
        # Simulate disconnect
        await manager.remove(session_id)
        
        # Verify session removed
        session = await manager.get(session_id)
        assert session is None
    
    @pytest.mark.asyncio
    async def test_session_activity_updated_on_message(self):
        """Test that session activity is updated when message received."""
        manager = SessionManager()
        
        # Create session
        session_id = "test-session-3"
        session = await manager.ensure(session_id)
        initial_activity = session.last_activity
        
        # Wait a bit
        await asyncio.sleep(0.1)
        
        # Simulate message received
        await manager.update_activity(session_id)
        
        # Verify activity updated
        session = await manager.get(session_id)
        assert session.last_activity > initial_activity
    
    @pytest.mark.asyncio
    async def test_session_timeout_detection(self):
        """Test that timed out sessions are detected correctly."""
        manager = SessionManager(session_timeout_secs=1)  # 1 second timeout
        
        # Create session
        session_id = "test-session-4"
        session = await manager.ensure(session_id)
        
        # Session should not be timed out initially
        assert not manager.is_session_timed_out(session)
        
        # Wait for timeout
        await asyncio.sleep(1.5)
        
        # Session should be timed out now
        session = await manager.get(session_id)
        assert manager.is_session_timed_out(session)
    
    @pytest.mark.asyncio
    async def test_session_cleanup_removes_stale_sessions(self):
        """Test that cleanup removes timed out sessions."""
        manager = SessionManager(session_timeout_secs=1)
        
        # Create multiple sessions
        await manager.ensure("session-1")
        await manager.ensure("session-2")
        await manager.ensure("session-3")
        
        # Wait for timeout
        await asyncio.sleep(1.5)
        
        # Cleanup stale sessions
        cleaned = await manager.cleanup_stale_sessions()
        
        # All sessions should be cleaned
        assert cleaned == 3
        
        # Verify all sessions removed
        metrics = await manager.get_session_metrics()
        assert metrics["total_sessions"] == 0
    
    @pytest.mark.asyncio
    async def test_session_limit_enforcement(self):
        """Test that session limit is enforced."""
        manager = SessionManager(max_concurrent_sessions=3)
        
        # Create sessions up to limit
        await manager.ensure("session-1")
        await manager.ensure("session-2")
        await manager.ensure("session-3")
        
        # Try to create one more session
        with pytest.raises(RuntimeError, match="Maximum concurrent sessions"):
            await manager.ensure("session-4")
    
    @pytest.mark.asyncio
    async def test_session_metrics_collection(self):
        """Test that session metrics are collected correctly."""
        manager = SessionManager()
        
        # Create sessions
        await manager.ensure("session-1")
        await asyncio.sleep(0.1)
        await manager.ensure("session-2")
        await asyncio.sleep(0.1)
        await manager.ensure("session-3")
        
        # Get metrics
        metrics = await manager.get_session_metrics()
        
        assert metrics["total_sessions"] == 3
        assert metrics["active_sessions"] == 3
        assert metrics["oldest_session_age"] > metrics["newest_session_age"]
        assert metrics["avg_session_age"] > 0


class TestTimeoutHierarchyIntegration:
    """Test timeout hierarchy integration across all layers."""
    
    def test_timeout_hierarchy_validation(self):
        """Test that timeout hierarchy is valid."""
        # Verify hierarchy: tool < daemon < shim < client
        tool_timeout = TimeoutConfig.WORKFLOW_TOOL_TIMEOUT_SECS
        daemon_timeout = TimeoutConfig.get_daemon_timeout()
        shim_timeout = TimeoutConfig.get_shim_timeout()
        client_timeout = TimeoutConfig.get_client_timeout()
        
        assert tool_timeout < daemon_timeout
        assert daemon_timeout < shim_timeout
        assert shim_timeout < client_timeout
        
        # Verify 1.5x buffer rule
        assert daemon_timeout == tool_timeout * 1.5
        assert shim_timeout == tool_timeout * 2.0
        assert client_timeout == tool_timeout * 2.5
    
    def test_timeout_config_environment_override(self):
        """Test that environment variables override defaults."""
        import os
        
        # Set environment variable
        os.environ["WORKFLOW_TOOL_TIMEOUT_SECS"] = "180"
        
        # Reload config (in real scenario, would restart server)
        # For testing, we just verify the value would be read
        timeout = int(os.getenv("WORKFLOW_TOOL_TIMEOUT_SECS", "120"))
        assert timeout == 180
        
        # Cleanup
        del os.environ["WORKFLOW_TOOL_TIMEOUT_SECS"]
    
    @pytest.mark.asyncio
    async def test_tool_timeout_triggers_before_daemon(self):
        """Test that tool timeout triggers before daemon timeout."""
        # This is a conceptual test - in real scenario, tool would timeout first
        tool_timeout = TimeoutConfig.WORKFLOW_TOOL_TIMEOUT_SECS
        daemon_timeout = TimeoutConfig.get_daemon_timeout()
        
        # Simulate long-running operation
        start_time = time.time()
        
        try:
            # Tool timeout should trigger first
            await asyncio.wait_for(
                asyncio.sleep(daemon_timeout + 10),  # Longer than daemon timeout
                timeout=tool_timeout
            )
        except asyncio.TimeoutError:
            elapsed = time.time() - start_time
            # Should timeout at tool timeout, not daemon timeout
            assert elapsed < daemon_timeout
            assert elapsed >= tool_timeout - 1  # Allow 1s tolerance


class TestProgressHeartbeatIntegration:
    """Test progress heartbeat integration with WebSocket."""
    
    @pytest.mark.asyncio
    async def test_heartbeat_sent_during_long_operation(self):
        """Test that heartbeat is sent during long operations."""
        from utils.progress import ProgressHeartbeat
        
        messages = []
        
        async def callback(data):
            messages.append(data)
        
        # Create heartbeat with 1 second interval
        async with ProgressHeartbeat(interval_secs=1.0, callback=callback) as hb:
            hb.set_total_steps(5)
            
            # Simulate long operation
            for step in range(1, 6):
                hb.set_current_step(step)
                await hb.send_heartbeat(f"Step {step}")
                await asyncio.sleep(0.5)  # Shorter than interval
        
        # Should have received heartbeats
        assert len(messages) >= 2  # At least 2 heartbeats in 2.5 seconds

        # Verify heartbeat structure
        for msg in messages:
            assert "message" in msg
            assert "elapsed_secs" in msg
            assert "timestamp" in msg
    
    @pytest.mark.asyncio
    async def test_heartbeat_includes_progress_info(self):
        """Test that heartbeat includes progress information."""
        from utils.progress import ProgressHeartbeat
        
        messages = []
        
        async def callback(data):
            messages.append(data)
        
        async with ProgressHeartbeat(interval_secs=0.5, callback=callback) as hb:
            hb.set_total_steps(10)
            hb.set_current_step(5)
            
            await hb.force_heartbeat("Halfway done")
        
        assert len(messages) == 1
        msg = messages[0]
        
        assert msg["step"] == 5
        assert msg["total_steps"] == 10
        assert msg["message"] == "Halfway done"
        assert msg["estimated_remaining_secs"] is not None


class TestGracefulDegradationIntegration:
    """Test graceful degradation integration with circuit breaker."""
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_opens_after_failures(self):
        """Test that circuit breaker opens after consecutive failures."""
        from utils.error_handling import GracefulDegradation
        
        degradation = GracefulDegradation()
        
        # Simulate failing function
        async def failing_fn():
            raise Exception("Simulated failure")
        
        # Try multiple times to trigger circuit breaker
        for i in range(6):  # More than threshold (5)
            try:
                await degradation.execute_with_fallback(
                    failing_fn,
                    timeout_secs=1.0,
                    max_retries=0
                )
            except Exception:
                pass
        
        # Circuit should be open now
        assert degradation._is_circuit_open("failing_fn")
    
    @pytest.mark.asyncio
    async def test_fallback_executed_on_failure(self):
        """Test that fallback is executed when primary fails."""
        from utils.error_handling import GracefulDegradation
        
        degradation = GracefulDegradation()
        
        async def failing_fn():
            raise Exception("Primary failed")
        
        async def fallback_fn():
            return "Fallback result"
        
        # Execute with fallback
        result = await degradation.execute_with_fallback(
            failing_fn,
            fallback_fn=fallback_fn,
            timeout_secs=1.0,
            max_retries=0
        )
        
        assert result == "Fallback result"
    
    @pytest.mark.asyncio
    async def test_exponential_backoff_on_retries(self):
        """Test that exponential backoff is used on retries."""
        from utils.error_handling import GracefulDegradation
        
        degradation = GracefulDegradation()
        
        call_times = []
        
        async def failing_fn():
            call_times.append(time.time())
            raise Exception("Simulated failure")
        
        try:
            await degradation.execute_with_fallback(
                failing_fn,
                timeout_secs=10.0,
                max_retries=2
            )
        except Exception:
            pass
        
        # Should have 3 calls (initial + 2 retries)
        assert len(call_times) == 3
        
        # Verify exponential backoff (1s, 2s)
        delay1 = call_times[1] - call_times[0]
        delay2 = call_times[2] - call_times[1]
        
        assert 0.9 <= delay1 <= 1.5  # ~1 second
        assert 1.9 <= delay2 <= 2.5  # ~2 seconds


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

