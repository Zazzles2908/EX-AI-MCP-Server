"""
Tests for Phase 2.2.5 High-Priority Improvements

Tests session metadata size limits, graceful shutdown, and metrics collection.

Created: 2025-10-21
Phase: 2.2.5 - High-Priority Improvements
"""

import pytest
import time
import threading
from src.utils.concurrent_session_manager import (
    ConcurrentSessionManager,
    SessionState
)


class TestSessionMetadataSizeLimits:
    """Tests for session metadata size limits."""
    
    def test_metadata_within_limit(self):
        """Test that sessions with small metadata are accepted."""
        manager = ConcurrentSessionManager(max_metadata_size=10240)
        
        # Small metadata should be accepted
        session = manager.create_session(
            provider="test",
            model="test-model",
            small_data="test"
        )
        
        assert session is not None
        assert session.provider == "test"
    
    def test_metadata_exceeds_limit(self):
        """Test that sessions with large metadata are rejected."""
        manager = ConcurrentSessionManager(max_metadata_size=100)
        
        # Large metadata should be rejected
        with pytest.raises(RuntimeError, match="Metadata size.*exceeds limit"):
            manager.create_session(
                provider="test",
                model="test-model",
                large_data="x" * 10000  # 10KB of data
            )
        
        # Verify rejection was tracked in metrics
        stats = manager.get_statistics()
        assert stats['sessions_rejected_metadata_size'] == 1
    
    def test_metadata_size_tracking(self):
        """Test that metadata size is tracked in metrics."""
        manager = ConcurrentSessionManager(max_metadata_size=10240)

        # Create sessions with metadata
        manager.create_session(provider="test", model="test1", data="small")
        manager.create_session(provider="test", model="test2", data="medium" * 10)

        stats = manager.get_statistics()
        # FIX: Changed from total_metadata_bytes to current_metadata_bytes
        assert stats['current_metadata_bytes'] > 0


class TestConcurrentSessionLimits:
    """Tests for concurrent session limits."""
    
    def test_within_capacity_limit(self):
        """Test that sessions within capacity limit are accepted."""
        manager = ConcurrentSessionManager(max_concurrent_sessions=5)
        
        # Create 5 sessions (at limit)
        sessions = []
        for i in range(5):
            session = manager.create_session(provider="test", model=f"model-{i}")
            sessions.append(session)
        
        assert len(sessions) == 5
        stats = manager.get_statistics()
        assert stats['active_sessions'] == 5
    
    def test_exceeds_capacity_limit(self):
        """Test that sessions exceeding capacity limit are rejected."""
        manager = ConcurrentSessionManager(max_concurrent_sessions=3)
        
        # Create 3 sessions (at limit)
        for i in range(3):
            manager.create_session(provider="test", model=f"model-{i}")
        
        # 4th session should be rejected
        with pytest.raises(RuntimeError, match="Maximum concurrent sessions.*reached"):
            manager.create_session(provider="test", model="model-4")
        
        # Verify rejection was tracked
        stats = manager.get_statistics()
        assert stats['sessions_rejected_capacity'] == 1
    
    def test_capacity_freed_after_release(self):
        """Test that capacity is freed after releasing sessions."""
        manager = ConcurrentSessionManager(max_concurrent_sessions=2)
        
        # Create 2 sessions (at limit)
        session1 = manager.create_session(provider="test", model="model-1")
        session2 = manager.create_session(provider="test", model="model-2")
        
        # Release one session
        manager.release_session(session1.request_id)
        
        # Should be able to create another session now
        session3 = manager.create_session(provider="test", model="model-3")
        assert session3 is not None


class TestGracefulShutdown:
    """Tests for graceful shutdown functionality."""
    
    def test_shutdown_with_no_active_sessions(self):
        """Test shutdown when no sessions are active."""
        manager = ConcurrentSessionManager()
        
        shutdown_stats = manager.shutdown(timeout_seconds=5.0)
        
        assert shutdown_stats['initial_active_sessions'] == 0
        assert shutdown_stats['final_active_sessions'] == 0
        assert shutdown_stats['shutdown_duration'] < 1.0
        assert not shutdown_stats['timeout_reached']
    
    def test_shutdown_prevents_new_sessions(self):
        """Test that shutdown prevents creation of new sessions."""
        manager = ConcurrentSessionManager()
        
        # Initiate shutdown
        manager.shutdown(timeout_seconds=1.0)
        
        # Attempt to create new session should fail
        with pytest.raises(RuntimeError, match="shutting down"):
            manager.create_session(provider="test", model="test-model")
    
    def test_shutdown_waits_for_active_sessions(self):
        """Test that shutdown waits for active sessions to complete."""
        manager = ConcurrentSessionManager()
        
        # Create and start a session
        session = manager.create_session(provider="test", model="test-model")
        session.start()
        
        # Shutdown in background thread
        shutdown_stats = {}
        def shutdown_thread():
            nonlocal shutdown_stats
            shutdown_stats.update(manager.shutdown(timeout_seconds=2.0))
        
        thread = threading.Thread(target=shutdown_thread)
        thread.start()
        
        # Wait a bit, then complete the session
        time.sleep(0.5)
        session.complete(result="test")
        
        # Wait for shutdown to complete
        thread.join(timeout=3.0)
        
        assert shutdown_stats['initial_active_sessions'] == 1
        assert shutdown_stats['final_active_sessions'] == 0
        assert shutdown_stats['sessions_completed_during_shutdown'] == 1
    
    def test_shutdown_timeout(self):
        """Test that shutdown times out if sessions don't complete."""
        manager = ConcurrentSessionManager()
        
        # Create and start a session that won't complete
        session = manager.create_session(provider="test", model="test-model")
        session.start()
        
        # Shutdown with short timeout
        shutdown_stats = manager.shutdown(timeout_seconds=0.5)
        
        assert shutdown_stats['initial_active_sessions'] == 1
        assert shutdown_stats['final_active_sessions'] == 1
        assert shutdown_stats['timeout_reached']


class TestMetricsCollection:
    """Tests for metrics collection functionality."""
    
    def test_session_creation_metrics(self):
        """Test that session creation is tracked in metrics."""
        manager = ConcurrentSessionManager()
        
        # Create 3 sessions
        for i in range(3):
            manager.create_session(provider="test", model=f"model-{i}")
        
        stats = manager.get_statistics()
        assert stats['lifetime_total_created'] == 3
    
    def test_session_completion_metrics(self):
        """Test that session completion is tracked in metrics."""
        manager = ConcurrentSessionManager()
        
        # Create, complete, and release sessions
        session1 = manager.create_session(provider="test", model="model-1")
        session1.start()
        session1.complete(result="success")
        manager.release_session(session1.request_id)
        
        session2 = manager.create_session(provider="test", model="model-2")
        session2.start()
        session2.fail(error="test error")
        manager.release_session(session2.request_id)
        
        session3 = manager.create_session(provider="test", model="model-3")
        session3.start()
        session3.timeout()
        manager.release_session(session3.request_id)
        
        stats = manager.get_statistics()
        assert stats['lifetime_total_completed'] == 1
        assert stats['lifetime_total_error'] == 1
        assert stats['lifetime_total_timeout'] == 1
    
    def test_peak_concurrent_sessions(self):
        """Test that peak concurrent sessions is tracked."""
        manager = ConcurrentSessionManager()
        
        # Create 5 sessions
        sessions = []
        for i in range(5):
            session = manager.create_session(provider="test", model=f"model-{i}")
            sessions.append(session)
        
        stats = manager.get_statistics()
        assert stats['peak_concurrent_sessions'] == 5
        
        # Release 3 sessions
        for i in range(3):
            manager.release_session(sessions[i].request_id)
        
        # Peak should still be 5
        stats = manager.get_statistics()
        assert stats['peak_concurrent_sessions'] == 5
        assert stats['active_sessions'] == 2
    
    def test_get_metrics_with_rates(self):
        """Test that get_metrics() returns success/error rates."""
        manager = ConcurrentSessionManager()
        
        # Create and complete sessions with different outcomes
        for i in range(7):
            session = manager.create_session(provider="test", model=f"model-{i}")
            session.start()
            if i < 5:
                session.complete(result="success")
            elif i < 6:
                session.fail(error="error")
            else:
                session.timeout()
            manager.release_session(session.request_id)
        
        metrics = manager.get_metrics()
        
        # 5 success, 1 error, 1 timeout = 7 total
        assert metrics['success_rate'] == pytest.approx(5/7, rel=0.01)
        assert metrics['error_rate'] == pytest.approx(1/7, rel=0.01)
        assert metrics['timeout_rate'] == pytest.approx(1/7, rel=0.01)
    
    def test_average_session_duration(self):
        """Test that average session duration is calculated."""
        manager = ConcurrentSessionManager()
        
        # Create sessions with known durations
        session1 = manager.create_session(provider="test", model="model-1")
        session1.start()
        time.sleep(0.1)
        session1.complete(result="success")
        
        session2 = manager.create_session(provider="test", model="model-2")
        session2.start()
        time.sleep(0.2)
        session2.complete(result="success")
        
        stats = manager.get_statistics()
        assert stats['average_session_duration'] > 0.0
        assert stats['average_session_duration'] < 1.0  # Should be under 1 second


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

