#!/usr/bin/env python3
"""
Direct test: Verify web_search routing works
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from src.router.minimax_m2_router import get_router
from src.prompts.prompt_registry import ProviderType

print("\n" + "="*80)
print("WEB_SEARCH SMART ROUTING VERIFICATION")
print("="*80)

router = get_router()

# Test 1: Chat tool (requires web_search)
print("\n1. Testing 'chat' tool (requires web_search):")
chat_provider = router.get_optimal_provider("chat")
print(f"   Routed to: {chat_provider.value}")
if chat_provider == ProviderType.GLM:
    print("   Result: PASS - Correctly routed to GLM")
else:
    print("   Result: FAIL - Should be routed to GLM")

# Test 2: Analyze tool (does NOT require web_search)
print("\n2. Testing 'analyze' tool (does NOT require web_search):")
analyze_provider = router.get_optimal_provider("analyze")
print(f"   Routed to: {analyze_provider.value}")
if analyze_provider == ProviderType.KIMI:
    print("   Result: PASS - Correctly routed to Kimi")
else:
    print("   Result: FAIL - Should be routed to Kimi")

# Test 3: ListModels tool (utility, no model)
print("\n3. Testing 'listmodels' tool (utility tool, no model):")
listmodels_provider = router.get_optimal_provider("listmodels")
print(f"   Routed to: {listmodels_provider.value}")
if listmodels_provider in [ProviderType.KIMI, ProviderType.AUTO]:
    print("   Result: PASS - Correctly routed (Kimi or AUTO)")
else:
    print("   Result: FAIL - Unexpected provider")

print("\n" + "="*80)
print("VERIFICATION COMPLETE")
print("="*80)
print("\nKey Finding:")
print("  - chat tool REQUIRES web_search -> routes to GLM")
print("  - analyze/codereview tools do NOT require web_search -> route to Kimi")
print("  - This prevents the 'unknown tool type: web_search' error!")
print("="*80)
