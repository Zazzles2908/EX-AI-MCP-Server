#!/usr/bin/env python3
"""
Test MCP Connection - Validates that the EX-AI MCP Server is working properly
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path

def test_mcp_server_direct():
    """Test the MCP server directly via subprocess"""
    print("=" * 60)
    print("TESTING EX-AI MCP SERVER DIRECTLY")
    print("=" * 60)
    
    # Change to project directory
    project_dir = Path(__file__).resolve().parent
    sys.path.insert(0, str(project_dir))
    
    # Load environment
    from dotenv import load_dotenv
    load_dotenv(project_dir / ".env")
    
    try:
        # Test the MCP shim directly
        cmd = [
            sys.executable,
            "-u", 
            str(project_dir / "scripts" / "runtime" / "run_ws_shim.py")
        ]
        
        print(f"Running command: {' '.join(cmd)}")
        
        # Send MCP request
        mcp_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }
        
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(project_dir)
        )
        
        # Send request and get response
        try:
            stdout, stderr = process.communicate(
                input=json.dumps(mcp_request) + "\n",
                timeout=30
            )
            
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            print(f"Return code: {process.returncode}")
            
            if stdout:
                try:
                    response = json.loads(stdout.strip())
                    print(f"Parsed response: {json.dumps(response, indent=2)}")
                    return True
                except json.JSONDecodeError:
                    print("Could not parse JSON response")
                    return False
            
        except subprocess.TimeoutExpired:
            print("Request timed out")
            process.kill()
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_minimax_search():
    """Test MiniMax Search MCP server"""
    print("=" * 60)
    print("TESTING MINIMAX SEARCH MCP SERVER")
    print("=" * 60)
    
    # Test with uvx
    cmd = [
        "uvx",
        "--from",
        "git+https://github.com/MiniMax-AI/minimax_search",
        "minimax-search"
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    
    process = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=dict( MINIAGENT_API_KEY = "test-key" )
    )
    
    try:
        # Send tools list request
        mcp_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }
        
        stdout, stderr = process.communicate(
            input=json.dumps(mcp_request) + "\n",
            timeout=15
        )
        
        print(f"STDOUT: {stdout}")
        print(f"STDERR: {stderr}")
        print(f"Return code: {process.returncode}")
        
        if process.returncode == 0 and stdout:
            try:
                response = json.loads(stdout.strip())
                print(f"MiniMax Search tools: {json.dumps(response, indent=2)}")
                return True
            except json.JSONDecodeError:
                print("Could not parse MiniMax Search response")
                return False
                
    except subprocess.TimeoutExpired:
        print("MiniMax Search timed out")
        process.kill()
        return False
    except Exception as e:
        print(f"MiniMax Search error: {e}")
        return False

if __name__ == "__main__":
    print("EX-AI MCP Server Validation Test")
    print("=" * 60)
    
    # Test MiniMax Search first (should be faster)
    minimax_success = test_minimax_search()
    
    print("\n")
    
    # Test EX-AI MCP server
    exai_success = test_mcp_server_direct()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"MiniMax Search MCP: {'SUCCESS' if minimax_success else 'FAILED'}")
    print(f"EX-AI MCP Server: {'SUCCESS' if exai_success else 'FAILED'}")
    
    if minimax_success and exai_success:
        print("\nALL MCP SERVERS WORKING!")
    else:
        print("\nSome MCP servers failed to connect")