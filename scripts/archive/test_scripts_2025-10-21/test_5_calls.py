"""
Test 5 different MCP tool calls and record results

This script makes 5 different calls to test the thinking_mode implementation:
1. Chat tool (baseline - no expert analysis)
2. Thinkdeep with default thinking_mode (minimal from env)
3. Thinkdeep with user-provided thinking_mode=low
4. Thinkdeep with user-provided thinking_mode=high
5. Debug tool with thinking_mode=minimal
"""

import asyncio
import json
import time
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import MCP client
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def call_tool(session, tool_name: str, arguments: dict) -> tuple[float, dict]:
    """Call a tool and return duration and result"""
    start = time.time()
    
    try:
        result = await session.call_tool(tool_name, arguments)
        duration = time.time() - start
        
        # Parse result
        if result and hasattr(result, 'content'):
            content = result.content[0].text if result.content else "{}"
            result_data = json.loads(content) if content else {}
        else:
            result_data = {"error": "No result"}
        
        return duration, result_data
        
    except Exception as e:
        duration = time.time() - start
        return duration, {"error": str(e)}


async def main():
    """Run 5 test calls"""
    
    print("\n" + "="*80)
    print("TESTING 5 MCP TOOL CALLS")
    print("="*80)
    print("\nStarting MCP client session...")
    
    # Start MCP server
    server_params = StdioServerParameters(
        command="python",
        args=["server.py"],
        env=None
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            
            await session.initialize()
            print("✅ MCP session initialized\n")
            
            # TEST 1: Chat tool (baseline)
            print("="*80)
            print("TEST 1: Chat tool (baseline - no expert analysis)")
            print("="*80)
            
            duration, result = await call_tool(
                session,
                "chat",
                {
                    "prompt": "Say 'Hello from Test 1' in exactly 5 words.",
                    "model": "glm-4.5-flash"
                }
            )
            
            print(f"Duration: {duration:.2f}s")
            print(f"Result: {str(result)[:200]}...")
            print(f"Has error: {'error' in result}")
            print()
            
            # TEST 2: Thinkdeep with default thinking_mode
            print("="*80)
            print("TEST 2: Thinkdeep with DEFAULT thinking_mode (minimal from env)")
            print("="*80)
            
            duration, result = await call_tool(
                session,
                "thinkdeep",
                {
                    "step": "Analyze the trade-offs between REST and GraphQL APIs",
                    "step_number": 1,
                    "total_steps": 1,
                    "next_step_required": False,
                    "findings": "Testing default thinking_mode - should use minimal from env",
                    "model": "glm-4.5-flash"
                    # No thinking_mode specified - should use minimal from env
                }
            )
            
            print(f"Duration: {duration:.2f}s")
            print(f"Expected: ~5-7s (minimal mode)")
            print(f"Has expert_analysis: {'expert_analysis' in str(result)}")
            print(f"Has error: {'error' in result}")
            print()
            
            # TEST 3: Thinkdeep with thinking_mode=low
            print("="*80)
            print("TEST 3: Thinkdeep with USER-PROVIDED thinking_mode=low")
            print("="*80)
            
            duration, result = await call_tool(
                session,
                "thinkdeep",
                {
                    "step": "Analyze the trade-offs between microservices and monolithic architecture",
                    "step_number": 1,
                    "total_steps": 1,
                    "next_step_required": False,
                    "findings": "Testing user-provided thinking_mode=low",
                    "model": "glm-4.5-flash",
                    "thinking_mode": "low"  # User provides thinking mode
                }
            )
            
            print(f"Duration: {duration:.2f}s")
            print(f"Expected: ~8-10s (low mode)")
            print(f"Has expert_analysis: {'expert_analysis' in str(result)}")
            print(f"Has error: {'error' in result}")
            print()
            
            # TEST 4: Thinkdeep with thinking_mode=high
            print("="*80)
            print("TEST 4: Thinkdeep with USER-PROVIDED thinking_mode=high")
            print("="*80)
            
            duration, result = await call_tool(
                session,
                "thinkdeep",
                {
                    "step": "Deep analysis: Should we use event sourcing for a financial trading system?",
                    "step_number": 1,
                    "total_steps": 1,
                    "next_step_required": False,
                    "findings": "Testing user-provided thinking_mode=high for deep analysis",
                    "model": "glm-4.5-flash",
                    "thinking_mode": "high"  # User requests deep analysis
                }
            )
            
            print(f"Duration: {duration:.2f}s")
            print(f"Expected: ~25-30s (high mode)")
            print(f"Has expert_analysis: {'expert_analysis' in str(result)}")
            print(f"Has error: {'error' in result}")
            print()
            
            # TEST 5: Debug tool with thinking_mode=minimal
            print("="*80)
            print("TEST 5: Debug tool with thinking_mode=minimal")
            print("="*80)
            
            duration, result = await call_tool(
                session,
                "debug",
                {
                    "step": "Debug why a function returns None unexpectedly",
                    "step_number": 1,
                    "total_steps": 1,
                    "next_step_required": False,
                    "findings": "Testing debug tool with minimal thinking mode",
                    "hypothesis": "Function is missing return statement",
                    "model": "glm-4.5-flash",
                    "thinking_mode": "minimal",
                    "confidence": "medium"
                }
            )
            
            print(f"Duration: {duration:.2f}s")
            print(f"Expected: ~5-7s (minimal mode)")
            print(f"Has expert_analysis: {'expert_analysis' in str(result)}")
            print(f"Has error: {'error' in result}")
            print()
            
            # SUMMARY
            print("="*80)
            print("TEST SUMMARY")
            print("="*80)
            print("\nAll 5 tests completed!")
            print("\nExpected results:")
            print("- Test 1 (chat): Fast (<5s), no expert analysis")
            print("- Test 2 (thinkdeep default): ~5-7s with expert analysis")
            print("- Test 3 (thinkdeep low): ~8-10s with expert analysis")
            print("- Test 4 (thinkdeep high): ~25-30s with expert analysis")
            print("- Test 5 (debug minimal): ~5-7s with expert analysis")


if __name__ == "__main__":
    asyncio.run(main())

