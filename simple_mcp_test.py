#!/usr/bin/env python3
"""
SIMPLE MCP TEST - No Unicode
"""

import asyncio
import sys
from pathlib import Path

async def test_mcp_system():
    """Simple test of the MCP system."""
    
    print("=" * 60)
    print("EX-AI MCP SERVER - REAL SYSTEM TEST")
    print("=" * 60)
    
    # Change to directory
    exai_dir = Path("C:/Project/EX-AI-MCP-Server")
    if exai_dir.exists():
        import os
        os.chdir(exai_dir)
        print(f"Directory: {os.getcwd()}")
    
    try:
        # Test 1: Import core modules
        print("\n1. Testing core imports...")
        
        from src.daemon.mcp_server import DaemonMCPServer
        from tools.registry import get_tool_registry
        from src.providers.registry_core import get_registry_instance
        
        print("   SUCCESS: Core modules imported")
        
        # Test 2: Create components
        print("\n2. Testing component creation...")
        
        tool_registry = get_tool_registry()
        provider_registry = get_registry_instance()
        server = DaemonMCPServer(tool_registry, provider_registry)
        
        print("   SUCCESS: All components created")
        
        # Test 3: Check tools
        print("\n3. Testing tool registry...")
        
        tools = tool_registry.list_tools()
        print(f"   Tools available: {len(tools)}")
        
        if tools:
            sample_tools = list(tools.keys())[:3]
            print(f"   Sample: {sample_tools}")
        
        # Test 4: Test specific tool
        print("\n4. Testing tool instantiation...")
        
        if "test_echo" in tools:
            try:
                from tools.simple.test_echo import TestEchoTool
                tool = TestEchoTool()
                print("   SUCCESS: TestEchoTool created")
                
                schema = tool.get_tool_schema()
                print(f"   SUCCESS: Schema generated ({len(schema)} props)")
                
            except Exception as e:
                print(f"   ERROR: Tool failed - {e}")
                return False
        else:
            print("   WARNING: test_echo not found")
        
        # Test 5: Docker check
        print("\n5. Testing Docker services...")
        
        import subprocess
        result = subprocess.run([
            "docker-compose", "ps", "exai-mcp-stdio"
        ], capture_output=True, text=True)
        
        if "Up" in result.stdout:
            print("   SUCCESS: exai-mcp-stdio running")
        else:
            print("   WARNING: exai-mcp-stdio not running")
        
        print("\n" + "=" * 60)
        print("RESULT: MCP SYSTEM TEST PASSED")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_mcp_system())
    sys.exit(0 if success else 1)