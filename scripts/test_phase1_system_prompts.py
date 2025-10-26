#!/usr/bin/env python3
"""
Test script for Phase 1: System Prompts Implementation

Tests:
1. configurations/file_handling_guidance.py imports correctly
2. systemprompts/base_prompt.py imports from configurations
3. No duplication of FILE_PATH_GUIDANCE
4. All expected constants are available
5. No import errors

Created: 2025-10-26
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_configurations_import():
    """Test that configurations/file_handling_guidance.py imports correctly."""
    print("=" * 80)
    print("TEST 1: Import configurations/file_handling_guidance.py")
    print("=" * 80)
    
    try:
        from configurations.file_handling_guidance import FILE_PATH_GUIDANCE, FILE_UPLOAD_GUIDANCE
        print("✅ Successfully imported FILE_PATH_GUIDANCE")
        print("✅ Successfully imported FILE_UPLOAD_GUIDANCE")
        
        # Verify content
        assert "FULL ABSOLUTE paths" in FILE_PATH_GUIDANCE, "FILE_PATH_GUIDANCE missing expected content"
        assert "FILE UPLOAD METHOD SELECTION" in FILE_UPLOAD_GUIDANCE, "FILE_UPLOAD_GUIDANCE missing expected content"
        print("✅ Content validation passed")
        
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

def test_base_prompt_import():
    """Test that systemprompts/base_prompt.py imports from configurations."""
    print("\n" + "=" * 80)
    print("TEST 2: Import systemprompts/base_prompt.py")
    print("=" * 80)
    
    try:
        from systemprompts.base_prompt import FILE_PATH_GUIDANCE, RESPONSE_QUALITY
        print("✅ Successfully imported FILE_PATH_GUIDANCE from base_prompt")
        print("✅ Successfully imported RESPONSE_QUALITY from base_prompt")
        
        # Verify FILE_PATH_GUIDANCE is from configurations
        assert "FULL ABSOLUTE paths" in FILE_PATH_GUIDANCE, "FILE_PATH_GUIDANCE missing expected content"
        print("✅ FILE_PATH_GUIDANCE content matches configurations")
        
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

def test_no_duplication():
    """Test that there's no duplication between files."""
    print("\n" + "=" * 80)
    print("TEST 3: Check for duplication")
    print("=" * 80)
    
    try:
        from configurations.file_handling_guidance import FILE_PATH_GUIDANCE as CONFIG_PATH
        from systemprompts.base_prompt import FILE_PATH_GUIDANCE as PROMPT_PATH
        
        # They should be the same object (imported, not duplicated)
        if CONFIG_PATH == PROMPT_PATH:
            print("✅ FILE_PATH_GUIDANCE is shared (no duplication)")
        else:
            print("⚠️  WARNING: FILE_PATH_GUIDANCE content differs")
            return False
        
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

def test_file_upload_guidance_available():
    """Test that FILE_UPLOAD_GUIDANCE is available from base_prompt."""
    print("\n" + "=" * 80)
    print("TEST 4: FILE_UPLOAD_GUIDANCE availability")
    print("=" * 80)
    
    try:
        from systemprompts.base_prompt import FILE_UPLOAD_GUIDANCE
        print("✅ FILE_UPLOAD_GUIDANCE available from base_prompt")
        
        # Verify content
        assert "5-20MB" in FILE_UPLOAD_GUIDANCE, "FILE_UPLOAD_GUIDANCE missing Supabase gateway guidance"
        assert "Supabase gateway" in FILE_UPLOAD_GUIDANCE, "FILE_UPLOAD_GUIDANCE missing Supabase gateway mention"
        print("✅ FILE_UPLOAD_GUIDANCE contains Supabase gateway guidance")
        
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

def test_all_expected_constants():
    """Test that all expected constants are available."""
    print("\n" + "=" * 80)
    print("TEST 5: All expected constants available")
    print("=" * 80)
    
    try:
        from systemprompts.base_prompt import (
            FILE_PATH_GUIDANCE,
            FILE_UPLOAD_GUIDANCE,
            RESPONSE_QUALITY,
            ANTI_OVERENGINEERING,
            ESCALATION_PATTERN
        )
        
        print("✅ FILE_PATH_GUIDANCE available")
        print("✅ FILE_UPLOAD_GUIDANCE available")
        print("✅ RESPONSE_QUALITY available")
        print("✅ ANTI_OVERENGINEERING available")
        print("✅ ESCALATION_PATTERN available")
        
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("PHASE 1: SYSTEM PROMPTS IMPLEMENTATION - TEST SUITE")
    print("=" * 80)
    
    results = []
    
    # Run all tests
    results.append(("configurations import", test_configurations_import()))
    results.append(("base_prompt import", test_base_prompt_import()))
    results.append(("no duplication", test_no_duplication()))
    results.append(("FILE_UPLOAD_GUIDANCE available", test_file_upload_guidance_available()))
    results.append(("all constants available", test_all_expected_constants()))
    
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
        print("\n🎉 ALL TESTS PASSED - Phase 1 implementation successful!")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed - Phase 1 needs fixes")
        return 1

if __name__ == "__main__":
    sys.exit(main())

