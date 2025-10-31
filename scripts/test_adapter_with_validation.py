#!/usr/bin/env python3
"""Test the realtime adapter with validation framework"""

import asyncio
import os
import sys
from datetime import datetime, timezone
from src.monitoring.adapters.realtime_adapter import RealtimeAdapter
from src.monitoring.adapters.base import UnifiedMonitoringEvent

# Set environment variables
os.environ['SUPABASE_URL'] = 'https://mxaazuhlqewmkweewyaz.supabase.co'
os.environ['SUPABASE_KEY'] = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im14YWF6dWhscWV3bWt3ZWV3eWF6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjkwMDAwMDAsImV4cCI6MTg4Njc2ODAwMH0.a'
os.environ['MONITORING_USE_ADAPTER'] = 'true'
os.environ['MONITORING_ADAPTER_TYPE'] = 'realtime'
os.environ['MONITORING_ENABLE_VALIDATION'] = 'true'

async def main():
    print('🔧 Initializing RealtimeAdapter with validation...')
    adapter = RealtimeAdapter()
    print('✅ Adapter initialized')

    # Test 1: Broadcast valid event
    print('\n📤 Test 1: Broadcasting valid event...')
    valid_event = UnifiedMonitoringEvent(
        event_type='test_event',
        timestamp=datetime.now(timezone.utc),
        source='test_adapter',
        data={'test': 'data', 'value': 123},
        metadata={'test': 'metadata'},
    )

    try:
        await adapter.broadcast_event(valid_event)
        print('✅ Valid event broadcast successful')
    except Exception as e:
        print(f'❌ Error: {e}')

    # Test 2: Broadcast invalid event (missing required field)
    print('\n📤 Test 2: Broadcasting invalid event (missing source)...')
    invalid_event_dict = {
        'event_type': 'test_event',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'data': {'test': 'data'},
        # Missing 'source' field
    }

    try:
        # Create event manually to bypass model validation
        await adapter.broadcast_event(invalid_event_dict)
        print('✅ Invalid event broadcast attempted (validation should have caught it)')
    except Exception as e:
        print(f'❌ Error: {e}')

    # Test 3: Get adapter metrics
    print('\n📊 Test 3: Checking adapter metrics...')
    metrics = await adapter.get_metrics()
    print(f'✅ Adapter metrics:')
    print(f'   Total broadcasts: {metrics.get("broadcasts", 0)}')
    print(f'   Validation errors: {metrics.get("validation_errors", 0)}')
    print(f'   Failures: {metrics.get("failures", 0)}')

    # Test 4: Get validator metrics
    print('\n📊 Test 4: Checking validator metrics...')
    if hasattr(adapter, '_validator'):
        validator_metrics = adapter._validator.get_metrics()
        print(f'✅ Validator metrics:')
        print(f'   Total validations: {validator_metrics["total_validations"]}')
        print(f'   By event type: {list(validator_metrics["by_event_type"].keys())}')
    else:
        print('⚠️  Validator not available')

    print('\n✅ ALL ADAPTER TESTS COMPLETED!')

if __name__ == '__main__':
    asyncio.run(main())

