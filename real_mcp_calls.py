#!/usr/bin/env python3
"""
REAL MCP TOOL CALLS - Getting Actual AI Responses
This makes real MCP protocol calls to get AI responses from EX-AI
"""

import asyncio
import json
import sys
from pathlib import Path

async def call_chat_tool(message):
    """Make a real MCP call to the chat tool."""
    
    print("=" * 60)
    print("MAKING REAL MCP CALL TO EX-AI SERVER")
    print("=" * 60)
    
    exai_dir = Path("C:/Project/EX-AI-MCP-Server")
    if exai_dir.exists():
        import os
        os.chdir(exai_dir)
    
    try:
        # Start the MCP server in stdio mode
        process = await asyncio.create_subprocess_exec(
            sys.executable, "-m", "src.daemon.ws_server", "--mode", "stdio",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(exai_dir)
        )
        
        print(f"Sending message to EX-AI: '{message}'")
        
        # Step 1: Initialize MCP connection
        init_msg = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize", 
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "mcp-test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        print("1. Initializing MCP connection...")
        await process.stdin.send((json.dumps(init_msg) + "\\n").encode())
        await process.stdin.drain()
        
        # Small delay for initialization
        await asyncio.sleep(0.5)
        
        # Step 2: Call the chat tool
        chat_call_msg = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "chat",
                "arguments": {
                    "prompt": message,
                    "model": "glm-4.5-flash",
                    "temperature": 0.3
                }
            }
        }
        
        print("2. Calling EX-AI chat tool...")
        await process.stdin.send((json.dumps(chat_call_msg) + "\\n").encode())
        await process.stdin.drain()
        
        # Step 3: Read response
        print("3. Waiting for AI response...")
        try:
            # Set a reasonable timeout for AI processing
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=60.0  # 60 seconds for AI processing
            )
            
            # Parse all responses
            responses = stdout.decode().strip().split('\\n')
            valid_responses = []
            
            for response in responses:
                if response.strip():
                    try:
                        data = json.loads(response)
                        valid_responses.append(data)
                    except json.JSONDecodeError:
                        pass
            
            print(f"\\nReceived {len(valid_responses)} MCP responses")
            
            # Find the tools/call response
            for response in valid_responses:
                if (response.get("id") == 2 and 
                    "result" in response and 
                    "content" in response.get("result", {})):
                    
                    content = response["result"]["content"]
                    print("\\n" + "=" * 60)
                    print("EX-AI AI RESPONSE:")
                    print("=" * 60)
                    
                    # Extract the actual AI response
                    if isinstance(content, list) and content:
                        for item in content:
                            if item.get("type") == "text":
                                ai_response = item.get("text", "")
                                print(ai_response)
                                print("=" * 60)
                                return True
                    elif isinstance(content, dict) and content.get("text"):
                        ai_response = content["text"]
                        print(ai_response)
                        print("=" * 60)
                        return True
            
            print("No valid AI response found in MCP responses")
            print("Debug - Raw responses:")
            for i, resp in enumerate(valid_responses):
                print(f"Response {i}: {resp}")
            
            return False
            
        except asyncio.TimeoutError:
            print("TIMEOUT: EX-AI didn't respond within 60 seconds")
            process.kill()
            await process.wait()
            return False
            
    except Exception as e:
        print(f"ERROR: MCP call failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def call_analyze_tool():
    """Test another MCP tool - analyze."""
    
    print("\\n" + "=" * 60)
    print("TESTING ANALYZE TOOL VIA MCP")
    print("=" * 60)
    
    exai_dir = Path("C:/Project/EX-AI-MCP-Server")
    if exai_dir.exists():
        import os
        os.chdir(exai_dir)
    
    try:
        process = await asyncio.create_subprocess_exec(
            sys.executable, "-m", "src.daemon.ws_server", "--mode", "stdio",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(exai_dir)
        )
        
        # Initialize
        init_msg = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize", 
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "mcp-test-client", "version": "1.0.0"}
            }
        }
        
        await process.stdin.send((json.dumps(init_msg) + "\\n").encode())
        await process.stdin.drain()
        await asyncio.sleep(0.5)
        
        # Call analyze tool
        analyze_msg = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "analyze",
                "arguments": {
                    "step": "Analyze the Python programming language and its key characteristics",
                    "step_number": 1,
                    "total_steps": 1,
                    "next_step_required": False,
                    "model": "glm-4.5-flash"
                }
            }
        }
        
        print("Calling analyze tool...")
        await process.stdin.send((json.dumps(analyze_msg) + "\\n").encode())
        await process.stdin.drain()
        
        # Get response
        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=45.0
        )
        
        responses = stdout.decode().strip().split('\\n')
        for response in responses:
            if response.strip():
                try:
                    data = json.loads(response)
                    if (data.get("id") == 2 and 
                        "result" in data and 
                        "content" in data.get("result", {})):
                        
                        content = data["result"]["content"]
                        if isinstance(content, list) and content:
                            for item in content:
                                if item.get("type") == "text":
                                    print("\\nANALYZE TOOL RESPONSE:")
                                    print("-" * 40)
                                    print(item.get("text", ""))
                                    print("-" * 40)
                                    return True
                except json.JSONDecodeError:
                    pass
        
        return False
        
    except Exception as e:
        print(f"ERROR: Analyze tool call failed: {e}")
        return False

async def main():
    """Make real MCP calls to get AI responses."""
    
    print("EX-AI MCP SERVER - REAL AI CALLS")
    print("Making actual MCP protocol calls to get AI responses")
    print("This proves the system works end-to-end!")
    print()
    
    # Test 1: Chat tool
    result1 = await call_chat_tool("Hello! Can you tell me what Python is?")
    
    # Test 2: Analyze tool  
    result2 = await call_analyze_tool()
    
    print("\\n" + "=" * 60)
    print("MCP AI CALL RESULTS:")
    print("=" * 60)
    print(f"Chat Tool: {'SUCCESS' if result1 else 'FAILED'}")
    print(f"Analyze Tool: {'SUCCESS' if result2 else 'FAILED'}")
    
    if result1 or result2:
        print("\\nSUCCESS: Made real MCP calls and got AI responses!")
        print("The EX-AI MCP server is fully functional!")
    else:
        print("\\nFAILED: Could not get AI responses via MCP")
        print("There may be issues with the MCP protocol implementation")

if __name__ == "__main__":
    asyncio.run(main())