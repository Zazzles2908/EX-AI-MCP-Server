#!/usr/bin/env python3
"""
MCP Server Test Script
Tests MCP protocol compliance and tool discovery
"""

import json
import subprocess
import sys
import time

def test_mcp_server():
    """Test the MCP server using docker exec"""
    
    # Test 1: Initialize connection
    init_request = {
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
    
    print("🔍 Testing MCP Server...")
    print(f"Request: {json.dumps(init_request, indent=2)}")
    
    # Send request to MCP server
    cmd = [
        "docker", "exec", "-i", "exai-mcp-stdio",
        "python", "-m", "src.daemon.ws_server", "--mode", "stdio"
    ]
    
    try:
        # Start the process
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Send initialize request
        request_json = json.dumps(init_request) + "\n"
        stdout, stderr = process.communicate(input=request_json, timeout=10)
        
        print("Response:")
        print(stdout)
        
        if stderr:
            print("Stderr:")
            print(stderr)
            
        return stdout
        
    except subprocess.TimeoutExpired:
        process.kill()
        print("❌ Request timed out")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    test_mcp_server()
