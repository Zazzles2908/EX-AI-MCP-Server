#!/usr/bin/env python3
"""
End-to-End Test for smart_file_query Tool

Tests the complete workflow:
1. Tool registration and loading
2. Execute method (MCP protocol)
3. Response formatting
4. Error handling
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set minimal environment
os.environ.setdefault("LEAN_MODE", "true")
os.environ.setdefault("REDIS_HOST", "localhost")

from tools.registry import ToolRegistry
from mcp.types import TextContent


async def test_smart_file_query_e2e():
    """Test smart_file_query end-to-end."""
    
    print("=" * 80)
    print("SMART_FILE_QUERY END-TO-END TEST")
    print("=" * 80)
    
    # Test 1: Tool Registration
    print("\n[TEST 1] Tool Registration")
    print("-" * 80)
    try:
        registry = ToolRegistry()
        registry.build_tools()  # Must call build_tools() to load tools
        tools = registry.list_tools()

        print(f"   Total tools registered: {len(tools)}")
        print(f"   Tools: {list(tools.keys())}")

        # Check for errors
        if hasattr(registry, '_errors') and registry._errors:
            print(f"\n   ⚠️  Tool loading errors:")
            for tool_name, error in registry._errors.items():
                print(f"      - {tool_name}: {error}")

        if "smart_file_query" not in tools:
            print("\n❌ FAILED: smart_file_query not registered")
            if "smart_file_query" in registry._errors:
                print(f"   Error: {registry._errors['smart_file_query']}")
            return False

        print(f"✅ PASSED: smart_file_query registered")

    except Exception as e:
        print(f"❌ FAILED: Tool registration error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 2: Get Tool Instance
    print("\n[TEST 2] Get Tool Instance")
    print("-" * 80)
    try:
        tool = registry.get_tool("smart_file_query")
        print(f"✅ PASSED: Got tool instance: {type(tool).__name__}")
        
        # Check for execute method
        if not hasattr(tool, "execute"):
            print("❌ FAILED: Tool missing execute method")
            return False
        
        print(f"✅ PASSED: Tool has execute method")
        
        # Check if execute is async
        if not asyncio.iscoroutinefunction(tool.execute):
            print("❌ FAILED: execute method is not async")
            return False
        
        print(f"✅ PASSED: execute method is async")
        
    except Exception as e:
        print(f"❌ FAILED: Get tool error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 3: Create Test File
    print("\n[TEST 3] Create Test File")
    print("-" * 80)
    test_file = project_root / "test_sample.py"
    test_content = '''"""Sample Python file for testing."""

def hello_world():
    """Print hello world."""
    print("Hello, World!")

if __name__ == "__main__":
    hello_world()
'''
    
    try:
        test_file.write_text(test_content)
        print(f"✅ PASSED: Created test file: {test_file}")
    except Exception as e:
        print(f"❌ FAILED: Create test file error: {e}")
        return False
    
    # Test 4: Execute Method (MCP Protocol)
    print("\n[TEST 4] Execute Method (MCP Protocol)")
    print("-" * 80)
    
    # Convert Windows path to Linux container path
    file_path = f"/mnt/project/EX-AI-MCP-Server/test_sample.py"
    
    try:
        result = await tool.execute({
            "file_path": file_path,
            "question": "What does this code do?",
            "provider": "auto"
        })
        
        # Check result type
        if not isinstance(result, list):
            print(f"❌ FAILED: Result is not a list: {type(result)}")
            return False
        
        print(f"✅ PASSED: Result is a list")
        
        if len(result) == 0:
            print(f"❌ FAILED: Result list is empty")
            return False
        
        print(f"✅ PASSED: Result list has {len(result)} items")
        
        # Check first item is TextContent
        if not isinstance(result[0], TextContent):
            print(f"❌ FAILED: First item is not TextContent: {type(result[0])}")
            return False
        
        print(f"✅ PASSED: First item is TextContent")
        
        # Check content
        content = result[0].text
        print(f"✅ PASSED: Got response content ({len(content)} chars)")
        print(f"\n   Response preview:")
        print(f"   {content[:200]}...")
        
    except Exception as e:
        print(f"❌ FAILED: Execute error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 5: Error Handling
    print("\n[TEST 5] Error Handling")
    print("-" * 80)
    try:
        result = await tool.execute({
            "file_path": "/mnt/project/nonexistent_file.py",
            "question": "What does this do?"
        })
        
        # Should return error in TextContent format
        if not isinstance(result, list) or len(result) == 0:
            print(f"❌ FAILED: Error handling returned invalid format")
            return False
        
        content = result[0].text
        if "error" not in content.lower():
            print(f"❌ FAILED: Error response doesn't contain 'error'")
            return False
        
        print(f"✅ PASSED: Error handling works correctly")
        print(f"   Error response: {content[:200]}...")
        
    except Exception as e:
        print(f"❌ FAILED: Error handling test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Cleanup
    print("\n[CLEANUP]")
    print("-" * 80)
    try:
        test_file.unlink()
        print(f"✅ Deleted test file: {test_file}")
    except Exception as e:
        print(f"⚠️  Warning: Could not delete test file: {e}")
    
    print("\n" + "=" * 80)
    print("ALL TESTS PASSED! ✅")
    print("=" * 80)
    print("\nsmartfile_query is fully operational for external agents!")
    
    return True


if __name__ == "__main__":
    try:
        success = asyncio.run(test_smart_file_query_e2e())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

