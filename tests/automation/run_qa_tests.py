#!/usr/bin/env python3
"""QA Test Runner - No Unicode"""

import os
import sys
import traceback

# Add project root
sys.path.insert(0, os.getcwd())

def safe_import(module_name, from_list=None):
    """Safely import and return module or None"""
    try:
        if from_list:
            mod = __import__(module_name, fromlist=from_list)
            return getattr(mod, from_list[0])
        else:
            return __import__(module_name)
    except Exception as e:
        return None

print("=" * 80)
print("EX-AI-MCP-SERVER - QA VALIDATION")
print("=" * 80)

results = {}

# TEST 1: Package Structure
print("\n[TEST 1] Package Structure")
print("-" * 80)
try:
    critical_files = [
        "src/providers/registry_core.py",
        "src/providers/base.py",
        "src/router/hybrid_router.py",
        "src/router/routing_cache.py",
        "src/router/service.py",
        "src/router/minimax_m2_router.py",
        "tools/models.py",
    ]

    all_exist = True
    for f in critical_files:
        exists = os.path.exists(f)
        print(f"  [{'OK' if exists else 'MISSING'}] {f}")
        if not exists:
            all_exist = False

    results['package_structure'] = all_exist
    print(f"RESULT: {'PASS' if all_exist else 'FAIL'}")
except Exception as e:
    print(f"ERROR: {e}")
    results['package_structure'] = False

# TEST 2: Provider Registry Core
print("\n[TEST 2] Provider Registry Core")
print("-" * 80)
try:
    get_registry = safe_import('src.providers.registry_core', ['get_registry_instance'])
    if get_registry:
        registry = get_registry()
        print(f"  [OK] get_registry_instance() works")
        print(f"  [INFO] Registry type: {type(registry).__name__}")
        results['provider_registry'] = True
    else:
        print("  [FAIL] Could not import get_registry_instance")
        results['provider_registry'] = False
    print(f"RESULT: {'PASS' if results.get('provider_registry') else 'FAIL'}")
except Exception as e:
    print(f"ERROR: {e}")
    traceback.print_exc()
    results['provider_registry'] = False

# TEST 3: Routing Cache
print("\n[TEST 3] Routing Cache System")
print("-" * 80)
try:
    get_cache = safe_import('src.router.routing_cache', ['get_routing_cache'])
    if get_cache:
        cache = get_cache()
        print(f"  [OK] get_routing_cache() works")
        print(f"  [INFO] Cache type: {type(cache).__name__}")
        results['routing_cache'] = True
    else:
        print("  [FAIL] Could not import get_routing_cache")
        results['routing_cache'] = False
    print(f"RESULT: {'PASS' if results.get('routing_cache') else 'FAIL'}")
except Exception as e:
    print(f"ERROR: {e}")
    results['routing_cache'] = False

# TEST 4: Tool Model Categories
print("\n[TEST 4] Tool Model Categories")
print("-" * 80)
try:
    category_mapping = safe_import('tools.models', ['CategoryMapping'])
    if category_mapping:
        print(f"  [OK] CategoryMapping imported")
        mappings = getattr(CategoryMapping, '_CATEGORY_MAPPINGS', None)
        if mappings:
            print(f"  [INFO] Found {len(mappings)} category mappings")
        results['tool_categories'] = True
    else:
        print("  [FAIL] Could not import CategoryMapping")
        results['tool_categories'] = False
    print(f"RESULT: {'PASS' if results.get('tool_categories') else 'FAIL'}")
except Exception as e:
    print(f"ERROR: {e}")
    results['tool_categories'] = False

# TEST 5: Hybrid Router
print("\n[TEST 5] Hybrid Router Initialization")
print("-" * 80)
try:
    get_router = safe_import('src.router.hybrid_router', ['get_hybrid_router'])
    if get_router:
        router = get_router()
        print(f"  [OK] get_hybrid_router() works")
        print(f"  [INFO] Router type: {type(router).__name__}")
        results['hybrid_router'] = True
    else:
        print("  [FAIL] Could not import get_hybrid_router")
        results['hybrid_router'] = False
    print(f"RESULT: {'PASS' if results.get('hybrid_router') else 'FAIL'}")
except Exception as e:
    print(f"ERROR: {e}")
    traceback.print_exc()
    results['hybrid_router'] = False

# TEST 6: MiniMax M2 Router
print("\n[TEST 6] MiniMax M2 Router")
print("-" * 80)
try:
    mm_router = safe_import('src.router.minimax_m2_router')
    if mm_router:
        print(f"  [OK] minimax_m2_router module imported")
        results['minimax_router'] = True
    else:
        print("  [FAIL] Could not import minimax_m2_router")
        results['minimax_router'] = False
    print(f"RESULT: {'PASS' if results.get('minimax_router') else 'FAIL'}")
except Exception as e:
    print(f"ERROR: {e}")
    results['minimax_router'] = False

# TEST 7: Router Service Layer
print("\n[TEST 7] Router Service Layer")
print("-" * 80)
try:
    service = safe_import('src.router.service')
    if service:
        print(f"  [OK] service module imported")
        results['router_service'] = True
    else:
        print("  [FAIL] Could not import service")
        results['router_service'] = False
    print(f"RESULT: {'PASS' if results.get('router_service') else 'FAIL'}")
except Exception as e:
    print(f"ERROR: {e}")
    results['router_service'] = False

# TEST 8: Configuration System
print("\n[TEST 8] Configuration System")
print("-" * 80)
try:
    import config
    print(f"  [OK] config module imported")
    context_eng = getattr(config, 'CONTEXT_ENGINEERING', None)
    if context_eng is not None:
        print(f"  [INFO] CONTEXT_ENGINEERING = {context_eng}")
    results['config_system'] = True
except Exception as e:
    print(f"ERROR: {e}")
    results['config_system'] = False
    print(f"RESULT: {'PASS' if results.get('config_system') else 'FAIL'}")

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
    print("\n[VERDICT] ALL TESTS PASSING - System Fully Operational")
    sys.exit(0)
else:
    print(f"\n[VERDICT] {total - passed} TEST(S) FAILING - System NOT Fully Operational")
    sys.exit(1)
