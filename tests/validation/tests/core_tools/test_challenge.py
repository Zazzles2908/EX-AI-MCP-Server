"""
Test suite for Challenge tool - MCP Server validation

Tests the challenge tool through the MCP server via WebSocket daemon.
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


def test_challenge_basic_glm(mcp_client: MCPClient, **kwargs):
    """Test challenge - basic functionality with GLM"""
    result = mcp_client.call_tool(
        tool_name="challenge",
        arguments={"prompt": 'Python is the best language for all use cases'},
        test_name="challenge",
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


def test_challenge_basic_kimi(mcp_client: MCPClient, **kwargs):
    """Test challenge - basic functionality with Kimi"""
    result = mcp_client.call_tool(
        tool_name="challenge",
        arguments={"prompt": 'Python is the best language for all use cases'},
        test_name="challenge",
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
        ("challenge", "basic_glm", test_challenge_basic_glm),
        ("challenge", "basic_kimi", test_challenge_basic_kimi),
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

    print(f"\nChallenge tool tests complete!")
    print(f"Results saved to: {runner.get_results_dir()}")
