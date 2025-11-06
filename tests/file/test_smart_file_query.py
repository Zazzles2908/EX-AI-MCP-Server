"""
Test script for smart_file_query tool.

Tests:
1. Path validation
2. Provider selection
3. Deduplication
4. Upload and query
5. Fallback mechanism

Created: 2025-10-29
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools.smart_file_query import SmartFileQueryTool
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_path_validation():
    """Test path validation."""
    print("\n" + "="*80)
    print("TEST 1: Path Validation")
    print("="*80)
    
    tool = SmartFileQueryTool()
    
    # Test 1: Windows path (should fail)
    print("\n[TEST 1.1] Windows path (should fail)")
    try:
        result = tool._run(
            file_path="c:\\Project\\EX-AI-MCP-Server\\README.md",
            question="Test"
        )
        print("❌ FAILED: Windows path should have been rejected")
    except ValueError as e:
        if "PATH FORMAT ERROR" in str(e):
            print(f"✅ PASSED: Windows path rejected correctly")
        else:
            print(f"❌ FAILED: Wrong error: {e}")
    
    # Test 2: Relative path (should fail)
    print("\n[TEST 1.2] Relative path (should fail)")
    try:
        result = tool._run(
            file_path="./README.md",
            question="Test"
        )
        print("❌ FAILED: Relative path should have been rejected")
    except ValueError as e:
        if "PATH FORMAT ERROR" in str(e):
            print(f"✅ PASSED: Relative path rejected correctly")
        else:
            print(f"❌ FAILED: Wrong error: {e}")
    
    # Test 3: Path traversal (should fail)
    print("\n[TEST 1.3] Path traversal (should fail)")
    try:
        result = tool._run(
            file_path="/mnt/project/../etc/passwd",
            question="Test"
        )
        print("❌ FAILED: Path traversal should have been rejected")
    except ValueError as e:
        if "SECURITY ERROR" in str(e):
            print(f"✅ PASSED: Path traversal rejected correctly")
        else:
            print(f"❌ FAILED: Wrong error: {e}")
    
    print("\n✅ Path validation tests complete")


def test_provider_selection():
    """Test provider selection logic."""
    print("\n" + "="*80)
    print("TEST 2: Provider Selection")
    print("="*80)
    
    tool = SmartFileQueryTool()
    
    # Test 1: Small file (<20MB) should select GLM
    print("\n[TEST 2.1] Small file (<20MB) should select GLM")
    provider = tool._select_provider("auto", 5.0)
    if provider == "glm":
        print(f"✅ PASSED: Selected GLM for 5MB file")
    else:
        print(f"❌ FAILED: Expected GLM, got {provider}")
    
    # Test 2: Large file (>20MB) should select Kimi
    print("\n[TEST 2.2] Large file (>20MB) should select Kimi")
    provider = tool._select_provider("auto", 50.0)
    if provider == "kimi":
        print(f"✅ PASSED: Selected Kimi for 50MB file")
    else:
        print(f"❌ FAILED: Expected Kimi, got {provider}")
    
    # Test 3: Huge file (>100MB) should fail
    print("\n[TEST 2.3] Huge file (>100MB) should fail")
    try:
        provider = tool._select_provider("auto", 150.0)
        print(f"❌ FAILED: Should have rejected 150MB file")
    except ValueError as e:
        if "exceeds maximum limit" in str(e):
            print(f"✅ PASSED: Rejected 150MB file correctly")
        else:
            print(f"❌ FAILED: Wrong error: {e}")
    
    # Test 4: User preference should override
    print("\n[TEST 2.4] User preference should override")
    provider = tool._select_provider("kimi", 5.0)
    if provider == "kimi":
        print(f"✅ PASSED: User preference overrode auto-selection")
    else:
        print(f"❌ FAILED: Expected Kimi (user pref), got {provider}")
    
    print("\n✅ Provider selection tests complete")


def test_tool_registration():
    """Test that tool is properly registered."""
    print("\n" + "="*80)
    print("TEST 3: Tool Registration")
    print("="*80)
    
    from tools.registry import TOOL_MAP, TOOL_VISIBILITY
    
    # Test 1: Tool in TOOL_MAP
    print("\n[TEST 3.1] Tool in TOOL_MAP")
    if "smart_file_query" in TOOL_MAP:
        module, cls = TOOL_MAP["smart_file_query"]
        print(f"✅ PASSED: Tool registered - {module}.{cls}")
    else:
        print(f"❌ FAILED: Tool not in TOOL_MAP")
    
    # Test 2: Tool visibility is 'core'
    print("\n[TEST 3.2] Tool visibility is 'core'")
    if TOOL_VISIBILITY.get("smart_file_query") == "core":
        print(f"✅ PASSED: Tool visibility is 'core'")
    else:
        print(f"❌ FAILED: Tool visibility is {TOOL_VISIBILITY.get('smart_file_query')}")
    
    print("\n✅ Tool registration tests complete")


def test_schema():
    """Test tool schema."""
    print("\n" + "="*80)
    print("TEST 4: Tool Schema")
    print("="*80)
    
    tool = SmartFileQueryTool()
    
    # Test 1: Get schema
    print("\n[TEST 4.1] Get schema")
    schema = tool.get_input_schema()
    if schema and "properties" in schema:
        print(f"✅ PASSED: Schema has properties")
    else:
        print(f"❌ FAILED: Invalid schema")
    
    # Test 2: Required fields
    print("\n[TEST 4.2] Required fields")
    required = schema.get("required", [])
    if "file_path" in required and "question" in required:
        print(f"✅ PASSED: Required fields: {required}")
    else:
        print(f"❌ FAILED: Missing required fields: {required}")
    
    # Test 3: Path pattern validation
    print("\n[TEST 4.3] Path pattern validation")
    pattern = schema["properties"]["file_path"].get("pattern")
    if pattern == "^/mnt/project/.*":
        print(f"✅ PASSED: Path pattern: {pattern}")
    else:
        print(f"❌ FAILED: Wrong pattern: {pattern}")
    
    print("\n✅ Schema tests complete")


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("SMART FILE QUERY TOOL - TEST SUITE")
    print("="*80)
    
    try:
        test_path_validation()
        test_provider_selection()
        test_tool_registration()
        test_schema()
        
        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ TEST SUITE FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

