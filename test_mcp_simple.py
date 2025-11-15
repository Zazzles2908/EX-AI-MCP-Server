#!/usr/bin/env python3
"""
Simple MCP Test - Focus on EX-AI MCP validation
"""

import json
import subprocess
import sys
from pathlib import Path

# Add session tracking
sys.path.append(str(Path(__file__).resolve().parent))
from session_memory_tracker import get_session_tracker

def test_exai_mcp_direct():
    """Test EX-AI MCP server directly"""
    print("Testing EX-AI MCP Server Direct")
    print("="*50)
    
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
    
    try:
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(project_dir)
        )
        
        # Send initialization
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
        
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        
        # Wait a moment for initialization
        import time
        time.sleep(2)
        
        # Send tools/list request
        tools_request = {
            "jsonrpc": "2.0", 
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        process.stdin.write(json.dumps(tools_request) + "\n")
        process.stdin.flush()
        
        # Read response
        import time
        time.sleep(3)
        
        try:
            # Read all available output
            stdout, stderr = process.communicate(timeout=5)
            
            print("STDOUT:")
            print(stdout)
            print("\nSTDERR:")
            print(stderr)
            
            # Check if we got tools in stdout
            lines = stdout.strip().split('\n')
            for line in lines:
                if line.strip():
                    try:
                        data = json.loads(line)
                        if "result" in data and "tools" in data["result"]:
                            tools = data["result"]["tools"]
                            print(f"\nSUCCESS: EX-AI MCP returned {len(tools)} tools")
                            for tool in tools[:3]:  # Show first 3 tools
                                print(f"  - {tool.get('name', 'Unknown')}: {tool.get('description', '')[:100]}...")
                            process.terminate()
                            return True
                    except json.JSONDecodeError:
                        continue
                        
            print("\nNo tools found in response")
            process.terminate()
            return False
            
        except subprocess.TimeoutExpired:
            print("Process timed out")
            process.kill()
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        try:
            process.terminate()
        except:
            pass
        return False

def test_minimax_search_simple():
    """Test MiniMax Search installation"""
    print("Testing MiniMax Search Installation")
    print("="*50)
    
    try:
        # Test if uvx can install the package
        result = subprocess.run(
            ["uvx", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            print("uvx not available")
            return False
            
        print("uvx available, trying installation...")
        
        # Try to check if the package can be installed
        result = subprocess.run(
            ["uvx", "--from", "git+https://github.com/MiniMax-AI/minimax_search", "--help"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(f"Installation result: {result.returncode}")
        if result.stderr:
            print(f"Error: {result.stderr}")
            
        return result.returncode == 0
        
    except Exception as e:
        print(f"Error testing MiniMax Search: {e}")
        return False

def main():
    """Main test function"""
    tracker = get_session_tracker('mcp_validation_simple', str(Path(__file__).resolve().parent))
    
    print("MCP Server Validation - Simple Test")
    print("="*60)
    
    # Test EX-AI MCP
    exai_success = test_exai_mcp_direct()
    tracker.record_mcp_validation(
        "exai_mcp",
        "success" if exai_success else "failed",
        {"test_method": "direct_subprocess"}
    )
    
    # Test MiniMax Search installation
    minimax_success = test_minimax_search_simple()
    tracker.record_mcp_validation(
        "minimax_search",
        "success" if minimax_success else "failed", 
        {"test_method": "installation_test"}
    )
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"EX-AI MCP Server: {'SUCCESS' if exai_success else 'FAILED'}")
    print(f"MiniMax Search: {'SUCCESS' if minimax_success else 'FAILED'}")
    
    tracker.save_session()
    
    return 0 if all([exai_success, minimax_success]) else 1

if __name__ == "__main__":
    exit(main())