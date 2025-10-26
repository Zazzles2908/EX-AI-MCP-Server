"""
Async Concurrent Session Manager

Async version of concurrent session manager for handling concurrent async requests
with session-per-request isolation.

Created: 2025-10-21
Phase: 2.2.3 - Provider Integration (Async)
"""

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, Optional

from .request_lifecycle_logger import (
    log_request_received,
    log_request_completed,
    log_request_error,
    log_session_allocated,
    log_session_released
)

_logger = logging.getLogger(__name__)


class SessionState(Enum):
    """Session state enumeration."""
    IDLE = "idle"
    ALLOCATED = "allocated"
    PROCESSING = "processing"
    COMPLETED = "completed"
    TIMEOUT = "timeout"
    ERROR = "error"


@dataclass
class AsyncSession:
    """
    Async session for tracking individual request execution.
    
    Each session represents one request with its own isolated state.
    """
    session_id: str
    request_id: str
    provider: str
    model: str
    state: SessionState = SessionState.IDLE
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    timeout_seconds: float = 30.0
    result: Optional[Any] = None
    error: Optional[str] = None
    
    def start(self) -> None:
        """Mark session as started."""
        self.state = SessionState.PROCESSING
        self.started_at = time.time()
        _logger.debug(f"Session {self.session_id} started for request {self.request_id}")
    
    def complete(self, result: Any) -> None:
        """Mark session as completed with result."""
        self.state = SessionState.COMPLETED
        self.completed_at = time.time()
        self.result = result
        _logger.debug(f"Session {self.session_id} completed for request {self.request_id}")
    
    def fail(self, error: str) -> None:
        """Mark session as failed with error."""
        self.state = SessionState.ERROR
        self.completed_at = time.time()
        self.error = error
        _logger.error(f"Session {self.session_id} failed for request {self.request_id}: {error}")
    
    def is_timed_out(self) -> bool:
        """Check if session has timed out."""
        if not self.started_at:
            return False
        elapsed = time.time() - self.started_at
        return elapsed > self.timeout_seconds
    
    def get_duration(self) -> Optional[float]:
        """Get session duration in seconds."""
        if not self.started_at:
            return None
        end_time = self.completed_at or time.time()
        return end_time - self.started_at


class AsyncConcurrentSessionManager:
    """
    Async concurrent session manager for handling multiple async requests.
    
    PHASE 2.2.3 (2025-10-21): Async version of ConcurrentSessionManager
    
    Provides session-per-request isolation for async operations to prevent
    concurrent requests from blocking each other.
    
    Features:
    - Async session creation and management
    - Thread-safe session storage (asyncio.Lock)
    - Request ID generation and routing
    - Timeout detection and cleanup
    - Session lifecycle tracking
    """
    
    def __init__(self, default_timeout: float = 30.0):
        """
        Initialize async session manager.
        
        Args:
            default_timeout: Default timeout in seconds for sessions
        """
        self._sessions: Dict[str, AsyncSession] = {}
        self._lock = asyncio.Lock()
        self._default_timeout = default_timeout
        _logger.info(f"AsyncConcurrentSessionManager initialized with default timeout: {default_timeout}s")
    
    def _generate_request_id(self) -> str:
        """Generate unique request ID."""
        timestamp = int(time.time() * 1000)
        unique_id = str(uuid.uuid4())[:8]
        return f"req_{unique_id}_{timestamp}"
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID."""
        return f"session_{uuid.uuid4()}"
    
    async def create_session(
        self,
        provider: str,
        model: str,
        request_id: Optional[str] = None,
        timeout_seconds: Optional[float] = None
    ) -> AsyncSession:
        """
        Create a new session for a request.
        
        Args:
            provider: Provider name
            model: Model name
            request_id: Optional request ID (generated if not provided)
            timeout_seconds: Optional timeout override
        
        Returns:
            AsyncSession instance
        """
        async with self._lock:
            req_id = request_id or self._generate_request_id()
            session_id = self._generate_session_id()
            timeout = timeout_seconds if timeout_seconds is not None else self._default_timeout
            
            session = AsyncSession(
                session_id=session_id,
                request_id=req_id,
                provider=provider,
                model=model,
                state=SessionState.ALLOCATED,
                timeout_seconds=timeout
            )
            
            self._sessions[req_id] = session
            log_request_received(req_id, provider, model)
            log_session_allocated(req_id, session_id=session_id)
            
            _logger.info(f"Created session {session_id} for request {req_id} (provider={provider}, model={model})")
            return session
    
    async def get_session(self, request_id: str) -> Optional[AsyncSession]:
        """Get session by request ID."""
        async with self._lock:
            return self._sessions.get(request_id)
    
    async def release_session(self, request_id: str) -> None:
        """Release and remove session."""
        async with self._lock:
            session = self._sessions.pop(request_id, None)
            if session:
                log_session_released(request_id, session_id=session.session_id)
                _logger.info(f"Released session {session.session_id} for request {request_id}")
    
    async def execute_with_session(
        self,
        provider: str,
        model: str,
        func: Callable,
        *args,
        request_id: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
        add_session_context: bool = True,
        **kwargs
    ) -> Any:
        """
        Execute an async function within a managed session.
        
        PHASE 2.2.3 (2025-10-21): Async version with session context support
        
        Args:
            provider: Provider name
            model: Model name
            func: Async function to execute
            *args: Positional arguments for func
            request_id: Optional request ID
            timeout_seconds: Optional timeout override
            add_session_context: If True and result is dict, adds session metadata
            **kwargs: Keyword arguments for func
        
        Returns:
            Function result (with session context added if add_session_context=True and result is dict)
        
        Raises:
            TimeoutError: If execution exceeds timeout
            Exception: Any exception raised by func
        """
        session = None
        
        try:
            session = await self.create_session(provider, model, request_id, timeout_seconds)
            session.start()
            _logger.debug(f"Executing async function in session {session.session_id}")
            
            # Execute async function
            result = await func(*args, **kwargs)
            
            session.complete(result)
            log_request_completed(session.request_id, session_id=session.session_id)
            
            # Add session context to result if requested and result is a dict
            if add_session_context and isinstance(result, dict):
                if 'metadata' not in result:
                    result['metadata'] = {}
                result['metadata']['session'] = {
                    'session_id': session.session_id,
                    'request_id': session.request_id,
                    'duration_seconds': session.get_duration()
                }
            
            return result
            
        except Exception as e:
            if session:
                session.fail(str(e))
                log_request_error(session.request_id, str(e), session_id=session.session_id)
            raise
            
        finally:
            if session:
                await self.release_session(session.request_id)
    
    async def get_active_sessions(self) -> list[AsyncSession]:
        """Get list of active sessions."""
        async with self._lock:
            return [s for s in self._sessions.values() if s.state == SessionState.PROCESSING]
    
    async def cleanup_timed_out_sessions(self) -> int:
        """Clean up timed out sessions. Returns count of cleaned sessions."""
        async with self._lock:
            timed_out = []
            for req_id, session in self._sessions.items():
                if session.is_timed_out():
                    session.state = SessionState.TIMEOUT
                    timed_out.append(req_id)
            
            for req_id in timed_out:
                self._sessions.pop(req_id, None)
                _logger.warning(f"Cleaned up timed out session for request {req_id}")
            
            return len(timed_out)
    
    async def get_statistics(self) -> dict:
        """Get session statistics."""
        async with self._lock:
            total = len(self._sessions)
            by_state = {}
            for session in self._sessions.values():
                state = session.state.value
                by_state[state] = by_state.get(state, 0) + 1
            
            return {
                'total_sessions': total,
                'by_state': by_state,
                'active_sessions': by_state.get('processing', 0)
            }


# Global singleton instance
_global_async_session_manager: Optional[AsyncConcurrentSessionManager] = None
_global_async_lock = asyncio.Lock()


async def get_async_session_manager(default_timeout: float = 30.0) -> AsyncConcurrentSessionManager:
    """
    Get or create global async session manager instance.
    
    Args:
        default_timeout: Default timeout in seconds
    
    Returns:
        AsyncConcurrentSessionManager instance
    """
    global _global_async_session_manager
    
    async with _global_async_lock:
        if _global_async_session_manager is None:
            _global_async_session_manager = AsyncConcurrentSessionManager(default_timeout)
        return _global_async_session_manager


__all__ = [
    'SessionState',
    'AsyncSession',
    'AsyncConcurrentSessionManager',
    'get_async_session_manager'
]

