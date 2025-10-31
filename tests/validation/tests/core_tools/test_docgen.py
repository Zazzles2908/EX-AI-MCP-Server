"""
Test suite for Docgen tool - MCP Server validation

Tests the docgen tool through the MCP server via WebSocket daemon.
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


def test_docgen_basic_glm(mcp_client: MCPClient, **kwargs):
    """Test docgen - basic functionality with GLM"""
    result = mcp_client.call_tool(
        tool_name="docgen",
        arguments={"step": 'Generate documentation for the process_data function', "step_number": 1, "total_steps": 1, "next_step_required": False, "findings": 'Documentation generation requested', "relevant_files": ['tool_validation_suite/fixtures/sample_code.py'], "num_files_documented": 0, "total_files_to_document": 1, "model": 'glm-4.5-flash', "use_assistant_model": False},
        test_name="docgen",
        variation="basic_glm"
    )

    outputs = result.get("outputs", [])
    success = len(outputs) > 0

    content = ""
    if outputs and isinstance(outputs[0], dict):
        content = outputs[0].get("text", "")

    return {
        "success": success,
        "content": content[:200] if content else "",
        "outputs_count": len(outputs)
    }


def test_docgen_basic_kimi(mcp_client: MCPClient, **kwargs):
    """Test docgen - basic functionality with Kimi"""
    result = mcp_client.call_tool(
        tool_name="docgen",
        arguments={"step": 'Generate documentation for the process_data function', "step_number": 1, "total_steps": 1, "next_step_required": False, "findings": 'Documentation generation requested', "relevant_files": ['tool_validation_suite/fixtures/sample_code.py'], "num_files_documented": 0, "total_files_to_document": 1, "model": 'kimi-k2-0905-preview', "use_assistant_model": False},
        test_name="docgen",
        variation="basic_kimi"
    )

    outputs = result.get("outputs", [])
    success = len(outputs) > 0

    content = ""
    if outputs and isinstance(outputs[0], dict):
        content = outputs[0].get("text", "")

    return {
        "success": success,
        "content": content[:200] if content else "",
        "outputs_count": len(outputs)
    }


if __name__ == "__main__":
    mcp_client = MCPClient()
    runner = TestRunner()

    tests = [
        ("docgen", "basic_glm", test_docgen_basic_glm),
        ("docgen", "basic_kimi", test_docgen_basic_kimi),
    ]

    for tool_name, variation, test_func in tests:
        result = runner.run_test(
            tool_name=tool_name,
            variation=variation,
            test_func=test_func,
            mcp_client=mcp_client
        )

        print(f"\n{'='*60}")
        print(f"Test: {tool_name}/{variation}")
        print(f"Status: {result.get('status', 'unknown')}")
        if result.get('status') == 'passed':
            print("PASSED")
        else:
            print(f"FAILED: {result.get('error', 'Unknown error')}")
        print(f"{'='*60}")

    runner.generate_report()
    runner.print_results()

    print(f"\nDocgen tool tests complete!")
    print(f"Results saved to: {runner.get_results_dir()}")
