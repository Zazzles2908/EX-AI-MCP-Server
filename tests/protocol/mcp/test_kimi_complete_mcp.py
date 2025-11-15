#!/usr/bin/env python3
"""
Complete MCP Protocol Test for Kimi K2 Thinking
Demonstrates proper MCP calls including the complex analyze tool structure
"""

import json
import subprocess
import sys

def run_mcp_call(mcp_message, description):
    """Run an MCP call and return the result"""
    print(f"\n{'='*60}")
    print(f"=== {description} ===")
    print(f"{'='*60}")
    print(f"🔄 MCP Request:")
    print(json.dumps(mcp_message, indent=2))
    
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
        
        print(f"\n📤 MCP Response:")
        if stdout:
            print(stdout)
        if stderr:
            print(f"❌ Errors:")
            print(stderr)
        
        return stdout
        
    except subprocess.TimeoutExpired:
        process.kill()
        print("❌ MCP call timed out")
        return None
    except Exception as e:
        print(f"❌ MCP call failed: {e}")
        return None

def test_kimi_thinking_model():
    """Test the Kimi K2 Thinking model with various MCP calls"""
    
    print("🚀 Testing Kimi K2 Thinking Model with Proper MCP Protocol")
    
    # Test 1: Check server status
    status_call = {
        "jsonrpc": "2.0",
        "id": "status_test",
        "method": "tools/list"
    }
    run_mcp_call(status_call, "Server Status Check")
    
    # Test 2: Simple Kimi K2 Thinking chat (CORRECT TOOL NAME)
    kimi_chat_simple = {
        "jsonrpc": "2.0",
        "id": "kimi_chat_simple",
        "method": "tools/call",
        "params": {
            "name": "kimi_chat_with_tools",
            "arguments": {
                "prompt": "Hello! Can you confirm you are the kimi-k2-thinking model?",
                "model": "kimi-k2-thinking"
            }
        }
    }
    run_mcp_call(kimi_chat_simple, "Simple Kimi K2 Thinking Chat")
    
    # Test 3: Complex prompt for Kimi K2 Thinking
    kimi_chat_complex = {
        "jsonrpc": "2.0", 
        "id": "kimi_chat_complex",
        "method": "tools/call",
        "params": {
            "name": "kimi_chat_with_tools",
            "arguments": {
                "prompt": "What are the key differences between kimi-k2-thinking and other Kimi models like kimi-k2-0711-preview? Focus on context window size, thinking capabilities, and performance characteristics.",
                "model": "kimi-k2-thinking"
            }
        }
    }
    run_mcp_call(kimi_chat_complex, "Complex Kimi K2 Thinking Analysis")
    
    # Test 4: AnalyZ Workflow with PROPER structure
    analyze_workflow = {
        "jsonrpc": "2.0",
        "id": "analyze_kimi_capabilities", 
        "method": "tools/call",
        "params": {
            "name": "analyze",
            "arguments": {
                # REQUIRED FIELDS for AnalyzeWorkflowRequest:
                "step": "Analyze the capabilities and features of the kimi-k2-thinking AI model, focusing on its extended thinking capabilities, context window, and performance characteristics compared to other Kimi models.",
                "step_number": 1,
                "total_steps": 1,
                "next_step_required": False,
                "findings": "Investigating kimi-k2-thinking model specifications and capabilities",
                # OPTIONAL FIELDS:
                "files_checked": [],
                "relevant_files": [],
                "relevant_context": [],
                "issues_found": [],
                "backtrack_from_step": None,
                "images": None
            }
        }
    }
    run_mcp_call(analyze_workflow, "Analyze Workflow - Kimi K2 Thinking Capabilities")
    
    # Test 5: List models to verify kimi-k2-thinking is available
    list_models_call = {
        "jsonrpc": "2.0",
        "id": "list_models", 
        "method": "tools/call",
        "params": {
            "name": "listmodels",
            "arguments": {}
        }
    }
    run_mcp_call(list_models_call, "List Available Models")

if __name__ == "__main__":
    test_kimi_thinking_model()