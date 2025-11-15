#!/usr/bin/env python3
"""
Proper MCP Test Script for Kimi K2 Thinking Model
This script demonstrates the correct MCP protocol calls to test kimi-k2-thinking
"""

import json
import subprocess
import sys
import time

def run_mcp_call(mcp_message, description):
    """Run an MCP call and return the result"""
    print(f"\n=== {description} ===")
    print(f"MCP Request: {json.dumps(mcp_message, indent=2)}")
    
    try:
        # Run the MCP server and send the message
        process = subprocess.Popen(
            ["npx", "@modelcontextprotocol/cli", "run-stdio", "--path", "exai-mcp-server"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Send the MCP message
        stdout, stderr = process.communicate(input=json.dumps(mcp_message) + "\n", timeout=30)
        
        print(f"MCP Response: {stdout}")
        if stderr:
            print(f"Errors: {stderr}")
        
        return stdout
        
    except subprocess.TimeoutExpired:
        process.kill()
        print("MCP call timed out")
        return None
    except Exception as e:
        print(f"MCP call failed: {e}")
        return None

def main():
    print("=== Testing Kimi K2 Thinking Model with Proper MCP Calls ===")
    
    # Test 1: Check server status first
    status_call = {
        "op": "call_tool",
        "arguments": {
            "name": "status",
            "arguments": {}
        }
    }
    run_mcp_call(status_call, "Server Status Check")
    
    # Test 2: List available models
    listmodels_call = {
        "op": "call_tool", 
        "arguments": {
            "name": "listmodels",
            "arguments": {}
        }
    }
    run_mcp_call(listmodels_call, "List Available Models")
    
    # Test 3: Test Kimi K2 Thinking with chat
    kimi_chat_call = {
        "op": "call_tool",
        "arguments": {
            "name": "kimi_chat_with_tools",
            "arguments": {
                "prompt": "What are the key capabilities of kimi-k2-thinking model compared to other Kimi models?",
                "model": "kimi-k2-thinking",
                "tools": [],
                "tool_choice": "none"
            }
        }
    }
    run_mcp_call(kimi_chat_call, "Test Kimi K2 Thinking Chat")
    
    # Test 4: Test with a simple prompt
    simple_chat_call = {
        "op": "call_tool",
        "arguments": {
            "name": "kimi_chat_with_tools", 
            "arguments": {
                "prompt": "Hello, can you confirm you are kimi-k2-thinking?",
                "model": "kimi-k2-thinking"
            }
        }
    }
    run_mcp_call(simple_chat_call, "Simple Kimi K2 Thinking Test")

if __name__ == "__main__":
    main()