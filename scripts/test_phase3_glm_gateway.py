#!/usr/bin/env python3
"""
Test script for Phase 3: GLM Gateway Implementation

Tests:
1. upload_via_supabase_gateway_glm function exists
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
    """Test that upload_via_supabase_gateway_glm function exists."""
    print("=" * 80)
    print("TEST 1: Function exists")
    print("=" * 80)
    
    try:
        from tools.providers.glm.glm_files import upload_via_supabase_gateway_glm
        print("✅ Successfully imported upload_via_supabase_gateway_glm")
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
        from tools.providers.glm.glm_files import upload_via_supabase_gateway_glm
        import inspect
        
        sig = inspect.signature(upload_via_supabase_gateway_glm)
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
        from tools.providers.glm.glm_files import upload_via_supabase_gateway_glm
        
        doc = upload_via_supabase_gateway_glm.__doc__
        
        assert doc is not None, "Function missing docstring"
        assert "Supabase" in doc, "Docstring missing Supabase mention"
        assert "GLM" in doc, "Docstring missing GLM mention"
        assert "pre-signed URL" in doc, "Docstring missing pre-signed URL mention"
        assert "EXAI" in doc, "Docstring missing EXAI source reference"
        
        print("✅ Function has comprehensive docstring")
        print(f"   - Mentions Supabase: ✅")
        print(f"   - Mentions GLM: ✅")
        print(f"   - Mentions pre-signed URL: ✅")
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

def test_glm_files_module():
    """Test that glm_files module loads without errors."""
    print("\n" + "=" * 80)
    print("TEST 5: glm_files module loads")
    print("=" * 80)
    
    try:
        from tools.providers.glm import glm_files
        
        # Check that existing classes still exist
        assert hasattr(glm_files, 'GLMUploadFileTool'), "GLMUploadFileTool missing"
        
        # Check that new function exists
        assert hasattr(glm_files, 'upload_via_supabase_gateway_glm'), "upload_via_supabase_gateway_glm missing"
        
        print("✅ GLMUploadFileTool exists")
        print("✅ upload_via_supabase_gateway_glm exists")
        
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
        from tools.providers.glm.glm_files import upload_via_supabase_gateway_glm
        import inspect
        
        # Get function source
        source = inspect.getsource(upload_via_supabase_gateway_glm)
        
        # Check for key implementation steps
        checks = [
            ("File validation", "pth.exists()" in source),
            ("Size check (20MB)", "20 * 1024 * 1024" in source or "max_size" in source),
            ("Supabase upload", "storage.upload_file" in source),
            ("Pre-signed URL generation", "create_signed_url" in source),
            ("Pre-signed URL download", "requests.get" in source),
            ("GLM API upload", "requests.post" in source),
            ("Database tracking", 'table("provider_file_uploads")' in source),
            ("Error handling", "try:" in source and "except" in source),
            ("Logging", "logger.info" in source or "logger.error" in source),
            ("60s expiration", "60" in source)
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
    print("PHASE 3: GLM GATEWAY IMPLEMENTATION - TEST SUITE")
    print("=" * 80)
    
    results = []
    
    # Run all tests
    results.append(("Function exists", test_function_exists()))
    results.append(("Function signature", test_function_signature()))
    results.append(("Function docstring", test_function_docstring()))
    results.append(("Import dependencies", test_imports_no_errors()))
    results.append(("glm_files module", test_glm_files_module()))
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
        print("\n🎉 ALL TESTS PASSED - Phase 3 implementation successful!")
        print("\n⚠️  NOTE: This validates code structure only.")
        print("   Full integration testing requires:")
        print("   - Valid GLM_API_KEY")
        print("   - Supabase connection")
        print("   - Test file upload")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed - Phase 3 needs fixes")
        return 1

if __name__ == "__main__":
    sys.exit(main())

