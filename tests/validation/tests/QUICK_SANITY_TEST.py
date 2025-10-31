"""
Quick Sanity Test - Verify APIs are working

This script makes simple API calls to both Kimi and GLM to verify
the configuration is correct and APIs are responding.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment
from dotenv import load_dotenv
load_dotenv("tool_validation_suite/.env.testing")
load_dotenv(".env.testing")
load_dotenv(".env")

from openai import OpenAI

def test_kimi():
    """Test Kimi API"""
    print("\n=== Testing Kimi API ===")
    try:
        client = OpenAI(
            api_key=os.getenv("KIMI_API_KEY"),
            base_url=os.getenv("KIMI_BASE_URL", "https://api.moonshot.ai/v1")
        )
        
        response = client.chat.completions.create(
            model="kimi-k2-0905-preview",
            messages=[{"role": "user", "content": "Say 'Kimi works' in 3 words"}],
            temperature=0.0
        )
        
        result = response.choices[0].message.content
        print(f"✅ Kimi API WORKS!")
        print(f"   Response: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Kimi API FAILED: {str(e)[:200]}")
        return False


def test_glm():
    """Test GLM API"""
    print("\n=== Testing GLM API ===")
    try:
        client = OpenAI(
            api_key=os.getenv("GLM_API_KEY"),
            base_url=os.getenv("GLM_BASE_URL", "https://api.z.ai/api/paas/v4")
        )
        
        response = client.chat.completions.create(
            model="glm-4.5-flash",
            messages=[{"role": "user", "content": "Say 'GLM works' in 3 words"}],
            temperature=0.0
        )
        
        result = response.choices[0].message.content
        print(f"✅ GLM API WORKS!")
        print(f"   Response: {result}")
        return True
        
    except Exception as e:
        print(f"❌ GLM API FAILED: {str(e)[:200]}")
        return False


def test_glm_watcher():
    """Test GLM Watcher API"""
    print("\n=== Testing GLM Watcher API ===")
    
    if os.getenv("GLM_WATCHER_ENABLED", "false").lower() != "true":
        print("⏭️  GLM Watcher is disabled")
        return True
    
    try:
        client = OpenAI(
            api_key=os.getenv("GLM_WATCHER_KEY"),
            base_url=os.getenv("GLM_WATCHER_BASE_URL", "https://open.bigmodel.cn/api/paas/v4")
        )
        
        response = client.chat.completions.create(
            model=os.getenv("GLM_WATCHER_MODEL", "glm-4.5-flash"),
            messages=[{"role": "user", "content": "Say 'Watcher works' in 3 words"}],
            temperature=0.0,
            timeout=10
        )
        
        result = response.choices[0].message.content
        print(f"✅ GLM Watcher API WORKS!")
        print(f"   Response: {result}")
        return True
        
    except Exception as e:
        print(f"❌ GLM Watcher API FAILED: {str(e)[:200]}")
        return False


if __name__ == "__main__":
    print("\n" + "="*60)
    print("  QUICK SANITY TEST - API VALIDATION")
    print("="*60)
    
    # Show configuration
    print("\nConfiguration:")
    print(f"  KIMI_API_KEY: {'✅ Set' if os.getenv('KIMI_API_KEY') else '❌ Missing'}")
    print(f"  KIMI_BASE_URL: {os.getenv('KIMI_BASE_URL', 'NOT SET')}")
    print(f"  GLM_API_KEY: {'✅ Set' if os.getenv('GLM_API_KEY') else '❌ Missing'}")
    print(f"  GLM_BASE_URL: {os.getenv('GLM_BASE_URL', 'NOT SET')}")
    print(f"  GLM_WATCHER_ENABLED: {os.getenv('GLM_WATCHER_ENABLED', 'false')}")
    
    # Run tests
    results = []
    results.append(("Kimi", test_kimi()))
    results.append(("GLM", test_glm()))
    results.append(("GLM Watcher", test_glm_watcher()))
    
    # Summary
    print("\n" + "="*60)
    print("  SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name:20} {status}")
    
    print(f"\nTotal: {passed}/{total} passed")
    
    if passed == total:
        print("\n✅ All APIs working! Ready for full test suite.")
        sys.exit(0)
    else:
        print("\n❌ Some APIs failed. Fix configuration before running full suite.")
        sys.exit(1)

