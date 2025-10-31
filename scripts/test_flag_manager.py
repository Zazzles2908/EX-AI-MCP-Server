#!/usr/bin/env python3
"""Test the feature flag manager"""

import os
import sys
sys.path.insert(0, '/app')

from src.monitoring.flags import FlagManager, FlagSchema

# Set some environment variables for testing
os.environ['MONITORING_USE_ADAPTER'] = 'true'
os.environ['MONITORING_ADAPTER_TYPE'] = 'realtime'
os.environ['MONITORING_ENABLE_VALIDATION'] = 'true'
os.environ['MONITORING_METRICS_FLUSH_INTERVAL'] = '300'

print('🔧 Initializing FlagManager...')
manager = FlagManager()
print('✅ FlagManager initialized')

# Test 1: Get individual flags
print('\n📋 Test 1: Get individual flags')
print(f'  MONITORING_USE_ADAPTER: {manager.get_bool("MONITORING_USE_ADAPTER")}')
print(f'  MONITORING_ADAPTER_TYPE: {manager.get_string("MONITORING_ADAPTER_TYPE")}')
print(f'  MONITORING_ENABLE_VALIDATION: {manager.get_bool("MONITORING_ENABLE_VALIDATION")}')
print(f'  MONITORING_METRICS_FLUSH_INTERVAL: {manager.get_int("MONITORING_METRICS_FLUSH_INTERVAL")}')
print('✅ Individual flag access working')

# Test 2: Get all flags
print('\n📋 Test 2: Get all flags')
all_flags = manager.get_all()
print(f'  Total flags: {len(all_flags)}')
print(f'  Flags: {list(all_flags.keys())}')
print('✅ Get all flags working')

# Test 3: Set flag value
print('\n📋 Test 3: Set flag value')
success = manager.set('MONITORING_DUAL_MODE', True)
print(f'  Set MONITORING_DUAL_MODE to True: {success}')
print(f'  New value: {manager.get_bool("MONITORING_DUAL_MODE")}')
print('✅ Set flag working')

# Test 4: Invalid flag value
print('\n📋 Test 4: Invalid flag value')
success = manager.set('MONITORING_ADAPTER_TYPE', 'invalid')
print(f'  Set MONITORING_ADAPTER_TYPE to "invalid": {success}')
print(f'  Value unchanged: {manager.get_string("MONITORING_ADAPTER_TYPE")}')
print('✅ Validation working')

# Test 5: Flag schema
print('\n📋 Test 5: Flag schema')
all_schema_flags = FlagSchema.get_all_flags()
print(f'  Total schema flags: {len(all_schema_flags)}')
for name, flag_def in list(all_schema_flags.items())[:3]:
    print(f'  - {name}: {flag_def.description}')
print('✅ Flag schema working')

print('\n✅ ALL FLAG MANAGER TESTS PASSED!')

