"""
Timezone utilities for consistent timestamp formatting across the system.

This module provides utilities for generating timestamps in Melbourne/Australia timezone (AEDT/AEST)
with both ISO 8601 format and human-readable format.

Created: 2025-10-09 (Phase 6 Implementation)
Last Updated: 2025-10-09
"""

from datetime import datetime
from typing import Dict, Any
import pytz

# Melbourne timezone (automatically handles AEDT/AEST transitions)
MELBOURNE_TZ = pytz.timezone('Australia/Melbourne')


def get_melbourne_now() -> datetime:
    """
    Get current datetime in Melbourne timezone.
    
    Returns:
        datetime: Current time in Melbourne timezone (AEDT or AEST depending on season)
    
    Example:
        >>> now = get_melbourne_now()
        >>> print(now.tzinfo)  # AEDT or AEST
    """
    return datetime.now(MELBOURNE_TZ)


def get_iso_timestamp() -> str:
    """
    Get current timestamp in ISO 8601 format with Melbourne timezone.
    
    Returns:
        str: ISO 8601 timestamp (e.g., "2025-10-09T16:30:45+11:00")
    
    Example:
        >>> timestamp = get_iso_timestamp()
        >>> print(timestamp)
        2025-10-09T16:30:45+11:00
    """
    return get_melbourne_now().isoformat()


def get_human_readable_timestamp() -> str:
    """
    Get current timestamp in human-readable format with timezone abbreviation.
    
    Returns:
        str: Human-readable timestamp (e.g., "2025-10-09 16:30:45 AEDT")
    
    Example:
        >>> timestamp = get_human_readable_timestamp()
        >>> print(timestamp)
        2025-10-09 16:30:45 AEDT
    """
    now = get_melbourne_now()
    tz_name = now.strftime('%Z')  # AEDT or AEST
    return f"{now.strftime('%Y-%m-%d %H:%M:%S')} {tz_name}"


def get_unix_timestamp() -> float:
    """
    Get current Unix timestamp (seconds since epoch).
    
    Returns:
        float: Unix timestamp
    
    Example:
        >>> timestamp = get_unix_timestamp()
        >>> print(timestamp)
        1728454245.123456
    """
    return datetime.now(MELBOURNE_TZ).timestamp()


def get_timestamp_dict() -> Dict[str, Any]:
    """
    Get comprehensive timestamp information in dictionary format.
    
    Useful for JSON logging and structured data.
    
    Returns:
        dict: Dictionary containing multiple timestamp formats
            - timestamp: Unix timestamp (float)
            - timestamp_iso: ISO 8601 format (str)
            - timestamp_human: Human-readable format (str)
            - timezone: Timezone abbreviation (str)
    
    Example:
        >>> timestamps = get_timestamp_dict()
        >>> print(timestamps)
        {
            'timestamp': 1728454245.123456,
            'timestamp_iso': '2025-10-09T16:30:45+11:00',
            'timestamp_human': '2025-10-09 16:30:45 AEDT',
            'timezone': 'AEDT'
        }
    """
    now = get_melbourne_now()
    return {
        'timestamp': now.timestamp(),
        'timestamp_iso': now.isoformat(),
        'timestamp_human': f"{now.strftime('%Y-%m-%d %H:%M:%S')} {now.strftime('%Z')}",
        'timezone': now.strftime('%Z')
    }


def format_timestamp(dt: datetime, include_timezone: bool = True) -> str:
    """
    Format a datetime object in human-readable format.
    
    Args:
        dt: Datetime object to format
        include_timezone: Whether to include timezone abbreviation (default: True)
    
    Returns:
        str: Formatted timestamp
    
    Example:
        >>> from datetime import datetime
        >>> dt = datetime.now(MELBOURNE_TZ)
        >>> formatted = format_timestamp(dt)
        >>> print(formatted)
        2025-10-09 16:30:45 AEDT
    """
    # Convert to Melbourne timezone if not already
    if dt.tzinfo is None:
        dt = MELBOURNE_TZ.localize(dt)
    elif dt.tzinfo != MELBOURNE_TZ:
        dt = dt.astimezone(MELBOURNE_TZ)
    
    if include_timezone:
        return f"{dt.strftime('%Y-%m-%d %H:%M:%S')} {dt.strftime('%Z')}"
    else:
        return dt.strftime('%Y-%m-%d %H:%M:%S')


def parse_iso_timestamp(iso_string: str) -> datetime:
    """
    Parse an ISO 8601 timestamp string to datetime object in Melbourne timezone.
    
    Args:
        iso_string: ISO 8601 timestamp string
    
    Returns:
        datetime: Datetime object in Melbourne timezone
    
    Example:
        >>> dt = parse_iso_timestamp("2025-10-09T16:30:45+11:00")
        >>> print(dt.tzinfo)
        AEDT
    """
    dt = datetime.fromisoformat(iso_string)
    return dt.astimezone(MELBOURNE_TZ)


# Convenience functions for common use cases

def log_timestamp() -> str:
    """
    Get timestamp suitable for log files (human-readable with timezone).
    
    Returns:
        str: Log-friendly timestamp
    
    Example:
        >>> print(f"[{log_timestamp()}] Server started")
        [2025-10-09 16:30:45 AEDT] Server started
    """
    return get_human_readable_timestamp()


def json_timestamp() -> Dict[str, Any]:
    """
    Get timestamp suitable for JSON files (includes both Unix and human-readable).
    
    Returns:
        dict: JSON-friendly timestamp dictionary
    
    Example:
        >>> import json
        >>> data = {"event": "startup", **json_timestamp()}
        >>> print(json.dumps(data, indent=2))
        {
          "event": "startup",
          "timestamp": 1728454245.123456,
          "timestamp_iso": "2025-10-09T16:30:45+11:00",
          "timestamp_human": "2025-10-09 16:30:45 AEDT",
          "timezone": "AEDT"
        }
    """
    return get_timestamp_dict()


def filename_timestamp() -> str:
    """
    Get timestamp suitable for filenames (no spaces or special characters).
    
    Returns:
        str: Filename-safe timestamp
    
    Example:
        >>> filename = f"backup_{filename_timestamp()}.json"
        >>> print(filename)
        backup_2025-10-09_16-30-45.json
    """
    now = get_melbourne_now()
    return now.strftime('%Y-%m-%d_%H-%M-%S')


# Module-level constants for easy access
__all__ = [
    'MELBOURNE_TZ',
    'get_melbourne_now',
    'get_iso_timestamp',
    'get_human_readable_timestamp',
    'get_unix_timestamp',
    'get_timestamp_dict',
    'format_timestamp',
    'parse_iso_timestamp',
    'log_timestamp',
    'json_timestamp',
    'filename_timestamp',
]

