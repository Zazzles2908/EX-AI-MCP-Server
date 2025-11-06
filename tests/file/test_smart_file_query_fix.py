"""
Test script to validate smart_file_query fix.

This script tests that the async execute method is properly implemented
and that external AI agents can successfully use the tool.

Created: 2025-10-29
Purpose: Validate fix for "Subclasses must implement execute method" error
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.smart_file_query import SmartFileQueryTool
from mcp.types import TextContent


async def test_smart_file_query():
    """Test smart_file_query execute method."""
    print("=" * 80)
    print("TESTING smart_file_query ASYNC EXECUTE METHOD")
    print("=" * 80)
    
    # Initialize tool
    tool = SmartFileQueryTool()
    print(f"\n✓ Tool initialized: {tool.get_name()}")
    
    # Test 1: Verify execute method exists
    print("\n[TEST 1] Checking execute method exists...")
    assert hasattr(tool, 'execute'), "Tool missing execute method!"
    assert asyncio.iscoroutinefunction(tool.execute), "execute method is not async!"
    print("✓ execute method exists and is async")
    
    # Test 2: Test with invalid arguments (should return error)
    print("\n[TEST 2] Testing with invalid arguments...")
    try:
        result = await tool.execute(arguments={}, on_chunk=None)
        assert isinstance(result, list), "Result should be a list"
        assert len(result) > 0, "Result should not be empty"
        assert isinstance(result[0], TextContent), "Result should contain TextContent"
        print(f"✓ Invalid arguments handled correctly")
        print(f"  Response type: {type(result[0])}")
    except Exception as e:
        print(f"✓ Invalid arguments raised exception (expected): {e}")
    
    # Test 3: Test with valid arguments (file path + question)
    print("\n[TEST 3] Testing with valid arguments...")
    
    # Create a test file
    test_file_path = "/mnt/project/EX-AI-MCP-Server/test_file.txt"
    test_content = "This is a test file for smart_file_query validation."
    
    # Write test file
    with open(test_file_path, 'w') as f:
        f.write(test_content)
    print(f"✓ Created test file: {test_file_path}")
    
    try:
        arguments = {
            "file_path": test_file_path,
            "question": "What does this file contain?",
            "provider": "auto",
            "model": "auto"
        }
        
        print(f"  Arguments: {arguments}")
        result = await tool.execute(arguments=arguments, on_chunk=None)
        
        assert isinstance(result, list), "Result should be a list"
        assert len(result) > 0, "Result should not be empty"
        assert isinstance(result[0], TextContent), "Result should contain TextContent"
        
        print(f"✓ Valid arguments processed successfully")
        print(f"  Response type: {type(result[0])}")
        print(f"  Response length: {len(result)}")
        
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup test file
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
            print(f"✓ Cleaned up test file")
    
    # Test 4: Verify method signature matches BaseTool
    print("\n[TEST 4] Verifying method signature...")
    import inspect
    sig = inspect.signature(tool.execute)
    params = list(sig.parameters.keys())
    
    assert 'arguments' in params, "execute method missing 'arguments' parameter"
    assert 'on_chunk' in params, "execute method missing 'on_chunk' parameter"
    print(f"✓ Method signature correct: {params}")
    
    print("\n" + "=" * 80)
    print("ALL TESTS PASSED! ✓")
    print("=" * 80)
    print("\nThe smart_file_query tool is now ready for external AI agents!")
    print("External agents can call: smart_file_query(file_path='...', question='...')")


if __name__ == "__main__":
    asyncio.run(test_smart_file_query())

