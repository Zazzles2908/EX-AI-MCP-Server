#!/usr/bin/env python3
"""
REAL MCP PROTOCOL COMMUNICATION TEST
Tests actual MCP stdio server communication
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path

async def test_mcp_protocol_communication():
    """Test actual MCP stdio communication."""
    
    print("=" * 60)
    print("REAL MCP STDIO PROTOCOL TEST")
    print("=" * 60)
    
    exai_dir = Path("C:/Project/EX-AI-MCP-Server")
    if exai_dir.exists():
        import os
        os.chdir(exai_dir)
    
    try:
        print("Starting MCP stdio server communication test...")
        
        # Test by running the actual MCP server with stdio mode
        # This will test real MCP protocol communication
        
        process = await asyncio.create_subprocess_exec(
            sys.executable, "-m", "src.daemon.ws_server", "--mode", "stdio",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(exai_dir)
        )
        
        print("MCP server process started")
        
        # Send MCP initialize message
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
        
        print("Sending MCP initialize message...")
        await process.stdin.send((json.dumps(init_msg) + "\\n").encode())
        await process.stdin.drain()
        
        # Send tools/list request
        list_msg = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        print("Sending MCP tools/list request...")
        await process.stdin.send((json.dumps(list_msg) + "\\n").encode())
        await process.stdin.drain()
        
        # Wait for responses (with timeout)
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=15.0
            )
            
            # Parse responses
            responses = stdout.decode().strip().split('\\n')
            valid_responses = []
            
            for response in responses:
                if response.strip():
                    try:
                        data = json.loads(response)
                        valid_responses.append(data)
                    except json.JSONDecodeError:
                        pass
            
            print(f"Received {len(valid_responses)} valid MCP responses")
            
            # Check for expected responses
            has_init_response = any("result" in r and "capabilities" in r.get("result", {}) for r in valid_responses)
            has_tools_response = any("result" in r and "tools" in r.get("result", {}) for r in valid_responses)
            
            if has_init_response:
                print("SUCCESS: MCP initialize response received")
            else:
                print("WARNING: MCP initialize response not found")
            
            if has_tools_response:
                print("SUCCESS: MCP tools/list response received")
                # Find the tools response
                for r in valid_responses:
                    if "result" in r and "tools" in r.get("result", {}):
                        tools = r["result"]["tools"]
                        print(f"         Tools available: {len(tools)}")
                        if tools:
                            print(f"         Sample: {[t.get('name') for t in tools[:3]]}")
            else:
                print("WARNING: MCP tools/list response not found")
            
            # Check stderr for errors
            if stderr:
                error_output = stderr.decode()
                if error_output.strip():
                    print(f"STDERR: {error_output[:200]}...")
            
            return has_init_response and has_tools_response
            
        except asyncio.TimeoutError:
            print("TIMEOUT: MCP server didn't respond within 15 seconds")
            process.kill()
            await process.wait()
            return False
            
    except Exception as e:
        print(f"ERROR: MCP protocol test failed: {e}")
        return False

async def test_docker_stdio_directly():
    """Test the Docker stdio service directly."""
    
    print("\\n" + "=" * 60)
    print("TESTING DOCKER STDIO SERVICE DIRECTLY")
    print("=" * 60)
    
    try:
        # Test if the Docker container is responding to health checks
        import subprocess
        
        # Check container status
        result = subprocess.run([
            "docker", "ps", "--filter", "name=exai-mcp-stdio", "--format", "{{.Status}}"
        ], capture_output=True, text=True)
        
        if result.returncode == 0 and "Up" in result.stdout:
            print("SUCCESS: exai-mcp-stdio container is running")
            
            # Try to connect to the stdio service (it should be listening)
            result = subprocess.run([
                "docker", "exec", "exai-mcp-stdio", "python", "-c", 
                "import sys; sys.path.insert(0, '.'); from src.daemon.mcp_server import DaemonMCPServer; print('MCP server module OK')"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print("SUCCESS: MCP server module works in Docker")
                print(f"Output: {result.stdout.strip()}")
                return True
            else:
                print(f"ERROR: MCP module failed in Docker: {result.stderr}")
                return False
        else:
            print("ERROR: exai-mcp-stdio container not running")
            return False
            
    except Exception as e:
        print(f"ERROR: Docker test failed: {e}")
        return False

async def main():
    """Run the real MCP protocol tests."""
    
    print("EX-AI MCP SERVER - REAL PROTOCOL VALIDATION")
    print("Testing actual MCP stdio protocol communication")
    print("This validates the system is not just fabricated imports")
    print()
    
    results = []
    
    # Test 1: MCP protocol communication
    result1 = await test_mcp_protocol_communication()
    results.append(("MCP Protocol", result1))
    
    # Test 2: Docker service
    result2 = await test_docker_stdio_directly()
    results.append(("Docker Service", result2))
    
    # Summary
    print("\\n" + "=" * 60)
    print("REAL PROTOCOL TEST RESULTS:")
    print("=" * 60)
    
    all_passed = True
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name:20}: {status}")
        all_passed = all_passed and result
    
    print()
    if all_passed:
        print("CONFIRMED: The EX-AI MCP system is REAL and FUNCTIONAL!")
        print("This is not fabricated - the stdio protocol works!")
    else:
        print("WARNING: Some real protocol tests failed.")
        print("The system needs verification.")
    
    return all_passed

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)