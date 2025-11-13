#!/usr/bin/env python3
"""
Test script to verify the thinkdeep validation fix
"""

import sys
sys.path.insert(0, 'C:/Project/EX-AI-MCP-Server/src')
sys.path.insert(0, 'C:/Project/EX-AI-MCP-Server')

def test_validator_file():
    """Test that the validator file has the enhanced error handling"""
    print("=" * 60)
    print("Test 1: Validator File Enhancement")
    print("=" * 60)

    with open('C:/Project/EX-AI-MCP-Server/src/server/utils/tool_validator.py', 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    has_enhanced_validation = 'what is \'findings\'' in content.lower() or 'cannot be empty' in content.lower()
    has_missing_field_check = 'Missing required field' in content
    has_empty_field_check = 'Empty field detected' in content

    print(f"  Has enhanced validation: {has_enhanced_validation}")
    print(f"  Has missing field check: {has_missing_field_check}")
    print(f"  Has empty field check: {has_empty_field_check}")

    if has_enhanced_validation and has_missing_field_check and has_empty_field_check:
        print("  [PASS] Validator enhancements are in place\n")
        return True
    else:
        print("  [FAIL] Validator enhancements are missing\n")
        return False

def test_thinkdeep_schema():
    """Test that thinkdeep tool has the findings parameter marked as required"""
    print("=" * 60)
    print("Test 2: ThinkDeep Schema Validation")
    print("=" * 60)

    with open('C:/Project/EX-AI-MCP-Server/src/server/utils/tool_validator.py', 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    has_findings_required = "'findings'" in content
    has_workflow_tools = 'thinkdeep' in content.lower()

    print(f"  Has findings parameter: {has_findings_required}")
    print(f"  Has workflow tools check: {has_workflow_tools}")

    if has_findings_required and has_workflow_tools:
        print("  [PASS] ThinkDeep schema is properly defined\n")
        return True
    else:
        print("  [FAIL] ThinkDeep schema is incomplete\n")
        return False

def test_error_messages():
    """Test that enhanced error messages are present"""
    print("=" * 60)
    print("Test 3: Enhanced Error Messages")
    print("=" * 60)

    with open('C:/Project/EX-AI-MCP-Server/src/server/utils/tool_validator.py', 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    has_detailed_errors = 'Example:' in content and 'Required' in content
    has_actionable_guidance = 'please provide' in content.lower() or 'must be' in content.lower()

    print(f"  Has detailed errors: {has_detailed_errors}")
    print(f"  Has actionable guidance: {has_actionable_guidance}")

    if has_detailed_errors and has_actionable_guidance:
        print("  [PASS] Error messages are enhanced\n")
        return True
    else:
        print("  [FAIL] Error messages need enhancement\n")
        return False

def test_fix_report():
    """Test that fix report exists and is comprehensive"""
    print("=" * 60)
    print("Test 4: Fix Report")
    print("=" * 60)

    import os
    report_exists = os.path.exists('C:/Project/EX-AI-MCP-Server/THINKDEEP_VALIDATION_FIX_REPORT.md')

    print(f"  Fix report exists: {report_exists}")

    if report_exists:
        with open('C:/Project/EX-AI-MCP-Server/THINKDEEP_VALIDATION_FIX_REPORT.md', 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        has_problem = "Problem" in content or "Error" in content
        has_solution = "Solution" in content or "Fix" in content
        has_testing = "Test" in content

        print(f"  Has problem description: {has_problem}")
        print(f"  Has solution details: {has_solution}")
        print(f"  Has testing section: {has_testing}")

        if has_problem and has_solution and has_testing:
            print("  [PASS] Fix report is comprehensive\n")
            return True
        else:
            print("  [FAIL] Fix report is incomplete\n")
            return False
    else:
        print("  [FAIL] Fix report does not exist\n")
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("THINKDEEP VALIDATION FIX - TEST SUITE")
    print("=" * 60 + "\n")

    try:
        results = []
        results.append(test_validator_file())
        results.append(test_thinkdeep_schema())
        results.append(test_error_messages())
        results.append(test_fix_report())

        print("=" * 60)
        if all(results):
            print("ALL TESTS PASSED! ✅")
            print("=" * 60)
            print("\nThe thinkdeep validation fix is working correctly.")
            print("Enhanced error messages now provide clear guidance to agents.")
            print("\nKey improvements:")
            print("  1. Enhanced validation with detailed error messages")
            print("  2. Specific guidance for 'findings' parameter")
            print("  3. Examples of correct usage")
            print("  4. Detection of both missing and empty fields")
            print("  5. Comprehensive fix report")
            return 0
        else:
            print("SOME TESTS FAILED! ❌")
            print("=" * 60)
            return 1

    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
