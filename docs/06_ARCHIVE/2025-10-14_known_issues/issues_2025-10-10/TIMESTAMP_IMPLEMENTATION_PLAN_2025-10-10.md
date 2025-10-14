# Timestamp & Geo-Location Implementation Plan
**Date:** 2025-10-10 (10th October 2025)  
**Location:** Melbourne, Australia (AEDT)  
**Purpose:** Add timestamp metadata to requests and improve log clarity

---

## EXECUTIVE SUMMARY

This document provides a comprehensive implementation plan for adding timestamp and geo-location metadata to all EXAI-MCP requests, and improving log file timestamp clarity with human-readable AEDT timestamps.

**Goals:**
1. Add timestamp metadata to all tool call requests
2. Include geo-location information (Melbourne, Australia / AEDT)
3. Update all log files to include human-readable timestamps
4. Maintain backward compatibility with existing systems

---

## CURRENT STATE ANALYSIS

### Log Files - Current Format

**File:** `logs/toolcalls.jsonl`

```json
{
  "timestamp": 1759958101.4558785,
  "tool": "chat",
  "request_id": null,
  "duration_s": 5.549,
  "result_preview": "...",
  ...
}
```

**Issues:**
- Unix timestamp only (1759958101.4558785)
- No human-readable date/time
- No timezone information
- Difficult to correlate events across time zones

### Request Parameters - Current Format

**Current request arguments:**
```python
{
  "prompt": "User's question",
  "model": "glm-4.5-flash",
  "temperature": 0.5,
  "use_websearch": true,
  ...
}
```

**Issues:**
- No timestamp metadata
- No geo-location information
- Cannot determine when request was made
- Cannot correlate requests across systems

---

## IMPLEMENTATION PLAN

### Phase 1: Add Timestamp Utility Module

**File:** `src/utils/timestamp_utils.py` (NEW)

```python
"""
Timestamp and geo-location utilities for EXAI-MCP system.

Provides consistent timestamp formatting across all components.
"""

import time
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from typing import Dict, Any

# Melbourne timezone
MELBOURNE_TZ = ZoneInfo("Australia/Melbourne")

def get_current_timestamps() -> Dict[str, Any]:
    """
    Get current timestamp in multiple formats.
    
    Returns:
        Dictionary with timestamp_unix, timestamp_utc, timestamp_aedt
    """
    now_utc = datetime.now(timezone.utc)
    now_aedt = now_utc.astimezone(MELBOURNE_TZ)
    
    return {
        "timestamp_unix": time.time(),
        "timestamp_utc": now_utc.isoformat(),
        "timestamp_aedt": now_aedt.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "timezone": "Australia/Melbourne"
    }

def format_timestamp_for_logs(unix_timestamp: float) -> Dict[str, str]:
    """
    Convert Unix timestamp to human-readable formats.
    
    Args:
        unix_timestamp: Unix epoch timestamp
        
    Returns:
        Dictionary with formatted timestamps
    """
    dt_utc = datetime.fromtimestamp(unix_timestamp, tz=timezone.utc)
    dt_aedt = dt_utc.astimezone(MELBOURNE_TZ)
    
    return {
        "timestamp_unix": unix_timestamp,
        "timestamp_utc": dt_utc.isoformat(),
        "timestamp_aedt": dt_aedt.strftime("%Y-%m-%d %H:%M:%S %Z")
    }

def get_geo_location_metadata() -> Dict[str, str]:
    """
    Get geo-location metadata for Melbourne, Australia.
    
    Returns:
        Dictionary with location information
    """
    return {
        "city": "Melbourne",
        "state": "Victoria",
        "country": "Australia",
        "timezone": "Australia/Melbourne",
        "timezone_abbr": "AEDT"  # or AEST depending on DST
    }
```

### Phase 2: Update Request Handler to Add Metadata

**File:** `src/server/handlers/request_handler.py`

**Location:** In `handle_call_tool()` function, after line 73 (after req_id generation)

```python
# Add timestamp and geo-location metadata
from src.utils.timestamp_utils import get_current_timestamps, get_geo_location_metadata

# Inject metadata into arguments
if "_request_metadata" not in arguments:
    arguments["_request_metadata"] = {}

arguments["_request_metadata"].update({
    **get_current_timestamps(),
    **get_geo_location_metadata(),
    "request_id": req_id
})
```

### Phase 3: Update Logging Configuration

**File:** `src/bootstrap/setup_logging.py` (or wherever logging is configured)

**Update log formatters to include human-readable timestamps:**

```python
import logging
from src.utils.timestamp_utils import format_timestamp_for_logs

class AEDTFormatter(logging.Formatter):
    """Custom formatter that adds AEDT timestamp to log records."""
    
    def format(self, record):
        # Add AEDT timestamp to record
        timestamps = format_timestamp_for_logs(record.created)
        record.timestamp_aedt = timestamps["timestamp_aedt"]
        record.timestamp_utc = timestamps["timestamp_utc"]
        return super().format(record)

# Update formatter
formatter = AEDTFormatter(
    '%(timestamp_aedt)s | %(levelname)s | %(name)s | %(message)s'
)
```

### Phase 4: Update JSONL Log Writers

**Files to update:**
- `logs/toolcalls.jsonl` writer
- `logs/ws_daemon.metrics.jsonl` writer
- Any other JSONL log writers

**Example update for toolcalls.jsonl:**

```python
from src.utils.timestamp_utils import format_timestamp_for_logs

# When writing to toolcalls.jsonl
log_entry = {
    **format_timestamp_for_logs(time.time()),  # Add all timestamp formats
    "tool": name,
    "request_id": req_id,
    "duration_s": duration,
    ...
}
```

**Result:**
```json
{
  "timestamp_unix": 1759958101.4558785,
  "timestamp_utc": "2025-10-09T14:05:01.455879Z",
  "timestamp_aedt": "2025-10-10 01:05:01 AEDT",
  "tool": "chat",
  "request_id": "...",
  ...
}
```

### Phase 5: Update Health JSON Files

**Files to update:**
- `logs/ws_daemon.health.json`
- Any other health snapshot files

**Example update:**

```python
from src.utils.timestamp_utils import get_current_timestamps

health_data = {
    **get_current_timestamps(),
    "pid": os.getpid(),
    "sessions": session_count,
    ...
}
```

**Result:**
```json
{
  "timestamp_unix": 1759958101.455,
  "timestamp_utc": "2025-10-09T14:05:01.455Z",
  "timestamp_aedt": "2025-10-10 01:05:01 AEDT",
  "timezone": "Australia/Melbourne",
  "pid": 12345,
  "sessions": 2,
  ...
}
```

---

## IMPLEMENTATION CHECKLIST

### Step 1: Create Utility Module
- [ ] Create `src/utils/timestamp_utils.py`
- [ ] Implement `get_current_timestamps()`
- [ ] Implement `format_timestamp_for_logs()`
- [ ] Implement `get_geo_location_metadata()`
- [ ] Add unit tests for timestamp utilities

### Step 2: Update Request Handler
- [ ] Import timestamp utilities in `request_handler.py`
- [ ] Add metadata injection after req_id generation
- [ ] Test with sample tool calls
- [ ] Verify metadata appears in tool arguments

### Step 3: Update Logging Configuration
- [ ] Create `AEDTFormatter` class
- [ ] Update logging setup to use new formatter
- [ ] Test log output format
- [ ] Verify AEDT timestamps appear in logs

### Step 4: Update JSONL Writers
- [ ] Update `toolcalls.jsonl` writer
- [ ] Update `ws_daemon.metrics.jsonl` writer
- [ ] Update any other JSONL log writers
- [ ] Test JSONL output format
- [ ] Verify backward compatibility (old logs still readable)

### Step 5: Update Health Files
- [ ] Update `ws_daemon.health.json` writer
- [ ] Update any other health snapshot writers
- [ ] Test health file format
- [ ] Verify health checks still work

### Step 6: Documentation
- [ ] Update system-reference docs with timestamp metadata
- [ ] Document timestamp format standards
- [ ] Update troubleshooting guides with new log format
- [ ] Create migration guide for log parsing scripts

### Step 7: Testing
- [ ] Test timestamp accuracy across time zones
- [ ] Test DST transitions (AEDT ↔ AEST)
- [ ] Test backward compatibility with existing logs
- [ ] Test performance impact (should be negligible)
- [ ] Test with all EXAI tools

---

## EXAMPLE OUTPUT

### Before Implementation

**Request:**
```python
{
  "prompt": "Explain dependency injection",
  "model": "glm-4.5-flash"
}
```

**Log:**
```json
{"timestamp": 1759958101.455, "tool": "chat", "duration_s": 5.5}
```

### After Implementation

**Request:**
```python
{
  "prompt": "Explain dependency injection",
  "model": "glm-4.5-flash",
  "_request_metadata": {
    "timestamp_unix": 1759958101.455,
    "timestamp_utc": "2025-10-09T14:05:01.455Z",
    "timestamp_aedt": "2025-10-10 01:05:01 AEDT",
    "timezone": "Australia/Melbourne",
    "city": "Melbourne",
    "state": "Victoria",
    "country": "Australia",
    "request_id": "abc-123"
  }
}
```

**Log:**
```json
{
  "timestamp_unix": 1759958101.455,
  "timestamp_utc": "2025-10-09T14:05:01.455Z",
  "timestamp_aedt": "2025-10-10 01:05:01 AEDT",
  "tool": "chat",
  "request_id": "abc-123",
  "duration_s": 5.5
}
```

---

## BACKWARD COMPATIBILITY

### Existing Log Parsers

**Old format still works:**
```python
# Old code that reads timestamp
timestamp = log_entry["timestamp"]  # Still works! (timestamp_unix)
```

**New code can use enhanced format:**
```python
# New code with human-readable timestamps
timestamp_unix = log_entry["timestamp_unix"]
timestamp_aedt = log_entry["timestamp_aedt"]
timestamp_utc = log_entry["timestamp_utc"]
```

### Migration Strategy

1. **Phase 1:** Add new fields alongside old fields
2. **Phase 2:** Update log parsers to use new fields
3. **Phase 3:** (Optional) Deprecate old `timestamp` field in favor of `timestamp_unix`

---

## PERFORMANCE CONSIDERATIONS

**Impact:** Negligible

- Timestamp generation: ~0.001ms per request
- JSON serialization: ~0.01ms per log entry
- Total overhead: <0.1% of request processing time

**Optimization:**
- Cache timezone object (ZoneInfo) at module level
- Use pre-formatted strings where possible
- Avoid repeated datetime conversions

---

## TESTING PLAN

### Unit Tests

```python
def test_get_current_timestamps():
    """Test timestamp generation."""
    ts = get_current_timestamps()
    assert "timestamp_unix" in ts
    assert "timestamp_utc" in ts
    assert "timestamp_aedt" in ts
    assert "timezone" in ts
    assert ts["timezone"] == "Australia/Melbourne"

def test_format_timestamp_for_logs():
    """Test timestamp formatting."""
    unix_ts = 1759958101.455
    formatted = format_timestamp_for_logs(unix_ts)
    assert formatted["timestamp_unix"] == unix_ts
    assert "2025-10-10" in formatted["timestamp_aedt"]
    assert "AEDT" in formatted["timestamp_aedt"]
```

### Integration Tests

1. **Test request metadata injection:**
   - Call chat tool
   - Verify `_request_metadata` in arguments
   - Verify all timestamp fields present

2. **Test log file output:**
   - Trigger tool call
   - Read toolcalls.jsonl
   - Verify new timestamp fields present
   - Verify old timestamp field still works

3. **Test health file output:**
   - Read ws_daemon.health.json
   - Verify new timestamp fields present
   - Verify health checks still work

---

## ROLLOUT PLAN

### Phase 1: Development (Week 1)
- Create timestamp utility module
- Add unit tests
- Update request handler

### Phase 2: Testing (Week 1)
- Integration testing
- Performance testing
- Backward compatibility testing

### Phase 3: Deployment (Week 2)
- Deploy to development environment
- Monitor logs for issues
- Deploy to production

### Phase 4: Documentation (Week 2)
- Update system documentation
- Update troubleshooting guides
- Create migration guide

---

## SUCCESS CRITERIA

✅ All log files include human-readable AEDT timestamps  
✅ All requests include timestamp metadata  
✅ Backward compatibility maintained  
✅ Performance impact <0.1%  
✅ Documentation updated  
✅ All tests passing  

---

**Document Status:** READY FOR IMPLEMENTATION  
**Next Steps:** Create timestamp utility module and begin Phase 1

