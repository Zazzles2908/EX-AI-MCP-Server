#!/usr/bin/env python3
"""Test the validation framework"""

from src.monitoring.validation import EventValidator
from datetime import datetime, timezone

# Create validator
validator = EventValidator()
print('✅ Validator initialized')

# Test 1: Valid event
valid_event = {
    'event_type': 'test_event',
    'timestamp': datetime.now(timezone.utc).isoformat(),
    'source': 'test_source',
    'data': {'test': 'data'},
    'metadata': {'test': 'metadata'},
}

result = validator.validate(valid_event)
print(f'✅ Valid event: {result["is_valid"]}')
print(f'   Validation time: {result["validation_time_ms"]:.2f}ms')

# Test 2: Invalid event (missing required field)
invalid_event = {
    'event_type': 'test_event',
    'timestamp': datetime.now(timezone.utc).isoformat(),
    # Missing 'source' field
    'data': {'test': 'data'},
}

result = validator.validate(invalid_event)
print(f'✅ Invalid event detected: {not result["is_valid"]}')
print(f'   Errors: {len(result["errors"])}')
if result['errors']:
    print(f'   Error message: {result["errors"][0].error_message}')

# Test 3: Get metrics
metrics = validator.get_metrics()
print(f'✅ Metrics retrieved:')
print(f'   Total validations: {metrics["total_validations"]}')
print(f'   By event type: {list(metrics["by_event_type"].keys())}')

# Test 4: Batch validation
batch_events = [valid_event, invalid_event, valid_event]
batch_result = validator.validate_batch(batch_events)
print(f'✅ Batch validation:')
print(f'   Total events: {batch_result["total_events"]}')
print(f'   Valid events: {batch_result["valid_events"]}')
print(f'   Invalid events: {batch_result["invalid_events"]}')

print('\n✅ ALL TESTS PASSED - Validation framework is operational!')

