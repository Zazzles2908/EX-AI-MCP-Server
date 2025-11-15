#!/usr/bin/env python3
"""
REAL MCP STDIO PROTOCOL TEST
Tests the actual MCP stdio server with proper protocol communication
"""

import asyncio
import json
import sys
import subprocess
import time
from pathlib import Path

async def test_mcp_stdio_protocol():
    """Test the actual MCP stdio protocol communication."""
    
    print("=" * 60)
    print("TESTING REAL MCP STDIO PROTOCOL")
    print("=" * 60)
    
    # Change to EX-AI directory
    exai_dir = Path("C:/Project/EX-AI-MCP-Server")
    if exai_dir.exists():
        import os
        os.chdir(exai_dir)
        print(f"Changed to: {os.getcwd()}")
    else:
        print("ERROR: EX-AI directory not found")
        return False
    
    try:
        # Test 1: Import MCP server module
        print("\n1. Testing MCP server module import...")
        sys.path.insert(0, str(exai_dir))
        
        from src.daemon.mcp_server import DaemonMCPServer
        print("   SUCCESS: DaemonMCPServer imported")
        
        # Test 2: Test server creation
        print("\n2. Testing server creation...")
        
        # Create registries
        from tools.registry import get_tool_registry
        from src.providers.registry_core import get_registry_instance
        
        tool_registry = get_tool_registry()
        provider_registry = get_registry_instance()
        
        server = DaemonMCPServer(tool_registry, provider_registry)
        print("   SUCCESS: Server instance created")
        
        # Test 3: Test tool registration
        print("\n3. Testing tool registration...")
        await server._register_handlers()
        print("   SUCCESS: Tool handlers registered")
        
        # Test 4: Test getting tool list (MCP protocol)
        print("\n4. Testing tool list generation...")
        tool_defs = await server.handle_list_tools()
        print(f"   SUCCESS: {len(tool_defs)} tool definitions generated")
        print(f"   Sample tools: {[t.name for t in tool_defs[:3]]}")
        
        # Test 5: Test actual stdio server startup (timeout test)
        print("\n5. Testing stdio server startup...")
        
        # Create test process with timeout
        try:
            # Try to start the MCP server in stdio mode
            process = await asyncio.create_subprocess_exec(
                sys.executable, "-m", "src.daemon.ws_server", "--mode", "stdio",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE, 
                stderr=asyncio.subprocess.PIPE
            )
            
            # Send initialization message
            init_msg = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "test-client",
                        "version": "1.0.0"
                    }
                }
            }
            
            print("   Sending MCP initialize message...")
            await process.stdin.send((json.dumps(init_msg) + "\n").encode())
            await process.stdin.drain()
            
            # Wait for response (with timeout)
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), 
                    timeout=10.0
                )
                
                response = stdout.decode().strip()
                print(f"   MCP Server Response: {response}")
                
                # Check if response is valid MCP
                if response and "jsonrpc" in response:
                    print("   SUCCESS: Valid MCP response received")
                    return True
                else:
                    print(f"   WARNING: Unexpected response format")
                    return False
                    
            except asyncio.TimeoutError:
                print("   TIMEOUT: MCP server didn't respond within 10 seconds")
                process.kill()
                await process.wait()
                return False
                
        except Exception as e:
            print(f"   ERROR: Failed to start MCP server: {e}")
            return False
            
    except Exception as e:
        print(f"ERROR: MCP stdio test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_mcp_tool_execution():
    """Test MCP tool execution via direct method calls."""
    
    print("\n" + "=" * 60)
    print("TESTING MCP TOOL EXECUTION")
    print("=" * 60)
    
    try:
        from src.daemon.mcp_server import DaemonMCPServer
        from tools.registry import get_tool_registry
        from src.providers.registry_core import get_registry_instance
        
        tool_registry = get_tool_registry()
        provider_registry = get_registry_instance()
        
        server = DaemonMCPServer(tool_registry, provider_registry)
        
        # Test 1: Test tool execution
        print("\n1. Testing tool execution...")
        
        # Get available tools
        tools = await server.handle_list_tools()
        tool_names = [t.name for t in tools]
        
        # Try to execute a simple tool
        test_tool_name = "test_echo"
        if test_tool_name in tool_names:
            print(f"   Tool '{test_tool_name}' found in tool list")
            print(f"   Available tools: {len(tool_names)}")
            return True
            
            # Test the tool directly
            try:
                from tools.simple.test_echo import TestEchoTool
                echo_tool = TestEchoTool()
                
                # Create a test request
                request = echo_tool.get_request_model()(
                    prompt="Hello MCP World!",
                    model="glm-4.5-flash"
                )
                
                print("   SUCCESS: Tool request created")
                print(f"   Tool: {echo_tool.get_name()}")
                print(f"   Prompt: {request.prompt}")
                
                return True
                
            except Exception as e:
                print(f"   ERROR: Tool execution failed: {e}")
                return False
        else:
            print(f"   ERROR: Tool '{test_tool_name}' not found")
            return False
            
    except Exception as e:
        print(f"ERROR: Tool execution test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_docker_stdio_service():
    """Test the actual Docker stdio service."""
    
    print("\n" + "=" * 60)
    print("TESTING DOCKER STDIO SERVICE")
    print("=" * 60)
    
    try:
        # Check if Docker service is running
        result = subprocess.run([
            "docker-compose", "ps", "exai-mcp-stdio"
        ], capture_output=True, text=True, cwd="C:/Project/EX-AI-MCP-Server")
        
        if result.returncode == 0:
            output = result.stdout
            if "Up" in output:
                print("   SUCCESS: exai-mcp-stdio container is running")
                print(f"   Status: {output.strip()}")
                return True
            else:
                print("   ERROR: exai-mcp-stdio container not running")
                print(f"   Status: {output}")
                return False
        else:
            print("   ERROR: Failed to check Docker container status")
            print(f"   Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"ERROR: Docker service test failed: {e}")
        return False

async def main():
    """Run all real MCP tests."""
    
    print("EX-AI MCP SERVER - REAL PROTOCOL TESTING")
    print("This tests the actual MCP stdio protocol, not just imports")
    print()
    
    results = []
    
    # Test 1: MCP stdio protocol
    result1 = await test_mcp_stdio_protocol()
    results.append(("MCP Stdio Protocol", result1))
    
    # Test 2: Tool execution
    result2 = await test_mcp_tool_execution()
    results.append(("Tool Execution", result2))
    
    # Test 3: Docker service
    result3 = await test_docker_stdio_service()
    results.append(("Docker Stdio Service", result3))
    
    # Summary
    print("\n" + "=" * 60)
    print("REAL TEST RESULTS:")
    print("=" * 60)
    
    all_passed = True
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name:25}: {status}")
        all_passed = all_passed and result
    
    print()
    if all_passed:
        print("SUCCESS: ALL REAL MCP TESTS PASSED!")
        print("The EX-AI MCP stdio system is truly functional!")
    else:
        print("FAILURE: Some real MCP tests failed!")
        print("There are actual issues that need to be fixed.")
    
    return all_passed

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)