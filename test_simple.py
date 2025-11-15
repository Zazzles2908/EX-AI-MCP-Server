#!/usr/bin/env python3
"""Simple tool test - test one tool at a time."""

def test_tool(tool_name, module_path):
    """Test importing a single tool."""
    try:
        __import__(module_path)
        print(f"OK: {tool_name}")
        return True
    except Exception as e:
        print(f"FAIL: {tool_name} - {str(e)}")
        return False

# Test the 5 main workflow tools
tools = [
    ("Analyze", "tools.workflows.analyze"),
    ("CodeReview", "tools.workflows.codereview"), 
    ("Debug", "tools.workflows.debug"),
    ("DocGen", "tools.workflows.docgen"),
    ("Refactor", "tools.workflows.refactor"),
]

print("Testing Core Workflow Tools:")
print("-" * 40)

success_count = 0
total_count = len(tools)

for tool_name, module_path in tools:
    if test_tool(tool_name, module_path):
        success_count += 1

print(f"\nResults: {success_count}/{total_count} passed")