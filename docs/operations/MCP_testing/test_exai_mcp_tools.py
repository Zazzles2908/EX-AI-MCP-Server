#!/usr/bin/env python3
"""
Comprehensive MCP Testing Script
Tests all EXAI MCP tools through direct WebSocket calls
"""
import asyncio
import websockets
import json
import sys
from datetime import datetime

class MCPTester:
    def __init__(self):
        self.ws_url = "ws://127.0.0.1:3010"
        self.token = "pYf69sHNkOYlYLRTJfMrxCQghO5OJOUFbUxqaxp9Zxo"
        self.results = []
        
    async def connect(self):
        """Establish WebSocket connection"""
        self.ws = await websockets.connect(self.ws_url)
        await self.ws.send(json.dumps({
            'op': 'hello',
            'token': self.token
        }))
        resp = await asyncio.wait_for(self.ws.recv(), timeout=10)
        result = json.loads(resp)
        if result.get('ok'):
            self.session_id = result.get('session_id')
            print(f"[OK] Connected with session: {self.session_id}")
            return True
        return False
        
    async def test_tool(self, tool_name, arguments, description):
        """Test a specific tool"""
        print(f"\nTesting: {tool_name}")
        print(f"Description: {description}")
        print(f"Arguments: {json.dumps(arguments, indent=2)}")
        
        try:
            request_id = f"test-{tool_name}-{int(datetime.now().timestamp())}"
            await self.ws.send(json.dumps({
                'op': 'call_tool',
                'request_id': request_id,
                'name': tool_name,
                'arguments': arguments
            }))
            
            # Wait for response with longer timeout
            resp = await asyncio.wait_for(self.ws.recv(), timeout=30)
            result = json.loads(resp)
            
            if result.get('ok'):
                print(f"[SUCCESS] {tool_name} executed successfully")
                content = result.get('result', [])
                if content and len(content) > 0:
                    text_content = content[0].get('content', [{}])[0].get('text', '')
                    print(f"Response preview: {text_content[:200]}...")
                self.results.append({
                    'tool': tool_name,
                    'status': 'SUCCESS',
                    'description': description,
                    'response': result
                })
                return True
            else:
                error = result.get('error', {})
                print(f"[FAILED] {tool_name} failed: {error}")
                self.results.append({
                    'tool': tool_name,
                    'status': 'FAILED',
                    'description': description,
                    'error': error
                })
                return False
                
        except asyncio.TimeoutError:
            print(f"[TIMEOUT] {tool_name} timed out after 30 seconds")
            self.results.append({
                'tool': tool_name,
                'status': 'TIMEOUT',
                'description': description,
                'error': 'Operation timed out'
            })
            return False
        except Exception as e:
            print(f"[ERROR] {tool_name} error: {e}")
            self.results.append({
                'tool': tool_name,
                'status': 'ERROR',
                'description': description,
                'error': str(e)
            })
            return False
    
    async def list_tools(self):
        """List all available tools"""
        try:
            await self.ws.send(json.dumps({
                'op': 'list_tools',
                'request_id': 'list-tools'
            }))
            resp = await asyncio.wait_for(self.ws.recv(), timeout=10)
            result = json.loads(resp)
            tools = result.get('tools', [])
            print(f"\n[INFO] Available tools: {len(tools)}")
            for tool in tools:
                print(f"  - {tool.get('name')}: {tool.get('description', 'No description')[:60]}...")
            return tools
        except Exception as e:
            print(f"[ERROR] Failed to list tools: {e}")
            return []
    
    async def run_all_tests(self):
        """Run all MCP tool tests"""
        print("=" * 80)
        print("EXAI MCP TOOLS COMPREHENSIVE TEST")
        print("=" * 80)
        print(f"Started at: {datetime.now()}")
        
        # Connect
        if not await self.connect():
            print("[FATAL] Failed to connect to WebSocket")
            return False
            
        # List tools first
        tools = await self.list_tools()
        
        # Test each tool
        tests = [
            {
                'tool': 'glm_payload_preview',
                'description': 'Preview GLM API payload',
                'args': {
                    'prompt': 'What is the capital of France?',
                    'model': 'glm-4.5-flash',
                    'temperature': 0.3
                }
            },
            {
                'tool': 'status',
                'description': 'Get system status',
                'args': {
                    'doctor': False
                }
            }
        ]
        
        for test in tests:
            await self.test_tool(test['tool'], test['args'], test['description'])
            
        await self.ws.close()
        return True
    
    def save_report(self):
        """Save test results to file"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total': len(self.results),
                'success': len([r for r in self.results if r['status'] == 'SUCCESS']),
                'failed': len([r for r in self.results if r['status'] == 'FAILED']),
                'timeout': len([r for r in self.results if r['status'] == 'TIMEOUT']),
                'error': len([r for r in self.results if r['status'] == 'ERROR'])
            },
            'results': self.results
        }
        
        with open('documents/MCP_testing/reports/exai_mcp_test_report.json', 'w') as f:
            json.dump(report, f, indent=2)
            
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"Total tests: {report['summary']['total']}")
        print(f"Success: {report['summary']['success']}")
        print(f"Failed: {report['summary']['failed']}")
        print(f"Timeout: {report['summary']['timeout']}")
        print(f"Error: {report['summary']['error']}")
        print("=" * 80)
        print(f"\nReport saved to: documents/MCP_testing/reports/exai_mcp_test_report.json")
        
        return report

async def main():
    tester = MCPTester()
    if await tester.run_all_tests():
        tester.save_report()
        return 0
    return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
