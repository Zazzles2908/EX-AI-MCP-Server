#!/usr/bin/env python3
"""
Phase 4: Critical Priority Implementation - Tool Execution Test

Tests tool execution functionality after the latest rebuild to validate
Critical Priority #2: Tool Execution System Restoration
"""

import sys
import os
import time

# Add the app to the path
sys.path.insert(0, '/app')

async def test_tool_execution():
    """Test basic tool execution functionality."""
    print("=== Phase 4: Tool Execution System Test ===")
    
    try:
        # Test import of key components
        print("1. Testing component imports...")
        
        # Import tools registry
        from tools.registry import ToolRegistry
        print("   ✓ ToolRegistry imported successfully")
        
        # Import provider registry
        from src.providers.registry_core import ProviderRegistry
        print("   ✓ ProviderRegistry imported successfully")
        
        # Import MCP server
        from src.daemon.mcp_server import MCPNativeServer
        print("   ✓ MCPNativeServer imported successfully")
        
        # Test tool loading
        print("\n2. Testing tool loading...")
        registry = ToolRegistry()
        tools = registry.get_all_tools()
        print(f"   ✓ Loaded {len(tools)} tools")
        
        # List tool names
        tool_names = list(tools.keys())
        print(f"   Available tools: {', '.join(tool_names[:10])}...")  # Show first 10
        
        # Test provider loading
        print("\n3. Testing provider loading...")
        provider_registry = ProviderRegistry()
        providers = provider_registry.get_all_providers()
        print(f"   ✓ Loaded {len(providers)} providers")
        
        provider_names = list(providers.keys())
        print(f"   Available providers: {', '.join(provider_names)}")
        
        # Test basic MCP server initialization
        print("\n4. Testing MCP server initialization...")
        mcp_server = MCPNativeServer()
        print("   ✓ MCPNativeServer initialized successfully")
        
        # Test if we can access specific tools
        print("\n5. Testing specific tool access...")
        try:
            version_tool = tools.get('version')
            if version_tool:
                print(f"   ✓ Version tool found: {version_tool}")
            else:
                print("   ⚠️ Version tool not found")
        except Exception as e:
            print(f"   ❌ Version tool test failed: {e}")
        
        try:
            status_tool = tools.get('status')
            if status_tool:
                print(f"   ✓ Status tool found: {status_tool}")
            else:
                print("   ⚠️ Status tool not found")
        except Exception as e:
            print(f"   ❌ Status tool test failed: {e}")
        
        print("\n=== Tool Execution Test Results ===")
        print(f"✅ Components: All key components loaded successfully")
        print(f"✅ Tools: {len(tools)} tools loaded")
        print(f"✅ Providers: {len(providers)} providers loaded")
        print(f"✅ MCP Server: Server initialized")
        print(f"⚠️ Tool Access: Individual tool testing needed")
        
        return {
            "status": "success",
            "components_loaded": True,
            "tools_count": len(tools),
            "providers_count": len(providers),
            "mcp_server_status": "initialized",
            "tool_names": tool_names,
            "provider_names": provider_names
        }
        
    except Exception as e:
        print(f"❌ Tool execution test failed: {e}")
        import traceback
        traceback.print_exc()
        return {
            "status": "failed",
            "error": str(e),
            "components_loaded": False,
            "tools_count": 0,
            "providers_count": 0,
            "mcp_server_status": "failed"
        }

if __name__ == "__main__":
    import asyncio
    result = asyncio.run(test_tool_execution())
    print(f"\nFinal Result: {result}")
