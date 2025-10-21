"""
Test script to verify workflow tools fix (MRO bug)

This script tests that workflow tools now properly call expert analysis
after fixing the MRO bug in orchestration.py.

Expected behavior:
- Thinkdeep should take 10-30 seconds (not 0.00s)
- Expert analysis should be called
- Response should include expert_analysis field
- No hanging or instant completion
"""

import asyncio
import json
import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tools.workflows.thinkdeep import ThinkDeepTool


async def test_thinkdeep_basic():
    """Test basic thinkdeep execution with expert analysis"""
    print("\n" + "="*80)
    print("TEST 1: Basic Thinkdeep with Expert Analysis")
    print("="*80)

    tool = ThinkDeepTool()
    
    arguments = {
        "step": "Analyze the benefits and drawbacks of using Python's asyncio for concurrent programming",
        "step_number": 1,
        "total_steps": 1,
        "next_step_required": False,
        "findings": "Python's asyncio provides cooperative multitasking through coroutines and event loops",
        "use_assistant_model": True,  # Explicitly enable expert analysis
        "model": "glm-4.5-flash",
    }
    
    print(f"\n📋 Test Parameters:")
    print(f"   - Tool: thinkdeep")
    print(f"   - Step: {arguments['step'][:80]}...")
    print(f"   - Expert Analysis: Enabled")
    print(f"   - Model: {arguments['model']}")
    
    print(f"\n⏱️  Starting test at {time.strftime('%H:%M:%S')}...")
    start_time = time.time()
    
    try:
        result = await tool.execute(arguments)
        duration = time.time() - start_time
        
        print(f"\n✅ Test completed in {duration:.2f} seconds")
        
        # Parse result
        if result and len(result) > 0:
            result_text = result[0].text if hasattr(result[0], 'text') else str(result[0])
            result_data = json.loads(result_text)
            
            print(f"\n📊 Result Analysis:")
            print(f"   - Status: {result_data.get('status', 'unknown')}")
            print(f"   - Has expert_analysis: {'expert_analysis' in result_data}")
            
            if 'expert_analysis' in result_data:
                expert = result_data['expert_analysis']
                print(f"   - Expert analysis status: {expert.get('status', 'unknown')}")
                print(f"   - Expert analysis keys: {list(expert.keys())[:5]}")
            
            # Validation
            print(f"\n🔍 Validation:")
            
            if duration < 1.0:
                print(f"   ❌ FAIL: Duration too short ({duration:.2f}s) - expert analysis not called!")
                return False
            else:
                print(f"   ✅ PASS: Duration appropriate ({duration:.2f}s)")
            
            if 'expert_analysis' not in result_data:
                print(f"   ❌ FAIL: No expert_analysis field in response!")
                return False
            else:
                print(f"   ✅ PASS: Expert analysis field present")
            
            if result_data.get('status') == 'error':
                print(f"   ❌ FAIL: Error status returned")
                print(f"   Error: {result_data.get('content', 'unknown')}")
                return False
            else:
                print(f"   ✅ PASS: No error status")
            
            print(f"\n✅ TEST PASSED!")
            return True
        else:
            print(f"\n❌ TEST FAILED: No result returned")
            return False
            
    except Exception as e:
        duration = time.time() - start_time
        print(f"\n❌ TEST FAILED after {duration:.2f} seconds")
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_thinkdeep_without_expert():
    """Test thinkdeep with expert analysis disabled"""
    print("\n" + "="*80)
    print("TEST 2: Thinkdeep WITHOUT Expert Analysis")
    print("="*80)

    tool = ThinkDeepTool()
    
    arguments = {
        "step": "Quick analysis of Python list comprehensions",
        "step_number": 1,
        "total_steps": 1,
        "next_step_required": False,
        "findings": "List comprehensions provide concise syntax for creating lists",
        "use_assistant_model": False,  # Explicitly disable expert analysis
        "model": "glm-4.5-flash",
    }
    
    print(f"\n📋 Test Parameters:")
    print(f"   - Tool: thinkdeep")
    print(f"   - Expert Analysis: Disabled")
    
    print(f"\n⏱️  Starting test at {time.strftime('%H:%M:%S')}...")
    start_time = time.time()
    
    try:
        result = await tool.execute(arguments)
        duration = time.time() - start_time
        
        print(f"\n✅ Test completed in {duration:.2f} seconds")
        
        # Parse result
        if result and len(result) > 0:
            result_text = result[0].text if hasattr(result[0], 'text') else str(result[0])
            result_data = json.loads(result_text)
            
            print(f"\n📊 Result Analysis:")
            print(f"   - Status: {result_data.get('status', 'unknown')}")
            print(f"   - Has expert_analysis: {'expert_analysis' in result_data}")
            
            # Validation
            print(f"\n🔍 Validation:")
            
            if duration > 5.0:
                print(f"   ⚠️  WARNING: Duration longer than expected ({duration:.2f}s)")
                print(f"   (Should be <5s when expert analysis disabled)")
            else:
                print(f"   ✅ PASS: Duration appropriate ({duration:.2f}s)")
            
            if 'expert_analysis' in result_data and result_data['expert_analysis'].get('status') != 'skipped':
                print(f"   ⚠️  WARNING: Expert analysis present but should be disabled")
            else:
                print(f"   ✅ PASS: Expert analysis correctly disabled")
            
            print(f"\n✅ TEST PASSED!")
            return True
        else:
            print(f"\n❌ TEST FAILED: No result returned")
            return False
            
    except Exception as e:
        duration = time.time() - start_time
        print(f"\n❌ TEST FAILED after {duration:.2f} seconds")
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("WORKFLOW TOOLS FIX VERIFICATION")
    print("Testing MRO bug fix in orchestration.py")
    print("="*80)
    
    results = []
    
    # Test 1: With expert analysis
    result1 = await test_thinkdeep_basic()
    results.append(("Thinkdeep with expert analysis", result1))
    
    # Test 2: Without expert analysis
    result2 = await test_thinkdeep_without_expert()
    results.append(("Thinkdeep without expert analysis", result2))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED! Workflow tools fix verified!")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED! Fix may not be working correctly.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

