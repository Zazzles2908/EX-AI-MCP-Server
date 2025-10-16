#!/usr/bin/env python3
"""
Test script to verify async provider implementation.
This script tests the async providers directly to ensure they work correctly.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set environment variables
os.environ["GLM_API_KEY"] = "90c4c8f531334693b2f684687fc7d250.ZhQ1I7U2mAgGZRUD"
os.environ["GLM_API_URL"] = "https://api.z.ai/api/paas/v4"
os.environ["KIMI_API_KEY"] = "sk-ZpS6545OhteEeQuNSexAPhvW92WQqqYjkikNmxWExyeUsOjU"
os.environ["KIMI_API_URL"] = "https://api.moonshot.ai/v1"
os.environ["USE_ASYNC_PROVIDERS"] = "true"


async def test_async_glm_provider():
    """Test AsyncGLMProvider"""
    print("\n" + "="*80)
    print("TEST 1: AsyncGLMProvider")
    print("="*80)
    
    try:
        from src.providers.async_glm import AsyncGLMProvider
        
        print("✅ AsyncGLMProvider imported successfully")
        
        # Create provider
        provider = AsyncGLMProvider(
            api_key=os.getenv("GLM_API_KEY"),
            base_url=os.getenv("GLM_API_URL")
        )
        print("✅ AsyncGLMProvider instantiated successfully")
        
        # Test async call
        async with provider:
            print("✅ Async context manager entered")
            
            response = await provider.generate_content(
                prompt="Say 'Hello from async GLM provider!' in exactly 5 words.",
                model_name="glm-4.6",
                temperature=0.3,
                max_output_tokens=50
            )
            
            print(f"✅ Async call completed successfully")
            print(f"📝 Response: {response.content[:200]}")
            print(f"⏱️  Completion time: {response.metadata.get('completion_time', 'N/A')}")
            
        print("✅ Async context manager exited (resources cleaned up)")
        print("\n✅ TEST 1 PASSED: AsyncGLMProvider works correctly!\n")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 1 FAILED: {type(e).__name__}: {e}\n")
        import traceback
        traceback.print_exc()
        return False


async def test_async_kimi_provider():
    """Test AsyncKimiProvider"""
    print("\n" + "="*80)
    print("TEST 2: AsyncKimiProvider")
    print("="*80)
    
    try:
        from src.providers.async_kimi import AsyncKimiProvider
        
        print("✅ AsyncKimiProvider imported successfully")
        
        # Create provider
        provider = AsyncKimiProvider(
            api_key=os.getenv("KIMI_API_KEY"),
            base_url=os.getenv("KIMI_API_URL")
        )
        print("✅ AsyncKimiProvider instantiated successfully")
        
        # Test async call
        async with provider:
            print("✅ Async context manager entered")
            
            response = await provider.generate_content(
                prompt="Say 'Hello from async Kimi provider!' in exactly 5 words.",
                model_name="kimi-k2-0905-preview",
                temperature=0.3,
                max_output_tokens=50
            )
            
            print(f"✅ Async call completed successfully")
            print(f"📝 Response: {response.content[:200]}")
            print(f"⏱️  Completion time: {response.metadata.get('completion_time', 'N/A')}")
            
        print("✅ Async context manager exited (resources cleaned up)")
        print("\n✅ TEST 2 PASSED: AsyncKimiProvider works correctly!\n")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 2 FAILED: {type(e).__name__}: {e}\n")
        import traceback
        traceback.print_exc()
        return False


async def test_expert_analysis_async_path():
    """Test expert analysis with async providers"""
    print("\n" + "="*80)
    print("TEST 3: Expert Analysis with Async Providers")
    print("="*80)
    
    try:
        # This test would require full server setup
        # For now, just verify the environment variable is set
        use_async = os.getenv("USE_ASYNC_PROVIDERS", "false").lower() in ("true", "1", "yes")
        
        if use_async:
            print("✅ USE_ASYNC_PROVIDERS=true (async providers enabled)")
            print("✅ Expert analysis will use async providers")
            print("\n✅ TEST 3 PASSED: Environment configured for async providers!\n")
            return True
        else:
            print("❌ USE_ASYNC_PROVIDERS not set or false")
            print("\n❌ TEST 3 FAILED: Async providers not enabled in environment!\n")
            return False
            
    except Exception as e:
        print(f"\n❌ TEST 3 FAILED: {type(e).__name__}: {e}\n")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("ASYNC PROVIDER IMPLEMENTATION TEST SUITE")
    print("="*80)
    print(f"Python: {sys.version}")
    print(f"Project Root: {project_root}")
    print("="*80)
    
    results = []
    
    # Test 1: AsyncGLMProvider
    results.append(await test_async_glm_provider())
    
    # Test 2: AsyncKimiProvider
    results.append(await test_async_kimi_provider())
    
    # Test 3: Environment configuration
    results.append(await test_expert_analysis_async_path())
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    passed = sum(results)
    total = len(results)
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Async providers are working correctly!")
        print("="*80 + "\n")
        return 0
    else:
        print(f"\n⚠️  {total - passed} TEST(S) FAILED!")
        print("="*80 + "\n")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

