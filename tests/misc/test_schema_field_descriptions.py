"""
Test Schema Field Description Updates

Validates that tool schema field descriptions include new functionality:
- File deduplication (SHA256-based)
- "YOU Investigate First" pattern
- Confidence level progression
- Continuation ID lifecycle management

Date: 2025-10-26
Purpose: Validate Task 1 schema updates for full EXAI transparency
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tools.shared.base_models import COMMON_FIELD_DESCRIPTIONS, WORKFLOW_FIELD_DESCRIPTIONS


def test_files_field_description():
    """Test that files field includes deduplication information"""
    desc = COMMON_FIELD_DESCRIPTIONS["files"]
    
    required_content = [
        "DEDUPLICATION",
        "SHA256",
        "DECISION MATRIX",
        "kimi_upload_files",
        "70-80% token savings",
        "<5KB",
        ">5KB"
    ]
    
    missing = []
    for content in required_content:
        if content not in desc:
            missing.append(content)
    
    if missing:
        print(f"❌ FAIL: files field missing content: {missing}")
        return False
    
    print("✅ PASS: files field includes deduplication and decision matrix")
    return True


def test_continuation_id_field_description():
    """Test that continuation_id field includes lifecycle management"""
    desc = COMMON_FIELD_DESCRIPTIONS["continuation_id"]
    
    required_content = [
        "LIFECYCLE MANAGEMENT",
        "Create new ID",
        "Reuse existing ID",
        "persistent across tool calls"
    ]
    
    missing = []
    for content in required_content:
        if content not in desc:
            missing.append(content)
    
    if missing:
        print(f"❌ FAIL: continuation_id field missing content: {missing}")
        return False
    
    print("✅ PASS: continuation_id field includes lifecycle management")
    return True


def test_confidence_field_description():
    """Test that confidence field includes progression guidance"""
    desc = WORKFLOW_FIELD_DESCRIPTIONS["confidence"]
    
    required_content = [
        "PROGRESSION GUIDANCE",
        "exploring",
        "low",
        "medium",
        "high",
        "very_high",
        "almost_certain",
        "certain",
        "EFFICIENCY TIP"
    ]
    
    missing = []
    for content in required_content:
        if content not in desc:
            missing.append(content)
    
    if missing:
        print(f"❌ FAIL: confidence field missing content: {missing}")
        return False
    
    print("✅ PASS: confidence field includes progression guidance")
    return True


def test_step_field_description():
    """Test that step field includes 'YOU Investigate First' pattern"""
    desc = WORKFLOW_FIELD_DESCRIPTIONS["step"]
    
    required_content = [
        "YOU INVESTIGATE FIRST",
        "ALWAYS investigate and analyze",
        "WHAT TO INCLUDE",
        "findings and evidence",
        "Never start with 'I need more information'"
    ]
    
    missing = []
    for content in required_content:
        if content not in desc:
            missing.append(content)
    
    if missing:
        print(f"❌ FAIL: step field missing content: {missing}")
        return False
    
    print("✅ PASS: step field includes 'YOU Investigate First' pattern")
    return True


def test_findings_field_description():
    """Test that findings field includes documentation guidance"""
    desc = WORKFLOW_FIELD_DESCRIPTIONS["findings"]
    
    required_content = [
        "WHAT TO DOCUMENT",
        "Specific evidence",
        "Key insights",
        "EXAMPLES",
        "null pointer exception",
        "Database query timeout"
    ]
    
    missing = []
    for content in required_content:
        if content not in desc:
            missing.append(content)
    
    if missing:
        print(f"❌ FAIL: findings field missing content: {missing}")
        return False
    
    print("✅ PASS: findings field includes documentation guidance and examples")
    return True


def test_schema_generation():
    """Test that schemas can be generated without errors"""
    try:
        from tools.chat import ChatTool
        from tools.workflows.debug import DebugIssueTool
        
        # Test simple tool schema generation
        chat_tool = ChatTool()
        chat_schema = chat_tool.get_input_schema()
        
        if "properties" not in chat_schema:
            print("❌ FAIL: ChatTool schema missing properties")
            return False
        
        if "files" not in chat_schema["properties"]:
            print("❌ FAIL: ChatTool schema missing files field")
            return False
        
        # Test workflow tool schema generation
        debug_tool = DebugIssueTool()
        debug_schema = debug_tool.get_input_schema()
        
        if "properties" not in debug_schema:
            print("❌ FAIL: DebugTool schema missing properties")
            return False
        
        if "step" not in debug_schema["properties"]:
            print("❌ FAIL: DebugTool schema missing step field")
            return False
        
        if "confidence" not in debug_schema["properties"]:
            print("❌ FAIL: DebugTool schema missing confidence field")
            return False
        
        print("✅ PASS: Schema generation works correctly for both simple and workflow tools")
        return True
        
    except Exception as e:
        print(f"❌ FAIL: Schema generation error: {e}")
        return False


def main():
    """Run all schema field description tests"""
    print("=" * 60)
    print("SCHEMA FIELD DESCRIPTION VALIDATION")
    print("=" * 60)
    print()
    
    tests = [
        ("files field (deduplication)", test_files_field_description),
        ("continuation_id field (lifecycle)", test_continuation_id_field_description),
        ("confidence field (progression)", test_confidence_field_description),
        ("step field (YOU investigate first)", test_step_field_description),
        ("findings field (documentation)", test_findings_field_description),
        ("schema generation", test_schema_generation)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\nTesting {test_name}...")
        print("-" * 60)
        result = test_func()
        results.append((test_name, result))
        print()
    
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print()
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL SCHEMA FIELD DESCRIPTION TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit(main())

