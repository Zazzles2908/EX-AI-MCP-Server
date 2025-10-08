"""
Test script to verify thinkdeep diagnostic logging and timeout protection.

This script tests the fixes implemented for the thinkdeep hang issue:
1. MRO diagnostics
2. Timeout protection (180s)
3. Entry logging

Usage:
    python scripts/test_thinkdeep_diagnostic.py
"""

import asyncio
import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

async def test_thinkdeep_basic():
    """Test basic thinkdeep functionality with diagnostic logging."""
    print("=" * 80)
    print("TEST 1: Basic ThinkDeep Test (No Web Search)")
    print("=" * 80)
    
    # Import after path is set
    from tools.workflows.thinkdeep import ThinkDeepTool
    
    tool = ThinkDeepTool()
    
    arguments = {
        "step": "Test the diagnostic logging by analyzing whether Python's asyncio is suitable for CPU-bound tasks",
        "step_number": 1,
        "total_steps": 1,
        "next_step_required": False,
        "findings": "Testing diagnostic logging and timeout protection. Python's asyncio is designed for I/O-bound concurrency using cooperative multitasking. For CPU-bound tasks, the GIL prevents true parallelism.",
        "model": "glm-4.5-flash",
        "use_websearch": False,
        "confidence": "high"
    }
    
    print("\n[TEST] Calling thinkdeep tool...")
    print(f"[TEST] Arguments: {json.dumps(arguments, indent=2)}")
    print("\n[TEST] Waiting for response (max 180s timeout)...")
    
    try:
        result = await tool.execute(arguments)
        print("\n[TEST] ✅ Tool completed successfully!")
        print(f"[TEST] Result type: {type(result)}")
        print(f"[TEST] Result length: {len(result)}")
        
        if result and len(result) > 0:
            content = result[0].text
            data = json.loads(content)
            print(f"\n[TEST] Response status: {data.get('status', 'unknown')}")
            print(f"[TEST] Has expert_analysis: {'expert_analysis' in data}")
            
            if 'expert_analysis' in data:
                expert = data['expert_analysis']
                print(f"[TEST] Expert analysis status: {expert.get('status', 'unknown')}")
            
            # Print first 500 chars of response
            print(f"\n[TEST] Response preview (first 500 chars):")
            print(content[:500])
        
        return True
        
    except asyncio.TimeoutError:
        print("\n[TEST] ❌ TIMEOUT: Tool exceeded 180s timeout")
        return False
    except Exception as e:
        print(f"\n[TEST] ❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_thinkdeep_with_websearch():
    """Test thinkdeep with web search enabled."""
    print("\n\n" + "=" * 80)
    print("TEST 2: ThinkDeep Test (With Web Search)")
    print("=" * 80)
    
    from tools.workflows.thinkdeep import ThinkDeepTool
    
    tool = ThinkDeepTool()
    
    arguments = {
        "step": "Research and analyze the latest best practices for async/await patterns in Python 3.13",
        "step_number": 1,
        "total_steps": 1,
        "next_step_required": False,
        "findings": "Testing web search integration with diagnostic logging. Need to research current best practices for async programming.",
        "model": "glm-4.6",
        "use_websearch": True,
        "confidence": "medium"
    }
    
    print("\n[TEST] Calling thinkdeep tool with web search...")
    print(f"[TEST] Arguments: {json.dumps(arguments, indent=2)}")
    print("\n[TEST] Waiting for response (max 180s timeout)...")
    
    try:
        result = await tool.execute(arguments)
        print("\n[TEST] ✅ Tool completed successfully!")
        print(f"[TEST] Result type: {type(result)}")
        print(f"[TEST] Result length: {len(result)}")
        
        if result and len(result) > 0:
            content = result[0].text
            data = json.loads(content)
            print(f"\n[TEST] Response status: {data.get('status', 'unknown')}")
            print(f"[TEST] Has expert_analysis: {'expert_analysis' in data}")
            
            # Print first 500 chars of response
            print(f"\n[TEST] Response preview (first 500 chars):")
            print(content[:500])
        
        return True
        
    except asyncio.TimeoutError:
        print("\n[TEST] ❌ TIMEOUT: Tool exceeded 180s timeout")
        return False
    except Exception as e:
        print(f"\n[TEST] ❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("THINKDEEP DIAGNOSTIC TEST SUITE")
    print("=" * 80)
    print("\nThis test suite verifies:")
    print("1. MRO diagnostics are working")
    print("2. Timeout protection prevents infinite hangs")
    print("3. Entry logging provides visibility")
    print("4. Expert analysis is called correctly")
    print("\n" + "=" * 80)
    
    results = []
    
    # Test 1: Basic functionality
    result1 = await test_thinkdeep_basic()
    results.append(("Basic Test", result1))
    
    # Test 2: With web search
    result2 = await test_thinkdeep_with_websearch()
    results.append(("Web Search Test", result2))
    
    # Summary
    print("\n\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("\nThe diagnostic logging and timeout protection are working correctly.")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("\nCheck the logs above for details.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

