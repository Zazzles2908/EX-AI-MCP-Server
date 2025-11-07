"""
Test script for tool validator

This script demonstrates how to use the tool validator to check arguments
before sending them to EXAI MCP tools.
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from tool_validator import (
    validate_tool_args,
    fix_tool_args,
    validate_and_suggest,
    TOOL_SCHEMAS
)


def test_validation():
    """Test various validation scenarios."""

    print("=" * 80)
    print("EXAI MCP TOOL VALIDATOR - TEST SUITE")
    print("=" * 80)

    # Test 1: Valid analyze tool call
    print("\n[Test 1] Valid analyze tool call")
    print("-" * 80)
    args = {
        "step": "I analyzed the codebase structure and found that the authentication module uses JWT tokens",
        "step_number": 1,
        "total_steps": 3,
        "next_step_required": True,
        "findings": "Found JWT token usage in auth module, identified potential security improvements",
        "relevant_files": ["/path/to/auth.py"],
        "analysis_type": "security"
    }
    is_valid, error = validate_tool_args("analyze", args)
    print(f"Tool: analyze")
    print(f"Arguments: {args}")
    print(f"Valid: {is_valid}")
    if error:
        print(f"Error: {error}")
    else:
        print("OK - All good!")

    # Test 2: Invalid - extra parameter 'problem_context'
    print("\n[Test 2] Invalid analyze tool call - extra parameter")
    print("-" * 80)
    args = {
        "step": "Analyze the code",
        "step_number": 1,
        "total_steps": 3,
        "next_step_required": True,
        "findings": "Found issue",
        "problem_context": "Production-grade system"  # ❌ Not in schema
    }
    is_valid, error = validate_tool_args("analyze", args)
    print(f"Tool: analyze")
    print(f"Arguments: {args}")
    print(f"Valid: {is_valid}")
    print(f"Error: {error[:200]}...")

    # Test 3: Invalid - missing required fields
    print("\n[Test 3] Invalid analyze tool call - missing required fields")
    print("-" * 80)
    args = {
        "step": "Analyze",  # Missing step_number, total_steps, etc.
    }
    is_valid, error = validate_tool_args("analyze", args)
    print(f"Tool: analyze")
    print(f"Arguments: {args}")
    print(f"Valid: {is_valid}")
    print(f"Error: {error[:200]}...")

    # Test 4: Auto-fix arguments
    print("\n[Test 4] Auto-fix arguments")
    print("-" * 80)
    args = {
        "step": "Investigate",
        "stepnum": "1",  # Wrong field name
        "totalsteps": 3,  # Wrong field name
        "nextsteprequired": "true",  # Wrong field name
        "findings": "Found it",
        "problem_context": "Production"  # Extra field
    }
    print(f"Original: {args}")
    fixed = fix_tool_args("analyze", args)
    print(f"Fixed: {fixed}")

    # Test 5: Type conversion
    print("\n[Test 5] Auto-convert types")
    print("-" * 80)
    args = {
        "step": "Test",
        "step_number": "5",  # String
        "total_steps": "10",  # String
        "next_step_required": "true",  # String
        "findings": "Test findings"
    }
    print(f"Original: {args}")
    is_valid, error = validate_tool_args("analyze", args)
    print(f"Valid: {is_valid}")
    if is_valid:
        fixed = fix_tool_args("analyze", args)
        print(f"After fix: {fixed}")

    # Test 6: smart_file_query
    print("\n[Test 6] smart_file_query tool")
    print("-" * 80)
    args = {
        "file_path": "/path/to/file.py",
        "question": "What does this function do?"
    }
    is_valid, error = validate_tool_args("smart_file_query", args)
    print(f"Tool: smart_file_query")
    print(f"Arguments: {args}")
    print(f"Valid: {is_valid}")

    # Test 7: Suggestion for wrong tool
    print("\n[Test 7] Suggest correct tool")
    print("-" * 80)
    args = {
        "file_path": "/path/to/file.py",
        "question": "What is this?",
        "step": "Analyze"  # Wrong tool
    }
    is_valid, error, suggestion = validate_and_suggest("analyze", args)
    print(f"Tool: analyze (with file_path)")
    print(f"Valid: {is_valid}")
    if suggestion:
        print(f"Suggestion: {suggestion}")

    # Test 8: Unknown tool
    print("\n[Test 8] Unknown tool")
    print("-" * 80)
    is_valid, error = validate_tool_args("unknown_tool", {})
    print(f"Tool: unknown_tool")
    print(f"Valid: {is_valid}")
    print(f"Error: {error}")

    # Show available tools
    print("\n" + "=" * 80)
    print("AVAILABLE TOOLS")
    print("=" * 80)
    for tool, schema in sorted(TOOL_SCHEMAS.items()):
        required_count = len(schema["required"])
        optional_count = len(schema["optional"])
        print(f"  {tool:25s} - {schema['description']:40s} ({required_count} required, {optional_count} optional)")

    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    test_validation()
