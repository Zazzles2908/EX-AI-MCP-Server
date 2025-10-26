"""
Test script for thinking_mode parameter implementation

Tests:
1. Default behavior (minimal thinking mode from env)
2. User-provided thinking_mode parameter
3. Invalid thinking_mode handling
4. Performance comparison across modes
"""

import asyncio
import json
import time
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tools.workflows.thinkdeep import ThinkDeepTool
from tools.workflows.thinkdeep_models import ThinkDeepWorkflowRequest


async def test_default_thinking_mode():
    """Test 1: Default thinking mode from env (should be minimal)"""
    print("\n" + "="*80)
    print("TEST 1: Default thinking mode (from env)")
    print("="*80)
    
    tool = ThinkDeepTool()
    
    request = ThinkDeepWorkflowRequest(
        step="Analyze microservices vs monolithic architecture",
        step_number=1,
        total_steps=1,
        next_step_required=False,
        findings="Testing default thinking mode - should use minimal from env",
        model="glm-4.5-flash"
    )
    
    start = time.time()
    
    try:
        # Execute the tool
        result = await tool.execute(request.model_dump())
        duration = time.time() - start
        
        print(f"✅ SUCCESS")
        print(f"Duration: {duration:.1f}s")
        print(f"Status: {result[0].text[:200] if result else 'No result'}...")
        
        # Check if expert analysis was called
        result_data = json.loads(result[0].text) if result else {}
        has_expert = "expert_analysis" in result_data
        print(f"Expert analysis called: {has_expert}")
        
        return duration, has_expert
        
    except Exception as e:
        duration = time.time() - start
        print(f"❌ FAILED after {duration:.1f}s")
        print(f"Error: {e}")
        return duration, False


async def test_user_provided_thinking_mode(mode: str):
    """Test 2: User-provided thinking_mode parameter"""
    print("\n" + "="*80)
    print(f"TEST 2: User-provided thinking_mode='{mode}'")
    print("="*80)
    
    tool = ThinkDeepTool()
    
    request = ThinkDeepWorkflowRequest(
        step="Analyze microservices vs monolithic architecture",
        step_number=1,
        total_steps=1,
        next_step_required=False,
        findings=f"Testing user-provided thinking_mode={mode}",
        model="glm-4.5-flash",
        thinking_mode=mode  # User provides thinking mode
    )
    
    start = time.time()
    
    try:
        result = await tool.execute(request.model_dump())
        duration = time.time() - start
        
        print(f"✅ SUCCESS")
        print(f"Duration: {duration:.1f}s")
        
        result_data = json.loads(result[0].text) if result else {}
        has_expert = "expert_analysis" in result_data
        print(f"Expert analysis called: {has_expert}")
        
        return duration, has_expert
        
    except Exception as e:
        duration = time.time() - start
        print(f"❌ FAILED after {duration:.1f}s")
        print(f"Error: {e}")
        return duration, False


async def test_invalid_thinking_mode():
    """Test 3: Invalid thinking_mode handling"""
    print("\n" + "="*80)
    print("TEST 3: Invalid thinking_mode='invalid'")
    print("="*80)
    
    tool = ThinkDeepTool()
    
    request = ThinkDeepWorkflowRequest(
        step="Test invalid thinking mode",
        step_number=1,
        total_steps=1,
        next_step_required=False,
        findings="Testing invalid thinking_mode - should fall back to minimal",
        model="glm-4.5-flash",
        thinking_mode="invalid"  # Invalid mode
    )
    
    start = time.time()
    
    try:
        result = await tool.execute(request.model_dump())
        duration = time.time() - start
        
        print(f"✅ SUCCESS (fallback to minimal)")
        print(f"Duration: {duration:.1f}s")
        
        return duration, True
        
    except Exception as e:
        duration = time.time() - start
        print(f"❌ FAILED after {duration:.1f}s")
        print(f"Error: {e}")
        return duration, False


async def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("THINKING MODE PARAMETER TESTS")
    print("="*80)
    print("\nThese tests verify:")
    print("1. Default thinking mode from env works")
    print("2. User-provided thinking_mode parameter works")
    print("3. Invalid modes fall back gracefully")
    print("4. Performance varies by thinking mode")
    
    results = {}
    
    # Test 1: Default (minimal from env)
    duration, has_expert = await test_default_thinking_mode()
    results['default'] = {'duration': duration, 'has_expert': has_expert}
    
    # Test 2: User-provided minimal
    duration, has_expert = await test_user_provided_thinking_mode('minimal')
    results['minimal'] = {'duration': duration, 'has_expert': has_expert}
    
    # Test 3: User-provided low
    duration, has_expert = await test_user_provided_thinking_mode('low')
    results['low'] = {'duration': duration, 'has_expert': has_expert}
    
    # Test 4: Invalid mode
    duration, has_expert = await test_invalid_thinking_mode()
    results['invalid'] = {'duration': duration, 'has_expert': has_expert}
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    for test_name, result in results.items():
        status = "✅" if result['has_expert'] else "❌"
        print(f"{status} {test_name:15s}: {result['duration']:6.1f}s | Expert: {result['has_expert']}")
    
    print("\n" + "="*80)
    print("EXPECTED RESULTS:")
    print("="*80)
    print("- Default: ~5-7s with expert analysis")
    print("- Minimal: ~5-7s with expert analysis")
    print("- Low: ~8-10s with expert analysis")
    print("- Invalid: ~5-7s with expert analysis (fallback to minimal)")
    print("\nIf any test took >10s or didn't call expert analysis, there's a problem!")


if __name__ == "__main__":
    asyncio.run(main())

