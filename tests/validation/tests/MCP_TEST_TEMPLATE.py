"""
MCP TEST TEMPLATE - Testing actual MCP server tools through daemon

This shows the CORRECT way to write test scripts that test the actual
EX-AI MCP Server tools through the WebSocket daemon.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.mcp_client import MCPClient
from utils.test_runner import TestRunner


def test_chat_basic(mcp_client: MCPClient, **kwargs):
    """Test chat tool - basic functionality"""
    # Call MCP tool through daemon
    result = mcp_client.call_tool(
        tool_name="chat",
        arguments={
            "prompt": "Say hello in 5 words",
            "model": "glm-4.5-flash"
        },
        test_name="chat",
        variation="basic_functionality"
    )
    
    # Extract outputs
    outputs = result.get("outputs", [])
    
    # Validate we got a response
    success = len(outputs) > 0
    
    # Extract text from first output
    content = ""
    if outputs and isinstance(outputs[0], dict):
        content = outputs[0].get("text", "")
    
    # Return test result
    return {
        "success": success and len(content) > 0,
        "content": content[:200],  # First 200 chars
        "outputs_count": len(outputs),
        "metadata": result.get("_metadata", {})
    }


def test_chat_kimi(mcp_client: MCPClient, **kwargs):
    """Test chat tool - with Kimi model"""
    result = mcp_client.call_tool(
        tool_name="chat",
        arguments={
            "prompt": "Say hello in 5 words",
            "model": "kimi-k2-0905-preview"
        },
        test_name="chat",
        variation="kimi_model"
    )
    
    outputs = result.get("outputs", [])
    success = len(outputs) > 0
    
    content = ""
    if outputs and isinstance(outputs[0], dict):
        content = outputs[0].get("text", "")
    
    return {
        "success": success and len(content) > 0,
        "content": content[:200],
        "outputs_count": len(outputs),
        "metadata": result.get("_metadata", {})
    }


def test_analyze_basic(mcp_client: MCPClient, **kwargs):
    """Test analyze tool - basic functionality"""
    result = mcp_client.call_tool(
        tool_name="analyze",
        arguments={
            "content": "This is a test document about AI and machine learning.",
            "model": "glm-4.5-flash"
        },
        test_name="analyze",
        variation="basic_functionality"
    )
    
    outputs = result.get("outputs", [])
    success = len(outputs) > 0
    
    content = ""
    if outputs and isinstance(outputs[0], dict):
        content = outputs[0].get("text", "")
    
    return {
        "success": success and len(content) > 0,
        "content": content[:200],
        "outputs_count": len(outputs),
        "metadata": result.get("_metadata", {})
    }


if __name__ == "__main__":
    # Initialize MCP client and test runner
    mcp_client = MCPClient()
    runner = TestRunner()
    
    # Define tests to run
    tests = [
        ("chat", "basic_functionality", test_chat_basic),
        ("chat", "kimi_model", test_chat_kimi),
        ("analyze", "basic_functionality", test_analyze_basic),
    ]
    
    # Run each test
    for tool_name, variation, test_func in tests:
        result = runner.run_test(
            tool_name=tool_name,
            variation=variation,
            test_func=test_func,
            mcp_client=mcp_client  # Pass MCP client instead of API client
        )
        
        print(f"\n{'='*60}")
        print(f"Test: {tool_name}/{variation}")
        print(f"Status: {result.get('status', 'unknown')}")
        if result.get('status') == 'passed':
            print(f"✅ PASSED")
        else:
            print(f"❌ FAILED: {result.get('error', 'Unknown error')}")
        print(f"{'='*60}")
    
    # Generate report
    runner.generate_report()
    
    # Print summary
    runner.print_results()
    
    print(f"\n✅ MCP tool tests complete!")
    print(f"Results saved to: {runner.get_results_dir()}")

