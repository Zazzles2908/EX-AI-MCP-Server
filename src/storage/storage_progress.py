"""
Progress Tracker Module

Thread-safe progress tracking with throttling for file upload/download operations.
Provides callback-based progress reporting for long-running storage operations.
"""

import threading
import time
from typing import Optional, Callable


class ProgressTracker:
    """Thread-safe progress tracking with throttling.

    Tracks upload/download progress and calls a callback function
    with throttling to avoid excessive callback invocations.
    """

    def __init__(
        self,
        callback: Optional[Callable[[int, int, float], None]],
        throttle_interval: float = 0.5
    ):
        """
        Initialize progress tracker.

        Args:
            callback: Function called with (bytes_transferred, total_bytes, percentage)
            throttle_interval: Minimum time between callbacks in seconds (default 0.5s)
        """
        self.callback = callback
        self.throttle_interval = throttle_interval
        self.last_update = 0
        self.lock = threading.Lock()

    def update(self, bytes_transferred: int, total_bytes: int):
        """
        Update progress with throttling.

        Args:
            bytes_transferred: Number of bytes transferred so far
            total_bytes: Total number of bytes to transfer
        """
        if not self.callback:
            return

        current_time = time.time()
        with self.lock:
            if current_time - self.last_update >= self.throttle_interval:
                percentage = (bytes_transferred / total_bytes) * 100 if total_bytes > 0 else 0
                try:
                    self.callback(bytes_transferred, total_bytes, percentage)
                except Exception:
                    # Silently ignore callback errors to avoid disrupting main flow
                    pass
                finally:
                    self.last_update = current_time
