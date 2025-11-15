#!/usr/bin/env python3
"""
Proper MCP Protocol Test - Tests MCP servers with correct initialization
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any

# Add session tracking
sys.path.append(str(Path(__file__).resolve().parent))
from session_memory_tracker import get_session_tracker

def create_mcp_client_test(mcp_command, server_name):
    """Create a proper MCP client test"""
    
    print(f"\n{'='*60}")
    print(f"TESTING {server_name.upper()} MCP SERVER")
    print(f"{'='*60}")
    
    try:
        # Start the MCP server process
        if isinstance(mcp_command, list):
            process = subprocess.Popen(
                mcp_command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(Path(__file__).resolve().parent)
            )
        else:
            # String command
            process = subprocess.Popen(
                mcp_command,
                shell=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(Path(__file__).resolve().parent)
            )
        
        # Step 1: Send initialization request
        init_request = {
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
        
        print(f"Sending initialization request...")
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        
        # Read initialization response
        init_response = process.stdout.readline()
        if init_response:
            try:
                init_data = json.loads(init_response.strip())
                print(f"Initialization response: {json.dumps(init_data, indent=2)}")
                
                if "error" in init_data:
                    print(f"Initialization failed: {init_data['error']}")
                    process.terminate()
                    return False
                    
            except json.JSONDecodeError as e:
                print(f"Failed to parse initialization response: {e}")
                process.terminate()
                return False
        
        # Step 2: Send tools/list request
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        print(f"Sending tools list request...")
        process.stdin.write(json.dumps(tools_request) + "\n")
        process.stdin.flush()
        
        # Read tools response
        tools_response = process.stdout.readline()
        if tools_response:
            try:
                tools_data = json.loads(tools_response.strip())
                print(f"Tools list response: {json.dumps(tools_data, indent=2)}")
                
                if "error" in tools_data:
                    print(f"Tools list failed: {tools_data['error']}")
                    process.terminate()
                    return False
                    
                # Check if we got tools
                if "result" in tools_data and "tools" in tools_data["result"]:
                    tools_count = len(tools_data["result"]["tools"])
                    print(f"SUCCESS: {server_name} returned {tools_count} tools")
                    process.terminate()
                    return True
                else:
                    print(f"WARNING: {server_name} returned no tools")
                    process.terminate()
                    return False
                    
            except json.JSONDecodeError as e:
                print(f"Failed to parse tools response: {e}")
                process.terminate()
                return False
        
        process.terminate()
        return False
        
    except Exception as e:
        print(f"Error testing {server_name}: {e}")
        try:
            process.terminate()
        except:
            pass
        return False

def test_minimax_search_proper():
    """Test MiniMax Search with proper approach"""
    print(f"\n{'='*60}")
    print("TESTING MINIMAX SEARCH MCP SERVER (Proper)")
    print(f"{'='*60}")
    
    # Try the official GitHub installation approach
    cmd = ["uvx", "--from", "git+https://github.com/MiniMax-AI/minimax_search", "minimax-search"]
    
    return create_mcp_client_test(cmd, "MiniMax Search")

def test_exai_mcp_proper():
    """Test EX-AI MCP with proper protocol"""
    print(f"\n{'='*60}")
    print("TESTING EX-AI MCP SERVER (Proper)")
    print(f"{'='*60}")
    
    project_dir = Path(__file__).resolve().parent
    sys.path.insert(0, str(project_dir))
    
    # Load environment
    from dotenv import load_dotenv
    load_dotenv(project_dir / ".env")
    
    cmd = [
        sys.executable,
        "-u",
        str(project_dir / "scripts" / "runtime" / "run_ws_shim.py")
    ]
    
    return create_mcp_client_test(cmd, "EX-AI MCP")

def main():
    """Main test function"""
    print("MCP Protocol Validation Test")
    print("Testing MCP servers with proper initialization protocol")
    
    # Initialize session tracker
    tracker = get_session_tracker("mcp_validation_2025", str(Path(__file__).resolve().parent))
    tracker.record_operation("mcp_validation_start", "Starting MCP validation test")
    
    results = {}
    
    # Test MiniMax Search
    minimax_success = test_minimax_search_proper()
    results["minimax_search"] = minimax_success
    
    tracker.record_mcp_validation(
        "minimax_search", 
        "success" if minimax_success else "failed",
        {"test_method": "proper_mcp_protocol", "error": "uvx installation issue" if not minimax_success else None}
    )
    
    # Test EX-AI MCP
    exai_success = test_exai_mcp_proper()
    results["exai_mcp"] = exai_success
    
    tracker.record_mcp_validation(
        "exai_mcp",
        "success" if exai_success else "failed", 
        {"test_method": "proper_mcp_protocol"}
    )
    
    # Summary
    print(f"\n{'='*60}")
    print("MCP VALIDATION SUMMARY")
    print(f"{'='*60}")
    
    for server, success in results.items():
        status = "SUCCESS" if success else "FAILED"
        print(f"{server}: {status}")
        
    # Save session data
    tracker.save_session()
    
    if all(results.values()):
        print("\nALL MCP SERVERS WORKING CORRECTLY!")
        return 0
    else:
        print("\nSome MCP servers failed validation")
        return 1

if __name__ == "__main__":
    exit(main())