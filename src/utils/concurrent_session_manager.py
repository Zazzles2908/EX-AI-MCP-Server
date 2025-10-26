"""
Concurrent Session Manager

Manages concurrent request sessions with isolation, routing, and timeout handling.
Implements session-per-request architecture to prevent blocking.

Created: 2025-10-21
Phase: 2.2 - Concurrent Request Handling
"""

import threading
import time
import uuid
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

from src.utils.request_lifecycle_logger import (
    log_request_received,
    log_request_queued,
    log_request_dequeued,
    log_session_allocated,
    log_session_released,
    log_request_completed,
    log_request_timeout,
    log_request_error
)

_logger = logging.getLogger(__name__)


class SessionState(Enum):
    """Session lifecycle states."""
    IDLE = "idle"
    ALLOCATED = "allocated"
    PROCESSING = "processing"
    COMPLETED = "completed"
    TIMEOUT = "timeout"
    ERROR = "error"


@dataclass
class Session:
    """
    Individual session for handling a single request.
    
    Provides isolation between concurrent requests with provider-specific state,
    request context, and timeout handling.
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
    metadata: Dict[str, Any] = field(default_factory=dict)
    result: Optional[Any] = None
    error: Optional[str] = None
    
    def start(self) -> None:
        """Mark session as started."""
        self.state = SessionState.PROCESSING
        self.started_at = time.time()
    
    def complete(self, result: Any) -> None:
        """Mark session as completed with result."""
        self.state = SessionState.COMPLETED
        self.completed_at = time.time()
        self.result = result
    
    def fail(self, error: str) -> None:
        """Mark session as failed with error."""
        self.state = SessionState.ERROR
        self.completed_at = time.time()
        self.error = error
    
    def timeout(self) -> None:
        """Mark session as timed out."""
        self.state = SessionState.TIMEOUT
        self.completed_at = time.time()
    
    def is_active(self) -> bool:
        """Check if session is still active."""
        return self.state in (SessionState.IDLE, SessionState.ALLOCATED, SessionState.PROCESSING)
    
    def is_timed_out(self) -> bool:
        """Check if session has exceeded timeout."""
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


class ConcurrentSessionManager:
    """
    Thread-safe session manager for concurrent request handling.
    
    Implements session-per-request architecture with:
    - Request ID generation and routing
    - Session lifecycle management
    - Isolation between concurrent requests
    - Timeout handling
    - Automatic cleanup
    """
    
    def __init__(
        self,
        default_timeout: float = 30.0,
        max_concurrent_sessions: int = 200,
        max_metadata_size: int = 10240
    ):
        """
        Initialize concurrent session manager.

        PHASE 2.2.5 (2025-10-21): High-Priority Improvements
        - Added max_concurrent_sessions to prevent resource exhaustion
        - Added max_metadata_size to prevent memory bloat
        - Added metrics collection for monitoring
        - Added graceful shutdown support

        PHASE 2.2.5 FIX (2025-10-21): Increased default max_concurrent_sessions to 200

        Args:
            default_timeout: Default timeout in seconds for sessions (default: 30s)
            max_concurrent_sessions: Maximum concurrent sessions allowed (default: 200)
            max_metadata_size: Maximum metadata size in bytes per session (default: 10KB)
        """
        self._sessions: Dict[str, Session] = {}
        self._lock = threading.Lock()
        self._default_timeout = default_timeout
        self._max_concurrent_sessions = max_concurrent_sessions
        self._max_metadata_size = max_metadata_size
        self._shutdown_requested = False

        # Metrics tracking (PHASE 2.2.5)
        # Note: current_metadata_bytes tracks active sessions only (not cumulative)
        self._metrics = {
            'total_sessions_created': 0,
            'total_sessions_completed': 0,
            'total_sessions_timeout': 0,
            'total_sessions_error': 0,
            'peak_concurrent_sessions': 0,
            'current_metadata_bytes': 0,  # FIX: Changed from total to current
            'sessions_rejected_capacity': 0,
            'sessions_rejected_metadata_size': 0
        }

        _logger.info(
            f"ConcurrentSessionManager initialized: "
            f"timeout={default_timeout}s, max_concurrent={max_concurrent_sessions}, "
            f"max_metadata_size={max_metadata_size}B"
        )
    
    def generate_request_id(self) -> str:
        """Generate unique request ID."""
        return f"req_{uuid.uuid4().hex[:16]}_{int(time.time() * 1000)}"

    def _calculate_metadata_size(self, metadata: Dict[str, Any]) -> int:
        """
        Calculate actual metadata size including nested objects.

        PHASE 2.2.5 FIX (2025-10-21): Use JSON serialization for accurate size

        Args:
            metadata: Metadata dictionary to measure

        Returns:
            Size in bytes of JSON-serialized metadata
        """
        import json
        try:
            return len(json.dumps(metadata, default=str).encode('utf-8'))
        except Exception as e:
            _logger.warning(f"Failed to calculate metadata size: {e}, using sys.getsizeof fallback")
            import sys
            return sys.getsizeof(metadata)

    def create_session(
        self,
        provider: str,
        model: str,
        request_id: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
        **metadata
    ) -> Session:
        """
        Create a new session for a request.

        PHASE 2.2.5: Enhanced with capacity limits and metadata size validation.

        Args:
            provider: Provider name (kimi, glm, etc.)
            model: Model name
            request_id: Optional request ID (generated if not provided)
            timeout_seconds: Optional timeout override
            **metadata: Additional metadata to store with session

        Returns:
            Created session

        Raises:
            RuntimeError: If shutdown is requested, capacity limit reached, or metadata too large
        """
        # PHASE 2.2.5 FIX: All validation and creation inside lock for thread safety
        with self._lock:
            # Check if shutdown requested
            if self._shutdown_requested:
                raise RuntimeError("Session manager is shutting down, cannot create new sessions")

            # Check capacity limit
            active_count = sum(1 for s in self._sessions.values() if s.is_active())
            if active_count >= self._max_concurrent_sessions:
                self._metrics['sessions_rejected_capacity'] += 1
                raise RuntimeError(
                    f"Maximum concurrent sessions ({self._max_concurrent_sessions}) reached. "
                    f"Active sessions: {active_count}"
                )

            # Validate metadata size using accurate calculation
            metadata_size = self._calculate_metadata_size(metadata)
            if metadata_size > self._max_metadata_size:
                self._metrics['sessions_rejected_metadata_size'] += 1
                raise RuntimeError(
                    f"Metadata size ({metadata_size} bytes) exceeds limit ({self._max_metadata_size} bytes)"
                )

            # Generate IDs
            if request_id is None:
                request_id = self.generate_request_id()

            session_id = f"session_{uuid.uuid4().hex[:12]}"
            timeout = timeout_seconds if timeout_seconds is not None else self._default_timeout

            # Create session
            session = Session(
                session_id=session_id,
                request_id=request_id,
                provider=provider,
                model=model,
                timeout_seconds=timeout,
                metadata=metadata
            )

            # Store session
            self._sessions[request_id] = session

            # Update metrics
            self._metrics['total_sessions_created'] += 1
            self._metrics['current_metadata_bytes'] += metadata_size  # FIX: Use current not total
            current_active = sum(1 for s in self._sessions.values() if s.is_active())
            if current_active > self._metrics['peak_concurrent_sessions']:
                self._metrics['peak_concurrent_sessions'] = current_active

        log_request_received(request_id, provider, model, session_id=session_id)
        log_session_allocated(request_id, session_id=session_id)

        _logger.debug(f"Created session {session_id} for request {request_id} (metadata: {metadata_size} bytes)")

        return session
    
    def get_session(self, request_id: str) -> Optional[Session]:
        """Get session by request ID."""
        with self._lock:
            return self._sessions.get(request_id)
    
    def release_session(self, request_id: str) -> None:
        """
        Release a session and clean up resources.

        PHASE 2.2.5: Enhanced with metrics tracking.

        Args:
            request_id: Request ID to release
        """
        with self._lock:
            session = self._sessions.get(request_id)
            if session:
                # Update metrics based on session state (PHASE 2.2.5)
                if session.state == SessionState.COMPLETED:
                    self._metrics['total_sessions_completed'] += 1
                elif session.state == SessionState.TIMEOUT:
                    self._metrics['total_sessions_timeout'] += 1
                elif session.state == SessionState.ERROR:
                    self._metrics['total_sessions_error'] += 1

                # FIX: Decrement current metadata bytes when releasing session
                if session.metadata:
                    metadata_size = self._calculate_metadata_size(session.metadata)
                    self._metrics['current_metadata_bytes'] = max(
                        0,
                        self._metrics['current_metadata_bytes'] - metadata_size
                    )

                log_session_released(request_id, session_id=session.session_id)
                del self._sessions[request_id]
                _logger.debug(f"Released session {session.session_id} for request {request_id}")
    
    def execute_with_session(
        self,
        provider: str,
        model: str,
        func: Callable,
        *args,
        request_id: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
        add_session_context: bool = True,
        enforce_timeout: bool = True,
        **kwargs
    ) -> Any:
        """
        Execute a function within a managed session.

        PHASE 2.2.3 (2025-10-21): Enhanced to optionally add session context to result
        PHASE 0.3 (2025-10-24): Added timeout enforcement to prevent provider hangs

        Args:
            provider: Provider name
            model: Model name
            func: Function to execute
            *args: Positional arguments for func
            request_id: Optional request ID
            timeout_seconds: Optional timeout override
            add_session_context: If True and result is dict, adds session metadata
            enforce_timeout: If True, actively enforce timeout (default: True)
            **kwargs: Keyword arguments for func

        Returns:
            Function result (with session context added if add_session_context=True and result is dict)

        Raises:
            TimeoutError: If execution exceeds timeout
            Exception: Any exception raised by func
        """
        session = None

        try:
            session = self.create_session(provider, model, request_id, timeout_seconds)
            session.start()
            _logger.debug(f"Executing function in session {session.session_id} (timeout: {session.timeout_seconds}s, enforce: {enforce_timeout})")

            # PHASE 0.3 (2025-10-24): Add timeout enforcement
            if enforce_timeout and session.timeout_seconds:
                result_container = {'result': None, 'exception': None, 'completed': False}

                def execute_func():
                    try:
                        result_container['result'] = func(*args, **kwargs)
                        result_container['completed'] = True
                    except Exception as e:
                        result_container['exception'] = e
                        result_container['completed'] = True

                # Execute in thread with timeout monitoring
                exec_thread = threading.Thread(target=execute_func, daemon=True)
                exec_thread.start()
                exec_thread.join(timeout=session.timeout_seconds)

                if not result_container['completed']:
                    # Timeout occurred
                    session.timeout()
                    log_request_timeout(session.request_id, timeout_seconds=session.timeout_seconds, session_id=session.session_id)
                    raise TimeoutError(
                        f"{provider} provider timeout after {session.timeout_seconds}s "
                        f"(session: {session.session_id})"
                    )

                if result_container['exception']:
                    raise result_container['exception']

                result = result_container['result']
            else:
                # No timeout enforcement - execute directly
                result = func(*args, **kwargs)

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
                self.release_session(session.request_id)
    
    def get_active_sessions(self) -> list[Session]:
        """Get list of active sessions."""
        with self._lock:
            return [s for s in self._sessions.values() if s.is_active()]
    
    def get_timed_out_sessions(self) -> list[Session]:
        """Get list of sessions that have timed out."""
        with self._lock:
            return [s for s in self._sessions.values() if s.is_timed_out()]
    
    def cleanup_timed_out_sessions(self) -> int:
        """
        Clean up sessions that have exceeded timeout.
        
        Returns:
            Number of sessions cleaned up
        """
        timed_out = self.get_timed_out_sessions()
        cleaned = 0
        
        for session in timed_out:
            session.timeout()
            log_request_timeout(session.request_id, session_id=session.session_id)
            self.release_session(session.request_id)
            cleaned += 1
        
        if cleaned > 0:
            _logger.warning(f"Cleaned up {cleaned} timed out sessions")
        
        return cleaned
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about managed sessions.

        PHASE 2.2.5: Enhanced with lifetime metrics and memory tracking.
        """
        with self._lock:
            total_sessions = len(self._sessions)
            active_sessions = len([s for s in self._sessions.values() if s.is_active()])
            completed_sessions = len([s for s in self._sessions.values() if s.state == SessionState.COMPLETED])
            error_sessions = len([s for s in self._sessions.values() if s.state == SessionState.ERROR])
            timeout_sessions = len([s for s in self._sessions.values() if s.state == SessionState.TIMEOUT])

            # Calculate session durations
            durations = [s.get_duration() for s in self._sessions.values() if s.get_duration() is not None]
            avg_duration = sum(durations) / len(durations) if durations else 0.0

            return {
                # Current state
                'total_sessions': total_sessions,
                'active_sessions': active_sessions,
                'completed_sessions': completed_sessions,
                'error_sessions': error_sessions,
                'timeout_sessions': timeout_sessions,

                # Lifetime metrics (PHASE 2.2.5)
                'lifetime_total_created': self._metrics['total_sessions_created'],
                'lifetime_total_completed': self._metrics['total_sessions_completed'],
                'lifetime_total_timeout': self._metrics['total_sessions_timeout'],
                'lifetime_total_error': self._metrics['total_sessions_error'],
                'peak_concurrent_sessions': self._metrics['peak_concurrent_sessions'],

                # Memory tracking (PHASE 2.2.5 FIX: current_metadata_bytes)
                'current_metadata_bytes': self._metrics['current_metadata_bytes'],
                'sessions_rejected_capacity': self._metrics['sessions_rejected_capacity'],
                'sessions_rejected_metadata_size': self._metrics['sessions_rejected_metadata_size'],

                # Performance metrics
                'average_session_duration': avg_duration,
                'shutdown_requested': self._shutdown_requested
            }

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get detailed metrics for monitoring.

        PHASE 2.2.5: New method for metrics collection.

        Returns:
            Dictionary with detailed metrics including rates and distributions
        """
        stats = self.get_statistics()

        # Calculate success rate
        total_completed = (
            stats['lifetime_total_completed'] +
            stats['lifetime_total_timeout'] +
            stats['lifetime_total_error']
        )
        success_rate = (
            stats['lifetime_total_completed'] / total_completed
            if total_completed > 0 else 0.0
        )

        return {
            **stats,
            'success_rate': success_rate,
            'timeout_rate': stats['lifetime_total_timeout'] / total_completed if total_completed > 0 else 0.0,
            'error_rate': stats['lifetime_total_error'] / total_completed if total_completed > 0 else 0.0,
        }

    def reset_metrics(self) -> None:
        """
        Reset all metrics counters.

        PHASE 2.2.5 FIX: Added to prevent unbounded metrics growth.

        Note: This resets lifetime counters but preserves current session state.
        """
        with self._lock:
            self._metrics['total_sessions_created'] = 0
            self._metrics['total_sessions_completed'] = 0
            self._metrics['total_sessions_timeout'] = 0
            self._metrics['total_sessions_error'] = 0
            self._metrics['peak_concurrent_sessions'] = 0
            # Note: current_metadata_bytes is NOT reset as it tracks active sessions
            self._metrics['sessions_rejected_capacity'] = 0
            self._metrics['sessions_rejected_metadata_size'] = 0

        _logger.info("Session manager metrics reset")

    def shutdown(self, timeout_seconds: float = 30.0) -> Dict[str, Any]:
        """
        Gracefully shutdown the session manager.

        PHASE 2.2.5: Graceful shutdown implementation.

        This method:
        1. Sets shutdown flag to prevent new sessions
        2. Waits for active sessions to complete (up to timeout)
        3. Returns statistics about shutdown process

        Args:
            timeout_seconds: Maximum time to wait for active sessions (default: 30s)

        Returns:
            Dictionary with shutdown statistics
        """
        _logger.info(f"Initiating graceful shutdown (timeout={timeout_seconds}s)")

        with self._lock:
            self._shutdown_requested = True
            initial_active = sum(1 for s in self._sessions.values() if s.is_active())

        start_time = time.time()
        elapsed = 0.0

        # Wait for active sessions to complete
        while elapsed < timeout_seconds:
            with self._lock:
                active_count = sum(1 for s in self._sessions.values() if s.is_active())
                if active_count == 0:
                    break

            time.sleep(0.1)
            elapsed = time.time() - start_time

        # Final statistics
        with self._lock:
            final_active = sum(1 for s in self._sessions.values() if s.is_active())

            shutdown_stats = {
                'shutdown_duration': elapsed,
                'initial_active_sessions': initial_active,
                'final_active_sessions': final_active,
                'sessions_completed_during_shutdown': initial_active - final_active,
                'timeout_reached': elapsed >= timeout_seconds,
                'total_sessions_at_shutdown': len(self._sessions)
            }

        if final_active > 0:
            _logger.warning(
                f"Shutdown completed with {final_active} active sessions remaining "
                f"after {elapsed:.2f}s"
            )
        else:
            _logger.info(f"Graceful shutdown completed successfully in {elapsed:.2f}s")

        return shutdown_stats


# Global instance
_session_manager: Optional[ConcurrentSessionManager] = None
_manager_lock = threading.Lock()


def get_session_manager(
    default_timeout: float = 30.0,
    max_concurrent_sessions: int = 200,
    max_metadata_size: int = 10240
) -> ConcurrentSessionManager:
    """
    Get the global concurrent session manager instance.

    PHASE 2.2.5: Enhanced with capacity and metadata limits.
    PHASE 2.2.5 FIX: Increased default max_concurrent_sessions to 200.

    Args:
        default_timeout: Default timeout in seconds (default: 30s)
        max_concurrent_sessions: Maximum concurrent sessions (default: 200)
        max_metadata_size: Maximum metadata size in bytes (default: 10KB)

    Returns:
        Global ConcurrentSessionManager instance
    """
    global _session_manager

    if _session_manager is None:
        with _manager_lock:
            if _session_manager is None:
                _session_manager = ConcurrentSessionManager(
                    default_timeout=default_timeout,
                    max_concurrent_sessions=max_concurrent_sessions,
                    max_metadata_size=max_metadata_size
                )

    return _session_manager


__all__ = [
    'SessionState',
    'Session',
    'ConcurrentSessionManager',
    'get_session_manager'
]

