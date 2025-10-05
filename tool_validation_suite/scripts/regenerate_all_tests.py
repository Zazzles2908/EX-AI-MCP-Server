"""
Script to regenerate all test files to use NEW MCP daemon approach

This script converts all 36 test files from OLD approach (api_client.py)
to NEW approach (mcp_client.py) for full stack testing.
"""

import os
from pathlib import Path

# Tool definitions with their arguments
TOOL_DEFINITIONS = {
    # Core tools (14)
    "analyze": {"content": "This is test content for analysis.", "model": "glm-4.5-flash"},
    "debug": {"code": "def test(): return 42", "model": "glm-4.5-flash"},
    "codereview": {"code": "def hello(): print('world')", "model": "glm-4.5-flash"},
    "refactor": {"code": "x=1;y=2;print(x+y)", "model": "glm-4.5-flash"},
    "secaudit": {"code": "password = 'hardcoded123'", "model": "glm-4.5-flash"},
    "planner": {"task": "Build a simple web app", "model": "glm-4.5-flash"},
    "tracer": {"code": "def factorial(n): return 1 if n==0 else n*factorial(n-1)", "model": "glm-4.5-flash"},
    "testgen": {"code": "def add(a, b): return a + b", "model": "glm-4.5-flash"},
    "consensus": {"question": "What is 2+2?", "model": "glm-4.5-flash"},
    "thinkdeep": {"question": "Explain recursion", "model": "glm-4.5-flash"},
    "docgen": {"code": "def process_data(data): return data.upper()", "model": "glm-4.5-flash"},
    "precommit": {"files": ["test.py"], "model": "glm-4.5-flash"},
    "challenge": {"claim": "Python is the best language", "model": "glm-4.5-flash"},
    
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

