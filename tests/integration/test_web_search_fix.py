#!/usr/bin/env python3
"""
Test the web_search fix - Verify that Kimi no longer receives web_search tool type
"""
import sys
import os

# Test the capability router
sys.path.insert(0, os.path.dirname(__file__))

from src.router.minimax_m2_router import get_router
from src.providers.capabilities import get_capabilities_for_provider
from src.providers.base import ProviderType

def test_kimi_web_search_capability():
    """Test that Kimi capabilities report web_search as False"""
    print("\n" + "="*80)
    print("TEST 1: Kimi Web Search Capability")
    print("="*80)

    # Get Kimi capabilities
    kimi_caps = get_capabilities_for_provider(ProviderType.KIMI)
    supports_websearch = kimi_caps.supports_websearch()

    print(f"Kimi supports websearch: {supports_websearch}")

    if not supports_websearch:
        print("✅ PASS - Kimi correctly reports web_search as NOT supported")
        return True
    else:
        print("❌ FAIL - Kimi should NOT support web_search tool type")
        return False

def test_kimi_tool_schema():
    """Test that Kimi returns no web_search tools"""
    print("\n" + "="*80)
    print("TEST 2: Kimi Tool Schema (should return None/empty)")
    print("="*80)

    kimi_caps = get_capabilities_for_provider(ProviderType.KIMI)
    schema = kimi_caps.get_websearch_tool_schema({"use_websearch": True})

    print(f"Schema tools: {schema.tools}")
    print(f"Schema tool_choice: {schema.tool_choice}")

    if schema.tools is None:
        print("✅ PASS - Kimi returns no web_search tools")
        return True
    else:
        print("❌ FAIL - Kimi should return empty tools list")
        return False

def test_glm_web_search_capability():
    """Test that GLM correctly supports web_search"""
    print("\n" + "="*80)
    print("TEST 3: GLM Web Search Capability (should still work)")
    print("="*80)

    glm_caps = get_capabilities_for_provider(ProviderType.GLM)
    supports_websearch = glm_caps.supports_websearch()

    print(f"GLM supports websearch: {supports_websearch}")

    if supports_websearch:
        print("✅ PASS - GLM correctly supports web_search")
        return True
    else:
        print("❌ FAIL - GLM should support web_search")
        return False

def test_smart_routing():
    """Test that tools requiring web_search are routed to GLM"""
    print("\n" + "="*80)
    print("TEST 4: Smart Routing (chat tool → GLM)")
    print("="*80)

    router = get_router()
    # The 'chat' tool requires web_search (from TOOL_REQUIREMENTS)
    optimal_provider = router.get_optimal_provider("chat")

    print(f"Optimal provider for 'chat' tool: {optimal_provider}")

    if optimal_provider == ProviderType.GLM:
        print("✅ PASS - chat tool (requires web_search) correctly routed to GLM")
        return True
    else:
        print("❌ FAIL - chat tool should be routed to GLM for web_search")
        return False

def test_kimi_routing():
    """Test that tools NOT requiring web_search can still use Kimi"""
    print("\n" + "="*80)
    print("TEST 5: Kimi Routing (listmodels tool → AUTO/KIMI)")
    print("="*80)

    router = get_router()
    # The 'listmodels' tool does NOT require web_search
    optimal_provider = router.get_optimal_provider("listmodels")

    print(f"Optimal provider for 'listmodels' tool: {optimal_provider}")

    # Should NOT be forced to GLM
    if optimal_provider in [ProviderType.AUTO, ProviderType.KIMI]:
        print("✅ PASS - listmodels tool can still use Kimi")
        return True
    else:
        print("❌ FAIL - listmodels should not be forced to GLM")
        return False

def main():
    """Run all web_search fix tests"""
    print("\n" + "="*80)
    print("WEB_SEARCH FIX VALIDATION TESTS")
    print("="*80)
    print("Testing the fix for: 'Invalid request: unknown tool type: web_search'")
    print("="*80)

    results = []

    # Run tests
    results.append(("Kimi Web Search Capability", test_kimi_web_search_capability()))
    results.append(("Kimi Tool Schema", test_kimi_tool_schema()))
    results.append(("GLM Web Search Capability", test_glm_web_search_capability()))
    results.append(("Smart Routing to GLM", test_smart_routing()))
    results.append(("Kimi Still Available", test_kimi_routing()))

    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")

    all_passed = all(passed for _, passed in results)

    print("\n" + "="*80)
    if all_passed:
        print("🎉 ALL TESTS PASSED - web_search fix is working correctly!")
        print("\nImpact:")
        print("  • Kimi no longer receives web_search tool type")
        print("  • Tools requiring web_search are auto-routed to GLM")
        print("  • Users get proper responses instead of errors")
    else:
        print("❌ SOME TESTS FAILED - web_search fix needs review")
    print("="*80 + "\n")

    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
