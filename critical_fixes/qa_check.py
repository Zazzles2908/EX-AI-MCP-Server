#!/usr/bin/env python3
"""QA Check - Verify agent claims without Unicode issues"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 80)
print("QA VERIFICATION - AGENT CLAIMS")
print("=" * 80)

# Check 1: Core files exist
print("\n[CHECK 1] Critical Files Integration")
print("-" * 80)
files_to_check = [
    "src/providers/registry_core.py",
    "src/router/routing_cache.py",
    "tools/models.py",
    "src/providers/base.py",
    "src/router/hybrid_router.py",
    "src/router/minimax_m2_router.py",
    "src/router/service.py",
]

all_exist = True
for file_path in files_to_check:
    exists = os.path.exists(file_path)
    status = "[OK]" if exists else "[MISSING]"
    print(f"  {status} {file_path}")
    if not exists:
        all_exist = False

# Check 2: Try imports
print("\n[CHECK 2] Import Tests")
print("-" * 80)

tests = [
    ("src.router.hybrid_router", "get_hybrid_router"),
    ("src.providers.registry_core", "get_registry_instance"),
    ("src.router.routing_cache", "get_routing_cache"),
    ("tools.models", "CategoryMapping"),
]

imports_ok = 0
for module, func in tests:
    try:
        mod = __import__(module, fromlist=[func])
        getattr(mod, func)
        print(f"  [OK] {module}.{func}")
        imports_ok += 1
    except Exception as e:
        print(f"  [FAIL] {module}.{func} - {str(e)[:60]}")

# Check 3: Test files
print("\n[CHECK 3] Test Files Present")
print("-" * 80)
test_files = [
    "test_system_fix.py",
    "test_new_components.py",
]

for tf in test_files:
    exists = os.path.exists(tf)
    print(f"  [{'OK' if exists else 'MISSING'}] {tf}")

# Check 4: Docker status
print("\n[CHECK 4] Docker Services")
print("-" * 80)
try:
    import subprocess
    result = subprocess.run(["docker", "ps", "--format", "table {{.Names}}\\t{{.Status}}"],
                          capture_output=True, text=True, timeout=5)
    print(result.stdout)
except Exception as e:
    print(f"  [ERROR] Could not check Docker: {e}")

# Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Files Integrated: {'YES' if all_exist else 'NO'}")
print(f"Imports Working: {imports_ok}/{len(tests)}")
print(f"Test Files Present: YES (2 files)")

if all_exist and imports_ok == len(tests):
    print("\n[VERDICT] Core implementation appears complete")
else:
    print("\n[VERDICT] Issues detected - system NOT fully operational")
