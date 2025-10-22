"""
Simple test for request lifecycle logger to verify it works without hanging.

Created: 2025-10-21
"""

import time
from src.utils.request_lifecycle_logger import (
    get_lifecycle_logger,
    log_request_received,
    log_request_completed,
    RequestPhase
)


def test_logger_basic_functionality():
    """Test that logger works without hanging."""
    logger = get_lifecycle_logger()
    
    # Log a simple request
    request_id = "test_req_1"
    log_request_received(request_id, 'kimi', 'moonshot-v1-8k')
    time.sleep(0.1)
    log_request_completed(request_id)
    
    # Verify events were logged
    events = logger.get_request_events(request_id)
    assert len(events) == 2
    assert events[0].phase == RequestPhase.RECEIVED
    assert events[1].phase == RequestPhase.COMPLETED
    
    # Verify duration tracking
    duration = logger.get_request_duration(request_id)
    assert duration is not None
    assert duration >= 100  # At least 100ms
    
    print(f"✅ Logger test passed! Duration: {duration}ms")


if __name__ == '__main__':
    test_logger_basic_functionality()
    print("All tests passed!")

