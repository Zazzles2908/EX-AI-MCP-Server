"""
Session Tracker Module

Tracks session metrics for monitoring dashboard.

Split from monitoring_endpoint.py (2025-11-03) to eliminate god object.
Originally part of 1,467-line monitoring_endpoint.py file.

Responsibilities:
- Track active sessions
- Track session metrics
- Provide session statistics
"""

from typing import Dict
from collections import defaultdict


class SessionTracker:
    """
    Track session metrics for monitoring dashboard.

    Monitors:
    - Active sessions
    - Session creation/destruction
    - Session duration
    - Session-related events
    """

    def __init__(self):
        self.sessions: Dict[str, Dict] = {}
        self.metrics = {
            'total_sessions': 0,
            'active_sessions': 0,
            'session_events': defaultdict(int)
        }

    def register_session(self, session_id: str, session_data: Dict) -> None:
        """Register a new session"""
        self.sessions[session_id] = session_data
        self.metrics['total_sessions'] += 1
        self.metrics['active_sessions'] += 1
        self.metrics['session_events']['created'] += 1

    def unregister_session(self, session_id: str) -> None:
        """Unregister a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            self.metrics['active_sessions'] -= 1
            self.metrics['session_events']['destroyed'] += 1

    def record_event(self, event_type: str) -> None:
        """Record a session event"""
        self.metrics['session_events'][event_type] += 1

    def get_metrics(self) -> dict:
        """
        Get session metrics for monitoring dashboard.

        Returns:
            Dictionary with session metrics
        """
        return {
            'sessions': self.sessions,
            'metrics': dict(self.metrics)
        }


# Global session tracker instance
_session_tracker = SessionTracker()


def get_session_tracker() -> SessionTracker:
    """Get the global session tracker instance"""
    return _session_tracker
