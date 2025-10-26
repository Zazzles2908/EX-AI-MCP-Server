"""
Tests for Concurrent Session Manager

Created: 2025-10-21
Phase: 2.2 - Concurrent Request Handling
"""

import pytest
import time
import threading
from concurrent.futures import ThreadPoolExecutor

from src.utils.concurrent_session_manager import (
    ConcurrentSessionManager,
    Session,
    SessionState,
    get_session_manager
)


class TestSession:
    """Tests for Session class."""
    
    def test_session_creation(self):
        """Test session creation with default values."""
        session = Session(
            session_id="test_session_1",
            request_id="test_req_1",
            provider="kimi",
            model="moonshot-v1-8k"
        )
        
        assert session.session_id == "test_session_1"
        assert session.request_id == "test_req_1"
        assert session.provider == "kimi"
        assert session.model == "moonshot-v1-8k"
        assert session.state == SessionState.IDLE
        assert session.is_active()
    
    def test_session_lifecycle(self):
        """Test session state transitions."""
        session = Session(
            session_id="test_session_2",
            request_id="test_req_2",
            provider="glm",
            model="glm-4.5-flash"
        )
        
        # Start session
        session.start()
        assert session.state == SessionState.PROCESSING
        assert session.started_at is not None
        assert session.is_active()
        
        # Complete session
        session.complete({"result": "success"})
        assert session.state == SessionState.COMPLETED
        assert session.completed_at is not None
        assert not session.is_active()
        assert session.result == {"result": "success"}
    
    def test_session_timeout_detection(self):
        """Test session timeout detection."""
        session = Session(
            session_id="test_session_3",
            request_id="test_req_3",
            provider="kimi",
            model="moonshot-v1-8k",
            timeout_seconds=0.1
        )
        
        session.start()
        assert not session.is_timed_out()
        
        time.sleep(0.15)
        assert session.is_timed_out()


class TestConcurrentSessionManager:
    """Tests for ConcurrentSessionManager."""
    
    def test_manager_initialization(self):
        """Test manager initialization."""
        manager = ConcurrentSessionManager(default_timeout=60.0)
        assert manager._default_timeout == 60.0
        
        stats = manager.get_statistics()
        assert stats['total_sessions'] == 0
    
    def test_request_id_generation(self):
        """Test unique request ID generation."""
        manager = ConcurrentSessionManager()
        
        id1 = manager.generate_request_id()
        id2 = manager.generate_request_id()
        
        assert id1 != id2
        assert id1.startswith("req_")
        assert id2.startswith("req_")
    
    def test_session_creation_and_retrieval(self):
        """Test creating and retrieving sessions."""
        manager = ConcurrentSessionManager()
        
        session = manager.create_session(
            provider="kimi",
            model="moonshot-v1-8k"
        )
        
        assert session is not None
        assert session.provider == "kimi"
        assert session.model == "moonshot-v1-8k"
        
        # Retrieve session
        retrieved = manager.get_session(session.request_id)
        assert retrieved is not None
        assert retrieved.session_id == session.session_id
    
    def test_session_release(self):
        """Test session release and cleanup."""
        manager = ConcurrentSessionManager()
        
        session = manager.create_session(
            provider="glm",
            model="glm-4.5-flash"
        )
        
        request_id = session.request_id
        
        # Verify session exists
        assert manager.get_session(request_id) is not None
        
        # Release session
        manager.release_session(request_id)
        
        # Verify session is gone
        assert manager.get_session(request_id) is None
    
    def test_execute_with_session_success(self):
        """Test successful execution within session."""
        manager = ConcurrentSessionManager()
        
        def test_func(x, y):
            return x + y
        
        result = manager.execute_with_session(
            "kimi",
            "moonshot-v1-8k",
            test_func,
            10,
            20
        )
        
        assert result == 30
    
    def test_execute_with_session_error(self):
        """Test error handling within session."""
        manager = ConcurrentSessionManager()
        
        def failing_func():
            raise ValueError("Test error")
        
        with pytest.raises(ValueError, match="Test error"):
            manager.execute_with_session(
                "glm",
                "glm-4.5-flash",
                failing_func
            )
    
    def test_concurrent_sessions(self):
        """Test multiple concurrent sessions."""
        manager = ConcurrentSessionManager()
        results = []
        
        def process_request(value):
            time.sleep(0.1)
            return value * 2
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for i in range(5):
                future = executor.submit(
                    manager.execute_with_session,
                    "kimi",
                    "moonshot-v1-8k",
                    process_request,
                    i
                )
                futures.append(future)
            
            for future in futures:
                results.append(future.result())
        
        assert len(results) == 5
        assert sorted(results) == [0, 2, 4, 6, 8]
    
    def test_timeout_cleanup(self):
        """Test cleanup of timed out sessions."""
        manager = ConcurrentSessionManager()
        
        # Create session with short timeout
        session = manager.create_session(
            provider="kimi",
            model="moonshot-v1-8k",
            timeout_seconds=0.1
        )
        
        session.start()
        time.sleep(0.15)
        
        # Cleanup timed out sessions
        cleaned = manager.cleanup_timed_out_sessions()
        assert cleaned == 1
        
        # Verify session is gone
        assert manager.get_session(session.request_id) is None
    
    def test_statistics(self):
        """Test session statistics."""
        manager = ConcurrentSessionManager()
        
        # Create some sessions
        session1 = manager.create_session("kimi", "moonshot-v1-8k")
        session2 = manager.create_session("glm", "glm-4.5-flash")
        
        stats = manager.get_statistics()
        assert stats['total_sessions'] == 2
        assert stats['active_sessions'] == 2
        
        # Complete one session
        session1.complete({"result": "done"})
        
        stats = manager.get_statistics()
        assert stats['completed_sessions'] == 1


class TestGlobalSessionManager:
    """Tests for global session manager instance."""
    
    def test_get_global_instance(self):
        """Test getting global session manager instance."""
        manager1 = get_session_manager()
        manager2 = get_session_manager()
        
        # Should be same instance
        assert manager1 is manager2
    
    def test_global_instance_thread_safety(self):
        """Test thread-safe access to global instance."""
        managers = []
        
        def get_manager():
            managers.append(get_session_manager())
        
        threads = [threading.Thread(target=get_manager) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # All should be same instance
        assert len(set(id(m) for m in managers)) == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

