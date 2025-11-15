#!/usr/bin/env python3
"""Test additional MCP tool categories."""

def test_tool(tool_name, module_path):
    """Test importing a single tool."""
    try:
        __import__(module_path)
        print(f"OK: {tool_name}")
        return True
    except Exception as e:
        print(f"FAIL: {tool_name} - {str(e)}")
        return False

# Test additional workflow tools
additional_tools = [
    ("Consensus", "tools.workflows.consensus"),
    ("Precommit", "tools.workflows.precommit"), 
    ("SecurityAudit", "tools.workflows.secaudit"),
    ("TestGen", "tools.workflows.testgen"),
    ("ThinkDeep", "tools.workflows.thinkdeep"),
    ("Planner", "tools.workflows.planner"),
    ("Tracer", "tools.workflows.tracer"),
]

# Test core tools
core_tools = [
    ("Chat", "tools.chat"),
    ("Models", "tools.models"),
    ("Smart File Download", "tools.smart_file_download"),
    ("Smart File Query", "tools.smart_file_query"),
    ("Version", "tools.version"),
    ("Registry", "tools.registry"),
]

# Test shared/base classes
shared_tools = [
    ("Base Models", "tools.shared.base_models"),
    ("Base Tool", "tools.shared.base_tool"),
    ("Base Tool Core", "tools.shared.base_tool_core"),
    ("Base Tool Response", "tools.shared.base_tool_response"),
    ("Schema Builder", "tools.shared.schema_builders"),
]

categories = [
    ("Additional Workflow Tools", additional_tools),
    ("Core Tools", core_tools), 
    ("Shared/Base Classes", shared_tools)
]

for category_name, tools in categories:
    print(f"\n{category_name}:")
    print("-" * 50)
    
    success_count = 0
    total_count = len(tools)
    
    for tool_name, module_path in tools:
        if test_tool(tool_name, module_path):
            success_count += 1
    
    print(f"\n{category_name} Results: {success_count}/{total_count} passed")