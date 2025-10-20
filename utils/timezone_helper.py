"""
Timezone Utility Module - Centralized timezone conversion for EXAI MCP Server

This module provides consistent timezone handling across the application:
- Database stores all timestamps in UTC (industry standard)
- Application layer converts to Australia/Melbourne (AEDT/AEDT) for display/logging
- Ensures consistent timestamp correlation across Docker, Supabase, and system logs

Created: 2025-10-18
EXAI Consultation: 89cc866c-7d88-4339-93de-d8ae08921310
Strategy: Store UTC, convert to AEDT in application layer (EXAI recommended)
"""

from datetime import datetime, timezone
from typing import Optional
import pytz

# Melbourne/Australia timezone
MELBOURNE_TZ = pytz.timezone('Australia/Melbourne')

# UTC timezone
UTC_TZ = pytz.UTC


def utc_now() -> datetime:
    """
    Get current time in UTC with timezone info.
    
    Returns:
        datetime: Current UTC time with timezone info
        
    Example:
        >>> now = utc_now()
        >>> print(now.tzinfo)
        UTC
    """
    return datetime.now(UTC_TZ)


def to_aedt(utc_dt: Optional[datetime]) -> Optional[datetime]:
    """
    Convert UTC datetime to Australia/Melbourne timezone (AEDT/AEDT).
    
    Args:
        utc_dt: UTC datetime (with or without timezone info)
        
    Returns:
        datetime: Melbourne time with timezone info, or None if input is None
        
    Example:
        >>> utc_time = datetime(2025, 10, 18, 12, 0, 0, tzinfo=UTC_TZ)
        >>> melb_time = to_aedt(utc_time)
        >>> print(melb_time.hour)  # Will be 23 (UTC+11 during AEDT)
        23
    """
    if utc_dt is None:
        return None
    
    # If datetime is naive (no timezone), assume it's UTC
    if utc_dt.tzinfo is None:
        utc_dt = utc_dt.replace(tzinfo=UTC_TZ)
    
    # Convert to Melbourne timezone
    return utc_dt.astimezone(MELBOURNE_TZ)


def to_utc(aedt_dt: Optional[datetime]) -> Optional[datetime]:
    """
    Convert Australia/Melbourne datetime to UTC.
    
    Args:
        aedt_dt: Melbourne datetime (with or without timezone info)
        
    Returns:
        datetime: UTC time with timezone info, or None if input is None
        
    Example:
        >>> melb_time = MELBOURNE_TZ.localize(datetime(2025, 10, 18, 23, 0, 0))
        >>> utc_time = to_utc(melb_time)
        >>> print(utc_time.hour)  # Will be 12 (AEDT is UTC+11)
        12
    """
    if aedt_dt is None:
        return None
    
    # If datetime is naive (no timezone), assume it's Melbourne time
    if aedt_dt.tzinfo is None:
        aedt_dt = MELBOURNE_TZ.localize(aedt_dt)
    
    # Convert to UTC
    return aedt_dt.astimezone(UTC_TZ)


def format_aedt(utc_dt: Optional[datetime], format_str: str = "%Y-%m-%d %H:%M:%S %Z") -> str:
    """
    Format UTC datetime as Melbourne time string.
    
    Args:
        utc_dt: UTC datetime to format
        format_str: strftime format string (default: "YYYY-MM-DD HH:MM:SS TZ")
        
    Returns:
        str: Formatted Melbourne time string, or "N/A" if input is None
        
    Example:
        >>> utc_time = datetime(2025, 10, 18, 12, 0, 0, tzinfo=UTC_TZ)
        >>> formatted = format_aedt(utc_time)
        >>> print(formatted)
        2025-10-18 23:00:00 AEDT
    """
    if utc_dt is None:
        return "N/A"
    
    melb_time = to_aedt(utc_dt)
    return melb_time.strftime(format_str)


def format_utc(utc_dt: Optional[datetime], format_str: str = "%Y-%m-%d %H:%M:%S UTC") -> str:
    """
    Format UTC datetime as UTC string.
    
    Args:
        utc_dt: UTC datetime to format
        format_str: strftime format string (default: "YYYY-MM-DD HH:MM:SS UTC")
        
    Returns:
        str: Formatted UTC time string, or "N/A" if input is None
        
    Example:
        >>> utc_time = datetime(2025, 10, 18, 12, 0, 0, tzinfo=UTC_TZ)
        >>> formatted = format_utc(utc_time)
        >>> print(formatted)
        2025-10-18 12:00:00 UTC
    """
    if utc_dt is None:
        return "N/A"
    
    # Ensure timezone info
    if utc_dt.tzinfo is None:
        utc_dt = utc_dt.replace(tzinfo=UTC_TZ)
    
    return utc_dt.strftime(format_str)


def parse_iso8601(iso_string: str) -> datetime:
    """
    Parse ISO 8601 datetime string to UTC datetime.
    
    Args:
        iso_string: ISO 8601 formatted datetime string
        
    Returns:
        datetime: UTC datetime with timezone info
        
    Example:
        >>> dt = parse_iso8601("2025-10-18T12:00:00Z")
        >>> print(dt.tzinfo)
        UTC
    """
    # Parse ISO 8601 string
    dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
    
    # Ensure UTC timezone
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC_TZ)
    else:
        dt = dt.astimezone(UTC_TZ)
    
    return dt


def get_timezone_offset() -> str:
    """
    Get current Melbourne timezone offset from UTC.
    
    Returns:
        str: Timezone offset (e.g., "+11:00" for AEDT, "+10:00" for AEST)
        
    Example:
        >>> offset = get_timezone_offset()
        >>> print(offset)
        +11:00
    """
    now_melb = datetime.now(MELBOURNE_TZ)
    offset = now_melb.strftime('%z')
    # Format as +HH:MM
    return f"{offset[:3]}:{offset[3:]}"


def is_dst() -> bool:
    """
    Check if Melbourne is currently in Daylight Saving Time (AEDT).
    
    Returns:
        bool: True if DST is active (AEDT), False otherwise (AEST)
        
    Example:
        >>> in_dst = is_dst()
        >>> print("AEDT" if in_dst else "AEST")
        AEDT
    """
    now_melb = datetime.now(MELBOURNE_TZ)
    return now_melb.dst() is not None and now_melb.dst().total_seconds() != 0


# Convenience functions for logging
def log_timestamp() -> str:
    """
    Get current timestamp formatted for logging (Melbourne time).
    
    Returns:
        str: Formatted timestamp for logs
        
    Example:
        >>> timestamp = log_timestamp()
        >>> print(timestamp)
        2025-10-18 23:00:00 AEDT
    """
    return format_aedt(utc_now())


def db_timestamp() -> datetime:
    """
    Get current timestamp for database storage (UTC).

    Returns:
        datetime: Current UTC time for database storage

    Example:
        >>> db_time = db_timestamp()
        >>> print(db_time.tzinfo)
        UTC
    """
    return utc_now()


def utc_now_iso() -> str:
    """
    Get current UTC timestamp in ISO 8601 format.

    Returns:
        str: ISO 8601 formatted UTC timestamp

    Example:
        >>> utc_now_iso()
        '2025-10-18T12:00:00Z'
    """
    return utc_now().strftime('%Y-%m-%dT%H:%M:%SZ')


def melbourne_now_iso() -> str:
    """
    Get current Melbourne timestamp in ISO 8601 format.

    Returns:
        str: ISO 8601 formatted Melbourne timestamp with timezone offset

    Example:
        >>> melbourne_now_iso()
        '2025-10-18T23:00:00+11:00'
    """
    melb_time = to_aedt(utc_now())
    # Format with timezone offset
    iso_str = melb_time.strftime('%Y-%m-%dT%H:%M:%S%z')
    # Insert colon in timezone offset: +1100 -> +11:00
    return iso_str[:-2] + ':' + iso_str[-2:]


# Module-level constants for easy access
__all__ = [
    'MELBOURNE_TZ',
    'UTC_TZ',
    'utc_now',
    'to_aedt',
    'to_utc',
    'format_aedt',
    'format_utc',
    'parse_iso8601',
    'get_timezone_offset',
    'is_dst',
    'log_timestamp',
    'db_timestamp',
    'utc_now_iso',
    'melbourne_now_iso',
]

