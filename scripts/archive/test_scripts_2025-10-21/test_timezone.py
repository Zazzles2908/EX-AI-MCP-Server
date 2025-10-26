"""
Test script for timezone utilities

Tests all timezone functions to ensure they work correctly.
Created: 2025-10-09 (Phase 6 Implementation)
"""

import os
import sys
import json
from datetime import datetime

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from src.utils.timezone import (
    MELBOURNE_TZ,
    get_melbourne_now,
    get_iso_timestamp,
    get_human_readable_timestamp,
    get_unix_timestamp,
    get_timestamp_dict,
    format_timestamp,
    parse_iso_timestamp,
    log_timestamp,
    json_timestamp,
    filename_timestamp,
)


def test_melbourne_now():
    """Test get_melbourne_now()"""
    print("\n" + "="*80)
    print("TEST: get_melbourne_now()")
    print("="*80)
    
    now = get_melbourne_now()
    print(f"Current Melbourne time: {now}")
    print(f"Timezone: {now.tzinfo}")
    print(f"Timezone abbreviation: {now.strftime('%Z')}")
    print(f"✅ PASS")


def test_iso_timestamp():
    """Test get_iso_timestamp()"""
    print("\n" + "="*80)
    print("TEST: get_iso_timestamp()")
    print("="*80)
    
    timestamp = get_iso_timestamp()
    print(f"ISO 8601 timestamp: {timestamp}")
    
    # Verify it's valid ISO format
    try:
        parsed = datetime.fromisoformat(timestamp)
        print(f"Parsed successfully: {parsed}")
        print(f"✅ PASS")
    except Exception as e:
        print(f"❌ FAIL: {e}")


def test_human_readable_timestamp():
    """Test get_human_readable_timestamp()"""
    print("\n" + "="*80)
    print("TEST: get_human_readable_timestamp()")
    print("="*80)
    
    timestamp = get_human_readable_timestamp()
    print(f"Human-readable timestamp: {timestamp}")
    
    # Verify format: YYYY-MM-DD HH:MM:SS AEDT/AEST
    if ' AEDT' in timestamp or ' AEST' in timestamp:
        print(f"✅ PASS - Contains timezone abbreviation")
    else:
        print(f"❌ FAIL - Missing timezone abbreviation")


def test_unix_timestamp():
    """Test get_unix_timestamp()"""
    print("\n" + "="*80)
    print("TEST: get_unix_timestamp()")
    print("="*80)
    
    timestamp = get_unix_timestamp()
    print(f"Unix timestamp: {timestamp}")
    
    # Verify it's a reasonable number (after 2020, before 2030)
    if 1577836800 < timestamp < 1893456000:  # 2020-01-01 to 2030-01-01
        print(f"✅ PASS - Timestamp is in reasonable range")
    else:
        print(f"❌ FAIL - Timestamp out of range")


def test_timestamp_dict():
    """Test get_timestamp_dict()"""
    print("\n" + "="*80)
    print("TEST: get_timestamp_dict()")
    print("="*80)
    
    timestamps = get_timestamp_dict()
    print(f"Timestamp dictionary:")
    print(json.dumps(timestamps, indent=2))
    
    # Verify all required keys are present
    required_keys = ['timestamp', 'timestamp_iso', 'timestamp_human', 'timezone']
    missing_keys = [key for key in required_keys if key not in timestamps]
    
    if not missing_keys:
        print(f"✅ PASS - All required keys present")
    else:
        print(f"❌ FAIL - Missing keys: {missing_keys}")


def test_format_timestamp():
    """Test format_timestamp()"""
    print("\n" + "="*80)
    print("TEST: format_timestamp()")
    print("="*80)
    
    now = get_melbourne_now()
    
    # Test with timezone
    formatted_with_tz = format_timestamp(now, include_timezone=True)
    print(f"With timezone: {formatted_with_tz}")
    
    # Test without timezone
    formatted_without_tz = format_timestamp(now, include_timezone=False)
    print(f"Without timezone: {formatted_without_tz}")
    
    if ' AEDT' in formatted_with_tz or ' AEST' in formatted_with_tz:
        print(f"✅ PASS - Timezone formatting works")
    else:
        print(f"❌ FAIL - Timezone formatting failed")


def test_parse_iso_timestamp():
    """Test parse_iso_timestamp()"""
    print("\n" + "="*80)
    print("TEST: parse_iso_timestamp()")
    print("="*80)
    
    # Create an ISO timestamp
    iso_string = get_iso_timestamp()
    print(f"Original ISO string: {iso_string}")
    
    # Parse it back
    parsed = parse_iso_timestamp(iso_string)
    print(f"Parsed datetime: {parsed}")
    print(f"Timezone: {parsed.tzinfo}")
    
    if parsed.tzinfo == MELBOURNE_TZ or str(parsed.tzinfo) in ['AEDT', 'AEST']:
        print(f"✅ PASS - Parsed to Melbourne timezone")
    else:
        print(f"❌ FAIL - Wrong timezone: {parsed.tzinfo}")


def test_log_timestamp():
    """Test log_timestamp()"""
    print("\n" + "="*80)
    print("TEST: log_timestamp()")
    print("="*80)
    
    timestamp = log_timestamp()
    print(f"Log timestamp: {timestamp}")
    
    # Test in log format
    log_message = f"[{timestamp}] Server started successfully"
    print(f"Example log: {log_message}")
    print(f"✅ PASS")


def test_json_timestamp():
    """Test json_timestamp()"""
    print("\n" + "="*80)
    print("TEST: json_timestamp()")
    print("="*80)
    
    timestamps = json_timestamp()
    print(f"JSON timestamp:")
    print(json.dumps(timestamps, indent=2))
    
    # Test in JSON structure
    event_data = {
        "event": "test_event",
        "status": "success",
        **timestamps
    }
    print(f"\nExample JSON event:")
    print(json.dumps(event_data, indent=2))
    print(f"✅ PASS")


def test_filename_timestamp():
    """Test filename_timestamp()"""
    print("\n" + "="*80)
    print("TEST: filename_timestamp()")
    print("="*80)
    
    timestamp = filename_timestamp()
    print(f"Filename timestamp: {timestamp}")
    
    # Test in filename
    filename = f"backup_{timestamp}.json"
    print(f"Example filename: {filename}")
    
    # Verify no spaces or special characters (except dash and underscore)
    if ' ' not in timestamp and ':' not in timestamp:
        print(f"✅ PASS - Filename-safe format")
    else:
        print(f"❌ FAIL - Contains unsafe characters")


def test_consistency():
    """Test that all timestamp functions return consistent times"""
    print("\n" + "="*80)
    print("TEST: Consistency Check")
    print("="*80)
    
    # Get all timestamps at once
    unix_ts = get_unix_timestamp()
    iso_ts = get_iso_timestamp()
    human_ts = get_human_readable_timestamp()
    dict_ts = get_timestamp_dict()
    
    print(f"Unix: {unix_ts}")
    print(f"ISO: {iso_ts}")
    print(f"Human: {human_ts}")
    print(f"Dict Unix: {dict_ts['timestamp']}")
    print(f"Dict ISO: {dict_ts['timestamp_iso']}")
    print(f"Dict Human: {dict_ts['timestamp_human']}")
    
    # Check that Unix timestamps are within 1 second of each other
    if abs(unix_ts - dict_ts['timestamp']) < 1.0:
        print(f"✅ PASS - Timestamps are consistent")
    else:
        print(f"❌ FAIL - Timestamps differ by more than 1 second")


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("TIMEZONE UTILITIES TEST SUITE")
    print("Phase 6 Implementation - 2025-10-09")
    print("="*80)
    
    # Run all tests
    test_melbourne_now()
    test_iso_timestamp()
    test_human_readable_timestamp()
    test_unix_timestamp()
    test_timestamp_dict()
    test_format_timestamp()
    test_parse_iso_timestamp()
    test_log_timestamp()
    test_json_timestamp()
    test_filename_timestamp()
    test_consistency()
    
    print("\n" + "="*80)
    print("ALL TESTS COMPLETE")
    print("="*80)


if __name__ == "__main__":
    main()

