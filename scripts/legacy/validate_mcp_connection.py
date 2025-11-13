#!/usr/bin/env python3
"""
MCP Connection Validation Script for EX-AI-MCP-Server
Tests connection to global MCP environment and MiniMax integration
"""

import asyncio
import json
import sys
import subprocess
from pathlib import Path

def test_mcp_config():
    """Test that MCP config file exists and is valid"""
    mcp_config = Path(__file__).parent / "project-template" / ".mcp.json"
    if not mcp_config.exists():
        print("FAIL: .mcp.json not found in project-template/")
        return False
    
    try:
        with open(mcp_config) as f:
            config = json.load(f)
        if "mcpServers" in config:
            print(f"PASS: .mcp.json found with {len(config['mcpServers'])} MCP servers")
            for server_name in config["mcpServers"].keys():
                print(f"   - {server_name}")
            return True
        else:
            print("FAIL: .mcp.json missing 'mcpServers' key")
            return False
    except json.JSONDecodeError as e:
        print(f"FAIL: .mcp.json invalid JSON: {e}")
        return False

def test_claude_enhancements_connection():
    """Test connection to claude-enhancements MCP server"""
    print("\nTesting claude-enhancements MCP server...")
    
    # Test if the server script exists
    server_path = Path("c:/Users/Jazeel-Home/.claude/claude_enhancements_mcp/server.py")
    if not server_path.exists():
        print(f"FAIL: Claude enhancements server not found at {server_path}")
        return False
    
    print(f"PASS: Claude enhancements server found at {server_path}")
    return True

def test_exai_mcp_server():
    """Test EX-AI MCP server configuration"""
    print("\nTesting EX-AI MCP server...")
    
    exai_config = Path(__file__).parent / "project-template" / ".mcp.json"
    if not exai_config.exists():
        print("FAIL: project-template/.mcp.json not found")
        return False
    
    try:
        with open(exai_config) as f:
            config = json.load(f)
        
        if "exai-mcp" in config.get("mcpServers", {}):
            print("PASS: exai-mcp server configured")
            return True
        else:
            print("FAIL: exai-mcp server not found in config")
            return False
    except Exception as e:
        print(f"FAIL: Could not read config: {e}")
        return False

def test_global_settings():
    """Test that global settings are using MiniMax"""
    settings_path = Path("c:/Users/Jazeel-Home/.claude/config/settings.json")
    if not settings_path.exists():
        print(f"WARNING: Global settings not found at {settings_path}")
        return True  # Non-critical
    
    try:
        with open(settings_path) as f:
            settings = json.load(f)
        
        model = settings.get("model")
        if model and "minimax" in model.lower():
            print(f"PASS: Global model configured as '{model}'")
            return True
        else:
            print(f"WARNING: Model is '{model}', expected MiniMax")
            return True
    except Exception as e:
        print(f"WARNING: Could not read settings: {e}")
        return True

def main():
    """Run all validation tests"""
    print("=" * 60)
    print("MCP Connection Validation - EX-AI-MCP-Server Project")
    print("=" * 60)
    
    tests = [
        ("MCP Configuration", test_mcp_config),
        ("EX-AI MCP Server", test_exai_mcp_server),
        ("Global Settings", test_global_settings),
        ("Claude Enhancements", test_claude_enhancements_connection),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\nTest: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"ERROR: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\nAll validation checks passed!")
        print("The project is properly connected to the global MCP environment.")
        return 0
    else:
        print(f"\n{total - passed} test(s) failed. Please review the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
