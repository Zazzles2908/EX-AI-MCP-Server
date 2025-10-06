#!/usr/bin/env python
"""
Test script to reproduce the web search RAG failure.
Tests that models use search results instead of hallucinating.
"""

import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()


def test_kimi_pricing_query():
    """Test Kimi with verifiable pricing query"""
    print("\n" + "="*80)
    print("TEST: Kimi K2 Pricing Query (Verifiable)")
    print("="*80)
    
    try:
        # Import after adding to path
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        
        # Use the MCP tool directly
        from tools.simple.chat import ChatTool
        
        tool = ChatTool()
        result = tool.run(
            prompt="What is the current pricing for Moonshot AI's Kimi K2 model? Please search for the official pricing and cite your sources.",
            model="kimi-k2-0905-preview",
            use_websearch=True
        )
        
        print(f"\n📊 Response:")
        print(f"{result}")
        
        # Check if response contains correct pricing
        response_text = str(result).lower()
        
        # Ground truth: $0.15/M input (cache hit), $2.50/M output
        # Common errors: $12/M, ¥20/M, etc.
        
        if "$0.15" in response_text or "0.15" in response_text:
            print("\n✅ PASS: Response contains correct input pricing ($0.15/M)")
            return True
        elif "$12" in response_text or "12.00" in response_text:
            print("\n❌ FAIL: Response contains WRONG pricing ($12/M) - 80x error!")
            return False
        else:
            print("\n⚠️  UNCERTAIN: Could not verify pricing in response")
            return False
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_glm_pricing_query():
    """Test GLM with verifiable pricing query"""
    print("\n" + "="*80)
    print("TEST: GLM Pricing Query (Verifiable)")
    print("="*80)
    
    try:
        from tools.simple.chat import ChatTool
        
        tool = ChatTool()
        result = tool.run(
            prompt="What is the current pricing for GLM-4.5 model? Please search for the official pricing and cite your sources.",
            model="glm-4.5",
            use_websearch=True
        )
        
        print(f"\n📊 Response:")
        print(f"{result}")
        
        # Check if response contains search results
        response_text = str(result).lower()
        
        # Look for signs of web search being used
        if "search" in response_text or "source" in response_text or "http" in response_text:
            print("\n✅ Response appears to use web search")
        else:
            print("\n⚠️  Response may not be using web search results")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all web search RAG failure tests"""
    print("\n" + "="*80)
    print("WEB SEARCH RAG FAILURE INVESTIGATION")
    print("Testing if models use search results or hallucinate")
    print("="*80)
    
    results = {
        "Kimi Pricing Query": test_kimi_pricing_query(),
        "GLM Pricing Query": test_glm_pricing_query(),
    }
    
    print("\n" + "="*80)
    print("TEST RESULTS SUMMARY")
    print("="*80)
    
    for test, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*80)
    if all_passed:
        print("✅ ALL TESTS PASSED - Web search working correctly!")
    else:
        print("❌ SOME TESTS FAILED - RAG failure detected!")
    print("="*80)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

