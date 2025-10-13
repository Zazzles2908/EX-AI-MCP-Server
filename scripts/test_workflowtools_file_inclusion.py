#!/usr/bin/env python3
"""
Test script to validate WorkflowTools file inclusion bug fix.
Tests that EXPERT_ANALYSIS_INCLUDE_FILES=false is respected.
"""

import asyncio
import json
import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tools.workflows.analyze import AnalyzeTool
from tools.workflows.codereview import CodeReviewTool
from tools.workflows.refactor import RefactorTool
from tools.workflows.secaudit import SecauditTool


async def test_tool(tool_class, tool_name):
    """Test a single WorkflowTool for file inclusion behavior."""
    print(f"\n{'='*60}")
    print(f"Testing: {tool_name}")
    print(f"{'='*60}")
    
    try:
        # Create tool instance
        tool = tool_class()
        
        # Prepare test arguments
        test_args = {
            "step": f"Test {tool_name} after file inclusion fix",
            "step_number": 1,
            "total_steps": 1,
            "next_step_required": False,
            "findings": "Testing file inclusion fix",
            "model": "glm-4.5-flash",
            "confidence": "high" if tool_name != "refactor" else "incomplete",
            "use_assistant_model": False,
        }
        
        # Execute tool
        print(f"Executing {tool_name}...")
        start_time = time.time()

        result = await tool.execute(test_args)

        duration = time.time() - start_time
        
        # Parse result
        if hasattr(result, 'text'):
            result_data = json.loads(result.text)
        else:
            result_data = result
        
        # Check for file inclusion
        files_included = result_data.get('metadata', {}).get('files_included', 0)
        
        # Print results
        print(f"✅ Status: SUCCESS")
        print(f"⏱️  Duration: {duration:.2f}s")
        print(f"📁 Files Included: {files_included}")
        print(f"📊 Response Length: {len(str(result_data))} chars")
        
        # Validate
        if files_included > 0:
            print(f"❌ FAIL: Files were included despite EXPERT_ANALYSIS_INCLUDE_FILES=false")
            return False
        else:
            print(f"✅ PASS: No files included (correct behavior)")
            return True
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all WorkflowTools tests."""
    print("="*60)
    print("WORKFLOWTOOLS FILE INCLUSION TEST")
    print("="*60)
    print(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Testing 4 WorkflowTools for file inclusion bug fix")
    print()

    # Test configuration
    tools_to_test = [
        (AnalyzeTool, "analyze"),
        (CodeReviewTool, "codereview"),
        (RefactorTool, "refactor"),
        (SecauditTool, "secaudit"),
    ]

    results = {}

    # Run tests
    for tool_class, tool_name in tools_to_test:
        results[tool_name] = await test_tool(tool_class, tool_name)
        await asyncio.sleep(1)  # Brief pause between tests
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for tool_name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{tool_name:15} {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - File inclusion bug fix validated!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} TEST(S) FAILED - File inclusion issue persists")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

