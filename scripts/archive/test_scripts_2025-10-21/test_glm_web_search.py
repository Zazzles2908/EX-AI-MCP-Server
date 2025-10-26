"""
Test script for GLM native web search

Tests the GLM native web search API to ensure DuckDuckGo fallback is removed.
Created: 2025-10-09 (DuckDuckGo Removal)
"""

import os
import sys
import json

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Load .env file
from dotenv import load_dotenv
env_path = os.path.join(project_root, '.env')
load_dotenv(env_path)

from src.providers.tool_executor import run_web_search_backend


def test_glm_native_web_search():
    """Test GLM native web search"""
    print("\n" + "="*80)
    print("TEST: GLM Native Web Search")
    print("="*80)
    
    api_key = os.getenv("GLM_API_KEY")
    if not api_key:
        print("❌ ERROR: GLM_API_KEY not set in environment")
        return False
    
    print(f"✅ GLM_API_KEY: {api_key[:10]}...{api_key[-10:]}")
    print(f"✅ GLM_BASE_URL: {os.getenv('GLM_BASE_URL', 'https://api.z.ai/api/paas/v4')}")
    
    # Test query
    query = "Python programming language"
    print(f"\nSearching for: {query}")
    
    try:
        result = run_web_search_backend(query)
        
        print(f"\nSearch Result:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # Verify it's using GLM native, not DuckDuckGo
        engine = result.get("engine", "")
        if engine == "glm_native":
            print(f"\n✅ PASS - Using GLM native web search")
            return True
        elif "duckduck" in engine.lower():
            print(f"\n❌ FAIL - Still using DuckDuckGo fallback: {engine}")
            return False
        else:
            print(f"\n⚠️  WARNING - Unknown engine: {engine}")
            return False
            
    except Exception as e:
        print(f"\n❌ FAIL - Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_search_with_filters():
    """Test GLM web search with filters"""
    print("\n" + "="*80)
    print("TEST: GLM Web Search with Filters")
    print("="*80)
    
    # Set environment variables for this test
    os.environ["GLM_WEBSEARCH_COUNT"] = "5"
    os.environ["GLM_WEBSEARCH_RECENCY"] = "oneWeek"
    
    query = "AI news"
    print(f"\nSearching for: {query}")
    print(f"Filters: count=5, recency=oneWeek")
    
    try:
        result = run_web_search_backend(query)
        
        print(f"\nSearch Result:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        if result.get("engine") == "glm_native":
            print(f"\n✅ PASS - GLM native web search with filters")
            return True
        else:
            print(f"\n❌ FAIL - Not using GLM native")
            return False
            
    except Exception as e:
        print(f"\n❌ FAIL - Error: {e}")
        return False


def test_no_duckduckgo_imports():
    """Verify no DuckDuckGo imports in the codebase"""
    print("\n" + "="*80)
    print("TEST: Verify No DuckDuckGo Imports")
    print("="*80)

    # Check if duckduckgo_search is imported anywhere
    tool_executor_file = os.path.join(project_root, 'src', 'providers', 'tool_executor.py')

    with open(tool_executor_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check for actual imports or usage (not just comments)
    has_import = 'from duckduckgo_search import' in content
    has_ddgs_usage = 'DDGS()' in content
    has_ddg_url = 'duckduckgo.com' in content

    if has_import or has_ddgs_usage or has_ddg_url:
        print(f"❌ FAIL - Found DuckDuckGo code in tool_executor.py")
        if has_import:
            print(f"  - Found import statement")
        if has_ddgs_usage:
            print(f"  - Found DDGS() usage")
        if has_ddg_url:
            print(f"  - Found duckduckgo.com URL")
        return False
    else:
        print(f"✅ PASS - No DuckDuckGo code in tool_executor.py")
        print(f"  (Comments mentioning removal are OK)")
        return True


def test_glm_web_search_endpoint():
    """Test that the correct GLM endpoint is being used"""
    print("\n" + "="*80)
    print("TEST: Verify GLM Web Search Endpoint")
    print("="*80)
    
    base_url = os.getenv("GLM_BASE_URL", "https://api.z.ai/api/paas/v4")
    expected_endpoint = f"{base_url}/web_search"
    
    print(f"Expected endpoint: {expected_endpoint}")
    
    # Check the code uses the correct endpoint
    tool_executor_file = os.path.join(project_root, 'src', 'providers', 'tool_executor.py')
    
    with open(tool_executor_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if '/web_search' in content:
        print(f"✅ PASS - Code uses /web_search endpoint")
        return True
    else:
        print(f"❌ FAIL - /web_search endpoint not found in code")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("GLM NATIVE WEB SEARCH TEST SUITE")
    print("DuckDuckGo Fallback Removal Verification - 2025-10-09")
    print("="*80)
    
    results = []
    
    # Run tests
    results.append(("No DuckDuckGo Imports", test_no_duckduckgo_imports()))
    results.append(("GLM Endpoint Verification", test_glm_web_search_endpoint()))
    results.append(("GLM Native Web Search", test_glm_native_web_search()))
    results.append(("GLM Search with Filters", test_search_with_filters()))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - DuckDuckGo fallback successfully removed!")
        print("✅ Now using GLM native web search exclusively")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed - review output above")
    
    print("="*80)


if __name__ == "__main__":
    main()

