"""
Script to regenerate all test files to use NEW MCP daemon approach

This script converts all 36 test files from OLD approach (api_client.py)
to NEW approach (mcp_client.py) for full stack testing.
"""

import os
from pathlib import Path

# Tool definitions with their arguments
# NOTE: Workflow tools require step, step_number, total_steps, next_step_required, and findings
TOOL_DEFINITIONS = {
    # Core tools (14) - Workflow tools with proper schema
    "analyze": {
        "step": "Analyze the provided code for potential improvements",
        "step_number": 1,
        "total_steps": 1,
        "next_step_required": False,
        "findings": "Initial code review requested",
        "relevant_files": ["test.py"],
        "model": "glm-4.5-flash"
    },
    "debug": {
        "step": "Debug the provided code to find the issue",
        "step_number": 1,
        "total_steps": 1,
        "next_step_required": False,
        "findings": "Code appears to have a logic error",
        "relevant_files": ["test.py"],
        "model": "glm-4.5-flash"
    },
    "codereview": {
        "step": "Review the code for best practices and potential issues",
        "step_number": 1,
        "total_steps": 1,
        "next_step_required": False,
        "findings": "Code review requested for quality assurance",
        "relevant_files": ["test.py"],
        "model": "glm-4.5-flash"
    },
    "refactor": {
        "step": "Refactor the code to improve readability and maintainability",
        "step_number": 1,
        "total_steps": 1,
        "next_step_required": False,
        "findings": "Code could benefit from refactoring",
        "relevant_files": ["test.py"],
        "model": "glm-4.5-flash"
    },
    "secaudit": {
        "step": "Audit the code for security vulnerabilities",
        "step_number": 1,
        "total_steps": 1,
        "next_step_required": False,
        "findings": "Security audit requested",
        "relevant_files": ["test.py"],
        "model": "glm-4.5-flash"
    },
    "planner": {
        "step": "Create a plan for building a simple web application",
        "step_number": 1,
        "total_steps": 1,
        "next_step_required": False,
        "findings": "Project planning phase initiated",
        "model": "glm-4.5-flash"
    },
    "tracer": {
        "step": "Trace the execution flow of the factorial function",
        "step_number": 1,
        "total_steps": 1,
        "next_step_required": False,
        "findings": "Execution trace requested for recursive function",
        "relevant_files": ["test.py"],
        "model": "glm-4.5-flash"
    },
    "testgen": {
        "step": "Generate unit tests for the add function",
        "step_number": 1,
        "total_steps": 1,
        "next_step_required": False,
        "findings": "Test generation requested",
        "relevant_files": ["test.py"],
        "model": "glm-4.5-flash"
    },
    "consensus": {
        "step": "Gather consensus on whether Python or JavaScript is better for web backend development",
        "step_number": 1,
        "total_steps": 1,
        "next_step_required": False,
        "findings": "Initial analysis: Both languages have strong ecosystems. Need expert consensus.",
        "models": [
            {"name": "glm-4.5-flash", "stance": "neutral"},
            {"name": "kimi-k2-0905-preview", "stance": "neutral"}
        ],
        "model": "glm-4.5-flash"
    },
    "thinkdeep": {
        "step": "Deeply analyze the concept of recursion and its applications",
        "step_number": 1,
        "total_steps": 1,
        "next_step_required": False,
        "findings": "Deep thinking requested on recursion concept",
        "model": "glm-4.5-flash"
    },
    "docgen": {
        "step": "Generate documentation for the process_data function",
        "step_number": 1,
        "total_steps": 1,
        "next_step_required": False,
        "findings": "Documentation generation requested",
        "relevant_files": ["test.py"],
        "model": "glm-4.5-flash"
    },
    "precommit": {
        "step": "Run pre-commit checks on the specified files",
        "step_number": 1,
        "total_steps": 1,
        "next_step_required": False,
        "findings": "Pre-commit validation requested",
        "files_checked": ["test.py"],
        "model": "glm-4.5-flash"
    },
    # Simple tools (non-workflow)
    "challenge": {"prompt": "Python is the best language for all use cases"},
    
    # Advanced tools (8)
    "listmodels": {},
    "version": {},
    "activity": {},
    "health": {},
    "provider_capabilities": {},
    "toolcall_log_tail": {"lines": 10},
    "self-check": {},
    "status": {},
    
    # Provider tools (8)
    "kimi_upload_and_extract": {"file_path": "test.txt"},
    "kimi_multi_file_chat": {"files": ["test1.txt", "test2.txt"], "question": "Summarize these files"},
    "kimi_intent_analysis": {"prompt": "I want to build a website"},
    "kimi_capture_headers": {},
    "kimi_chat_with_tools": {"prompt": "What's the weather?", "tools": []},
    "glm_upload_file": {"file_path": "test.txt"},
    "glm_web_search": {"search_query": "Python programming"},  # Fixed: search_query not query
    "glm_payload_preview": {"prompt": "Test prompt"},
}

TEST_TEMPLATE = '''"""
Test suite for {tool_name_title} tool - MCP Server validation

Tests the {tool_name} tool through the MCP server via WebSocket daemon.
This validates the ENTIRE stack: MCP protocol → daemon → server → tool → providers → APIs
"""

import sys
import io
from pathlib import Path

# Fix Windows console encoding for Unicode
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from utils.mcp_client import MCPClient
from utils.test_runner import TestRunner


def test_{tool_name}_basic_glm(mcp_client: MCPClient, **kwargs):
    """Test {tool_name} - basic functionality with GLM"""
    result = mcp_client.call_tool(
        tool_name="{tool_name}",
        arguments={arguments_glm},
        test_name="{tool_name}",
        variation="basic_glm"
    )

    outputs = result.get("outputs", [])
    success = len(outputs) > 0

    content = ""
    if outputs and isinstance(outputs[0], dict):
        content = outputs[0].get("text", "")

    return {{
        "success": success,
        "content": content[:200] if content else "",
        "outputs_count": len(outputs)
    }}


def test_{tool_name}_basic_kimi(mcp_client: MCPClient, **kwargs):
    """Test {tool_name} - basic functionality with Kimi"""
    result = mcp_client.call_tool(
        tool_name="{tool_name}",
        arguments={arguments_kimi},
        test_name="{tool_name}",
        variation="basic_kimi"
    )

    outputs = result.get("outputs", [])
    success = len(outputs) > 0

    content = ""
    if outputs and isinstance(outputs[0], dict):
        content = outputs[0].get("text", "")

    return {{
        "success": success,
        "content": content[:200] if content else "",
        "outputs_count": len(outputs)
    }}


if __name__ == "__main__":
    mcp_client = MCPClient()
    runner = TestRunner()

    tests = [
        ("{tool_name}", "basic_glm", test_{tool_name}_basic_glm),
        ("{tool_name}", "basic_kimi", test_{tool_name}_basic_kimi),
    ]

    for tool_name, variation, test_func in tests:
        result = runner.run_test(
            tool_name=tool_name,
            variation=variation,
            test_func=test_func,
            mcp_client=mcp_client
        )

        print(f"\\n{{'='*60}}")
        print(f"Test: {{tool_name}}/{{variation}}")
        print(f"Status: {{result.get('status', 'unknown')}}")
        if result.get('status') == 'passed':
            print("PASSED")
        else:
            print(f"FAILED: {{result.get('error', 'Unknown error')}}")
        print(f"{{'='*60}}")

    runner.generate_report()
    runner.print_results()

    print(f"\\n{tool_name_title} tool tests complete!")
    print(f"Results saved to: {{runner.get_results_dir()}}")
'''

def format_arguments(args, model="glm-4.5-flash"):
    """Format arguments dict for template"""
    if not args:
        return "{}"
    
    # Add model if not present and tool accepts it
    if "model" not in args and model:
        args = {**args, "model": model}
    
    # Format as Python dict string
    items = [f'"{k}": {repr(v)}' for k, v in args.items()]
    return "{" + ", ".join(items) + "}"


def regenerate_test_file(tool_name, test_dir):
    """Regenerate a single test file"""
    # Get tool arguments
    base_args = TOOL_DEFINITIONS.get(tool_name, {})
    
    # Create arguments for GLM and Kimi
    args_glm = base_args.copy()
    if "model" in args_glm:
        args_glm["model"] = "glm-4.5-flash"
    
    args_kimi = base_args.copy()
    if "model" in args_kimi:
        args_kimi["model"] = "kimi-k2-0905-preview"
    
    # Format arguments
    arguments_glm = format_arguments(args_glm, None)
    arguments_kimi = format_arguments(args_kimi, None)
    
    # Generate test content
    content = TEST_TEMPLATE.format(
        tool_name=tool_name,
        tool_name_title=tool_name.replace("_", " ").title(),
        arguments_glm=arguments_glm,
        arguments_kimi=arguments_kimi
    )
    
    # Write file
    file_path = test_dir / f"test_{tool_name}.py"
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Regenerated: {file_path}")


def main():
    """Regenerate all test files"""
    base_dir = Path(__file__).parent.parent / "tests"
    
    # Core tools
    core_dir = base_dir / "core_tools"
    core_tools = ["analyze", "debug", "codereview", "refactor", "secaudit", 
                  "planner", "tracer", "testgen", "consensus", "thinkdeep", 
                  "docgen", "precommit", "challenge"]
    
    print("\n🔄 Regenerating core_tools tests...")
    for tool in core_tools:
        regenerate_test_file(tool, core_dir)
    
    # Advanced tools
    advanced_dir = base_dir / "advanced_tools"
    advanced_tools = ["listmodels", "version", "activity", "health", 
                      "provider_capabilities", "toolcall_log_tail", 
                      "self-check", "status"]
    
    print("\n🔄 Regenerating advanced_tools tests...")
    for tool in advanced_tools:
        regenerate_test_file(tool, advanced_dir)
    
    # Provider tools
    provider_dir = base_dir / "provider_tools"
    provider_tools = ["kimi_upload_and_extract", "kimi_multi_file_chat", 
                      "kimi_intent_analysis", "kimi_capture_headers", 
                      "kimi_chat_with_tools", "glm_upload_file", 
                      "glm_web_search", "glm_payload_preview"]
    
    print("\n🔄 Regenerating provider_tools tests...")
    for tool in provider_tools:
        regenerate_test_file(tool, provider_dir)
    
    print("\n✅ All test files regenerated!")
    print(f"\nTotal: {len(core_tools) + len(advanced_tools) + len(provider_tools)} files")
    print("\nNote: test_chat.py was manually updated and not regenerated.")
    print("\nNext: Start daemon and run tests:")
    print("  powershell -NoProfile -ExecutionPolicy Bypass -File .\\scripts\\ws_start.ps1 -Restart")
    print("  python tool_validation_suite/scripts/run_all_tests_simple.py")


if __name__ == "__main__":
    main()

