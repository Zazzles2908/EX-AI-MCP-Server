"""
Tests for Session Management Cleanup

This test suite validates:
1. Session creation and cleanup
2. Session timeout detection and cleanup
3. Session activity tracking
4. Session limits enforcement
5. Session metrics collection
6. Stale session cleanup
"""

import pytest
import asyncio
import time
from src.daemon.session_manager import SessionManager, Session


class TestSessionCreation:
    """Test session creation and basic operations."""
    
    @pytest.mark.asyncio
    async def test_create_session(self):
        """Test creating a new session."""
        manager = SessionManager()
        session = await manager.ensure("test-session-1")
        
        assert session is not None
        assert session.session_id == "test-session-1"
        assert session.created_at > 0
        assert session.last_activity > 0
        assert not session.closed
    
    @pytest.mark.asyncio
    async def test_create_session_with_auto_id(self):
        """Test creating session with auto-generated ID."""
        manager = SessionManager()
        session = await manager.ensure(None)
        
        assert session is not None
        assert session.session_id is not None
        assert len(session.session_id) > 0
    
    @pytest.mark.asyncio
    async def test_get_existing_session(self):
        """Test retrieving existing session."""
        manager = SessionManager()
        session1 = await manager.ensure("test-session-2")
        session2 = await manager.get("test-session-2")
        
        assert session1 is session2
        assert session1.session_id == session2.session_id
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_session(self):
        """Test retrieving non-existent session returns None."""
        manager = SessionManager()
        session = await manager.get("nonexistent")
        
        assert session is None


class TestSessionTimeout:
    """Test session timeout detection and cleanup."""
    
    @pytest.mark.asyncio
    async def test_session_not_timed_out_when_active(self):
        """Test active session is not timed out."""
        manager = SessionManager(session_timeout_secs=10)
        session = await manager.ensure("test-session-3")
        
        is_timed_out = manager.is_session_timed_out(session)
        assert not is_timed_out
    
    @pytest.mark.asyncio
    async def test_session_timed_out_after_inactivity(self):
        """Test session times out after inactivity period."""
        manager = SessionManager(session_timeout_secs=1)
        session = await manager.ensure("test-session-4")
        
        # Wait for timeout
        await asyncio.sleep(1.5)
        
        is_timed_out = manager.is_session_timed_out(session)
        assert is_timed_out
    
    @pytest.mark.asyncio
    async def test_update_activity_prevents_timeout(self):
        """Test updating activity prevents timeout."""
        manager = SessionManager(session_timeout_secs=2)
        session = await manager.ensure("test-session-5")
        
        # Wait half the timeout
        await asyncio.sleep(1)
        
        # Update activity
        await manager.update_activity("test-session-5")
        
        # Wait another half timeout
        await asyncio.sleep(1)
        
        # Should not be timed out because we updated activity
        is_timed_out = manager.is_session_timed_out(session)
        assert not is_timed_out
    
    @pytest.mark.asyncio
    async def test_cleanup_stale_sessions(self):
        """Test cleanup of stale sessions."""
        manager = SessionManager(session_timeout_secs=1)
        
        # Create multiple sessions
        await manager.ensure("session-1")
        await manager.ensure("session-2")
        await manager.ensure("session-3")
        
        # Wait for timeout
        await asyncio.sleep(1.5)
        
        # Cleanup stale sessions
        cleaned = await manager.cleanup_stale_sessions()
        
        assert cleaned == 3
        
        # Verify all sessions removed
        session_ids = await manager.list_ids()
        assert len(session_ids) == 0


class TestSessionLimits:
    """Test session limit enforcement."""
    
    @pytest.mark.asyncio
    async def test_session_limit_not_exceeded(self):
        """Test creating sessions within limit."""
        manager = SessionManager(max_concurrent_sessions=5)
        
        # Create sessions within limit
        for i in range(5):
            session = await manager.ensure(f"session-{i}")
            assert session is not None
        
        session_ids = await manager.list_ids()
        assert len(session_ids) == 5
    
    @pytest.mark.asyncio
    async def test_session_limit_exceeded(self):
        """Test creating session beyond limit raises error."""
        manager = SessionManager(max_concurrent_sessions=3)
        
        # Create sessions up to limit
        for i in range(3):
            await manager.ensure(f"session-{i}")
        
        # Try to create one more
        with pytest.raises(RuntimeError, match="Maximum concurrent sessions"):
            await manager.ensure("session-overflow")
    
    @pytest.mark.asyncio
    async def test_session_limit_after_cleanup(self):
        """Test can create new session after cleanup."""
        manager = SessionManager(max_concurrent_sessions=2, session_timeout_secs=1)
        
        # Create sessions up to limit
        await manager.ensure("session-1")
        await manager.ensure("session-2")
        
        # Wait for timeout
        await asyncio.sleep(1.5)
        
        # Cleanup stale sessions
        await manager.cleanup_stale_sessions()
        
        # Should be able to create new session
        session = await manager.ensure("session-3")
        assert session is not None


class TestSessionMetrics:
    """Test session metrics collection."""
    
    @pytest.mark.asyncio
    async def test_get_session_metrics(self):
        """Test getting session metrics."""
        manager = SessionManager()
        
        # Create some sessions
        await manager.ensure("session-1")
        await manager.ensure("session-2")
        
        metrics = await manager.get_session_metrics()
        
        assert metrics is not None
        assert "total_sessions" in metrics
        assert "active_sessions" in metrics
        assert metrics["total_sessions"] == 2
        assert metrics["active_sessions"] == 2
    
    @pytest.mark.asyncio
    async def test_session_duration_tracking(self):
        """Test session duration is tracked."""
        manager = SessionManager()
        session = await manager.ensure("session-1")
        
        # Wait a bit
        await asyncio.sleep(0.5)
        
        # Get session duration
        duration = time.time() - session.created_at
        assert duration >= 0.5
    
    @pytest.mark.asyncio
    async def test_metrics_after_cleanup(self):
        """Test metrics updated after cleanup."""
        manager = SessionManager(session_timeout_secs=1)
        
        # Create sessions
        await manager.ensure("session-1")
        await manager.ensure("session-2")
        
        # Wait for timeout
        await asyncio.sleep(1.5)
        
        # Cleanup
        await manager.cleanup_stale_sessions()
        
        # Check metrics
        metrics = await manager.get_session_metrics()
        assert metrics["active_sessions"] == 0


class TestSessionActivityTracking:
    """Test session activity tracking."""
    
    @pytest.mark.asyncio
    async def test_last_activity_updated_on_creation(self):
        """Test last_activity is set on creation."""
        manager = SessionManager()
        session = await manager.ensure("session-1")
        
        assert session.last_activity > 0
        assert session.last_activity >= session.created_at
    
    @pytest.mark.asyncio
    async def test_last_activity_updated_on_update(self):
        """Test last_activity is updated."""
        manager = SessionManager()
        session = await manager.ensure("session-1")
        
        original_activity = session.last_activity
        
        # Wait a bit
        await asyncio.sleep(0.5)
        
        # Update activity
        await manager.update_activity("session-1")
        
        # Get updated session
        updated_session = await manager.get("session-1")
        assert updated_session.last_activity > original_activity
    
    @pytest.mark.asyncio
    async def test_inactive_time_calculation(self):
        """Test calculating inactive time."""
        manager = SessionManager()
        session = await manager.ensure("session-1")
        
        # Wait a bit
        await asyncio.sleep(0.5)
        
        # Calculate inactive time
        inactive_time = time.time() - session.last_activity
        assert inactive_time >= 0.5


class TestSessionRemoval:
    """Test session removal."""
    
    @pytest.mark.asyncio
    async def test_remove_session(self):
        """Test removing a session."""
        manager = SessionManager()
        await manager.ensure("session-1")
        
        # Verify session exists
        session = await manager.get("session-1")
        assert session is not None
        
        # Remove session
        await manager.remove("session-1")
        
        # Verify session removed
        session = await manager.get("session-1")
        assert session is None
    
    @pytest.mark.asyncio
    async def test_remove_nonexistent_session(self):
        """Test removing non-existent session doesn't error."""
        manager = SessionManager()
        
        # Should not raise error
        await manager.remove("nonexistent")


class TestSessionManagerSingleton:
    """Test SessionManager can be used as singleton."""
    
    @pytest.mark.asyncio
    async def test_multiple_instances_independent(self):
        """Test multiple SessionManager instances are independent."""
        manager1 = SessionManager()
        manager2 = SessionManager()
        
        await manager1.ensure("session-1")
        
        # manager2 should not have session-1
        session = await manager2.get("session-1")
        assert session is None

