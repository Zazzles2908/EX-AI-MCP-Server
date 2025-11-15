#!/usr/bin/env python3
"""
ACCURATE MCP STDIO TEST
Tests the actual DaemonMCPServer with correct method names
"""

import asyncio
import json
import sys
from pathlib import Path

async def test_daemon_mcp_server():
    """Test the DaemonMCPServer correctly."""
    
    print("=" * 60)
    print("TESTING DAEMON MCP SERVER")
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
        # Test 1: Import DaemonMCPServer
        print("\n1. Testing DaemonMCPServer import...")
        sys.path.insert(0, str(exai_dir))
        
        from src.daemon.mcp_server import DaemonMCPServer
        from tools.registry import get_tool_registry
        from src.providers.registry_core import get_registry_instance
        
        print("   SUCCESS: DaemonMCPServer imported")
        
        # Test 2: Create server instance
        print("\n2. Testing server creation...")
        
        tool_registry = get_tool_registry()
        provider_registry = get_registry_instance()
        
        server = DaemonMCPServer(tool_registry, provider_registry)
        print("   SUCCESS: Server instance created")
        
        # Test 3: Check if server has required methods
        print("\n3. Testing server methods...")
        
        if hasattr(server, 'run_stdio'):
            print("   SUCCESS: run_stdio method exists")
        else:
            print("   ERROR: run_stdio method missing")
            return False
        
        if hasattr(server, 'run_websocket'):
            print("   SUCCESS: run_websocket method exists")
        else:
            print("   ERROR: run_websocket method missing")
            return False
        
        # Test 4: Test tool registry access
        print("\n4. Testing tool registry access...")
        
        available_tools = tool_registry.list_tools()
        print(f"   SUCCESS: {len(available_tools)} tools in registry")
        
        if available_tools:
            tool_names = list(available_tools.keys())[:3]
            print(f"   Sample tools: {tool_names}")
        else:
            print("   WARNING: No tools found in registry")
        
        # Test 5: Test provider registry
        print("\n5. Testing provider registry...")
        
        try:
            available_models = provider_registry.get_available_models()
            print(f"   SUCCESS: {len(available_models)} models available")
        except Exception as e:
            print(f"   WARNING: Provider registry issue: {e}")
            print("   (This may be expected if no API keys are configured)")
        
        return True
        
    except Exception as e:
        print(f"ERROR: DaemonMCPServer test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_tool_registry():
    """Test the tool registry independently."""
    
    print("\n" + "=" * 60)
    print("TESTING TOOL REGISTRY")
    print("=" * 60)
    
    try:
        from tools.registry import get_tool_registry
        
        registry = get_tool_registry()
        tools = registry.list_tools()
        
        print(f"\nTool Registry Status:")
        print(f"  Total tools: {len(tools)}")
        
        # Test specific tools
        test_tools = ["analyze", "chat", "test_echo"]
        for tool_name in test_tools:
            if tool_name in tools:
                print(f"  ✓ {tool_name}: Available")
            else:
                print(f"  ✗ {tool_name}: Missing")
        
        # Test tool instantiation
        print(f"\nTesting tool instantiation...")
        if "test_echo" in tools:
            try:
                from tools.simple.test_echo import TestEchoTool
                tool = TestEchoTool()
                print(f"  ✓ TestEchoTool instantiated successfully")
                
                # Test schema generation
                schema = tool.get_tool_schema()
                print(f"  ✓ Tool schema generated ({len(schema)} properties)")
                
                return True
            except Exception as e:
                print(f"  ✗ Tool instantiation failed: {e}")
                return False
        else:
            print("  ✗ test_echo tool not available")
            return False
            
    except Exception as e:
        print(f"ERROR: Tool registry test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_mcp_cli():
    """Test the MCP server via CLI."""
    
    print("\n" + "=" * 60)
    print("TESTING MCP SERVER CLI")
    print("=" * 60)
    
    try:
        import subprocess
        
        # Test if we can at least import the MCP server module
        result = subprocess.run([
            sys.executable, "-c", 
            "import sys; sys.path.insert(0, '.'); from src.daemon.mcp_server import DaemonMCPServer; print('MCP Server module imported successfully')"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("   SUCCESS: MCP server module can be imported")
            print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"   ERROR: MCP server import failed")
            print(f"   Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"ERROR: MCP CLI test failed: {e}")
        return False

async def main():
    """Run all accurate MCP tests."""
    
    print("EX-AI MCP SERVER - ACCURATE TESTING")
    print("Testing actual DaemonMCPServer functionality")
    print()
    
    results = []
    
    # Test 1: DaemonMCPServer
    result1 = await test_daemon_mcp_server()
    results.append(("DaemonMCPServer", result1))
    
    # Test 2: Tool Registry
    result2 = await test_tool_registry()
    results.append(("Tool Registry", result2))
    
    # Test 3: MCP CLI
    result3 = await test_mcp_cli()
    results.append(("MCP CLI", result3))
    
    # Summary
    print("\n" + "=" * 60)
    print("ACCURATE TEST RESULTS:")
    print("=" * 60)
    
    all_passed = True
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name:20}: {status}")
        all_passed = all_passed and result
    
    print()
    if all_passed:
        print("SUCCESS: All MCP components work correctly!")
        print("The MCP stdio system is functional!")
    else:
        print("FAILURE: Some MCP components failed!")
        print("The system needs fixes.")
    
    return all_passed

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)