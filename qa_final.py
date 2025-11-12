#!/usr/bin/env python3
"""Final QA Test - Correctly written"""

import os
import sys

sys.path.insert(0, os.getcwd())

print("=" * 80)
print("FINAL QA VERIFICATION")
print("=" * 80)

results = {}

# TEST 1: Package Structure
print("\n[TEST 1] Package Structure")
print("-" * 80)
critical_files = [
    "src/providers/registry_core.py",
    "src/providers/base.py",
    "src/router/hybrid_router.py",
    "src/router/routing_cache.py",
    "src/router/service.py",
    "src/router/minimax_m2_router.py",
    "tools/models.py",
]
all_exist = all(os.path.exists(f) for f in critical_files)
for f in critical_files:
    exists = os.path.exists(f)
    print(f"  [{'OK' if exists else 'MISSING'}] {f}")
results['package_structure'] = all_exist
print(f"RESULT: {'PASS' if all_exist else 'FAIL'}")

# TEST 2: Provider Registry
print("\n[TEST 2] Provider Registry Core")
print("-" * 80)
try:
    from src.providers.registry_core import get_registry_instance
    registry = get_registry_instance()
    print(f"  [OK] get_registry_instance() works")
    print(f"  [INFO] Registry type: {type(registry).__name__}")
    results['provider_registry'] = True
except Exception as e:
    print(f"  [FAIL] {e}")
    results['provider_registry'] = False
print(f"RESULT: {'PASS' if results['provider_registry'] else 'FAIL'}")

# TEST 3: Routing Cache
print("\n[TEST 3] Routing Cache System")
print("-" * 80)
try:
    from src.router.routing_cache import get_routing_cache
    cache = get_routing_cache()
    print(f"  [OK] get_routing_cache() works")
    print(f"  [INFO] Cache type: {type(cache).__name__}")
    results['routing_cache'] = True
except Exception as e:
    print(f"  [FAIL] {e}")
    results['routing_cache'] = False
print(f"RESULT: {'PASS' if results['routing_cache'] else 'FAIL'}")

# TEST 4: Tool Model Categories
print("\n[TEST 4] Tool Model Categories")
print("-" * 80)
try:
    from tools.models import CategoryMapping, ToolModelCategory
    print(f"  [OK] CategoryMapping imported")
    print(f"  [OK] ToolModelCategory imported")
    default_models = getattr(CategoryMapping, 'DEFAULT_MODELS', None)
    if default_models:
        print(f"  [INFO] DEFAULT_MODELS has {len(default_models)} categories")
    results['tool_categories'] = True
except Exception as e:
    print(f"  [FAIL] {e}")
    results['tool_categories'] = False
print(f"RESULT: {'PASS' if results['tool_categories'] else 'FAIL'}")

# TEST 5: Hybrid Router
print("\n[TEST 5] Hybrid Router")
print("-" * 80)
try:
    from src.router.hybrid_router import get_hybrid_router
    router = get_hybrid_router()
    print(f"  [OK] get_hybrid_router() works")
    print(f"  [INFO] Router type: {type(router).__name__}")
    results['hybrid_router'] = True
except Exception as e:
    print(f"  [FAIL] {e}")
    results['hybrid_router'] = False
print(f"RESULT: {'PASS' if results['hybrid_router'] else 'FAIL'}")

# TEST 6: MiniMax M2 Router
print("\n[TEST 6] MiniMax M2 Router")
print("-" * 80)
try:
    from src.router.minimax_m2_router import MiniMaxM2Router
    print(f"  [OK] MiniMaxM2Router imported")
    results['minimax_router'] = True
except Exception as e:
    print(f"  [FAIL] {e}")
    results['minimax_router'] = False
print(f"RESULT: {'PASS' if results['minimax_router'] else 'FAIL'}")

# TEST 7: Router Service
print("\n[TEST 7] Router Service Layer")
print("-" * 80)
try:
    from src.router.service import RouterService
    print(f"  [OK] RouterService imported")
    results['router_service'] = True
except Exception as e:
    print(f"  [FAIL] {e}")
    results['router_service'] = False
print(f"RESULT: {'PASS' if results['router_service'] else 'FAIL'}")

# TEST 8: Configuration
print("\n[TEST 8] Configuration System")
print("-" * 80)
try:
    import config
    print(f"  [OK] config imported")
    context_eng = getattr(config, 'CONTEXT_ENGINEERING', None)
    print(f"  [INFO] CONTEXT_ENGINEERING type: {type(context_eng).__name__}")
    results['config_system'] = True
except Exception as e:
    print(f"  [FAIL] {e}")
    results['config_system'] = False
print(f"RESULT: {'PASS' if results['config_system'] else 'FAIL'}")

# SUMMARY
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
passed = sum(1 for v in results.values() if v)
total = len(results)
print(f"Tests Passed: {passed}/{total}")

for test_name, result in results.items():
    status = "PASS" if result else "FAIL"
    print(f"  [{status}] {test_name}")

if passed == total:
    print("\n✓ ALL TESTS PASSING")
    sys.exit(0)
else:
    print(f"\n✗ {total - passed} TEST(S) FAILING")
    sys.exit(1)
