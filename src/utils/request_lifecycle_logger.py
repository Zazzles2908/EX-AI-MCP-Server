"""
Request Lifecycle Logger

Structured logging for tracking request lifecycle and diagnosing concurrent request issues.
Logs key events: request receipt, queue entry/exit, session allocation/release,
provider response, and blocking operations.

Created: 2025-10-21
Phase: 2.2 - Concurrent Request Handling
"""

import logging
import time
import threading
from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field, asdict
from enum import Enum

_logger = logging.getLogger(__name__)


class RequestPhase(Enum):
    """Request lifecycle phases."""
    RECEIVED = "received"
    QUEUED = "queued"
    DEQUEUED = "dequeued"
    SESSION_ALLOCATED = "session_allocated"
    PROVIDER_CALL_START = "provider_call_start"
    PROVIDER_CALL_END = "provider_call_end"
    SESSION_RELEASED = "session_released"
    COMPLETED = "completed"
    TIMEOUT = "timeout"
    ERROR = "error"


@dataclass
class RequestLifecycleEvent:
    """Single event in request lifecycle."""
    request_id: str
    phase: RequestPhase
    timestamp: float = field(default_factory=time.time)
    provider: Optional[str] = None
    model: Optional[str] = None
    duration_ms: Optional[float] = None
    thread_id: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging."""
        data = asdict(self)
        data['phase'] = self.phase.value
        data['timestamp_iso'] = datetime.fromtimestamp(self.timestamp).isoformat()
        return data


class RequestLifecycleLogger:
    """
    Tracks and logs request lifecycle events for concurrent request diagnostics.
    
    Thread-safe implementation for tracking multiple concurrent requests.
    """
    
    def __init__(self):
        self._events: Dict[str, list[RequestLifecycleEvent]] = {}
        self._lock = threading.Lock()
        self._start_times: Dict[str, float] = {}
    
    def log_event(
        self,
        request_id: str,
        phase: RequestPhase,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        **metadata
    ) -> None:
        """
        Log a lifecycle event for a request.
        
        Args:
            request_id: Unique request identifier
            phase: Current phase of the request
            provider: Provider name (kimi, glm, etc.)
            model: Model name
            **metadata: Additional metadata to log
        """
        thread_id = threading.get_ident()
        
        # Calculate duration if this is a completion event
        duration_ms = None
        if phase in (RequestPhase.COMPLETED, RequestPhase.TIMEOUT, RequestPhase.ERROR):
            with self._lock:
                if request_id in self._start_times:
                    duration_ms = (time.time() - self._start_times[request_id]) * 1000
                    del self._start_times[request_id]
        elif phase == RequestPhase.RECEIVED:
            with self._lock:
                self._start_times[request_id] = time.time()
        
        event = RequestLifecycleEvent(
            request_id=request_id,
            phase=phase,
            provider=provider,
            model=model,
            duration_ms=duration_ms,
            thread_id=thread_id,
            metadata=metadata
        )
        
        with self._lock:
            if request_id not in self._events:
                self._events[request_id] = []
            self._events[request_id].append(event)
        
        # Log to standard logger
        log_data = event.to_dict()
        _logger.info(
            f"Request lifecycle: {phase.value} | "
            f"request_id={request_id} | "
            f"provider={provider} | "
            f"model={model} | "
            f"thread={thread_id} | "
            f"duration_ms={duration_ms} | "
            f"metadata={metadata}"
        )
    
    def get_request_events(self, request_id: str) -> list[RequestLifecycleEvent]:
        """Get all events for a specific request."""
        with self._lock:
            return self._events.get(request_id, []).copy()
    
    def get_all_events(self) -> Dict[str, list[RequestLifecycleEvent]]:
        """Get all tracked events."""
        with self._lock:
            return {k: v.copy() for k, v in self._events.items()}
    
    def get_active_requests(self) -> list[str]:
        """Get list of request IDs that haven't completed."""
        with self._lock:
            active = []
            for request_id, events in self._events.items():
                last_phase = events[-1].phase if events else None
                if last_phase not in (RequestPhase.COMPLETED, RequestPhase.TIMEOUT, RequestPhase.ERROR):
                    active.append(request_id)
            return active
    
    def get_request_duration(self, request_id: str) -> Optional[float]:
        """Get total duration for a request in milliseconds."""
        events = self.get_request_events(request_id)
        if not events:
            return None
        
        start_time = events[0].timestamp
        end_event = next(
            (e for e in reversed(events) if e.phase in (RequestPhase.COMPLETED, RequestPhase.TIMEOUT, RequestPhase.ERROR)),
            None
        )
        
        if end_event:
            return (end_event.timestamp - start_time) * 1000
        else:
            # Still active
            return (time.time() - start_time) * 1000
    
    def get_phase_duration(self, request_id: str, phase: RequestPhase) -> Optional[float]:
        """Get duration spent in a specific phase in milliseconds."""
        events = self.get_request_events(request_id)
        if not events:
            return None
        
        phase_start = next((e for e in events if e.phase == phase), None)
        if not phase_start:
            return None
        
        # Find next phase
        phase_idx = events.index(phase_start)
        if phase_idx + 1 < len(events):
            next_event = events[phase_idx + 1]
            return (next_event.timestamp - phase_start.timestamp) * 1000
        else:
            # Still in this phase
            return (time.time() - phase_start.timestamp) * 1000
    
    def cleanup_completed(self, max_age_seconds: int = 3600) -> int:
        """
        Remove completed requests older than max_age_seconds.
        
        Returns:
            Number of requests cleaned up
        """
        cutoff_time = time.time() - max_age_seconds
        cleaned = 0
        
        with self._lock:
            to_remove = []
            for request_id, events in self._events.items():
                if not events:
                    to_remove.append(request_id)
                    continue
                
                last_event = events[-1]
                if (last_event.phase in (RequestPhase.COMPLETED, RequestPhase.TIMEOUT, RequestPhase.ERROR) and
                    last_event.timestamp < cutoff_time):
                    to_remove.append(request_id)
            
            for request_id in to_remove:
                del self._events[request_id]
                cleaned += 1
        
        if cleaned > 0:
            _logger.debug(f"Cleaned up {cleaned} completed requests older than {max_age_seconds}s")
        
        return cleaned
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about tracked requests."""
        with self._lock:
            total_requests = len(self._events)
            active_requests = len(self.get_active_requests())
            completed_requests = total_requests - active_requests
            
            # Calculate average duration for completed requests
            durations = []
            for request_id, events in self._events.items():
                if events and events[-1].phase in (RequestPhase.COMPLETED, RequestPhase.TIMEOUT, RequestPhase.ERROR):
                    duration = self.get_request_duration(request_id)
                    if duration is not None:
                        durations.append(duration)
            
            avg_duration = sum(durations) / len(durations) if durations else 0
            min_duration = min(durations) if durations else 0
            max_duration = max(durations) if durations else 0
            
            return {
                'total_requests': total_requests,
                'active_requests': active_requests,
                'completed_requests': completed_requests,
                'avg_duration_ms': avg_duration,
                'min_duration_ms': min_duration,
                'max_duration_ms': max_duration,
                'total_events': sum(len(events) for events in self._events.values())
            }


# Global instance
_lifecycle_logger: Optional[RequestLifecycleLogger] = None
_logger_lock = threading.Lock()


def get_lifecycle_logger() -> RequestLifecycleLogger:
    """Get the global request lifecycle logger instance."""
    global _lifecycle_logger
    
    if _lifecycle_logger is None:
        with _logger_lock:
            if _lifecycle_logger is None:
                _lifecycle_logger = RequestLifecycleLogger()
    
    return _lifecycle_logger


# Convenience functions
def log_request_received(request_id: str, provider: str, model: str, **metadata):
    """Log request received event."""
    get_lifecycle_logger().log_event(request_id, RequestPhase.RECEIVED, provider, model, **metadata)


def log_request_queued(request_id: str, **metadata):
    """Log request queued event."""
    get_lifecycle_logger().log_event(request_id, RequestPhase.QUEUED, **metadata)


def log_request_dequeued(request_id: str, **metadata):
    """Log request dequeued event."""
    get_lifecycle_logger().log_event(request_id, RequestPhase.DEQUEUED, **metadata)


def log_session_allocated(request_id: str, **metadata):
    """Log session allocated event."""
    get_lifecycle_logger().log_event(request_id, RequestPhase.SESSION_ALLOCATED, **metadata)


def log_provider_call_start(request_id: str, provider: str, model: str, **metadata):
    """Log provider call start event."""
    get_lifecycle_logger().log_event(request_id, RequestPhase.PROVIDER_CALL_START, provider, model, **metadata)


def log_provider_call_end(request_id: str, provider: str, model: str, **metadata):
    """Log provider call end event."""
    get_lifecycle_logger().log_event(request_id, RequestPhase.PROVIDER_CALL_END, provider, model, **metadata)


def log_session_released(request_id: str, **metadata):
    """Log session released event."""
    get_lifecycle_logger().log_event(request_id, RequestPhase.SESSION_RELEASED, **metadata)


def log_request_completed(request_id: str, **metadata):
    """Log request completed event."""
    get_lifecycle_logger().log_event(request_id, RequestPhase.COMPLETED, **metadata)


def log_request_timeout(request_id: str, **metadata):
    """Log request timeout event."""
    get_lifecycle_logger().log_event(request_id, RequestPhase.TIMEOUT, **metadata)


def log_request_error(request_id: str, error: str, **metadata):
    """Log request error event."""
    get_lifecycle_logger().log_event(request_id, RequestPhase.ERROR, error=error, **metadata)

