#!/usr/bin/env python3
"""Comprehensive MCP Function Testing Script"""

import asyncio
import websockets
import json
import os
from datetime import datetime
from dotenv import load_dotenv

class MCPFunctionTester:
    def __init__(self):
        self.host = "127.0.0.1"
        self.port = "3010"
        self.token = os.getenv("EXAI_WS_TOKEN", "")
        self.websocket = None
        self.test_results = []
        
    async def connect(self):
        """Connect to EXAI MCP Server"""
        uri = f"ws://{self.host}:{self.port}"
        print(f"Connecting to {uri}...")
        
        try:
            self.websocket = await websockets.connect(uri)
            print("✓ Connected successfully")
            
            # Send hello message
            hello_msg = {
                "op": "hello",
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "mcp-function-tester", "version": "1.0.0"},
                "token": self.token
            }
            
            await self.websocket.send(json.dumps(hello_msg))
            response = await asyncio.wait_for(self.websocket.recv(), timeout=10)
            data = json.loads(response)
            
            if data.get("ok"):
                print("✓ Authentication successful")
                return True
            else:
                print(f"✗ Authentication failed: {data.get('error')}")
                return False
                
        except Exception as e:
            print(f"✗ Connection failed: {e}")
            return False
    
    async def call_tool(self, tool_name, arguments=None):
        """Call an MCP tool"""
        if not self.websocket:
            return None
            
        try:
            # Send call_tool request
            call_msg = {
                "op": "call_tool",
                "id": f"test_{tool_name}_{int(datetime.now().timestamp())}",
                "name": tool_name,
                "arguments": arguments or {}
            }
            
            await self.websocket.send(json.dumps(call_msg))
            
            # Wait for response (longer timeout for AI calls)
            response = await asyncio.wait_for(self.websocket.recv(), timeout=60)
            data = json.loads(response)
            
            # Extract result from response
            result = data.get("outputs", data.get("result", []))
            return {
                "success": True,
                "result": result,
                "raw_response": data
            }
            
        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": "Timeout",
                "result": []
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "result": []
            }
    
    async def test_chat_tool(self):
        """Test the chat tool with a simple question"""
        print("\n=== Testing chat tool ===")
        arguments = {
            "prompt": "Hello! Please respond with a brief greeting to confirm the EX-AI MCP system is working properly.",
            "model": "auto"
        }
        
        result = await self.call_tool("chat", arguments)
        if result["success"]:
            print("✓ chat tool responded successfully")
            if result["result"] and len(result["result"]) > 0:
                content = result["result"][0].get("text", "")
                print(f"  Response: {content[:200]}...")
                return True
        print("✗ chat tool failed")
        return False
    
    async def test_listmodels_tool(self):
        """Test the listmodels tool"""
        print("\n=== Testing listmodels tool ===")
        result = await self.call_tool("listmodels", {})
        
        if result["success"]:
            print("✓ listmodels tool responded successfully")
            if result["result"] and len(result["result"]) > 0:
                content = result["result"][0].get("text", "")
                print(f"  Available models listed: {content[:300]}...")
                return True
        print("✗ listmodels tool failed")
        return False
    
    async def test_version_tool(self):
        """Test the version tool"""
        print("\n=== Testing version tool ===")
        result = await self.call_tool("version", {})
        
        if result["success"]:
            print("✓ version tool responded successfully")
            if result["result"] and len(result["result"]) > 0:
                content = result["result"][0].get("text", "")
                print(f"  Version info: {content[:200]}...")
                return True
        print("✗ version tool failed")
        return False
    
    async def test_status_tool(self):
        """Test the status tool"""
        print("\n=== Testing status tool ===")
        arguments = {
            "tail_lines": 10,
            "include_tools": False
        }
        
        result = await self.call_tool("status", arguments)
        if result["success"]:
            print("✓ status tool responded successfully")
            if result["result"] and len(result["result"]) > 0:
                content = result["result"][0].get("text", "")
                print(f"  Status: {content[:200]}...")
                return True
        print("✗ status tool failed")
        return False
    
    async def test_analyze_tool(self):
        """Test the analyze tool"""
        print("\n=== Testing analyze tool ===")
        arguments = {
            "step": "Starting analysis of EX-AI MCP system status",
            "step_number": 1,
            "total_steps": 1,
            "next_step_required": False,
            "findings": "EX-AI MCP system is operational with 30 tools available. All core components are functioning correctly.",
            "model": "auto"
        }
        
        result = await self.call_tool("analyze", arguments)
        if result["success"]:
            print("✓ analyze tool responded successfully")
            if result["result"] and len(result["result"]) > 0:
                content = result["result"][0].get("text", "")
                print(f"  Analysis: {content[:300]}...")
                return True
        print("✗ analyze tool failed")
        return False
    
    async def test_planner_tool(self):
        """Test the planner tool"""
        print("\n=== Testing planner tool ===")
        arguments = {
            "step": "Plan to validate EX-AI MCP system functionality",
            "step_number": 1,
            "total_steps": 1,
            "next_step_required": False,
            "model": "auto"
        }
        
        result = await self.call_tool("planner", arguments)
        if result["success"]:
            print("✓ planner tool responded successfully")
            if result["result"] and len(result["result"]) > 0:
                content = result["result"][0].get("text", "")
                print(f"  Plan: {content[:300]}...")
                return True
        print("✗ planner tool failed")
        return False
    
    async def test_debug_tool(self):
        """Test the debug tool"""
        print("\n=== Testing debug tool ===")
        arguments = {
            "step": "Debug session to verify EX-AI MCP system debugging capabilities",
            "step_number": 1,
            "total_steps": 1,
            "next_step_required": False,
            "findings": "System debugging tools are functioning correctly. No issues found in current session.",
            "hypothesis": "EX-AI MCP debug tool is working as expected",
            "model": "auto"
        }
        
        result = await self.call_tool("debug", arguments)
        if result["success"]:
            print("✓ debug tool responded successfully")
            if result["result"] and len(result["result"]) > 0:
                content = result["result"][0].get("text", "")
                print(f"  Debug analysis: {content[:300]}...")
                return True
        print("✗ debug tool failed")
        return False
    
    async def test_refactor_tool(self):
        """Test the refactor tool"""
        print("\n=== Testing refactor tool ===")
        arguments = {
            "step": "Analyze codebase for refactoring opportunities in EX-AI MCP system",
            "step_number": 1,
            "total_steps": 1,
            "next_step_required": False,
            "findings": "System architecture is well-designed. Minor optimizations possible in session management.",
            "refactor_type": "codesmells",
            "model": "auto"
        }
        
        result = await self.call_tool("refactor", arguments)
        if result["success"]:
            print("✓ refactor tool responded successfully")
            if result["result"] and len(result["result"]) > 0:
                content = result["result"][0].get("text", "")
                print(f"  Refactor analysis: {content[:300]}...")
                return True
        print("✗ refactor tool failed")
        return False
    
    async def test_all_functions(self):
        """Test all available MCP functions"""
        print("Starting comprehensive MCP function testing...")
        
        # Test basic functions first
        basic_tests = [
            ("chat", self.test_chat_tool),
            ("listmodels", self.test_listmodels_tool),
            ("version", self.test_version_tool),
            ("status", self.test_status_tool)
        ]
        
        # Test analysis functions
        analysis_tests = [
            ("analyze", self.test_analyze_tool),
            ("planner", self.test_planner_tool),
            ("debug", self.test_debug_tool),
            ("refactor", self.test_refactor_tool)
        ]
        
        all_tests = basic_tests + analysis_tests
        
        results = {}
        for test_name, test_func in all_tests:
            try:
                results[test_name] = await test_func()
            except Exception as e:
                print(f"✗ {test_name} tool test failed with exception: {e}")
                results[test_name] = False
        
        # Summary
        print("\n" + "="*60)
        print("MCP FUNCTION TESTING SUMMARY")
        print("="*60)
        
        passed = sum(1 for v in results.values() if v)
        total = len(results)
        
        for test_name, result in results.items():
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"{test_name:20} {status}")
        
        print(f"\nTotal: {passed}/{total} tests passed")
        
        return results
    
    async def close(self):
        """Close the connection"""
        if self.websocket:
            await self.websocket.close()

async def main():
    """Main testing function"""
    # Load environment
    load_dotenv('.env')
    
    # Create tester
    tester = MCPFunctionTester()
    
    try:
        # Connect
        if await tester.connect():
            # Run all tests
            results = await tester.test_all_functions()
            
            # Save results to file
            with open('mcp_function_test_results.json', 'w') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'results': results,
                    'summary': {
                        'passed': sum(1 for v in results.values() if v),
                        'total': len(results),
                        'success_rate': sum(1 for v in results.values() if v) / len(results) * 100
                    }
                }, f, indent=2)
            
            print(f"\nTest results saved to: mcp_function_test_results.json")
            
        else:
            print("Failed to connect to EXAI MCP Server")
            return 1
            
    except Exception as e:
        print(f"Testing failed: {e}")
        return 1
    finally:
        await tester.close()
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)