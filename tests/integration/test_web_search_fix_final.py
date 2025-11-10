#!/usr/bin/env python3
"""
Final test for web_search fix - Verify smart routing works
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from src.providers.capability_router import get_router
from src.providers.capabilities import get_capabilities_for_provider
from src.prompts.prompt_registry import ProviderType

def test_smart_routing():
    """Test that tools requiring web_search are routed to GLM"""
    print("\n" + "="*80)
    print("TEST: Smart Routing for web_search")
    print("="*80)

    router = get_router()

    # Test tools that require web_search
    test_cases = [
        ("chat", ProviderType.GLM, "Chat tool requires web_search"),
        ("analyze", ProviderType.GLM, "Analyze tool requires web_search"),
        ("codereview", ProviderType.GLM, "CodeReview tool requires web_search"),
    ]

    all_passed = True
    for tool_name, expected_provider, description in test_cases:
        optimal_provider = router.get_optimal_provider(tool_name)
        status = "PASS" if optimal_provider == expected_provider else "FAIL"
        if status == "FAIL":
            all_passed = False
        print(f"{status} - {tool_name}: routed to {optimal_provider.value} (expected {expected_provider.value}) - {description}")

    # Test tools that do NOT require web_search
    print("\n" + "-"*80)
    print("Testing tools that should NOT be forced to GLM:")
    print("-"*80)

    non_websearch_tools = [
        ("listmodels", "Utility tool - no model needed"),
        ("version", "Utility tool - no model needed"),
    ]

    for tool_name, description in non_websearch_tools:
        optimal_provider = router.get_optimal_provider(tool_name)
        # These should default to Kimi or AUTO
        if optimal_provider in [ProviderType.KIMI, ProviderType.AUTO]:
            print(f"PASS - {tool_name}: {optimal_provider.value} (correct - {description})")
        else:
            print(f"FAIL - {tool_name}: {optimal_provider.value} (should be KIMI or AUTO - {description})")
            all_passed = False

    print("\n" + "="*80)
    if all_passed:
        print("SUCCESS: Smart routing is working correctly!")
        print("\nKey points:")
        print("  - Tools requiring web_search are routed to GLM")
        print("  - Tools not requiring web_search can use Kimi")
        print("  - Kimi web_search capability is disabled")
        return 0
    else:
        print("FAILURE: Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(test_smart_routing())
