"""
Session Monitor Module

Handles session and conversation tracking for the monitoring system.
Extracted from monitoring_endpoint.py to improve maintainability.

Components:
- SessionTracker: Track session and conversation metrics
- Session lifecycle management
- Token usage tracking
- Model usage tracking
"""

import logging
from typing import Dict, Optional
from collections import defaultdict

from utils.timezone_helper import log_timestamp

logger = logging.getLogger(__name__)


class SessionTracker:
    """
    Track session and conversation metrics for the monitoring dashboard.

    Tracks:
    - Conversation chains (conversation_id -> message_count)
    - Model usage (session_id -> current_model)
    - Token usage (conversation_id -> tokens_used/max_tokens)
    - Active sessions and their metadata
    """

    def __init__(self):
        self.conversation_chains: Dict[str, int] = defaultdict(int)  # conversation_id -> message_count
        self.model_usage: Dict[str, str] = {}  # session_id -> current_model
        self.token_usage: Dict[str, Dict[str, int]] = {}  # conversation_id -> {used, max}
        self.active_sessions: Dict[str, Dict] = {}  # session_id -> metadata
        self.last_activity: Dict[str, str] = {}  # session_id -> timestamp

    def update_from_event(self, event_data: dict) -> None:
        """
        Update session metrics from a monitoring event.

        Args:
            event_data: Monitoring event data
        """
        # Extract metadata
        metadata = event_data.get("metadata", {})
        connection_type = event_data.get("connection_type", "")

        # Track conversation chains (from continuation_id or conversation_id)
        conversation_id = metadata.get("continuation_id") or metadata.get("conversation_id")
        if conversation_id:
            self.conversation_chains[conversation_id] += 1

        # Track model usage (from Kimi/GLM events)
        if connection_type in ["kimi", "glm"]:
            model = metadata.get("model")
            if model:
                # Use conversation_id as session_id for now
                session_id = conversation_id or "default"
                self.model_usage[session_id] = model

                # Update last activity
                self.last_activity[session_id] = event_data.get("timestamp", log_timestamp())

        # Track token usage (from API responses)
        tokens = metadata.get("tokens")
        if tokens and conversation_id:
            if conversation_id not in self.token_usage:
                # Initialize with default max tokens (will be updated based on model)
                self.token_usage[conversation_id] = {"used": 0, "max": 128000}

            # Update tokens used
            self.token_usage[conversation_id]["used"] = tokens

            # Update max tokens based on model
            model = metadata.get("model", "")
            if "128k" in model.lower():
                self.token_usage[conversation_id]["max"] = 128000
            elif "32k" in model.lower():
                self.token_usage[conversation_id]["max"] = 32000
            elif "8k" in model.lower():
                self.token_usage[conversation_id]["max"] = 8000

    def get_metrics(self) -> dict:
        """
        Get current session metrics for dashboard.

        Returns:
            Dictionary with session metrics
        """
        # Get most recent conversation
        recent_conversation_id = None
        recent_timestamp = None
        for session_id, timestamp in self.last_activity.items():
            if recent_timestamp is None or timestamp > recent_timestamp:
                recent_timestamp = timestamp
                recent_conversation_id = session_id

        # Get metrics for most recent conversation
        conversation_length = 0
        current_model = "--"
        context_tokens_used = 0
        context_tokens_max = 128000

        if recent_conversation_id:
            conversation_length = self.conversation_chains.get(recent_conversation_id, 0)
            current_model = self.model_usage.get(recent_conversation_id, "--")

            if recent_conversation_id in self.token_usage:
                context_tokens_used = self.token_usage[recent_conversation_id]["used"]
                context_tokens_max = self.token_usage[recent_conversation_id]["max"]

        return {
            "active_sessions": 0,  # This will be updated from websocket_handler
            "total_sessions": len(self.active_sessions),
            "conversation_length": conversation_length,
            "current_model": current_model,
            "context_tokens_used": context_tokens_used,
            "context_tokens_max": context_tokens_max,
        }

    def cleanup_old_sessions(self, max_age_hours: int = 24) -> None:
        """
        Clean up old session data to prevent memory leaks.

        Args:
            max_age_hours: Maximum age of sessions to keep (default 24 hours)
        """
        # TODO: Implement cleanup based on last_activity timestamps
        pass


# Global session tracker instance
_session_tracker = SessionTracker()


def get_session_tracker() -> SessionTracker:
    """Get the session tracker instance"""
    return _session_tracker
