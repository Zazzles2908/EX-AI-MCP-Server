"""
Tests for Async Concurrent Session Manager

Tests the async version of concurrent session manager for handling async requests.

Created: 2025-10-21
Phase: 2.2.3 - Provider Integration (Async)
"""

import pytest
import asyncio
import time
from src.utils.async_concurrent_session_manager import (
    AsyncSession,
    AsyncConcurrentSessionManager,
    SessionState,
    get_async_session_manager
)


class TestAsyncSession:
    """Tests for AsyncSession class."""
    
    def test_session_creation(self):
        """Test async session creation."""
        session = AsyncSession(
            session_id="test_session",
            request_id="test_request",
            provider="kimi",
            model="moonshot-v1-8k"
        )
        
        assert session.session_id == "test_session"
        assert session.request_id == "test_request"
        assert session.provider == "kimi"
        assert session.model == "moonshot-v1-8k"
        assert session.state == SessionState.IDLE
    
    def test_session_lifecycle(self):
        """Test async session lifecycle."""
        session = AsyncSession(
            session_id="test_session",
            request_id="test_request",
            provider="kimi",
            model="moonshot-v1-8k"
        )
        
        # Start session
        session.start()
        assert session.state == SessionState.PROCESSING
        assert session.started_at is not None
        
        # Complete session
        session.complete({"result": "success"})
        assert session.state == SessionState.COMPLETED
        assert session.result == {"result": "success"}
        assert session.completed_at is not None
    
    def test_session_timeout_detection(self):
        """Test async session timeout detection."""
        session = AsyncSession(
            session_id="test_session",
            request_id="test_request",
            provider="kimi",
            model="moonshot-v1-8k",
            timeout_seconds=0.1
        )
        
        # Not timed out before start
        assert not session.is_timed_out()
        
        # Start and wait
        session.start()
        time.sleep(0.2)
        
        # Should be timed out
        assert session.is_timed_out()


@pytest.mark.asyncio
class TestAsyncConcurrentSessionManager:
    """Tests for AsyncConcurrentSessionManager class."""
    
    async def test_manager_initialization(self):
        """Test async manager initialization."""
        manager = AsyncConcurrentSessionManager(default_timeout=60.0)
        assert manager._default_timeout == 60.0
        assert len(manager._sessions) == 0
    
    async def test_request_id_generation(self):
        """Test request ID generation."""
        manager = AsyncConcurrentSessionManager()
        req_id1 = manager._generate_request_id()
        req_id2 = manager._generate_request_id()
        
        assert req_id1.startswith("req_")
        assert req_id2.startswith("req_")
        assert req_id1 != req_id2
    
    async def test_session_creation_and_retrieval(self):
        """Test async session creation and retrieval."""
        manager = AsyncConcurrentSessionManager()
        
        session = await manager.create_session("kimi", "moonshot-v1-8k")
        assert session.provider == "kimi"
        assert session.model == "moonshot-v1-8k"
        assert session.state == SessionState.ALLOCATED
        
        # Retrieve session
        retrieved = await manager.get_session(session.request_id)
        assert retrieved is not None
        assert retrieved.session_id == session.session_id
    
    async def test_session_release(self):
        """Test async session release."""
        manager = AsyncConcurrentSessionManager()
        
        session = await manager.create_session("kimi", "moonshot-v1-8k")
        request_id = session.request_id
        
        # Session exists
        assert await manager.get_session(request_id) is not None
        
        # Release session
        await manager.release_session(request_id)
        
        # Session no longer exists
        assert await manager.get_session(request_id) is None
    
    async def test_execute_with_session_success(self):
        """Test successful async execution with session."""
        manager = AsyncConcurrentSessionManager()
        
        async def test_func(value: int) -> dict:
            await asyncio.sleep(0.1)
            return {"result": value * 2}
        
        result = await manager.execute_with_session(
            provider="kimi",
            model="moonshot-v1-8k",
            func=test_func,
            value=5
        )
        
        assert result["result"] == 10
        assert "metadata" in result
        assert "session" in result["metadata"]
        assert "session_id" in result["metadata"]["session"]
        assert "request_id" in result["metadata"]["session"]
    
    async def test_execute_with_session_error(self):
        """Test async execution with session error handling."""
        manager = AsyncConcurrentSessionManager()
        
        async def failing_func():
            await asyncio.sleep(0.1)
            raise ValueError("Test error")
        
        with pytest.raises(ValueError, match="Test error"):
            await manager.execute_with_session(
                provider="kimi",
                model="moonshot-v1-8k",
                func=failing_func
            )
    
    async def test_concurrent_sessions(self):
        """Test multiple concurrent async sessions."""
        manager = AsyncConcurrentSessionManager()
        
        async def test_func(delay: float, value: int) -> dict:
            await asyncio.sleep(delay)
            return {"result": value}
        
        # Create 5 concurrent tasks
        tasks = [
            manager.execute_with_session(
                provider="kimi",
                model="moonshot-v1-8k",
                func=test_func,
                delay=0.1,
                value=i
            )
            for i in range(5)
        ]
        
        # Execute concurrently
        results = await asyncio.gather(*tasks)
        
        # Verify all completed
        assert len(results) == 5
        for i, result in enumerate(results):
            assert result["result"] == i
            assert "session" in result["metadata"]
    
    async def test_timeout_cleanup(self):
        """Test async timeout cleanup."""
        manager = AsyncConcurrentSessionManager()
        
        # Create session with short timeout
        session = await manager.create_session(
            "kimi",
            "moonshot-v1-8k",
            timeout_seconds=0.1
        )
        session.start()
        
        # Wait for timeout
        await asyncio.sleep(0.2)
        
        # Cleanup
        cleaned = await manager.cleanup_timed_out_sessions()
        assert cleaned == 1
        
        # Session should be gone
        assert await manager.get_session(session.request_id) is None
    
    async def test_statistics(self):
        """Test async session statistics."""
        manager = AsyncConcurrentSessionManager()
        
        # Create some sessions
        session1 = await manager.create_session("kimi", "moonshot-v1-8k")
        session2 = await manager.create_session("glm", "glm-4.5-flash")
        
        session1.start()
        session2.start()
        
        stats = await manager.get_statistics()
        assert stats["total_sessions"] == 2
        assert stats["active_sessions"] == 2


@pytest.mark.asyncio
class TestGlobalAsyncSessionManager:
    """Tests for global async session manager instance."""
    
    async def test_get_global_instance(self):
        """Test getting global async instance."""
        manager1 = await get_async_session_manager()
        manager2 = await get_async_session_manager()
        
        # Should be same instance
        assert manager1 is manager2
    
    async def test_global_instance_thread_safety(self):
        """Test global async instance thread safety."""
        async def get_manager():
            return await get_async_session_manager()
        
        # Get instance from multiple coroutines
        tasks = [get_manager() for _ in range(10)]
        managers = await asyncio.gather(*tasks)
        
        # All should be same instance
        first = managers[0]
        assert all(m is first for m in managers)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

