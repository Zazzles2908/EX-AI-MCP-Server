"""
Rate limiter implementation for file operations.
"""

import time
from typing import Optional, Dict


class RateLimiter:
    """Simple rate limiter for API calls."""

    def __init__(self, max_calls: int = 10, time_window: int = 60):
        """Initialize rate limiter.

        Args:
            max_calls: Maximum number of calls allowed
            time_window: Time window in seconds
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []

    def is_allowed(self) -> bool:
        """Check if a call is allowed based on rate limits."""
        now = time.time()

        # Remove old calls outside the time window
        self.calls = [call_time for call_time in self.calls if now - call_time < self.time_window]

        # Check if we can make another call
        if len(self.calls) < self.max_calls:
            self.calls.append(now)
            return True

        return False

    def time_until_next(self) -> float:
        """Get time until next allowed call."""
        if not self.calls:
            return 0.0

        oldest_call = min(self.calls)
        return max(0.0, self.time_window - (time.time() - oldest_call))
