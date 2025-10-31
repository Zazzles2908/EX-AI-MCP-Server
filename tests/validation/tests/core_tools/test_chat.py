"""
Test suite for Chat tool - MCP Server validation

Tests the chat tool through the MCP server via WebSocket daemon.
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


def test_chat_basic_glm(mcp_client: MCPClient, **kwargs):
    """Test chat - basic functionality with GLM"""
    result = mcp_client.call_tool(
        tool_name="chat",
        arguments={
            "prompt": "What is 2+2? Answer with just the number.",
            "model": "glm-4.5-flash"
        },
        test_name="chat",
        variation="basic_glm"
    )

    outputs = result.get("outputs", [])
    success = len(outputs) > 0

    content = ""
    if outputs and isinstance(outputs[0], dict):
        content = outputs[0].get("text", "")

    # Check if response contains "4"
    contains_answer = "4" in content

    return {
        "success": success and contains_answer,
        "content": content[:200],
        "outputs_count": len(outputs)
    }


def test_chat_basic_kimi(mcp_client: MCPClient, **kwargs):
    """Test chat - basic functionality with Kimi"""
    result = mcp_client.call_tool(
        tool_name="chat",
        arguments={
            "prompt": "What is 2+2? Answer with just the number.",
            "model": "kimi-k2-0905-preview"
        },
        test_name="chat",
        variation="basic_kimi"
    )

    outputs = result.get("outputs", [])
    success = len(outputs) > 0

    content = ""
    if outputs and isinstance(outputs[0], dict):
        content = outputs[0].get("text", "")

    contains_answer = "4" in content

    return {
        "success": success and contains_answer,
        "content": content[:200],
        "outputs_count": len(outputs)
    }


def test_chat_long_prompt(mcp_client: MCPClient, **kwargs):
    """Test chat - with longer prompt"""
    long_prompt = "Explain the concept of artificial intelligence in one sentence. " * 5

    result = mcp_client.call_tool(
        tool_name="chat",
        arguments={
            "prompt": long_prompt,
            "model": "glm-4.5-flash"
        },
        test_name="chat",
        variation="long_prompt"
    )

    outputs = result.get("outputs", [])
    success = len(outputs) > 0

    content = ""
    if outputs and isinstance(outputs[0], dict):
        content = outputs[0].get("text", "")

    return {
        "success": success and len(content) > 0,
        "content": content[:200],
        "outputs_count": len(outputs)
    }


def test_chat_special_chars(mcp_client: MCPClient, **kwargs):
    """Test chat - with special characters"""
    result = mcp_client.call_tool(
        tool_name="chat",
        arguments={
            "prompt": "Echo this: Hello! 你好 🚀 @#$%",
            "model": "glm-4.5-flash"
        },
        test_name="chat",
        variation="special_chars"
    )

    outputs = result.get("outputs", [])
    success = len(outputs) > 0

    content = ""
    if outputs and isinstance(outputs[0], dict):
        content = outputs[0].get("text", "")

    return {
        "success": success,
        "content": content[:200],
        "outputs_count": len(outputs)
    }


if __name__ == "__main__":
    mcp_client = MCPClient()
    runner = TestRunner()

    tests = [
        ("chat", "basic_glm", test_chat_basic_glm),
        ("chat", "basic_kimi", test_chat_basic_kimi),
        ("chat", "long_prompt", test_chat_long_prompt),
        ("chat", "special_chars", test_chat_special_chars),
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

    print("\nChat tool tests complete!")
    print(f"Results saved to: {runner.get_results_dir()}")

