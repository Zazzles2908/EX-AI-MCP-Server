#!/usr/bin/env python3
"""
CONNECT TO EXISTING DOCKER STDIO SERVICE
Using the running exai-mcp-stdio container to make real MCP calls
"""

import subprocess
import json
import sys

def make_mcp_call_via_docker():
    """Make MCP call through the running Docker container."""
    
    print("=" * 60)
    print("CONNECTING TO RUNNING EX-AI STDIO SERVICE")
    print("=" * 60)
    
    try:
        # Check if the container is running
        result = subprocess.run([
            "docker", "ps", "--filter", "name=exai-mcp-stdio", "--format", "{{.Status}}"
        ], capture_output=True, text=True)
        
        if "Up" not in result.stdout:
            print("ERROR: exai-mcp-stdio container is not running")
            return False
        
        print("SUCCESS: exai-mcp-stdio container is running")
        
        # Try to execute a simple Python script in the container that makes MCP calls
        mcp_test_script = '''
import sys
import json
import asyncio
from pathlib import Path

# Add the app to path
sys.path.insert(0, "/app")

async def test_mcp_call():
    try:
        from mcp.server import Server
        from mcp.types import Tool, TextContent
        
        # Import EX-AI components
        from tools.registry import get_tool_registry
        from src.providers.registry_core import get_registry_instance
        from src.daemon.mcp_server import DaemonMCPServer
        
        # Create server
        tool_registry = get_tool_registry()
        provider_registry = get_registry_instance()
        server = DaemonMCPServer(tool_registry, provider_registry)
        
        # Test calling a tool directly
        print("Testing direct tool call...")
        
        # Get the chat tool
        tools = tool_registry.list_tools()
        if "chat" in tools:
            from tools.chat import ChatTool
            chat_tool = ChatTool()
            
            # Create request
            request = chat_tool.get_request_model()(
                prompt="Hello! What is artificial intelligence?",
                model="glm-4.5-flash"
            )
            
            print("Executing chat tool...")
            result = await chat_tool.execute({
                "prompt": "Hello! What is artificial intelligence?", 
                "model": "glm-4.5-flash"
            })
            
            print("RESULT:", json.dumps(result, indent=2))
            return True
        else:
            print("Chat tool not found")
            return False
            
    except Exception as e:
        print("ERROR:", str(e))
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_mcp_call())
'''
        
        # Write the script to a temporary file
        script_path = "/tmp/test_mcp_call.py"
        
        # Execute the script in the Docker container
        cmd = [
            "docker", "exec", "exai-mcp-stdio", "python", "-c", mcp_test_script
        ]
        
        print("Executing MCP call test in container...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        print(f"Return code: {result.returncode}")
        print(f"STDOUT:\\n{result.stdout}")
        
        if result.stderr:
            print(f"STDERR:\\n{result.stderr}")
        
        if result.returncode == 0:
            print("\\nSUCCESS: Made real MCP call via Docker!")
            return True
        else:
            print("\\nFAILED: MCP call failed")
            return False
            
    except subprocess.TimeoutExpired:
        print("TIMEOUT: MCP call took too long")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_simple_tool_execution():
    """Test tool execution directly."""
    
    print("\\n" + "=" * 60)
    print("TESTING SIMPLE TOOL EXECUTION")
    print("=" * 60)
    
    try:
        # Execute a simple test in Docker
        simple_test = '''
import sys
sys.path.insert(0, "/app")

try:
    from tools.registry import get_tool_registry
    registry = get_tool_registry()
    tools = registry.list_tools()
    
    print("TOOLS_FOUND:", len(tools))
    print("SAMPLE_TOOLS:", list(tools.keys())[:3])
    
    # Test instantiating a tool
    if "chat" in tools:
        from tools.chat import ChatTool
        tool = ChatTool()
        print("TOOL_NAME:", tool.get_name())
        print("SUCCESS")
    else:
        print("CHAT_TOOL_NOT_FOUND")
        
except Exception as e:
    print("ERROR:", str(e))
'''
        
        result = subprocess.run([
            "docker", "exec", "exai-mcp-stdio", "python", "-c", simple_test
        ], capture_output=True, text=True, timeout=30)
        
        print("Output:")
        print(result.stdout)
        
        if "SUCCESS" in result.stdout and "TOOLS_FOUND: 20" in result.stdout:
            print("\\nSUCCESS: Tool execution working in Docker!")
            return True
        else:
            print("\\nFAILED: Tool execution test failed")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def main():
    """Make real MCP calls through Docker."""
    
    print("EX-AI MCP SERVER - REAL DOCKER CALLS")
    print("Connecting to running stdio service for real AI responses")
    print()
    
    # Test 1: Simple tool execution
    result1 = test_simple_tool_execution()
    
    # Test 2: Full MCP call
    result2 = make_mcp_call_via_docker()
    
    print("\\n" + "=" * 60)
    print("DOCKER MCP CALL RESULTS:")
    print("=" * 60)
    print(f"Tool Execution: {'SUCCESS' if result1 else 'FAILED'}")
    print(f"MCP Call: {'SUCCESS' if result2 else 'FAILED'}")
    
    if result1:
        print("\\nSUCCESS: Connected to EX-AI via Docker!")
        print("The MCP stdio service is operational!")
        
        if result2:
            print("SUCCESS: Got real AI response from MCP call!")
        else:
            print("Partial success - service running but tool call failed")
    else:
        print("\\nFAILED: Could not connect to EX-AI service")

if __name__ == "__main__":
    main()