#!/usr/bin/env python3
"""
Test script for Phase 2: Kimi Gateway Implementation

Tests:
1. upload_via_supabase_gateway_kimi function exists
2. Function signature is correct
3. Import works without errors
4. Mock test of function logic (without actual API calls)

Created: 2025-10-26
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_function_exists():
    """Test that upload_via_supabase_gateway_kimi function exists."""
    print("=" * 80)
    print("TEST 1: Function exists")
    print("=" * 80)
    
    try:
        from tools.providers.kimi.kimi_files import upload_via_supabase_gateway_kimi
        print("✅ Successfully imported upload_via_supabase_gateway_kimi")
        return True
    except ImportError as e:
        print(f"❌ FAILED: {e}")
        return False

def test_function_signature():
    """Test that function has correct signature."""
    print("\n" + "=" * 80)
    print("TEST 2: Function signature")
    print("=" * 80)
    
    try:
        from tools.providers.kimi.kimi_files import upload_via_supabase_gateway_kimi
        import inspect
        
        sig = inspect.signature(upload_via_supabase_gateway_kimi)
        params = list(sig.parameters.keys())
        
        print(f"Function parameters: {params}")
        
        # Check required parameters
        assert "file_path" in params, "Missing 'file_path' parameter"
        assert "storage" in params, "Missing 'storage' parameter"
        assert "purpose" in params, "Missing 'purpose' parameter"
        
        print("✅ Function signature correct")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

def test_function_docstring():
    """Test that function has comprehensive docstring."""
    print("\n" + "=" * 80)
    print("TEST 3: Function docstring")
    print("=" * 80)
    
    try:
        from tools.providers.kimi.kimi_files import upload_via_supabase_gateway_kimi
        
        doc = upload_via_supabase_gateway_kimi.__doc__
        
        assert doc is not None, "Function missing docstring"
        assert "Supabase" in doc, "Docstring missing Supabase mention"
        assert "Kimi" in doc, "Docstring missing Kimi mention"
        assert "URL extraction" in doc, "Docstring missing URL extraction mention"
        assert "EXAI" in doc, "Docstring missing EXAI source reference"
        
        print("✅ Function has comprehensive docstring")
        print(f"   - Mentions Supabase: ✅")
        print(f"   - Mentions Kimi: ✅")
        print(f"   - Mentions URL extraction: ✅")
        print(f"   - References EXAI source: ✅")
        
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

def test_imports_no_errors():
    """Test that all imports work without errors."""
    print("\n" + "=" * 80)
    print("TEST 4: Import dependencies")
    print("=" * 80)
    
    try:
        # Test all imports used in the function
        import mimetypes
        import requests
        from pathlib import Path
        from utils.file.cache import FileCache
        
        print("✅ mimetypes imported")
        print("✅ requests imported")
        print("✅ pathlib.Path imported")
        print("✅ FileCache imported")
        
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

def test_kimi_files_module():
    """Test that kimi_files module loads without errors."""
    print("\n" + "=" * 80)
    print("TEST 5: kimi_files module loads")
    print("=" * 80)
    
    try:
        from tools.providers.kimi import kimi_files
        
        # Check that existing classes still exist
        assert hasattr(kimi_files, 'KimiUploadFilesTool'), "KimiUploadFilesTool missing"
        assert hasattr(kimi_files, 'KimiChatWithFilesTool'), "KimiChatWithFilesTool missing"
        assert hasattr(kimi_files, 'KimiManageFilesTool'), "KimiManageFilesTool missing"
        
        # Check that new function exists
        assert hasattr(kimi_files, 'upload_via_supabase_gateway_kimi'), "upload_via_supabase_gateway_kimi missing"
        
        print("✅ KimiUploadFilesTool exists")
        print("✅ KimiChatWithFilesTool exists")
        print("✅ KimiManageFilesTool exists")
        print("✅ upload_via_supabase_gateway_kimi exists")
        
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

def test_function_logic_validation():
    """Test function logic without making actual API calls."""
    print("\n" + "=" * 80)
    print("TEST 6: Function logic validation")
    print("=" * 80)
    
    try:
        from tools.providers.kimi.kimi_files import upload_via_supabase_gateway_kimi
        import inspect
        
        # Get function source
        source = inspect.getsource(upload_via_supabase_gateway_kimi)
        
        # Check for key implementation steps
        checks = [
            ("File validation", "pth.exists()" in source),
            ("Size check", "100 * 1024 * 1024" in source or "max_size" in source),
            ("Supabase upload", "storage.upload_file" in source),
            ("Public URL", "get_public_url" in source or "supabase_url" in source),
            ("Kimi API call", "requests.post" in source),
            ("Database tracking", 'table("provider_file_uploads")' in source),
            ("Error handling", "try:" in source and "except" in source),
            ("Logging", "logger.info" in source or "logger.error" in source)
        ]
        
        all_passed = True
        for check_name, check_result in checks:
            status = "✅" if check_result else "❌"
            print(f"{status} {check_name}")
            if not check_result:
                all_passed = False
        
        if all_passed:
            print("\n✅ All logic checks passed")
            return True
        else:
            print("\n❌ Some logic checks failed")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("PHASE 2: KIMI GATEWAY IMPLEMENTATION - TEST SUITE")
    print("=" * 80)
    
    results = []
    
    # Run all tests
    results.append(("Function exists", test_function_exists()))
    results.append(("Function signature", test_function_signature()))
    results.append(("Function docstring", test_function_docstring()))
    results.append(("Import dependencies", test_imports_no_errors()))
    results.append(("kimi_files module", test_kimi_files_module()))
    results.append(("Function logic", test_function_logic_validation()))
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print("\n" + "=" * 80)
    print(f"TOTAL: {passed}/{total} tests passed")
    print("=" * 80)
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - Phase 2 implementation successful!")
        print("\n⚠️  NOTE: This validates code structure only.")
        print("   Full integration testing requires:")
        print("   - Valid KIMI_API_KEY")
        print("   - Supabase connection")
        print("   - Test file upload")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed - Phase 2 needs fixes")
        return 1

if __name__ == "__main__":
    sys.exit(main())

